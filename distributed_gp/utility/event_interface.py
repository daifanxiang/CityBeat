##########
# Author: Chaolun Xia, 2013-Jan-09#
#
# A high level interface to access the alarm data, for labeling the event
##########
#Edited by: (Please write your name here)#

from mongodb_interface import MongoDBInterface
from event import Event
from config import InstagramConfig
from datetime import datetime
from bson.objectid import ObjectId

import config
import time
import logging
import string
import types

class EventInterface(MongoDBInterface):
	def __init__(self, db=InstagramConfig.event_db,  
	             collection=InstagramConfig.event_collection):
	  # initialize an interface for accessing event from mongodb
	  super(EventInterface, self).__init__()
	  self.setDB(db)
	  self.setCollection(collection)
	
	def saveDocument(self, raw_event):
		#rewrite the method
		self.addEvent(raw_event)
		
	def getEventByID(self, ID):
		return self.getDocument({'_id':ObjectId(str(ID))})
	
	def addEventWithoutMerge(self, raw_event):
		super(EventInterface, self).saveDocument(raw_event)
	
	def addEvent(self, raw_event):
		# do not call the method saveDocument, instead, call this method
		# add an event to the db. raw_event can either be a json or an instance of Event 
		if not type(raw_event) is types.DictType:
			new_event = raw_event.toJSON()
		else:
			new_event = raw_event
		new_event = Event(new_event)
		new_event.sortPhotos()
		new_event = new_event.toJSON()
		# before adding, find if any event can be merged
		region = new_event['region']
		condition = ({'region.min_lat':region['min_lat'],
			            'region.min_lng':region['min_lng'],
			            'region.max_lat':region['max_lat'],
			            'region.max_lng':region['max_lng']})
#		condition = {'region.' + k:v for k,v in region.items()}
		old_events = self.getAllDocuments(condition).sort('created_time', -1)
#		print 'condition1:', condition
#		print 'results1:', 
#		for oe in old_events:
#			print '**************'
		
#		condition = {'region':new_event['region']}
#		old_events = self.getAllDocuments(condition).sort('created_time', -1)
#		print 'condition2:', condition
#		print 'results2:', 
#		for oe in old_events:
#			print '**************'
		
		for old_event in old_events:
			end_time1 = int(new_event['photos'][0]['created_time'])
			begin_time1 = int(new_event['photos'][-1]['created_time'])
			end_time2 = int(old_event['photos'][0]['created_time'])
			begin_time2 = int(old_event['photos'][-1]['created_time'])
			time_interval = InstagramConfig.merge_time_interval
#			print 'new: ',end_time1,begin_time1
#			print 'old: ',end_time2,begin_time2
			if end_time1 + time_interval >= begin_time2 and end_time2 + time_interval >= begin_time1:
				# if can merge
				merged_event = Event(old_event)
				merged = merged_event.mergeWith(new_event)
				if merged >= 0:
					print '%d out of %d photos are merged into an old event' % (merged, len(new_event['photos']))
#					print old_event['_id'], new_event['_id']
				if merged > 0:
					self.updateDocument(merged_event)
				return
		# cannot merge
		print 'create a new event'
		super(EventInterface, self).saveDocument(new_event)
		
	def getPhotoDistributionArray(self):
		events = self.getAllDocuments()
		photoNumbers = []
		for event in events:
			photoNumbers.append(len(event['photos']))
		return photoNumbers
		
			
if __name__=='__main__':
	
	ei = EventInterface()
	ei.setDB('citybeat')
	ei.setCollection('candidate_event_25by25_merged')
	print ei.getPhotoDistributionArray()
	
			
#def getPhotoFromInstagram(cnt):
#	# only for test
#	cur_time = datetime.utcnow()
#	#sw_ne = (40.773012,-73.9863145)
#	sw_ne = (40.75953, -73.9863145)
#	lat = sw_ne[0]
#	lon = sw_ne[1]
#	client = InstagramAPI(client_id = config.instagram_client_id, client_secret = config.instagram_client_secret)
#	try:
#		res = client.media_search(lat = lat, lng = lon, return_json = True, distance = 1*1000, count=cnt)
#		return res
#	except Exception as e:
#		print 'Exception!'
#		logging.warning(e)
#	return None
#
#
#def TestWithFakeItems():
#	myDB = MongoDBInterface(dbAddress, 27017)
#	myDB.SetDB('alarm_filter')
#	myDB.SetCollection('photos')
#	for i in xrange(2):
#		photos = getPhotoFromInstagram(2)
#		myDB.SaveItem({'label':'unlabeled', 'photo':photos, 'test':'test'})
#	testDB = AlarmDataInterface(dbAddress, 27017)
#	i = 0
#	while True:
#		event = testDB.GetUnlabeledEvent()
#		if event is None:
#			break
#		testDB.LabelEvent(event, 'fake')
#		i = i + 1
#		print i
#	
#	
#def main():
#	# main() function is only for test
#	TestWithFakeItems()
#
#if __name__ == "__main__":
#	main()
