import os
import json
import xlrd
import urllib2
from sqlalchemy import create_engine
from farmsList.settings import ProdConfig, DevConfig

if os.environ.get("FARMSLIST_ENV") == 'prod':
	engine = create_engine(ProdConfig().SQLALCHEMY_DATABASE_URI)
	filepath = '/app'
	debug = False
else:
	engine = create_engine(DevConfig().SQLALCHEMY_DATABASE_URI)
	filepath = '..'
	debug = True

def debugPrint(printString):
	if debug:
		print printString

class WestSacParcelUpdater():
	def getParcels():
		print 'code goes here'

	def update(self):
		self.getParcels()

		for x in range(0, 17):
			filename = 'parcels{0:02d}.json'.format(x)
			file = open("{}/parcels-pristine/{}".format(filepath, filename))
			array = json.loads(file.read())
			for y in range(0, len(array)):
				if 'apn' not in array[y]:
					continue
				if int(array[y]['parcode']) != 1 or int(array[y]['apn']) in compiledAPNs:
					continue
				geojsonString = '{{"type":"MultiPolygon","coordinates":[{}]}}'.format(array[y]['shape']['geometry']['rings'])
				point = [float(array[y]['shape']['longitude']), float(array[y]['shape']['latitude'])]
				centerString = '{{"type":"Point","coordinates":{}}}'.format(point)
				soil = ""
				parcel = {}
				parcel['geometry'] = geojsonString
				parcel['center'] = centerString
				parcel['soil'] = soil
				size = round(float(array[y]['acres']), 2)
				size = size if size >= 0.01 else 0.01
				parcel['size'] = size
				parcel['apn'] = int(array[y]['apn'])
				compiledAPNs.append(parcel['apn'])
				parcels.append(parcel)

		for parcel in parcels:
			conn.execute("INSERT INTO parcels (geometry, size, zoning, center, water, apn, soil, cent, geom) VALUES ('{}', {}, 'Ag', '{}', 0, {}, '{}', ST_GeomFromGeoJson('{}'), ST_GeomFromGeoJson('{}'))".format(parcel['geometry'], parcel['size'], parcel['center'], parcel['apn'], parcel['soil'], parcel['center'], parcel['geometry']))

		conn.execute("CREATE temporary TABLE t_parcel_to_soil(parcel_id INT,soil VARCHAR(100))")

		result = conn.execute("SELECT id FROM parcels")
		for row in result:
			# print str(row['id'])
			conn.execute("insert into t_parcel_to_soil(SELECT parcels.id,additional_layers.name FROM additional_layers CROSS JOIN parcels WHERE additional_layers.name NOT LIKE '%%tax%%' AND ST_Contains(additional_layers.geom, (SELECT cent FROM parcels WHERE id={})) AND parcels.id={})".format(row["id"], row["id"]))

		conn.execute("UPDATE parcels AS p SET soil = REPLACE(temp_p.soil, 'soil', '') FROM t_parcel_to_soil AS temp_p WHERE p.id = temp_p.parcel_id")
		conn.execute("UPDATE parcels SET soil = REPLACE(soil, 'Sacrament', 'Sacramento')")
		conn.execute("DROP TABLE t_parcel_to_soil")

class WestSacWaterUpdater():
	def update(self):
		print 'code goes here'

class FoodDesertUpdater():
	def update(self):
		# Grab the food desert excel file from the USDA ERS website and get it into a python object we can use
		xmlBinaryString = urllib2.urlopen('http://www.ers.usda.gov/datafiles/Food_Access_Research_Atlas/Download_the_Data/Current_Version/DataDownload.xlsx').read()
		workbook = xlrd.open_workbook(file_contents=xmlBinaryString)
		sheet = workbook.sheet_by_name('Food Access Research Atlas Data')
		foodDesertCensusTracts = []
		debugPrint('Got the USDA Data.')

		# Now go through and grab all the census tracts that qualify as any of the 4 publicly atlased USDA ERS Food Desert Measures
		for rownum in xrange(sheet.nrows):
			if rownum == 0:
				continue
			rowValues = sheet.row_values(rownum)
			if rowValues[1] == 'CA' and rowValues[2] in ['El Dorado', 'Placer', 'Sacramento', 'Sutter', 'Yolo', 'Yuba'] and 0 < sum(rowValues[3:6]):
				foodDesertCensusTracts.append(int(rowValues[0]))
		debugPrint('Found the food deserts in SACOG region.')

		# Finally build a geojson layer from the 2010 census tract boundaries file with the tracts that are 'food deserts'
		foodDesertLayerString = '{"type":"MultiPolygon","coordinates":['
		for censusTract in foodDesertCensusTracts:
			# censusTractFile = open('{}/parcels-pristine/foodDesertsCalifornia.geojson'.format(filepath), 'r')
			censusTractFile = open('parcels-pristine/foodDesertsCalifornia.geojson', 'r')
			censusTracts = json.loads(censusTractFile.read())
			for tract in censusTracts['features']:
				if int(tract['properties']['GEO_ID'].split('US')[1]) in foodDesertCensusTracts:
					geometryType = tract['geometry']['type']
					if geometryType == 'Polygon':
						foodDesertLayerString += json.dumps(tract['geometry']['coordinates']) + ', '
					elif geometryType == 'MultiPolygon':
						for polygonCoordinateArray in tract['geometry']['coordinates']:
							foodDesertLayerString += json.dumps(polygonCoordinateArray) + ', '
					else:
						print 'Something seems wrong. geometryType was neither Polygon nor MultiPolygon. Please check out this census tract: ' + json.dumps(tract)
		foodDesertLayerString = foodDesertLayerString[:-2]
		foodDesertLayerString += ']}'
		debugPrint('Created a geojson string with all of the food deserts in SACOG region.')

		# Add our new layer to the database, get rid of the old layer
		with engine.connect() as conn:
			conn.execute("DELETE FROM additional_layers WHERE name = 'foodDesert'")
			conn.execute("INSERT INTO additional_layers (name, geom) VALUES('foodDesert',ST_GeomFromGeoJson('{}'))".format(foodDesertLayerString))

class SoilUpdater():
	county = ''

	def __init__(self, county):
		self.county = county

	def update(self):
		# Figure out where this might live, again, for now, shouldn't matter because the parser always finds it's not updated
		soilsFile = open("{}/parcels-pristine/{}-soils.geojson".format(filepath, self.county.lower()))
		soils = json.loads(soilsFile.read())
		soilsArray = soils['features']

		# For now, we pretty much assume that land is correctly soiled on a first come first serve basis in terms of importing new soil data.
		# This is based on the nature of frequency with which such data sets are updated.
		# Currently, the government is only responsible for collecting this data on an ad hoc basis.
		with engine.connect() as conn:
			for soilFeature in soilsArray:
				stringVersion = json.dumps(soilFeature['geometry'])
				name = 'soil' + soilFeature['properties']['COMPONENT_']
				result = conn.execute("SELECT * FROM additional_layers WHERE name LIKE 'soil%%' AND ST_Intersects(ST_GeomFromGeoJson('{}'), geom) AND (ST_Area(ST_Intersection(ST_GeomFromGeoJson('{}'), geom))/ST_Area(geom)) > .25".format(stringVersion,stringVersion)).first()
				if result == None:
					conn.execute("INSERT INTO additional_layers (name, geom) VALUES('{}',ST_GeomFromGeoJson('{}'))".format(name, stringVersion))
				elif debug:
					print '{} intersects by more than 25%% with an existing soil geometry ({})'.format(name, result)
