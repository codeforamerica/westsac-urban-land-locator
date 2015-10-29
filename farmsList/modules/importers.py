import os
import json
import time
from copy import deepcopy
from sqlalchemy import create_engine
from farmsList.settings import ProdConfig, DevConfig

if os.environ.get("FARMSLIST_ENV") == 'prod':
	engine = create_engine(ProdConfig().SQLALCHEMY_DATABASE_URI)
	debug = False
else:
	engine = create_engine(DevConfig().SQLALCHEMY_DATABASE_URI)
	debug = True

conn = engine.connect()

def findExistingMatchingParcels(parcels):
	for parcel in parcels:
		if "*|*" in parcel['id'] + parcel['jurisdiction']:
			raise ValueError('parcel id or jurisdiction contains delimeter *|*: {} {}'.format(parcel['id'], parcel['jurisdiction']))
	timestamp = int(time.time())
	conn.execute("CREATE TEMPORARY TABLE temp_parcels_{} (internal_id INTEGER, id VARCHAR(800))".format(timestamp))
	conn.execute("INSERT INTO temp_parcels_{} (SELECT id AS internal_id, apn || '*|*' || jurisdiction AS id FROM parcels)".format(timestamp))
	conn.execute("CREATE TEMPORARY TABLE temp_parcels_new_{} (id VARCHAR(800))".format(timestamp))
	sqlCommandsString = "INSERT INTO temp_parcels_new_{} (id) VALUES ".format(timestamp)
	for parcel in parcels:
		sqlCommandsString += "('{}'), ".format(parcel['id'] + "*|*" + parcel['jurisdiction'])
	sqlCommandsString = sqlCommandsString[:-2]
	conn.execute(sqlCommandsString)
	results = conn.execute("SELECT apn, jurisdiction, geometry, water, zoning, soil, address FROM parcels WHERE id IN (SELECT internal_id AS id FROM temp_parcels_{} WHERE id IN (SELECT id FROM temp_parcels_new_{}))".format(timestamp, timestamp)).fetchall()
	conn.execute('DROP TABLE temp_parcels_{}'.format(timestamp))
	conn.execute('DROP TABLE temp_parcels_new_{}'.format(timestamp))
	return results

class importer():
	def importParcels(self, parcels):
		matchingParcelsRaw = findExistingMatchingParcels(parcels)
		# get the data for the existing parcels and build it out, so updates don't overwrite existing data
		# then in the following loop, we will use it (or defaults) to preset the data[]
		indexedMatchingParcels = {}
		for rawMatchedParcel in matchingParcelsRaw:
			apn, jurisdiction, geometry, water, zoning, soil, address = rawMatchedParcel
			index = str(apn) + "*|*" + jurisdiction
			indexedMatchingParcels[index] = {'geometry': geometry, 'water': water, 'zoning': zoning, 'soil': soil, 'address': address}
		sqlInsertStatement = "INSERT INTO parcels (apn, jurisdiction, geometry, water, zoning, soil, address, center, geom) VALUES "
		sqlUpdateStatementInner = ""
		insertNeeded = False
		updateNeeded = False
		fillData = {'geometry': "", 'water': 0, 'zoning': "Unknown", 'soil': "NULL", 'address': "NULL", 'geom': "NULL"}
		for parcel in parcels:
			#preset the data for updates
			data = {}
			index = parcel['id'] + "*|*" + parcel['jurisdiction']
			isUpdate = index in indexedMatchingParcels
			if isUpdate:
				for dataType, dataValue in indexedMatchingParcels[index].iteritems():
					if dataType == 'geometry':
						data['geom'] = "ST_GeomFromGeoJSON('{}')".format(geometry)
					data[dataType] = dataValue
			# set imported values for either inserts or updates
			neededFillData = deepcopy(fillData)  # track which data isn't being inserted via update
			for dataType in fillData:
				if dataType in parcel:
					if dataType == 'geometry':
						del neededFillData['geom']
						data['geometry'] = json.dumps(parcel['geometry'])
						data['geom'] = "ST_GeomFromGeoJSON('{}')".format(json.dumps(parcel['geometry']))
					else:
						data[dataType] = parcel[dataType]
					del neededFillData[dataType]
			# use defaults for inserts where data not explicitly added
			if not isUpdate:
				for dataType, dataValue in neededFillData.iteritems():
					data[dataType] = dataValue
			sqlStatementInner = "({}, '{}', '{}', {}, '{}', '{}', '{}', '{}', {}), ".format(
				int(parcel['id']), 
				parcel['jurisdiction'], 
				data['geometry'], 
				data['water'], 
				data['zoning'], 
				data['soil'], 
				data['address'], 
				"",
				data['geom']
			)
			if isUpdate:
				updateNeeded = True
				sqlUpdateStatementInner += sqlStatementInner
			else:
				insertNeeded = True
				sqlInsertStatement += sqlStatementInner
		sqlInsertStatement = sqlInsertStatement[:-2]
		sqlUpdateStatementInner = sqlUpdateStatementInner[:-2]
		sqlUpdateStatement = (
			"UPDATE parcels AS p SET "
				"geometry = v.geometry, "
				"water = v.water, "
				"zoning = v.zoning, "
				"soil = v.soil, "
				"address = v.address, "
				"center = v.center, "
				"geom = v.geom "
			"FROM (VALUES "
				"{}"
			") AS v(id, jurisdiction, geometry, water, zoning, soil, address, center, geom) "
			"WHERE p.apn = v.id AND p.jurisdiction = v.jurisdiction"
		).format(sqlUpdateStatementInner)
		if insertNeeded:
			conn.execute(sqlInsertStatement)
		if updateNeeded:
			conn.execute(sqlUpdateStatement)
		conn.execute("UPDATE parcels SET cent = ST_Centroid(geom) WHERE geom IS NOT NULL")
		conn.execute("UPDATE parcels SET center = ST_AsGeoJSON(cent) WHERE geom IS NOT NULL")
		return None
