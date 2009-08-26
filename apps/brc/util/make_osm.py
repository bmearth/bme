import sys,os

sys.path.append('/home/bme/src/pinax/apps')
sys.path.append('/home/bme/src')
sys.path.append('/home/bme/src/bme/apps')

os.environ['DJANGO_SETTINGS_MODULE'] ='bme.settings'

from brc.models import *
from brc.views import *

from time import strftime

nodeid = -1
wayid = -1
nodes = {}

print("<?xml version='1.0' encoding='UTF-8'?>")
print("<osm version='0.6'>")

xyear = Year.objects.filter(year='2009')
time_streets = TimeStreet.objects.filter(year=xyear[0])
circular_streets = CircularStreet.objects.filter(year=xyear[0])
toilets = Infrastructure.objects.filter(year=xyear[0],tags='toilet')
fence = Infrastructure.objects.filter(year=xyear[0],tags='fence')
closure = Infrastructure.objects.filter(year=xyear[0],tags='closure')
gate = Infrastructure.objects.filter(year=xyear[0],tags='gate')
airport = Infrastructure.objects.filter(year=xyear[0],tags='airport')
runway = Infrastructure.objects.filter(year=xyear[0],tags='runway')
roads = Infrastructure.objects.filter(year=xyear[0],tags='road')
walkin_camp = [] #Infrastructure.objects.filter(year=xyear[0],tags='walkin_camp')
plazas = Infrastructure.objects.filter(year=xyear[0],tags='plaza')
fires = Infrastructure.objects.filter(year=xyear[0],tags='firebarrell')
art =  []# ArtInstallation.objects.filter(year=xyear[0])
camps = []#ThemeCamp.objects.filter(year=xyear[0])

cc_outer_ring = Infrastructure.objects.filter(year=xyear[0],name='Evolution')[0].location_line.convex_hull
double_wide = Infrastructure.objects.filter(year=xyear[0],tags='camp_null')[0].location_multigeom

def add_node(lat,lon):
	global nodeid
	global nodes
	if (nodes.get(str(lat) + '_' + str(lon),0) == 0):
		print("<node id='" + str(nodeid) + "' visible='true' lat='" + str(lat) + "' lon='" + str(lon) + "' />")
		nodes[str(lat) + '_' + str(lon)] = nodeid
		nodeid = nodeid - 1
	return nodes[str(lat) + '_' + str(lon)]

def add_street(t):
	global wayid
	u = t.street_line.difference(cc_outer_ring)
	if (t.name[0] == 'E') or (t.name[0] == 'B'):
		u = u.difference(double_wide)
	if (t.name == "06:30" or t.name == 
"05:30"):
		u = u[1]		
	if (u.geom_type == "LineString"):
		ls = [u]
	else:
		ls = u
	for v in ls:
		waynodes = []
		for p in v:
			waynodes.append( add_node(p[1], p[0]) )

		print("<way id='" + str(wayid) + "' visible='true'>")
		for n in waynodes:
			print("<nd ref='" + str(n) + "' />")
		print("<tag k='name' v='" + t.name + "'/>")
		print("<tag k='highway' v='track'/>")
		print("</way>")
		wayid = wayid - 1	
		
for t in time_streets:
	if (t.street_line):
		add_street(t)

for t in circular_streets:
	if (t.street_line):
		add_street(t)

for t in toilets:
	print("<node id='" + str(nodeid) + "' visible='true' lat='" + str(t.location_point.y) + "' lon='" + str(t.location_point.x) + "' >")
	print("<tag k='amenity' v='toilets'/>")
	print("</node>")
	nodeid = nodeid - 1

for t in closure:
	startnode = nodeid
	for l in t.location_poly:
		for p in l:
			print("<node id='" + str(nodeid) + "' visible='true' lat='" + str(p[1]) + "' lon='" + str(p[0]) + "' />")
			nodeid = nodeid - 1

	print("<way id='" + str(wayid) + "' visible='true'>")
	for z in range(startnode, nodeid, -1):
		print("<nd ref='" + str(z) + "' />")
	print("<tag k='boundary' v='administrative'/>")
	print("<tag k='admin_level' v='7'/>")
	print("</way>")
	wayid = wayid - 1

