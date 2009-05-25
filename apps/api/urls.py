from django.conf.urls.defaults import *
from piston.resource import Resource
from api.handlers import * 
from piston.authentication import OAuthAuthentication

auth = OAuthAuthentication()

year_handler = Resource(YearHandler, authentication=auth)
camp_handler = Resource(ThemeCampHandler, authentication=auth)
art_handler = Resource(ArtInstallationHandler, authentication=auth)
event_handler = Resource(PlayaEventHandler, authentication=auth)
user_handler = Resource(UserHandler, authentication=auth)
cstreet_handler = Resource(CircularStreetHandler, authentication=auth)
tstreet_handler = Resource(TimeStreetHandler, authentication=auth)

urlpatterns = patterns('',
   url(r'^year/', year_handler),
   url(r'^camp/', camp_handler),
   url(r'^art/', art_handler),
   url(r'^event/', event_handler),
   url(r'^user/', user_handler),
   url(r'^cstreet/', cstreet_handler),
   url(r'^tstreet/', tstreet_handler),
)

