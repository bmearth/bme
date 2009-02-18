from django.conf import settings
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


class year_admin(admin.OSMGeoAdmin):
    list_display = ('year','location')


class time_street_admin(BME_OSMAdmin):
    list_display = ('name', 'year',)
    list_filter = ['year']

class circular_street_admin(admin.OSMGeoAdmin):
    list_display = ('name', 'year','order', 'distance_from_center')
    list_filter = ['year']   
    ordering = ('year','order')

class theme_camp_admin(BME_OSMAdmin):
    list_display = ('name', 'year', 'circular_street', 'time_address','location_point', 'location_poly')
    list_filter = ['year', 'circular_street', 'time_address']
    ordering = ('name',)
    search_fields = ('name','description')

class art_installation_admin(BME_OSMAdmin):
    list_display = ('name','year', 'location_point')
    list_filter = ['year']
    search_fields = ('name','description')

class vehicle_admin(BME_OSMAdmin):
    list_display = ('name', 'year', 'type','last_point')
    list_filter = ['year']
    search_fields = ('name','description')

class playa_event_admin(BME_OSMAdmin):
    list_display = ('name', 'year', 'type', 'start_date_time', 'end_date_time')
    list_filter = ['year', 'type']
    ordering = ('name','start_date_time')
    search_fields = ('name','description')

class track_point_admin(BME_OSMAdmin):
    list_display = ('user', 'vehicle', 'xypoint', 'xypoint_time')
    list_filter = ['user', 'vehicle']
    search_fields = ('user','vehicle')

class three_d_model_admin(BME_OSMAdmin):
    list_display = ('art_installation', 'theme_camp', 'vehicle', 'model_url',)

admin.site.register(year, year_admin)
admin.site.register(circular_street, circular_street_admin)
admin.site.register(time_street, time_street_admin)
admin.site.register(theme_camp, theme_camp_admin)
admin.site.register(art_installation, art_installation_admin)
admin.site.register(playa_event, playa_event_admin)
admin.site.register(vehicle, vehicle_admin)
admin.site.register(track_point, track_point_admin)
admin.site.register(three_d_model, three_d_model_admin)

