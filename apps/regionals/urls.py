from django.conf.urls.defaults import *

urlpatterns = patterns('',
        url(r'^$', 'regionals.views.regionals', name="regional_list"),
    )
