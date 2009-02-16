import math
from django.contrib.gis.geos import *

def __distance(lat1,lon1,lat2,lon2):
	return 6076.11549*(math.acos(math.sin(lat1)*math.sin(lat2)+math.cos(lat1)*math.cos(lat2)*math.cos(lon1-lon2)))

def __direction(lat1,lon1,lat2,lon2):
	return math.degrees(math.atan2(math.sin(lon1-lon2)*math.cos(lat2), math.cos(lat1)*math.sin(lat2)-math.sin(lat1)*math.cos(lat2)*math.cos(lon1-lon2)) % 2*math.pi)

def __getpoint(lat1,lon1,dist,dir):
	lat1 = (math.pi/180)*lat1
	lon1 = abs((math.pi/180)*lon1)
	dir = (math.pi/180)*dir
	dist = dist / (185200.0/30.48)
	dist = dist / (180*60/math.pi)
	
	lat=math.asin(math.sin(lat1)*math.cos(dist)+math.cos(lat1)*math.sin(dist)*math.cos(dir))
	dlon=math.atan2(math.sin(dir)*math.sin(dist)*math.cos(lat1),math.cos(dist)-math.sin(lat1)*math.sin(lat))
	lon = ((lon1 - dlon+math.pi) % (2*math.pi)) - math.pi

	lat = lat * (180/math.pi)
	lon = lon * (180/math.pi)
	pnt = Point(float(lon), float(lat))

	return pnt
