import sys,os
import urllib2
from BeautifulSoup import BeautifulSoup
import re
import psycopg2 as Database

sys.path.append('/home/bme/src/pinax/apps')
sys.path.append('/home/bme/src')
sys.path.append('/home/bme/src/bme/apps')

os.environ['DJANGO_SETTINGS_MODULE'] ='bme.settings'

from brc.models import *

def process_page(url):
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)

    camps = soup.findAll('span', { "class": "subhead" })

    for camp in camps:
        try:
            title = camp.string.strip()
            #print title
            description = camp.findNextSibling(text=True)
            description_str = description.strip()
            hometown = description.findNextSibling(text=True)
            hometown_str = hometown.replace('Hometown:', '')
            contact = None 
            url = None

            nextstr = hometown.findNextSibling(text=True)
            if(nextstr.find("Contact")>-1):
                contact = nextstr.findNextSibling().string
            elif(nextstr.find("URL")>-1):
                url = nextstr.findNextSibling()
                contact = url.findNextSibling().findNextSibling()
            
            if(contact):
                contact = contact.string
                contact = contact.replace(" (at) ", "@")
                contact = contact.replace(" (dot) ", ".")

            #year = Year.objects.get(year='2009')
	    xcamp = ThemeCamp.objects.filter(year=year,name=title)[0]
            if(hometown != None):
                xcamp.hometown = str(hometown_str).strip()[:50]
            xcamp.description = description.strip(),
            #if(url): 
            # 	xcamp.url = str(url).strip()
            if(contact):
                xcamp.contact_email = str(contact).strip()
            xcamp.save()
        except NameError, msg:
            print msg
        except AttributeError, msg:
            print msg
        except RuntimeError, msg:
            print msg
        except TypeError, msg:
            print msg
        except Database.InternalError, msg:
            print msg
        except Database.DataError, msg:
            print msg
        except:
            print "Unexpected error:", sys.exc_info()[0]

pages = [
    'http://www.burningman.com/themecamps/09_camp_vill_number.html',
    'http://www.burningman.com/themecamps/09_camp_vill_a.html',
    'http://www.burningman.com/themecamps/09_camp_vill_b.html',
    'http://www.burningman.com/themecamps/09_camp_vill_c.html',
    'http://www.burningman.com/themecamps/09_camp_vill_d.html',
    'http://www.burningman.com/themecamps/09_camp_vill_e.html',
    'http://www.burningman.com/themecamps/09_camp_vill_f.html',
    'http://www.burningman.com/themecamps/09_camp_vill_g.html',
    'http://www.burningman.com/themecamps/09_camp_vill_h.html',
    'http://www.burningman.com/themecamps/09_camp_vill_i.html',
    'http://www.burningman.com/themecamps/09_camp_vill_j.html',
    'http://www.burningman.com/themecamps/09_camp_vill_k.html',
    'http://www.burningman.com/themecamps/09_camp_vill_l.html',
    'http://www.burningman.com/themecamps/09_camp_vill_m.html',
    'http://www.burningman.com/themecamps/09_camp_vill_n.html',
    'http://www.burningman.com/themecamps/09_camp_vill_o.html',
    'http://www.burningman.com/themecamps/09_camp_vill_p.html',
    'http://www.burningman.com/themecamps/09_camp_vill_q.html',
    'http://www.burningman.com/themecamps/09_camp_vill_r.html',
    'http://www.burningman.com/themecamps/09_camp_vill_s.html',
    'http://www.burningman.com/themecamps/09_camp_vill_t.html',
    'http://www.burningman.com/themecamps/09_camp_vill_u.html',
    'http://www.burningman.com/themecamps/09_camp_vill_v.html',
    'http://www.burningman.com/themecamps/09_camp_vill_w.html',
    'http://www.burningman.com/themecamps/09_camp_vill_y.html',
    'http://www.burningman.com/themecamps/09_camp_vill_z.html']

for page in pages:
    process_page(page)
