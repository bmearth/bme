import math
import csv

from datetime import datetime, date, time
from django.shortcuts import get_object_or_404, render_to_response
from django.core.paginator import InvalidPage
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.gis.geos import *
from django.contrib.auth.decorators import login_required
from django.views.generic.create_update import delete_object
from django.db.models import Count
from django.contrib.auth.models import AnonymousUser

from swingtime.models import Event, Occurrence
from swingtime import utils, forms
from swingtime.views import *
from olwidget.widgets import MapDisplay
from brc.models import *
from brc import forms as brcforms

from dateutil import parser

if swingtime_settings.CALENDAR_FIRST_WEEKDAY is not None:
    calendar.setfirstweekday(swingtime_settings.CALENDAR_FIRST_WEEKDAY)

def index(request, template_name="brc/index.html"):
	years = Year.objects.all().order_by('-year')
	return render_to_response(template_name, {"years": years,}, context_instance=RequestContext(request))

def apidocs(request):
	return render_to_response('brc/apidocs.html',context_instance=RequestContext(request))
	

#-------------------------------------------------------------------------------
#---------- Map ----------
#-------------------------------------------------------------------------------
def map(request, year_year):
	xyear = Year.objects.filter(year=year_year)
	streets = CircularStreet.objects.filter(year=xyear[0])
	previous = int(year_year) -1
	next = int(year_year) + 1
	return render_to_response('brc/map.html', {'year': xyear[0],
						'previous' : previous,
						'next' : next,}, context_instance=RequestContext(request))
def mobile_map(request, year_year):
	return render_to_response('brc/mobile_map.html', context_instance=RequestContext(request))

def sikrit_map(request, year_year):
	return render_to_response('brc/sikrit_map.html', context_instance=RequestContext(request))

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#---------- Globe ----------
#-------------------------------------------------------------------------------
def globe(request, year_year):
	xyear = Year.objects.filter(year=year_year)
	streets = CircularStreet.objects.filter(year=xyear[0])
	previous = int(year_year) -1
	next = int(year_year) + 1
	return render_to_response('brc/globe.html', {'year': xyear[0],
						'previous' : previous,
						'next' : next,}, context_instance=RequestContext(request))



#-------------------------------------------------------------------------------
#---------- Year ----------
#-------------------------------------------------------------------------------

def year_info(request, year_year):
	xyear = Year.objects.filter(year=year_year)
	streets = CircularStreet.objects.filter(year=xyear[0])
	previous = int(year_year) -1
	next = int(year_year) + 1
	return render_to_response('brc/year.html', {'year': xyear[0],
						'streets' : streets,
						'previous' : previous,
						'next' : next,}, context_instance=RequestContext(request))

#-------------------------------------------------------------------------------
#---------- Art Installations ----------
#-------------------------------------------------------------------------------

def art_installation_id(request, year_year, art_installation_id):
	xyear = Year.objects.filter(year=year_year)
	xArtInstallation = ArtInstallation.objects.get(id=art_installation_id)
	events = PlayaEvent.objects.filter(located_at_art=xArtInstallation, moderation='A')
	if xArtInstallation.location_point:
		map = MapDisplay(map_options={'default_lat': xArtInstallation.location_point.y, 'default_lon': xArtInstallation.location_point.x, 'default_zoom': 17, 'layers': ['osm.bme'], 'map_style':{'width':'400px','height':'400px'}})
	else:
		map = ''
	return render_to_response('brc/art_installation.html', {'year': xyear[0],
							'art_installation': xArtInstallation,'events': events,'map':map}, context_instance=RequestContext(request))

def art_installation_uuid(request, art_installation_id):
	xArtInstallation = ArtInstallation.objects.get(id=art_installation_id)
	xyear = xArtInstallation.year
	events = PlayaEvent.objects.filter(located_at_art=xArtInstallation, moderation='A')
	if xArtInstallation.location_point:
		map = MapDisplay(map_options={'default_lat': xArtInstallation.location_point.y, 'default_lon': xArtInstallation.location_point.x, 'default_zoom': 17, 'layers': ['osm.bme'], 'map_style':{'width':'400px','height':'400px'}})
	else:
		map = ''
	return render_to_response('brc/art_installation.html', {'year': xyear,
							'art_installation': xArtInstallation,'events': events,'map':map}, context_instance=RequestContext(request))

