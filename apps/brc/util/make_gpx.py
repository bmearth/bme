import sys,os

sys.path.append('/home/bme/src/pinax/apps')
sys.path.append('/home/bme/src')
sys.path.append('/home/bme/src/bme/apps')
os.environ['DJANGO_SETTINGS_MODULE'] ='bme.settings'

from brc.models import *

filename = "2009_art.gpx"

FILE = open(filename, "w")
FILE.writelines('<?xml version="1.0" encoding="ISO-8859-1" standalone="yes"?>')
FILE.writelines('<gpx')
FILE.writelines('  xmlns="http://www.topografix.com/GPX/1/0"')
FILE.writelines('  version="1.0" creator="Burning Man Earth"')
FILE.writelines('  xmlns:wissenbach="http://earth.burningman.com/"')
FILE.writelines('  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"')
FILE.writelines('  xsi:schemaLocation="http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd">')
FILE.writelines('<name>Black Rock City 2009 Art Installations</name>')
FILE.writelines('<url>http://earth.burningman.com</url>')
FILE.writelines('<urlname>Burning Man Earth</urlname>')


xyear = Year.objects.filter(year='2009')

qs = ArtInstallation.objects.filter(year=xyear[0]).kml()

for x in qs:
	if(x.location_point):
		print x
		FILE.writelines('<wpt lat="' + str(x.location_point.y) + '" lon="' + str(x.location_point.x) + '">')
		FILE.writelines('<name>' + str(x.bm_fm_id) + '</name>')
		FILE.writelines('<cmt>' + str(x.name) + '</cmt>')
		FILE.writelines('<description>' + str(unicode(x.name)) + '</description>')
		FILE.writelines('<sym>Dot</sym>')
		FILE.writelines('</wpt>')

FILE.writelines('</gpx>')
FILE.close()
