#!/usr/bin/python3

################# Bash script trtgolf.py to run for GOLF application ###########
#
#     call with "trtgolf.py datapath gps_filename rad_filename"
#
#


import numpy as np
import pandas as pd
import datetime
import sys
import os
import importlib
from tools import libdrone

def ground_calibrator(configfile,L0filepath,L1outfilepath):
    # import config script
    config_loader = importlib.util.spec_from_file_location('config',configfile)
    cfg = importlib.util.module_from_spec(config_loader)
    config_loader.loader.exec_module(cfg)

    # get parts of path / filename
    L0filename = os.path.basename(L0filepath)
    L0filename_stem = os.path.splitext(L0filename)[0]
    L0filepath_stem = os.path.splitext(L0filepath)[0]

    alphai = cfg.viewangle
    ###############################################################################
    print("Loading PoLRa Data...",end='',flush=True)
    DATA = np.genfromtxt(L0filepath,autostrip=True,invalid_raise = False, skip_header=8)
    # throw out first line
    DATA = DATA[1:]
    print("Done.")
    print("Processing & Calibrating Radiometer Data...")

    #extract POSIX timestamp as it has sub-second accuracy

    unixtime = DATA[:,4].astype(float)
    if 'cfg.toffset' in locals():
        unixtime = unixtime+cfg.toffset
    # standard column format since PoLRa3
    ###radiometer voltages
    cl = DATA[:,5]     #cold load
    ml = DATA[:,6]     #matched load
    rv = DATA[:,7]     #v pol
    rh = DATA[:,8]     #h pol

    ###extract physical temperatures and save mean to vector
    Tdet = DATA[:,9]+273.15   #Infrared temperature sensor (saved in deg C!) convert to K
    Tml = DATA[:,10]    #matched load physical temp
    Tcl = DATA[:,11]    #cold load physical temp
    Tpam1 = DATA[:,12]  #aux board temp / ext. 1
    Tpam2 = DATA[:,13]  #external temp
    #Tpam = 0.9*Tml+0.1*Tpam2 # effective temperature for cable loss
    Tpam = (Tpam1+Tpam2)/2
    ucl = DATA[:,14]   #cold load
    uml = DATA[:,15]   #matched load
    urv = DATA[:,16]   #v pol
    urh = DATA[:,17]   #h pol

    print(DATA)

    date_time = np.array([datetime.datetime.utcfromtimestamp(i) for i in unixtime])  #convert unix time to datetimes
    print("")
    print("PoLRa Start Time:")
    print(date_time[0])
    print("")
    print("PoLRa End Time:")
    print(date_time[-1])


    tsec = unixtime-unixtime[0]     # elapsed time in seconds (vector)
    tmin = tsec/60                  # elapsed time in minutes
    totalt = unixtime[-1:]-unixtime[0]

    int1 = DATA[:,19]               # single channel integration time
    inttot = DATA[:,20]             # total time for 4 ports
    mnwindowsz = 1000*cfg.int_time/np.nanmean(inttot)   # window size for moving average
    print("Done.")

    ####standard deviations of each individual measurement

    #### smooth calibration voltages
    ## standard deviation filtering (calibraton loads)
    cl[ucl>cfg.stdthresh]=np.nan
    ml[uml>cfg.stdthresh]=np.nan

    rh[urh>cfg.stdthresh]=np.nan
    rv[urv>cfg.stdthresh]=np.nan

    if cfg.madfiltbool:
        # run median absolute deviation on raw voltages to remove any spikes
        nmad = 2.0
        madwindowsz = 30
        cl,nfiltcl = libdrone.madfilter(cl,nmad,madwindowsz)
        ml,nfiltml = libdrone.madfilter(ml,nmad,madwindowsz)
        rh,nfiltrh = libdrone.madfilter(rh,nmad,madwindowsz)
        rv,nfiltrh = libdrone.madfilter(rv,nmad,madwindowsz)
        #print(nfilth,' H, ',nfiltv,' V values filtered by MAD filter.')

    #### Smoothing with Gaussian window averaging ###
    # cl = pd.Series(cl).fillna(pd.Series(cl).rolling(cfg.mnwindowsz_cal, min_periods=1,win_type='gaussian').mean(std=cfg.mnwindowsz_cal))
    # ml = pd.Series(ml).fillna(pd.Series(ml).rolling(cfg.mnwindowsz_cal, min_periods=1,win_type='gaussian').mean(std=cfg.mnwindowsz_cal))
    # ### Smooth calibration loads with Gaussian window ###
    # cl_smth = pd.Series(cl).rolling(cfg.mnwindowsz_cal, min_periods=cfg.mnwindowsz_cal-cfg.mnwindowsz_miss,center=True,win_type='gaussian').mean(std=cfg.mnwindowsz_cal)
    # ml_smth =pd.Series(ml).rolling(cfg.mnwindowsz_cal, min_periods=cfg.mnwindowsz_cal-cfg.mnwindowsz_miss,center=True,win_type='gaussian').mean(std=cfg.mnwindowsz_cal)
    # Tml_smth = pd.Series(Tml).rolling(cfg.mnwindowsz_cal, min_periods=cfg.mnwindowsz_cal-cfg.mnwindowsz_miss,center=True,win_type='gaussian').mean(std=cfg.mnwindowsz_cal)
    # Tcl_smth = pd.Series(Tcl).rolling(cfg.mnwindowsz_cal, min_periods=cfg.mnwindowsz_cal-cfg.mnwindowsz_miss,center=True,win_type='gaussian').mean(std=cfg.mnwindowsz_cal)
    Tml_smth = Tml
    Tcl_smth = Tcl
    cl_smth = cl
    ml_smth = ml

    ## Apply raw voltage correction (matched load test) if in config
    rv = rv+cfg.V_rawoffset
    rh = rh+cfg.H_rawoffset
    ########################## Brightness Temperature Calculation ##################
