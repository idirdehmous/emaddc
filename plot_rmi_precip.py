import os
import sys  
import numpy as np  
from datetime import datetime
import calendar  
from matplotlib import pyplot as plt
import pysteps
from pysteps import io, rcparams 
from pysteps.utils import conversion , reprojection
from pysteps.visualization import plot_precip_field
from pysteps.verification  import  spatialscores , salscores , probscores
from pysteps import verification
import sqlite3   






# COPY THE pystepsrc file 
os.system( "cp -f ./rc/pystepsrc_1h ./pystepsrc ")



def Date2Epoch(date , Time ):
    yy=date[0:4] ; mm=date[4:6] ; dd=date[6:8] ; hh=Time[0:2]
    Current  = datetime(int(yy) , int(mm),int(dd) , int(hh)  )
    UnixTime = calendar.timegm(Current.utctimetuple())   # TIME IN UTC  
    return  UnixTime





def Regrid( nwp_pcp , rad_pcp , nwp_meta , rad_meta ):
    """
    FUNCTION TO REPROJECT THE MODEL GRID TO THE RADAR ONE 
    OUTPUT : NWP PCP FIELD IN RADAR GRID 
    """
    pcp_new =reprojection.reproject_grids(nwp_pcp , rad_pcp  , 
                                           meta_src , meta_dst)
    return pcp_new  



# PLOT THE RADAR RAINFALL AGAINST THE AROME (1 H ACCUM )
def PlotFields (step  , rad_arr, xp_arr ):
    """
    FUNCTION:  PLOTS RADAR AND MODEL PCP FIELDS  
    """

    npng="{:02}".format(( -1 )* step)
#    date_str = datetime.strftime (date_radar, "%Y-%m-%d %H:%M")
    rad_date= rad_meta ['timestamps' ][step]
    nwp_date= nwp_meta ['time_stamps'][step]
#    print("plot field " , rad_date , nwp_date  )

    print( "plot ..." , rad_date )  

    rad_pcp = rad_arr[0]
    cntr_pcp  =xp_arr[0] 
    scnr01_pcp=xp_arr[1]
    scnr02_pcp=xp_arr[2]

    plt.figure(figsize=(13, 8))
    plt.subplot(111)   
    plot_precip_field( rad_pcp[step,:,:]  , geodata=rad_meta, title=f"Radar observation at {rad_date}", )

    plt.subplot(132)
    plot_precip_field(cntr_pcp[step,:,:]  , geodata=nwp_meta  , title=f"NWP forecast at {nwp_date}" )

    plt.subplot(333)
    plot_precip_field(scnr01_pcp[step,:,:]  , geodata=nwp_meta  , title=f"NWP forecast at {nwp_date}" )

    plt.tight_layout()
    plt.savefig( "pcp_radar_ar13_"+str( npng )+".png" )




def GetRadar(StrDate  ):
    """
    FUNCTION : READS THE DATA FROM RADAR ARCHIVE  
    BY PARSING THE JSON FILE (pystepsrc)
    RETURN   : RADAR ACC PCP AND META DATA 
    """
    # GET DATE 
    pathdate = datetime.strptime(StrDate, "%Y%m%d%H%M%S").strftime( "%Y/%m/%d")
    rad_date = datetime.strptime(StrDate, "%Y%m%d%H%M%S")

    # SOURCE 
    radar_data_source = rcparams.data_sources["rmi"]

    # TO BE PARSED AND READ FROM pystepsrc FILE
    root_path       = radar_data_source["root_path"]
    path_fmt        = "%Y%m%d"
    fn_pattern      = "%Y%m%d%H%M00.rad.best.comp.acrr.qpe_1h"
    fn_ext          = radar_data_source["fn_ext"]
    importer_name   = radar_data_source["importer"]
    importer_kwargs = radar_data_source["importer_kwargs"]
    timestep        = 60.0             # IN MINUTES
    # FIND THE RADAR FILE IN ARCHIVE 
    fns = io.find_by_date( rad_date, root_path, path_fmt, fn_pattern, fn_ext, timestep, num_prev_files=23 )
    # READ THE RADAR COMPOSITE 
    importer                         = io.get_method     (importer_name, "importer")
    radar_precip, _ , radar_metadata = io.read_timeseries(fns, importer,qty="ACRR", **importer_kwargs)
    print( "1st Radar file  ...." ,   fns[0][0]  )
    return  radar_metadata , radar_precip  



