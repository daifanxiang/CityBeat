from event_interface import EventInterface
from event_feature import EventFeature
from photo_interface import PhotoInterface
from photo import Photo
from region import Region
from event import Event
from caption_parser import CaptionParser
from stopwords import Stopwords

import operator
import string
import types
import random
import math

pi = PhotoInterface()
pi.setDB('citybeat')
pi.setCollection('photos')

photos = pi.getAllDocuments()

n_cap = 0
cap_len = 0

for photo in photos:
	p = Photo(photo)
	l_cap = len(p.getCaption())
	if l_cap > 0:
		n_cap += 1
		cap_len += l_cap

print n_cap
print cap_len