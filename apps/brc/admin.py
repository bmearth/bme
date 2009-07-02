from django.conf import settings
from swingtime.admin import EventNoteInline, OccurrenceInline
from django.contrib.gis import admin
from brc.models import *



class BME_OSMAdmin(admin.OSMGeoAdmin):
    wms_url = 'http://earthdev.burningman.com/cgi-bin/mapserv?map=/home/ortelius/brc2008.map'
    wms_layer = 'brc2008'
    wms_name = 'Theme Camp Map'
    default_lat = 4980570.4837072379887104
    default_lon = -13269816.5229190997779369
    default_zoom = 13
    display_srid = 4326
    list_per_page = 20
    openlayers_url = 'http://www.openlayers.org/api/2.8/OpenLayers.js'

class YearAdmin(admin.OSMGeoAdmin):
    list_display = ('year','location')


class TimeStreetAdmin(BME_OSMAdmin):
    list_display = ('name', 'year', 'street_line')
    list_filter = ['year']
    list_editable  = ('street_line',)

class CircularStreetAdmin(BME_OSMAdmin):
    list_display = ('name', 'year','order', 'distance_from_center', 'street_line')
    list_filter = ['year']   
    ordering = ('year','order')
    list_editable = ('street_line',)

class ThemeCampAdmin(BME_OSMAdmin):
    list_display = ('name', 'year', 'circular_street', 'time_address','location_point', 'location_poly')
    list_filter = ['year', 'circular_street', 'time_address']
    ordering = ('name',)
    search_fields = ('name','description')

class ArtInstallationAdmin(BME_OSMAdmin):
    list_display = ('name','year', 'location_point')
    list_filter = ['year']
    search_fields = ('name','description')

class VehicleAdmin(BME_OSMAdmin):
    list_display = ('name', 'year', 'type','last_point')
    list_filter = ['year']
    search_fields = ('name','description')

class PlayaEventAdmin(BME_OSMAdmin):
    list_display = ('title', 'event_type', 'year')
    list_filter = ['year', 'event_type']
    ordering = ['title']
    search_fields = ('title','description')
    inlines = [EventNoteInline, OccurrenceInline]

class TrackPointAdmin(BME_OSMAdmin):
    list_display = ('user', 'vehicle', 'xypoint', 'xypoint_time')
    list_filter = ['user', 'vehicle']
    search_fields = ('user','vehicle')

class ThreeDModelAdmin(BME_OSMAdmin):
    list_display = ('art_installation', 'theme_camp', 'vehicle', 'model_url',)

admin.site.register(Year, YearAdmin)
admin.site.register(CircularStreet, CircularStreetAdmin)
admin.site.register(TimeStreet, TimeStreetAdmin)
admin.site.register(ThemeCamp, ThemeCampAdmin)
admin.site.register(ArtInstallation, ArtInstallationAdmin)
admin.site.register(PlayaEvent, PlayaEventAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(TrackPoint, TrackPointAdmin)
admin.site.register(ThreeDModel, ThreeDModelAdmin)

