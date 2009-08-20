from django.contrib.gis.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

#from olwidget.widgets import MapDisplay


class CheckIn(models.Model):
    ''' a geographic point that can be added to any model instance

    '''
    owner = models.ForeignKey('auth.User')
    datetime = models.DateTimeField(editable=False, auto_now=True)

    # in case we can't get an content_object with a point,
    # we may allow just adding out own
    point = models.PointField(blank=True, null=True)

    objects = models.GeoManager()

    # This is the object that should be geocoded, hopefully
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()

    def __unicode__(self):
        return "%s::%s::%s" % (self.owner, self.content_object, self.datetime)

    @models.permalink
    def get_absolute_url(self):
        return ('checkins.views.detail', (str(self.id),))

    def save(self, force_insert=False, force_update=False):
        ''' try to get the point of the object we are checking into '''
        if not self.point:

            location_point = getattr(self.content_object, 'location_point', None)
            point = getattr(self.content_object, 'point', None)

            if location_point:
                self.point = location_point

            elif point:
                self.point = point

            else:
                pass

        super(CheckIn, self).save(force_insert, force_update) # Call the "real" save() method.

    class Meta:
        ordering=( '-datetime', )


