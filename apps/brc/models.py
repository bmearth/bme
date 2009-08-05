from django.contrib.gis.db import models
from django.conf import settings
from django.db import connection
from django.contrib.auth.models import User
from swingtime.models import Event
from datetime import datetime, timedelta
	
if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
else:
    notification = None
    

MODERATION_CHOICES = (
	('U', 'UnModerated'),
	('A', 'Accepted'),
	('R', 'Rejected'),
)

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
    event_start = models.DateField(null=True)
    event_end = models.DateField(null=True)
    class Meta:
        ordering = ('year',)
    
    def daterange(self):
      """
      Returns a list of datetime objects for every day of the event
      """
      numdays = (self.event_end - self.event_start).days + 1
      return [self.event_start + timedelta(days=x) for x in range(0,numdays)]
      


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
    slug = models.SlugField(max_length=255, null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    url = models.URLField(null=True,blank=True)
    contact_email = models.EmailField(null=True,blank=True)
    hometown = models.CharField(max_length=50, null=True, blank=True)
    image = models.ImageField(upload_to='theme_camp', null=True, blank=True)
    location_string = models.CharField(max_length=50, null=True, blank=True)
    location_point = models.PointField(null=True, blank=True)
    location_poly = models.PolygonField(null=True, blank=True)
    circular_street = models.ForeignKey(CircularStreet, null=True, blank=True)
    time_address = models.TimeField(null=True, blank=True)
    participants = models.ManyToManyField(User, null=True, blank=True)  
    bm_fm_id = models.IntegerField(null=True,blank=True)
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
    slug = models.SlugField(max_length=255, null=True, blank=True)
    artist = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    image = models.ImageField(upload_to='art_install', null=True, blank=True)
    circular_street = models.ForeignKey(CircularStreet, null=True, blank=True)
    time_address = models.TimeField(null=True, blank=True)
    distance = models.IntegerField(null=True, blank=True)
    location_string = models.CharField(max_length=50, null=True, blank=True)
    location_point = models.PointField(null=True, blank=True)
    location_poly = models.PolygonField(null=True, blank=True)
    bm_fm_id = models.IntegerField(null=True,blank=True)
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
    image = models.ImageField(upload_to='vehicle', null=True, blank=True)
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

class PlayaEvent(Event):

  def __unicode__(self):
    return self.year.year + ":" + self.title
  year = models.ForeignKey(Year)
  print_description = models.CharField(max_length=150, null=False, blank=True)
  slug = models.SlugField(max_length=255)
  hosted_by_camp = models.ForeignKey(ThemeCamp, null=True, blank=True)
  located_at_art = models.ForeignKey(ArtInstallation, null=True, blank=True)
  other_location = models.CharField(max_length=255, null=True, blank=True)
  check_location = models.NullBooleanField()
  location_point = models.PointField(null=True, blank=True)
  location_track = models.LineStringField(null=True, blank=True)
  url = models.URLField(null=True, blank=True)
  contact_email = models.EmailField(null=True, blank=True)
  all_day = models.NullBooleanField()
  list_online = models.NullBooleanField()
  list_contact_online = models.NullBooleanField()
  creator = models.ForeignKey(User, null=False)
  moderation =  models.CharField(max_length=1, choices=MODERATION_CHOICES, default='U')
  objects = models.GeoManager()



  def event_moderation(sender, instance,  **kwargs):
    if isinstance(instance, PlayaEvent):
      event = instance
#     get old event instance
#     compare old event moderation to new event moderation
      if notification:
        notification.send([event.creator], "brc_event_moderation", {"user": event.creator, "event": event}, on_site=False)
        
        
#  models.signals.pre_save.connect(event_creation, sender=PlayaEvent)

def event_creation(sender, instance,  **kwargs):
  if isinstance(instance, PlayaEvent):
    event = instance
    
    if kwargs['created']:
      if notification:
        notification.send([event.creator], "brc_event_creation", {"user": event.creator, "event": event}, on_site=False)
# models.signals.post_save.connect(event_creation, sender=PlayaEvent)
      
