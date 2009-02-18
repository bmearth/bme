import sys,os
import urllib2
from BeautifulSoup import BeautifulSoup
import re

sys.path.append('/var/projects')
os.environ['DJANGO_SETTINGS_MODULE'] ='bme.settings'

from bme.web.models import *


def process_page(url):
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page)

    camps = soup.findAll('span', { "class": "subhead" })

    for camp in camps:
        try:
            title = camp.string
            print title
            description = camp.findNextSibling(text=True)
            print description
            hometown = description.findNextSibling(text=True)
            print hometown
            
            contact = ""
            url = ""

            nextstr = hometown.findNextSibling(text=True)
            if(nextstr == "Contact:"):
                contact = next.findNextSibling().string
            elif(nextstr == "URL:"):
                url = next.findNextSibling()
                contact = url.findNextSibling(text=True)
                url = url.string
                if(contact.strip().startswith("Contact:")):
                    contact = contact.findNextSibling().string
                else:
                    contact = ""
        
            contact = str(contact)
            contact = contact.replace(" (at) ", "@")
            contact = contact.replace(" (dot) ", ".")
            
            print contact
            print url

            xyear = year.objects.get(year='2008')
            newcamp = theme_camp(name = title.strip(),
                    year = xyear)

            #        description = description.strip(),
            #        url = str(url).strip(),
            #        contact_email = str(contact).strip(),
            #        hometown = str(hometown).strip())
            newcamp.save()
        except:
            print "Unexpected error:", sys.exc_info()[0]

pages = [
    #'http://www.burningman.com/themecamps/08_camp_vill_number.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_a.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_b.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_c.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_d.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_e.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_f.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_g.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_h.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_i.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_j.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_k.html',
    'http://www.burningman.com/themecamps/08_camp_vill_l.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_m.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_n.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_o.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_p.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_q.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_r.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_s.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_t.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_u.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_v.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_w.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_y.html',
    #'http://www.burningman.com/themecamps/08_camp_vill_z.html']
    ]

for page in pages:
    process_page(page)
