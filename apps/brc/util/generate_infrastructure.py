import sys,os
import math
from django.contrib.gis.geos import *

sys.path.append('../../../../bme/src/pinax/apps')
sys.path.append('../../../..')
sys.path.append('../../../../bme/apps')

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
(cc,dist_inner_ring,dist_outer_ring) = centercamp(year)

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
B = CircularStreet.objects.filter(year=year,name__startswith='B')[0]
D = CircularStreet.objects.filter(year=year,name__startswith='D')[0]
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
E = CircularStreet.objects.filter(year=year,name__startswith='E').exclude(name__iexact='Esplanade').exclude(name__iexact='Evolution')[0].name
L = CircularStreet.objects.filter(year=year,name__startswith='L')[0]
geom_collection = "GEOMETRYCOLLECTION("

geom_collection = geom_collection + "POLYGON(("
geom_collection = geom_collection + ret_street_point(year,8,0,D.name) + ","
geom_collection = geom_collection + ret_street_point(year,8,30,D.name) + ","
geom_collection = geom_collection + ret_street_point(year,8,30,L.name) + ","
geom_collection = geom_collection + ret_street_point(year,8,0,L.name) + ","
geom_collection = geom_collection + ret_street_point(year,8,0,D.name)
geom_collection = geom_collection + ")),"

geom_collection = geom_collection + "POLYGON(("
geom_collection = geom_collection + ret_street_point(year,5,0,D.name) + ","
geom_collection = geom_collection + ret_street_point(year,7,0,D.name) + ","
geom_collection = geom_collection + ret_street_point(year,7,0,L.name) + ","
geom_collection = geom_collection + ret_street_point(year,5,0,L.name) + ","
geom_collection = geom_collection + ret_street_point(year,5,0,D.name)
geom_collection = geom_collection + ")),"

geom_collection = geom_collection + "POLYGON(("
geom_collection = geom_collection + ret_street_point(year,3,30,D.name) + ","
geom_collection = geom_collection + ret_street_point(year,4,0,D.name) + ","
geom_collection = geom_collection + ret_street_point(year,4,0,L.name) + ","
geom_collection = geom_collection + ret_street_point(year,3,30,L.name) + ","
geom_collection = geom_collection + ret_street_point(year,3,30,D.name)
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

# ENTRANCE ROADS (HARDCODED! -- CONTACT GATE CREW FOR UPDATE)
entrance_road = Infrastructure.objects.create(year=year)
entrance_road.name = "entrance"
entrance_road.location_line = "LINESTRING(-119.239315394275 40.7610286856975,-119.236633185256 40.7621988830906,-119.236354235516 40.762410166535,-119.236161116469 40.7626051968109,-119.235903624409 40.762913993577,-119.235689047681 40.7633203029263,-119.235581759327 40.7636778530985,-119.235581759327 40.7640354013478)"
entrance_road.tags = 'road'
entrance_road.save()

entrance_road = Infrastructure.objects.create(year=year)
entrance_road.name = "entrance"
entrance_road.location_line = "LINESTRING(-119.236590269932 40.7622151356829,-119.236010912781 40.7622638934485,-119.235302809605 40.7622476408642,-119.23487365616 40.7621826304856,-119.234487418065 40.7621013674241,-119.234079722291 40.761971346318)"
entrance_road.tags = 'road'
entrance_road.save()

entrance_road = Infrastructure.objects.create(year=year)
entrance_road.name = "entrance"
entrance_road.location_line = "LINESTRING(-119.237985018613 40.7615975342256,-119.23810303581 40.7613862481983,-119.238306883695 40.761256225693,-119.238478545071 40.7611749614988,-119.238671664118 40.7610936972048,-119.238907698507 40.7610327489191,-119.239116910815 40.7610043063667,-119.239326123119 40.7610327489191)"
entrance_road.tags = 'road'
entrance_road.save()

