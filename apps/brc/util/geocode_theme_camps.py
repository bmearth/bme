import math

import sys,os
import urllib2
from BeautifulSoup import BeautifulSoup
import re

sys.path.append('../../../../pinax/apps')
sys.path.append('../../../../../src')
sys.path.append('../../../../../src/bme/apps')

os.environ['DJANGO_SETTINGS_MODULE'] ='bme.settings'

from brc.models import *
from brc.views import *

curr_year='2009'
year = Year.objects.get(year=curr_year)

(cc,dist_inner_ring,dist_outer_ring) = centercamp(year)

theme_camps = ThemeCamp.objects.filter(year=year)

x = re.compile('[a-zA-Z]{0,100} & \d{1,2}:\d{1,2} Portal')
a = re.compile('[a-zA-Z]{0,100} & \d{1,2}:\d{1,2}')
b = re.compile('\d{1,2}:\d{1,2} & [a-zA-Z]{0,100}')
c = re.compile('\d{1,2}:\d{1,2} Portal')
d = re.compile('\d{1,2}:\d{1,2} Plaza at \d{1,2}:\d{1,2}')
e = re.compile('\d{1,2}:\d{1,2} plaza at \d{1,2}:\d{1,2}')
f = re.compile('[a-zA-Z]{0,100} at \d{1,2}:\d{1,2}')
g = re.compile('[a-zA-Z]{0,100} &  \d{1,2}:\d{1,2}')
h = re.compile('Center Camp at \d{1,2}:\d{1,2}')
i = re.compile('[a-zA-Z]{0,100} and \d{1,2}:\d{1,2}')
j = re.compile('within [a-zA-Z]{0,100}')
k = re.compile('Within [a-zA-Z]{0,100}')

for camp in theme_camps:
	if(camp.location_string != None and camp.location_string.strip() == ""):
		camp.location_string = None
		camp.save()
	plaza_string = None	
	cstreet_string = None
	tstreet_string = None
	camp_name = None
	try:
		if(camp.location_string and camp.location_point == None):
			if(x.match(camp.location_string)):
				print camp, camp.location_string
				pass	
			elif(a.match(camp.location_string)):
				parts = camp.location_string.partition(' & ')
				cstreet_string = parts[0].strip()
				tstreet_string = parts[2].strip()
			elif(b.match(camp.location_string)):
				parts = camp.location_string.partition(' & ')
				cstreet_string = parts[2].strip()
				tstreet_string = parts[0].strip()
			elif(c.match(camp.location_string)):
				print camp, camp.location_string
				pass
			elif(d.match(camp.location_string)):
				parts = camp.location_string.partition(' Plaza at ')
				plaza_string = parts[0].strip()
				tstreet_string = parts[2].strip()
			elif(e.match(camp.location_string)):
				parts = camp.location_string.partition(' plaza at ')
				plaza_string = parts[0].strip()
				tstreet_string = parts[2].strip()
			elif(f.match(camp.location_string)):
				print camp, camp.location_string
				pass
			elif(g.match(camp.location_string)):
				print camp, camp.location_string
				pass
			elif(h.match(camp.location_string)):
				parts = camp.location_string.partition(' at ')
				cstreet_string = parts[2].strip()
				tstreet_string = parts[0].strip()
			elif(i.match(camp.location_string)):
				print camp, camp.location_string
				pass
			elif(j.match(camp.location_string)):
				camp_name = camp.location_string.replace('within ', '')
				camp_name = camp_name.replace('_', '')
			elif(k.match(camp.location_string)):
				camp_name = camp.location_string.replace('Within ', '')
				camp_name = camp_name.replace('_', '')
			else:
				print camp, camp.location_string
				pass

			if(plaza_string and tstreet_string):
				camp.time_address = tstreet_string.strip()
				time_parts = str(camp.time_address).split(':')
				hour = time_parts[0]
				minute = time_parts[1]
				angle = time2radial(hour, minute)
				
				plaza_parts = str(plaza_string).split(':')
				plaza_hour = time_parts[0]
				plaza_minutes= time_parts[1]
				(pt,plaza_radius) = plaza(year,plaza_hour,plaza_minutes)
				point = getpoint(pt.y,pt.x,plaza_radius,-angle)
				camp.location_point = point
				camp.save()
				
			elif(cstreet_string == "Evolution" and tstreet_string):
				camp.time_address = tstreet_string.strip()
				time_parts = str(camp.time_address).split(':')
				hour = time_parts[0]
				minutes = time_parts[1]
				angle = time2radial(hour, minutes)
				point = getpoint(cc.y,cc.x,dist_outer_ring,-angle)
				camp.location_point = point
				camp.save()
			elif(cstreet_string == "Center Camp" and tstreet_string):
				camp.time_address = tstreet_string.strip()
				time_parts = str(camp.time_address).split(':')
				hour = time_parts[0]
				minutes = time_parts[1]
				angle = time2radial(hour, minutse)
				point = getpoint(cc.y,cc.x,dist_inner_ring,-angle)
				camp.location_point = point
				camp.save()			
			elif(cstreet_string and tstreet_string):
				camp.time_address = tstreet_string.strip()
				cstreet = CircularStreet.objects.get(year=year, name=cstreet_string.strip())
				camp.circular_street = cstreet;
				time_parts = str(camp.time_address).split(':')
				hour = time_parts[0]
				minutes = time_parts[1]
				point = geocode('2009', hour, minutes, str(cstreet_string))
				camp.location_point = point
				camp.save()
			elif(camp_name):
				within_camp = ThemeCamp.objects.get(year=year, name=camp_name.strip())
				if(within_camp):
					camp.time_address = within_camp.time_address
					camp.circular_street = within_camp.circular_street
					camp.location_point = within_camp.location_point
					camp.save()
	except ValueError, msg:
		print msg
	except AttributeError, msg:
		print msg
	except NameError, msg:
		print msg
	except:
		print sys.exc_info()[0] 
		print camp, camp.location_string
