import sys,os
import urllib2
from BeautifulSoup import BeautifulSoup
import re

sys.path.append('/var/projects')
os.environ['DJANGO_SETTINGS_MODULE'] ='bme.settings'

from bme.web.models import *
from bme.web.views import *

def ret_point(year, hour, minute, street):
	pnt = geocode(year, hour, minute, street)
	return str(pnt.x) + ' ' + str(pnt.y)
	
def line_string_for_street(street):
	linestring = "LINESTRING("
	for x in range (2,10):
		linestring = linestring +  ret_point('2008',x,00,street) + ","
		linestring = linestring +  ret_point('2008',x,05,street) + ","
		linestring = linestring +  ret_point('2008',x,10,street) + ","
		linestring = linestring +  ret_point('2008',x,15,street) + ","
		linestring = linestring +  ret_point('2008',x,20,street) + ","
		linestring = linestring +  ret_point('2008',x,25,street) + ","
		linestring = linestring +  ret_point('2008',x,30,street) + ","
		linestring = linestring +  ret_point('2008',x,35,street) + ","
		linestring = linestring +  ret_point('2008',x,40,street) + ","
		linestring = linestring +  ret_point('2008',x,45,street) + ","
		linestring = linestring +  ret_point('2008',x,50,street) + ","
		linestring = linestring +  ret_point('2008',x,55,street) + ","
	linestring = linestring +  ret_point('2008',10,00,street)
	linestring = linestring + ")"
	return linestring

xyear = year.objects.filter(year='2008')
print xyear[0]
streets = circular_street.objects.filter(year=xyear[0])
for street in streets:
	print street.name
	linestring = line_string_for_street(street.name)
	print linestring
	street.street_line=linestring
	street.save()