def art_installation_name(request, year_year, art_installation_name):
	xyear = Year.objects.filter(year=year_year)
	xArtInstallation = ArtInstallation.objects.filter(year=xyear[0],slug=art_installation_name)
	return render_to_response('brc/art_installation.html', {'year': xyear[0],
							'art_installation': xArtInstallation[0],}, context_instance=RequestContext(request))

def art_installations(request, year_year):
	xyear = Year.objects.filter(year=year_year)
	previous = int(year_year) -1
	next = int(year_year) + 1
	ArtInstallations = ArtInstallation.objects.filter(year=xyear[0]).extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
	return render_to_response('brc/art_installations.html', {'year': xyear[0],
							'art_installations': ArtInstallations,
							'previous' : previous,
							'next' : next,}, context_instance=RequestContext(request))

#-------------------------------------------------------------------------------
#---------- ThemeCamps ----------
#-------------------------------------------------------------------------------

def themecamps(request, year_year):
	year = Year.objects.get(year=year_year)
	previous = int(year_year) -1
	next = int(year_year) + 1
	ThemeCamps = ThemeCamp.objects.filter(year=year).extra(select={'lower_name': 'lower(name)'}).order_by('lower_name')
	return render_to_response('brc/themecamps.html', {'year': year,
							'theme_camps': ThemeCamps,
							'previous' : previous,
							'next' : next,}, context_instance=RequestContext(request))
	
def themecampid(request, year_year, theme_camp_id):
	year = Year.objects.get(year=year_year)
	camp = ThemeCamp.objects.get(id=theme_camp_id)
	events = PlayaEvent.objects.filter(hosted_by_camp=camp, moderation='A')
	if camp.location_point:
		map = MapDisplay(map_options={'default_lat': camp.location_point.y, 'default_lon': camp.location_point.x, 'default_zoom': 17, 'layers': ['osm.bme'], 'map_style':{'width':'400px','height':'400px'}})
	else:
		map = ''
	return render_to_response('brc/themecamp.html', {'year': year,
							'theme_camp': camp, 'events': events, 'map':map}, context_instance=RequestContext(request))

def themecampuuid(request, theme_camp_id):
	camp = ThemeCamp.objects.get(id=theme_camp_id)
	year = camp.year 
	events = PlayaEvent.objects.filter(hosted_by_camp=camp, moderation='A')
	if camp.location_point:
		map = MapDisplay(map_options={'default_lat': camp.location_point.y, 'default_lon': camp.location_point.x, 'default_zoom': 17, 'layers': ['osm.bme'], 'map_style':{'width':'400px','height':'400px'}})
	else:
		map = ''
	return render_to_response('brc/themecamp.html', {'year': year,
							'theme_camp': camp, 'events': events, 'map':map}, context_instance=RequestContext(request))

def themecampname(request, year_year, theme_camp_name):
	xyear = Year.objects.filter(year=year_year)
	ThemeCamp_name = ThemeCamp_name.replace('-',' ')
	camp =ThemeCamp.objects.filter(year=xyear[0],name__iexact=theme_camp_name)[0]
	events = PlayaEvents.objects.filter(hosted_by_camp=camp)
	return render_to_response('brc/themecamp.html', {'year': xyear[0],
							'theme_camp': camp,'events':events}, context_instance=RequestContext(request))

#-------------------------------------------------------------------------------
#---------- ArtCars ----------
#-------------------------------------------------------------------------------

def art_cars(request, year_year):
	xyear = Year.objects.filter(year=year_year)
	previous = int(year_year) -1
	next = int(year_year) + 1
	xArtCars = Vehicle.objects.filter(year=xyear[0])
	return render_to_response('brc/art_cars.html', {'year': xyear[0],
							'art_cars': xArtCars,
							'previous' : previous,
							'next' : next,}, context_instance=RequestContext(request))

def art_car_id(request, year_year, art_car_id):
	xyear = Year.objects.filter(year=year_year)
	xArtCar = Vehicle.objects.get(id=art_car_id)
	return render_to_response('brc/art_car.html', {'year': xyear[0],
							'art_car': xArtCar,}, context_instance=RequestContext(request))
