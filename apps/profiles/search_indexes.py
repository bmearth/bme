import datetime
from haystack import indexes
from haystack import site
from profiles.models import Profile


class ProfileIndex(indexes.SearchIndex):
    description = indexes.CharField(document=True, use_template=True, model_attr='user')
    full_name = indexes.CharField(model_attr='name')
site.register(Profile, ProfileIndex)
