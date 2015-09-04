import os
import json
from sqlalchemy import create_engine
from farmsList.settings import ProdConfig, DevConfig

if os.environ.get("FARMSLIST_ENV") == 'prod':
	engine = create_engine(ProdConfig().SQLALCHEMY_DATABASE_URI)
	debug = False
else:
	engine = create_engine(DevConfig().SQLALCHEMY_DATABASE_URI)
	debug = True

class WestSacParcelUpdater():
	def update(self):
		print 'code goes here'

class WestSacWaterUpdater():
	def update(self):
		print 'code goes here'

class SoilUpdater():
	county = ''

	def __init__(self, county):
		self.county = county

	def update(self):
		# Figure out where this might live, again, for now, shouldn't matter because the parser always finds it's not updated
		soilsFile = open("../parcels-pristine/{}-soils.geojson".format(self.county.lower()))
		soils = json.loads(soilsFile.read())
		soilsArray = soils['features']

		# For now, we pretty much assume that land is correctly soiled on a first come first serve basis in terms of importing new soil data.
		# This is based on the nature of frequency with which such data sets are updated.
		# Currently, the government is only responsible for collecting this data on an ad hoc basis.
		for soilFeature in soilsArray:
			stringVersion = json.dumps(soilFeature['geometry'])
			name = 'soil' + soilFeature['properties']['COMPONENT_']
			result = conn.execute("SELECT * FROM additional_layers WHERE name LIKE 'soil%%' AND ST_Intersects(ST_GeomFromGeoJson('{}'), geom) AND (ST_Area(ST_Intersection(ST_GeomFromGeoJson('{}'), geom))/ST_Area(geom)) > .25".format(stringVersion,stringVersion)).first()
			if result == None:
				conn.execute("INSERT INTO additional_layers (name, geometry, geom) VALUES('{}','{}',ST_GeomFromGeoJson('{}'))".format(name,stringVersion, stringVersion))
			elif debug:
				print '{} intersects by more than 25%% with an existing soil geometry ({})'.format(name, result)