entrance_road = Infrastructure.objects.create(year=year)
entrance_road.name = "entrance"
entrance_road.location_line = "LINESTRING(-119.235270623067 40.7622313882786,-119.236225489472 40.7625158080043)"
entrance_road.tags = 'road'
entrance_road.save()


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
D = CircularStreet.objects.filter(year=year,name__startswith='D')[0]
E = CircularStreet.objects.filter(year=year,name__startswith='E').exclude(name__iexact='Esplanade').exclude(name__iexact='Evolution')[0].name
G = CircularStreet.objects.filter(year=year,name__startswith='G')[0]
H = CircularStreet.objects.filter(year=year,name__startswith='H')[0].name
I = CircularStreet.objects.filter(year=year,name__startswith='I')[0].name

## C/D potties and H/I potties
for y in range(5,20):
  x = float(y)/2
  if x not in [3,6,9]:
		create_potty(year,C,D.name,x)
  if x not in [6]:
		create_potty(year,H,I,x)
  if x in [3,9]:
		create_potty(year,D.name,E,x)
  if x in [6]:
		create_potty(year,G.name,H,x)
    
# AIRPORT (ONSITE DETERMINED)!
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

## RUNWAY (HARDCODED!)
airport_runway = Infrastructure.objects.create(year=year)
airport_runway.name = "Runway"
airport_runway.location_line = "LINESTRING(-119.226762656086 40.747326091884,-119.212171439046 40.7499595497597)"
airport_runway.tags = 'runway'
airport_runway.save()

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

# PLAZAS

## 3:00 plaza
(pt,plaza_radius) = plaza(year,3,0)

angle_start = int(time2radial(2,55))
angle_end = int(time2radial(3,05))
polystring = "POLYGON(("
polystring = polystring + ret_arc(clat,clon,Esplanade.distance_from_center,angle_start,angle_end,1)
polystring = polystring + "," + str(pt.x) + " " + str(pt.y)
polystring = polystring + "," + ret_point(clat,clon,Esplanade.distance_from_center,angle_start)
polystring = polystring + "))"
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = polystring
plaza.tags = 'plaza'
plaza.save()

plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = "POLYGON((" + ret_arc(pt.y,pt.x,plaza_radius,0,360,1) + "))"
plaza.tags = 'plaza'
plaza.save()

## 9:00 plaza
(pt,plaza_radius) = plaza(year,9,0)

angle_start = int(time2radial(8,55))
angle_end = int(time2radial(9,05))
polystring = "POLYGON(("
polystring = polystring + ret_arc(clat,clon,Esplanade.distance_from_center,angle_start,angle_end,1)
polystring = polystring + "," + str(pt.x) + " " + str(pt.y)
polystring = polystring + "," + ret_point(clat,clon,Esplanade.distance_from_center,angle_start)
polystring = polystring + "))"
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = polystring
plaza.tags = 'plaza'
plaza.save()

plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = "POLYGON((" + ret_arc(pt.y,pt.x,plaza_radius,0,360,1) + "))"
plaza.tags = 'plaza'
plaza.save()

## 4:30 plaza
(pt,plaza_radius) = plaza(year,4,30)
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = "POLYGON((" + ret_arc(pt.y,pt.x,plaza_radius,0,360,1) + "))"
plaza.tags = 'plaza'
plaza.save()

A = CircularStreet.objects.filter(year=year,name__startswith='A')[0]
angle_start = int(time2radial(4,25))
angle_end = int(time2radial(4,35))
polystring = "POLYGON(("
polystring = polystring + ret_arc(clat,clon,Esplanade.distance_from_center,angle_start,angle_end,1)
pt = geocode(yea.year, 4, 30, A.name)
polystring = polystring + "," + str(pt.x) + " " + str(pt.y)
polystring = polystring + "," + ret_point(clat,clon,Esplanade.distance_from_center,angle_start)
polystring = polystring + "))"
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = polystring
plaza.tags = 'plaza'
plaza.save()

## 7:30 plaza
(pt,plaza_radius) = plaza(year,7,30)
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = "POLYGON((" + ret_arc(pt.y,pt.x,plaza_radius,0,360,1) + "))"
plaza.tags = 'plaza'
plaza.save()

