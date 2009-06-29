import sys,os
import urllib2
import re

sys.path.append('/home/bme/src/pinax/apps')
sys.path.append('/home/bme/src')
sys.path.append('/home/bme/src/bme/apps')

os.environ['DJANGO_SETTINGS_MODULE'] ='bme.settings'

from brc.models import *
from brc.views import *
	
xyear = Year.objects.filter(year='2009')

def ret_point(year, hour, minute, street):
        pnt = geocode(year, hour, minute, street)
        print str(pnt)
        return str(pnt.x) + ' ' + str(pnt.y)

def line_string_for_street(t_street):
	linestring = "LINESTRING("
	circular_streets = CircularStreet.objects.filter(year=xyear[0])
	for c_street in circular_streets:
		linestring = linestring + ret_point('2009',t_street.hour, t_street.minute, c_street.name) + ","
        linestring = linestring[:-1]
        linestring = linestring + ")"
	return linestring

time_streets = TimeStreet.objects.filter(year=xyear[0])

for t_street in time_streets:
	linestring = line_string_for_street(t_street)
	print linestring
	t_street.street_line=linestring
	t_street.save()
