from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.generic.list_detail import object_list

urlpatterns = patterns('',


    url(r'^$', view='checkins.views.all', name="checkins_all"),

    url(r'^(?P<id>\d+)/$', view='checkins.views.detail', name='checkins_detail'),

    url(r'^for/(?P<username>[-\w]+)/$', view='checkins.views.for_user',
            name='checkins_for_user'),

    url(r'^checkins/friends/of/(?P<username>[-\w]+)/$',
            view='checkins.views.friends',
            name='checkins_friends'),

    url(r'^delete/(?P<id>\d+)/', view='points.views.delete', name='checkins_delete'),
    url(r'change/(?P<id>\d+)/', view='points.views.change', name='checkins_change'),


    url(r'list/(?P<app_label>[-\w]+)/(?P<model_name>[-\w]+)/(?P<id>\d+)/$',\
            view='checkins.views.list', name='checkins_list'),


    url(r'add/(?P<app_label>[-\w]+)/(?P<model_name>[-\w]+)/(?P<id>\d+)/$',\
            view='checkins.views.add', name='checkins_add'),

)

'''
from settings import INSTALLED_APPS

if 'piston' in INSTALLED_APPS:
    from piston.resource import Resource
    from piston.authentication import HttpBasicAuthentication

    from points.handlers import PointHandler

    point_resource = Resource(handler=PointHandler)

    urlpatterns += patterns('',

            url(r'^api/(?P<id>\d+)/$', point_resource),

    )
'''
