library(Rfa)
library(raster)
library(harpIO)
library(sp)
library(rgdal)
library(rgeos)
library(sf)
library(readr)


source("functions.R")
# - easy leading zeros
lz=function(x,n=2) formatC(x,flag="0",format="d",width=n)



# READ BLEG STATIONS 
stat= read.table("stat.txt"  , header = TRUE , sep=",")
slon=stat$lon 
slat=stat$lat 
name=stat$name 


# COLOR PALETTE 
col_pcp   =c("#ffffff","#edddd3","#dcbfb5","#c3a197","#beeff9","#a3cff8",
             "#6b9ef2","#5177ed","#31a31b","#52d643","#87f977","#bafdac",
             "#fbfeae","#f5c54a","#f16723","#f02820","#9b1111","#a400b8","#e606fd")



#breaks_pcp=c(0,0.2,0.5,1,2,3,4,5,7,10,15,20,25,30,35,40,50,65,80,150)
#col_pcp   =c("#ffffff","#edddd3","#dcbfb5","#c3a197","#beeff9","#a3cff8",
#             "#6b9ef2","#5177ed","#31a31b","#52d643","#87f977","#bafdac",
#             "#fbfeae","#f5c54a","#f16723")
#breaks_pcp=c(0,0.5,1,1.5,2.5,3,3.5,4,5,6,7,9,10,12,13,15)

# DATA DESCRIPTION 
period="SUM"
exp ="control"
model="AR13"
year=2021
month=7
day=12
starth=12
basedir="/home/micro/Bureau/ex-R/exps"
id=""

files_ref   =paste0(basedir,"/",exp,"/",year ,lz(month),lz(day),lz(starth),"/","PF",model,"be13b_l+",lz(seq(1,12,1),4))



# GET THE PCP FIELDS 
pcp=lapply(files_ref, function(fa) FAdec(fa,"SURFACCPLUIE") )

pcp_1h=list()
first=TRUE
for(i in seq_along(pcp)){
  print(i)
  if (first){
    pcp_1h[[i]]=pcp[[i]]
    first=FALSE
  } else {
    pcp_1h[[i]]=pcp[[i]]-pcp[[i-1]]
    pcp_1h[[i]][pcp_1h[[i]]<0]=0
  }
}


# GET THE DATES ( UNIX FORMAT )
validdates=lapply(files_ref ,function(fa) attr(FAopen(fa),"time")$validdate)
dates=c()
for (i in seq_along(validdates)){
epoch <- as.numeric(validdates[[i]])
dates =c(dates , epoch)  
}



#RADAR
library(rhdf5)
library(belgium)
radarbase="/home/micro/Bureau/ex-R/rad"
#validdates=lapply(files_ref[1]  ,function(fa) attr(FAopen(fa),"time")$validdate)

radar_1h=list()

for (i in seq_along(validdates)){
  date=validdates[[i]]
  print(date)
  file=paste0(radarbase ,"/",
              format.Date(date,"%Y"),
              format.Date(date,"%m"),
              format.Date(date,"%d"),
              "00" , "/", format.Date(date,"%Y%m%d%H%M%S"),".rad.bhbjbwdnfa.comp.acrr.qpe2_1h.hdf" )

  pcp=h5read(file,name='dataset1/data1/data')
  # hdf5 files have a different row/column dominance, so we need to transform the matrix given
  # by h5read
  # at the sametime we create the geofield by providing the qpe domain, which is included in the 
  # belgium library
  radar_1h[[i]]=as.geofield(t(apply(pcp  ,1,rev)),domain=domain_list$qpe)
}


# CUMULATIVE SUM OF RADAR FIELDS 
for ( i in 1:(length(radar_1h)-1))  {
radar_1h[[i+1]] = radar_1h[[i]]  +  radar_1h[[i+1]]
}

lats = c(51.0702, 49.9143, 51.1917, 50.1283 )
lons = c(5.4054, 5.5056 ,3.0642, 3.81181   )
names= c("Helchteren", "Wideumont","Jabbeke", "Avesnes")
flevs= c(  59, 59 , 59, 59)

