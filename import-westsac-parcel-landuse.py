import os
import json
from sqlalchemy import create_engine
from farmsList.settings import ProdConfig, DevConfig

if os.environ.get("FARMSLIST_ENV") == 'prod':
	engine = create_engine(ProdConfig().SQLALCHEMY_DATABASE_URI)
else:
	engine = create_engine(DevConfig().SQLALCHEMY_DATABASE_URI)

conn = engine.connect()
parcels = []

for x in range(0, 17):
	filename = 'landuse{0:02d}.json'.format(x)
	file = open("parcels-pristine/" + filename)
	array = json.loads(file.read())
	for y in range(0, len(array)):
		if 'apn' not in array[y] or 'zoning' not in array[y]:
			continue
		parcel = {}
		parcel['apn'] = int(array[y]['apn'])
		parcel['zoning'] = array[y]['zoning']
		if 'land_type' in array[y]:
			parcel['landType'] = array[y]['land_type']
		else:
			parcel['landType'] = '';
		if 'land_use' in array[y]:
			parcel['landUse'] = array[y]['land_use']
		else:
			parcel['landUse'] = '';
		parcels.append(parcel)

for parcel in parcels:
	conn.execute("UPDATE parcels SET \"landType\" = '{}', zoning='{}', \"landUse\" = '{}' WHERE apn = {}".format(parcel['landType'], parcel['zoning'], parcel['landUse'], parcel['apn']))
