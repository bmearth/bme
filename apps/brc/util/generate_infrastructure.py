import sys,os
import math
from django.contrib.gis.geos import *

sys.path.append('../../../../bme/src/pinax/apps')
sys.path.append('../../../..')
sys.path.append('../../../../bme/apps')

os.environ['DJANGO_SETTINGS_MODULE'] ='bme.settings'

from brc.models import *
from brc.views import *

curr_year='2009'
year = Year.objects.filter(year=curr_year)[0]
clat = 40.769288
clon = -119.220037 

def ret_point(lat,lon,dist,angle):
	pnt = getpoint(lat,lon,dist,-angle) 
	return str(pnt.x) + ' ' + str(pnt.y)
	
def ret_street_point(year, hour, minute, street):
	pnt = geocode(year.year, hour, minute, street)
	return str(pnt.x) + ' ' + str(pnt.y)

def ret_arc(lat,lon,dist,angle_start,angle_end,interval):
	linestring = ""
	for x in range(angle_start,angle_end,interval):
		linestring = linestring + ret_point(lat,lon,dist,x) + ","
	linestring = linestring + ret_point(lat,lon,dist,angle_end)
	return linestring

# CENTER CAMP
(cc,dist_inner_ring,dist_outer_ring) = centercamp(year)

## INNER RING
linestring = "LINESTRING(" + ret_arc(cc.y,cc.x,dist_inner_ring,0,360,1) + ")"
inner_ring = Infrastructure.objects.create(year=year)
inner_ring.name = "Center Camp"
inner_ring.location_line = linestring
inner_ring.tags = 'road'
inner_ring.save()	

## OUTER RING
linestring = "LINESTRING(" + ret_arc(cc.y,cc.x,dist_outer_ring,0,360,1) + ")"
outer_ring = Infrastructure.objects.create(year=year)
outer_ring.name = "Evolution"
outer_ring.location_line = linestring
outer_ring.tags = 'road'
outer_ring.save()

## 6 o'clock spur
B = CircularStreet.objects.filter(year=year,name__startswith='B')[0]
D = CircularStreet.objects.filter(year=year,name__startswith='D')[0]
pt1 = six.street_line.intersection(B.street_line)
pt2 = six.street_line.intersection(D.street_line)
linestring = "LINESTRING("
linestring = linestring + str(pt1.x) + " " + str(pt1.y) + "," 
linestring = linestring + str(pt2.x) + " " + str(pt2.y)
linestring = linestring + ")"
six_spur = Infrastructure.objects.create(year=year)
six_spur.name = "6:00"
six_spur.location_line = linestring
six_spur.tags = 'road'
six_spur.save()

## B spurs
pts = [geocode('2009', 5, 30, B.name), geocode('2009', 6, 30, B.name)]
for i in range(0,2):
	linestring = "LINESTRING("
	linestring = linestring + str(pts[i].x) + " " + str(pts[i].y) + ","
	linestring = linestring + str(cc.x) + " " + str(cc.y)
	linestring = linestring + ")"
	b_spur = Infrastructure.objects.create(year=year)
	b_spur.name = B.name
	b_spur.location_line = GEOSGeometry(linestring).difference(inner_ring.location_line.convex_hull)
	b_spur.tags = 'road'
	b_spur.save()

# DOUBLEWIDES
## Extinct .. 8/8:30, 5/7, 3:30/4
A = CircularStreet.objects.filter(year=year,name__startswith='A')[0]
E = CircularStreet.objects.filter(year=year,name__startswith='E').exclude(name__iexact='Esplanade').exclude(name__iexact='Evolution')[0].name
L = CircularStreet.objects.filter(year=year,name__startswith='L')[0]
geom_collection = "GEOMETRYCOLLECTION("

geom_collection = geom_collection + "POLYGON(("
geom_collection = geom_collection + ret_street_point(year,8,0,D.name) + ","
geom_collection = geom_collection + ret_street_point(year,8,30,D.name) + ","
geom_collection = geom_collection + ret_street_point(year,8,30,L.name) + ","
geom_collection = geom_collection + ret_street_point(year,8,0,L.name) + ","
geom_collection = geom_collection + ret_street_point(year,8,0,D.name)
geom_collection = geom_collection + ")),"

