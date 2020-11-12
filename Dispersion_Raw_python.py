import tkinter as tk
from tkinter import filedialog
import pandas as pd 
import numpy as np
from scipy.interpolate import splev,splrep
import h5py
import os


root = tk.Tk()
root.lift()
root.attributes('-topmost',True)
root.after_idle(root.attributes,'-topmost',False)
root.withdraw()

filepath_dispersion = filedialog.askopenfilename()

try:
    dfleak = pd.read_excel(filepath_dispersion, sheet_name = 'leak_scenarios', header = None)
    dfparameters = pd.read_excel(filepath_dispersion, sheet_name = 'Parameter_Control', header = None)
except:
    print('Select Files Please')



monlist = np.empty(shape = (26,1), dtype = float)

for i in range(0,20):
    monlist[i] = (i+1)/10
    
extra_monlist = [2.5,3,3.5,4,4.5,5]
monlist[20:] = np.array(extra_monlist).reshape(6,1)

#selects result folder 
#dest is destination where the MON files are
dest = filedialog.askdirectory()
filepath_ventilation = filedialog.askopenfilename()

dfventilation = pd.read_excel(filepath_ventilation, sheet_name = 'summary_FPSO', header = None)

#ACH x axis indices correspond to wind speed 
#ACH 
ACH_temp = dfventilation.iloc[3:20,0:17]
ACH_temp.reset_index(drop = True, inplace = True)
ACH = ACH_temp.to_numpy()
print('hi')

#making the Region to nummeric IDs
regions = dfleak.iloc[1:,1].unique().tolist()

region_count = 1
for region in regions:
    dfleak.loc[:,1][dfleak.loc[:,1] == region] = region_count
    region_count += 1




loc = int(dfleak.loc[1:,1].max())
leak_cls = int(dfleak.iloc[:,39].max())
wind = int(sum(~(ACH_temp.iloc[0,:].isna())))
sp = int(sum(~(ACH_temp.iloc[:,0].isna())))
zone = int(sum((~(dfparameters.iloc[5:,2:5].isna())).sum())/6)


dir_no_dictionary = {'+X':1,'-X':2,'+Y':3,'-Y':4,'+Z':5,'-Z':6}

#making the multidimensional arrays for Q9,Q6 and flam
#as compared to matlab, the indexes of each position is in the otherway round
Q9 = np.zeros(shape = (sp,wind,leak_cls,6,zone,loc), dtype = object)
Q6 = np.zeros(shape = (sp,wind,leak_cls,6,zone,loc), dtype = object)
flam = np.zeros(shape = (sp,wind,leak_cls,6,zone,loc), dtype = object)

