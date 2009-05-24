from piston.handler import BaseHandler
from piston.emitters import Emitter, JSONEmitter
from brc.models import *
from api.emitters import GeoJSONEmitter

JSONEmitter.unregister('json')
Emitter.register('json', GeoJSONEmitter, content_type='text/javascript; charset=utf-8')

class ArtInstallationHandler(BaseHandler):
	allow_methods = ('GET',)
	model = ArtInstallation 
	fields = ('id', 'name', 'year', 'slug', 'artist', 'description', 'url', 'contact_email', 'location_point', 'location_poly', 'circular_street', 'time_address')

	@classmethod
	def read(self, request):
		base = ArtInstallation.objects
		return base.all()

class PlayaEventHandler(BaseHandler):
	allow_methods = ('GET',)
	model = PlayaEvent 
	fields = ('id', 'name', 'year', 'description', 'url', 'contact_email', 'hometown', 'location_point', 'location_poly', 'circular_street', 'time_address', 'participants')

	@classmethod
	def read(self, request):
		base = PlayaEvent.objects
		return base.all()

class ThemeCampHandler(BaseHandler):
	allow_methods = ('GET',)
	model = ThemeCamp 
	fields = ('id', 'year', 'name', 'description', 'type', 'start_date_time', 'end_date_time', 'duration', 'repeats', 'hosted_by_camp', 'located_at_art', 'location_point', 'location_track', 'url', 'contact_email') 

	@classmethod
	def read(self, request):
		base = ThemeCamp.objects
		return base.all()

class CircularStreetHandler(BaseHandler):
	allow_methods = ('GET',)
	model = CircularStreet 

	fields = ('id', 'year', 'name', 'order', 'width', 'distance_from_center', 'street_line')

	@classmethod
	def read(self, request):
		base = CircularStreet.objects
		return base.all()

class TimeStreetHandler(BaseHandler):
	allow_methods = ('GET',)
	model = TimeStreet

	fields = ('id', 'year', 'hour', 'minute', 'name', 'width', 'street_line')

	@classmethod
	def read(self, request):
		base = TimeStreet.objects
		return base.all()

class YearHandler(BaseHandler):
	allow_methods = ('GET',)
	model = Year   

	fields = ('id', 'location', 'location_point', 'participants', 'theme')

	@classmethod
	def read(self, request):
		base = Year.objects
		return base.all()

class UserHandler(BaseHandler):
	allow_methods = ('GET',)
	model = User

	fields = ('id', 'username', 'first_name', 'last_name', 'active') 

	@classmethod
	def read(self, request):
		base = User.objects
		return base.all()
