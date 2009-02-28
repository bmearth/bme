from django.contrib.gis.db import models
from django.contrib.auth.models import User
from tribes.models import Tribe 
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Regional(Tribe):
    contacts = models.ManyToManyField(User)
    quote = models.TextField(null=True)
    email = models.EmailField(null=True)
    announcment_list = models.EmailField(null=True)
    discussion_list = models.EmailField(null=True)
    # geo stuff
    location = models.PointField(null=True)
    location_text = models.CharField(max_length=80, unique=True, null=True)
