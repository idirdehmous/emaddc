import os   
import sys   
from math import sqrt  
import datetime  
import numpy as np 
import sqlite3
import  calendar


""" PROLOGUE 
    
    PYTHON SCRIPT TO WRITE EXTRACTED  odbsql FILES 
    INTO AN SQLITE DB 

@__:RMI 
@__:IDIRDEHMOUS
C__:14/10/2022 
"""

def Emaddc2Sqlite(outfile ,code, id ,vdate,dt_str, lat , lon ,alt ,  press, varno , obsvalue  ):
    sqlite_file =   outfile
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    sql_command = 'CREATE TABLE IF NOT EXISTS EMADDC  (      \
                                         codetype INTEGER ,  \
                                         id  INTEGER,        \
                                         validdate INTEGER , \
                                         date_str  TEXT     , \
                                         lats REAL ,         \
                                         lons REAL ,         \
                                         alts REAL ,         \
                                         press REAL,         \
                                         varno  REAL,        \
                                         obsvalue )'

    c.execute(sql_command )
    sql_insert ="INSERT INTO EMADDC (codetype,id,validdate,date_str ,lats,lons,alts, press,varno, obsvalue) VALUES (?,?,?,?,?,?,?,?,?,?)"
    for i in range(len(id)):
      c.execute(sql_insert,( codetype,id[i] ,vdate[i],dt_str[i],lat[i] ,lon[i] ,alt[i], press[i] ,varno[i], obsvalue[i]))
    conn.commit()
    conn.close()





dates=[]  ; 
times=[]  ;  



def Date2Epoch(date , Time ):
    yy=date[0:4] ; mm=date[4:6] ; dd=date[6:8] ; hh=Time[0:2]
    Current  = datetime.datetime(int(yy) , int(mm),int(dd) , int(hh)  )
    UnixTime = calendar.timegm(Current.utctimetuple())   # TIME IN UTC  
    return  UnixTime

def ReadOdbsql(infile):
    global codetype  
    validdate=[]
    dt_str =[]
    ids =[]
    lats=[]
    lons=[]
    alts=[] 
    varnos =[]
    oma_dep=[]
    omg_dep=[]
    press=[]
    obsval=[]
    
    filepath=infile  
    file=open(filepath , "r")
    lines=file.readlines()

    for line in lines: 
        
        l=line.rstrip().replace("'","").split() 
        codetype=l[1]
        if codetype   ==  "147":     #147 ----Mode-S   ,  144---AMDAR

#               dt = datetime.datetime.strptime(l[8]+" "+l[9][0:4], '%Y%m%d %H%M')
           dt=l[8]+l[9][0:2]
           validdate.append( Date2Epoch ( l[8] ,  l[9][0:4] ) )  
           dt_str.append(dt)
#               dates.append(dt)
           ids.append(l[2])
           varnos.append(int(l[3]))
           lats.append(float(l[4]))
           lons.append(float(l[5])) 
           alts.append(float(l[7]))
           press.append(float(l[6])/100. )
#               omg_dep.append(float(l[11]))
#               oma_dep.append(float(l[12]))
           obsval.append(float(l[10]))
    return  codetype, ids , varnos ,validdate, dt_str,  lats , lons , alts, press , obsval   


# READ ALL FILES   
exp="control"
obstype="modes"
period="WIN"
mode="total"
path="/mnt/HDS_ALD_TEAM/ALD_TEAM/idehmous/testruns/EMADDC/"+period+"/ODB/data/"+mode+"/"+exp+"/"+obstype+"/"
files=os.listdir(path)

outpath="/mnt/HDS_ALD_TEAM/ALD_TEAM/idehmous/testruns/EMADDC/"+period+"/ODB/"
for file in files:
    infile=path+file
    if os.path.exists(infile):
       size= os.path.getsize( infile  )
       CODETYPE=147
       codetype=CODETYPE 
       codetype, ids , varno ,vdate, dt_str, lats , lons , alts, press ,obsval  =ReadOdbsql(infile )
       if len(ids) != 0 and size != 0 :
          print( "file" ,infile ,"exists " )  
#          Emaddc2Sqlite(mode+"_"+exp+"_"+period.lower()+".sqlite", codetype, ids ,vdate, dt_str ,lats , lons ,alts ,  press, varno , omg_dep, oma_dep,obsval )
          Emaddc2Sqlite(mode+"_"+exp+"_"+period.lower()+".sqlite", codetype, ids ,vdate, dt_str,lats , lons ,alts ,press, varno ,obsval )

    else:
       print( infile ,"file doesn t exist or empty "  ) 
       continue  


