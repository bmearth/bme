import sys,os
import urllib2
from BeautifulSoup import BeautifulSoup
import re

sys.path.append('/var/projects')
os.environ['DJANGO_SETTINGS_MODULE'] ='bme.settings'

from bme.web.models import *
from bme.web.views import *
	
xyear = year.objects.filter(year='2008')

def ret_point(year, hour, minute, street):
        pnt = geocode(year, hour, minute, street)
        print str(pnt)
        return str(pnt.x) + ' ' + str(pnt.y)

def line_string_for_street(t_street):
	linestring = "LINESTRING("
	circular_streets = circular_street.objects.filter(year=xyear[0])
	for c_street in circular_streets:
		linestring = linestring + ret_point('2008',t_street.hour, t_street.minute, c_street.name) + ","
        linestring = linestring[:-1]
        linestring = linestring + ")"
	return linestring

time_streets = time_street.objects.filter(year=xyear[0])

for t_street in time_streets:
	linestring = line_string_for_street(t_street)
	print linestring
	t_street.street_line=linestring
	t_street.save()
