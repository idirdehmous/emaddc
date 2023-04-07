library(Rfa)
library(harpSpatial)
library(RSQLite)
library(stringr)


source("functions.R")





args = commandArgs(trailingOnly=TRUE)
if (length(args) !=2 ) {
  stop("Arguments missing : USAGE : ./getForecast.R  exp  day", call.=FALSE)
} else  if  ( length(args)==2) {
exp  =args[1]
DD  =args[2]

}


# - easy leading zeros
lz=function(x,n=2) formatC(x,flag="0",format="d",width=n)



fdate=function(date){
  format.Date(date,"%Y-%m-%d %H:%M UTC")
}

# MODEL 
period="WIN"
ref   = exp  
model ="AR13"
year  =2022
month =1
day   =DD
starth=12
basedir=paste( "/mnt/HDS_ALD_TEAM/ALD_TEAM/idehmous/testruns/EMADDC/fpos", period, sep="/" )
id=""

files_ref  =paste0(basedir,"/",ref,"/",year ,lz(month),lz(day),lz(starth),"/","PF",model,"be13b_l+",lz(seq(1,24,1),4))


GetPcp  = function ( files ) {
pcp=lapply(files,function(fa) FAdec(fa,"SURFACCPLUIE"))

pcp_1h=list()
first=TRUE
for(i in seq_along(pcp)){
#  print(i)
  if (first){
    pcp_1h[[i]]=pcp[[i]]
    first=FALSE
  } else {
    pcp_1h[[i]]=pcp[[i]]-pcp[[i-1]]
    pcp_1h[[i]][pcp_1h[[i]]<0]=0
  }
}

return ( pcp_1h ) 
}

pcp_1h= GetPcp ( files_ref ) 

#RADAR
library(rhdf5)
library(belgium)
radarbase="/mnt/HDS_RADAR_EDP/realtime"
validdates=lapply(files_ref  ,function(fa) attr(FAopen(fa),"time")$validdate)
radar_1h=list()

for (i in seq_along(validdates)){
  date=validdates[[i]]
  print(date)
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


db   <- dbConnect(RSQLite::SQLite(),  paste("/mnt/HDS_ALD_TEAM/ALD_TEAM/idehmous/testruns/EMADDC/pcp/FSS/sqlite/fss" , period , starth,  sep="_"   ) )
query=paste ("CREATE TABLE IF NOT EXISTS  FSS   (
                                exp    TEXT  , 
                                th    REAL ,
                                scale   INTEGER , 
                                fss     REAL   , 
                                leadtime  REAL )", sep=" ")
dbSendQuery(conn = db  , query  )





# COMPUTE FSS 
# FSS THRESHOLD  
thresh=c(0.01, 0.05 ,0.1 , 0.15, 0.5 ,1,2, 5 )

# N WINDOWS 
scales=c(3,5, 9, 17 , 33 , 65 , 129 , 257 , 501  )

options(scipen=999)
# REGRID PCP TO RADAR GRID
for (  i in 1:length( pcp_1h)) {

# REGRID
pcp_reg =regrid(  pcp_1h[[i]] , radar_1h[[i]]) 

fcfield=pcp_reg
obfield=radar_1h[[i]]

#verify_fuzzy (obfield, fcfield, thresholds, window_sizes)
for ( j in seq_along (scales))  {
n=scales[j]

    for ( k in seq_along(thresh))  {
      thr=thresh[k]
      InsertQuery=paste('INSERT INTO ', 'FSS' ,' (exp ,th , scale , fss , leadtime ) VALUES(?,?,?,?,?);'  , sep=" ")


fss= verify_fuzzy ( fcfield , obfield , thresh[k]  ,   c( n, n )   )
th= fss[[1]][[1]]   # THRESHOLD 
sc= fss[[2]][[1]]   # SCALE
fs= fss[[3]][[1]]   # FSS 
ldtime=i 

# WRITE THE DATA 
dbSendQuery(db, InsertQuery ,list(exp , th , sc  , fs  , i ))
print( c(th ,  sc , i , fs ) ) 
   }
}
}

dbDisconnect(conn)
q()