#-------------------------------------------------------------------------------
#---------- PlayaEvents ----------
#-------------------------------------------------------------------------------

def playa_events_home(request, 
	year_year, 
	template='brc/playa_events_home.html',	
	queryset=None
):	
	year = Year.objects.get(year=year_year)
	user=request.user
	if user and type(user) != AnonymousUser:
		my_events = PlayaEvent.objects.filter(year=year, creator=user)[0]
		my_events = True if my_events else False
	else:
		my_events = False
	data = {'year':year, 'user':request.user, 'my_events':my_events}
	#return render_to_response(template, {}, context_instance=RequestContext(request))
	return render_to_response(template, data,context_instance=RequestContext(request))

def all_playa_events(request, 
	year_year, 
	template='brc/all_playa_events.html', 
	queryset=None
):
	year = Year.objects.get(year=year_year)
	previous = int(year.year) -1
	next = int(year.year) + 1

	if queryset:
		queryset = queryset._clone()
	else:
		queryset = Occurrence.objects.select_related().filter(event__playaevent__moderation='A', event__playaevent__list_online=True)
      
	occurrences=queryset.filter(start_time__range=(year.event_start, year.event_end)).order_by('start_time')
	
	by_day = [(dt, list(items)) for dt,items in itertools.groupby(occurrences, lambda o: o.start_time.date())]
  
	data=dict(year=year,by_day=by_day,previous=previous,next=next,)
	return render_to_response(template, data,context_instance=RequestContext(request))

def playa_events_by_day(request, year_year, playa_day=1, template='brc/playa_events_by_day.html', queryset=None):
	'''
	View a day's worth of playa events
	
	Context parameters:
	
	year_year: The 4 digit year
	playa_day: The current day of the festival, defined as the index into a
		list from event_start to event_end, starting with 1
	'''

	year = get_object_or_404(Year, year=year_year)
	previous = int(year.year) -1
	next = int(year.year) + 1
	
	event_date_list = year.daterange()
	
	# Normalize playa_day to start at 0
	playa_day =int(playa_day)
		
	if playa_day < 1:
		return http.HttpResponseBadRequest('Bad Request')
	
	if playa_day > len(event_date_list): 
		return http.HttpResponseBadRequest('Bad Request')
	
	playa_day_dt = event_date_list[playa_day-1]
	previous_playa_day = playa_day  -1
	next_playa_day = playa_day  +1
	
	if playa_day == 0:
		previous_playa_day = None
		previous_playa_day_dt = None
		next_playa_day_dt = event_date_list[next_playa_day-1]
	elif playa_day == len(event_date_list):
		next_playa_day = None
		next_playa_day_dt = None
		previous_playa_day_dt=event_date_list[previous_playa_day-1]
	else:
		next_playa_day_dt = event_date_list[next_playa_day-1]
		previous_playa_day_dt=event_date_list[previous_playa_day-1]

		
	if queryset:
		queryset = queryset._clone()
	else:
		queryset = Occurrence.objects.select_related().filter(event__playaevent__moderation='A', event__playaevent__list_online=True)

	dt_begin = datetime.combine(playa_day_dt, time(0))
	dt_end = datetime.combine(playa_day_dt, time(23,30))

	occurrences=queryset.filter(start_time__range=(dt_begin, dt_end)).order_by('-event__playaevent__all_day', 'start_time')
	
	# This is an optimization to avoid making 2 trips to the database. We want
	# a list of all the events that are all, and another with those that are 
	# not. 
	#
	# The below will cause 2 database round trips.
	# all_day_occurrences = occurrences.filter(event__playaevent__all_day=True)
	# timed_occurrences = occurrences.filter(event__playaevent__all_day=False)
	#
	# Instead, if we do an iterator over the original queryset, we can group
	# them in memory. It's important to sort the original queryset by all_day,
	# since it would otherwise cause strange results from itertools.groupby
	
	by_all_day=dict([(all_day, list(items)) for all_day, items in itertools.groupby(occurrences, lambda o: o.event.playaevent.all_day)])

	all_day_occurrences = by_all_day.setdefault(True)
	timed_occurrences = by_all_day.setdefault(False)
	
	data= dict(
		year = year,
		playa_day = playa_day,
		day = playa_day_dt,
		next = next,
		previous = previous,
		next_day = next_playa_day,
		next_day_dt = next_playa_day_dt,
		prev_day = previous_playa_day,
		prev_day_dt = previous_playa_day_dt,
		event_dates = event_date_list,
		all_day_occ = all_day_occurrences,
		timed_occ = timed_occurrences,
	)
	
	return render_to_response(
		template,
		data,
		context_instance=RequestContext(request)
	)

