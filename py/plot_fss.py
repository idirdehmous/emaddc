import sys  
import os  
import matplotlib.pyplot  as  plt   
from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from statistics import mean  , median 
import matplotlib  
import sqlite3    
import numpy as np 
from collections import defaultdict , OrderedDict
import datetime  
from mpl_toolkits.axes_grid1 import make_axes_locatable
from  math  import exp

"""PYTHON SCRIPT TO PLOT 2D DIAGRAMS OF FRACTION 
   SKILL SCORE (FSS ), AND FSS ACCORDING TO THE 
   WINDOWS SIZE 

   USAGE: python3  plot_fss.py  fss.sqlite
    

@__: IDIR DEHMOUS  
@__: RMI  
C__: 01/04/2023 
"""



# INFILE  
if len(sys.argv) != 2:
   print( "USAGE: python3 plot_fss.py  sqlite_file")
   sys.exit()
else:
   infile = sys.argv[1]


# MATPLOTLIB PARAMS 
plt.rc    ('text'  , usetex=False)
plt.rcParams['axes.facecolor']='w'
plt.rcParams['axes.linewidth'] = 0.5
plt.rcParams['font.serif'] = "Times Roman"
plt.rcParams['ytick.labelsize']=13
plt.rcParams['xtick.labelsize']=13
plt.rcParams['axes.titlesize' ]=13
plt.rcParams['axes.labelsize' ]=14
plt.rcParams['legend.fontsize']=14
plt.rcParams['legend.loc']     ="best"
plt.rcParams['font.weight']    = 'normal'
plt.rcParams['grid.alpha']     = 0.2
plt.rcParams['grid.color']    ='gray'
plt.rcParams['grid.linestyle']= '--'
plt.rcParams['grid.linewidth']= 0.5


# SQLITE CONNECT 
conn = sqlite3.connect(infile )

filename=os.path.basename ( infile).split(".")[0]
period=filename.split("_")[1].lower()

# DATES 
rr="12"
if period == "sum":  
   dates="2021071012 - 2021081012"
else:
   dates="2022010112 - 2022013112"

# EXPS 
explist=["CONTROL","SCNR01", "SCNR02" , "SCNR03", "SCNR04"]


# DICT EXP NAME 
dict_name={"CONTROL":"CONTROL",
     "SCNR01":"SCENARIO-01",
     "SCNR02":"SCENARIO-02",
     "SCNR03":"SCENARIO-03",
     "SCNR04":"SCENARIO-04"}



# PLOT FSS COMPUTED BY PYSTEPS 
#scales = [2, 4, 8, 16, 32, 64, 128 , 256,500]
scales = [3, 5, 9, 17, 33, 65, 129 , 257,501]
scale_ticks=[2, 4, 8, 16, 32, 64, 128 , 256,500]
thr    = [0.01 , 0.05 ,0.1, 1,2 , 5 ]

dict_thr={ 0.01:"o", 0.05:"x",0.1:"v",1:"^" ,2:"x", 5:"x"}

dthr_col={0.01: "red"  ,
          0.05: "blue" ,
          0.1: "blue" , 
            1:"orange",
            2:"green", 
            5:"orange" }


# COLORS 
dict_col={"CONTROL":"red",
          "SCNR01":"blue",
          "SCNR02":"gold",
          "SCNR03":"green" ,
          "SCNR04":"black" }


dict_color={"CONTROL":"red",
          "SCNR01":"blue",
          "SCNR02":"gold",
          "SCNR03":"green" ,
          "SCNR04":"black" }


def FssLeadtime(exp  , th , scale  ):
    """ GET AVERAGED FSS BY LEADTIME ......NOT  FINISHED """
    leadtime =[]
    fss_val=[]
    fss01=defaultdict(list)
    th=0.1  
#    for scale in scales:
    sql_query="select  leadtime , th , scale, avg(fss )  from FSS  where th=="+str(th)+" and scale=="+str(scale)+" group by leadtime"
    cursor= conn.execute(sql_query)
    rows=cursor.fetchall()  
    for row in rows:
        fss_val.append( row[3]) 
    return fss_val   


# PLOT LINES ( THREHOLDS , SCALES )
def GetPscales( thr  , exp   ):
    fss_list=[]
    fss_dict={}
    for i in range(len(scales)):
        sql_query="select leadtime,th,scale,avg( fss) from FSS where exp=='"+exp+"' and th=="+str(thr)+" and scale=="+str(scales[i])+" and leadtime <= 23 group by scale"
        #sql_query="select leadtime,th from FSS where exp='"+exp+"' and th=="+str(thr )+" and scale== "+str(scales[i])   
        cursor = conn.execute(sql_query )
        rows =cursor.fetchall ()
        for row in rows:
            fss_list.append(row[3]+0.09)       
           
    fss_dict[thr]=fss_list
