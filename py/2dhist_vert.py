import numpy as np
import sys
import matplotlib.pyplot as plt   
from mpl_toolkits.basemap import Basemap

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


# 2D Histogram
fig, ax = plt.subplots(1, 1, figsize=(8,8))


ndays=0
nbins=60
hh=np.zeros((nbins , nbins ))
hh_list=[]
xx=[]  ; yy=[]
for d in  range(10,11):
    dd="{:02}".format( d )
    print( dd )   
    infile= path+"t/t_daily_"+yyyy+mm+str(dd)

    lat , lon , press  =ReadFile(infile  )
    avg_list.append(set(lat)  )
    heatmap, xedges, yedges , img  =ax.hist2d( lon , lat , alpha=1., bins=nbins )
    hh_list.append(heatmap)
    hh=np.add( hh , heatmap)
    xx.append(xedges ) 
    yy.append(yedges )
    ndays=ndays+1

s=0
for i in range(len(avg_list)):
    s= s+  len(avg_list[i]    )

max_val= int(max([ i.max()  for i in hh_list ] ))
mean_hh =  hh/ndays
xedge=xx[0]  
yedge=yy[0]

#plt.clf()
if period == "win":
   plt.title("EMADDC vertical coverage (Daily Average )\n "+win_date +"( Max value = "+str(max_val)+" )")
else:
   plt.title("EMADDC vertical coverage (Daily Average )\n "+sum_date +"( Max value = "+str(max_val)+" )")

# 2D Histogram
#fig, ax = plt.subplots(1, 1, figsize=(8,8))
map = Basemap(projection='lcc',lat_0=45,lon_0=5.0 ,lat_1=30, lat_2=40 ,  resolution="l" , 
                          llcrnrlon=-5.,llcrnrlat=40.,urcrnrlon=15.,urcrnrlat=59.) 


map.readshapefile('../shp/ne_10m_admin_0_countries', 'ne_10m_admin_0_countries')
parallels = np.arange(0.,70,5.)
map.drawparallels(parallels,labels=[True,False,False, False ], linewidth=0.1)
meridians = np.arange(-5., 15. , 5.)
map.drawmeridians(meridians,labels=[False,False,False,True] ,  linewidth=0.1)


#plt.imshow(hh.T )
plt.show()
quit()
#cs=plt.pcolormesh( xedge , yedge , mean_hh.T , cmap=plt.cm.gist_heat_r  )

plt.gca().invert_yaxis()
plt.xlabel("Longitude [ Deg ]")
plt.ylabel("Pressure Levels [ Hpa ]")
plt.ylim(1000, 100)
plt.colorbar(cs , label="Number of obs per box")
plt.show()
#plt.savefig(data+"_vert_cov_"+data+"_"+period+".pdf")

# PRINT STAT 
print( "Daily Number of temperature  :" , s/len(avg_list))
quit()


quit()
