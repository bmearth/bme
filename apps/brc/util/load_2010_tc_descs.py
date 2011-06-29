import os,sys,csv, codecs, cStringIO

sys.path.append('/home/bme/src/pinax/apps')
sys.path.append('/home/bme/src')
sys.path.append('/home/bme/src/bme/apps')

sys.path.append('../../../../pinax/apps')
sys.path.append('../../../../../src')
sys.path.append('../../../../../src/bme/apps')

os.environ['DJANGO_SETTINGS_MODULE'] ='bme.settings'

from brc.models import *

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

    def __init__(self, f, dialect='excel-tab', encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

reader = UnicodeReader(open("2010_tc_descs.tab", "rb"))
count = 0

for row in reader:
    try:
        #print row[2]
            #print "Year: %s" % row[0]
            #print "BM-FMID: %s" % row[1]
            #print "Camp Name: %s" % row[2]
            #print "Street Add: %s" % row[3]
            #print "URL: %s" % row[4]
            #print "People: %s" % row[5]
            #print "Dimensions: %s" % row[6]
            #print "Desc: %s" % row[7]
            #print "First Name: %s" % row[8]
            #print "Last Name: %s" % row[9]
            #print "City: %s" % row[10]
            #print "State: %s" % row[11]
            #print "Country: %s" % row[12]
            #print "Contact Email: %s" % row[13]
            #print "###"
        
        tc = ThemeCamp.objects.filter(name=row[2], year=xyear)
        
        if not tc:
            #print row[2]
            pass
        else:
            tc = tc[0]
            tc.bm_fm_id = row[1]
            tc.location_string = row[3]
            tc.url = row[4]
            tc.people = row[5]
            tc.dimensions = row[6]
            tc.description = row[7]
            tc.country = row[12]
            tc.contact_email = row[13]
            tc.save()
            print tc
    except:
        print sys.exc_info() 
