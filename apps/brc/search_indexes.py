import datetime
from haystack import indexes
from haystack import site
from brc.models import * 
from profiles.models import * 

current_year=Year.objects.get(year='2009')
class PlayaEventIndex(indexes.SearchIndex):
  title = indexes.CharField(model_attr='title', use_template=True)
  description = indexes.CharField(document=True, use_template=True)
  def get_queryset(self):
      "Used when the entire index for model is updated."
      return PlayaEvent.objects.filter(year=current_year, moderation='A', list_online=True)

site.register(PlayaEvent, PlayaEventIndex)

class ThemeCampIndex(indexes.SearchIndex):
  title=indexes.CharField(use_template=True, model_attr='name')
  description = indexes.CharField(use_template=True, document=True)
  
  def get_queryset(self):
    "Used when the entire index for model is updated."
    return ThemeCamp.objects.filter(year=current_year)
    
site.register(ThemeCamp, ThemeCampIndex)

class ArtInstallationIndex(indexes.SearchIndex):
  title=indexes.CharField(use_template=True, model_attr='name')
  description = indexes.CharField(use_template=True, document=True)
  
  def get_queryset(self):
    "Used when the entire index for model is updated."
    return ArtInstallation.objects.filter(year=current_year)
    
site.register(ArtInstallation, ArtInstallationIndex)

#class ProfileIndex(indexes.SearchIndex):
#  title=indexes.CharField(use_template=True, model_attr='user')
#  name=indexes.CharField(use_template=True, model_attr='name')
#  description=indexes.CharField(document=True,use_template=True, model_attr='about')
#  location=indexes.CharField(use_template=True, model_attr='location')
#  
#  def get_queryset(self):
#    "Used when the entire index for model is updated."
#    return Profile.objects.all()
    
#site.register(Profile, ProfileIndex)
