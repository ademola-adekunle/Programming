"""
Code for finding the best regression fit of BOD and COD data against the average Y values for a day. This regression
may then be used to estimate the BOD/COD in a biosensor
"""
import numpy as np
from matplotlib import pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.preprocessing import PolynomialFeatures, FunctionTransformer
from sklearn.pipeline import make_pipeline

def AprilPoly(T): #just using the April regression for now as a means to evaluate the Ys
    return 0.016072*(T**3)-1.29312*(T**2)+36.04835*(T)+143.2215

def BOD_reg(input,V_avgs,T_avgs):
    Y_avgs = np.array([])
    Y_avgs = V_avgs/AprilPoly(T_avgs)

    if np.amin(input) < 3: #checks if there is a "0 point" in the given data (<3 considered enough a zero; BOD of 2 taken as a "0" for these fits)
        input = np.append(input,0.1) #adds a "0" point for BOD; 0.1 because it cannot do log calc with a 0 value
        Y_avgs = np.append(Y_avgs,0) #adds a "0" point for Y_avgs

    exp_coefs = np.polyfit(Y_avgs,np.log(input),1,w=np.sqrt(input))
    # BOD = np.exp(exp_coefs[1])*np.exp(exp_coefs[0]*Y_avgs)
    r2_exp = r2_score(input, np.exp(exp_coefs[1])*np.exp(exp_coefs[0]*Y_avgs))

    input = input[:, np.newaxis] #turns the input and Y_avgs array into 2D arrays; required for polynomial regressions
    Y_avgs = Y_avgs[:, np.newaxis]

    for i in range(1,3): #iterates with i = 1, 2
        polyfeats = PolynomialFeatures(degree=i)
        modelo = make_pipeline(polyfeats,LinearRegression())
        modelo.fit(Y_avgs,input)
        poly_pred = modelo.predict(Y_avgs)

        if i == 1:
            r2_lin = r2_score(input,poly_pred) #r2 score for linear fit
            lin_coefs = modelo.steps[1][1].coef_
            lin_inter = modelo.steps[1][1].intercept_
        if i == 2:
            r2_poly2 = r2_score(input,poly_pred) #r2 score for the 2nd order polynomial
            poly2_coefs = modelo.steps[1][1].coef_
            poly2_inter = modelo.steps[1][1].intercept_

    if r2_exp > r2_lin: #if the r2 of the exp is greater than the linear, the exp is initally taken as the best fit
        Is_Negative = False
        for i in [float(j)/100 for j in range(0,100,1)]: #checks if there are any negative values for Y = 0 to 0.99
            if np.exp(exp_coefs[1])*np.exp(exp_coefs[0]*i) < 0:
                Is_Negative = True
                break
        if Is_Negative == True:
            pass
        r2_BOD = r2_exp
        fit_eqn = "BOD = exp(%f)*exp(%f*Y)" % (exp_coefs[1],exp_coefs[0])
        fit_type = 'exp'
    else: #if this is not the case, then the linear is initially taken as the best fit
        Is_Negative = False
        for i in [float(j)/100 for j in range(0,100,1)]: #checks if there are any negative values for Y = 0 to 0.99
            if lin_inter+lin_coefs[0][1]*i < 0:
                Is_Negative = True
                break
        if Is_Negative == True:
            pass #if there are negative values from the linear reg, it not considered a viable fit and is discarded
        else:
            r2_BOD = r2_lin
            fit_eqn = "BOD = %f + %f*Y" % (lin_inter,lin_coefs[0][1])
            fit_type = 'linear'

    if r2_poly2 > max(r2_lin,r2_exp): #checks that the r2 of poly2 is greater than all other r2s
        Is_Negative = False
        for i in [float(j)/100 for j in range(0,100,1)]: #checks if there are any negative values for Y = 0 to 0.99
            if poly2_inter+poly2_coefs[0][1]*i+poly2_coefs[0][2]*(i**2) < 0:
                Is_Negative = True
                break
        if Is_Negative == True:
            pass #if there are negative values from the polynomial, it not considered a viable fit and is discarded
        else:
            r2_BOD = r2_poly2
            fit_eqn = "BOD = %f + %f*Y + %f*Y^2" % (poly2_inter,poly2_coefs[0][1],poly2_coefs[0][2])
            fit_type = 'poly2'

    plt.scatter(Y_avgs,input)
    plt.title('BOD')
    plt.xlabel('Daily Average Y')
    plt.ylabel('Daily Average BOD')
    for i in [float(j)/100 for j in range(0,150,5)]:
        if fit_type == 'exp':
            plt.scatter(i,np.exp(exp_coefs[1])*np.exp(exp_coefs[0]*i),marker=',',s=10,color='red')
        if fit_type == 'linear':
            plt.scatter(i,lin_inter+lin_coefs[0][1]*i,marker=',',s=10,color='red')
        if fit_type == 'poly2':
            plt.scatter(i,poly2_inter+poly2_coefs[0][1]*i+poly2_coefs[0][2]*(i**2),marker=',',s=10,color='red')
    plt.show()

    print('For BOD:')
    print('R^2 is: %f' %r2_BOD)
    print('Fit equation is: %s' %fit_eqn)
    print('Fit type is: %s' %fit_type) #can use fit_type check as a means of knowing which equation to estimate BOD with


