from django.contrib.gis.db import models
from django.db import connection
from django.contrib.auth.models import User
import datetime

class Year(models.Model):
    def __unicode__(self):
        return self.year
    year = models.CharField(max_length=4)
    location = models.CharField(max_length=50)
    location_point = models.PointField(null=True, blank=True)
    participants = models.IntegerField(null=True, blank=True)
    theme = models.CharField(max_length=20, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    objects = models.GeoManager()
    class Meta:
        ordering = ('year',)

class CircularStreet(models.Model):
    def __unicode__(self):
        return self.year.year + ":" + self.name
    year = models.ForeignKey(Year)
    name = models.CharField(max_length=50)
    #slug = models.SlugField(max_length=255)
    order = models.IntegerField(null=True, blank=True)
    width = models.IntegerField(null=True, blank=True)
    distance_from_center = models.IntegerField(null=True, blank=True)
    street_line = models.LineStringField(null=True, blank=True, srid=4326)
    objects = models.GeoManager()
    class Meta:
        ordering = ('year','order',)

class TimeStreet(models.Model):
    def __unicode__(self):
        return self.year.year + ":" + self.name
    year = models.ForeignKey(Year)
    hour = models.IntegerField() # Should be restricted
    minute = models.IntegerField() # Should be restricted
    name = models.CharField(max_length=5)
    #slug = models.SlugField(max_length=255)
    width = models.IntegerField(null=True, blank=True)
    street_line = models.LineStringField(null=True, blank=True)
    objects = models.GeoManager()
    class Meta:
        ordering = ('year','name',)

class ThemeCamp(models.Model):
    def __unicode__(self):
        return self.year.year + ":" + self.name
    name = models.CharField(max_length=100)
    year = models.ForeignKey(Year)
    #slug = models.SlugField(max_length=255)
    description = models.TextField(null=True,blank=True)
    url = models.URLField(null=True,blank=True)
    contact_email = models.EmailField(null=True,blank=True)
    hometown = models.CharField(max_length=50, null=True, blank=True)
    location_point = models.PointField(null=True, blank=True)
    location_poly = models.PolygonField(null=True, blank=True)
    circular_street = models.ForeignKey(CircularStreet, null=True, blank=True)
    time_address = models.TimeField(null=True, blank=True)
    participants = models.ManyToManyField(User, null=True, blank=True)  
    objects = models.GeoManager()
    class Meta:
        ordering = ('year','name',)

    def save(self):
        if self.location_poly:
            self.location_point = self.location_poly.centroid
        super(ThemeCamp, self).save()


class ArtInstallation(models.Model):
    def __unicode__(self):
        return self.year.year + ":" + self.name
    year = models.ForeignKey(Year)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    artist = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    circular_street = models.ForeignKey(CircularStreet, null=True, blank=True)
    time_address = models.TimeField(null=True, blank=True)
    location_point = models.PointField(null=True, blank=True)
    location_poly = models.PolygonField(null=True, blank=True)
    objects = models.GeoManager()
    class Meta:
        ordering = ('year','name',)

class Vehicle(models.Model):
    VEHICLE_TYPE_CHOICES = (
            ('UNKWN', 'Unknown'),
            ('MUTANT', 'Mutant Vehicle'),
            ('UTIL', 'Utility Vehicle'),
            ('LEVEH', 'Law Enforcement Vehicle'),
            ('FIXED', 'Fixed Wing Airplane'),
            ('VTOL', 'VTOL'))
    def __unicode__(self):
        return self.year.year + ":" + self.name
    year = models.ForeignKey(Year)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    type = models.CharField(max_length=6, choices=VEHICLE_TYPE_CHOICES)
    artist = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    last_point = models.PointField(null=True, blank=True)
    last_point_time = models.DateTimeField(null=True, blank=True)
    participants = models.ManyToManyField(User, null=True, blank=True)  
    objects = models.GeoManager()
    class Meta:
        ordering = ('year','name',)

class TrackPoint(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, null=True, blank=True)
    xypoint = models.PointField()
    xypoint_time = models.DateTimeField()

class ThreeDModel(models.Model):
    art_installation = models.ForeignKey(ArtInstallation, null=True, blank=True)
    theme_camp = models.ForeignKey(ThemeCamp, null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, null=True, blank=True)
    model_point = models.PointField(null=True, blank=True)
    model_url = models.URLField() #Google 3D Warehouse
    artist = models.CharField(max_length=200, null=True, blank=True)

class PlayaEvent(models.Model):
    EVENT_TYPE_CHOICES = (
        ('NONE', 'None'),
        ('AA', 'AA Meeting'),
        ('CLASS', 'Class/Workshop'),
        ('BURN', 'Burning'),
        ('PARADE', 'Parade'),
        ('KIDS', 'Kids Event'),
        ('DAILY', 'Daily Event'),
        ('MUSIC', 'Music Event'),
        ('PERF', 'Performance Event'))
    def __unicode__(self):
        return self.year.year + ":" + self.name
    year = models.ForeignKey(Year)
    name = models.CharField(max_length=100)
    #slug = models.SlugField(max_length=255)
    description = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=6, choices=EVENT_TYPE_CHOICES)
    start_date_time = models.DateTimeField(null=True, blank=True)
    end_date_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    repeats = models.BooleanField(null=True, blank=True)
    hosted_by_camp = models.ForeignKey(ThemeCamp, null=True, blank=True)
    located_at_art = models.ForeignKey(ArtInstallation, null=True, blank=True)
    location_point = models.PointField(null=True, blank=True)
    location_track = models.LineStringField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    objects = models.GeoManager()
