import sys,os
#import urllib2
#import re
import math
import Numeric
from django.contrib.gis.geos import *

#sys.path.append('/home/bme/src/pinax/apps')
#sys.path.append('/home/bme/src')
#sys.path.append('/home/bme/src/bme/apps')
sys.path.append('/home/mikel/Projects/bmearth/2009/bmedev/src/bme/src/pinax/apps')
sys.path.append('/home/mikel/Projects/bmearth/2009/bmedev/src')
sys.path.append('/home/mikel/Projects/bmearth/2009/bmedev/src/bme/apps')

os.environ['DJANGO_SETTINGS_MODULE'] ='bme.settings'

from brc.models import *
from brc.views import *

curr_year='2009'
year = Year.objects.filter(year=curr_year)[0]
clat = 40.769288
clon = -119.220037 

def ret_point(lat,lon,dist,angle):
	pnt = getpoint(lat,lon,dist,-angle) 
	return str(pnt.x) + ' ' + str(pnt.y)
	
def ret_street_point(year, hour, minute, street):
	pnt = geocode(year.year, hour, minute, street)
	return str(pnt.x) + ' ' + str(pnt.y)

def ret_arc(lat,lon,dist,angle_start,angle_end,interval):
	linestring = ""
	for x in range(angle_start,angle_end,interval):
		linestring = linestring + ret_point(lat,lon,dist,x) + ","
	linestring = linestring + ret_point(lat,lon,dist,angle_end)
	return linestring

# CENTER CAMP
dist_to_center_centercamp = 2450
	
radial = time2radial(6,0)
cc = getpoint(clat,clon,dist_to_center_centercamp,-radial)
B = CircularStreet.objects.filter(year=year,name__startswith='B')[0]
D = CircularStreet.objects.filter(year=year,name__startswith='D')[0]
six = TimeStreet.objects.filter(year=year,name="06:00")[0]
dist_inner_ring = dist_to_center_centercamp - B.distance_from_center #300 
dist_outer_ring = dist_to_center_centercamp - D.distance_from_center #610' outside (725' radius to the center of the outer circle road) ??!!

## INNER RING
linestring = "LINESTRING(" + ret_arc(cc.y,cc.x,dist_inner_ring,0,360,1) + ")"
inner_ring = Infrastructure.objects.create(year=year)
inner_ring.name = "Center Camp"
inner_ring.location_line = linestring
inner_ring.tags = 'road'
inner_ring.save()	

## OUTER RING
linestring = "LINESTRING(" + ret_arc(cc.y,cc.x,dist_outer_ring,0,360,1) + ")"
outer_ring = Infrastructure.objects.create(year=year)
outer_ring.name = "Evolution"
outer_ring.location_line = linestring
outer_ring.tags = 'road'
outer_ring.save()

## 6 o'clock spur
pt1 = six.street_line.intersection(B.street_line)
pt2 = six.street_line.intersection(D.street_line)
linestring = "LINESTRING("
linestring = linestring + str(pt1.x) + " " + str(pt1.y) + "," 
linestring = linestring + str(pt2.x) + " " + str(pt2.y)
linestring = linestring + ")"
six_spur = Infrastructure.objects.create(year=year)
six_spur.name = "6:00"
six_spur.location_line = linestring
six_spur.tags = 'road'
six_spur.save()

## B spurs
pts = B.street_line.intersection(outer_ring.location_line)
for i in range(0,2):
	linestring = "LINESTRING("
	linestring = linestring + str(pts[i].x) + " " + str(pts[i].y) + ","
	linestring = linestring + str(cc.x) + " " + str(cc.y)
	linestring = linestring + ")"
 	b_spur = Infrastructure.objects.create(year=year)
 	b_spur.name = B.name
 	b_spur.location_line = GEOSGeometry(linestring).difference(inner_ring.location_line.convex_hull)
 	b_spur.tags = 'road'
 	b_spur.save()

