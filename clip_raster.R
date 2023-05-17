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
exp   ="radar"
year  =2021
month =7
day   =16
starth=0
tifdir="/home/micro/Bureau/ex-R/tiff"




# READ SHAPE FILE  
blg     = shapefile("blg_shp/BEL_adm1.shp")
vsd     = shapefile("vesdre_shp/Vesdre_catchment.shp")


# READ REPROJECTED RASTER 

for (i in seq( 1, 24 , 1)) {
date=paste( year ,lz(month), lz(day) , lz(starth), sep="" )
filedate=paste( date ,"_" , lz(i) , sep="")

rast_name= paste( tifdir , "/", exp , "/", exp ,"_", filedate, ".tif" , sep=""  )

print( c("Reading raster: " , filedate ) )
ras     = raster ( rast_name  )
ras_res = disaggregate( ras  , fact = 3 , method = "bilinear" )

# CROP WITH VESDRE SHAPE
ras_crop =  crop  (ras_res   , extent(vsd))

# CLIP 
print( c("Clipping file ... !") )
ras_mask =  mask  (ras_crop  ,       vsd)

tifname=paste( exp , "_vesdre_", filedate , ".tif", sep="" )
writeRaster(ras_mask , tifname , overwrite=TRUE )  
}



q()



# CROP AND CLIP 
ras_crop =  crop  (ras_res   , extent(vsd))
ras_mask =  mask  (ras_crop  ,       vsd)

pdf( "10_vesdre.pdf" ) 

# PLOT TO CHECK 
plot(ras_mask  ,main = "24h accumulated precipitation \n 20210715 00:00 \n Vesdre catchment",  col=col_pcp  , legend=TRUE  , xlab="Longitude", ylab="Latitude" , zlim=c(0,13) )
plot(vsd , border="black"  , lwd=1.5  , add=TRUE )

   
q()
#plot( slon ,slat , pch=18, col="blue",xlim=c(5.5,6.5), ylim=c(50.35,50.7) )

# PLOT TO CHECK
plot(ras  ,main =" 24h accumulated Precpitation \n20210715 00:00 \n Vesdre catchement ",  col=col_pcp  , legend=TRUE  , xlab="Longitude", ylab="Latitude", zlim=c(0,145))
#plot(vsd , border="black"  , lwd=1.5  , xlab="Longitude", ylab="Latitude" , add=TRUE ,xlim=c(5.5,6.5), ylim=c(50.35,50.7) )
#text( slon, slat, name , cex=1., pos=4, col="black")



q()
# PLOT BLG SHAPE
#plot(blg, border="black"  , lwd=1.5  , xlab="Longitude", ylab="Latitude" , add=TRUE) 
#plot(world, border="black"  , lwd=1.5  , xlab="Longitude", ylab="Latitude" , xlim=c(-1,12), ylim=c(45,55.6))
# PLOT VESRDE SHAPE
plot(vsd , border="black"  , lwd=1.5  , xlab="Longitude", ylab="Latitude" , add=TRUE ,xlim=c(5.5,6.5), ylim=c(50.35,50.7) )
#plot(vesdr, border="black", lwd= 2 , add=TRUE    )
#axis(side=1 )
#axis(side=2 )
#color.bar(colorRampPalette(col_pcp)(100), -1)
q()

#RADAR
library(rhdf5)
library(belgium)
radarbase="/mnt/HDS_RADAR_EDP/realtime"
#validdates=lapply(files_ref[1]  ,function(fa) attr(FAopen(fa),"time")$validdate)

radar_1h=list()

for (i in seq_along(validdates)){
  date=validdates[[i]]
#  print(date)
  file=paste0(
    radarbase,"/",
    format.Date(date,"%Y"),"/",
    format.Date(date,"%m"),"/",
    format.Date(date,"%d"),"/",
    "bhbjbwdnfa/comp/acrr/qpe2_1h/hdf/",
    format.Date(date,"%Y%m%d%H%M%S"),
    ".rad.bhbjbwdnfa.comp.acrr.qpe2_1h.hdf"
  )
 
  pcp=h5read(file,name='dataset1/data1/data')
  # hdf5 files have a different row/column dominance, so we need to transform the matrix given
  # by h5read
  # at the sametime we create the geofield by providing the qpe domain, which is included in the 
  # belgium library
  radar_1h[[i]]=as.geofield(t(apply(pcp_1h[[1]] ,1,rev)),domain=domain_list$be13_l)
}

q()
# REGRID 
pcp_reg=regrid(pcp_1h[[i]], radar_1h[[i]])


# NETCDF OUTFILE 
ncfname=paste("ar13_",year ,lz(month),lz(day),lz(starth),"_native_1h.nc", sep="")

  # META DATA 
nlon  <- as.array(seq(-0,-731900,-1300.))
nlat  <- as.array(seq(0 ,731900 ,1300. ))
times <- as.array(dates)  
ntime <- length( times )

# DIMENSIONS  
londim   <- ncdim_def("y","m"  , as.double(nlon)) 
latdim   <- ncdim_def("x","m"  , as.double(nlat))

timedim  <- ncdim_def("time","seconds since 1970-01-01T00:00:00Z",as.double(times))
dimnchar <- ncdim_def("nchar", "", 1:16, create_dimvar=FALSE )
andim    <- ncdim_def("analysis_time","seconds since 1970-01-01T00:00:00Z",as.double(times[1]))