def GetNwp(StrDate , Period , ExpName  ):
    """
    FUNCTION : READ MODEL PCP FIELD FROM A NETCDF FILE  
    RETURN   : PCP FIELD   AND META DATA 
    """
    # ROOT PATH TO EXPS
    exppath="/mnt/HDS_ALD_TEAM/ALD_TEAM/idehmous/testruns/EMADDC/pcp"
    # LAST NWP FORECAST at 12:00
    date_nwp = datetime.strptime(StrDate  , "%Y%m%d%H%M")

    # SOURCE 
    nwp_data_source   = rcparams.data_sources["rmi_nwp"]

    # GET NWP ( OVERWRITE THE PATHS )
    nwp_data_source["root_path"] =exppath+"/"+Period.upper()+"/"+ExpName.upper()
    nwp_data_source["path_fmt"]  ="%Y%m%d%H"
    nwp_data_source["fn_pattern"]="ar13_%Y%m%d%H_native_1h"
    nwp_data_source["fn_ext"]    ="nc"
    
    # FILENAME 
    filename = os.path.join( nwp_data_source["root_path"],datetime.strftime(date_nwp, nwp_data_source["fn_pattern"])+ "."+ nwp_data_source["fn_ext"]  )
    print( "Nwp data ...." , filename )  
    nwp_importer = io.get_method("rmi_nwp", "importer")
    nwp_precip  , _  ,nwp_metadata = nwp_importer(filename )
    return  nwp_metadata , nwp_precip   



# LOOP OVER THE DATES 
period="SUM"
#exp= "CONTROL"
yy="2021"   ; mm="07"  ; start=14  ; end=14

# START RAD AND NWP 
rad_hh="23" ; nwp_hh="00"

# STEPS 
ntimes =np.arange(-1,-24,-1)

rad_exps=[]
nwp_exps=[]
# LOOP OVER DAYS 
for d in range(start , end+1):

    for exp in  ["CONTROL", "SCNR01","SCNR02"]:
        dd= "{:02}".format(d )  
        print( dd )   
        rad_date=yy+mm+str(dd)+rad_hh+"00" 
        nwp_date=yy+mm+str(dd)+nwp_hh+"00"

        rad_meta , rad_pcp  = GetRadar( rad_date )
        nwp_meta , nwp_pcp  = GetNwp  ( nwp_date  , period , exp )

        nwp_pcp =np.flip(nwp_pcp, axis=1)
        

        # MAKE SURE THE UNITS ARE IN mm/h
        converter                  = pysteps.utils.get_method("mm/h")
        rad_pcp , rad_meta = converter(rad_pcp  , rad_meta )
        nwp_pcp , nwp_meta = converter(nwp_pcp  , nwp_meta )
    
        # THRESHOLD THE DATA 
        rad_pcp [rad_pcp   < 0.01] = 0.0
        nwp_pcp [nwp_pcp   < 0.01] = 0.0

        # PROJECT THE PCP FIELD  ( RETURN A TUPLE , GET ONLY THE DATA )
        meta_src = nwp_meta
        meta_dst = rad_meta
        nwp_pcp  = Regrid ( nwp_pcp , rad_pcp , nwp_meta , rad_meta )[0]
        rad_exps.append(rad_pcp)
        nwp_exps.append(nwp_pcp)

for i in ntimes:
    PlotFields(i , rad_exps , nwp_exps  )
quit()

# PERCENTILES 
#    for i in range(nwp_pcp.shape[0]):
#        for j in range(nwp_pcp.shape[1]):
#            for k in range(nwp_pcp.shape[2]):
#                arr.append( nwp_pcp[i,j,k])
#    print( np.percentile( pp , [10,20,30,40,50,60,70,80,90,99] ) )


#fss = verification.get_method("SAL")
fig , ax = plt.subplots(figsize=(8,8))
plt.plot( scales , score  , marker="o" )
plt.savefig("fss.png")
quit()

# THE ROC 
# Upscale data to 2 km
#R_o, metadata_o = dimension.aggregate_fields_space(R_o, metadata_o, 1000)
#R_f, metadata_f = dimension.aggregate_fields_space(nwp_pcp , nwp_metadata, 1000)

#R_o[~np.isfinite(R_o)] = -15.0
#P_f = ensemblestats.excprob(R_f[:, :, :], 0.1, ignore_nan=True)

roc = verification.ROC_curve_init(0.01, n_prob_thrs=5)

verification.ROC_curve_accum(roc, nwp_pcp[-5,:,:]  , rad_pcp[-5, :, :])
print( verification.ROC_curve_compute(roc, compute_area=True))

#fig, ax = plt.subplots()
#verification.plot_ROC(roc, ax, opt_prob_thr=True)
#plt.savefig("roc.png")



quit()