# DOUBLEWIDES
## Extinct .. 8/8:30, 5/7, 3:30/4
D = CircularStreet.objects.filter(year=year,name__startswith='D')[0].name
E = CircularStreet.objects.filter(year=year,name__startswith='E').exclude(name__iexact='Esplanade').exclude(name__iexact='Evolution')[0].name
L = CircularStreet.objects.filter(year=year,name__startswith='L')[0]
geom_collection = "GEOMETRYCOLLECTION("

geom_collection = geom_collection + "POLYGON(("
geom_collection = geom_collection + ret_street_point(year,8,0,D) + ","
geom_collection = geom_collection + ret_street_point(year,8,30,D) + ","
geom_collection = geom_collection + ret_street_point(year,8,30,L.name) + ","
geom_collection = geom_collection + ret_street_point(year,8,0,L.name) + ","
geom_collection = geom_collection + ret_street_point(year,8,0,D)
geom_collection = geom_collection + ")),"

geom_collection = geom_collection + "POLYGON(("
geom_collection = geom_collection + ret_street_point(year,5,0,D) + ","
geom_collection = geom_collection + ret_street_point(year,7,0,D) + ","
geom_collection = geom_collection + ret_street_point(year,7,0,L.name) + ","
geom_collection = geom_collection + ret_street_point(year,5,0,L.name) + ","
geom_collection = geom_collection + ret_street_point(year,5,0,D)
geom_collection = geom_collection + ")),"

geom_collection = geom_collection + "POLYGON(("
geom_collection = geom_collection + ret_street_point(year,3,30,D) + ","
geom_collection = geom_collection + ret_street_point(year,4,0,D) + ","
geom_collection = geom_collection + ret_street_point(year,4,0,L.name) + ","
geom_collection = geom_collection + ret_street_point(year,3,30,L.name) + ","
geom_collection = geom_collection + ret_street_point(year,3,30,D)
geom_collection = geom_collection + "))"

geom_collection = geom_collection + ")"

double_wide = Infrastructure.objects.create(year=year)
double_wide.name = "double wide camps"
double_wide.location_multigeom = geom_collection
double_wide.tags = 'camp_null'
double_wide.save()

# PROMENADES
for x in (3,6,9):
	pt = geocode(year.year,x,0,'Esplanade')
	linestring = "LINESTRING("
	linestring = linestring + str(clon) + " " + str(clat) + ","
	linestring = linestring + str(pt.x) + " " + str(pt.y)
	linestring = linestring + ")"
	promenade = Infrastructure.objects.create(year=year)
	promenade.name = "Promenade"
	promenade.location_line = GEOSGeometry(linestring).difference(outer_ring.location_line.convex_hull)
	promenade.tags = 'road'
	promenade.save()

Esplanade = CircularStreet.objects.filter(year=year,name='Esplanade')[0]
pt = getpoint(clat,clon,Esplanade.distance_from_center,-time2radial(0,0))
linestring = "LINESTRING("
linestring = linestring + str(clon) + " " + str(clat) + ","
linestring = linestring + str(pt.x) + " " + str(pt.y)
linestring = linestring + ")"
promenade = Infrastructure.objects.create(year=year)
promenade.name = "Promenade"
promenade.location_line = linestring
promenade.tags = 'road'
promenade.save()

# FENCE 	
dist_to_fence=7300

## top of pentagon aligned with 6'. make poly?
fence = Infrastructure.objects.create(year=year)
fence.name = 'fence'
polystring = "LINESTRING("
twelve = time2radial(0,0)
polystring = polystring + ret_point(clat,clon,dist_to_fence,twelve) + ","
polystring = polystring + ret_point(clat,clon,dist_to_fence,twelve+72) + ","
polystring = polystring + ret_point(clat,clon,dist_to_fence,twelve+144) + ","
polystring = polystring + ret_point(clat,clon,dist_to_fence,twelve+216) + ","
polystring = polystring + ret_point(clat,clon,dist_to_fence,twelve+288) + ","
polystring = polystring + ret_point(clat,clon,dist_to_fence,twelve+360)
polystring = polystring + ")"
fence.location_line = polystring
fence.tags = 'fence'
fence.save()

