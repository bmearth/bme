import datetime
from haystack import indexes
from haystack import site
from brc.models import * 

'''
class PlayaEventIndex(indexes.SearchIndex):
    title = indexes.CharField(use_template=True)
    description = indexes.CharField(document=True, use_template=True)

site.register(PlayaEvent, PlayaEventIndex)
'''
