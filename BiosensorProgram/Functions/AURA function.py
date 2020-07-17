"""
AURA = Auto updating regression analysis
This scripts contains a series of functions that altogether helps to take \
takes a retained dataset containing temperatures and voltages \
constructs a polynomial from this training data,
and tries to improve upon the regression based on the last day data from the biosensor.
"""
import numpy as np
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

def FitTrainer():
    Vmin_trained_avg = Temp_trained_avg = day = np.array([])

    f = open(r"C:\Users\matth\AppData\Local\atom\YTempComp\Data\TrainingData.txt","r")
    line = f.readline()

    while line:
        fields = line.split(' ') #splits the row into columns, or "fields"
        #'\t' if columns separated by tabs, ' ' if by spaces
        if 'Date' in line: #if there is "Date" in the row, indicates header row and will be skipped
            line = f.readline() #this will skip the line
            continue
        #hoping to find way to automate this - generate names from headerlist strings, piggyback on n_cols iteration?
        day = np.append(day,str(fields[0].split()[0]))
        Vmin_trained_avg = np.append(Vmin_trained_avg,float(fields[2].split()[0])) #fill Vmin, keeps permanent store of values
        Temp_trained_avg = np.append(Temp_trained_avg,float(fields[1].split()[0])) #fills Temp, keeps permanent store of values
        line = f.readline()
    f.close()
    return Temp_trained_avg, Vmin_trained_avg, day


def TxtRead():
    Vmin = Temp = np.array([])
    Vmin_avg = Temp_avg = np.array([])
    day = daytab = np.array([])

    f = open(r"C:\Users\matth\AppData\Local\atom\YTempComp\Data\QuickData_Ext.txt","r")
    line = f.readline()

    fields = line.split('\t')
    n_cols = 5 #number of columns from which to extract data
    headerlist = np.array([]) #list of header titles taken from data file
    for i in range(n_cols):
        headerlist = np.append(headerlist, "%s " % str(fields[i].split()[0]))
    header = ''.join(headerlist) #makes header titles into single line for txt file writing

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

    #takes last day's average
    Vmin_avg = np.append(Vmin_avg, np.mean(Vmin))
    Temp_avg = np.append(Temp_avg, np.mean(Temp))
    daytab = np.append(daytab, daysave)
    Vmin = Temp = np.array([])
    f.close()
    return daytab, Vmin_avg, Temp_avg


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
    return r2  # when calling function: [0]=r2, [1]=y_poly_pred, etc.