geom_collection = geom_collection + "POLYGON(("
geom_collection = geom_collection + ret_street_point(year,5,0,A.name) + ","
geom_collection = geom_collection + ret_street_point(year,7,0,A.name) + ","
geom_collection = geom_collection + ret_street_point(year,7,0,L.name) + ","
geom_collection = geom_collection + ret_street_point(year,5,0,L.name) + ","
geom_collection = geom_collection + ret_street_point(year,5,0,A.name)
geom_collection = geom_collection + ")),"

geom_collection = geom_collection + "POLYGON(("
geom_collection = geom_collection + ret_street_point(year,3,30,D.name) + ","
geom_collection = geom_collection + ret_street_point(year,4,0,D.name) + ","
geom_collection = geom_collection + ret_street_point(year,4,0,L.name) + ","
geom_collection = geom_collection + ret_street_point(year,3,30,L.name) + ","
geom_collection = geom_collection + ret_street_point(year,3,30,D.name)
geom_collection = geom_collection + "))"

geom_collection = geom_collection + ")"

double_wide = Infrastructure.objects.create(year=year)
double_wide.name = "double wide camps"
double_wide.location_multigeom = geom_collection
double_wide.tags = 'camp_null'
double_wide.save()

# PROMENADES
for x in (3,6,9):
	pt = geocode(year.year,x,0,'Esplanade')
	linestring = "LINESTRING("
	linestring = linestring + str(clon) + " " + str(clat) + ","
	linestring = linestring + str(pt.x) + " " + str(pt.y)
	linestring = linestring + ")"
	promenade = Infrastructure.objects.create(year=year)
	promenade.name = "Promenade"
	promenade.location_line = GEOSGeometry(linestring).difference(outer_ring.location_line.convex_hull)
	promenade.tags = 'road'
	promenade.save()

Esplanade = CircularStreet.objects.filter(year=year,name='Esplanade')[0]
pt = getpoint(clat,clon,Esplanade.distance_from_center,-time2radial(0,0))
linestring = "LINESTRING("
linestring = linestring + str(clon) + " " + str(clat) + ","
linestring = linestring + str(pt.x) + " " + str(pt.y)
linestring = linestring + ")"
promenade = Infrastructure.objects.create(year=year)
promenade.name = "Promenade"
promenade.location_line = linestring
promenade.tags = 'road'
promenade.save()

# ENTRANCE ROADS (HARDCODED! -- CONTACT GATE CREW FOR UPDATE)
entrance_road = Infrastructure.objects.create(year=year)
entrance_road.name = "entrance"
entrance_road.location_line = "LINESTRING(-119.239315394275 40.7610286856975,-119.236633185256 40.7621988830906,-119.236354235516 40.762410166535,-119.236161116469 40.7626051968109,-119.235903624409 40.762913993577,-119.235689047681 40.7633203029263,-119.235581759327 40.7636778530985,-119.235581759327 40.7640354013478)"
entrance_road.tags = 'road'
entrance_road.save()

entrance_road = Infrastructure.objects.create(year=year)
entrance_road.name = "entrance"
entrance_road.location_line = "LINESTRING(-119.236590269932 40.7622151356829,-119.236010912781 40.7622638934485,-119.235302809605 40.7622476408642,-119.23487365616 40.7621826304856,-119.234487418065 40.7621013674241,-119.234079722291 40.761971346318)"
entrance_road.tags = 'road'
entrance_road.save()

entrance_road = Infrastructure.objects.create(year=year)
entrance_road.name = "entrance"
entrance_road.location_line = "LINESTRING(-119.237985018613 40.7615975342256,-119.23810303581 40.7613862481983,-119.238306883695 40.761256225693,-119.238478545071 40.7611749614988,-119.238671664118 40.7610936972048,-119.238907698507 40.7610327489191,-119.239116910815 40.7610043063667,-119.239326123119 40.7610327489191)"
entrance_road.tags = 'road'
entrance_road.save()

