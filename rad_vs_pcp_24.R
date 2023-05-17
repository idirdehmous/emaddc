library(Rfa)
#library(harpSpatial)
#library(scales)
library(raster)
source("functions.R")

# - easy leading zeros
lz=function(x,n=2) formatC(x,flag="0",format="d",width=n)

# - Precipitation 
col_pcp=c("#ffffff","#edddd3","#dcbfb5","#c3a197","#beeff9","#a3cff8",
           "#6b9ef2","#5177ed","#31a31b","#52d643","#87f977","#bafdac",
           "#fbfeae","#f5c54a","#f16723","#f02820","#9b1111","#a400b8","#e606fd")
breaks_pcp=c(0,0.2,0.5,1,2,3,4,5,7,10,15,20,25,30,35,40,50,65,80,150)



fdate=function(date){
  format.Date(date,"%Y-%m-%d %H:%M UTC")
}

# MODEL 
period="SUM"
ref ="CONTROL"
xp1 ="SCNR01"
xp2 ="SCNR02"
xp3 ="SCNR03"
xp4 ="SCNR04"


model="AR13"
year=2021
month=7
day=14
starth=0
basedir="/mnt/HDS_ALD_TEAM/ALD_TEAM/idehmous/testruns/EMADDC/fpos"
#basedir="/home/idehmous/Desktop/emaddc/case/data/alaro40"
id=""
#PFAO40arch00+0000
#files_ref  =paste0(basedir,"/",period,"/",ref,"/",year ,lz(month),lz(day),lz(starth),"/","PF",model,"be13b_l+",lz(seq(1,24,1),4))

# ALARO 
#files_ref  =paste0(basedir,"/","PFAO40arch00+",lz(seq(6,30,6),4))
step1 =1
step2 =18
files_ref  =paste0(basedir,"/",period,"/",ref,"/",year ,lz(month),lz(day),lz(starth),"/","PF",model,"be13b_l+",lz(seq(1,step2,1),4))
files_xp1  =paste0(basedir,"/",period,"/",xp1,"/",year ,lz(month),lz(day),lz(starth),"/","PF",model,"be13b_l+",lz(seq(1,step2,1),4))
files_xp2  =paste0(basedir,"/",period,"/",xp2,"/",year ,lz(month),lz(day),lz(starth),"/","PF",model,"be13b_l+",lz(seq(1,step2,1),4))
files_xp3  =paste0(basedir,"/",period,"/",xp3,"/",year ,lz(month),lz(day),lz(starth),"/","PF",model,"be13b_l+",lz(seq(1,step2,1),4))
files_xp4  =paste0(basedir,"/",period,"/",xp4,"/",year ,lz(month),lz(day),lz(starth),"/","PF",model,"be13b_l+",lz(seq(1,step2,1),4))

validdates=lapply(files_ref ,function(fa) attr(FAopen(fa),"time")$validdate)


GetPcp  = function ( files ) {
pcp=lapply(files,function(fa) FAdec(fa,"SURFACCPLUIE"))
pcp_1h=list()
first=TRUE
for(i in seq_along(pcp)){
  if (first){
    pcp_1h[[i]]=pcp[[i]]
    first=FALSE
  } else {
    pcp_1h[[i]]=pcp[[i]]-pcp[[i-1]]
    pcp_1h[[i]][pcp_1h[[i]]<0]=0
  }
}

return ( pcp ) 
}


#RADAR
library(rhdf5)
library(belgium)
radarbase="/mnt/HDS_RADAR_EDP/realtime"
validdates=lapply(files_ref ,function(fa) attr(FAopen(fa),"time")$validdate)
radar_1h  =list()
rad_fields=list()  # LIST TO CONTAIN ALL RADAR GEOFIELDS 

for (i in seq_along(validdates)){
  date=validdates[[i]]
  print( validdates [[i]]   )
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
  radar_1h[[i]]=as.geofield(t(apply(pcp,1,rev)),domain=domain_list$qpe)
}

# CUMULATIVE SUM OF RADAR FIELDS 
for ( i in 1:(length(radar_1h)-1))  {
radar_1h[[i+1]] = radar_1h[[i]]  +  radar_1h[[i+1]]
}

lats = c(51.0702, 49.9143, 51.1917, 50.1283 )
lons = c(5.4054, 5.5056 ,3.0642, 3.81181   )
names= c("Helchteren", "Wideumont","Jabbeke", "Avesnes")

#ras =   geofield_to_raster(   radar_1h[[18]])
#writeRaster(  ras , "radar_obs_202107142300.tiff", overwrite=TRUE     )
iview( radar_1h[[18]] , levels=breaks_pcp,  col=col_pcp ,legend=T )
plot( lons, lats , add=TRUE  )
q()

