from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.emitters import Emitter, JSONEmitter
from brc.models import *
from api.emitters import GeoJSONEmitter

JSONEmitter.unregister('json')
Emitter.register('json', GeoJSONEmitter, content_type='text/javascript; charset=utf-8')

art_fields = ('id', 'name', 'year', 'slug', 'artist', 'description', 'url', 'contact_email', 'location_point', 'location_poly', 'circular_street', 'time_address')
playa_fields = ('id', 'name', 'year', 'description', 'url', 'contact_email', 'hometown', 'location_point', 'location_poly', 'circular_street', 'time_address', 'participants')
theme_fields = ('id', 'year', 'name', 'description', 'type', 'start_date_time', 'end_date_time', 'duration', 'repeats', 'hosted_by_camp', 'located_at_art', 'location_point', 'location_poly', 'url', 'contact_email') 
cstreet_fields = ('id', 'year', 'name', 'order', 'width', 'distance_from_center', 'street_line')
tstreet_fields = ('id', 'year', 'hour', 'minute', 'name', 'width', 'street_line')
year_fields = ('id', 'location', 'location_point', 'participants', 'theme')
user_fields = ('id', 'username', 'first_name', 'last_name', 'active')

class AnonymousArtInstallationHandler(BaseHandler):
	allow_methods = ('GET',)
	model = ArtInstallation 
	fields = art_installation_fields
	
class ArtInstallationHandler(BaseHandler):
	allow_methods = ('GET',)
	model = ArtInstallation 
	fields = art_installation_fields
	anonymous = AnonymousArtInstallationHandler

class AnonymousPlayaEventHandler(AnonymousBaseHandler):
	allow_methods = ('GET',)
	model = PlayaEvent 
	fields = playa_fields

class PlayaEventHandler(BaseHandler):
	allow_methods = ('GET',)
	model = PlayaEvent 
	fields = playa_fields
	anonymous = AnonymousPlayaEventHandler

class AnonymousThemeCampHandler(AnonymousBaseHandler):
	allow_methods = ('GET',)
	model = ThemeCamp 
	fields = theme_fields

class ThemeCampHandler(BaseHandler):
	allow_methods = ('GET',)
	model = ThemeCamp 
	fields = theme_fields
	anonymous = AnonymousThemeCampHandler

class AnonymousCircularStreetHandler(AnonymousBaseHandler):
	allow_methods = ('GET',)
	model = CircularStreet 
	fields = cstreet_fields

class CircularStreetHandler(BaseHandler):
	allow_methods = ('GET',)
	model = CircularStreet 
	fields = cstreet_fields
	anonymous = AnonymousCircularStreetHandler

class AnonymousTimeStreetHandler(AnonymousBaseHandler):
	allow_methods = ('GET',)
	model = TimeStreet
	fields = tstreet_fields

class TimeStreetHandler(BaseHandler):
	allow_methods = ('GET',)
	model = TimeStreet
	fields = tstreet_fields
	anonymous = AnonymousTimeStreetHandler

class AnonymousYearHandler(AnonymousBaseHandler):
	allow_methods = ('GET',)
	model = Year   
	fields = year_fields

class YearHandler(BaseHandler):
	allow_methods = ('GET',)
	model = Year
	fields = year_fields
	anonymous = AnonymousYearHandler

class UserHandler(BaseHandler):
	allow_methods = ('GET',)
	model = User
	fields = user_fie