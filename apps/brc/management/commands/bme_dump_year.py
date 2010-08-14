from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from cStringIO import StringIO
import csv, codecs
import os
import re
from brc.models import ArtInstallation, ThemeCamp, PlayaEvent, Year, CircularStreet


class Command(BaseCommand):
    '''Dump BRC models.'''

    help = "exports CSV files for Streets, ThemeCamps, ArtInstallations, and PlayaEvents"""
    args = 'year'
    option_list = BaseCommand.option_list + (
        make_option('--dest', dest='dest', default='.',
            help='Where to put the output files.'),
    )

    def handle(self, *args, **options):
        if not args:
            raise CommandError("No year specified")

        y = args[0]

        try:
            self.year = Year.objects.get(year = y)
        except Year.DoesNotExist:
            raise CommandError("Can't find year '%s' in the database." % y)

        self.verbose = options.get('verbosity', 0) > 0

        destdir = options['dest']
        self.destdir = os.path.abspath(destdir)

        if not os.path.exists(destdir):
            self.verbose_log("Making output directory: %s", destdir)
            os.path.mkdirs(destdir)

        self.circle_streets = {}
        for c in CircularStreet.objects.all():
            self.circle_streets['%s_%s' % (c.year.year, c.name.lower())] = c

        self.dump_streets()
        self.dump_camps()
        self.dump_art()
        self.dump_events()

    def dump_art(self):
        fn, outfile = self.get_outfile('art')
        fields = ['id','year','name','slug','artist','description',
                  'url','contact_email','image','circular_street',
                  'time_address','distance','location_string']
        writer = UnicodeWriter(outfile, fields)
        writer.writeheader()
        for art in ArtInstallation.objects.filter(year=self.year):
            row = self.parse_fields(art, fields)
            writer.writerow(row)


    def dump_camps(self):
        fn, outfile = self.get_outfile('camps')
        fields = ['id','year','name','slug','description',
                  'url','contact_email','hometown','image',
                  'location_string','list_online','circular_street',
                  'time_address']
        writer = UnicodeWriter(outfile, fields)
        writer.writeheader()
        for camp in ThemeCamp.objects.filter(year=self.year):
            row = self.parse_fields(camp, fields)
            writer.writerow(row)

    def dump_events(self):
        fn, outfile = self.get_outfile('events')
        fields = ['id','year','slug','print_description','hosted_by_camp',
                  'located_at_art', 'other_location', 'url',
                  'contact_email','all_day','list_online','list_contact_online',
                  'creator','moderation']
        writer = UnicodeWriter(outfile, fields)
        writer.writeheader()
        for event in PlayaEvent.objects.filter(year=self.year, moderation__in=('U','A')):
            row = self.parse_fields(event, fields)
            writer.writerow(row)


    def dump_streets(self):
        fn, outfile = self.get_outfile('circlestreets')
        fields = ['id','year','name','order','width','distance_from_center']
        writer = UnicodeWriter(outfile, fields)
        writer.writeheader()
        for street in CircularStreet.objects.filter(year=self.year):
            row = self.parse_fields(street, fields)
            writer.writerow(row)


    def get_outfile(self, section):
        fn = os.path.join(self.destdir, '%s_%s.csv' % (self.year.year, section))
        self.verbose_log('Writing: %s', fn)
        return (fn, open(fn, 'wb'))

    def parse_fields(self, obj, fields):
        MODERATION = {'U' : 'Unmoderated', 'A' : 'Accepted', 'R' : 'Rejected'}
        row = {}
        for field in fields:
            if field == 'year':
                val = obj.year.year

            elif field == 'image':
                val = obj.image.name

            elif field == 'slug':
                if obj.slug:
                    val = slugify(obj.slug)
                else:
                    val = slugify(obj.name)

            elif field == 'circular_street':
                try:
                    val = obj.circular_street.name
                except AttributeError:
                    val = ''

            elif field == 'hosted_by_camp':
                try:
                    val = obj.hosted_by_camp.name
                except AttributeError:
                    val = ''

            elif field == 'located_at_art':
                try:
                    val = obj.located_at_art.name
                except AttributeError:
                    val = ''

            elif field == 'creator':
                try:
                    val = obj.creator.name
                except AttributeError:
                    val = ''

            elif field == 'moderation':
                val = MODERATION.get(obj.moderation, 'Unmoderated')

            else:
                val = getattr(obj, field)

            row[field] = val
        return row


    def verbose_log(self, fmt, *args):
        if self.verbose:
            print fmt % args

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    value = value.replace(' ','-')
    return value

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, fieldnames, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.fieldnames =  fieldnames
        self.queue = StringIO()
        self.writer = csv.DictWriter(self.queue, fieldnames, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writeheader(self):
        f = {}
        for field in self.fieldnames:
            f[field] = field
        self.writerow(f)

    def writerow(self, row):
        for key in row.keys():
            val = row[key]
            if val:
                try:
                    val = val.strip()
                    val = val.encode('utf-8')
                except AttributeError:
                    pass
            else:
                val = ''
            row[key] = val
        self.writer.writerow(row)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
