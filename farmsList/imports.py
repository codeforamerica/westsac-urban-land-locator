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
from updaters import WestSacParcelUpdater, WestSacWaterUpdater, SoilUpdater, FoodDesertUpdater

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
					self.updateInstant = datetime.fromtimestamp(int(value))

# create a subclass and override the handler methods
class USDAEconomicResearchServiceParcer(HTMLParser):
	foundUpdateTag = False
	foundUpdateInstant = False
	dataBuffer = ''
	updateInstant = datetime.min

	def handle_starttag(self, tag, attrs):
		if ('id', 'UpdateContact') in attrs:
			self.foundUpdateTag = True

	def handle_endtag(self, tag):
		if tag == 'p' and self.foundUpdateTag and not self.foundUpdateInstant:
			self.foundUpdateInstant = True
			timeString = self.dataBuffer.strip()
			self.updateInstant = datetime.strptime(timeString, '%A, %B %d, %Y')

	def handle_data(self, data):
		if self.foundUpdateTag and not self.foundUpdateInstant:
			self.dataBuffer = data

# create a subclass and override the handler methods
class UCDavisSoilsHTMLParcer(HTMLParser):
	soilRegionCode = ''
	foundYoloSoil = False
	foundUpdateInstant = False
	updateInstant = datetime.min

	def handle_data(self, data):
		if data == self.soilRegionCode:
			self.foundYoloSoil = True
		elif self.foundYoloSoil and not self.foundUpdateInstant and data.strip():
			self.updateInstant = datetime.strptime(data, '%Y-%m-%d')
			self.foundUpdateInstant = True

	def __init__(self, code):
		self.soilRegionCode = code
		HTMLParser.__init__(self)

# for each dataset in the database, we need some special code to check for updates (parcer), and to run new updates when needed (updater)
# this maps the dataset named in the database to a give updater and parser for maintaining the data in our database
def getToolsForDataset(name):
    return {
        'elDoradoSoil': (UCDavisSoilsHTMLParcer('ca624'), SoilUpdater('ElDorado')),  # ca724,ca693 are also technically required for el dorado county soil mapping
        'foodDesertSACOG': (USDAEconomicResearchServiceParcer(), FoodDesertUpdater()),
        'placerSoil': (UCDavisSoilsHTMLParcer('ca719'), SoilUpdater('Placer')),
        'sacramentoSoil': (UCDavisSoilsHTMLParcer('ca067'), SoilUpdater('Sacramento')),
        'sutterSoil': (UCDavisSoilsHTMLParcer('ca101'), SoilUpdater('Sutter')),
        'westSacParcels': (WestSacUpdateHTMLParser(), WestSacParcelUpdater()),
        'westSacWater': (WestSacUpdateHTMLParser(), WestSacWaterUpdater()),
        'yoloSoil': (UCDavisSoilsHTMLParcer('ca113'), SoilUpdater('Yolo')),
        'yubaSoil': (UCDavisSoilsHTMLParcer('ca618'), SoilUpdater('Yuba'))
    }[name]

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
		updateInstant = parser.updateInstant.strftime('%Y-%m-%d %H:%M:%S')
		print 'Last Updated Locally: ' + dataset.lastUpdatedLocally.strftime('%Y-%m-%d %H:%M:%S')
		print 'Last Updated Remotely: ' + updateInstant
		if parser.updateInstant > dataset.lastUpdatedLocally:
			print 'Updating dataset: ' + name
			updater.update()
			print 'Finished updating dataset: ' + name
			connection.execute("UPDATE remote_datasets SET \"lastUpdatedLocally\"='{}' WHERE id={}".format(updateInstant, dataset.id))
		else:
			print 'No update required for dataset: ' + name
	print 'Finished the 1am job.'
