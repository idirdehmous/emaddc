library(Rfa)
library(raster)
library(harpIO)
library(sp)
library(rgdal)
library(rgeos)
library(sf)

args = commandArgs(trailingOnly=TRUE)
if (length(args) !=2 ) {
  stop("Arguments missing : USAGE : ./getForecast.R  exp  day ", call.=FALSE)
} else  if  ( length(args)==2) {
exp  =args[1]
DD   =args[2]
}




col_pcp=c("#ffffff","#edddd3","#dcbfb5","#c3a197","#beeff9","#a3cff8",
           "#6b9ef2","#5177ed","#31a31b","#52d643","#87f977","#bafdac",
           "#fbfeae","#f5c54a","#f16723","#f02820","#9b1111","#a400b8","#e606fd")
breaks_pcp=c(0,0.2,0.5,1,2,3,4,5,7,10,15,20,25,30,35,40,50,65,80,150)


#library(belgium )
source("functions.R")
# - easy leading zeros
lz=function(x,n=2) formatC(x,flag="0",format="d",width=n)

period="SUM"
exp = exp 
model="AR13"
year=2021
month=7
day=DD
starth=12
basedir="/home/micro/Bureau/ex-R/exps"
id=""

files_ref   =paste0(basedir,"/",exp,"/",year ,lz(month),lz(day),lz(starth),"/","PF",model,"be13b_l+",lz(seq(1,24,1),4))



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


# CONVERT  RADAR PCP 
#for (i in seq_along(radar_1h ))  {
# print( c("write radar data to geotiff" , lz(i )   ))

#rad_reg=regrid(radar_1h[[i]], pcp_1h[[i]])
# ras = geofield_to_raster( radar_1h[[i]] )
# tifname=  paste( "radar_",year ,lz(month),lz(day),lz(starth), "_", lz(i) , ".tiff", sep="")
# writeRaster(ras , tifname , overwrite=TRUE )
#}
#print( "Done ....!" )
#q()

# CONVERT MODEL PCP
for (i in seq_along(pcp_1h ))  {
 print( c("write model data to geotiff , experiment =",  exp  , lz(i )   ))
 ras = geofield_to_raster( pcp_1h[[i]] )
 tifname=  paste( exp, "_",year ,lz(month),lz(day),lz(starth), "_", lz(i) , ".tiff", sep="")
 writeRaster(ras , tifname , overwrite=TRUE )
}

print( "Done ....!")


q()

