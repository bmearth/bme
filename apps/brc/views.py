import math

from datetime import datetime, date, time
from django.shortcuts import get_object_or_404, render_to_response
from django.core.paginator import InvalidPage
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.gis.geos import *
from django.contrib.auth.decorators import login_required
from django.views.generic.create_update import delete_object

from swingtime.models import Event, Occurrence
from swingtime import utils, forms
from swingtime.views import *
from brc.models import *
from brc import forms as brcforms

from dateutil import parser

if swingtime_settings.CALENDAR_FIRST_WEEKDAY is not None:
    calendar.setfirstweekday(swingtime_settings.CALENDAR_FIRST_WEEKDAY)

def index(request, template_name="brc/index.html"):
	years = Year.objects.all().order_by('-year')
	return render_to_response(template_name, {"years": years,}, context_instance=RequestContext(request))

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
	return render_to_response('brc/art_installation.html', {'year': xyear[0],
							'art_installation': xArtInstallation,}, context_instance=RequestContext(request))

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
	xThemeCamp = ThemeCamp.objects.get(id=theme_camp_id)
	return render_to_response('brc/themecamp.html', {'year': year,
							'theme_camp': xThemeCamp,}, context_instance=RequestContext(request))

def themecampname(request, year_year, theme_camp_name):
	xyear = Year.objects.filter(year=year_year)
	ThemeCamp_name = ThemeCamp_name.replace('-',' ')
	xThemeCamp =ThemeCamp.objects.filter(year=xyear[0],name__iexact=theme_camp_name)
	return render_to_response('brc/themecamp.html', {'year': xyear[0],
							'theme_camp': xThemeCamp[0],}, context_instance=RequestContext(request))

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

def playa_events_by_day(request, year_year, playa_day, template='brc/playa_events_by_day.html', queryset=None):
	'''
	View a day's worth of playa events
	
	Context parameters:
	
	year_year: The 4 digit year
	playa_day: The current day of the festival, defined as the index into a
		list from event_start to event_end, starting with 1
	'''

	year = get_object_or_404(Year, year=year_year)
	
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
		day = playa_day_dt,
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

	return render_to_response(template, dict(playa_event=event, event_form=event_form_class, recurrence_form=recurrence_form_class),context_instance=RequestContext(request))
 
def playa_occurrence_view(request,
	year_year,
	playa_event_id, 
	playa_occurrence_id, 
	template='brc/occurrence_detail.html',
	form_class=brcforms.PlayaEventOccurrenceForm
):
	'''
	View a specific occurrence and optionally handle any updates.
	
	Context parameters:
	
	occurrence: the occurrence object keyed by ``pk``
	form: a form object for updating the occurrence
	'''
	occurrence = get_object_or_404(Occurrence, pk=playa_occurrence_id, event__pk=playa_event_id)
	if request.method == 'POST':
		form = form_class(request.POST, instance=occurrence)
		if form.is_valid():
			form.save(occurrence.event, playa_occurrence_id)
			next = "/brc/" + occurrence.event.playaevent.year.year + "/playa_event/" + str(occurrence.event.playaevent.id)
			return HttpResponseRedirect(next)
		else:
			form = form_class(instance=occurrence)
	else:
		form = form_class(instance=occurrence)

	return render_to_response(template,dict(occurrence=occurrence, form=form),context_instance=RequestContext(request))

@login_required
def create_or_edit_event(request, 
	year_year, 
	playa_event_id=None, 
	template_name='brc/add_event.html'
):
	user = request.user
	
	instance = None
	if playa_event_id is not None:
        	instance = get_object_or_404(PlayaEvent, id=playa_event_id)
	
	if request.method=='POST':
		form=brcforms.PlayaEventForm(data=request.POST, instance=instance)
		if form.is_valid():
			event = form.save(year_year, user, playa_event_id)
			next = "/brc/" + event.year.year + "/playa_event/" + str(event.id)
			return HttpResponseRedirect(next)
	else:
		form=brcforms.PlayaEventForm(initial=dict(year=Year.objects.get(year=year_year)), instance=instance)
	return render_to_response(template_name, {"form": form,}, context_instance=RequestContext(request))
 
@login_required
def delete_event(request, 
	year_year,
	playa_event_id, 
	next=None, 
):
	"""
	After the event is deleted there are three options for redirect, tried in
	this order:

	# Try to find a 'next' GET variable
	# If the key word argument redirect is set
	# Lastly redirect to the event detail of the recently create event
	"""
	event = get_object_or_404(PlayaEvent, id=playa_event_id)
	#next = next or reverse('day_calendar', args=[event.calendar.slug])
	#next = get_next_url(request, next)
	next = "/brc/" + event.year.year + "/playa_events/"
	return delete_object(
		request,model = PlayaEvent,
		object_id = playa_event_id,
		post_delete_redirect = next,
		template_name = "brc/delete_event.html",
		extra_context = dict(next=next),
		login_required = login_required
	)

#-------------------------------------------------------------------------------
#---------- Misc ----------
#-------------------------------------------------------------------------------

def geocode2(year_year, hour, minute, distance):
	xyear = Year.objects.filter(year=year_year)
	hour = int(hour)
	minute = int(minute)
	radial = ((hour*30)+(minute*0.5))+45
	if radial >= 360:
		radial = radial - 360
	
	pnt = xyear[0].location_point
	
	pnt2 = getpoint(xyear[0].location_point.y, xyear[0].location_point.x,int(distance),-radial)
	return pnt2


def geocode(year_year, hour, minute, street):
	hour = int(hour)
	minute = int(minute)
	#if minute == 0:
	#	minute = 58
	#	hour = hour -1
	#else:
	#	minute = minute - 2 # Magnetic Declination??
	
	if(hour > 12):
		return HttpResponse("invalid time")
	elif(hour < 0):
		return HttpResponse("invalid time")
	if(minute > 59):
		return HttpResponse("invalid time")
	elif(minute < 0):
		return HttpResponse("invalid time")
	
	xyear = Year.objects.filter(year=year_year)
	street = street.replace('-',' ')
	xstreet = CircularStreet.objects.filter(year=xyear[0],name__iexact=street)
	if xstreet.count() < 1:
		return HttpResponse("invalid street")

	radial = ((hour*30)+(minute*0.5))+60
	if radial >= 360:
		radial = radial - 360

	pnt = xyear[0].location_point
	
	pnt2 = getpoint(xyear[0].location_point.y, xyear[0].location_point.x,xstreet[0].distance_from_center,-radial)
	return pnt2	

def geocoder(request, year_year, hour, minute, street):
	pnt = geocode(year_year, hour, minute, street)
	return HttpResponse(pnt)

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
