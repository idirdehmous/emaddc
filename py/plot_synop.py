#import matplotlib  
#matplotlib.use("Agg")
from scipy.interpolate   import  make_interp_spline, BSpline
import numpy as np   
import sys
from   statistics  import stdev  , mean  
from collections import OrderedDict
from matplotlib import pyplot as plt
from matplotlib import rc
#import pandas as pd 
import os  

# GET INPUT FILE 
# SPLIT TIBBLE OBJECT FROM HARP 
infile=sys.argv[1]



# GET THE PLT PLOT GLOBAL SETTINGS 
#for k , v in plt.rcParams.items():
#    print( k , v  )  

# PLOT FROM SPLITTED  TIBBLE OBJECT (HARP)
#plt.style.use("ggplot")
# CUSTOM SETTING OF PLT PLOT 
plt.rc    ('text'  , usetex=False)
plt.rcParams['axes.facecolor']='w'
plt.rcParams['axes.linewidth'] = 0.5
plt.rcParams['font.serif'] = "Times Roman"
plt.rcParams['ytick.labelsize']=16
plt.rcParams['xtick.labelsize']=16
plt.rcParams['axes.titlesize' ]=14
plt.rcParams['axes.labelsize' ]=18
plt.rcParams['legend.fontsize']=12
plt.rcParams['legend.loc']     ="best"
plt.rcParams['font.weight']    = 'normal'
plt.rcParams['grid.alpha']     = 0.2
plt.rcParams['grid.color']    ='gray'
plt.rcParams['grid.linestyle']= '--'
plt.rcParams['grid.linewidth']= 0.5

#plt.rcParams['axes.labelweight']='bold'





# PARIOD
prd="WIN"

# PARAMS 
params=["T2m","S10m","RH2m","Pmsl","CCtot"]     # PARAMS TO PLOT 

# EXPS 
exps  =["CONTROL_"+prd, 
         "SCNR01_"+prd,
         "SCNR02_"+prd,
         "SCNR03_"+prd,
         "SCNR04_"+prd]                    # EXPS NAMES (AS IN .csv  FILE )

# DICTIONARY EXPS 
ds={"CONTROL_"+prd:"CONTROL",
     "SCNR01_"+prd:"SCENARIO-01",
     "SCNR02_"+prd:"SCENARIO-02",
     "SCNR03_"+prd:"SCENARIO-03",
     "SCNR04_"+prd:"SCENARIO-04"}



#dictcol={"CONTROL_"+prd:"#F8766D",
#          "SCNR01_"+prd:"#7CAE00",
#          "SCNR02_"+prd:"#00BFC4",
#          "SCNR03_"+prd:"#C77CFF" ,
#          "SCNR04_"+prd:"#3258fc" }
dictcol={"CONTROL_"+prd:"red",
          "SCNR01_"+prd:"blue",
          "SCNR02_"+prd:"gold",
          "SCNR03_"+prd:"green" ,
          "SCNR04_"+prd:"black" }



dalpha={"CONTROL_"+prd :0.8,      
          "SCNR01_"+prd:0.7,
          "SCNR02_"+prd:0.9,
          "SCNR03_"+prd:0.6,
          "SCNR04_"+prd:0.6}

#  LINES WIDTHS 
dls={"CONTROL_"+prd:1.8,
     "SCNR01_"+prd: 1.8,
     "SCNR02_"+prd: 1.7,
     "SCNR03_"+prd: 1.6,
     "SCNR04_"+prd: 1.0}
dmarker={"CONTROL_"+prd:"o",
         "SCNR01_"+prd :"v",
         "SCNR02_"+prd :"x",
         "SCNR03_"+prd :"*",
         "SCNR04_"+prd :"^"}



# PARAM NAMES 
dictp={"T2m" :"T2m" ,"RH2m" :"RH2m",
       "S10m":"S10m","Pmsl" :"Pmsl", 
       "G10m":"G10m","CCtot":"CCtot"}

# PARAM LIST 
plist=["T2m","RH2m","S10m","G10m","Pmsl","CCtot"]

# PARAM NAMES 
dname={"T2m" :"2m Temperature ","RH2m":"2m Relative humidity ",
       "S10m":"10m Wind speed","G10m":"Wind gust",
       "Pmsl":"Mean sea level pressure","CCtot":"Total could cover"}

# PARAM UNITS 
dictu={"T2m" :"C"  , "RH2m":"%"  ,"S10m" :"m/s",
       "G10m":"m/s", "Pmsl":"hpa","CCtot":"Oktas"}

# METRICS TO PLOT 
metrics=["bias","rmse"]#"stde"]



Dates=[]
nstation=[]
leadtime=[]

def ReadTibble(infile , param , exp    ):
    ldtime=[]
    bias  =[]
    rmse  =[]
    stde  =[]
    ncase =[]
    nstat =[]
    file=open(infile , "r")
    lines=file.readlines()[1:]
    for line in lines:
        l=line.rstrip().split(",")
       
        if l[7].replace('"','') == param and l[0].replace('"','') ==exp :
         
           ldtime.append( int(l[1])   )
           ncase.append( int(l[2])   ) 
           bias.append ( float(l[3])   )
           rmse.append ( float(l[4])   )
           stde.append ( float(l[6])   )
           Dates.append(l[8])   
           nstat.append(  int(l[9])   )
           nstation.append(  (l[9])   )
    return   ldtime , bias , rmse  , stde , ncase , nstat  
