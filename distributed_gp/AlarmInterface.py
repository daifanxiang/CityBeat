##########
# Author: Chaolun Xia, 2013-Jan-09#
#
# A high level interface to access the alarm data, for labeling the event
##########
#Edited by: (Please write your name here)#

from MongoDB import MongoDBInterface
from instagram.client import InstagramAPI
from datetime import datetime

import config
import time
import logging
import string

dbAddress = 'grande'

class AlarmDataInterface:
	
	def __init__(self, address = dbAddress, port = 27017):
		self.db = MongoDBInterface(address, port)
		self.db.SetDB('alarm_filter')
		self.db.SetCollection('photos')
		
	def GetUnlabeledEvent(self):
		# Get unlabeled "event" from the alarm filter
		return self.db.GetItem({'label':'unlabeled'})
	
	def LabelEvent(self, event, label):
		# Label an "event" as a true event or non-event
		event['label'] = label
		self.db.UpdateItem(event)
		
	def _GetAllEventsAtLocation(self, lat, lon):
		return self.db.GetAllItems({'lat':lat, 'lng':lon})
			
	def _MergeTwoEvents(self, oldEvent, newEvent):
		# merge the photos from the new event to the old event
		# it will remove the duplicate photos
		oldPhotos = oldEvent['photos']
		newPhotos = newEvent['photos']
		oldPhoto = oldPhotos[-1]
		for i in xrange(0,len(newPhotos)):
			if self._UnicodeToInt(newPhotos[i]['created_time']) > self._UnicodeToInt(oldPhoto['created_time']):
				oldPhotos = oldPhotos + newPhotos[i:]
				print '%d out of %d photos have been increased' %(len(newPhotos[i:]), len(newPhotos))
				break
			
		# this print is just for debug
		print 'no photo has been increased'
		# end for debug
		
		oldEvent['photos'] = oldPhotos
		return oldEvent
	
	def _UnicodeToInt(self, unic):
		return string.atoi(unic.encode("utf-8"))
		
	def MergeEvent(self, event):
		# merge the event with older events in DB
		
		# get all events in the same location
		allEvents = self._GetAllEventsAtLocation(event['lat'], event['lng'])
		if allEvents is None:
			return False
		for oldEvent in allEvents:
			# find a proper old event to combine (we assume there is only one "proper" old event)
			lastPhoto = oldEvent['photos'][-1]
			t1 = self._UnicodeToInt(event['photos'][-1]['created_time'])
			t2 = self._UnicodeToInt(lastPhoto['created_time'])
			
			if t1 == t2:
				# no further photos for this event
				return True
			
			# maximal allowed time interval is 15 mins
			if t1 > t2 and t1 <= t2 + 60*15:
				#within 15 minutes
				mergedEvent = self._MergeTwoEvents(oldEvent, event)
				self.db.UpdateItem(mergedEvent)
				return True
		return False
				
	
	def GetUnlabelEvents(self, condition = None):
		# TODO: select events according to the conditions
		pass 

		
	
def getPhotoFromInstagram(cnt):
	# only for test
	cur_time = datetime.utcnow()
	#sw_ne = (40.773012,-73.9863145)
	sw_ne = (40.75953, -73.9863145)
	lat = sw_ne[0]
	lon = sw_ne[1]
	client = InstagramAPI(client_id = config.instagram_client_id, client_secret = config.instagram_client_secret)
	try:
		res = client.media_search(lat = lat, lng = lon, return_json = True, distance = 1*1000, count=cnt)
		return res
	except Exception as e:
		print 'Exception!'
		logging.warning(e)
	return None


def TestWithFakeItems():
	myDB = MongoDBInterface(dbAddress, 27017)
	myDB.SetDB('alarm_filter')
	myDB.SetCollection('photos')
	for i in xrange(2):
		photos = getPhotoFromInstagram(2)
		myDB.SaveItem({'label':'unlabeled', 'photo':photos, 'test':'test'})
	testDB = AlarmDataInterface(dbAddress, 27017)
	i = 0
	while True:
		event = testDB.GetUnlabeledEvent()
		if event is None:
			break
		testDB.LabelEvent(event, 'fake')
		i = i + 1
		print i
	
	
def main():
	# main() function is only for test
	TestWithFakeItems()

if __name__ == "__main__":
	main()
