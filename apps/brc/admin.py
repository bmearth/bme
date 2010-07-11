from django.conf import settings
from swingtime.admin import EventNoteInline, OccurrenceInline
from django.contrib.gis import admin
from brc.models import *

class BME_OSMAdmin(admin.OSMGeoAdmin):
    wms_url = 'http://strabo.pictearth.com/cgi-bin/mapserv?map=/data/projects/burningman09/brc2009.map'
    wms_layer = 'BRC_2009'
    wms_name = 'Theme Camp Map'
    default_lat = 4980570.4837072379887104
    default_lon = -13269816.5229190997779369
    default_zoom = 13
    display_srid = 4326
    list_per_page = 20
    openlayers_url = '/media/js/openlayers/OpenLayers.js'

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
    list_display = ('name', 'year', 'bm_fm_id', 'location_string', 'location_point', 'location_poly')
    list_filter = ['year', 'circular_street', 'time_address']
    ordering = ('name',)
    search_fields = ('name','description','bm_fm_id')
    list_per_page = 50
    
    def queryset(self, request):
        return ThemeCamp.all_objects

class ArtInstallationAdmin(BME_OSMAdmin):
    list_display = ('name','year', 'bm_fm_id', 'location_string', 'artist', 'url', 'contact_email')
    list_filter = ['year']
    search_fields = ('name','description', 'bm_fm_id')
    list_per_page = 50

class VehicleAdmin(BME_OSMAdmin):
    list_display = ('name', 'year', 'type','last_point')
    list_filter = ['year']
    search_fields = ('name','description')

class PlayaEventAdmin(BME_OSMAdmin):
    list_display = ('title', 'event_type', 'year', 'print_description', 'moderation')
    list_filter = ['year', 'event_type', 'moderation']
    ordering = ['title']
    search_fields = ('title','description', 'print_description')
    inlines = [EventNoteInline, OccurrenceInline]

    actions = ['make_accepted', 'make_rejected', 'make_unmoderated']
    def make_accepted(self, request, queryset):
      rows_updated=queryset.update(moderation='A')
      if rows_updated == 1:
          message_bit = "1 event was"
      else:
          message_bit = "%s events were" % rows_updated
      self.message_user(request, "%s successfully marked as Accepted." % message_bit)
    make_accepted.short_description = "Moderate selected events as accepted"
    
    def make_rejected(self, request, queryset):
      rows_updated=queryset.update(moderation='R')
      if rows_updated == 1:
          message_bit = "1 event was"
      else:
          message_bit = "%s events were" % rows_updated
      self.message_user(request, "%s successfully marked as Rejected." % message_bit)
    make_rejected.short_description = "Moderate selected events as rejected"
    
    def make_unmoderated(self, request, queryset):
      rows_updated=queryset.update(moderation='U')
      if rows_updated == 1:
          message_bit = "1 event was"
      else:
          message_bit = "%s events were" % rows_updated
      self.message_user(request, "%s successfully marked as Unmoderated." % message_bit)
    make_unmoderated.short_description = "Moderate selected events as unmoderated"

class TrackPointAdmin(BME_OSMAdmin):
    list_display = ('user', 'vehicle', 'xypoint', 'xypoint_time')
    list_filter = ['user', 'vehicle']
    search_fields = ('user','vehicle')

class ThreeDModelAdmin(BME_OSMAdmin):
    list_display = ('art_installation', 'theme_camp', 'vehicle', 'model_url',)

class InfrastructureAdmin(BME_OSMAdmin):
    list_display = ('name','year','location_point')
    list_filter = ['year']
    search_fields = (['name'])
    list_editable = (['location_point'])
    
admin.site.register(Year, YearAdmin)
admin.site.register(CircularStreet, CircularStreetAdmin)
admin.site.register(TimeStreet, TimeStreetAdmin)
admin.site.register(ThemeCamp, ThemeCampAdmin)
admin.site.register(ArtInstallation, ArtInstallationAdmin)
admin.site.register(PlayaEvent, PlayaEventAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(TrackPoint, TrackPointAdmin)
admin.site.register(ThreeDModel, ThreeDModelAdmin)
admin.site.register(Infrastructure, InfrastructureAdmin)
