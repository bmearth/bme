import logging
from piston.handler import BaseHandler, AnonymousBaseHandler
from piston.emitters import Emitter, JSONEmitter
from brc.models import *
from api.emitters import GeoJSONEmitter
from swingtime.models import Event, Occurrence
import time

JSONEmitter.unregister('json')
Emitter.register('json', GeoJSONEmitter, content_type='text/javascript; charset=utf-8')

art_fields = ('id', 'name', ('year', ('id','year')), 'slug', 'artist', 'description', 'url', 'contact_email', 'location_point', 'location_poly', 'circular_street', 'time_address')
event_fields = ('id', 'title','description', 'print_description', ('year', ('id','year')), 'slug', 'event_type', 'hosted_by_camp', 'located_at_art', 'other_location', 'check_location', 'url', 'contact_email', 'location_point', 'location_track', 'all_day', ('occurrence_set', ('start_time', 'end_time')))
camp_fields = ('id', ('year', ('id','year')), 'name', 'description', 'type', 'start_date_time', 'end_date_time', 'duration', 'repeats', 'hosted_by_camp', 'located_at_art', 'location_point', 'location_poly', 'url', 'contact_email') 
cstreet_fields = ('id', ('year', ('id','year')), 'name', 'order', 'width', 'distance_from_center', 'street_line')
tstreet_fields = ('id', ('year', ('id','year')), 'hour', 'minute', 'name', 'width', 'street_line')
year_fields = ('id', 'location', 'location_point', 'participants', 'theme')
user_fields = ('id', 'username', 'first_name', 'last_name', 'active')

class AnonymousArtInstallationHandler(BaseHandler):
	allow_methods = ('GET',)
	model = ArtInstallation 
	fields = art_fields
	
class ArtInstallationHandler(BaseHandler):
	allow_methods = ('GET',)
	model = ArtInstallation 
	fields = art_fields
	anonymous = AnonymousArtInstallationHandler

class AnonymousPlayaEventHandler(AnonymousBaseHandler):
	allow_methods = ('GET',)
	model = PlayaEvent 
	fields = event_fields 

	def read(self, request, year_year=None, playa_event_id=None):
		base = PlayaEvent.objects.filter(moderation='A', list_online=True)
		if(year_year):
		        year = Year.objects.get(year=year_year)
			if(playa_event_id):
				events = PlayaEvent.objects.filter(year=year,id=playa_event_id)
			else:
				if(request.GET.get('start_time') and request.GET.get('end_time')):
					event_list = Occurrence.objects.filter(start_time__gte=request.GET.get('start_time'), end_time__lte=request.GET.get('end_time')).values_list('event', flat=True)
					events = PlayaEvent.objects.filter(id__in=event_list)
				elif(request.GET.get('start_time')):
					event_list = Occurrence.objects.filter(start_time__gte=request.GET.get('start_time')).values_list('event', flat=True)
					events = PlayaEvent.objects.filter(id__in=event_list)
				elif(request.GET.get('end_time')):
					event_list = Occurrence.objects.filter(end_time__lte=request.GET.get('end_time')).values_list('event', flat=True)
					events = PlayaEvent.objects.filter(id__in=event_list)
				else:
	        			events = PlayaEvent.objects.filter(year=year)
			return events
		else:
			return base.all()

class PlayaEventHandler(BaseHandler):
	allow_methods = ('GET',)
	model = PlayaEvent 
	anonymous = AnonymousPlayaEventHandler
	fields = event_fields

class AnonymousThemeCampHandler(AnonymousBaseHandler):
	allow_methods = ('GET',)
	model = ThemeCamp 
	fields = camp_fields

class ThemeCampHandler(BaseHandler):
	allow_methods = ('GET',)
	model = ThemeCamp 
	fields = camp_fields
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
	fields = user_fields
