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

print("<?xml version='1.0' encoding='UTF-8'?>")
print("<osm version='0.6'>")

xyear = Year.objects.filter(year='2009')
time_streets = TimeStreet.objects.filter(year=xyear[0])
circular_streets = CircularStreet.objects.filter(year=xyear[0])

for t in time_streets:
	if (t.street_line):
		startnode = nodeid
		for p in t.street_line:
			print("<node id='" + str(nodeid) + "' visible='true' lat='" + str(p[1]) + "' lon='" + str(p[0]) + "' />")
			nodeid = nodeid - 1

		print("<way id='" + str(wayid) + "' visible='true'>")
		for z in range(startnode, nodeid, -1):
			print("<nd ref='" + str(z) + "' />")
		print("<tag k='highway' v='track'/>")
		print("</way>")

		wayid = wayid - 1

for t in circular_streets:
	if (t.street_line):
		startnode = nodeid
		for p in t.street_line:
			print("<node id='" + str(nodeid) + "' visible='true' lat='" + str(p[1]) + "' lon='" + str(p[0]) + "' />")
			nodeid = nodeid - 1

		print("<way id='" + str(wayid) + "' visible='true'>")
		for z in range(startnode, nodeid, -1):
			print("<nd ref='" + str(z) + "' />")
		print("</way>")

		wayid = wayid - 1

print("</osm>")