entrance_road = Infrastructure.objects.create(year=year)
entrance_road.name = "entrance"
entrance_road.location_line = "LINESTRING(-119.235270623067 40.7622313882786,-119.236225489472 40.7625158080043)"
entrance_road.tags = 'road'
entrance_road.save()

entrance_road = Infrastructure.objects.create(year=year)
entrance_road.name = "entrance"
entrance_road.location_line = "LINESTRING (-119.2389416527786068 40.7611868217703659, -119.2393105767211239 40.7610310632211394, -119.2394775595245022 40.7609513793597742, -119.2396621865081414 40.7608512529300029, -119.2398670000000038 40.7607449999999929, -119.2400249999999744 40.7606819999999814, -119.2402979999999530 40.7605689999999825, -119.2405679999999819 40.7604510000000104, -119.2408079999999870 40.7603449999999867, -119.2410419999999789 40.7602349999999944, -119.2413920000000047 40.7600630000000024, -119.2416410000000013 40.7599289999999712, -119.2418249999999915 40.7598089999999829, -119.2420130000000000 40.7596739999999897, -119.2421700000000016 40.7595609999999979, -119.2422870000000046 40.7594269999999739, -119.2424020000000127 40.7592780000000019, -119.2425149999999974 40.7591199999999887, -119.2426609999999840 40.7588920000000030, -119.2427930000000060 40.7586809999999673, -119.2429119999999898 40.7584699999999813, -119.2429949999999792 40.7582529999999892, -119.2430769999999995 40.7580259999999797, -119.2431610000000006 40.7578079999999900, -119.2432419999999667 40.7575969999999828, -119.2433070000000015 40.7574320000000014, -119.2433879999999675 40.7572199999999825, -119.2434469999999891 40.7570589999999910, -119.2435229999999819 40.7568460000000030, -119.2435779999999994 40.7566839999999928, -119.2436249999999802 40.7565179999999998, -119.2436880000000059 40.7562959999999848, -119.2437289999999876 40.7560709999999844, -119.2437199999999962 40.7558409999999967, -119.2436919999999958 40.7556079999999952, -119.2436779999999885 40.7554159999999825, -119.2436620000000005 40.7551749999999871, -119.2436439999999749 40.7549349999999748, -119.2436299999999818 40.7546999999999855, -119.2436220000000020 40.7544619999999895, -119.2436160000000029 40.7542229999999819, -119.2436209999999903 40.7539809999999960, -119.2436349999999976 40.7537359999999893, -119.2436519999999831 40.7534949999999938, -119.2436719999999895 40.7532459999999972, -119.2436989999999923 40.7529999999999859, -119.2437390000000050 40.7527499999999918, -119.2437860000000143 40.7525029999999759, -119.2438189999999878 40.7523169999999766, -119.2438690000000037 40.7520699999999962, -119.2439339999999817 40.7518239999999849, -119.2440030000000064 40.7515810000000016, -119.2441000000000031 40.7513359999999949, -119.2442180000000178 40.7510829999999871, -119.2443479999999880 40.7508289999999960, -119.2444649999999911 40.7505859999999771, -119.2445830000000058 40.7503509999999878, -119.2447009999999921 40.7501229999999808, -119.2448269999999724 40.7498939999999976, -119.2449529999999953 40.7496689999999973, -119.2450869999999554 40.7494379999999978, -119.2452029999999894 40.7492570000000001, -119.2453620000000001 40.7490200000000016, -119.2455159999999807 40.7487809999999939, -119.2456679999999949 40.7485369999999989, -119.2458380000000062 40.7482879999999810, -119.2459829999999954 40.7480789999999899, -119.2461349999999811 40.7478689999999801, -119.2463020000000142 40.7476319999999745, -119.2464619999999798 40.7474179999999961, -119.2466090000000065 40.7472289999999902, -119.2467289999999593 40.7470769999999973, -119.2468339999999927 40.7469559999999760, -119.2468559999999655 40.7469349999999935, -119.2468499999999807 40.7469429999999733, -119.2469179999999938 40.7468879999999913, -119.2469869999999617 40.7468219999999874, -119.2471919999999841 40.7466099999999756, -119.2473459999999932 40.7464359999999814, -119.2475729999999885 40.7461749999999938, -119.2477919999999898 40.7459289999999825, -119.2479849999999999 40.7457279999999926, -119.2481870000000015 40.7455459999999761, -119.2483439999999888 40.7454129999999779, -119.2485779999999949 40.7452370000000030, -119.2488389999999612 40.7450579999999789, -119.2491200000000049 40.7448839999999777, -119.2494080000000025 40.7447169999999801, -119.2497009999999875 40.7445499999999754, -119.2499399999999952 40.7444259999999758, -119.2502849999999768 40.7442599999999757, -119.2506180000000029 40.7440980000000010, -119.2508699999999777 40.7439800000000005, -119.2511279999999800 40.7438649999999996, -119.2514740000000018 40.7437179999999941, -119.2517419999999646 40.7436159999999816, -119.2521029999999627 40.7434839999999880, -119.2524869999999595 40.7433640000000068, -119.2527849999999887 40.7432799999999773, -119.2530849999999845 40.7432019999999966, -119.2534890000000019 40.7431109999999848, -119.2537920000000042 40.7430509999999799, -119.2541999999999689 40.7429869999999852, -119.2546059999999954 40.7429389999999927, -119.2549219999999934 40.7429210000000026, -119.2553399999999897 40.7429119999999969, -119.2556580000000110 40.7429159999999797, -119.2559789999999964 40.7429149999999822, -119.2564030000000059 40.7429210000000026, -119.2568030000000050 40.7429399999999831, -119.2572090000000031 40.7429590000000132, -119.2576080000000047 40.7429669999999930, -119.2580070000000063 40.7429849999999973, -119.2584019999999896 40.7430129999999764, -119.2587900000000047 40.7430379999999843, -119.2591710000000091 40.7430659999999989, -119.2595719999999915 40.7430909999999855, -119.2599739999999997 40.7431209999999808, -119.2603810000000095 40.7431519999999736, -119.2607449999999858 40.7431919999999792, -119.2611039999999889 40.7432429999999997, -119.2614509999999797 40.7433029999999903, -119.2617900000000049 40.7433759999999907, -119.2621159999999918 40.7434509999999861, -119.2624499999999870 40.7435349999999872, -119.2628159999999866 40.7436319999999910, -119.2631789999999796 40.7437380000000147, -119.2635439999999960 40.7438730000000007, -119.2638029999999958 40.7439859999999925, -119.2640609999999981 40.7441149999999936, -119.2643099999999947 40.7442559999999929, -119.2645539999999897 40.7444149999999823, -119.2647999999999939 40.7445880000000002, -119.2650449999999722 40.7447680000000076, -119.2652939999999973 40.7449499999999887, -119.2655479999999955 40.7451309999999935, -119.2658029999999911 40.7453129999999959, -119.2660589999999843 40.7454959999999744, -119.2663129999999967 40.7456769999999864, -119.2665659999999832 40.7458559999999821, -119.2668139999999681 40.7460340000000016, -119.2670559999999824 40.7462080000000029, -119.2672629999999856 40.7463529999999921, -119.2674470000000042 40.7464799999999769, -119.2676269999999761 40.7466149999999772, -119.2678079999999881 40.7467669999999913, -119.2679829999999868 40.7469289999999944, -119.2681509999999605 40.7470989999999844, -119.2683019999999772 40.7472769999999755, -119.2684419999999648 40.7474580000000088, -119.2685749999999842 40.7476399999999899, -119.2687020000000047 40.7478229999999968, -119.2688300000000083 40.7480120000000028, -119.2689639999999685 40.7482019999999991, -119.2690940000000097 40.7483859999999964, -119.2692270000000008 40.7485709999999770, -119.2693529999999811 40.7487489999999895, -119.2694810000000132 40.7489279999999923, -119.2696529999999768 40.7491750000000010, -119.2698239999999856 40.7494259999999997, -119.2699640000000016 40.7496129999999894, -119.2701749999999805 40.7498489999999975, -119.2704269999999838 40.7500659999999897, -119.2707129999999722 40.7502629999999755, -119.2709389999999985 40.7504019999999869, -119.2711740000000020 40.7505369999999942, -119.2714199999999920 40.7506669999999929, -119.2716609999999946 40.7507929999999874, -119.2718949999999865 40.7509110000000021, -119.2721300000000042 40.7510140000000050, -119.2723629999999986 40.7511009999999771, -119.2725910000000198 40.7511789999999863, -119.2728049999999911 40.7512469999999993, -119.2729989999999987 40.7513099999999895, -119.2731720000000024 40.7513719999999964, -119.2733179999999891 40.7514279999999900, -119.2734370000000013 40.7514829999999932, -119.2735639999999933 40.7515500000000017, -119.2737129999999723 40.7516200000000026, -119.2738939999999985 40.7516879999999873, -119.2741029999999682 40.7517539999999912, -119.2744049999999874 40.7518349999999856, -119.2747079999999897 40.7519049999999865, -119.2750049999999931 40.7519649999999842, -119.2751910000000208 40.7520140000000097, -119.2755449999999939 40.7521349999999956, -119.2757179999999551 40.7522019999999898, -119.2759850000000057 40.7523039999999739, -119.2762919999999980 40.7524149999999921, -119.2765030000000053 40.7524879999999996, -119.2767099999999942 40.7525709999999961, -119.2769020000000069 40.7526609999999962, -119.2770389999999878 40.7527860000000004, -119.2771249999999981 40.7529499999999985, -119.2771819999999963 40.7531189999999768, -119.2772409999999752 40.7532679999999701, -119.2772899999999936 40.7534040000000104, -119.2773260000000022 40.7535139999999814, -119.2773529999999909 40.7536259999999899)"
entrance_road.tags = 'road'
entrance_road.save()