for t in fence:
	startnode = nodeid
	for p in t.location_line:
		print("<node id='" + str(nodeid) + "' visible='true' lat='" + str(p[1]) + "' lon='" + str(p[0]) + "' />")
		nodeid = nodeid - 1

	print("<way id='" + str(wayid) + "' visible='true'>")
	for z in range(startnode, nodeid, -1):
		print("<nd ref='" + str(z) + "' />")
	print("<tag k='barrier' v='fence'/>")
	print("<tag k='boundary' v='administrative'/>")
	print("<tag k='admin_level' v='8'/>")
	print("</way>")
	wayid = wayid - 1

for t in gate:
	print("<node id='" + str(nodeid) + "' visible='true' lat='" + str(t.location_point.y) + "' lon='" + str(t.location_point.x) + "' >")
	print("<tag k='barrier' v='gate'/>")
	print("</node>")
	nodeid = nodeid - 1

for t in airport:
	print("<node id='" + str(nodeid) + "' visible='true' lat='" + str(t.location_point.y) + "' lon='" + str(t.location_point.x) + "' >")
	print("<tag k='aeroway' v='aerodrome'/>")
	print("</node>")
	nodeid = nodeid - 1


for t in runway:
	if (t.location_line):
		waynodes = []
		for p in t.location_line:
			waynodes.append( add_node(p[1], p[0]) )

		print("<way id='" + str(wayid) + "' visible='true'>")
		for n in waynodes:
			print("<nd ref='" + str(n) + "' />")
		print("<tag k='aeroway' v='runway'/>")
		print("<tag k='name' v='" + t.name + "'/>")
		print("</way>")

		wayid = wayid - 1

for t in roads:
	if (t.location_line):
		waynodes = []
		for p in t.location_line:
			waynodes.append( add_node(p[1], p[0]) )

		print("<way id='" + str(wayid) + "' visible='true'>")
		for n in waynodes:
			print("<nd ref='" + str(n) + "' />")
		print("<tag k='highway' v='track'/>")
		print("<tag k='name' v='" + t.name + "'/>")
		print("</way>")

		wayid = wayid - 1

for t in walkin_camp:
	if (t.location_poly):
		waynodes = []
		for p in t.location_poly[0]:
			waynodes.append( add_node(p[1], p[0]) )

		print("<way id='" + str(wayid) + "' visible='true'>")
		for n in waynodes:
			print("<nd ref='" + str(n) + "' />")
		print("<tag k='tourism' v='camp_site'/>")
		print("<tag k='name' v='" + t.name + "'/>")
		print("</way>")

		wayid = wayid - 1

for t in camps:
	name = t.name.replace("&","&amp;").replace("'","&apos;")
	if (t.location_poly):
		waynodes = []
		for p in t.location_poly[0]:
			waynodes.append( add_node(p[1], p[0]) )

		print("<way id='" + str(wayid) + "' visible='true'>")
		for n in waynodes:
			print("<nd ref='" + str(n) + "' />")
		print("<tag k='tourism' v='camp_site'/>")
		print("<tag k='name' v='" + name + "'/>")
		print("</way>")

		wayid = wayid - 1			

		if (t.location_point):
			print("<node id='" + str(nodeid) + "' visible='true' lat='" + str(t.location_point.y) + "' lon='" + str(t.location_point.x) + "' >")
			print("<tag k='tourism' v='camp_site'/>")
			print("<tag k='name' v='" + name + "'/>")
			print("</node>")
			nodeid = nodeid - 1

for t in plazas:
	if (t.location_poly):
		waynodes = []
		for p in t.location_poly[0]:
			waynodes.append( add_node(p[1], p[0]) )

		print("<way id='" + str(wayid) + "' visible='true'>")
		for n in waynodes:
			print("<nd ref='" + str(n) + "' />")
		print("<tag k='highway' v='pedestrian'/>")
		print("<tag k='area' v='yes'/>")
		print("</way>")

		wayid = wayid - 1			

for t in fires:
	print("<node id='" + str(nodeid) + "' visible='true' lat='" + str(t.location_point.y) + "' lon='" + str(t.location_point.x) + "' >")
	print("<tag k='amenity' v='recycling'/>")
	print("</node>")
	nodeid = nodeid - 1		

for t in art:
  if (t.location_point):
  	name = t.name.replace("'","&apos;")
	print("<node id='" + str(nodeid) + "' visible='true' lat='" + str(t.location_point.y) + "' lon='" + str(t.location_point.x) + "' >")
	print("<tag k='tourism' v='museum'/>")
	print("<tag k='name' v='" + name + "'/>")
	print("</node>")
	nodeid = nodeid - 1
				
print("</osm>")
