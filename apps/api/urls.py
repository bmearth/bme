from django.conf.urls.defaults import *
from piston.resource import Resource
from api.handlers import * 

year_handler = Resource(YearHandler)
camp_handler = Resource(ThemeCampHandler)
art_handler = Resource(ArtInstallationHandler)
event_handler = Resource(PlayaEventHandler)
user_handler = Resource(UserHandler)
cstreet_handler = Resource(CircularStreetHandler)
tstreet_handler = Resource(TimeStreetHandler)

urlpatterns = patterns('',
   url(r'^year/', year_handler),
   url(r'^camp/', camp_handler),
   url(r'^art/', art_handler),
   url(r'^event/', event_handler),
   url(r'^user/', user_handler),
   url(r'^cstreet/', cstreet_handler),
   url(r'^tstreet/', tstreet_handler),
)

