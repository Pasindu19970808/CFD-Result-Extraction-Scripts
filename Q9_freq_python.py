'''
This file produces Q9 exceedance frequencies

Author : Pasindu

'''

import numpy as np
import pickle
import pandas  as pd
import os
import tkinter as tk
from tkinter import filedialog
import math

root = tk.Tk()
root.withdraw()

dest = filedialog.askdirectory()
##changing directory
os.chdir(dest)

with open('Q9Q6flam.p','rb') as j:
    reloaded = pickle.load(j)
    
Q9 = reloaded[0]
Q6 = reloaded[1]
flam = reloaded[2]
#wind speeds
'''
sp = reloaded[3]
wind = reloaded[4]
zone = reloaded[5]
leak_cls = reloaded[6]
'''

sp = 15
wind= 8
zone = 3
leak_cls = 9


#getting the Module File and the ventilation file
#module file
filepath_module = filedialog.askopenfilename()
df_frequency = pd.read_excel(filepath_module, sheet_name = 'Freq')
df_curve = pd.read_excel(filepath_module, sheet_name = 'curve')
#Both are extracted from the Aegis files
filepath_aegis = filedialog.askopenfilename()
df_leaksettings = pd.read_excel(filepath_aegis,sheet_name = 'leak_settings',header = None)
df_windrose = pd.read_excel(filepath_aegis,sheet_name = 'windrose')

windpro = df_windrose.iloc[0:sp+1,0:wind+1]

redu = 0.01
hl_ele = 5
hl_pump = 15
PSML = df_frequency.iloc[0:,1:]

Q9_Q6_flam_freq_exp = np.zeros(shape = (sp,wind,leak_cls,zone,PSML.shape[0]), dtype = object)
Q9_exceed = np.zeros(shape = (PSML.shape[0],zone), dtype = object)


