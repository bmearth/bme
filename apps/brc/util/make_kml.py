import sys,os

sys.path.append('/home/ortelius/projects')
os.environ['DJANGO_SETTINGS_MODULE'] ='bme.settings'

from bme.web.models import *

filename = "test.kml"

FILE = open(filename, "w")
FILE.writelines("<?xml version='1.0' encoding='UTF-8'?>")
FILE.writelines("<kml xmlns='http://earth.google.com/kml/2.1'>")
FILE.writelines("<Document>")

xyear = year.objects.filter(year='2008')

qs = time_street.objects.filter(year=xyear[0]).kml()

for x in qs:
	FILE.writelines("<Placemark>")
	FILE.writelines("<description>" + str(x.name) + "</description>")
	FILE.writelines("<name>" + str(x.name) + "</name>")

	FILE.writelines(x.kml)

	FILE.writelines("</Placemark>")

qs = circular_street.objects.filter(year=xyear[0]).kml()

for x in qs:
	FILE.writelines("<Placemark>")
	FILE.writelines("<description>" + str(x.name) + "</description>")
	FILE.writelines("<name>" + str(x.name) + "</name>")

	FILE.writelines(x.kml)

	FILE.writelines("</Placemark>")

FILE.writelines("</Document>")
FILE.writelines("</kml>")
FILE.close()
