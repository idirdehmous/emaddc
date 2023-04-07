import numpy as np
import sys
import matplotlib.pyplot as plt   
from mpl_toolkits.basemap import Basemap


"""PROLOGUE 
   -PYTHON SCRIPT : READS FILE WITH LATLON VALUES 
    CONVERTS GEOPOINTS TO DENSITY BINS 
    
@__: IDIR DEHMOUS  
@__: RMI  
C__: 01/04/2023 
"""



plt.rc    ('text'  , usetex=False)
plt.rcParams['axes.facecolor']='w'
plt.rcParams['axes.linewidth'] = 0.5
plt.rcParams['font.serif'] = "Times Roman"
plt.rcParams['ytick.labelsize']=12
plt.rcParams['xtick.labelsize']=12
plt.rcParams['axes.titlesize' ]=12
plt.rcParams['axes.labelsize' ]=12
plt.rcParams['legend.fontsize']=12
plt.rcParams['legend.loc']     ="best"
plt.rcParams['font.weight']    = 'normal'  

avg_list=[]
def ReadFile(infile  ):
    lat=[]
    lon=[]
    flev=[]
    press=[]
    filepath=infile
    file=open(filepath , "r")
    lines=file.readlines()
    for line in lines:
        l=line.rstrip().split()
#        if float(l[1])  >= -2 and float(l[1]) <=11. :
        lat.append(float(l[5]) )
        lon.append(float(l[6]) )
        press.append(float(l[7])/100. )
    print( len(set(lat)))
    return   lat , lon , press  


fig, ax = plt.subplots(1, 1, figsize=(8,8))


# READ FILE

data="modes"
period="SUM"
yyyy="2021"
mm="07"
win_date="2022010100 2022013121"
sum_date="2021071000 2021081021"
path="/mnt/HDS_ALD_TEAM/ALD_TEAM/idehmous/testruns/EMADDC/"+period+"/ODB/data/total/control/"+data+"/"
#path="/mnt/HDS_ALD_TEAM/ALD_TEAM/idehmous/testruns/EMADDC/cov/vert/"+data+"/"+period+"/"

ndays=0
nbins=60
hh=np.zeros((nbins , nbins ))
hh_list=[]
xx=[]  ; yy=[]
lats=[]; lons=[] 
for d in  range(10,11):
    dd="{:02}".format( d )
    print( dd )   
    infile= path+"uv/uv_file_"+yyyy+mm+str(dd)

    lat , lon , press  =ReadFile(infile  )
    lats.append(lat)  ;  lons.append(lon)  

max_val=None
if period == "win":
   plt.title("EMADDC vertical coverage (Daily Average )\n "+win_date +"( Max value = "+str(max_val)+" )")
else:
   plt.title("EMADDC vertical coverage (Daily Average )\n "+sum_date +"( Max value = "+str(max_val)+" )")

nx, ny = 10, 3

# compute appropriate bins to histogram the data into
lon_bins = np.linspace(min(lons), max(lons), nx+1)
lat_bins = np.linspace(min(lats), max(lats), ny+1)

# Histogram the lats and lons to produce an array of frequencies in each box.
# Because histogram2d does not follow the cartesian convention 
# (as documented in the numpy.histogram2d docs)
# we need to provide lats and lons rather than lons and lats
#density, _, _ = np.histogram2d(lats, lons, [lat_bins, lon_bins])
np.histogram2d(lats, lons, [lat_bins, lon_bins] )

# Turn the lon/lat bins into 2 dimensional arrays ready 
# for conversion into projected coordinates
lon_bins_2d, lat_bins_2d = np.meshgrid(lon_bins, lat_bins)

# convert the xs and ys to map coordinates
xs, ys = m(lon_bins_2d, lat_bins_2d)

plt.pcolormesh(xs, ys, density)
plt.colorbar(orientation='horizontal')

# overlay the scatter points to see that the density 
# is working as expected
#plt.scatter(*m(lons, lats))

plt.show()



quit()

