import os, sys
import psycopg2
from pysqlite2 import dbapi2 as sqlite

sys.path.append('/home/bme/src/pinax/apps')
sys.path.append('/home/bme/src')
sys.path.append('/home/bme/src/bme')
sys.path.append('/home/bme/src/bme/apps')
os.environ['DJANGO_SETTINGS_MODULE'] ='bme.settings'

from brc.models import *
from django.contrib.auth.models import *

from swingtime.models import Event, Occurrence

#open sqlite connection
connection = sqlite.connect('iBurnDB.sqlite')
cursor = connection.cursor()

year = Year.objects.filter(year='2009')

try:
	cursor.execute('delete from theme_camp')
except:
	cursor.execute("CREATE TABLE IF NOT EXISTS 'theme_camp' ('pk' INTEGER NOT NULL, 'id' INTEGER, 'name' TEXT, 'year' INTEGER, 'description' TEXT, 'url' TEXT, 'contact_email' TEXT, 'hometown' TEXT, 'location' TEXT, 'circular_street' INTEGER, 'time_address' TEXT, 'latitude' FLOAT, 'longitude' FLOAT, 'image_url' TEXT)")


camps = ThemeCamp.objects.filter(year=4).extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')

count = 0
for camp in camps:
	try:
		if(camp.circular_street):
			cstreet = camp.circular_street.id
		else:
			cstreet = None
		if(camp.location_point):
			lon = camp.location_point.x
			lat = camp.location_point.y
		else:
			lon = None
			lat = None

		sql = 'INSERT INTO theme_camp (pk, id, name, year,  description, url, contact_email, hometown, location, circular_street, time_address, latitude, longitude, image_url) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)' 
		cursor.execute(sql,(count, camp.id, camp.name, int(camp.year.year), camp.description, camp.url, camp.contact_email, camp.hometown, camp.location_string, cstreet, str(camp.time_address), lat, lon, str(camp.image)))
		connection.commit()
		count += 1
	except sqlite.OperationalError, msg:
		print msg
	except sqlite.ProgrammingError, msg:
		print msg
	except:
		print sys.exc_info()
try:
	cursor.execute('delete from art_install')
except:
	cursor.execute("CREATE TABLE IF NOT EXISTS 'art_install' ('pk' INTEGER PRIMARY KEY  NOT NULL , 'id' INTEGER, 'year' INTEGER, 'name' TEXT, 'slug' TEXT, 'artist' TEXT, 'description' TEXT, 'url' TEXT, 'contact_email' TEXT, 'circular_street' INTEGER, 'time_address' TEXT, 'latitude' FLOAT, 'longitude' FLOAT, 'image_url' TEXT)")

art_installs = ArtInstallation.objects.filter(year=4).extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')

count = 0
for art in art_installs:
	try:
		if(art.location_point):
			lon = art.location_point.x
			lat = art.location_point.y
		else:
			lon = None
			lat = None
		sql = 'INSERT INTO art_install (pk, id, year, name, slug, artist, description, url, contact_email, image_url, latitude, longitude) VALUES (?,?,?, ?, ?, ?, ?,?, ?, ?, ?, ?)' 
		cursor.execute(sql,(count, art.id, int(art.year.year), art.name, art.slug, art.artist, art.description, art.url, art.contact_email, str(art.image), lat, lon))
		connection.commit()
		count += 1
	except sqlite.ProgrammingError, msg:
		print msg
	except:
		print sys.exc_info()[0]

try:
	cursor.execute('delete from user')
except:
	cursor.execute("CREATE TABLE IF NOT EXISTS 'user' ('pk' INTEGER PRIMARY KEY  NOT NULL , 'username' TEXT, 'name' TEXT, 'about' TEXT, 'location' TEXT, 'website' TEXT, 'email_address' TEXT, 'image_url' TEXT)")

for user in User.objects.all():
	try:
		sql = 'INSERT INTO user (pk, username, name, about, location, website, email_address, image_url) VALUES (?,?,?,?,?,?,?,?)'
		cursor.execute(sql, (user.id, user.username, user.username, '', '', '', user.email, ''))
		connection.commit()
	except AttributeError, msg:
		print msg
	except sqlite.OperationalError, msg:
		print msg
	except:
		print sys.exc_info()[0]

try:
	cursor.execute('delete from events')
except:
	cursor.execute("CREATE TABLE IF NOT EXISTS 'events' ('pk' INTEGER PRIMARY KEY NOT NULL, 'event_id' INTEGER, 'title' TEXT, 'description' TEXT, 'event_type' TEXT, 'camp' INTEGER, 'art' INTEGER, 'other_location' TEXT, 'website' TEXT, 'email_address' TEXT, 'latitude' FLOAT, 'longitude' FLOAT, 'all_day' BOOLEAN, 'start_time' TIMESTAMP, 'end_time' TIMESTAMP)")

occurrences = Occurrence.objects.select_related().filter(event__playaevent__moderation='A', event__playaevent__list_online=True)

count = 0
for occurrence in occurrences:
	count += 1
	try:
		if(occurrence.event.playaevent.location_point):
			lon = occurrence.event.playaevent.location_point.x
			lat = occurrence.event.playaevent.location_point.y
		else:
			lon = None
			lat = None

		if(occurrence.event.playaevent.hosted_by_camp):
			camp_id = occurrence.event.playaevent.hosted_by_camp.id
		else:
			camp_id = None

		if(occurrence.event.playaevent.located_at_art):
			art_id = occurrence.event.playaevent.located_at_art.id
		else:
			art_id = None

		sql = 'INSERT INTO events (pk, event_id, title, description, event_type, camp, art, other_location, website, email_address, latitude, longitude, all_day, start_time, end_time) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
		cursor.execute(sql, (count, occurrence.event.playaevent.id, occurrence.event.title, occurrence.event.description, occurrence.event.event_type.label, camp_id, art_id, occurrence.event.playaevent.other_location, occurrence.event.playaevent.url, occurrence.event.playaevent.contact_email, lat, lon, occurrence.event.playaevent.all_day, occurrence.start_time, occurrence.end_time))
		connection.commit()
	except AttributeError, msg:
		print msg
	except sqlite.OperationalError, msg:
		print msg
	except sqlite.InterfaceError, msg:
		print msg
	except:
		print sys.exc_info()[0]
