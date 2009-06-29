import sys,os
import urllib2
import re

sys.path.append('/home/bme/src/pinax/apps')
sys.path.append('/home/bme/src')
sys.path.append('/home/bme/src/bme/apps')

os.environ['DJANGO_SETTINGS_MODULE'] ='bme.settings'

from brc.models import *
from brc.views import *

def ret_point(year, hour, minute, street):
	pnt = geocode(year, hour, minute, street)
	return str(pnt.x) + ' ' + str(pnt.y)
	
def line_string_for_street(street,year):
	linestring = "LINESTRING("
	for x in range (2,10):
		linestring = linestring +  ret_point(year,x,00,street) + ","
		linestring = linestring +  ret_point(year,x,05,street) + ","
		linestring = linestring +  ret_point(year,x,10,street) + ","
		linestring = linestring +  ret_point(year,x,15,street) + ","
		linestring = linestring +  ret_point(year,x,20,street) + ","
		linestring = linestring +  ret_point(year,x,25,street) + ","
		linestring = linestring +  ret_point(year,x,30,street) + ","
		linestring = linestring +  ret_point(year,x,35,street) + ","
		linestring = linestring +  ret_point(year,x,40,street) + ","
		linestring = linestring +  ret_point(year,x,45,street) + ","
		linestring = linestring +  ret_point(year,x,50,street) + ","
		linestring = linestring +  ret_point(year,x,55,street) + ","
	linestring = linestring +  ret_point(year,10,00,street)
	linestring = linestring + ")"
	return linestring

curr_year='2009'
xyear = Year.objects.filter(year=curr_year)
print xyear[0]
streets = CircularStreet.objects.filter(year=xyear[0])
for street in streets:
	print street.name
	linestring = line_string_for_street(street.name,curr_year)
	print linestring
	street.street_line=linestring
	street.save()