A = CircularStreet.objects.filter(year=year,name__startswith='A')[0]
angle_start = int(time2radial(7,25))
angle_end = int(time2radial(7,35))
polystring = "POLYGON(("
polystring = polystring + ret_arc(clat,clon,Esplanade.distance_from_center,angle_start,angle_end,1)
pt = geocode(year.year, 7, 30, A.name)
polystring = polystring + "," + str(pt.x) + " " + str(pt.y)
polystring = polystring + "," + ret_point(clat,clon,Esplanade.distance_from_center,angle_start)
polystring = polystring + "))"
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = polystring
plaza.tags = 'plaza'
plaza.save()

## center camp
angle_start = int(time2radial(5,30))
angle_end = int(time2radial(6,30))
polystring = "POLYGON(("
polystring = polystring + ret_arc(cc.y,cc.x,dist_outer_ring,angle_start,angle_end,1)
polystring = polystring + "," + str(cc.x) + " " + str(cc.y)
polystring = polystring + "," + ret_point(cc.y,cc.x,dist_outer_ring,angle_start)
polystring = polystring + "))"
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = polystring
plaza.tags = 'plaza'
plaza.save()

polystring = "POLYGON((" + ret_arc(cc.y,cc.x,dist_inner_ring,0,360,1) + "))"
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = polystring
plaza.tags = 'plaza'
plaza.save()

## playa
fire_circle_radius = 300
polystring = "POLYGON((" + ret_arc(clat,clon,fire_circle_radius,0,360,1) + "))"
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = polystring
plaza.tags = 'plaza'
plaza.save()

temple_radius = 100 #determined ONSITE
pt = geocode(year.year,0,0,'Esplanade')
polystring = "POLYGON((" + ret_arc(pt.y,pt.x,temple_radius,0,360,1) + "))"
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = polystring
plaza.tags = 'plaza'
plaza.save()

# DPW/Fire
dpw_radius = 200 #determined ONSITE

pt = geocode(year.year, 5, 30, L.name)
angle = int(time2radial(5,30))
pt2 = getpoint(clat,clon,L.distance_from_center + 550,-angle)
ls = LineString((pt.x,pt.y),(pt2.x,pt2.y))
dpw_road = Infrastructure.objects.create(year=year)
dpw_road.name = ""
dpw_road.location_line = ls
dpw_road.tags = 'road'
dpw_road.save()

polystring = "POLYGON((" + ret_arc(pt2.y,pt2.x,dpw_radius,0,360,1) + "))"
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = polystring
plaza.tags = 'plaza'
plaza.save()

pt = geocode(year.year, 6, 30, L.name)
angle = int(time2radial(6,30))
pt2 = getpoint(clat,clon,L.distance_from_center + 550,-angle)
ls = LineString((pt.x,pt.y),(pt2.x,pt2.y))
dpw_road = Infrastructure.objects.create(year=year)
dpw_road.name = ""
dpw_road.location_line = ls
dpw_road.tags = 'road'
dpw_road.save()

polystring = "POLYGON((" + ret_arc(pt2.y,pt2.x,dpw_radius,0,360,1) + "))"
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = polystring
plaza.tags = 'plaza'
plaza.save()

# Fire barrells
fire_barrell_offset = 50
for x in range(2,10):
	fire = Infrastructure.objects.create(year=year)
	fire.name = "Fire Barrell"
	fire.location_point =	"POINT(" + ret_point(clat,clon,Esplanade.distance_from_center-fire_barrell_offset,time2radial(x,30)) + ")"
	fire.tags = 'firebarrell'
	fire.save()

J = CircularStreet.objects.filter(year=year,name__startswith='J')[0]
for x in (A,D,G,J):
	fire = Infrastructure.objects.create(year=year)
	fire.name = "Fire Barrell"
	fire.location_point =	"POINT(" + ret_point(clat,clon,x.distance_from_center,time2radial(1,57)) + ")"
	fire.tags = 'firebarrell'
	fire.save()
	
	fire = Infrastructure.objects.create(year=year)
	fire.name = "Fire Barrell"
	fire.location_point =	"POINT(" + ret_point(clat,clon,x.distance_from_center,time2radial(10,03)) + ")"
	fire.tags = 'firebarrell'
	fire.save()