fillvalue <- 1e32

latname="lat"
lonname="lon"
#varname="precipitation"
lat_def =ncvar_def("lat","degrees_north"   , list(latdim,londim)         ,fillvalue,latname ,prec="single")
lon_def =ncvar_def("lon","degrees_east"    , list(latdim,londim)         ,fillvalue,lonname ,prec="single")
#x_def   =ncvar_def( "x" , "" ,  londim )
#y_def   =ncvar_def ("y" , "",   latdim )
temp_def =ncvar_def("temperature",     "K"   , list(latdim,londim,timedim) ,fillvalue,varname ,prec="single")
rhum_def =ncvar_def("relative_humidity","%"  , list(latdim,londim,timedim) ,fillvalue,varname ,prec="single") 
u_def    =ncvar_def("u_component"      ,"m/s", list(latdim,londim,timedim) ,fillvalue,varname ,prec="single")
v_def    =ncvar_def("v_component"      ,"m/s", list(latdim,londim,timedim) ,fillvalue,varname ,prec="single")
mslp_def =ncvar_def("mslp"             ,"Pa" , list(latdim,londim,timedim) ,fillvalue,varname ,prec="single")

proj_def=ncvar_def("Lambert_Conformal", "",dimnchar , prec="char")
an_def  =ncvar_def("analysis_time","", NULL)# list(andim) ,fillvalue,"analysis_t" ,prec="single")

# PUT VAR DIM 
ncout <- nc_create(ncfname,list( lon_def , lat_def ,pcp_def,  proj_def ) ,force_v4=TRUE)

ncvar_put(ncout,lat_def, as.double(yy))
ncvar_put(ncout,lon_def, as.double(xx))

pcp_array <- array(unlist(pcp_1h), c(ntime, ny , nx ))

ncvar_put(ncout,pcp_def,  pcp_array  )


# LAT LON ATTRIBUTES
ncatt_put(ncout,"lat","long_name","latitude")
ncatt_put(ncout,"lon","long_name","longitude")



# x, y  ATTRIBUTES 
ncatt_put(ncout ,"x","long_name","projection_x_coordinate") ; ncatt_put(ncout ,"y","long_name","projection_y_coordinate")
ncatt_put(ncout ,"x","type","uniform")                      ; ncatt_put(ncout ,"y","type","uniform")
ncatt_put(ncout ,"x","axis","X")                            ; ncatt_put(ncout ,"y","axis","Y")
ncatt_put(ncout ,"x","valid_min" ,0. )                      ; ncatt_put(ncout ,"y","valid_min" ,-731900. )
ncatt_put(ncout ,"x","valid_max",731900. )                  ; ncatt_put(ncout ,"y","valid_max",-0. )
ncatt_put(ncout ,"x","spacing",1300. )                       ; ncatt_put(ncout ,"y","spacing",1300. )
# TIME ATTRIBUTES
ncatt_put(ncout,"time","calendar","standard")
ncatt_put(ncout,"time","standard_name","time")                     
ncatt_put(ncout,"time","axis","T")                           
# PRECIP ATTRIBUTES 
ncatt_put(ncout,"precipitation","units"    ,"kg m-2" )
ncatt_put(ncout,"precipitation","long_name"    ,"Accumulation forecast")
ncatt_put(ncout,"precipitation","coordinates"  ,"lat lon")
ncatt_put(ncout,"precipitation","standard_name","precipitation_amount")
# PROJECTION ATTRIB 
ncatt_put(ncout,"Lambert_Conformal","grid_mapping_name","lambert_conformal_conic")
ncatt_put(ncout,"Lambert_Conformal","longitude_of_central_meridian","4.55000000000001")
ncatt_put(ncout,"Lambert_Conformal","latitude_of_projection_origin","50.8")
ncatt_put(ncout,"Lambert_Conformal","standard_parallel","50.8")
ncatt_put(ncout,"Lambert_Conformal","false_easting","365950.")
ncatt_put(ncout,"Lambert_Conformal","false_northing","365950.000000001")


gvars=c("interpolation_method","proj4string","reference_longitude", "reference_latitude","Conventions","creation_date","history","NCO" )

gvals=c( "nearest_neighbour",
         "+proj=lcc +lon_0=4.55 +lat_1=50.8 +lat_2=50.8 +a=6371229 +es=0 +lat_0=50.8 +x_0=365950 +y_0=-365950.000000001",
         "-1.04076249768297",
         "53.9648250227956" ,
         "CF-1.7",
         "2021-10-26T11:40:27Z",
         "Tue Oct 26 14:41:10 2021: ncks -L 5 /scratch/ledecruz/ao13_2021071400_native_1h_clipped.nc /scratch/ledecruz/ar13_2021071400_native_1h_clipped_compressed.nc\nTue Oct 26 13:43:33 2021: ncks -F -d time,25,48 ao13_2021071400_native_1h.nc ar13_2021071400_native_1h_clipped.nc" ,"netCDF Operators version 4.7.9 (Homepage = http://nco.sf.net, Code = http://github.com/nco/nco)")

for (i in seq_along( gvars)) {
ncatt_put( ncout, 0, gvars[i],gvals[i], prec="text" ) 

}
nc_close(ncout)
q()
