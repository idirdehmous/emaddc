




exp=$1
data=/home/micro/Bureau/ex-R/tiff

# CONVERT EXPS

yy=2021
mm=07
rr=12
for dd in {12..16} ; do  
    for hh in {01..24} ; do 
	 date=${yy}${mm}${dd}${rr}
   gdalwarp -t_srs "+proj=longlat +datum=WGS84 +no_defs" ${data}/${exp}_${date}_${hh}.tiff  ${data}/${exp}_${date}_${hh}_gdal.tiff
    done 
done
exit  
# CONVERT RADAR 
for dd in {12..16} ; do
   for hh in {01..24} ; do
	    date=${yy}${mm}${dd}${rr}_${hh}
	    #radar_2021071500_12.tiff
   gdalwarp -t_srs "+proj=longlat +datum=WGS84 +no_defs" ${data}/${exp}_${date}.tiff  ${data}/${exp}_${date}_gdal.tif
   done
done  