def playa_event_view(request,
	year_year,
	playa_event_id,
	template='brc/playa_event_view.html',
	event_form_class=brcforms.PlayaEventForm,
	recurrence_form_class=brcforms.PlayaEventOccurrenceForm,
):
	'''
	View an ``PlayaEvent`` instance and optionally update either the event or its
	occurrences.

	Context parameters:

	event: the event keyed by ``pk``
	event_form: a form object for updating the event
    	recurrence_form: a form object for adding occurrences
	'''

	event = get_object_or_404(PlayaEvent, pk=playa_event_id)
	'''
	event_form = recurrence_form = None
	if request.method == 'POST':
		if '_update' in request.POST:
			event_form = event_form_class(request.POST, instance=event)
			if event_form.is_valid():
				event_form.save(event)
				return http.HttpResponseRedirect(request.path)
	elif '_add' in request.POST:
		recurrence_form = recurrence_form_class(request.POST)
		if recurrence_form.is_valid():
			recurrence_form.save(event)
			return http.HttpResponseRedirect(request.path)
		else:
			return http.HttpResponseBadRequest('Bad Request')

	event_form = event_form or event_form_class(instance=event)
	if not recurrence_form:
		recurrence_form = recurrence_form_class(initial=dict(year=Year.objects.get(year=year_year)))
	'''
	data = dict(
		playa_event=event, 
		event_form=event_form_class, 
		recurrence_form=recurrence_form_class,
		year = get_object_or_404(Year, year=year_year)
	)
	return render_to_response(template, data,
		context_instance=RequestContext(request))


def playa_event_view_uuid(request,
	playa_event_id,
	template='brc/playa_event_view.html',
	event_form_class=brcforms.PlayaEventForm,
	recurrence_form_class=brcforms.PlayaEventOccurrenceForm,
):
	'''
	View an ``PlayaEvent`` instance and optionally update either the event or its
	occurrences.

	Context parameters:

	event: the event keyed by ``pk``
	event_form: a form object for updating the event
    	recurrence_form: a form object for adding occurrences
	'''

	event = get_object_or_404(PlayaEvent, pk=playa_event_id)
	year_year = event.year.year
	'''
	event_form = recurrence_form = None
	if request.method == 'POST':
		if '_update' in request.POST:
			event_form = event_form_class(request.POST, instance=event)
			if event_form.is_valid():
				event_form.save(event)
				return http.HttpResponseRedirect(request.path)
	elif '_add' in request.POST:
		recurrence_form = recurrence_form_class(request.POST)
		if recurrence_form.is_valid():
			recurrence_form.save(event)
			return http.HttpResponseRedirect(request.path)
		else:
			return http.HttpResponseBadRequest('Bad Request')

	event_form = event_form or event_form_class(instance=event)
	if not recurrence_form:
		recurrence_form = recurrence_form_class(initial=dict(year=Year.objects.get(year=year_year)))
	'''

	return render_to_response(template, dict(playa_event=event, event_form=event_form_class, recurrence_form=recurrence_form_class),context_instance=RequestContext(request))

@login_required
def playa_events_view_mine(
  request,
  year_year,
  template='brc/playa_view_my_events.html',
):
  '''
  View all of a users PlayaEvents
  '''
  
  user=request.user
  year = get_object_or_404(Year, year=year_year)
  
  my_events = PlayaEvent.objects.filter(year=year, creator=user).order_by('moderation')
  by_moderation=dict([(moderation, list(items)) for moderation, items in itertools.groupby(my_events, lambda e: e.moderation)])

  approved_events = by_moderation.setdefault('A')
  unmoderated_events = by_moderation.setdefault('U')
  rejected_events = by_moderation.setdefault('R')

  data = dict (
    year = year,
    approved_events = approved_events,
    unmoderated_events = unmoderated_events,
    rejected_events = rejected_events,
  )
  
  return render_to_response(
    template,
    data,
    context_instance=RequestContext(request)
)

