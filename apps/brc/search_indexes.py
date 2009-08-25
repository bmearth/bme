import datetime
from haystack import indexes
from haystack import site
from brc.models import * 


class PlayaEventIndex(indexes.SearchIndex):
  title = indexes.CharField(use_template=True)
  description = indexes.CharField(document=True, use_template=True)
  
  def get_queryset(self):
      "Used when the entire index for model is updated."
      year=Year.objects.get(year='2009')
      return PlayaEvent.objects.filter(year=year, moderation='A', list_online=True)

site.register(PlayaEvent, PlayaEventIndex)
