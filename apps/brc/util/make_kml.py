import sys,os

sys.path.append('/home/bme/src/pinax/apps')
sys.path.append('/home/bme/src')
sys.path.append('/home/bme/src/bme/apps')
os.environ['DJANGO_SETTINGS_MODULE'] ='bme.settings'

from brc.models import *

filename = "2009.kml"

FILE = open(filename, "w")
FILE.writelines("<?xml version='1.0' encoding='UTF-8'?>")
FILE.writelines("<kml xmlns='http://earth.google.com/kml/2.1'>")
FILE.writelines("<Document>")

xyear = Year.objects.filter(year='2009')

qs = TimeStreet.objects.filter(year=xyear[0]).kml()

for x in qs:
	FILE.writelines("<Placemark>")
	FILE.writelines("<description>" + str(x.name) + "</description>")
	FILE.writelines("<name>" + str(x.name) + "</name>")

	FILE.writelines(x.kml)

	FILE.writelines("</Placemark>")

qs = CircularStreet.objects.filter(year=xyear[0]).kml()

for x in qs:
	FILE.writelines("<Placemark>")
	FILE.writelines("<description>" + str(x.name) + "</description>")
	FILE.writelines("<name>" + str(x.name) + "</name>")

	FILE.writelines(x.kml)

	FILE.writelines("</Placemark>")

FILE.writelines("</Document>")
FILE.writelines("</kml>")
FILE.close()
