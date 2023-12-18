# PoLRa
**The following file describes how to take measurements with this radiometer and process the data to access the readings in both
a table format and a line graph.**

**Steps to start collecting data from the PoLRa sensor:**
  1. Find Resources Needed (12 V Power Supply, Ethernet Cable, USB to Ethernet Dongle (If needed for your computer), Download Filezilla Program). Also, you will need to create a static IP Address on your PC for the next steps (see the bottom of page 4 of the user_manual.pdf file in this repo)
  2. Connect the power supply to the sensor and make the Ethernet connection between your computer and the sensor.
  3. In Terminal, type in the command “ssh pi@10.66.0.xx” (xx is located on the side of the sensor; for our sensor, the number is 11) and the password is microwave.
  4. After connecting to the sensor, type in command “polra_main_nogps” and disconnect the ethernet cable from the sensor. Now, the sensor should be collecting data.
  5. To stop the data collection, reconnect the ethernet cable to the sensor and connect to the pi again through the Terminal. Now, type in command “polra_stop”. Then, open FileZilla Client.
  6. At the top of the Filezilla program, fill in “sftp://10.66.0.xx” (where xx is located on the side of the sensor) for the host section, “pi” for the username, “microwave” for the password, and “22” for the port. After filling all of this in, click Quickconnect.
  7. The data files will be saved in the directory /home/pi/data. FileZilla automatically opens the directory /home/pi also known as the “home directory”. The data is saved with the naming structure: ‘POLRA3_yyyymmdd_hhmmss.dat'
  8. Your local computer files will show on the left and the PoLRa on the right. Drag the data file (‘POLRA3_yyyymmdd_hhmmss.dat’) from the right to the left to copy to your local computer. (Note: the date and time will be inaccurate when making a non-GPS measurement; To make GPS measurements, follow the same steps above, but connect the GPS to the sensor and type in 'polra_main' instead of 'polra_main_nogps')

**Steps to process the data from the PoLRa sensor:**

  Processing PoLRa data requires python3 and a number of other python packages. 
   
  Recommended Installation: Anaconda 
  We recommend installing python3 and the required dependencies via anaconda. This will automatically package many of the required dependencies including numpy, scipy, pandas, etc, and will make it easier 
  to install some of the dependencies, such as gdal.  
  Installation is also possible using “brew” on mac, and other methods on Windows, but these are not directly supported.
  
  Anaconda on Apple / OSX: 
    1. Download and install anaconda from here: https://www.anaconda.com/products/individual 
     
    2. When the installation completes,  
    open Terminal (from Applications or Spotlight) and type, 
    python3 
     
    this should bring up the python command line prompt  
    >> 
     
    we can now close python. Type, 
    exit() 
  
  If you do not get the above prompt you may need to activate anaconda with the command conda activate and/or restart your computer. Anaconda installation instructions can also help you with 
  the latest up-to-date instructions on this.
  
  For Both Mac and Windows: 
    You can create a separate environment for pypolra if you regularly use anaconda and want to 
    keep track of the dependencies. In this case, you would use the command  
    “conda create --name pypolra”, and “conda activate pypolra”  
   
  4. Start installing the dependencies required for data processing using the convenient conda command and repositories. 
   One by one, type the following commands into the terminal to install the dependencies:
   
    conda install numpy 
   
    conda install -c conda-forge pyproj 
   
    conda install -c anaconda xarray 
   
    conda install -c conda-forge shapely 
   
    conda install -c conda-forge Descartes 
   
    conda install -c oggm oggm 
   
    conda install -c conda-forge motionless 
   
    pip3 install salem 
   
    conda install -c conda-forge gdal 
   
    pip3 install netCDF4
  
  Notes:
  - Depending on versioning and dependencies of other packages you may get messages such as “# All requested packages already installed”. This is not an error and you can proceed to the 
  next package installation.  
  - Alternatively, the salem install can be replaced with “conda install -c oggm salem“ which may or may not work depending on versions of other packages. The above should work regardless.  
  - Some of the packages will ask you to type “yes” or “y” and hit <enter> to confirm the usage of system 
  resources.  
  - Dependencies can occasionally be difficult with version updates and changes to the package managers. If you have difficulties with an import, or with installing any package, please first 
  consult google or stack overflow and second contact TerraRad for support.

  
  Next, to begin processing the data, simply navigate to the main_interval_proc.py file in the ground_based folder and change the "rawappended" variable to equal a path to the local .dat file of the data 
  collected from the PoLRa sensor. 
  Then, change the "L1filepath" variable to equal a path to a empty csv file (this will contain the processed output of the radiometer data). 
  Now, save the main_interval_proc.py file.

  Finally, open up a new terminal and type in the following commands.

  cd (insert directory for ground-based folder)
  conda activate pypolra
  python main_interval_proc.py

**The data is now processed and you can navigate to the csv file created to see the data in a table format or copy and paste the link from the terminal to your browser (Should look something like http://0.0.0.0:8080/)**

**For additional information about the PoLRa setup, see the user_manual.pdf file in this repository.**
**To learn more about the sensor, visit https://terraradtech.com/technology/**