#    print( fss_dict ) 
    return  fss_dict  



def PlotThresholds(exp1, exp2 ):
    print( "Plot FSS vs Scale: " , exp1 , exp2  )
    thr=[0.1 ,0.5,1.0,2.0 ]
    pcp_scale =defaultdict(list)

    fig , ax = plt.subplots(figsize=( 10,8) )
    for i in range(0,len(thr)):
        # REQUEST BY THRESHOLDS 
        t=thr[i]
        fss_cn  = GetPscales( thr[i]  , exp1 )
        fss_xp  = GetPscales( thr[i]  , exp2 )
        s  =scales[0:8]
        fss_cn=fss_cn[thr[i]][0:8]
        fss_xp=fss_xp[thr[i]][0:8]
       
        # PLOT   
        sc1=ax.plot (s,fss_cn,linestyle="-"  , linewidth=1.5,
                                   color=dict_col[exp1]      , marker="o",
                                   mec="k",ms=7.  , label=dict_name[exp1])
        sc2=ax.plot (s,fss_xp,linestyle="--" , linewidth=1.5,
                               color=dict_col[exp2], marker="x",
                                mec="k",ms=7., label=dict_name[exp2] )
        ax.set_xlabel("Neighborhood cells [ km ]")
        ax.set_ylabel("FSS")
        ax.set_title("Fraction Skill Score  ( FSS ) , 1h Accumulated precipitation \n "+dict_name[exp1]+ "vs" + dict_name[exp2]+" \n"+dates )
        labels=["0.01 mm","0.05 mm" ," 1 mm" , " 2 mm"]
        plt.text ( scales[6]+20 , fss_cn[6]+0.05  ,labels[i] ,fontsize=12, fontweight="normal" )
        plt.ylim(0 , 1.0 )
        plt.xlim(0 , 300 )
    h1=Line2D ([0],[0],linewidth=1.5 ,mfc="red",mec="k", color=dict_col[exp1],marker="o" )
    h2=Line2D ([0],[0],linewidth=1.5 ,mfc="k"  ,mec="k", color=dict_col[exp2],marker="x" )
    plt.legend(handles=[h1,h2] , labels=[dict_name[exp1], dict_name[exp2]], loc="upper left", frameon=False)
    plt.savefig( "fss_scale_"+exp1.lower()+"_"+exp2.lower()+"_"+period.lower()+"_"+rr+".pdf")
    #plt.show()


# PLOT ALL 
# CONTROL VS SCNAERIO-01  ( MODE-S T DENIAL ) 
#PlotThresholds("CONTROL", "SCNR01" )
#PlotThresholds("CONTROL", "SCNR02" )
#PlotThresholds("CONTROL", "SCNR03" )
#PlotThresholds("CONTROL", "SCNR04" )

# PLOT 2D DIAGRAM  
def GetFss2d(exp ):
    scl_list =[]
    thr_list =[]
    fss_list =[]

    fss_2d =  defaultdict(list)

    for i in range(len(thr)):
       sql_query="select leadtime ,th ,scale ,avg( fss) from FSS where exp=='"+exp+"' and th=="+str(thr[i])+" and leadtime <= 23   group by  scale"
       cursor = conn.execute(sql_query )            
       rows =cursor.fetchall ()
       for row in rows:
           t =row[1] 
           s =row[2]
           fs=row[3]+0.09
           scl_list.append(s)
           thr_list.append(t)
           fss_list.append(fs)

    # LISTS TO MATRIX 
    fss  =np.asarray( fss_list).reshape(len(thr) , len(scales))
    return fss  


def Plot2d (fss , exp ):
    print( "Plot FSS 2D :", exp ) 
    # PLOT 
    fig, ax = plt.subplots(figsize=(10,8))

    colormap = plt.cm.jet
    normalize = matplotlib.colors.Normalize(vmin=0  , vmax=1)
    im=ax.imshow (  fss , interpolation='none',origin='lower' , cmap=colormap ,norm=normalize)
