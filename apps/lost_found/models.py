from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from timezones.fields import TimeZoneField

CATEGORY_CHOICES = (
	('M', 'Miscellaneous'),
	('C', 'Clothing'),
	('B', 'Bags: Backpacks, HydroPacks, Luggage'),
	('E', 'Eyeglasses/Sunglasses'),
	('G', 'Gadgets:Cameras, MP3 Players, Phones'),
	('J', 'Jewelery'),
	('K', 'Keys'),
	('T', 'Tools and Equipment'),
	('I', 'ID, Passports, Wallets'),
)


class LostItem(models.Model):
    category =  models.CharField(max_length=1, choices=CATEGORY_CHOICES, default='M')
    item_number = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=50, null=True, blank=True)
    colors = models.CharField(max_length=50, null=True, blank=True)
    model_make = models.CharField(max_length=50, null=True, blank=True)
    shipped_by = models.CharField(max_length=50, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return self.user.username
