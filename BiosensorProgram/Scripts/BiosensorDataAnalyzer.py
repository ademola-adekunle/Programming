# -*- coding: utf-8 -*-
import numpy as np
from matplotlib import pyplot as plt
import tkFileDialog

file_path_string = tkFileDialog.askopenfilename()
#f = open(r'C:\Users\adekunlea\Documents\OnlineBiosensor\TempComp_BODEstimation\floatingbiosensordata.txt')
f = open(file_path_string)
line = f.readline()

day = Time = Vmax_Est = Area = OCV_time = Tolerance = Vmin = alpha1 = Vmin_Est = prev_discharge_time = DischargeArea = Temp = np.array([])
Vmax_Est_avg = Area_avg = OCV_time_avg = Tolerance_avg = Vmin_avg = alpha1_avg = Vmin_Est_avg = prev_discharge_time_avg = DischargeArea_avg = Temp_avg = np.array([])
dayplot = daytab = np.array([])
daycount = 0

fields = line.split(' ')
n_cols = 13 #number of columns from which to extract data
headerlist = np.array([]) #list of header titles taken from data file
for i in range(0, n_cols-1):
    headerlist = np.append(headerlist, "%s " % str(fields[i].split()[0]))
header = ''.join(headerlist) #makes header titles into single line for txt file writing

while line:
    fields = line.split(' ') #splits each row into columns
    if 'Date' in line: #if there is "Date" in the row, indicates header row and will be skipped
        line = f.readline() #this will skip the line
        continue
    #hoping to find way to automate this - generate names from headerlist strings, piggyback on n_cols iteration?
    day = np.append(day, str(fields[0].split()[0]))

    if len(day) == 1: #will fill value of daysave on iteration before next if loop
        daysave = fields[0].split()[0]

    if day[len(day)-1] != daysave: #check if day has changed
        Vmax_Est_avg = np.append(Vmax_Est_avg, np.mean(Vmax_Est))
        Area_avg = np.append(Area_avg, np.mean(Area))
        OCV_time_avg = np.append(OCV_time_avg, np.mean(OCV_time))
        Tolerance_avg = np.append(Tolerance_avg, np.mean(Tolerance))
        Vmin_avg = np.append(Vmin_avg, np.mean(Vmin))
        alpha1_avg = np.append(alpha1_avg, np.mean(alpha1))
        Vmin_Est_avg = np.append(Vmin_Est_avg, np.mean(Vmin_Est))
        prev_discharge_time_avg = np.append(prev_discharge_time_avg, np.mean(prev_discharge_time))
        DischargeArea_avg = np.append(DischargeArea_avg, np.mean(DischargeArea))
        Temp_avg = np.append(Temp_avg, np.mean(Temp))
        daytab = np.append(daytab, daysave) #saves day in yyyy-mm-dd format for storage text file
        dayplot = np.append(dayplot, daycount) #saves the day number, used for plotting
        Vmax_Est = Area = OCV_time = Tolerance = Vmin = alpha1 = Vmin_Est = prev_discharge_time = DischargeArea = Temp = np.array([]) #clears array; only keeps values for one day
        daycount += 1

    Time = np.append(Time, str(fields[1].split()[0]))
    Vmax_Est = np.append(Vmax_Est, float(fields[2].split()[0]))
    Area = np.append(OCV_time, float(fields[3].split()[0]))
    OCV_time = np.append(OCV_time, float(fields[4].split()[0]))
    Tolerance = np.append(Tolerance, float(fields[5].split()[0]))
    Vmin = np.append(Vmin, float(fields[6].split()[0]))
    alpha1 = np.append(alpha1, float(fields[7].split()[0]))
    Vmin_Est = np.append(Vmin_Est, float(fields[8].split()[0]))
    prev_discharge_time = np.append(prev_discharge_time, float(fields[9].split()[0]))
    DischargeArea = np.append(DischargeArea, float(fields[10].split()[0]))
    Temp = np.append(Temp, float(fields[11].split()[0]))

    daysave = day[len(day)-1]
    line = f.readline() #reads next line of text file, does above code for each line of the file
f.close()

f = open(r'A:\(T) GPRC\Sensor_at_GPRC_data\May 2020 restart\DailyAvgs.txt',"w")
f.write(header+'\n')
for i in range(0,daycount-1): #increments for the number of days in data
    f.write("%s " % daytab[i])
    f.write("%f " % Vmax_Est_avg[i])
    f.write("%f " % Area_avg[i])
    f.write("%f " % OCV_time_avg[i])
    f.write("%f " % Tolerance_avg[i])
    f.write("%f " % Vmin_avg[i])
    f.write("%f " % alpha1_avg[i])
    f.write("%f " % Vmin_Est_avg[i])
    f.write("%f " % prev_discharge_time_avg[i])
    f.write("%f " % DischargeArea_avg[i])
    f.write("%f\n" % Temp_avg[i])
f.close()


#plotting of daily averages done below
fig, ax1 = plt.subplots()

ax1.set_xlabel('day')
ax1.set_ylabel(u'Average Vmin_Est, mV', color = 'blue')
ax1.plot(dayplot, Vmin_Est_avg, color = 'blue')
ax1.tick_params(axis='y', labelcolor = 'blue')

ax2 = ax1.twinx()
ax2.set_ylabel(u'Average Temp, Â°C', color = 'orange')
ax2.plot(dayplot, Temp_avg, color = 'orange')
ax2.tick_params(axis='y', labelcolor = 'orange')

fig.tight_layout()
plt.show()
