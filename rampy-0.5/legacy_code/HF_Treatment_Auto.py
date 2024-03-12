# -*- coding: utf-8 -*-
"""
Created on Wed Jul  9 17:52 2014
Modified 16 nov 2014 for "auto" treatment

@author: charleslelosq
Carnegie Institution for Science

This script is used to subtract the second order of diamond
in the 2000-4000 cm-1 frequency range of Raman spectra from Diamond Anvil Cell
experiments.

Put it anywhere, you need however to properly set up the path of /lib-charles 
and /lib-charles/gcvspl/ libraries (as well as numpy, scipy, matplotlib, 
and Tkinter that usually come with any python distribution)
"""

import sys
sys.path.append("/Users/closq/Google Drive/RamPy/lib-charles/")
sys.path.append("/Users/closq/Google Drive/RamPy/lib-charles/gcvspl/")

import numpy as np
import scipy
import matplotlib

import matplotlib.gridspec as gridspec
from pylab import *
from scipy import interpolate
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
# to fit spectra we use the lmfit software of Matt Newville, CARS, university of Chicago, available on the web
from lmfit import minimize, Minimizer, Parameters, Parameter, report_fit, fit_report


from Tkinter import *
import tkMessageBox
from tkFileDialog import askopenfilename
     
# Home made modules
from spectratools import *

###############################################################################
######## HERE ARE DEFINED THE BONDARIES / BIRS USED IN THE CODE ###############
###############################################################################
# SAME FOR ALL SPECTRA
# DEFINED HERE TO SIMPLIFY THE USE OF THIS CODE

x = np.arange(2035,3795,0.2) # X scale for correction of X deviations, take care to put correct bondaries

# Background Interpolation Regions for baseline subtraction
birDiamond = np.array([(2035,2050),(2730,3795)]) # BIR diamond
smofd = 0.07 # smoothing factor
birSample = np.array([(2035,2050),(2730,2900),(3000,3030),(3770,3795)]) # BIR sample: typical 2860-2950 for melt; For fluid, may add (3000,3100)
btype = 'gcvspline' # 'poly' or 'gcvspline' for the sample
smofs = 0.07 # smoothing factor / poly factor

#### DO YOU NEED A FILTER BEFORE ADJUSTING DIAMOND/SAMPLE SIGNALS???
filterSwitch1 = 0 #0 to switch off, 1 to turn on
cutfq = np.array([0.05]) # cutoff Frequency
filter1type = 'low' # 'low', 'high', 'bandstop', 'bandpass', change cutfq as a function of the filter type (see doc)

#### HERE CHOOSE HOW YOU REMOVE THE DIAMOND AND THE PARAMETERS
method = 2
if method == 1:
    # Method 1: good in most cases => we find peak maxima for x shift correction and we fit a small portion for diamond intensity adjustment
    #bmaxd = np.array([(2660,2688)]) # 2400 2475 or 2645, 2680 (sharper peak) Here is were the program have to search for the frequency of the peak that is used for x calibration
    bmaxd = np.array([(2400,2600)])
    dconvfit = np.array([(2195,2370)]) # Here is were we calculate the conversion factor between the diamond and sample spectra. Unless you know what you are doing, DO NOT MODIFY!
elif method ==2:
    # Method 2: best for HT spectra and if no signal is expected below 2450 cm-1 => we correct for x shifts AND diamond intensity at the same time by adjusting the low frequency part of the 2nd order diamond. 
    dconvfit = np.array([(2130,2450)])  
else:
    print('You did not choose method 1 or 2, invalid number, change that in the code!')
    exit()

#### DO YOU NEED A SECOND FILTER BEFORE AREA CALCULATION, IN CASE OF "INTERFRINGEANCE" BANDS FOR INSTANCE?
filterSwitch2 = 0 #0 to switch off, 1 to turn on
cutfq2 = np.array([0.013]) # cutoff Frequency
filter2type = 'low' # 'low', 'high', 'bandstop', 'bandpass', change cutfq2 as a function of the filter type (see doc)

# Here are the bondaries for the calculation of the areas. Please CHANGE THEM AS A FUNCTION OF YOUR DATA!!!!!!
lb = 2200 # Lower Bondary
hb = 3800 # Upper Bondary
mb1 = 3026 # Intermediate 1 (end of OD peak) good for fluid at 2860 (D2 doublet near 2900 to avoid), for melt at 2800, depends on temperature
mb2 = 3026 # Intermediate 2 (beginning of OH peak) set as mb1 for melt, but for fluid at 3000 it allows avoiding the D2 doublet near 2900 cm-1