@login_required 
def playa_occurrence_view(request,
	year_year,
	playa_event_id, 
	playa_occurrence_id=None, 
	template='brc/occurrence_detail.html',
	form_class=brcforms.PlayaEventOccurrenceForm
):
	occurrence = None
	if(playa_occurrence_id is not None):
		occurrence = get_object_or_404(Occurrence, pk=playa_occurrence_id, event__pk=playa_event_id)
	event = get_object_or_404(PlayaEvent, pk=playa_event_id)
	next = "/brc/" + event.year.year + "/playa_event/" + str(event.id)
	if request.method == 'POST':
		form = form_class(request.POST, instance=occurrence)
		if form.is_valid():
			form.save(event, playa_occurrence_id)
			if(occurrence is not None):
				request.user.message_set.create(message="Your Event Occurrence was Updated successfully.")
			else:
				request.user.message_set.create(message="Your Event Occurrence was Added successfully.")
			return HttpResponseRedirect(next)
		else:
			form = form_class(instance=occurrence)
	else:
		form = form_class(instance=occurrence)

	return render_to_response(template,dict(event=event, occurrence=occurrence, form=form, next=next),context_instance=RequestContext(request))

@login_required
def create_or_edit_event(request, 
	year_year, 
	playa_day=1,
	playa_event_id=None, 
	template_name='brc/add_event.html'
):
	user = request.user	
  	year = get_object_or_404(Year, year=year_year)

	instance = None
	if playa_event_id is not None:
        	instance = get_object_or_404(PlayaEvent, id=playa_event_id)
	
	if request.method=='POST':
		form=brcforms.PlayaEventForm(data=request.POST, instance=instance)
		if form.is_valid():
			event = form.save(year_year, user, playa_event_id)
			next = "/brc/" + event.year.year + "/playa_event/" + str(event.id)
			if(playa_event_id is not None):
				request.user.message_set.create(message="Your Event Updated successfully.")
			else:
				request.user.message_set.create(message="Your Event was Added successfully. Please wait for it to be moderated")
			return HttpResponseRedirect(next)
	else:
		initial = dict(year=year_year)
		if not instance:
			event_date_list = year.daterange()
			playa_day = int(playa_day)
			if playa_day > len(event_date_list): 
				return http.HttpResponseBadRequest('Bad Request')
			playa_day_dt = event_date_list[playa_day-1]
			initial['day'] = datetime.combine(playa_day_dt, time(9))
			
		form=brcforms.PlayaEventForm(initial=initial, instance=instance)
		
	data = {"form": form, "year": year}
	return render_to_response(template_name, data, context_instance=RequestContext(request))
 
@login_required
def delete_event(request, 
	year_year,
	playa_event_id, 
	next=None, 
):
	print "made it this far"
	event = get_object_or_404(PlayaEvent, id=playa_event_id)
	next = "/brc/" + event.year.year + "/playa_events/"
	print 'and here', login_required
	return delete_object(
		request,model = PlayaEvent,
		object_id = playa_event_id,
		post_delete_redirect = next,
		template_name = "brc/delete_event.html",
		extra_context = dict(next=next, year=event.year),
		login_required = login_required
	)

def delete_occurrence(request,
	year_year,
	occurrence_id,
	next=None,
):
	occurrence = get_object_or_404(Occurrence, id=occurrence_id)
	if(Occurrence.objects.filter(event=occurrence.event).count() == 1): #Last Occurrence 
		event = get_object_or_404(PlayaEvent, id=occurrence.event.id)
		next = "/brc/" + occurrence.event.playaevent.year.year + "/playa_events/"
		return delete_object(
			request,model = PlayaEvent,
			object_id = occurrence.event.id,
			post_delete_redirect = next,
			template_name = "brc/delete_event.html",
			extra_context = dict(next=next, year=event.year,
				msg="This is the only occurrence of this event. By deleting it, you will delete the entire event. Are you sure you want to do this??"),
			login_required = login_required
		)
	else:
		next = "/brc/" + year_year + "/playa_event/" + str(occurrence.event.id)
		return delete_object(
			request,model = Occurrence,
			object_id = occurrence_id,
			post_delete_redirect = next,
			template_name = "brc/delete_occurrence.html",
			extra_context = dict(next=next),
			login_required = login_required
		)
	

