#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 22:47:07 2022

@author: kellyngochoang
@author: sarahnguyen
"""

import os 
import pandas as pd 
import numpy as np 
from scipy import stats 
import matplotlib.pyplot as plt 

path = r"/Users/nhungochoang/School/CS4830/Project2/data-set/arrivals" 

dirList = os.listdir(path)

interarrivalTimes = [] 

for file in dirList: 

    fileParts = file.split('.') 

    name = fileParts[0] 
    ext = fileParts[1] 


    fullFileName = path + r"/" + file 


    if name.find('arrival') == 0: 

        if ext == 'xlsx': 
            tbl = pd.read_excel(fullFileName) 
            tbl['Time'] = pd.to_datetime(tbl['Time'], format="%H:%M:%S") 


        elif ext == 'csv': 
            tbl = pd.read_csv(fullFileName) 
            tbl['Time'] = pd.to_datetime(tbl['Time']) 


        tbl['delta'] = (tbl['Time']-tbl['Time'].shift()).fillna(pd.Timedelta(0))

        tbl['elapsedTime'] = tbl['delta'].apply(lambda x: x  / np.timedelta64(1,'s')).astype('int64') % (24*60) 


        print(name) 

        print(tbl) 

        interarrivalTimes += tbl['elapsedTime'].to_list() 

sampleData = interarrivalTimes

#summary statistics 

#describe calculates statistics 

sampleSize, min_max, sampleMean, sampleVariance, skew, kurtosis= stats.describe(sampleData) 

print(f'mean {sampleMean:0.3f}  variance: {sampleVariance:0.3f} range: ({min_max[0]:f}, {min_max[1]:f})') 
 

#generating plots of data 

#have every bin to have at least 5 points 

binSize = [5, 10, 20, 50, 100] 

fig, axs = plt.subplots(len(binSize), 1) 

plt.subplots_adjust(hspace=.5) 

 

titleLabel = 'Number of bins: ' + ' '.join([str(bs) for bs in binSize]) 

                                  

fig.suptitle(titleLabel) 

for idx, ax in enumerate(axs): 

    ax.hist(sampleData, bins=binSize[idx]) 

 

plt.show() 

# check chi square goodness of fit of an exponential distribution 

# observed 

numBins = 30 

binEdges = np.linspace(0.0, np.max(sampleData), numBins) 

observed, _ = np.histogram(sampleData, bins=binEdges) 

 

# MLE 

fit_loc, fit_beta = stats.expon.fit(sampleData, floc=0) 
rv = stats.expon.rvs(fit_beta, 1)
print('rv = ', rv) 

# expected 

expectedProb = stats.expon.cdf(binEdges, scale=fit_beta) 

expectedProb[-1] += 1.0 - np.sum(np.diff(expectedProb)) 

expected = sampleSize * np.diff(expectedProb) 

 

binMidPt = (binEdges[1:] + binEdges[:-1]) / 2 

plt.hist(sampleData, bins=binEdges, label='Observed') 

plt.plot(binMidPt, expected, 'or-', label='Expected') 

plt.plot(binMidPt, observed, 'oy-', label='Observed') 

plt.legend()  

chiSq, pValue = stats.chisquare(f_obs=observed, f_exp=expected) 

print(f'ChiSquare Statistic {chiSq:0.3f} P value {pValue:0.3f}') 
print('H0: (null hypothesis) Sample data follows the hypothesized distribution.') 
print('H1: (alternative hypothesis) Sample data does not follow a hypothesized distribution.') 

if pValue >= 0.05: 

    print('we can not reject the null hypothesis') 

else: 

    print('we reject the null hypothesis') 

     
# generate exponential distributed data  

sampleSize, min_max, sampleMean, sampleVariance, skew, kurtosis= stats.describe(sampleData) 

sampleScale = sampleMean  # mean 

sampleSize = len(sampleData) 

 

sortedData = np.sort(sampleData) 

 

count = np.ones(sampleSize) 

count = np.cumsum(count) / sampleSize 

 

cdf = stats.expon.cdf(sortedData, scale=sampleScale) 

 

plt.figure() 

plt.plot(sortedData, count, 'b', label='sample data') 

plt.plot(sortedData, cdf, 'r', label='theoretical data') 

plt.legend() 

plt.xlabel('data sample') 

plt.ylabel('cummulative frequency') 

 

KS_stat, p_value = stats.ks_2samp(count, cdf) 

 

print('KS statistic', KS_stat) 

print('p value', p_value) 

 

print('H0: (null hypothesis) Sample data comes from same distribution as theoretical distribution.') 

print('H1: (alternative hypothesis) Sample data does not comes from same distribution as theoretical distribution.') 

 

if p_value >= 0.05: 

    print('we can not reject the null hypothesis') 

else: 

    print('we reject the null hypothesis') 