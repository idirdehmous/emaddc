import os   
import sys   
from math import sqrt  
import datetime  
import numpy as np 
import sqlite3
import  calendar


"""PROLOGUE 
   PYTHON SCRIPT TO WRITE FSS VALUES TO AN 
   SQLITE FILE CONTAINING THE COLUMNS :
          validdate , ldtime , th , scale , fss

@__: IDIR DEHMOUS  
@__: RMI  
C__: 01/04/2023 
"""


# ARGS 
if len(sys.argv) != 4:
   print("USAGE:  python3 fss2sqlite.py  infile expname period \nWritten for the emaddc study" )
   sys.exit()
else:
   infile=sys.argv[1]
   exp  = sys.argv[2]
   period=sys.argv[3]


# FUNCTIONS 
def Fss2Sqlite(outfile ,exp , date,ldtime ,  th , scale ,fss  ):
    sqlite_file =   outfile
    conn = sqlite3.connect(sqlite_file)
    c = conn.cursor()
    sql_command = 'CREATE TABLE IF NOT EXISTS FSS  (      \
                                         exp    TEXT ,  \
                                         date INTEGER  ,        \
                                         th   REAL    , \
                                         scale REAL   ,         \
                                         leadtime REAL  ,         \
                                         fss   REAL )'

    c.execute(sql_command )
    sql_insert ="INSERT INTO FSS  (exp , date , th , scale , leadtime , fss ) VALUES (?,?,?,?,?,?)"
    for i in range(len(fss)):
        c.execute(sql_insert,( exp, date[i], th[i], scale[i], ldtime[i], fss[i]) )
    conn.commit()
    conn.close()


def Date2Epoch(date , Time ):
    yy=date[0:4] ; mm=date[4:6] ; dd=date[6:8] ; hh=Time[0:2]
    Current  = datetime.datetime(int(yy) , int(mm),int(dd) , int(hh)  )
    UnixTime = calendar.timegm(Current.utctimetuple())   # TIME IN UTC  
    return  UnixTime

# READ FSS TEXT FILE 
def ReadFssText(infile):
    validdate=[]
    scale=[]
    ldtime=[]
    th=[] 
    fss =[]
    
    filepath=infile  
    file=open(filepath , "r")
    lines=file.readlines()

    for line in lines: 
        
        l=line.rstrip().replace("'","").split() 
        
        if len(l) == 4: 
           ts=l[0] ; sc=l[1] ; fs=l[2] ; ldt=l[3]

           ldtime.append(ldt) 
           th.append(float(ts))
           scale.append(float(sc))
           fss.append(float(fs ))
        elif len(l) ==1 :
           vdate=l[0]        
           validdate.append(vdate)  
    return validdate , ldtime , th , scale , fss  

validdate , ldtime , th , scale , fss  =ReadFssText(infile )
# CONVERT
Fss2Sqlite("fss_"+period+".sqlite",exp.upper() , validdate , ldtime , th , scale , fss )
