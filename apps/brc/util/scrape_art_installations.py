import sys,os
import urllib2
from BeautifulSoup import BeautifulSoup
import re

sys.path.append('/home/bme/src/pinax/apps')
sys.path.append('/home/bme/src')
sys.path.append('/home/bme/src/bme/apps')

os.environ['DJANGO_SETTINGS_MODULE'] ='bme.settings'

from brc.models import *

def slugify(inStr):
    removelist = ["a", "an", "as", "at", "before", "but", "by", "for","from","is", "in", "into", "like", "of", "off", "on", "onto","per","since", "than", "the", "this", "that", "to", "up", "via","with"];
    for a in removelist:
        aslug = re.sub(r'\b'+a+r'\b','',inStr)
    aslug = re.sub('[^\w\s-]', '', aslug).strip().lower()
    aslug = re.sub('\s+', '-', aslug)
    return aslug


def process_page(url):
	page = urllib2.urlopen(url)
	soup = BeautifulSoup(page)
	brs = soup.findAll('br')
	for br in brs:
		br.extract()

	installations = soup.findAll('span', { "class": "subhead" })

	for installation in installations:
		try:
			title = installation.next.next
			artists = title.next
			description = artists.next
			contact = description.next.next
			if(contact.string):
				if(contact.string.strip() == 'Contact:'):
					contact = contact.next
			print title.strip()
			print artists.strip()
			print description.strip()
			#print contact.string.strip()
			print

			year = Year.objects.get(year='2009')
			newart = ArtInstallation(name = title.strip(),
					year = year,
					artist = str(artists.strip()),
					slug = slugify(title.strip()),
					description = description.strip())
			newart.save()
			print newart
		except:
			print title
			print "Unexpected error:", sys.exc_info()

pages = ['http://www.burningman.com/installations/09_art_brc.html',]

for page in pages:
	process_page(page)