def _map_to_ascii(t):
  punctuation = { 0x2018:0x27, 0x2019:0x27, 0x201C:0x22, 0x201D:0x22 }
  new_string=t.translate(punctuation).encode('ascii', 'xmlcharrefreplace')
  return new_string
    
            
@login_required
def csv_onetime(request, year_year):
  year= Year.objects.filter(year=year_year)
  events = PlayaEvent.objects.filter(year=year, moderation='A').order_by('id').annotate(num_occurrences=Count('occurrence'))[:980]
  timed_events= itertools.ifilter(lambda e: e.all_day==False, events)
  
  onetime_events = list(itertools.ifilter(lambda e: e.num_occurrences==1, timed_events))
  
  # Create the HttpResponse object with the appropriate CSV header.
  response = HttpResponse(mimetype='text/csv')
  response['Content-Disposition'] = 'attachment; filename=onetime_events.csv'

  writer = csv.writer(response)
  writer.writerow(['Title', 'Description', 'Start Date', 'Start Time', 'End Date', 'End Time', 'Location', 'Placement', 'Event Type'])
  for e in onetime_events:
    o = e.next_occurrence()
    title = _map_to_ascii(e.title)
    start_date = o.start_time.strftime('%A')
    if o.start_time.day == 7:
      start_date = 'Lastday'
    start_time = o.start_time.strftime('%H:%M')
    end_date = o.end_time.strftime('%a %b %d')
    if o.end_time.day == 7:
      end_date = 'Lastday'
    end_time = o.end_time.strftime('%H:%M')
    print_description = _map_to_ascii(e.print_description)
    placement_location = ''
    if e.check_location:
      location = 'Check @ Play Info'
      placement_location = 'Check @ Playa Info'
    if e.other_location:
      location = e.other_location
    elif e.located_at_art:
      location = e.located_at_art.name
      placement_location = e.located_at_art.location_string
    else:
      location = e.hosted_by_camp.name
      placement_location = e.hosted_by_camp.location_string
    event_type = e.event_type
    writer.writerow([title, print_description, start_date, start_time, end_date, end_time, location, placement_location, event_type])
    
  return response
  
@login_required
def csv_repeating(request, year_year):
  year= Year.objects.filter(year=year_year)
  events = PlayaEvent.objects.filter(year=year, moderation='A').order_by('id').annotate(num_occurrences=Count('occurrence'))[:980]
  timed_events= itertools.ifilter(lambda e: e.all_day==False, events)
  
  repeating_events = list(itertools.ifilter(lambda e: e.num_occurrences>1, timed_events))

  # Create the HttpResponse object with the appropriate CSV header.
  response = HttpResponse(mimetype='text/csv')
  response['Content-Disposition'] = 'attachment; filename=repeating_events.csv'

  writer = csv.writer(response)
  writer.writerow(['Title', 'Description', 'Start Date', 'Start Time', 'End Date', 'End Time', 'Location', 'Placement', 'Event Type'])
  for e in repeating_events:
    occurrences = e.upcoming_occurrences().order_by('start_time')
    title = _map_to_ascii(e.title)
    print_description = _map_to_ascii(e.print_description)
    placement_location = ''
    if e.check_location:
      location = 'Check @ Play Info'
      placement_location = 'Check @ Playa Info'
    if e.other_location:
      location = e.other_location
    elif e.located_at_art:
      location = e.located_at_art.name
      placement_location = e.located_at_art.location_string
    else:
      location = e.hosted_by_camp.name
      placement_location = e.hosted_by_camp.location_string
    event_type = e.event_type
    for o in occurrences:
      start_date = o.start_time.strftime('%A')
      if o.start_time.day == 7:
        start_date = 'Lastday'
      start_time = o.start_time.strftime('%H:%M')
      end_date = o.end_time.strftime('%a %b %d')
      if o.end_time.day == 7:
        end_date = 'Lastday'
      end_time = o.end_time.strftime('%H:%M')

      writer.writerow([title, print_description, start_date, start_time, end_date, end_time, location, placement_location, event_type])[:980]
      # Blank out the descriptive items of the event so we only have data data for the repeat occurrences
      title=''
      print_description = ''
      location = ''
      placement_location=''
      event_type=''

  return response
  