def COD_reg(input,V_avgs,T_avgs):
    Y_avgs = np.array([])
    Y_avgs = V_avgs/AprilPoly(T_avgs)

    if np.amin(input) > 10:
        input = np.append(input,0.1) #adds a "0" point for COD; 0.1 because it cannot do log calc with a 0 value
        Y_avgs = np.append(Y_avgs,0) #adds a "0" point for Y_avgs

    exp_coefs = np.polyfit(Y_avgs, np.log(input),1,w=np.sqrt(input))
    # COD = np.exp(exp_coefs[1])*np.exp(exp_coefs[0]*Y_avgs)
    r2_exp = r2_score(input, np.exp(exp_coefs[1])*np.exp(exp_coefs[0]*Y_avgs))

    input = input[:, np.newaxis] #turns the input and Y_avgs array into 2D arrays; required for polynomial regressions
    Y_avgs = Y_avgs[:, np.newaxis]

    for i in range(1,3): #iterates with i = 1, 2
        polyfeats = PolynomialFeatures(degree=i)
        modelo = make_pipeline(polyfeats,LinearRegression())
        modelo.fit(Y_avgs,input)
        poly_pred = modelo.predict(Y_avgs)

        if i == 1:
            r2_lin = r2_score(input,poly_pred) #r2 score for linear fit
            lin_coefs = modelo.steps[1][1].coef_
            lin_inter = modelo.steps[1][1].intercept_
        if i == 2:
            r2_poly2 = r2_score(input,poly_pred) #r2 score for the 2nd order polynomial
            poly2_coefs = modelo.steps[1][1].coef_
            poly2_inter = modelo.steps[1][1].intercept_

    if r2_exp > r2_lin: #if the r2 of the exp is greater than the linear, the exp is initally taken as the best fit
        Is_Negative = False
        for i in [float(j)/100 for j in range(0,100,1)]: #checks if there are any negative values for Y = 0 to 0.99
            if np.exp(exp_coefs[1])*np.exp(exp_coefs[0]*i) < 0:
                Is_Negative = True
                break
        if Is_Negative == True:
            pass
        r2_COD = r2_exp
        fit_eqn = "COD = exp(%f)*exp(%f*Y)" % (exp_coefs[1],exp_coefs[0])
        fit_type = 'exp'
    else: #if this is not the case, then the linear is initially taken as the best fit
        Is_Negative = False
        for i in [float(j)/100 for j in range(0,100,1)]: #checks if there are any negative values for Y = 0 to 0.99
            if lin_inter+lin_coefs[0][1]*i < 0:
                Is_Negative = True
                break
        if Is_Negative == True:
            pass #if there are negative values from the linear reg, it not considered a viable fit and is discarded
        else:
            r2_COD = r2_lin
            fit_eqn = "COD = %f + %f*Y" % (lin_inter,lin_coefs[0][1])
            fit_type = 'linear'

    if r2_poly2 > max(r2_lin,r2_exp): #checks that the r2 of poly2 is greater than all other r2s
        Is_Negative = False
        for i in [float(j)/100 for j in range(0,100,1)]: #checks if there are any negative values for Y = 0 to 0.99
            if poly2_inter+poly2_coefs[0][1]*i+poly2_coefs[0][2]*(i**2) < 0:
                Is_Negative = True
                break
        if Is_Negative == True:
            pass #if there are negative values from the polynomial, it not considered a viable fit and is discarded
        else:
            r2_COD = r2_poly2
            fit_eqn = "COD = %f + %f*Y + %f*Y^2" % (poly2_inter,poly2_coefs[0][1],poly2_coefs[0][2])
            fit_type = 'poly2'

    plt.scatter(Y_avgs,input)
    plt.title('COD')
    plt.xlabel('Daily Average Y')
    plt.ylabel('Daily Average COD')
    for i in [float(j)/100 for j in range(0,150,5)]:
        if fit_type == 'exp':
            plt.scatter(i,np.exp(exp_coefs[1])*np.exp(exp_coefs[0]*i),marker=',',s=10,color='red')
        if fit_type == 'linear':
            plt.scatter(i,lin_inter+lin_coefs[0][1]*i,marker=',',s=10,color='red')
        if fit_type == 'poly2':
            plt.scatter(i,poly2_inter+poly2_coefs[0][1]*i+poly2_coefs[0][2]*(i**2),marker=',',s=10,color='red')
    plt.show()

    print("For COD:")
    print('R^2 is: %f' %r2_COD)
    print('Fit equation is: %s' %fit_eqn)
    print('Fit type is: %s' %fit_type) #can use fit_type check as a means of knowing which equation to estimate BOD with

T_avgs = V_avgs = BOD_input = COD_input = np.array([])

f = open(r"C:\Users\matth\AppData\Local\atom\YTempComp\Data\BOD_COD_Data.txt","r") #text file with 6 daily average temperatures and BODs
line = f.readline()
while line:
    if 'BOD' in line:
        line = f.readline()
        continue
    fields = line.split('\t')
    V_avgs = np.append(V_avgs,float(fields[0].split()[0]))
    T_avgs = np.append(T_avgs,float(fields[1].split()[0]))
    BOD_input = np.append(BOD_input,float(fields[2].split()[0]))
    COD_input = np.append(COD_input,float(fields[3].split()[0]))
    line = f.readline()
f.close()

try:
    BOD_reg(BOD_input,V_avgs,T_avgs)
except:
    print('Error with BOD_reg funciton call')
    pass

try:
    COD_reg(COD_input,V_avgs,T_avgs)
except:
    print('Error with COD_reg funciton call')
    pass
