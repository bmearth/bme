from checkins.models import CheckIn
from django.contrib.gis import admin

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




class CheckInAdmin(BME_OSMAdmin):
    this='that'

admin.site.register(CheckIn, CheckInAdmin)
