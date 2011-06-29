import os,sys,csv, codecs, cStringIO, time

from time import strptime

sys.path.append('../../../../pinax/apps')
sys.path.append('../../../../../src')
sys.path.append('../../../../../src/bme/apps')

os.environ['DJANGO_SETTINGS_MODULE'] ='bme.settings'

from brc.models import *
from brc.views import *

from django.template.defaultfilters import slugify

curr_year='2010'
xyear = Year.objects.filter(year=curr_year)

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

reader = UnicodeReader(open("2010_art.csv", "rb"))
count = 0
bad_count = 0
for row in reader:
	try:
		#art = ArtInstallation.objects.get(bm_fm_id=row[0])
		#art.name = row[1]
                art = ArtInstallation()
                art.bm_fm_id = row[0]
                art.name = row[1]
                art.year = xyear[0]
                art.slug = slugify(row[1])
                # we don't have the following data at this time
		#art.description = row[3]
		#art.location_string = row[4]
		#art.artist = row[5]
		#art.contact_email = row[8]
		art.save()
                print art
		
		'''
		if(row[3] and row[4]):
			art.time_address = row[3]
			art.distance = row[4]
			xtime = strptime(row[3], "%H:%M")
			point = geocode2(xyear[0].year, xtime.tm_hour, xtime.tm_min, int(row[4]))
			art.location_point = point
			art.save()
		elif(row[2]):
			art.location_string = row[2]
			art.save()
		'''
		count += 1
	except AttributeError, msg:
		print msg
	except:
		print sys.exc_info()
		bad_count += 1
		pass