# FENCE 	
dist_to_fence=7300

## top of pentagon aligned with 6'. make poly?
fence = Infrastructure.objects.create(year=year)
fence.name = 'fence'
polystring = "LINESTRING("
twelve = time2radial(0,0)
polystring = polystring + ret_point(clat,clon,dist_to_fence,twelve) + ","
polystring = polystring + ret_point(clat,clon,dist_to_fence,twelve+72) + ","
polystring = polystring + ret_point(clat,clon,dist_to_fence,twelve+144) + ","
polystring = polystring + ret_point(clat,clon,dist_to_fence,twelve+216) + ","
polystring = polystring + ret_point(clat,clon,dist_to_fence,twelve+288) + ","
polystring = polystring + ret_point(clat,clon,dist_to_fence,twelve+360)
polystring = polystring + ")"
fence.location_line = polystring
fence.tags = 'fence'
fence.save()

# PORTAPOTTY

## halfway between circular streets, offset from radial street
def potty_point(year, street1, street2, time):
  if time < 6:
    time = time - .03
  else:
    time = time + .03
  pt1 = geocode(year.year, math.floor(time), math.modf(time)[0] * 60, street1)
  pt2 = geocode(year.year, math.floor(time), math.modf(time)[0] * 60, street2)
  return str((pt1.x + pt2.x)/2) + ' ' + str((pt1.y + pt2.y)/2)
  
