##### Retrieval Variables
toffset = 0

# TYPE OF RETRIEVAL
retbool = True
retstring = 'WS'        # set the retrieval string ('WSTAU' or 'WS' or 'TAU') for 1 parameter or two
retmeanbool = False
#W_s = 0.33                 # Soil Moisture    only used if retstring = 'TAU'
tau = 0.0                   # L-VOD            only used if retstring = 'WS'

# mode = 'v'               # option to use only 1 of two antennas
T_g = 273.15+19            # Ground Temperature in (K) ( can approximate with air temperature )

omega = 0.00               # single scattering albedo (Tau-Omega emission model)

# INCIDENCE ANGLE
viewangle = 40.0           # degrees INCIDENCE ANGLE OF ANTENNA

#files for cold load
hfile = 'TclH.txt'         # files containing fit parameters for cold load TB
vfile = 'TclV.txt'

# Calibration offset
# These can be necesary in situations with extreme interference or
# obstructed view of the sky
H_bias = 0 # (K)
V_bias = 0 # (K)
V_rawoffset = 3.443144175046205
H_rawoffset = 1.0543062995332517

#### Min and Max contraints on fitting
varminwfit = 0.0     # Soil moisture min
varmaxwfit = 0.4     # Soil moisture max
varmintaufit = 0.0   # Tau min
varmaxtaufit = 1.0   # Tau max

#### Smoothing and Filtering
int_time  = 4.2       # INTEGRATION TIME

cf_thresh = 1e8       # threshold for Cost Function value (filter)

#### Standard Deviation Filter
stdthresh =  4.    # mV of raw voltages

#### Calibration Reference Smoothing
mnwindowsz_cal = 1  # number of samples to average for calibration loads
mnwindowsz_miss = 1 # the minimum allowed non-nan size of window


#madfiltbool = True
madfiltbool = False
#cable correction?
cablecorrbool = True    # defaults to True
spikefilterbool = False
