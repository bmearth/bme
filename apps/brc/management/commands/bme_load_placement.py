from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import csv, codecs
import os
import sys
from brc.models import ThemeCamp, Year, CircularStreet


class Command(BaseCommand):
    '''Load placement data from a CSV file.

    To update: Simply re-run on the newer CSV file.
    Any unchanged entries will be left alone, and any changed ones will be
    updated properly and the new rows inserted.'''

    help = "Imports a CSV placement file for themecamps."
    args = 'file'
    option_list = BaseCommand.option_list + (
        make_option('--dryrun', action='store_true', dest='dryrun', default=False,
            help='Do not update the database, just test what would happen.'),
    )

    def handle(self, *args, **options):
        processed = 0
        new = 0
        updated = 0
        unchanged = 0
        if not args:
            raise CommandError("No file specified")
        fname = args[0]
        if not os.path.isfile(fname):
            raise RuntimeError("File: %s is not a normal file or doesn't exist." % fname)

        self.dryrun = options.get('dryrun', False)
        self.verbose = options.get('verbosity', 0) > 0
        infile = open(fname, 'r')
        self.years = {}
        for y in Year.objects.all():
            self.years[y.year] = y

        if self.verbose:
            print "Years: %s" % "\n".join(self.years.keys())

        self.circle_streets = {}
        for c in CircularStreet.objects.all():
            self.circle_streets['%s_%s' % (c.year.year, c.name.lower())] = c

        if self.verbose:
            keys = self.circle_streets.keys()
            keys.sort()
            print "Circles: %s" % "\n".join(keys)

        fields = ['year',
                  'bm_fm_id',
                  'name',
                  'location_string',
                  'url',
                  'people_count', #ignored
                  'placement_size', #ignored
                  'description',
                  'contact_firstname', #ignored
                  'contact_lastname', #ignored
                  'home_city',
                  'home_state',
                  'home_country',
                  'contact_email'
                  ]
        reader = UnicodeDictReader(infile, fields)
        for row in reader:
            processed += 1
            data = self.parse_row(row)
            try:
                camp = ThemeCamp.objects.get(bm_fm_id = data['bm_fm_id'])
                dirty, camp = self.update_camp_data(camp, data)
                if dirty:
                    updated += 1
                else:
                    unchanged += 1
            except ThemeCamp.DoesNotExist:
                camp = self.create_camp(data)
                new += 1

        print "Done\nTotal processed: %d\nNew: %d\nUpdated: %d\nUnchanged: %d" % (processed, new, updated, unchanged)

    def create_camp(self, data):
        camp = ThemeCamp()
        for key, val in data.items():
            if val is not None:
                setattr(camp, key, val)
        if not self.dryrun:
            camp.save()
        if self.verbose:
            print 'Created: %s' % camp.name
        return camp

    def parse_row(self, row):
        year = self.years.get(row['year'], None)
        if year is None:
            print "ABORT: Cannot find year '%(year)s" % row
            sys.exit(1)

        hometown = "%(home_city)s, %(home_state)s" % row
        country = row['home_country']
        if country and country.lower() !=  'united states of america':
            hometown = '%s, %s' % (hometown, country)

        description = row['description']
        description = description.replace('', ' ')
        description = description.replace('  ', ' ')

        loc = row['location_string']
        # parse this
        if '&' in loc:
            cname, time_address = loc.split('&')
            cname = cname.strip()
            time_address = time_address.strip()
            if cname[0] in '0123456789':
                holder = time_address
                time_address = cname
                cname = holder

            # normalize on ordering of street & time
            loc = "%s & %s" % (cname, time_address)

            hour = time_address.split(':')[0]
            if len(hour) == 1:
                time_address = "0" + time_address

            circle_street = self.circle_streets.get('%s_%s' % (year, cname.lower()), None)
            if circle_street is None and self.verbose:
                print "Error finding '%s'" % cname

            # final sanity check for time
            clean_time = []
            for ch in time_address:
                if ch in '0123456789:':
                    clean_time.append(ch)
            if len(clean_time) == 5:
                time_address = ''.join(clean_time) + ":00"
            else:
                time_address = None


        else:
            if self.verbose and loc:
                print "Can't parse location: %s" % loc
            circle_street = None
            time_address = None

        data = {
            'year' : year,
            'bm_fm_id' : int(row['bm_fm_id']),
            'name' : row['name'],
            'location_string' : loc,
            'url' : row['url'],
            'description' : description,
            'hometown' : hometown,
            'contact_email' : row['contact_email'],
            'circular_street' : circle_street,
            'time_address' : time_address,
            }
        return data

    def update_camp_data(self, camp, data):
        dirty = False
        dirties = []

        for key, val in data.items():
            ok = True
            oldval = getattr(camp, key)
            if oldval != val:
                if key == 'time_address' and not val:
                    ok = False

                if ok:
                    dirty = True
                    setattr(camp, key, val)
                    dirties.append("%s: %s -> %s" % (key, oldval, val))

        if dirty:
            if not self.dryrun:
                camp.save()
            if self.verbose:
                print 'Updated: %s\n%s' % (camp.name, dirties)
        else:
            if self.verbose:
                print "Unchanged: %s" % camp.name

        return dirty, camp

class UTF16Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-16
    """
    def __init__(self, f, encoding):
        reader = codecs.getreader(encoding)
        reader.errors = 'ignore'
        self.reader = reader(f)

    def __iter__(self):
        return self

    def next(self):
        ret = self.reader.next().encode("utf-16")
        ret = ret.replace('\x00','')
        return ret

class UnicodeDictReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, fields, dialect=csv.excel, encoding="utf-16", **kwds):
        f = UTF16Recoder(f, encoding)
        self.reader = csv.DictReader(f, fields, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        for key in row.keys():
            val = unicode(row[key], "utf-8", errors='ignore')
            if val.startswith('"'):
                val = val[1:]
            if val.endswith('"'):
                val = val[:-1]
            val = val.replace("\'", "'")
            val = val.replace(u'\x1c','"')
            val = val.replace(u'\x1d','"')
            val = val.strip()
            row[key] = val
        return row

    def __iter__(self):
        return self