@login_required
def csv_all_day_onetime(request, year_year):
  year= Year.objects.filter(year=year_year)
  events = PlayaEvent.objects.filter(year=year, moderation='A').order_by('id').annotate(num_occurrences=Count('occurrence'))[:980]
  all_day_events= itertools.ifilter(lambda e: e.all_day==True, events)

  onetime_all_day_events = list(itertools.ifilter(lambda e: e.num_occurrences==1, all_day_events))

  # Create the HttpResponse object with the appropriate CSV header.
  response = HttpResponse(mimetype='text/csv')
  response['Content-Disposition'] = 'attachment; filename=all_day_onetime_events.csv'

  writer = csv.writer(response)
  writer.writerow(['Title', 'Description', 'Start Date', 'Location', 'Placement', 'Event Type'])
  for e in onetime_all_day_events:
    occurrences = e.upcoming_occurrences().order_by('start_time')
    title = _map_to_ascii(e.title)
    print_description = _map_to_ascii(e.print_description)
    placement_location = ''
    if e.check_location:
      location = 'Check @ Play Info'
      placement_location = 'Check @ Playa Info'
    if e.other_location:
      location = e.other_location
    elif e.located_at_art:
      location = e.located_at_art.name
      placement_location = e.located_at_art.location_string
    else:
      location = e.hosted_by_camp.name
      placement_location = e.hosted_by_camp.location_string
    event_type = e.event_type
    for o in occurrences:
      start_date = o.start_time.strftime('%A')
      if o.start_time.day == 7:
        start_date = 'Lastday'

      writer.writerow([title, print_description, start_date, location, placement_location, event_type])
      # Blank out the descriptive items of the event so we only have data data for the repeat occurrences
      title=''
      print_description = ''
      location = ''
      placement_location=''
      event_type=''

  return response
  
@login_required
def csv_all_day_repeating(request, year_year):
  year= Year.objects.filter(year=year_year)
  events = PlayaEvent.objects.filter(year=year, moderation='A').order_by('id').annotate(num_occurrences=Count('occurrence'))
  all_day_events= itertools.ifilter(lambda e: e.all_day==True, events)

  repeating_events = list(itertools.ifilter(lambda e: e.num_occurrences>1, all_day_events))

  # Create the HttpResponse object with the appropriate CSV header.
  response = HttpResponse(mimetype='text/csv')
  response['Content-Disposition'] = 'attachment; filename=all_day_repeating_events.csv'

  writer = csv.writer(response)
  writer.writerow(['Title', 'Description', 'Start Date',  'Location', 'Placement', 'Event Type'])
  for e in repeating_events:
    occurrences = e.upcoming_occurrences().order_by('start_time')
    title = _map_to_ascii(e.title)
    print_description = _map_to_ascii(e.print_description)
    placement_location = ''
    if e.check_location:
      location = 'Check @ Play Info'
      placement_location = 'Check @ Playa Info'
    if e.other_location:
      location = e.other_location
    elif e.located_at_art:
      location = e.located_at_art.name
      placement_location = e.located_at_art.location_string
    else:
      location = e.hosted_by_camp.name
      placement_location = e.hosted_by_camp.location_string
    event_type = e.event_type
    for o in occurrences:
      start_date = o.start_time.strftime('%A')
      if o.start_time.day == 7:
        start_date = 'Lastday'


      writer.writerow([title, print_description, start_date, location, placement_location, event_type])
      # Blank out the descriptive items of the event so we only have data data for the repeat occurrences
      title=''
      print_description = ''
      location = ''
      placement_location=''
      event_type=''

  return response
#-------------------------------------------------------------------------------
#---------- Misc ----------
#-------------------------------------------------------------------------------

def geocode2(year_year, hour, minute, distance):
	xyear = Year.objects.filter(year=year_year)
	radial = time2radial(hour,minute)
	
	pnt = xyear[0].location_point
	
	pnt2 = getpoint(xyear[0].location_point.y, xyear[0].location_point.x,int(distance),-radial)
	return pnt2


