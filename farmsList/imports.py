'''
	This is where we want to go through and check for any updates to the remote data sets that we're using.
	If a remote data set has been updated, we will fetch it and populate the updates to our database.
'''
import os
import urllib2
from datetime import datetime

from HTMLParser import HTMLParser
from sqlalchemy import create_engine
from farmsList.settings import ProdConfig, DevConfig
from updaters import WestSacParcelUpdater, WestSacWaterUpdater, YoloSoilUpdater

# establish connection with the database we want to be using
if os.environ.get("FARMSLIST_ENV") == 'prod':
	engine = create_engine(ProdConfig().SQLALCHEMY_DATABASE_URI)
else:
	engine = create_engine(DevConfig().SQLALCHEMY_DATABASE_URI)
connection = engine.connect()

# create a subclass and override the handler methods
class WestSacUpdateHTMLParser(HTMLParser):
	foundUpdateTag = False
	foundUpdateInstant = False
	updateInstant = datetime.min

	def handle_starttag(self, tag, attrs):
		if ('class', 'aboutUpdateDate') in attrs:
			self.foundUpdateTag = True
		elif self.foundUpdateTag and not self.foundUpdateInstant:
			self.foundUpdateInstant = True
			for attribute in attrs:
				key, value = attribute
				if (key == 'data-rawdatetime'):
					self.updateInstant = int(value)

class SACOGUpdateHTMLParser(HTMLParser):
	# Assume they never update data for now. Do they have an open data portal yet?
	updateInstant = datetime.min

def getToolsForDataset(name):
    return {
        'westSacParcels': (WestSacUpdateHTMLParser(), WestSacParcelUpdater()),
        'westSacWater': (WestSacUpdateHTMLParser(), WestSacWaterUpdater()),
        'yoloSoil': (SACOGUpdateHTMLParser(), YoloSoilUpdater())
    }[x]

def every_night_at_1am():
	print 'Starting the 1am job.'
	# Important to note that the order of the updates in the database matters
	# For example, the soil of the imported parcels is based on soil data already being present
	remoteDatasets = connection.execute("SELECT * FROM remote_datasets ORDER BY id")
	for dataset in remoteDatasets:
		name = dataset.name
		print 'Checking for update to dataset: ' + name
		responseHtml = urllib2.urlopen(dataset.url).read()
		parser, updater = getToolsForDataset(name)
		parser.feed(responseHtml)
		if parser.updateInstant > dataset.lastUpdatedLocally:
			print 'Updating dataset: ' + name
			updater.run()
			print 'Finished updating dataset: ' + name
		else:
			print 'No update required for dataset: ' + name
	print 'Finished the 1am job.'
