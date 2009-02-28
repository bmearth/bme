from django.conf.urls.defaults import *

from regionals.models import Regional
from wiki import models as wiki_models

wiki_args = {'group_slug_field': 'slug',
             'group_qs': Regional.objects.filter(deleted=False)}


urlpatterns = \
    patterns('',
    )