#iview( radar_1h[[12]] , levels=breaks_pcp,title="Radar QPE composite\n20210714 12:00" ,   col=col_pcp ,legend=T )
#obsplot(lons ,lats ,flevs  ,breaks=2,pretty=TRUE,legend.pos=NULL,
#        add=TRUE,domain=newdom ,col=irainbow,  cex = 1.3)
#q()

#ras =   geofield_to_raster(   radar_1h[[15]])
#writeRaster(  ras , "radar_obs_202107141500.tiff", overwrite=TRUE     )
#q()


# CONVERT 
#for (i in seq_along(pcp_1h ))  {

# print( c("write data to geotiff" , lz(i )   )) 
# ras = geofield_to_raster( pcp[[i]] )
# tifname=  paste( exp, "_",year ,lz(month),lz(day),lz(starth), "_", lz(i) , ".tiff", sep="")
# writeRaster(ras , tifname , overwrite=TRUE )
#}
#iview(pcp_1h[[24]]     , levels=breaks_pcp, col=col_pcp, legend=TRUE  ) 
#iview(radar_1h[[6]], levels=breaks_pcp, col=col_pcp, legend=TRUE  )

# READ SHAPE FILE  
gbr     = shapefile("eu_shp/GBR_adm/GBR_adm0.shp")
fra     = shapefile("eu_shp/FRA_adm/FRA_adm0.shp")
ger     = shapefile("eu_shp/DEU_adm/DEU_adm0.shp")
nld     = shapefile("eu_shp/NLD_adm/NLD_adm0.shp")
blg     = shapefile("blg_shp/BEL_adm0.shp")
vsd     = shapefile("vesdre_shp/Vesdre_catchment.shp")




# READ REPROJECTED RASTER 
ras     = raster ("../tiff/radar_2021071600_24.tiff" )
ras_res = disaggregate( ras  , fact = 3 , method = "bilinear" )


#plot( ras  , col=col_pcp ,zlim=c(0, 120) , ,main = "Radar QPE accumulated precipitation \n 20210714 00:00 to 18:00 UTC", legend=TRUE  , xlab="Longitude", ylab="Latitude" )

#plot( ger , border="black" , xlim=c(-1 , 10) , ylim =c(46, 55) , add=TRUE )
#plot( nld , border="black", add=TRUE )
#plot( blg , border="black", add=TRUE )
#plot( gbr , border="black", add=TRUE )
#plot( fra , border="black", add=TRUE )
#plot( vsd , border="black", lwd =1.5 , add=TRUE )
#q()

# CROP AND CLIP
ras_crop =  crop  (ras_res   , extent(vsd))
ras_mask =  mask  (ras_crop  ,       vsd)
plot(ras_mask  ,  col=col_pcp ,main = "Radar QPE accumulated precipitation \n 20210714 00:00 to 18:00 UTC \n Vesdre catchment", legend=TRUE  , xlab="Longitude", ylab="Latitude" , zlim=c (0,120))   #xlim=c(5.2, 6.5) ,ylim=c(50.399, 50.75)  )
plot( vsd , border="black", lwd =1.5 , add=TRUE )
plot( blg , border="black", lwd =1.8 , add=TRUE )
plot( ger , border="black", lwd =1.8 , add=TRUE )
q()

# CROP AND CLIP 
#ras_crop =  crop  (ras_res   , extent(vsd))
ras_mask =  mask  (ras_crop  ,       vsd)


# PLOT TO CHECK 
plot(ras_mask  ,  col=col_pcp ,main = "24h accumulated precipitation \n 20210714 23:00 \n Vesdre catchment", legend=TRUE  , xlab="Longitude", ylab="Latitude" , zlim=c (0,60))
plot(vsd , border="blue"  , lwd=1.5  , add=TRUE )
plot(blg , border="black"  , lwd=1.8  , add=TRUE )
   
q()