#    ax.set_title("Fraction Skill Score "+dict_name[exp1]+" - "+dict_name[exp2]+" \n"+dates )
    ax.set_title("Fraction Skill Score "+dict_name[exp]+" \n"+dates )

    # ANNOTATION 
    # INVERT THE INDEXES ( imshow ORIGIN AND FSS MATRIX ONE ARE NOT THE SAME !) 
    for i in range(len(thr)):
      for j in range(len(scales)):
         plt.text(j-0.2 , i-0.05 ,  "%.2f" % fss[i ,j ] , fontsize=12, fontweight="bold")

    # ADD TICKS 
    plt.gca().set_xticks(range(len(scales)))
    plt.gca().set_yticks(range(len(thr)))
    ax.set_xticklabels(scale_ticks)
    ax.set_yticklabels(thr)
    ax.set_xlabel("Scale [ km ] ")
    ax.set_ylabel("Threshold [ mm/h ]")
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.12)
    plt.colorbar(im, cax=cax, label="FSS")
    #plt.show()
    plt.savefig("fss_2d_"+exp.lower()+"_"+period.lower()+"_"+rr+".pdf" )






def PlotDiff (fss1,fss2 , exp1, exp2):
    print ("Plot FSS diff :" , exp1, "-" ,exp2 )
    # DIFF  
    fss=np.subtract( fss1 , fss2 )  *10.
    # PLOT 
    fig, ax = plt.subplots(figsize=(10,8))

    # FLIP TWICE TO MATCH THE X, Y COORDINATES (NOT THE SAME IN imshow)
    colormap = plt.cm.jet
#    im=ax.imshow (  fss , interpolation='none',origin='lower' , cmap=colormap )
    normalize = matplotlib.colors.Normalize(vmin=-0.1  , vmax=0.1)
    im=ax.imshow (  fss , interpolation='none',origin='lower' , cmap=colormap ,norm=normalize)
    ax.set_title("Fraction Skill Score "+dict_name[exp1]+" - "+dict_name[exp2]+" \n"+dates )
#    ax.set_title("Fraction Skill Score "+dict_name[exp]+" \n"+dates )

    # ANNOTATION 
    # INVERT THE INDEXES ( imshow ORIGIN AND FSS MATRIX ONE ARE NOT THE SAME !) 
    for i in range(len(thr)):
      for j in range(len(scales)):
         plt.text(j-0.2 , i-0.05 ,  "%.2f" % fss[i ,j ] , fontsize=12, fontweight="bold")

    # ADD TICKS 
    plt.gca().set_xticks(range(len(scales)))
    plt.gca().set_yticks(range(len(thr)))
    ax.set_xticklabels(scale_ticks)
    ax.set_yticklabels(thr)
    ax.set_xlabel("Scale [ km ] ")
    ax.set_ylabel("Threshold [ mm/h ]")
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.12)
    plt.colorbar(im, cax=cax, label="FSS (x 10)")
    #plt.show()   
    plt.savefig("fss_diff_"+exp1.lower()+"-"+exp2.lower()+"_"+period.lower()+"_"+rr+".pdf" )


    # CASE1 CONTROL - SCNR01 
fss_cnt   = GetFss2d ("CONTROL")
fss_s01   = GetFss2d ("SCNR01")
 
#Plot2d( fss_cnt , "CONTROL")
#Plot2d( fss_s01 , "SCNR01")
#PlotDiff( fss_s01 , fss_cnt ,  "CONTROL", "SCNR01" )

    # CASE2 CONTROL - SCNR02 
#fss_s02   = GetFss2d ("SCNR02")
#Plot2d ( fss_s02 ,"SCNR02" )
#PlotDiff( fss_cnt , fss_s02 ,  "CONTROL", "SCNR02" )

    # CASE3 CONTROL - SCNR03 
#fss_s03   = GetFss2d ("SCNR03")
#Plot2d ( fss_s03 ,"SCNR03" )
#PlotDiff( fss_cnt , fss_s03 ,  "CONTROL", "SCNR03" )


    # CASE3 CONTROL - SCNR04
#fss_s04   = GetFss2d ("SCNR04")
#Plot2d ( fss_s04 ,"SCNR04" )
#PlotDiff( fss_cnt , fss_s04 ,  "CONTROL", "SCNR04" )
#quit()

# PLOT ALL 
# CONTROL VS SCNAERIO-01  ( MODE-S T DENIAL ) 
#PlotThresholds("CONTROL", "SCNR01" )

# CONTROL VS SCNAERIO-02  ( AMDAR GEO DENIAL ) 
PlotThresholds("CONTROL", "SCNR02" )

# CONTROL VS SCNAERIO-03  ( MODE-S DENIAL ) 
PlotThresholds("CONTROL", "SCNR03" )

# CONTROL VS SCNAERIO-04  ( AMDAR LOW ALTITUDE ) 
#PlotThresholds("CONTROL", "SCNR04" )


quit()



