import math

clat = 40.769288
clon = -119.220037 

def getpoint(lat1,lon1,dist,dir):
        lat1 = (math.pi/180)*lat1
        lon1 = (math.pi/180)*lon1
        dir = (math.pi/180)*dir
        dist = dist / (185200.0/30.48)
        dist = dist / (180*60/math.pi)

        lat=math.asin(math.sin(lat1)*math.cos(dist)+math.cos(lat1)*math.sin(dist)*math.cos(dir))
        dlon=math.atan2(math.sin(dir)*math.sin(dist)*math.cos(lat1),math.cos(dist)-math.sin(lat1)*math.sin(lat))
        lon = ((lon1 - dlon+math.pi) % (2*math.pi)) - math.pi

        lat = lat * (180/math.pi)
        lon = lon * (180/math.pi)
        pnt = [float(lon), float(lat)]

        return pnt

def add_node(lat,lon):
	global nodeid
	global nodes
	if (nodes.get(str(lat) + '_' + str(lon),0) == 0):
		print("<node id='" + str(nodeid) + "' visible='true' lat='" + str(lat) + "' lon='" + str(lon) + "' />")
		nodes[str(lat) + '_' + str(lon)] = nodeid
		nodeid = nodeid - 1
	return nodes[str(lat) + '_' + str(lon)]
        
def ret_arc(lat,lon,dist,angle_start,angle_end,interval):
	global wayid
	waynodes = []
	for x in range(angle_start,angle_end+interval,interval):
		p = getpoint(lat,lon,dist,x)
		waynodes.append( add_node(p[1], p[0]) )
	
	print("<way id='" + str(wayid) + "' visible='true'>")
	for n in waynodes:
		print("<nd ref='" + str(n) + "' />")
	print("<tag k='name' v='" + str(dist) + "'/>")
	print("<tag k='highway' v='pedestrian'/>")
	print("</way>")
	wayid = wayid - 1	

nodeid = -1
wayid = -1
nodes = {}

print("<?xml version='1.0' encoding='UTF-8'?>")
print("<osm version='0.6'>")
		
for x in range(400,7600,200):
 if x <= 2600:
	 ret_arc(clat,clon,x,0,360,1)
 else:
   ret_arc(clat,clon,x,240,360,1)
 
for x in range(0,375,15):
	if x >= 240 and x <= 360:
		dist = 7400
	else:
	  dist = 2600
	waynodes = []
	waynodes.append( add_node(clat, clon) )
	p = getpoint(clat,clon,dist,x)
	waynodes.append( add_node(p[1], p[0]) )
	print("<way id='" + str(wayid) + "' visible='true'>")
	for n in waynodes:
		print("<nd ref='" + str(n) + "' />")
	print("<tag k='highway' v='pedestrian'/>")
	name = str(((300 - x) % 360) / 30) + ":"
	if ((300 - x) % 30) == 15:
		name = name + "30"
	else:
	  name = name + "00"	 
	print("<tag k='name' v='" + name + "' />")
	print("</way>")
	wayid = wayid - 1
		 
print("</osm>")  
