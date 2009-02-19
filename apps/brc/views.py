import math
from datetime import datetime
from django.shortcuts import get_object_or_404, render_to_response
from django.core.paginator import InvalidPage
from django.http import HttpResponse
from django.template import RequestContext
from django.contrib.gis.geos import *
from brc.models import *

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

def art_installations(request, year_year):
	xyear = Year.objects.filter(year=year_year)
	previous = int(year_year) -1
	next = int(year_year) + 1
	ArtInstallations = ArtInstallation.objects.filter(year=xyear[0])
	return render_to_response('brc/art_installations.html', {'year': xyear[0],
							'art_installations': ArtInstallations,
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

	radial = ((hour*30)+(minute*0.5))+45
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
