import os
import json
import time
from sqlalchemy import create_engine
from farmsList.settings import ProdConfig, DevConfig
from farmsList.modules.importers import findExistingMatchingParcels

if os.environ.get("FARMSLIST_ENV") == 'prod':
	engine = create_engine(ProdConfig().SQLALCHEMY_DATABASE_URI)
	debug = False
else:
	engine = create_engine(DevConfig().SQLALCHEMY_DATABASE_URI)
	debug = True

conn = engine.connect()
DELIMETER = "*|*"

class jsonImportChecker():
	def validateIdsInternally(self, parcels):
		knownConflicts = []
		checkedParcels = {}
		for parcel in parcels:
			parcelId = parcel['id'] + DELIMETER + parcel['jurisdiction']
			if parcelId in checkedParcels and parcelId not in knownConflicts and checkedParcels[parcelId] != parcel:
				knownConflicts.append(parcelId)
			else:
				checkedParcels[parcelId] = parcel
		return knownConflicts

	def validateImportInternalGeometry(self, parcels):
		timestamp = int(time.time())
		indexedParcels = {}
		for parcel in parcels:
			index = parcel['id'] + DELIMETER + parcel['jurisdiction']
			indexedParcels[index] = parcel
		conn.execute("CREATE TEMPORARY TABLE temp_raw_parcels_{}(id VARCHAR(800), geometry GEOMETRY('MultiPolygon'))".format(timestamp))
		sqlCommandsString = "INSERT INTO temp_raw_parcels_{} (id, geometry) VALUES ".format(timestamp)
		for parcel in parcels:
			if 'geometry' in parcel:
				sqlCommandsString += "('{}', ST_GeomFromGeoJson('{}')), ".format(parcel['id'] + DELIMETER + parcel['jurisdiction'], json.dumps(parcel['geometry']))
		sqlCommandsString = sqlCommandsString[:-2]
		conn.execute(sqlCommandsString)
		conn.execute("CREATE TEMPORARY TABLE temp_parcels_polys_{} AS SELECT (ST_Dump(geometry)).geom AS geom FROM temp_raw_parcels_{}".format(timestamp, timestamp))
		conn.execute("CREATE TEMPORARY TABLE temp_rings_{} AS SELECT ST_ExteriorRing((ST_DumpRings(geom)).geom) AS geom FROM temp_parcels_polys_{}".format(timestamp, timestamp))
		conn.execute("CREATE TEMPORARY TABLE temp_boundaries_{} AS SELECT ST_Union(geom) AS geom FROM temp_rings_{}".format(timestamp, timestamp))
		conn.execute("CREATE TEMPORARY SEQUENCE temp_polyseq_{}".format(timestamp))
		conn.execute("CREATE TEMPORARY TABLE temp_polys_{} AS SELECT nextval('temp_polyseq_{}') AS id, (ST_Dump(ST_Polygonize(geom))).geom AS geom FROM temp_boundaries_{}".format(timestamp, timestamp, timestamp))
		knownConflicts = []
		result = conn.execute("SELECT p.id, o.id FROM temp_polys_{} p JOIN temp_raw_parcels_{} o ON ST_Contains(o.geometry, ST_PointOnSurface(p.geom)) ORDER BY p.id".format(timestamp, timestamp)).fetchall()
		currentPolygonId = ''
		currentParcelIds = []
		for row in result:
			polygonId, parcelId = row
			if polygonId == currentPolygonId:
				for currentParcelId in currentParcelIds:
					conflict = (parcelId, currentParcelId)
					if conflict not in knownConflicts:
						knownConflicts.append(conflict)
			else:
				currentPolygonId = polygonId
				currentParcelIds = []
			currentParcelIds.append(parcelId)
		conn.execute('DROP TABLE temp_raw_parcels_{}'.format(timestamp))
		conn.execute('DROP TABLE temp_rings_{}'.format(timestamp))
		conn.execute('DROP TABLE temp_boundaries_{}'.format(timestamp))
		conn.execute('DROP TABLE temp_parcels_polys_{}'.format(timestamp))
		conn.execute('DROP SEQUENCE temp_polyseq_{}'.format(timestamp))
		conn.execute('DROP TABLE temp_polys_{}'.format(timestamp))
		return knownConflicts

	def validateGeometryAgainstExisting(self, parcels):
		timestamp = int(time.time())
		indexedParcels = {}
		for parcel in parcels:
			index = parcel['id'] + DELIMETER + parcel['jurisdiction']
			indexedParcels[index] = parcel
		conn.execute("CREATE TEMPORARY TABLE temp_raw_parcels_{}(id VARCHAR(800), geometry GEOMETRY('MultiPolygon'), preexisting BOOLEAN DEFAULT TRUE)".format(timestamp))
		conn.execute("INSERT INTO temp_raw_parcels_{} (SELECT apn || '{}' || jurisdiction AS id, geom FROM parcels)".format(timestamp, DELIMETER))
		conn.execute("CREATE TEMPORARY TABLE temp_parcels_polys_{} AS SELECT (ST_Dump(geometry)).geom AS geom FROM temp_raw_parcels_{}".format(timestamp, timestamp))
		conn.execute("CREATE TEMPORARY TABLE temp_rings_{} AS SELECT ST_ExteriorRing((ST_DumpRings(geom)).geom) AS geom FROM temp_parcels_polys_{}".format(timestamp, timestamp))
		conn.execute("CREATE TEMPORARY TABLE temp_boundaries_{} AS SELECT ST_Union(geom) AS geom FROM temp_rings_{}".format(timestamp, timestamp))
		conn.execute("CREATE TEMPORARY SEQUENCE temp_polyseq_{}".format(timestamp))
		conn.execute("CREATE TEMPORARY TABLE temp_polys_{} AS SELECT nextval('temp_polyseq_{}') AS id, (ST_Dump(ST_Polygonize(geom))).geom AS geom FROM temp_boundaries_{}".format(timestamp, timestamp, timestamp))
		knownConflicts = []
		conn.execute("CREATE TEMPORARY TABLE temp_single_poly_{} AS SELECT ST_Union(geom) AS geom FROM temp_polys_{}".format(timestamp, timestamp))
		conn.execute("CREATE TEMPORARY TABLE temp_new_parcels_{}(id VARCHAR(800), geometry GEOMETRY('MultiPolygon'))".format(timestamp))
		sqlCommandsString = "INSERT INTO temp_new_parcels_{} (id, geometry) VALUES ".format(timestamp)
		for parcel in parcels:
			if 'geometry' in parcel:
				sqlCommandsString += "('{}', ST_GeomFromGeoJson('{}')), ".format(parcel['id'] + DELIMETER + parcel['jurisdiction'], json.dumps(parcel['geometry']))
		sqlCommandsString = sqlCommandsString[:-2]
		conn.execute(sqlCommandsString)
		result = conn.execute("SELECT n.id FROM temp_single_poly_{} p JOIN temp_new_parcels_{} n ON ST_Intersects(n.geometry, p.geom)".format(timestamp, timestamp)).fetchall()
		conn.execute('DROP TABLE temp_single_poly_{}'.format(timestamp))
		conn.execute('DROP TABLE temp_new_parcels_{}'.format(timestamp))
		for row in result:
			parcelId = row[0]
			if parcelId not in knownConflicts:
				hasGeom = 'geometry' in indexedParcels[index]
				if hasGeom:
					result = conn.execute("SELECT count(*) FROM parcels WHERE geometry = {}".format(indexedParcels[index]['geometry'])).fetchone()
					isNewParcel = result[0] == 0
				if hasGeom and isNewParcel:
					knownConflicts.append(parcelId)
		conn.execute('DROP TABLE temp_raw_parcels_{}'.format(timestamp))
		conn.execute('DROP TABLE temp_rings_{}'.format(timestamp))
		conn.execute('DROP TABLE temp_boundaries_{}'.format(timestamp))
		conn.execute('DROP TABLE temp_parcels_polys_{}'.format(timestamp))
		conn.execute('DROP SEQUENCE temp_polyseq_{}'.format(timestamp))
		conn.execute('DROP TABLE temp_polys_{}'.format(timestamp))
		return knownConflicts

	# This is formatting stuff right now. Ideally, this data would be formatted client side and be made more useful.
	def validateParcels(self, parcels):
		for parcel in parcels:
			if 'id' not in parcel or 'jurisdiction' not in parcel:
				raise IndexError('all parcels must have both an id and a jurisdiction')
			if DELIMETER in parcel['id'] + parcel['jurisdiction']:
				raise ValueError('parcel id or jurisdiction contains delimeter *|*: {} {}'.format(parcel['id'], parcel['jurisdiction']))
		issues = ''

		internalDuplicationErrors = self.validateIdsInternally(parcels)
		if len(internalDuplicationErrors) > 0:
			issues += '\n\r\n\rThese parcels are listed multiple times in your input:\n'
		for duplicate in internalDuplicationErrors:
			parts = duplicate.split(DELIMETER)
			parcelId = parts[0]
			jurisdiction = parts[1]
			issues += '\nID: {}  Jurisdiction: {}'.format(parcelId, jurisdiction)

		internalGeometryErrors = self.validateImportInternalGeometry(parcels)
		if len(internalGeometryErrors) > 0:
			issues += '\n\r\n\rThese parcels within your input overlap:\n'
		for overlap in internalGeometryErrors:
			parcel1, parcel2 = overlap
			parts1 = parcel1.split(DELIMETER)
			parts2 = parcel2.split(DELIMETER)
			parcelId1 = parts1[0]
			jurisdiction1 = parts1[1]
			parcelId2 = parts2[0]
			jurisdiction2 = parts2[1]
			issues += '\nID: {} Jurisdiction: {} overlaps with ID: {} Jurisdiction: {}'.format(parcelId1, jurisdiction1, parcelId2, jurisdiction2)

		existingGeometryConflicts = self.validateGeometryAgainstExisting(parcels)
		if len(existingGeometryConflicts) > 0:
			issues += '\n\r\n\rThese parcels overlap with existing data:\n'
		for overlap in existingGeometryConflicts:
			parts = overlap.split(DELIMETER)
			parcelId = parts[0]
			jurisdiction = parts[1]
			issues += '\nID: {}  Jurisdiction: {}'.format(parcelId, jurisdiction)

		if len(issues) < 1:
			issues = 'No issues!'
		else:
			issues += '\n\r\n\rPlease address this issues and run the import again.\nFor additional help, contact robertm@cityofwestsacramento.org or grantrobertsmith@gmail.com.'
		return issues

	def findUpdates(self, parcels):
		indexedParcels = {}
		for parcel in parcels:
			index = parcel['id'] + DELIMETER + parcel['jurisdiction']
			indexedParcels[index] = parcel
		updatedParcels = {}
		matchingParcels = findExistingMatchingParcels(parcels)
		for row in matchingParcels:
			apn, jurisdiction, geometry, water, zoning, soil, address = row
			index = str(apn) + DELIMETER + jurisdiction
			parcel = indexedParcels[index]
			updatedParcels[index] = []
			if 'geometry' in parcel and geometry != json.dumps(parcel['geometry']):
				tupleEntry = ('geometry', geometry, parcel['geometry'])
				updatedParcels[index].append(tupleEntry)
			if 'water' in parcel and water is not None and water != parcel['water']:
				tupleEntry = ('water', water, parcel['water'])
				updatedParcels[index].append(tupleEntry)
			if 'zoning' in parcel and zoning is not None and zoning.strip() != '' and zoning != parcel['zoning']:
				tupleEntry = ('zoning', zoning, parcel['zoning'])
				updatedParcels[index].append(tupleEntry)
			if 'soil' in parcel and soil is not None and soil.strip() != '' and soil != parcel['soil']:
				tupleEntry = ('soil', soil, parcel['soil'])
				updatedParcels[index].append(tupleEntry)
			if 'address' in parcel and address is not None and address.strip() != '' and address != parcel['address']:
				tupleEntry = ('address', address, parcel['address'])
				updatedParcels[index].append(tupleEntry)
			if updatedParcels[index] == []:
				del updatedParcels[index]
		issues = ''
		for index, parcelUpdates in updatedParcels.iteritems():
			parts = index.split(DELIMETER)
			issues += '\n\r\n\rParcel ID {} and Jurisdiction {} will be updated:\n'.format(parts[0], parts[1])
			for update in parcelUpdates:
				title, oldValue, newValue = update
				issues += '\nThe {} was {} and will be changed to {}.'.format(title, oldValue, newValue)
		if len(issues) < 1:
			issues = 'No issues!'
		else:
			issues += '\n\rTo CONTINUE with the import and ACCEPT THESE CHANGES, click below.'
		return issues