def AURA():
    Temp_trained, Vmin_trained, day_train = FitTrainer()
    day, Vmin, Temp = TxtRead()

    day_split_test = np.fromstring(day[len(day)-1],dtype=int,sep='-') #does day split for last day in TxtFile (should be today's date when the sensor is running properly)
    day_train_split = np.fromstring(day_train[len(day_train)-1],dtype=int,sep='-')
    #takes the day_split for the last day in the trained data set

    V_fit = T_fit = dayplot = day_fit = daysave = np.array([])

    V_fit = np.append(V_fit,Vmin_trained)
    T_fit = np.append(T_fit,Temp_trained)
    day_fit = np.append(day_fit,day_train)

    for i in range(len(Vmin)):
        day_split = np.fromstring(day[i],dtype=int,sep='-') #splits day str into day_split[0] = year, [1] = month, [2] = day

        #if the day has a greater day, month, and year value than the last day of the training data, then it could
        #be a new day. It checks if i's day value is less than
        if day_split[0] < day_train_split[0]: #checks if year is < last day of training data
            continue
        elif day_split[1] < day_train_split[1]: #checks if month is < last day of training data
            continue
        elif day_split[2] <= day_train_split[2]: #checks if day is <= last day of training data
            continue #if it is a lower day value, skips this day for the regression analysis

        if np.fromstring(day[len(day)-1],dtype=int,sep='-')[2] != 1: #if today's date is not the first of a month

            if np.fromstring(day[len(day)-1],dtype=int,sep='-')[2]-1 == day_split[2]: #checks for days that are 1 less than the current date
                if Temp[i] > 55.0: #keeps points with erronious temperature readings from being checked
                    continue
                elif Vmin[i] <= 15.0: #keeps points with erronious voltages from being checked
                    continue
                elif Vmin[i] in V_fit:
                    continue
                elif Temp[i] in T_fit:
                    continue

                daysave = np.append(day_fit,day[i])
                Vsave = np.append(V_fit,Vmin[i])
                Tsave = np.append(T_fit,Temp[i])

                r2_old = polyreg(T_fit,V_fit)
                r2_new = polyreg(Tsave,Vsave)

                if r2_new >= r2_old:
                    T_fit = V_fit = day_fit = np.array([])
                    V_fit = np.append(V_fit,Vsave)
                    T_fit = np.append(T_fit,Tsave)
                    day_fit = np.append(day_fit,daysave)
                    Vsave = Tsave = daysave = np.array([])
                    r2_fit = polyreg(T_fit,V_fit)
                elif Temp[i] > np.amax(T_fit): #to force an expansion of the temperature range
                    T_fit = V_fit = day_fit = np.array([])
                    V_fit = np.append(V_fit,Vsave)
                    T_fit = np.append(T_fit,Tsave)
                    day_fit = np.append(day_fit,daysave)
                    Vsave = Tsave = daysave = np.array([])
                    r2_fit = polyreg(T_fit,V_fit)
                elif Temp[i] < np.amin(T_fit): #to force an expansion of the temperature range
                    T_fit = V_fit = day_fit = np.array([])
                    V_fit = np.append(V_fit,Vsave)
                    T_fit = np.append(T_fit,Tsave)
                    day_fit = np.append(day_fit,daysave)
                    Vsave = Tsave = daysave = np.array([])
                    r2_fit = polyreg(T_fit,V_fit)
                else:
                    Tsave = Vsave = daysave = np.array([])

        elif day_split[2] == 28 or day_split[2] == 29 or day_split[2] == 30 or day_split[2] == 31: #checks if the day is a possible last day of the month
        #PROBABLY BETTER: make the conditional code below it's own function, call it in the AURA funciton for a neater script
            if Temp[i] > 55.0: #keeps points with erronious temperature readings from being checked
                continue
            elif Vmin[i] <= 15.0: #keeps points with erronious voltages from being checked
                continue
            elif Vmin[i] in V_fit:
                continue
            elif Temp[i] in T_fit:
                continue

            daysave = np.append(day_fit,day[i])
            Vsave = np.append(V_fit,Vmin[i])
            Tsave = np.append(T_fit,Temp[i])

            r2_old = polyreg(T_fit,V_fit)
            r2_new = polyreg(Tsave,Vsave)

            if r2_new >= r2_old:
                T_fit = V_fit = day_fit = np.array([])
                V_fit = np.append(V_fit,Vsave)
                T_fit = np.append(T_fit,Tsave)
                day_fit = np.append(day_fit,daysave)
                Vsave = Tsave = daysave = np.array([])
                r2_fit = polyreg(T_fit,V_fit)
            elif Temp[i] > np.amax(T_fit): #to force an expansion of the temperature range
                T_fit = V_fit = day_fit = np.array([])
                V_fit = np.append(V_fit,Vsave)
                T_fit = np.append(T_fit,Tsave)
                day_fit = np.append(day_fit,daysave)
                Vsave = Tsave = daysave = np.array([])
                r2_fit = polyreg(T_fit,V_fit)
            elif Temp[i] < np.amin(T_fit): #to force an expansion of the temperature range
                T_fit = V_fit = day_fit = np.array([])
                V_fit = np.append(V_fit,Vsave)
                T_fit = np.append(T_fit,Tsave)
                day_fit = np.append(day_fit,daysave)
                Vsave = Tsave = daysave = np.array([])
                r2_fit = polyreg(T_fit,V_fit)
            else:
                Tsave = Vsave = daysave = np.array([])


            r2_fit = polyreg(T_fit,V_fit)

        r2_fit = polyreg(T_fit,V_fit)

    r2_fit = polyreg(T_fit,V_fit)

    f = open(r"C:\Users\matth\AppData\Local\atom\YTempComp\Data\TrainingData.txt","w") #overwrites TrainingData file with new fit values
    f.write('Date Temperature Vmin\n')
    for i in range(len(V_fit)):
        f.write('%s ' % day_fit[i])
        f.write('%f ' % T_fit[i])
        f.write('%f\n' % V_fit[i])
    f.close

    return Temp_trained, Vmin_trained, T_fit, V_fit


def Y_calc(T,V):
    denom = poly_A*(T**3) + poly_B*(T**2) + poly_C*T + poly_inter
    Y = V/denom
    return Y


Temp_trained, Vmin_trained, T_fit, V_fit = AURA()


regaxis = plt.subplot()
regaxis.set_ylabel(u'Voltage, mV')
regaxis.set_xlabel(u'Temperature, C')
plt.scatter(Temp_trained,Vmin_trained,marker=",",color='blue',label=u'Training Data')
plt.scatter(T_fit,V_fit,marker=".",color ='green',label=u'Expanded Data')
plt.scatter(0,poly_inter,marker=">",color='red',label=u'Expanded Regression')
for i in range(0,35,1):
    plt.scatter(i,poly_A*(i**3) + poly_B*(i**2) + poly_C*i + poly_inter,marker=">",color='red')
plt.legend(loc='lower right')
plt.show()