for i in range(PSML.shape[0]):
    print('i value: {}'.format(i))
    for j in range(zone):
        for k in range(leak_cls):
            #c will run from 2 upto 11 (2 to 10)
            for c in range(2,11):
                try:
                    int(df_curve.iloc[k,c-1])
                    status = True
                except:
                    status = False
                #if df_curve.iloc[k,c-1] != np.nan:
                if status is True:
                   for m in range(sp):
                       for n in range(wind):
                           for p in range(1,7):
                               tempq9 = Q9[m,n,k,p-1,j,PSML.iloc[0,0]-1]
                               tempq6 = Q6[m,n,k,p-1,j,PSML.iloc[0,0]-1]
                               tempflam = flam[m,n,k,p-1,j,PSML.iloc[0,0]-1]
                               tempcombined = np.c_[tempq9,tempq6,tempflam]
                               temp4th = (PSML.iloc[i,c]*int(df_curve.iloc[k,c-1])*(windpro.iloc[1+m,1+n]/6))/100
                               tempcombined = np.c_[tempcombined, np.repeat(temp4th,tempcombined.shape[0])]
                               
                               
                               dis_ign = df_leaksettings.iloc[1 + (j+1)*8,32]
                               cont_ign = df_leaksettings.iloc[1 + (j+1)*8,34]
                               
                               tmpval = min(df_curve.iloc[k,10],tempcombined.shape[0])
                               tempcombined = np.c_[tempcombined, np.repeat(0,tempcombined.shape[0])]
                               for t in range(tmpval):
                                   tempcombined[t,4] = tempcombined[t,3]*(tempcombined[t,1]*cont_ign + tempcombined[t,2]*dis_ign)/df_leaksettings.iloc[((j+1)*8)-4,35]
                               
                               dis_ign = df_leaksettings.iloc[(j+1)*8,32]
                               dis_ign = dis_ign + df_leaksettings.iloc[((j+1)*8)-3,32]*redu
                               
                               dis_ign = dis_ign + (df_leaksettings.iloc[((j+1)*8)-6,32] + df_leaksettings.iloc[((j+1)*8)-5,32] + df_leaksettings.iloc[((j+1)*8)-4,32] + df_leaksettings.iloc[((j+1)*8)-2,32])*redu
                               dis_ign = dis_ign + df_leaksettings.iloc[((j+1)*8)-1,32]
                               
                               tlog = t
                               
                               tmpval2 = min(df_curve.iloc[k,11],tempcombined.shape[0])
                               for t in range(tlog + 1, tmpval2 + 1):
                                   cont_ign = cont_ign + math.pow((df_leaksettings.iloc[1 + (j+1)*8,34]*0.5),((1+(t - df_curve.iloc[k,10]))/hl_ele))
                                   cont_ign = cont_ign + math.pow(((df_leaksettings.iloc[((j+1)*8)-6,34] + df_leaksettings.iloc[((j+1)*8)-5,34] + df_leaksettings.iloc[((j+1)*8)-4,34] + df_leaksettings.iloc[((j+1)*8)-2,34])*0.25),((1+(t - df_curve.iloc[k,10]))/hl_pump))
                                   cont_ign = cont_ign + df_leaksettings.iloc[((j+1)*8)-1,34]
                                   try:
                                       tempcombined[t,4] = tempcombined[t,3]*((tempcombined[t,1]*cont_ign) + (tempcombined[t,2]*dis_ign))/(df_leaksettings.iloc[((j+1)*8)-4,35])
                                   except:
                                       tempcombined[t-1,4] = tempcombined[t-1,3]*((tempcombined[t-1,1]*cont_ign) + (tempcombined[t-1,2]*dis_ign))/(df_leaksettings.iloc[((j+1)*8)-4,35])
                                   
                               tlog = t
                               dis_ign = dis_ign - df_leaksettings.iloc[((j+1)*8)-1,32]
                               cont_ign = cont_ign - df_leaksettings.iloc[((j+1)*8)-1,34]
                               
                               tmpval3 = min(300,tempcombined.shape[0])
                               if tmpval3>tlog+1:
                                   for t in range(tlog+1,tmpval3):
                                       cont_ign = df_leaksettings.iloc[1 + (j+1)*8,34]
                                       cont_ign = cont_ign + math.pow((df_leaksettings.iloc[1 + (j+1)*8,34]*0.5),((1+(t - df_curve.iloc[k,10]))/hl_ele))
                                       cont_ign = cont_ign + math.pow(((df_leaksettings.iloc[((j+1)*8)-6,34] + df_leaksettings.iloc[((j+1)*8)-5,34] + df_leaksettings.iloc[((j+1)*8)-4,34] + df_leaksettings.iloc[((j+1)*8)-2,34])*0.25),((1+(t - df_curve.iloc[k,10]))/hl_pump))
                                       tempcombined[t,4] = tempcombined[t,3]*((tempcombined[t,1]*cont_ign) + (tempcombined[t,2]*dis_ign))/(df_leaksettings.iloc[((j+1)*8)-4,35])
                                   
                               if type(Q9_Q6_flam_freq_exp[m,n,k,j,i]) == int:
                                   Q9_Q6_flam_freq_exp[m,n,k,j,i] = tempcombined
                               elif type(Q9_Q6_flam_freq_exp[m,n,k,j,i]) != int:
                                   Q9_Q6_flam_freq_exp[m,n,k,j,i] = \
                                   np.append(Q9_Q6_flam_freq_exp[m,n,k,j,i],tempcombined,axis = 0)
                               if type(Q9_exceed[i,j]) == int:
                                   Q9_exceed[i,j] = np.array([max(tempcombined[:,0]),tempcombined[0,3]])
                               elif type(Q9_exceed[i,j]) != int:
                                   Q9_exceed[i,j] = np.append(Q9_exceed[i,j],np.array([max(tempcombined[:,0]),tempcombined[0,3]]),axis = 0)
                               
savepath =   filedialog.askdirectory()
os.chdir(savepath) 

itemstosave = (Q9_Q6_flam_freq_exp,Q9_exceed,c,cont_ign,df_curve,df_frequency,df_leaksettings,df_windrose,dis_ign,hl_ele,hl_pump,leak_cls,redu,sp,zone)
with open('Q9_exceed.p','rb') as i:
    pickle.dump(itemstosave,i)

i.close()             
                   
                                
    
    
    
    
    
    

