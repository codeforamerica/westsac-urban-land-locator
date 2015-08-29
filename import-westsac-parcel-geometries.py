import os
import json
import execjs
import urllib2
from sqlalchemy import create_engine
from farmsList.settings import ProdConfig, DevConfig

if os.environ.get("FARMSLIST_ENV") == 'prod':
	engine = create_engine(ProdConfig().SQLALCHEMY_DATABASE_URI)
	debug = False
else:
	engine = create_engine(DevConfig().SQLALCHEMY_DATABASE_URI)
	debug = True

conn = engine.connect()
parcels = []
compiledAPNs = []

soilsFile = open("parcels-pristine/yolo-soils.geojson")
yoloSoils = json.loads(soilsFile.read())
soilsArray = yoloSoils['features']

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

for x in range(0, 17):
	filename = 'parcels{0:02d}.json'.format(x)
	file = open("parcels-pristine/" + filename)
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