#load temp dependent CL files
#contains linear fit params mx+b and cable loss in db
    hpars,vpars = libdrone.getTCL(cfg.hfile,cfg.vfile)
    Tcl_H = hpars[0]*Tcl_smth+hpars[1]
    Tcl_V = vpars[0]*Tcl_smth+vpars[1]

    slopeh=(Tml_smth-Tcl_H)/(ml_smth-cl_smth)
    offh = slopeh*(-ml_smth)+Tml_smth
    Tb_hraw = offh+rh*slopeh                    #calibrated h pol

    slopev=(Tml_smth-Tcl_V)/(ml_smth-cl_smth)
    offv = slopev*(-ml_smth)+Tml_smth
    Tb_vraw = offv+rv*slopev                    #calibrated v pol

    #################### FILTERING AVERAGING AND QUALITY CONTROL %%%%%%#############
    cleanTbh = np.array(Tb_hraw) #copy raw data array
    cleanTbv = np.array(Tb_vraw)

    cleanTbh[urv>cfg.stdthresh]=np.nan  #apply standard deviation filter
    cleanTbh[urh>cfg.stdthresh]=np.nan  #both polarizations filtered together
    cleanTbv[urv>cfg.stdthresh]=np.nan  #apply standard deviation filter
    cleanTbv[urh>cfg.stdthresh]=np.nan  #both polarizations filtered together

    numstd =  (urv>cfg.stdthresh).sum()+(urh>cfg.stdthresh).sum()
    print(numstd,' values filtered by std filter.')

    np.warnings.filterwarnings('ignore') #turn off warnings for NaN values


    ##apply and insert moving median over missing values
    min_nonnan = 3
    # we are not averaging at least 3 samples we take std over 3
    if int(mnwindowsz)<3:
        mnwindowsz = 3
        min_nonnan = int(mnwindowsz)

    if cfg.madfiltbool:
        # filter brightness temperatures for MAD spikes also
        nmad = 3
        madwindowsz = 30
        cleanTbh,nfilth = libdrone.madfilter(cleanTbh,nmad,madwindowsz)
        cleanTbv,nfiltv = libdrone.madfilter(cleanTbv,nmad,madwindowsz)
        print(nfilth,' H, ',nfiltv,' V values filtered by MAD filter.')

    if cfg.spikefilterbool:
        nmad = 3
        # apply mad filter to entire time series
        cleanTbh,nfilth = libdrone.madfilter(cleanTbh,nmad,len(cleanTbh))
        cleanTbv,nfiltv = libdrone.madfilter(cleanTbv,nmad,len(cleanTbv))
        print(nfilth,' H, ',nfiltv,' V values filtered by Spike filter.')

    ###########  moving average
    #windowstd = int(np.around(mnwindowsz/3))
    #cleanTbv = pd.Series(cleanTbv).rolling(int(mnwindowsz), min_periods=min_nonnan,center=True,win_type='gaussian').mean(std=windowstd)
    #cleanTbh = pd.Series(cleanTbh).rolling(int(mnwindowsz), min_periods=min_nonnan,center=True,win_type='gaussian').mean(std=windowstd)

    ######## must also average angles to be looking at same time periods ###########
    #rollradt = pd.Series(rollradt).rolling(int(mnwindowsz), min_periods=min_nonnan,center=True,win_type='gaussian').mean(std=windowstd)
    #pitchradt = pd.Series(pitchradt).rolling(int(mnwindowsz), min_periods=min_nonnan,center=True,win_type='gaussian').mean(std=windowstd)

    ########### remove constant calibration bias (brightness temperature)  #########

    print("Applying V bias")
    cleanTbv = cleanTbv-cfg.V_bias;

    print("Applying H bias")
    cleanTbh = cleanTbh-cfg.H_bias;

    #####  calculate rolling standard deviation
    sigTbv = pd.Series(cleanTbv).rolling(int(mnwindowsz), min_periods=3).std()
    sigTbh = pd.Series(cleanTbh).rolling(int(mnwindowsz), min_periods=3).std()
    print("Done.")

    ###########  Apply cable loss correction to brightness temperatures  ###########
    if cfg.cablecorrbool:
        loss_ratio = 0.1#may depend on system!
        Teff = loss_ratio*Tpam+(1-loss_ratio)*Tml #effective temperature of transmission line loss
        print("Applying Cable Loss Correction...",end='',flush=True)
        Loss_V = vpars[2]
        Loss_H = hpars[2]
        t_cablev = 10**(Loss_V/10)
        t_cableh = 10**(Loss_H/10)
        cleanTbh = (cleanTbh-(1-t_cableh)*Teff)/(t_cableh)
        cleanTbv = (cleanTbv-(1-t_cablev)*Teff)/(t_cablev)
        print("Done.")

    ################################# Retrievals ###################################
    cleanTbv[np.isnan(cleanTbh)]=np.nan   #make sure we have both Tbs or both NaN
    cleanTbh[np.isnan(cleanTbv)]=np.nan

    mode='dual'                       # default to dual pol mode
    alpha = alphai * np.ones(len(cleanTbv))

    if cfg.retbool:
        if cfg.retmeanbool:
            print(retmeanbool)
            #Wsmn,Taumn,T_g,cfv = RetTauWsTgAll(cleanTbh,cleanTbv,alpha,omega,varminwfit,varmintaufit,varminTgfit,varmaxwfit,varmaxtaufit,varmaxTgfit)
            Wsmn,Taumn,omega,T_g,cfv = libdrone.RetTauWsOmegaTgAll(cleanTbh,cleanTbv,alpha,varminwfit,varmintaufit,varminomegafit,varminTgfit,varmaxwfit,varmaxtaufit,varmaxomegafit,varmaxTgfit)
            Tbhf,Tbvf = libdrone.tauomega_all_tb(Wsmn,Taumn,T_g,T_g,alpha,omega)
            print("Mean Soil Moisture Accross Flight: ",Wsmn)
            print("Mean L-VOD (Tau) Accross Flight: ",Taumn)
            print("Mean Single Scattering Albedo Accross Flight: ",omega)
            print("Mean Emission Temperature Accross Flight: ",T_g)
            print("Cost Function Value: ",np.sqrt(cfv/len(cleanTbh[~np.isnan(cleanTbh)])))
            # set values if doing a 1 parameter retrieval
            W_s = Wsmn
            tau = Taumn
        else:
            T_g = cfg.T_g
            print('Ground emission temperature T_g = ',T_g)
        # Begin standard retrievals
        if cfg.retstring == 'WS':
            print("Retreiving Soil Moisture for ",len(cleanTbv[~np.isnan(cleanTbv)])," points...",end='',flush=True)
            Ws,cfv = libdrone.RetWs(cleanTbh,cleanTbv,T_g,alpha,cfg.tau,cfg.omega,cfg.varminwfit,cfg.varmaxwfit,mode)
            ## filter cost function values above threshold
            Ws[cfv>cfg.cf_thresh]=np.nan
            #Smooth retrieval similar to brightness temperatures
            #Ws = pd.Series(Ws).rolling(int(mnwindowsz), min_periods=min_nonnan,center=True,win_type='gaussian').mean(std=windowstd)
            nonnans = ~np.isnan(Ws)
            Wsp = Ws[nonnans]             #pass only non-nan to plotting function
            print("Done.")
            print((cfv>cfg.cf_thresh).sum(),' values filtered by cost function value.')
            TBHtheory,TBVtheory = libdrone.tauomega_all_tb(Ws,cfg.tau,T_g,T_g,alpha,cfg.omega)

        if cfg.retstring == 'WSTAU':
            print("Retreiving Soil Moisture and Vegetation Depth for ",len(alpha[~np.isnan(cleanTbv)])," points...",end='',flush=True)
            Ws,Tau,cfv = libdrone.RetTauWs(cleanTbh,cleanTbv,T_g,alpha,cfg.omega,cfg.varminwfit,cfg.varmintaufit,cfg.varmaxwfit,cfg.varmaxtaufit)
            #Smooth retrieval similar to brightness temperatures
            #Ws = pd.Series(Ws).rolling(int(mnwindowsz), min_periods=min_nonnan,center=True,win_type='gaussian').mean(std=windowstd)
            #Tau = pd.Series(Tau).rolling(int(mnwindowsz), min_periods=min_nonnan,center=True,win_type='gaussian').mean(std=windowstd)
            ## filter cost function values above threshold
            Ws[cfv>cfg.cf_thresh]=np.nan
            Tau[cfv>cfg.cf_thresh]=np.nan
            nonnans = ~np.isnan(Ws)
            Wsp = Ws[nonnans]             #pass only non-nan to plotting function
            Taup = Tau[nonnans]
            print("Done.")
            print((cfv>cfg.cf_thresh).sum(),' values filtered by cost function value.')
            TBHtheory,TBVtheory = libdrone.tauomega_all_tb(Ws,Tau,T_g,T_g,alpha,cfg.omega)

        if cfg.retstring == 'TAU':
            print("Retreiving Vegetation Optical Depth for ",len(alpha[~np.isnan(cleanTbv)])," points...",end='',flush=True)
            Tau,cfv = libdrone.RetTau(cleanTbh,cleanTbv,T_g,alpha,cfg.W_s,cfg.omega,cfg.varmintaufit,cfg.varmaxtaufit,mode)
            #Smooth retrieval similar to brightness temperatures
            #Tau = pd.Series(Tau).rolling(int(mnwindowsz), min_periods=min_nonnan,center=True,win_type='gaussian').mean(std=windowstd)
            ## filter cost function values above threshold
            Tau[cfv>cfg.cf_thresh]=np.nan
            Tau,nfiltv = libdrone.madfilter(Tau,nmad,madwindowsz)
            nonnans = ~np.isnan(Tau)
            Taup = Tau[nonnans]
            print("Done.")
            print((cfv>cfg.cf_thresh).sum(),' values filtered by cost function value.')
            TBHtheory,TBVtheory = libdrone.tauomega_all_tb(cfg.W_s,Tau,T_g,T_g,alpha,cfg.omega)
    else:
        #nonnans = ~np.isnan(latrad)
        nonnans = ~np.isnan(cleanTbv)


    ###########################  Export CSV -- Processed  ##########################
    print("Exporting CSV file of processed Vector data ",end='',flush=True)
    if cfg.retbool:
        if cfg.retstring == 'WS':
            Tau = np.ones_like(cleanTbv)*np.nan
        if cfg.retstring =='TAU':
            Ws = np.ones_like(cleanTbv)*np.nan
    else:
        Tau = np.ones_like(cleanTbv)*np.nan
        Ws = np.ones_like(cleanTbv)*np.nan
        cfv = np.ones_like(cleanTbv)*np.nan
        TBHtheory = np.ones_like(cleanTbv)*np.nan
        TBVtheory = np.ones_like(cleanTbv)*np.nan


    ###########################  Calculate residual of TBs (better than cost function value)
    TBH_resid =  TBHtheory-cleanTbh
    TBV_resid =  TBVtheory-cleanTbv

    outarr = np.column_stack((unixtime,cleanTbv,cleanTbh,Ws,Tau,Tdet,Tml,Tcl,Tpam1,Tpam2,ml,cl,rv,rh,uml,ucl,urv,urh,slopeh,offh,TBV_resid,TBH_resid,cfv))

    #outarr = outarr[~np.isnan(xradt),:]
    outarr = outarr[~np.isnan(outarr[:,1]),:]

    formatstr =                                                             "%.18e,%4.3f,%4.3f,%1.3f,%1.3f,%3.3f,%3.3f,%3.3f,%3.3f,%3.3f,%4.3f,%4.3f,%4.3f,%4.3f,%3.3f,%3.3f,%3.3f,%3.3f,%3.4f,%5.4f,%3.3f,%3.3f,%5.3f"
    np.savetxt(L1outfilepath, outarr, delimiter=',', fmt = formatstr, header="posix time,TBV (K),TBH (K),Soil Moisture (m^3/m^3),Tau (-),T_IR (K),T_RS (K),T_ACS (K),T_Ant1 (K),T_Ant2 (K),u_RS (mV),u_ACS (mV),u_V (mV),u_H (mV),STDOM(u_RS) (mV),STDOM(u_ACS) (mV),STDOM(u_V) (mV),STDOM(u_H) (mV),Gain (K/mV),Offset (K),TBV Residual (K),TBH Residual (K),Cost Function Value (K^2)")

    print("Done.")
    return