def create_potty(year,street1,street2,time):
	potty = Infrastructure.objects.create(year=year)
	potty.name = "toilets " + street1[0] + "/" + street2[0] + ":" + str(time)
	potty.location_point = "POINT(" + potty_point(year, street1, street2, time) + ")"
	potty.tags = 'toilet'
	potty.save()
	
C = CircularStreet.objects.filter(year=year,name__startswith='C')[0].name
D = CircularStreet.objects.filter(year=year,name__startswith='D')[0]
E = CircularStreet.objects.filter(year=year,name__startswith='E').exclude(name__iexact='Esplanade').exclude(name__iexact='Evolution')[0].name
G = CircularStreet.objects.filter(year=year,name__startswith='G')[0]
H = CircularStreet.objects.filter(year=year,name__startswith='H')[0].name
I = CircularStreet.objects.filter(year=year,name__startswith='I')[0].name

## C/D potties and H/I potties
for y in range(5,20):
  x = float(y)/2
  if x not in [3,6,9]:
		create_potty(year,C,D.name,x)
  if x not in [6]:
		create_potty(year,H,I,x)
  if x in [3,9]:
		create_potty(year,D.name,E,x)
  if x in [6]:
		create_potty(year,G.name,H,x)
    
# AIRPORT (ONSITE DETERMINED)!
radial = time2radial(4,35)
tmp = getpoint(clat,clon,dist_to_fence,-radial)
ls = LineString((clon,clat),(tmp.x,tmp.y))
airport_point = fence.location_line.intersection(ls)
airport = Infrastructure.objects.create(year=year)
airport.name = "Airport"
airport.location_point = airport_point
airport.tags = 'airport'
airport.save()

