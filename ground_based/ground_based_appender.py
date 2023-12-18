#!/usr/bin/env python3
#
# Ground PoLRa Data Appender
# Takes hourly data files from Ground-based PoLRa3.x and appends them
# to a single csv file for further processing
# this script does not do any brightness temperature calibration
# or soil moisture retreivals

# Call this script with:
# python ground_based_appender.py /directory/to/data /directory/or/outputfile.csv

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import fnmatch
import re
import sys
#datadir = sys.argv[1]
#outputfile = sys.argv[2]
def append(datadir,outputfile):

    skiplines = 8 # number of lines in header

    header = "Year,Month,Day,Time,UnixTime,uacs,urs,up1,up2,Tir,Tacs,Trs,Taux,Tp1,uacs_std,urs_std,up1_std,up2_std,nsubsamp,t_1s,t_line"

    root = datadir
    pattern = "*.dat"
    filelist = []
    for path, subdirs, files in os.walk(root):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                if name[0]!='.':
                    filelist.append(os.path.join(path, name))
    filelist = sorted(filelist)

    with open(outputfile, 'w') as outfile:
        # write header of standard PoLRa raw dat file
        #outfile.write(header+"\n")
        first = True
        for fname in filelist:
            with open(fname) as infile:
                if not first:   # if it's not the first file being appended copy header
                    for i in range(skiplines): # read and throw out the header lines
                        infile.readline()
                filestring = infile.read()
                #for line in infile:
                #    filestring = infile.readline()
                filestring = re.sub(r'[^\S\r\n]+',',',filestring)
                outfile.write(filestring)
            first = False
