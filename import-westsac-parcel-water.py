import os
import json
import re
import __future__
from sqlalchemy import create_engine
from farmsList.settings import ProdConfig, DevConfig

if os.environ.get("FARMSLIST_ENV") == 'prod':
	engine = create_engine(ProdConfig().SQLALCHEMY_DATABASE_URI)
else:
	engine = create_engine(DevConfig().SQLALCHEMY_DATABASE_URI)

conn = engine.connect()
parcels = []
pipeSizes = {}

for x in range(0, 16):
	filename = 'water{0:02d}.json'.format(x)
	file = open("parcels-pristine/" + filename)
	array = json.loads(file.read())
	for y in range(0, len(array)):
		if 'apn' not in array[y] or 'pipe_size' not in array[y]:
			continue
		parcel = {}
		parcel['apn'] = int(array[y]['apn'])
		rawPipeSize = array[y]['pipe_size']
		pipeSize = re.search(r'\d(.*\d)?', rawPipeSize)  # get the part of the string that has numbers
		pipeSize = pipeSize = array[y]['pipe_size'] if pipeSize == None else pipeSize.group()  # if no numbers, get entire string
		flowRate = 0
		for pipeSize in pipeSize.split('&'):  # split on these strings ['&'] (ex. '5/8 & 3/4')
			pipeSize.strip()
			decimalPipeSize = 0
			for part in pipeSize.split(' '):  # split on spaces (ex. '1 1/2')
				if part != "" and part[0].isdigit():
					# do floating point division here and add up the fractional pieces
					decimalPipeSize += eval(compile(part, '<string>', 'eval', __future__.division.compiler_flag))
			# if str(decimalPipeSize) not in pipeSizes:
			# 	print str(decimalPipeSize)
			# 	pipeSizes[str(decimalPipeSize)] = 1
			# else:
			# 	pipeSizes[str(decimalPipeSize)] += 1
			flowRate += decimalPipeSize ** 2 * 28 # convert pipe size to gal/min, assuming 1/2 gives 7 gal/minute and it scales with area
		parcel['water'] = 500 if flowRate > 500 else flowRate
		parcels.append(parcel)

for parcel in parcels:
	conn.execute("UPDATE parcels SET \"water\" = {} WHERE apn = {}".format(parcel['water'], parcel['apn']))