## AIRPORT ROAD
ar1 = geocode(year.year, 5, 0, L.name)
ls = LineString((ar1.x,ar1.y),(airport_point.x,airport_point.y))
airport_road = Infrastructure.objects.create(year=year)
airport_road.name = "Airport Road"
airport_road.location_line = ls
airport_road.tags = 'road'
airport_road.save()

## RUNWAY (HARDCODED!)
airport_runway = Infrastructure.objects.create(year=year)
airport_runway.name = "Runway"
airport_runway.location_line = "LINESTRING(-119.226762656086 40.747326091884,-119.212171439046 40.7499595497597)"
airport_runway.tags = 'runway'
airport_runway.save()

# WALKIN CAMPING
polygon = "POLYGON(("
arc_start = time2radial(2,00)
arc_end = time2radial(5,00)
polygon = polygon + ret_arc(clat,clon,L.distance_from_center,int(arc_start),int(arc_end),1)
polygon = polygon + "," + str(airport.location_point.x) + " " + str(airport.location_point.y) 
polygon = polygon + "," + ret_point(clat,clon,dist_to_fence,twelve+72)
pt = GEOSGeometry("LINESTRING(" + str(clon) + " " + str(clat) + "," + ret_point(clat,clon,dist_to_fence,arc_start) + ")").intersection(fence.location_line)
polygon = polygon + "," + str(pt.x) + " " + str(pt.y)
polygon = polygon + "," + ret_street_point(year, 2, 0, L.name)
polygon = polygon + "))"
walkin_camping = Infrastructure.objects.create(year=year)
walkin_camping.name = "Walk-in Camping Area"
walkin_camping.location_poly = polygon
walkin_camping.tags = 'walkin_camp'
walkin_camping.save()

# PLAZAS

## 3:00 plaza
(pt,plaza_radius) = plaza(year,3,0)

angle_start = int(time2radial(2,55))
angle_end = int(time2radial(3,05))
polystring = "POLYGON(("
polystring = polystring + ret_arc(clat,clon,Esplanade.distance_from_center,angle_start,angle_end,1)
polystring = polystring + "," + str(pt.x) + " " + str(pt.y)
polystring = polystring + "," + ret_point(clat,clon,Esplanade.distance_from_center,angle_start)
polystring = polystring + "))"
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = polystring
plaza.tags = 'plaza'
plaza.save()

plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = "POLYGON((" + ret_arc(pt.y,pt.x,plaza_radius,0,360,1) + "))"
plaza.tags = 'plaza'
plaza.save()

## 9:00 plaza
(pt,plaza_radius) = plaza(year,9,0)

angle_start = int(time2radial(8,55))
angle_end = int(time2radial(9,05))
polystring = "POLYGON(("
polystring = polystring + ret_arc(clat,clon,Esplanade.distance_from_center,angle_start,angle_end,1)
polystring = polystring + "," + str(pt.x) + " " + str(pt.y)
polystring = polystring + "," + ret_point(clat,clon,Esplanade.distance_from_center,angle_start)
polystring = polystring + "))"
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = polystring
plaza.tags = 'plaza'
plaza.save()

plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = "POLYGON((" + ret_arc(pt.y,pt.x,plaza_radius,0,360,1) + "))"
plaza.tags = 'plaza'
plaza.save()

## 4:30 plaza
(pt,plaza_radius) = plaza(year,4,30)
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = "POLYGON((" + ret_arc(pt.y,pt.x,plaza_radius,0,360,1) + "))"
plaza.tags = 'plaza'
plaza.save()

angle_start = int(time2radial(4,25))
angle_end = int(time2radial(4,35))
polystring = "POLYGON(("
polystring = polystring + ret_arc(clat,clon,Esplanade.distance_from_center,angle_start,angle_end,1)
pt = geocode(yea.year, 4, 30, A.name)
polystring = polystring + "," + str(pt.x) + " " + str(pt.y)
polystring = polystring + "," + ret_point(clat,clon,Esplanade.distance_from_center,angle_start)
polystring = polystring + "))"
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = polystring
plaza.tags = 'plaza'
plaza.save()

## 7:30 plaza
(pt,plaza_radius) = plaza(year,7,30)
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = "POLYGON((" + ret_arc(pt.y,pt.x,plaza_radius,0,360,1) + "))"
plaza.tags = 'plaza'
plaza.save()

angle_start = int(time2radial(7,25))
angle_end = int(time2radial(7,35))
polystring = "POLYGON(("
polystring = polystring + ret_arc(clat,clon,Esplanade.distance_from_center,angle_start,angle_end,1)
pt = geocode(year.year, 7, 30, A.name)
polystring = polystring + "," + str(pt.x) + " " + str(pt.y)
polystring = polystring + "," + ret_point(clat,clon,Esplanade.distance_from_center,angle_start)
polystring = polystring + "))"
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = polystring
plaza.tags = 'plaza'
plaza.save()

## center camp
angle_start = int(time2radial(5,30))
angle_end = int(time2radial(6,30))
polystring = "POLYGON(("
polystring = polystring + ret_arc(cc.y,cc.x,dist_outer_ring,angle_start,angle_end,1)
polystring = polystring + "," + str(cc.x) + " " + str(cc.y)
polystring = polystring + "," + ret_point(cc.y,cc.x,dist_outer_ring,angle_start)
polystring = polystring + "))"
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = polystring
plaza.tags = 'plaza'
plaza.save()

polystring = "POLYGON((" + ret_arc(cc.y,cc.x,dist_inner_ring,0,360,1) + "))"
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = polystring
plaza.tags = 'plaza'
plaza.save()

## playa
fire_circle_radius = 300
polystring = "POLYGON((" + ret_arc(clat,clon,fire_circle_radius,0,360,1) + "))"
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = polystring
plaza.tags = 'plaza'
plaza.save()

temple_radius = 100 #determined ONSITE
pt = geocode(year.year,0,0,'Esplanade')
polystring = "POLYGON((" + ret_arc(pt.y,pt.x,temple_radius,0,360,1) + "))"
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = polystring
plaza.tags = 'plaza'
plaza.save()

# DPW/Fire
dpw_radius = 200 #determined ONSITE

pt = geocode(year.year, 5, 30, L.name)
angle = int(time2radial(5,30))
pt2 = getpoint(clat,clon,L.distance_from_center + 550,-angle)
ls = LineString((pt.x,pt.y),(pt2.x,pt2.y))
dpw_road = Infrastructure.objects.create(year=year)
dpw_road.name = ""
dpw_road.location_line = ls
dpw_road.tags = 'road'
dpw_road.save()

polystring = "POLYGON((" + ret_arc(pt2.y,pt2.x,dpw_radius,0,360,1) + "))"
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = polystring
plaza.tags = 'plaza'
plaza.save()

pt = geocode(year.year, 6, 30, L.name)
angle = int(time2radial(6,30))
pt2 = getpoint(clat,clon,L.distance_from_center + 550,-angle)
ls = LineString((pt.x,pt.y),(pt2.x,pt2.y))
dpw_road = Infrastructure.objects.create(year=year)
dpw_road.name = ""
dpw_road.location_line = ls
dpw_road.tags = 'road'
dpw_road.save()

