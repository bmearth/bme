from django.conf.urls.defaults import *

urlpatterns = patterns('',
     url(r'^$', 'brc.views.index', name="index"),
     url(r'^(?P<year_year>\d{4})/$', 'brc.views.year_info', name="year_info"),
     url(r'^(?P<year_year>\d{4})/themecamp/(?P<theme_camp_id>\d{1,4})/$', 'brc.views.themecampid', name="themecamp"),
     url(r'^(?P<year_year>\d{4})/themecamps/$', 'brc.views.themecamps', name="themecamps"),
     url(r'^(?P<year_year>\d{4})/art_installation/(?P<art_installation_id>\d{1,4})/$', 'brc.views.art_installation_id', name="art_installation"),
     url(r'^(?P<year_year>\d{4})/art_installations/$', 'brc.views.art_installations', name="art_installations"),
     url(r'^(?P<year_year>\d{4})/(?P<hour>\d{1,2}):(?P<minute>\d{1,2})/(?P<street>[a-z-]{0,50})/$', 'brc.views.neighborhood', name="neighborhood"),
     url(r'^geocoder/(?P<year_year>\d{4})/(?P<hour>\d{1,2}):(?P<minute>\d{1,2})/(?P<street>[a-z-]{0,50})/$', 'brc.views.geocoder', name="geocoder"),
)
