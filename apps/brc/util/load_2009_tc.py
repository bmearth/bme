import os,sys,csv, codecs, cStringIO

sys.path.append('/home/bme/src/pinax/apps')
sys.path.append('/home/bme/src')
sys.path.append('/home/bme/src/bme/apps')

os.environ['DJANGO_SETTINGS_MODULE'] ='bme.settings'

from brc.models import *

curr_year='2009'
xyear = Year.objects.filter(year=curr_year)
print xyear[0]

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

reader = UnicodeReader(open("whwhwh2009Names.csv", "rb"))
count = 0
for row in reader:
	tc = ThemeCamp(year=xyear[0], name=row[0], bm_fm_id=row[1])
	print tc
	if(count > 0): #Skip First Line
		print
		tc.save()
	count+=1
