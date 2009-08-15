import math

import sys,os
import urllib2
import re

sys.path.append('../../../../pinax/apps')
sys.path.append('../../../../../src')
sys.path.append('../../../../../src/bme/apps')

os.environ['DJANGO_SETTINGS_MODULE'] ='bme.settings'

from brc.models import *
from brc.views import *

curr_year='2009'
year = Year.objects.get(year=curr_year)

art_installations = ArtInstallation.objects.filter(year=year)

for art in art_installations:
	if(art.time_address and art.distance):
		items = str(art.time_address).split(':')
		hour = items[0]
		minutes = items[1]
	
		point = geocode2(curr_year, hour, minutes, art.distance)
		art.location_point = point
		art.save()
		print str(art) + " " + str(art.location_point)
