"""
This program can be used to extract temperature and Vmin data from a text file, perform the AURA algorithm on it,
and store the saved dates, Vmins, and temperatures in their own text file. This "training" file can then be used
in other programs as a baseline
"""
import numpy as np
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

def polyreg(x,y):
    global poly_A, poly_B, poly_C, poly_inter
    x = x[:, np.newaxis]
    y = y[:, np.newaxis]

    polyfeats = PolynomialFeatures(degree=3)
    modelo = make_pipeline(polyfeats,LinearRegression())
    modelo.fit(x,y)
    y_poly_pred = modelo.predict(x)

    poly_coefs = modelo.steps[1][1].coef_
    # y = A*(x**3) + B*(x**2) + C*x + poly_inter
    poly_A = poly_coefs[0][3]
    poly_B = poly_coefs[0][2]
    poly_C = poly_coefs[0][1]
    poly_inter = modelo.steps[1][1].intercept_

    r2 = r2_score(y,y_poly_pred) # finds R2 of fit
    return r2 # when calling function: [0]=r2, [1]=y_poly_pred, etc.


Vmin = Temp = np.array([])
Vmin_avg = Temp_avg = np.array([])
Vsave = Tsave =  np.array([])
V_fit = T_fit = np.array([])
V_fit_pred = np.array([])
day = day_fit = daytab = np.array([])
daycount = 0

f = open(r"C:\Users\matth\AppData\Local\atom\YTempComp\Data\QuickData_Ext.txt","r")
line = f.readline()

"""
while line: loop below is only here to test that the AURA code functions, the filling of day, Vmin,
and Temp is done using the TxtRead code in the same way
"""

while line:
    fields = line.split('\t') #splits the row into columns, or "fields"
    #'\t' if columns separated by tabs, ' ' if by spaces
    if 'Date' in line: #if there is "Date" in the row, indicates header row and will be skipped
        line = f.readline() #this will skip the line
        continue
    #hoping to find way to automate this - generate names from headerlist strings, piggyback on n_cols iteration?
    day = np.append(day,str(fields[0].split()[0]))

    if len(day) == 1: #will fill value of daysave on iteration before next if loop
        daysave = fields[0].split()[0]

    if day[len(day)-1] != daysave: #check if day has changed
        Vmin_avg = np.append(Vmin_avg, np.mean(Vmin))
        Temp_avg = np.append(Temp_avg, np.mean(Temp))
        daytab = np.append(daytab, daysave)
        Vmin = Temp = np.array([])

    Vmin = np.append(Vmin,float(fields[4].split()[0]))
    Temp = np.append(Temp,float(fields[3].split()[0]))

    daysave = day[len(day)-1]
    line = f.readline()
f.close()


for i in range(len(Vmin_avg)):
    if Temp_avg[i] > 55.0: #keeps points with erronious temperature readings from being checked
        continue
    elif Vmin_avg[i] <= 15.0: #keeps points with erronious voltages from being checked
        continue
    elif Vmin_avg[i] in V_fit:
        continue
    elif Temp_avg[i] in T_fit:
        continue

    if i == 0: #will fill value of daysave on iteration before next if loop
        day_fit = np.append(day_fit,daytab[0])
        V_fit = np.append(V_fit,Vmin_avg[0])
        T_fit = np.append(T_fit,Temp_avg[0])
        continue
    elif i == 1:
        day_fit = np.append(day_fit,daytab[i])
        V_fit = np.append(V_fit,Vmin_avg[i])
        T_fit = np.append(T_fit,Temp_avg[i])
        continue

    Vsave = np.append(V_fit,Vmin_avg[i])
    Tsave = np.append(T_fit,Temp_avg[i])

    r2_old = polyreg(T_fit,V_fit)
    r2_new = polyreg(Tsave,Vsave)


    if r2_new >= r2_old:
        T_fit = V_fit = np.array([])
        day_fit = np.append(day_fit,daytab[i])
        V_fit = np.append(V_fit,Vsave)
        T_fit = np.append(T_fit,Tsave)
        Vsave = Tsave = np.array([])
        r2_fit = polyreg(T_fit,V_fit)
    elif Temp_avg[i] > np.amax(T_fit): #to force an expansion of the temperature range
        T_fit = V_fit = np.array([])
        day_fit = np.append(day_fit,daytab[i])
        V_fit = np.append(V_fit,Vsave)
        T_fit = np.append(T_fit,Tsave)
        Vsave = Tsave = np.array([])
        r2_fit = polyreg(T_fit,V_fit)
    elif Temp_avg[i] < np.amin(T_fit): #to force an expansion of the temperature range
        T_fit = V_fit = np.array([])
        day_fit = np.append(day_fit,daytab[i])
        V_fit = np.append(V_fit,Vsave)
        T_fit = np.append(T_fit,Tsave)
        Vsave = Tsave = np.array([])
        r2_fit = polyreg(T_fit,V_fit)
    else:
        Tsave = Vsave = np.array([])
        r2_fit = polyreg(T_fit,V_fit)


regaxis = plt.subplot()
regaxis.set_ylabel(u'Voltage, mV')
regaxis.set_xlabel(u'Temperature, °C')
plt.scatter(T_fit,V_fit,s=10,label=u'Retained Data')
plt.scatter(0,poly_inter,s=10,marker=">",color ='red',label=u'AURA Regression')
for i in range(0,35,1):
    plt.scatter(i,poly_A*(i**3) + poly_B*(i**2) + poly_C*i + poly_inter,s=10,marker=">",color='red')
plt.legend(loc='lower right')
plt.show()

f = open(r"C:\Users\matth\AppData\Local\atom\YTempComp\Data\TrainingData.txt","w")
f.write('Date Temperature Vmin\n')
for i in range(len(V_fit)):
    f.write('%s ' % day_fit[i])
    f.write('%f ' % T_fit[i])
    f.write('%f\n' % V_fit[i])
f.close
