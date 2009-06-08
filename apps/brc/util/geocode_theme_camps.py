import math

import sys,os
import urllib2
from BeautifulSoup import BeautifulSoup
import re

sys.path.append('/home/ortelius/projects')
os.environ['DJANGO_SETTINGS_MODULE'] ='bme.settings'

from bme.web.models import *
from bme.web.views import *

theme_camps = theme_camp.objects.all()

xyear = year.objects.filter(year='2007')

for camp in theme_camps:
	if(camp.time_address):
		time_address = camp.time_address
		street = camp.circular_street.name

		items = str(time_address).split(':')
		hour = items[0]
		minutes = items[1]
	
		point = geocode('2007', hour, minutes, str(street))
		camp.location_point = point
	else:
		point = Point(float(0), float(0))
		camp.location_point = point
	camp.save()
	print str(camp) + " " + str(camp.location_point)
		
