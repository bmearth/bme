import math

from datetime import datetime
from django.shortcuts import get_object_or_404, render_to_response
from django.core.paginator import InvalidPage
from django.http import HttpResponse
from django.template import RequestContext
from django.contrib.gis.geos import *
from django.contrib.auth.decorators import login_required


from swingtime.models import Event, Occurrence
from swingtime.views import *
from brc.models import *
from brc.forms import PlayaEventForm

def index(request, template_name="brc/index.html"):
	years = Year.objects.all().order_by('-year')
	return render_to_response(template_name, {"years": years,}, context_instance=RequestContext(request))

def year_info(request, year_year):
	xyear = Year.objects.filter(year=year_year)
	streets = CircularStreet.objects.filter(year=xyear[0])
	previous = int(year_year) -1
	next = int(year_year) + 1
	return render_to_response('brc/year.html', {'year': xyear[0],
						'streets' : streets,
						'previous' : previous,
						'next' : next,}, context_instance=RequestContext(request))

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
	ArtInstallations = ArtInstallation.objects.filter(year=xyear[0])
	return render_to_response('brc/art_installations.html', {'year': xyear[0],
							'art_installations': ArtInstallations,
							'previous' : previous,
							'next' : next,}, context_instance=RequestContext(request))

def themecamps(request, year_year):
	xyear = Year.objects.filter(year=year_year)
	previous = int(year_year) -1
	next = int(year_year) + 1
	ThemeCamps = ThemeCamp.objects.filter(year=xyear[0])
	return render_to_response('brc/themecamps.html', {'year': xyear[0],
							'theme_camps': ThemeCamps,
							'previous' : previous,
							'next' : next,}, context_instance=RequestContext(request))
	
def themecampid(request, year_year, theme_camp_id):
	xyear = Year.objects.filter(year=year_year)
	xThemeCamp = ThemeCamp.objects.get(id=theme_camp_id)
	return render_to_response('brc/themecamp.html', {'year': xyear[0],
							'theme_camp': xThemeCamp,}, context_instance=RequestContext(request))

def themecampname(request, year_year, theme_camp_name):
	xyear = Year.objects.filter(year=year_year)
	ThemeCamp_name = ThemeCamp_name.replace('-',' ')
	xThemeCamp =ThemeCamp.objects.filter(year=xyear[0],name__iexact=theme_camp_name)
	return render_to_response('brc/themecamp.html', {'year': xyear[0],
							'theme_camp': xThemeCamp[0],}, context_instance=RequestContext(request))
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

def all_playa_events(request, year_year, template='brc/all_playa_events.html', queryset=None):
  xyear = Year.objects.get(year=year_year)
  previous = int(xyear.year) -1
  next = int(xyear.year) + 1

  if queryset:
      queryset = queryset._clone()
  else:
      queryset = Occurrence.objects.select_related()
      
  occurrences=queryset.filter(start_time__range=(xyear.event_start, xyear.event_end)).order_by('start_time')
  
  by_day = [
      (dt, list(items)) 
      for dt,items in itertools.groupby(occurrences, lambda o: o.start_time.date())
  ]
  
  data=dict(
    year=xyear,
    by_day=by_day,
    previous=previous,
    next=next,
  )
  return render_to_response(
      template, 
      data,
      context_instance=RequestContext(request)
  )

def playa_events(request, year_year):
	xyear = Year.objects.filter(year=year_year)
	previous = int(year_year) -1
	next = int(year_year) + 1
	xPlayaEvents = PlayaEvent.objects.filter(year=xyear[0]).order_by('start')
	return render_to_response('brc/playa_events.html', {'year': xyear[0],
							'playa_events': xPlayaEvents,
							'previous' : previous,
							'next' : next,}, context_instance=RequestContext(request))

def playa_event_id(request, year_year, playa_event_id):
	xyear = Year.objects.filter(year=year_year)
	xPlayaEvent = PlayaEvent.objects.get(id=playa_event_id)
	return render_to_response('brc/playa_event.html', {'year': xyear[0],
							'playa_event': xPlayaEvent,}, context_instance=RequestContext(request))

@login_required
def create_or_edit_event(request, calendar_slug, event_id=None, next=None,
    template_name='schedule/create_event.html'):
    """
    This function, if it receives a GET request or if given an invalid form in a
    POST request it will generate the following response

    Template:
        schedule/create_event.html
    
    Context Variables:
        
    form:
        an instance of EventForm
    
    calendar: 
        a Calendar with id=calendar_id

    if this function gets a GET request with ``year``, ``month``, ``day``,
    ``hour``, ``minute``, and ``second`` it will auto fill the form, with
    the date specifed in the GET being the start and 30 minutes from that
    being the end.

    If this form receives an event_id it will edit the event with that id, if it
    recieves a calendar_id and it is creating a new event it will add that event
    to the calendar with the id calendar_id

    If it is given a valid form in a POST request it will redirect with one of
    three options, in this order

    # Try to find a 'next' GET variable
    # If the key word argument redirect is set
    # Lastly redirect to the event detail of the recently create event
    """
    date = coerce_date_dict(request.GET)
    initial_data = None
    if date:
        try:
            start = datetime.datetime(**date)
            initial_data = {
                "start": start,
                "end": start + datetime.timedelta(minutes=30)
            }
        except TypeError:
            raise Http404
        except ValueError:
            raise Http404
    
    instance = None
    if event_id is not None:
        instance = get_object_or_404(PlayaEvent, id=event_id)
    
    calendar = get_object_or_404(Calendar, slug=calendar_slug)
    
    form = PlayaEventForm(data=request.POST or None, instance=instance, 
        hour24=True, initial=initial_data)
    
    if form.is_valid():
        event = form.save(commit=False)
        if instance is None:
            event.creator = request.user
            event.calendar = calendar
            event.year = Year.objects.get(year=str(event.start.year))
        event.save()
        #next = next or reverse('event', args=[event.id])
        #next = get_next_url(request, next)
	#find a better way to to do this!
	next = "/brc/" + event.year.year + "/playa_event/" + str(event.id)
        return HttpResponseRedirect(next)
	#return render_to_response('brc/playa_event.html', {'year': event.year,
	#						'playa_event': event,}, context_instance=RequestContext(request))
    
    next = get_next_url(request, next)
    return render_to_response(template_name, {
        "form": form,
        "calendar": calendar,
        "next":next
    }, context_instance=RequestContext(request))

def delete_event(request, event_id, next=None, login_required=True):
    """
    After the event is deleted there are three options for redirect, tried in
    this order:

    # Try to find a 'next' GET variable
    # If the key word argument redirect is set
    # Lastly redirect to the event detail of the recently create event
    """
    event = get_object_or_404(PlayaEvent, id=event_id)
    #next = next or reverse('day_calendar', args=[event.calendar.slug])
    #next = get_next_url(request, next)
    next = "/brc/" + event.year.year + "/playa_events/"
    return delete_object(request,
                         model = Event,
                         object_id = event_id,
                         post_delete_redirect = next,
                         template_name = "schedule/delete_event.html",
                         extra_context = dict(next=next),
                         login_required = login_required
                        )

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
