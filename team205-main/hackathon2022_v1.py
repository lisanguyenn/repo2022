# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 18:55:11 2022

@author: COS-FinleyLabUser
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

dataOG=pd.read_csv('ca-oshpd-preventablehospitalizations-county.csv')

#Reorganize Data:
    #x-axis:year and county
    #y-axis:AHRQ Prevention Quality Indicator Description
rowNames=[None]*len(dataOG)
for i in range(len(dataOG)):
    rowNames[i]=dataOG['County'][i]+' '+str(dataOG['Year'][i])
dataReformatted=pd.DataFrame(index=set(rowNames),columns=dataOG['PQIDescription'].unique())
for j in range(len(dataOG)):
    #print(dataOG['ObsRate_ICD9'][j])
    dataReformatted[dataOG['PQIDescription'][j]][dataOG['County'][j]+' '+str(dataOG['Year'][j])]=dataOG['RiskAdjRate_ICD9'][j]



#Generate Correlation Coefficients Between Each Quality Indicator
correlations=pd.DataFrame(index=dataReformatted.columns,columns=dataReformatted.columns)
for k in dataReformatted.columns:
    for m in dataReformatted.columns:
        if k!=m:
            corrDF=(dataReformatted[[k,m]]).dropna()
            
            if len(corrDF)>0:
                X = np.array(corrDF[k]).reshape((-1,1))
                y = np.array(corrDF[m])
                reg = LinearRegression().fit(X, y)
                correlations[k][m]=reg.score(X, y)

