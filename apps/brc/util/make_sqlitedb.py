import os, sys
import psycopg2
from pysqlite2 import dbapi2 as sqlite

sys.path.append('/home/ortelius/projects/mobitag/src/pinax/apps')
sys.path.append('/home/ortelius/projects/mobitag/src')
sys.path.append('/home/ortelius/projects/bme')
sys.path.append('/home/ortelius/projects/bme/bme/apps')
os.environ['DJANGO_SETTINGS_MODULE'] ='bme.settings'

from brc.models import *
from django.contrib.auth.models import *

#open sqlite connection
connection = sqlite.connect('iBurnDB.sqlite')
cursor = connection.cursor()

try:
	cursor.execute('delete from theme_camp')
except:
	cursor.execute("CREATE TABLE IF NOT EXISTS 'theme_camp' ('pk' INTEGER NOT NULL, 'name' TEXT, 'year' INTEGER, 'description' TEXT, 'url' TEXT, 'contact_email' TEXT, 'hometown' TEXT, 'circular_street' INTEGER, 'time_address' TEXT, 'latitude' FLOAT, 'longitude' FLOAT, 'image_url' TEXT)")


camps = ThemeCamp.objects.filter(year=4).extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')

for camp in camps:
	try:
		sql = 'INSERT INTO theme_camp (pk, name, year,  description, url, contact_email, hometown, circular_street, time_address, latitude, longitude, image_url) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)' 
		cursor.execute(sql,(camp.id, camp.name, int(camp.year.year), camp.description, camp.url, camp.contact_email, camp.hometown, camp.circular_street, camp.time_address, 1.0, 1.0, str(camp.image)))
		connection.commit()
	except:
		print sys.exc_info()[0]

try:
	cursor.execute('delete from art_install')
except:
	cursor.execute("CREATE TABLE IF NOT EXISTS 'art_install' ('pk' INTEGER PRIMARY KEY  NOT NULL , 'year' INTEGER, 'name' TEXT, 'slug' TEXT, 'artist' TEXT, 'description' TEXT, 'url' TEXT, 'contact_email' TEXT, 'circular_street' INTEGER, 'time_address' TEXT, 'latitude' FLOAT, 'longitude' FLOAT, 'image_url' TEXT)")

art_installs = ArtInstallation.objects.filter(year=4).extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')

for art in art_installs:
	try:
		sql = 'INSERT INTO art_install (pk, year, name, slug, artist, description, url, contact_email, image_url) VALUES (?,?, ?, ?, ?, ?,?, ?, ?)' 
		cursor.execute(sql,(art.id, int(art.year.year), art.name, art.slug, art.artist, art.description, art.url, art.contact_email, str(art.image)))
		connection.commit()
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
