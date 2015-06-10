import os
import json
from sqlalchemy import create_engine
import sqlalchemy

dirName = os.path.dirname(os.path.realpath(__file__))

engine = create_engine('postgresql://farmslistadmin:@localhost/farms_list')
conn = engine.connect()
parcels = []

for x in range(0, 17):
	filename = 'parcels{0:02d}.json'.format(x)
	file = open(filename)
	array = json.loads(file.read())
	for y in range(0, len(array)):
		type = 'MultiPolygon' if len(array[y]['shape']['geometry']['rings']) > 1 else 'Polygon'
		geojsonString = '{{"type":"{}","coordinates":{}}}'.format(type, array[y]['shape']['geometry']['rings'])
		point = [float(array[y]['shape']['longitude']), float(array[y]['shape']['latitude'])]
		centerString = '{{"geometry":{{"type":"Point","coordinates":{}}}}}'.format(point)
		parcel = {}
		parcel['geometry'] = geojsonString
		parcel['center'] = centerString
		size = round(float(array[y]['acres']), 2)
		size = size if size >= 0.01 else 0.01
		size = size if size < 100 else 99.99
		parcel['size'] = size
		parcels.append(parcel)

for parcel in parcels:
	try:
		conn.execute("INSERT INTO parcels (geometry, size, zoning, center) VALUES ('{}', {}, 'Ag', '{}')".format(parcel['geometry'], parcel['size'], parcel['center']))
	except sqlalchemy.exc.DataError:
		print "parcel geojson is too long, probably"