polystring = "POLYGON((" + ret_arc(pt2.y,pt2.x,dpw_radius,0,360,1) + "))"
plaza = Infrastructure.objects.create(year=year)
plaza.name = "Plaza"
plaza.location_poly = polystring
plaza.tags = 'plaza'
plaza.save()

# Fire barrells
fire_barrell_offset = 50
for x in range(2,10):
	fire = Infrastructure.objects.create(year=year)
	fire.name = "Fire Barrell"
	fire.location_point =	"POINT(" + ret_point(clat,clon,Esplanade.distance_from_center-fire_barrell_offset,time2radial(x,30)) + ")"
	fire.tags = 'firebarrell'
	fire.save()

J = CircularStreet.objects.filter(year=year,name__startswith='J')[0]
for x in (A,D,G,J):
	fire = Infrastructure.objects.create(year=year)
	fire.name = "Fire Barrell"
	fire.location_point =	"POINT(" + ret_point(clat,clon,x.distance_from_center,time2radial(1,57)) + ")"
	fire.tags = 'firebarrell'
	fire.save()
	
	fire = Infrastructure.objects.create(year=year)
	fire.name = "Fire Barrell"
	fire.location_point =	"POINT(" + ret_point(clat,clon,x.distance_from_center,time2radial(10,03)) + ")"
	fire.tags = 'firebarrell'
	fire.save()

closure = Infrastructure.objects.create(year=year)
closure.name = "BLM Closure Zone"
closure.location_poly = "POLYGON((-119.19533 40.79548, -119.19536 40.78098, -119.19536 40.78098, -119.19325 40.78098, -119.19324 40.76905, -119.18678 40.76917, -119.18668 40.76226, -119.18668 40.76097, -119.20293 40.75340, -119.21491 40.74742, -119.22833 40.74048, -119.24181 40.74050, -119.24995 40.74044, -119.26887 40.74043, -119.26887 40.74042, -119.27837 40.74049, -119.27826 40.74775, -119.27822 40.74775, -119.27821 40.74775, -119.27801 40.75391, -119.27801 40.75391, -119.27663 40.75421, -119.27606 40.75434, -119.27590 40.75437, -119.27483 40.75460, -119.27477 40.75462, -119.27474 40.75462, -119.27350 40.75489, -119.27214 40.75519, -119.27201 40.75522, -119.27169 40.75531, -119.27055 40.75563, -119.27036 40.75572, -119.27030 40.75574, -119.27014 40.75579, -119.26990 40.75592, -119.26976 40.75599, -119.26961 40.75608, -119.26866 40.75659, -119.26846 40.75670, -119.26814 40.75691, -119.26791 40.75706, -119.26764 40.75723, -119.26657 40.75792, -119.26512 40.75886, -119.26489 40.75905, -119.26387 40.75989, -119.26294 40.76080, -119.26192 40.76180, -119.26164 40.76223, -119.26162 40.76223, -119.26133 40.76267, -119.26133 40.76271, -119.26132 40.76351, -119.26132 40.76375, -119.26134 40.76389, -119.26177 40.76676, -119.26252 40.77089, -119.26299 40.77343, -119.26315 40.77400, -119.26338 40.77476, -119.26377 40.77581, -119.26379 40.77587, -119.26386 40.77606, -119.26468 40.77707, -119.26867 40.78074, -119.26867 40.78146, -119.26137 40.78141, -119.26148 40.79214, -119.25676 40.79220, -119.25682 40.79578, -119.24737 40.79574, -119.23315 40.79567, -119.22867 40.79565, -119.22865 40.79565, -119.21424 40.79558, -119.20478 40.79553, -119.19533 40.79548))"
closure.tags = 'closure'
closure.save()

gate = Infrastructure.objects.create(year=year)
gate.name= "Gate"
gate.location_point = "POINT(-119.246850 40.746943)"
gate.tags = "gate"
gate.save()
