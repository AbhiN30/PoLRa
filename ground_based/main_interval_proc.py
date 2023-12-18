#! /usr/bin/env python3
#
# Main executable script for processing interval (ground-based) PoLRa3.2 Data
#
# PoLRa functions
import ground_based_appender
import ground_calibrator
import subprocess


# path to directory containing hourly interval data
#datadir = './data/SN8/interval_sample'
#datadir = './data/SN11/interval_sample'
#datadir = '/Users/abhinavnayak/Desktop/ground_based/data/SN11/interval_sample'

# filepath to output appended csv file
#rawappended = './data/SN8/sample_appended.csv'
#rawappended = './data/SN11/sample_appended.csv'
rawappended = '/Users/abhinavnayak/Desktop/Monday 11:13/Trial 2-2/POLRA3_20231113_15_26_03.dat'

# filepath to config file for correct PoLRa S/N
#configfile = "./data/SN8/config.py"
#configfile = "./data/SN11/config.py"
configfile = "/Users/abhinavnayak/Desktop/ground_based/data/SN11/config.py"

# Output filepath for L1 datafile (L1)
#L1filepath = './data/SN8/sample_L1.csv'
#L1filepath = './data/SN11/sample_L1.csv'
L1filepath = '/Users/abhinavnayak/Desktop/Monday 11:13/Trial 2-2/Second Spot Trial 2 (11-13).csv'

# Measurement period (minutes)
measperiod = 1 # minute

# append the hourly files into a single csv (maintains headers which are ignored
# when loading.)
#ground_based_appender.append(datadir,rawappended)

# calibrate brightness temperatures and perform retrievals
ground_calibrator.ground_calibrator(configfile,rawappended,L1filepath)

# create dash app to display plot of L1 data
subprocess.run(["python","./interval_L1plotter.py",L1filepath,str(measperiod)])
