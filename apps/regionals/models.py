from django.contrib.gis.db import models
from django.contrib.auth.models import User
from tribes.models import Tribe 
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Regional(Tribe):
    contacts = models.ManyToManyField(User, null=True, blank=True)
    quote = models.TextField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    announcment_list = models.EmailField(null=True, blank=True)
    discussion_list = models.EmailField(null=True, blank=True)
    # geo stuff
    location = models.PointField(null=True, blank=True)
    location_text = models.CharField(max_length=80, unique=True, null=True, blank=True)