# In case some of the signal is in the negative portion at the end, you want to activate that:
birFinalSwitch = 0 # If 0, deactivated, if 1, activated
birFinal = np.array([(2100,2290),(2760,2780),(3800,3850)])
basetype = 'poly'
smofu = 3 #final smo/poly factor

#### DATA PATHS AND INPUT
tkMessageBox.showinfo(
            "Open ",
            "Please open the list of spectra")

Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
samplename = askopenfilename() # show an "Open" dialog box and return the path to the selected file

pathbeg = samplename[0:samplename.rfind('/')] # The path where the raw and treated folders are 

# we import the information in an array, skipping the first line
dataliste = np.genfromtxt(samplename,dtype = 'string',delimiter = '\t', skip_header=0,skip_footer=0)
pathdiamond = (dataliste[:,0])
pathsample = (dataliste[:,1])
pathsave = (dataliste[:,2])

output = np.zeros((len(pathdiamond),2))


for i in range(len(pathdiamond)): # We loop over in dataliste

    rawsample = np.genfromtxt(pathbeg+pathsample[i],skip_header=20, skip_footer=43) # Skipping lines from JASCO files
    diamond = np.genfromtxt(pathbeg+pathdiamond[i],skip_header=20, skip_footer=43)

    #### SUBTRACTION OF THE DIAMOND SIGNAL FROM SAMPLE SPECTRA
    # WE INTERPOLATE SPECTRA WITH SAME X in case its is not the case
    tck = interpolate.splrep(diamond[:,0],diamond[:,1],s=0) 
    rawdiamond = np.zeros(shape(rawsample))
    rawdiamond[:,1] = interpolate.splev(rawsample[:,0],tck,der=0) # interp with x from rawsample
    rawdiamond[:,0] = rawsample[:,0]

    # If needed to suppress high-frequency oscillations, here a filter:
    if filterSwitch1 == 1:
        rawsample = spectrafilter(rawsample,filter1type,cutfq,1,np.array([1]))
        rawdiamond = spectrafilter(rawdiamond,filter1type,cutfq,1,np.array([1]))

    # FOR GCVSPL: errors = sqrt(y), directly calculated in spectratools.linbaseline
    corrdiamond, baselineD, coeffsD = linbaseline(rawdiamond,birDiamond,'gcvspline',smofd) # SUbtract a  baseline below Diamond spectra  
    corrsample, baselineS, coeffsS = linbaseline(rawsample,birSample,btype,smofs)   # SUbtract a  baseline below Sample spectra
    
    #### Correction of X shifts and diamond intensity    
    if method == 1:
        #### CORRECTION OF ANY X SHIFTS    
    
        # We look at the Raman shift of the maximum intensity second order diamond peak near 2444-2475 cm-1
        # If needed please use the 2160 cm-1 peak and change values below!!!!! (see intro)
        # We search the maximum values in the spectra
        maxDiamond = corrdiamond[np.where((corrdiamond[:,0] > bmaxd[0,0]) & (corrdiamond[:,0] < bmaxd[0,1]))] 
        maxD = np.max(maxDiamond[:,1])
        maxSample = corrsample[np.where((corrsample[:,0] > bmaxd[0,0]) & (corrsample[:,0] < bmaxd[0,1]))]
        maxS = np.max(maxSample[:,1])
        # We retrieve the corresponding x value
        bebe = corrsample[np.where((corrsample[:,1]==maxS))]
        cece = corrdiamond[np.where((corrdiamond[:,1]==maxD))]
        # we calculate the correction factor
        corrx = bebe[:,0] - cece[:,0]
        # To apply the correction for x shift, we need to interpolate to create new datasets
        tck = interpolate.splrep(corrsample[:,0],corrsample[:,1],s=0)
        y = interpolate.splev(x,tck,der=0) # sample spectrum
        tck = interpolate.splrep(corrdiamond[:,0]+corrx,corrdiamond[:,1],s=0)
        y2 = interpolate.splev(x,tck,der=0) # diamond spectrum
    
        # The following rows contain the spectra corrected from x shifts
        diamondfinal = np.zeros((len(x),2))
        samplefinal = np.zeros((len(x),2))
        diamondfinal[:,0] = x
        samplefinal[:,0] = x
        diamondfinal[:,1] = y2
        samplefinal[:,1] = y
    
        ##### CALCULATION OF THE INTENSITY CONVERSION FACTOR DIAMOND-SAMPLE
    
        # We use least-square fit to find this conversion factor, between 2100 and 2360 cm-1
        # Their is few to no expected D2O-OD signals in this region, and two nice peak from diamond
        DiamondtoFit = diamondfinal[np.where((diamondfinal[:,0]> dconvfit[0,0]) & (diamondfinal[:,0] < dconvfit[0,1]))]
        SampletoFit =  samplefinal[np.where((samplefinal[:,0]> dconvfit[0,0]) & (samplefinal[:,0] < dconvfit[0,1]))]
        corrY, cov_out = curve_fit(fun, DiamondtoFit[:,1], SampletoFit[:,1]) #Fitting the peak
        
        # we record anorther spectra for diamond (normalized) and also for sample (subtracted from diamond and
        # area normalized)
        diamondfinal[:,1] = fun(diamondfinal[:,1],corrY[0]) # We correct the diamond spectra  
        sampleultimateINT = np.zeros(shape(samplefinal)) # we create the output array containing the good sample spectrum
        sampleultimateINT[:,0] = samplefinal[:,0] 
        sampleultimateINT[:,1] = samplefinal[:,1] - diamondfinal[:,1] #We subtract the second order diamond from sample
    
    elif method == 2:
        
        #######################################################################
        # Here we put some objective function we need
        def residual(pars, spforcorr, sptarget=None):
            # unpack parameters:
            #  extract .value attribute for each parameter
            xs = pars['xshift'].value
            yx = pars['yshift'].value
            yx2 = pars['yshiftcarr'].value
            spcorr = np.zeros((shape(spforcorr)))
        
            # we need to resample the spectra to compare them
            tck = interpolate.splrep(spforcorr[:,0]-xs,spforcorr[:,1]*yx+spforcorr[:,1]**2*yx2,s=0)
            spcorr[:,0] = spforcorr[:,0]    
            spcorr[:,1] = interpolate.splev(spcorr[:,0],tck,der=0)
            
            if sptarget is None: #in such case we return the corrected spectrum
                return spcorr
            return (spcorr[:,1] - sptarget[:,1])
        #######################################################################        
        
        # Now we choose the portion of spectra to fit
        DiamondtoFit = corrdiamond[np.where((corrdiamond[:,0]> dconvfit[0,0]) & (corrdiamond[:,0] < dconvfit[0,1]))]
        SampletoFit =  corrsample[np.where((corrsample[:,0]> dconvfit[0,0]) & (corrsample[:,0] < dconvfit[0,1]))]
       
        # Now we enter the model parameters
        params = Parameters()
        params.add_many(('xshift',   1,   True,  -15,      15,  None),
                        ('yshift',   1e-1,   True, None,    None,  None),
                        ('yshiftcarr',   1e-5,   True, None,    None,  None))
            
        # Now we chose the algorithm and run the optimization
        algorithm = "leastsq"
        result = minimize(residual, params,method = algorithm, args=(DiamondtoFit, SampletoFit))
    
        cds = residual(params,corrdiamond)    
        
        # To apply the correction for x shift, we need to interpolate to create new datasets
        tck = interpolate.splrep(corrsample[:,0],corrsample[:,1],s=0)
        tck2 = interpolate.splrep(cds[:,0],cds[:,1],s=0)
        
        # The following rows contain the spectra corrected from x and y shifts
        diamondfinal = np.zeros((len(x),2))
        samplefinal = np.zeros((len(x),2))
        diamondfinal[:,0] = x
        samplefinal[:,0] = x
        diamondfinal[:,1] = interpolate.splev(x,tck2,der=0)
        samplefinal[:,1] = interpolate.splev(x,tck,der=0)
        
        #and we subtract the second order diamond from the sample spectrum
        sampleultimateINT = np.zeros(shape(samplefinal)) # we create the output array containing the good sample spectrum
        sampleultimateINT[:,0] = samplefinal[:,0] 
        sampleultimateINT[:,1] = samplefinal[:,1] - diamondfinal[:,1] #We subtract the second order diamond from sample
            
    # Last correction, if their is a portion of the "ultimate" signal in the negative domain:
    if birFinalSwitch == 0:
        sampleultimate = sampleultimateINT
        if filterSwitch2 == 1:
            sampleultimate = spectrafilter(sampleultimate,filter2type,cutfq2,1,np.array([1]))
    else:
        if filterSwitch2 == 1:
            sampleultimateINT2 = spectrafilter(sampleultimateINT,filter2type,cutfq2,1,np.array([1]))
            sampleultimate, baselineU, coeffsU = linbaseline(sampleultimateINT2,birFinal,basetype,smofu)
        else:
            sampleultimate, baselineU, coeffsU = linbaseline(sampleultimateINT,birFinal,basetype,smofu)
    
    # Errors as sqrt(corrected y)
    # would be relatively higher than initial errors and may take a part of the correction process into account
    ese = np.zeros(np.shape(sampleultimate))
    ese[:,0] = sampleultimate[:,0]
    ese[:,1] = np.sqrt(abs(samplefinal[:,1]))/samplefinal[:,1]*sampleultimate[:,1]

    # Now we can do whatever we want
    # In the following we calculate the ratio between the D and H peaks
    # Values have to be adjusted manally in the following, because the value that separate OH and OD signals
    # varies! SEE INTRODUCTION... No automatic process also to find it (as for instance the minimum), because the D2 signal
    # mess up the things here for such a process... 
    peakOD = sampleultimate[np.where((sampleultimate[:,0]> lb) & (sampleultimate[:,0] < mb1))]
    peakOH = sampleultimate[np.where((sampleultimate[:,0]> mb2) & (sampleultimate[:,0] < hb))]
    esepeakOD = ese[np.where((ese[:,0]> lb) & (ese[:,0] < mb1))]
    esepeakOH = ese[np.where((ese[:,0]> mb2) & (ese[:,0] < hb))]
    AireOD = np.trapz(peakOD[:,1],peakOD[:,0])
    AireOH = np.trapz(peakOH[:,1],peakOH[:,0])
    eseAireOD = np.trapz(esepeakOD[:,1],esepeakOD[:,0])
    eseAireOH = np.trapz(esepeakOH[:,1],esepeakOH[:,0])
    ratioDH = AireOD/AireOH
    eseratioDH = np.sqrt((1/AireOH)**2*eseAireOD**2+((AireOD-AireOH)/(AireOH**2))**2*eseAireOH**2)
    output[i,0] = ratioDH
    output[i,1] = eseratioDH
    
    figure(figsize=(10,6))
    gs = matplotlib.gridspec.GridSpec(1, 3)
    ax1 = plt.subplot(gs[0])
    ax2 = plt.subplot(gs[1])
    ax3 = plt.subplot(gs[2])

    ax1.plot(rawsample[:,0],rawsample[:,1],'k-')
    ax1.plot(rawdiamond[:,0],rawdiamond[:,1],'r-')
    ax1.plot(baselineD[:,0],baselineD[:,1],'b--')
    ax1.plot(baselineS[:,0],baselineS[:,1],'b--')
    
    ax2.plot(corrsample[:,0],corrsample[:,1],'k-')
    ax2.plot(corrdiamond[:,0],corrdiamond[:,1],'r-')
    ax2.plot(diamondfinal[:,0],diamondfinal[:,1],'g-')
    
    # Intensity is normalized for representation
    ax3.plot(sampleultimateINT[:,0],sampleultimateINT[:,1]/amax(peakOD[:,1])*100 ,'k-')
    ax3.plot(sampleultimate[:,0],sampleultimate[:,1]/amax(peakOD[:,1])*100 ,'r-')
    if birFinalSwitch == 1:
        ax3.plot(baselineU[:,0],baselineU[:,1]/amax(peakOD[:,1])*100 ,'g-')
    
    # Limits
    ax1.set_xlim(2000,3850)
    ax2.set_xlim(2000,3850)
    ax3.set_xlim(2000,3850)
    
    # we search the lower limit for ax2 and ax3 but the higher free.
    ax1.set_ylim(0,40000)
    ax2.set_ylim(np.amin(corrdiamond[:,1])-5/100*np.amin(corrdiamond[:,1]),)#np.amax(corrdiamond[:,1])+10/100*np.amax(corrdiamond[:,1])
    ax3.set_ylim(np.amin(sampleultimate[:,1]/amax(peakOD[:,1])*100)-5/100*np.amin(sampleultimate[:,1]/amax(peakOD[:,1])*100),) #np.amax(sampleultimate[:,1]/amax(peakOD[:,1])*100)+10/100*np.amax(sampleultimate[:,1]/amax(peakOD[:,1])*100)
    
    # Labels:
    ax1.set_ylabel("Intensity, a. u.", fontsize = 18, fontweight = "bold")
    ax2.set_xlabel("Raman shift, cm$^{-1}$",fontsize = 18,fontweight = "bold")
    
    plt.tight_layout()

    #### DATA and FIGURE OUTPUT
    np.savetxt(pathbeg+pathsave[i],sampleultimate)
    name = pathsave[i]
    namefig = name[0:name.rfind('.')]+'.pdf'
    savefig(pathbeg+namefig) # save the figure
     