for p in params:
    for exp in exps:

        outfile=open( p+"_"+exp+".txt" , "w"  )
        ldtime , bias , rmse , stde,ncase , nstat    =  ReadTibble(infile ,  p ,  exp   )
        for i in range(len(ldtime)):
            outfile.write(  str(ldtime[i]) +" "+ str( bias[i]) +" "+str(rmse[i])+" "+str(stde[i])+" "+str(ncase[i])+" "+str(nstat[i]) + "\n" )
outfile.close()


# READ VALUES 
def ReadData(infile, target  ):
    leadtime=[]
    value=[]
    if   target  == "bias":
       idx=1
    elif target  == "rmse":
       idx=2  
    elif target  == "stde":
       idx=3
    elif target  == "ncase":
       idx=4
    else:
       print("Unknown variable to plot ", target )

    file= open(infile , "r")
    lines=file.readlines()  
    for line in  lines:
        l=  line.rstrip().split() 
        leadtime.append(float(l[0]))  
        value.append(float(l[idx]))
    return   leadtime , value  


def Smooth(x , y  ):
    x_new = np.linspace(min(x), max(x), 57)
    spl = make_interp_spline(x, y, k=1)
    y_new   = spl(x_new)
    return  x_new , y_new      




def PlotHists(plist ):
    plt.rcParams['axes.prop_cycle'] = plt.cycler(color=["#F8766D", "#7CAE00", "#00BFC4" ,"#C77CFF", "#0738FA"] )
    n=3 
    fig= plt.subplots(3, 2, figsize=(12,8))
    idx = [np.arange(0,3), 
           np.arange(0,3)-0.1,
           np.arange(0,3)-0.15,
           np.arange(0,3)-0.2 ,
           np.arange(0,3)-0.3    ]
    
    width=0.10
 
    labels = ['Bias' , 'Sigma', 'RMSE' ]
    i=0
    for p in plist:
        i=i+1  
        for j , exp  in enumerate(exps): 
            b,std , rms = ( mean(ReadData (p+"_"+exp+".txt", "bias")[1]), 
                            mean(ReadData (p+"_"+exp+".txt", "stde" )[1]),
                            mean(ReadData (p+"_"+exp+".txt", "rmse" )[1])
                             )
            print( b , std , rms , p )
            plt.subplot(3, 2, i)   
#            plt.bar( [0,1,2]  , [b  ,std , rms  ], width,  label=exp.upper())     
            plt.bar( idx[j]  , [b  ,std , rms  ], width,  label=exp.upper())
            plt.title(dictp[p], fontsize=10)
            plt.axhline(y = 0.0, color = 'k', linestyle = '--', linewidth=0.2 )
            plt.xticks( idx[j]  )
            plt.xticks( idx[j],  labels)
            plt.ylabel(dictu[p])
            plt.legend(frameon=False, fontsize=6)
   # plt.savefig("hists.png")
    plt.show ()  



def PlotParam(param, metric):
    
    fig,ax1 =   plt.subplots(figsize=(8,6))
    for xp in exps:
        x0, r0    =  ReadData (param+"_"+xp+".txt" , metric )
       

        x0_n, r0_n =   Smooth ( x0 , r0  )
        x_n=x0_n
        lw=1.5
        ms=4.5
        
        plt.plot(x0_n, r0_n  ,color=dictcol[xp] ,
                              ls    ="-" , linewidth=dls[xp], 
                              marker=dmarker[xp], markersize=ms  , 
                              alpha=dalpha[xp],
                              label = ds[xp])
        runtime = Dates[0].replace('"','')[-2:]
        plt.title(dname[param]+"\n fcrange= 0h  to +36h \n Period: "+str(Dates[0].replace('"',''))+"  ,Runtime: "+str(runtime)+"H" +" , stations="+nstation[0] )

        plt.subplots_adjust(top=0.8)

        if metric == "bias": 
           plt.ylabel("BIAS ["+dictu[param]+"]")
        elif metric == "rmse":
           plt.ylabel("RMSE ["+dictu[param]+"]")
        elif metric =="stde":
           plt.ylabel("Stdev["+dictu[param]+"]")
        else:
           print( "unknown variable ", metric ,"to plot on Y axis" ) 

        plt.xlabel("Leadtime [hour]")

        lgds, labels = plt.gca().get_legend_handles_labels()
        lls = OrderedDict(zip(labels, lgds))
        ax1.legend(lls.values(), lls.keys(),  frameon=False)
#        ax1.set_facecolor("#fafbfc")
        ax1.set_facecolor("#ffffff")
        ax1.grid(True)
        plt.tight_layout()
        print "Plot",  param+"_"+metric+"_"+prd.lower()+"_"+str(runtime), "..." 
    plt.savefig(param+"_"+metric+"_"+prd.lower()+"_"+str(runtime)+".pdf")
#    plt.show()

# PLOT GRAPHS 
for p in params: 
    for m in metrics:  PlotParam( p,  m    )


# CLEAN
os.system("rm  *.txt")
quit()


# PLOT  GLOBAL STATISTICS ( OPTIONAL  !! )
PlotHists(params)
quit()









#import img2pdf
#with open("pythonPlot.pdf", "wb") as f:
#    f.write(img2pdf.convert([i for i in os.listdir('.') if i.endswith(".png")]))

#os.system("rm   *.txt")

import img2pdf
with open("pythonPlot_surf_sum_00.pdf", "wb") as f:
     f.write(img2pdf.convert([i for i in os.listdir('.') if i.endswith(".png")]))   
 #---->> CHANGED 

     #f.write( img2pdf.convert([i for i in  plist ] ) )

# CLEAN
os.system("rm   *.png *.txt")



quit()