for i in range(1, dfleak.shape[0]):
    if pd.isna(dfleak.iloc[i,0]) is False:
        for j in range(zone):
            for k in range(sp):
                for m in range(wind):
                    '''
                    #find relevant MON file based on ACH
                    '''
                    #wind_speed_idx = ACH[ACH.iloc[:,0] == dfleak.iloc[1,5]].index[0]
                    #wind_direction_idx = ACH.iloc[0,:][ACH.iloc[0,:] == dfleak.iloc[i,6]].index[0]
                    
                    wind_speed_idx = np.where(ACH[:,0] == dfleak.iloc[i,5])[0][0]
                    wind_direction_idx = np.where(ACH[0:] == dfleak.iloc[i,6])[1][0]
                    if ACH[wind_speed_idx,wind_direction_idx]/ACH[1 + k, 1 + m] > 4.75:
                        mon = 50
                    else:
                        for n in range(monlist.shape[0] - 1):
                            if ACH[wind_speed_idx,wind_direction_idx]/ACH[1 + k, 1 + m] <= ((monlist[n] + monlist[n + 1])/2)[0]:
                                mon = 10*monlist[n][0]
                                break
                    
                    
                    filepath = dest + '/rt' + str(dfleak.iloc[i,0]) + '.mon.' + str(j + 1) + '%2d'%(mon)
                    tline = open(filepath,'r').readlines()
                    #Getting the first instance where the dispersion starts to occur in the MON file
                    idx_no_hash = [n[0] for n in enumerate(tline) if n[1][0] != '#'][0]
                    temp_a = [i.split() for i in tline[idx_no_hash:]]
                    #make the mon data into a matrix
                    matrix_a = np.transpose(np.array(temp_a))[:,1:]
                    
                    #interpolation models
                    interp_modelq9 = splrep(matrix_a[0,:],matrix_a[-1,:])
                    interp_modelq6 = splrep(matrix_a[0,:],matrix_a[-4,:])
                    interp_modelflam = splrep(matrix_a[0,:],matrix_a[-10,:])
                    
                    
                    open_side = dfleak.iloc[i,26]
                    dir_no = dir_no_dictionary[open_side]
                    
                    
                    start_time = int(dfleak.iloc[i,27])
                    end_time = int(min(float(matrix_a[0,-1]),float(dfleak.iloc[i,27]) + float(dfleak.iloc[i,28])))
                    
                    for t in range(start_time + 1, end_time + 1):
                        
                        #q9 value at the required time instance
                        q9_val = float(splev(t,interp_modelq9))
                        
                        if t >= (start_time + 60) and q9_val <= 0:
                            break
                        q9_val = float(splev(t,interp_modelq9))
                        q6_val = float(splev(t,interp_modelq6))
                        flam_val = float(splev(t,interp_modelflam))
                        #Q9
                        if Q9[k,m,int(dfleak.iloc[i,39]),dir_no - 1,j,dfleak.iloc[i,1]] == 0:
                            Q9[k,m,int(dfleak.iloc[i,39]),dir_no - 1,j,dfleak.iloc[i,1]] = np.array(q9_val)
                        elif Q9[k,m,int(dfleak.iloc[i,39]),dir_no - 1,j,dfleak.iloc[i,1]] != 0:
                            Q9[k,m,int(dfleak.iloc[i,39]),dir_no - 1,j,dfleak.iloc[i,1]] = \
                            np.append(Q9[k,m,int(dfleak.iloc[i,39]),dir_no - 1,j,dfleak.iloc[i,1]],q9_val)
                        #Q6   
                        if Q6[k,m,int(dfleak.iloc[i,39]),dir_no - 1,j,dfleak.iloc[i,1]] == 0:
                            Q6[k,m,int(dfleak.iloc[i,39]),dir_no - 1,j,dfleak.iloc[i,1]] = np.array(q6_val)
                        elif Q6[k,m,int(dfleak.iloc[i,39]),dir_no - 1,j,dfleak.iloc[i,1]] != 0:
                            Q6[k,m,int(dfleak.iloc[i,39]),dir_no - 1,j,dfleak.iloc[i,1]] = \
                            np.append(Q6[k,m,int(dfleak.iloc[i,39]),dir_no - 1,j,dfleak.iloc[i,1]],q6_val)
                        #flam    
                        if flam[k,m,int(dfleak.iloc[i,39]),dir_no - 1,j,dfleak.iloc[i,1]] == 0:
                            flam[k,m,int(dfleak.iloc[i,39]),dir_no - 1,j,dfleak.iloc[i,1]] = np.array(flam_val)
                        elif flam[k,m,int(dfleak.iloc[i,39]),dir_no - 1,j,dfleak.iloc[i,1]] != 0:
                            flam[k,m,int(dfleak.iloc[i,39]),dir_no - 1,j,dfleak.iloc[i,1]] = \
                            np.append(flam[k,m,int(dfleak.iloc[i,39]),dir_no - 1,j,dfleak.iloc[i,1]],flam_val)
                        
savepath =   filedialog.askdirectory()
os.chdir(savepath)                      
hf = h5py.File('q9q6flam.h5','w')
hf.create_dataset('Q9',data = Q9)
hf.create_dataset('Q6',data = Q6)
hf.create_dataset('Flam',data = flam)

hf.close()



                            
                        
                   
                    
                    
                    

        
   
        
    


