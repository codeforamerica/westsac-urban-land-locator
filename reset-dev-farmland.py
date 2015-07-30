import os
import json
import execjs
import urllib2
from sqlalchemy import create_engine
from farmsList.settings import DevConfig

if os.environ.get("FARMSLIST_ENV") == 'prod':
	engine = create_engine(ProdConfig().SQLALCHEMY_DATABASE_URI)
else:
	engine = create_engine(DevConfig().SQLALCHEMY_DATABASE_URI)

conn = engine.connect()
parcels = [{
	'geometry': '{"type":"Polygon","coordinates":[[[-121.51367978210449,38.58853235229309],[-121.51347978210449,38.58853235229309],[-121.51347978210449,38.58833235229309],[-121.51367978210449,38.58833235229309],[-121.51367978210449,38.58853235229309]]]}',
	'center': '{"geometry":{"type":"Point","coordinates":[-121.51357978210449,38.58843235229309]}}',
	'soil': 'Yolo',
	'size': '0.32',
	'id': 10000001
},
{
	'geometry': '{"type":"Polygon","coordinates":[[[-121.52367978210449,38.58853235229309],[-121.52347978210449,38.58853235229309],[-121.52347978210449,38.58833235229309],[-121.52367978210449,38.58833235229309],[-121.52367978210449,38.58853235229309]]]}',
	'center': '{"geometry":{"type":"Point","coordinates":[-121.52357978210449,38.58843235229309]}}',
	'soil': 'Made Land',
	'size': '1.03',
	'id': 10000002
},
{
	'geometry': '{"type":"Polygon","coordinates":[[[-121.53367978210449,38.58853235229309],[-121.53347978210449,38.58853235229309],[-121.53347978210449,38.58833235229309],[-121.53367978210449,38.58833235229309],[-121.53367978210449,38.58853235229309]]]}',
	'center': '{"geometry":{"type":"Point","coordinates":[-121.53357978210449,38.58843235229309]}}',
	'soil': 'Sacramento',
	'size': '2.01',
	'id': 10000003
}]

for parcel in parcels:
	conn.execute("INSERT INTO farmlands (geometry, size, zoning, center, water, id, soil) VALUES ('{}', {}, 'Ag', '{}', 0, {}, '{}')".format(parcel['geometry'], parcel['size'], parcel['center'], parcel['id'], parcel['soil']))