# PORTAPOTTY

## halfway between circular streets, offset from radial street
def potty_point(year, street1, street2, time):
  if time < 6:
    time = time - .03
  else:
    time = time + .03
  pt1 = geocode(year.year, math.floor(time), math.modf(time)[0] * 60, street1)
  pt2 = geocode(year.year, math.floor(time), math.modf(time)[0] * 60, street2)
  return str((pt1.x + pt2.x)/2) + ' ' + str((pt1.y + pt2.y)/2)
  
def create_potty(year,street1,street2,time):
	potty = Infrastructure.objects.create(year=year)
	potty.name = "toilets " + street1[0] + "/" + street2[0] + ":" + str(time)
	potty.location_point = "POINT(" + potty_point(year, street1, street2, time) + ")"
	potty.tags = 'toilet'
	potty.save()
	
C = CircularStreet.objects.filter(year=year,name__startswith='C')[0].name
D = CircularStreet.objects.filter(year=year,name__startswith='D')[0].name
E = CircularStreet.objects.filter(year=year,name__startswith='E').exclude(name__iexact='Esplanade').exclude(name__iexact='Evolution')[0].name
G = CircularStreet.objects.filter(year=year,name__startswith='G')[0].name
H = CircularStreet.objects.filter(year=year,name__startswith='H')[0].name
I = CircularStreet.objects.filter(year=year,name__startswith='I')[0].name

## C/D potties and H/I potties
for x in Numeric.arange(2.5,10,0.5):
  if x not in [3,6,9]:
		create_potty(year,C,D,x)
  if x not in [6]:
		create_potty(year,H,I,x)
  if x in [3,9]:
		create_potty(year,D,E,x)
  if x in [6]:
		create_potty(year,G,H,x)
    
# AIRPORT
radial = time2radial(4,35)
tmp = getpoint(clat,clon,dist_to_fence,-radial)
ls = LineString((clon,clat),(tmp.x,tmp.y))
airport_point = fence.location_line.intersection(ls)
airport = Infrastructure.objects.create(year=year)
airport.name = "Airport"
airport.location_point = airport_point
airport.tags = 'airport'
airport.save()

## AIRPORT ROAD
ar1 = geocode(year.year, 5, 0, L.name)
ls = LineString((ar1.x,ar1.y),(airport_point.x,airport_point.y))
airport_road = Infrastructure.objects.create(year=year)
airport_road.name = "Airport Road"
airport_road.location_line = ls
airport_road.tags = 'road'
airport_road.save()

## RUNWAY

# WALKIN CAMPING
polygon = "POLYGON(("
arc_start = time2radial(2,00)
arc_end = time2radial(5,00)
polygon = polygon + ret_arc(clat,clon,L.distance_from_center,int(arc_start),int(arc_end),1)
polygon = polygon + "," + str(airport.location_point.x) + " " + str(airport.location_point.y) 
polygon = polygon + "," + ret_point(clat,clon,dist_to_fence,twelve+72)
pt = GEOSGeometry("LINESTRING(" + str(clon) + " " + str(clat) + "," + ret_point(clat,clon,dist_to_fence,arc_start) + ")").intersection(fence.location_line)
polygon = polygon + "," + str(pt.x) + " " + str(pt.y)
polygon = polygon + "," + ret_street_point(year, 2, 0, L.name)
polygon = polygon + "))"
walkin_camping = Infrastructure.objects.create(year=year)
walkin_camping.name = "Walk-in Camping Area"
walkin_camping.location_poly = polygon
walkin_camping.tags = 'walkin_camp'
walkin_camping.save()