def geocode(year_year, hour, minute, street):
	xyear = Year.objects.filter(year=year_year)
	street = street.replace('-',' ')
	xstreet = CircularStreet.objects.filter(year=xyear[0],name__iexact=street)
	if xstreet.count() < 1:
		return HttpResponse("invalid street")

	radial = time2radial(hour,minute)

	pnt = xyear[0].location_point
	
	pnt2 = getpoint(40.769288, -119.220037,xstreet[0].distance_from_center,-radial)
	return pnt2	

def geocoder(request, year_year, hour, minute, street):
	pnt = geocode(year_year, hour, minute, street)
	return HttpResponse(str(pnt.x) + "," + str(pnt.y))

def centercamp(year):
	dist_to_center_centercamp = 2450
	radial = time2radial(6,0)
	cc = getpoint(year.location_point.y,year.location_point.x,dist_to_center_centercamp,-radial)
	B = CircularStreet.objects.filter(year=year,name__startswith='B')[0]
	D = CircularStreet.objects.filter(year=year,name__startswith='D')[0]
	dist_inner_ring = abs(dist_to_center_centercamp - B.distance_from_center) #300 
	dist_outer_ring = abs(dist_to_center_centercamp - D.distance_from_center) #610' outside (725' radius to the center of the outer circle road) ??!!
	return [cc,dist_inner_ring,dist_outer_ring]

def plaza(year,hour,minute):
	large_plaza_radius = 125
	small_plaza_radius = 100
	hour = int(hour)
	minute = int(minute)
	if (minute == 0):
		## 3:00 plaza
		B = CircularStreet.objects.filter(year=year,name__startswith='B')[0]
		pt = geocode(year.year, hour, minute, B.name)
		return [pt,large_plaza_radius]
	elif (minute == 30):
		G = CircularStreet.objects.filter(year=year,name__startswith='G')[0]
		pt = geocode(year.year, hour, minute, G.name)
		return [pt,small_plaza_radius]
		
#2009 4:00 in North
def time2radial(hour, minute):
	hour = int(hour)
	minute = int(minute)
	if(hour > 12):
		return HttpResponse("invalid time")
	elif(hour < 0):
		return HttpResponse("invalid time")
	if(minute > 59):
		return HttpResponse("invalid time")
	elif(minute < 0):
		return HttpResponse("invalid time")
		
	radial = ((hour*30)+(minute*0.5)) + 60 #add 60, because 4:00 is North

	if radial >= 360:
		radial = radial - 360
	return radial
		
def neighborhood(request, year_year, hour, minute, street):
	pnt = geocode(year_year, hour, minute, street)
	xyear = Year.objects.filter(year=year_year)
	previous = int(year_year) -1
	next = int(year_year) + 1
	time = hour + ":" + minute
	hour = int(hour)
	minute = int(minute)
	if minute == 0:
		minute = 58
		hour = hour -1
	else:
		minute = minute - 2 # Magnetic Declination??
	
	if(hour > 12):
		return HttpResponse("invalid time")
	elif(hour < 0):
		return HttpResponse("invalid time")
	if(minute > 59):
		return HttpResponse("invalid time")
	elif(minute < 0):
		return HttpResponse("invalid time")
	street = street.replace('-',' ')
	xstreet = CircularStreet.objects.filter(year=xyear[0],name__iexact=street)
	radial = ((hour*30)+(minute*0.5))+45
	if radial >= 360:
		radial = radial - 360
	return render_to_response('brc/neighborhood.html', {'year': xyear[0],
						'time': time,
						'previous' : previous,
						'next' : next,
						'street' : xstreet[0],
						'point' : pnt,
						'radial': -radial})

def getpoint(lat1,lon1,dist,dir):
        lat1 = (math.pi/180)*lat1
        lon1 = (math.pi/180)*lon1
        dir = (math.pi/180)*dir
        dist = dist / (185200.0/30.48)
        dist = dist / (180*60/math.pi)

        lat=math.asin(math.sin(lat1)*math.cos(dist)+math.cos(lat1)*math.sin(dist)*math.cos(dir))
        dlon=math.atan2(math.sin(dir)*math.sin(dist)*math.cos(lat1),math.cos(dist)-math.sin(lat1)*math.sin(lat))
        lon = ((lon1 - dlon+math.pi) % (2*math.pi)) - math.pi

        lat = lat * (180/math.pi)
        lon = lon * (180/math.pi)
        pnt = Point(float(lon), float(lat))

        return pnt
