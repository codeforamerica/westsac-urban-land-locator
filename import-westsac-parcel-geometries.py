import os
import json
import execjs
import urllib2
from sqlalchemy import create_engine
from farmsList.settings import ProdConfig, DevConfig

if os.environ.get("FARMSLIST_ENV") == 'prod':
	engine = create_engine(ProdConfig().SQLALCHEMY_DATABASE_URI)
else:
	engine = create_engine(DevConfig().SQLALCHEMY_DATABASE_URI)

conn = engine.connect()
parcels = []

soilsFile = open("parcels-pristine/yolo-soils-reduced-20.geojson")
yoloSoils = json.loads(soilsFile.read())
soilsArray = yoloSoils['features']
importantSoilFeatures = []

node = execjs.get("Node")
turfSource = urllib2.urlopen('https://api.tiles.mapbox.com/mapbox.js/plugins/turf/v2.0.0/turf.min.js').read()
turfWrapperCode = '''
	function inside(point, polygon) {
		return module.exports.inside(point, polygon);
	}
	function insideAll(points, polygons) {
		var result = [],
			numPoints = points.length;
		for (var i = 0; i < numPoints; i++) {
			// for (var j=0; j < )
		}
	}
'''
nodeContext = node.compile(turfSource + turfWrapperCode)

for x in range(0, 17):
	filename = 'parcels{0:02d}.json'.format(x)
	file = open("parcels-pristine/" + filename)
	array = json.loads(file.read())
	for y in range(0, len(array)):
		if int(array[y]['parcode']) != 1:
			continue
		if 'apn' not in array[y]:
			continue
		geojsonString = '{{"type":"Polygon","coordinates":{}}}'.format(array[y]['shape']['geometry']['rings'])
		point = [float(array[y]['shape']['longitude']), float(array[y]['shape']['latitude'])]
		centerString = '{{"geometry":{{"type":"Point","coordinates":{}}}}}'.format(point)
		soil = ""
		count = 0
		for soilFeature in soilsArray:
			print '{}\r'.format(count),
			centerStringFeature = '{"type":"Feature", "properties":{}, ' + centerString[1:-1] + '}'
			centerStringFeatureObj = json.loads(centerString)
			if soilFeature['geometry'] == None:
				soilsArray.remove(soilFeature)  # will error if next element happens to be the one we want
				count += 1
				continue
			if nodeContext.call("inside", centerStringFeatureObj, soilFeature):
				soil = soilFeature['properties']['COMPONENT_']
				tmpAry = []
				tmpAry.append(soilFeature)
				soilsArray.remove(soilFeature)
				tmpAry.extend(soilsArray)
				soilsArray = tmpAry
				print count, soil
				break
			count += 1
		if soil == "":
			print "UH OH"
		parcel = {}
		parcel['geometry'] = geojsonString
		parcel['center'] = centerString
		parcel['soil'] = soil
		size = round(float(array[y]['acres']), 2)
		size = size if size >= 0.01 else 0.01
		parcel['size'] = size
		parcel['apn'] = int(array[y]['apn'])
		parcels.append(parcel)

'''
for parcel in parcels:
	conn.execute("INSERT INTO parcels (geometry, size, zoning, center, water, apn, soil) VALUES ('{}', {}, 'Ag', '{}', 0, {}, {})".format(parcel['geometry'], parcel['size'], parcel['center'], parcel['apn'], parcel['soil']))
'''
