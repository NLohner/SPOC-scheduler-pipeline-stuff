This script filters target passes based on the time of day local to the target. By default filters passes outside of 9:00:00-17:00:00. This default can be changed in the .env file.

The script reads two .csv files named 'AccessTimes.csv' and 'SPOCTargetList.csv'.
'AccessTimes.csv' contains the time of each target pass and name of the target, and\
 'SPOCTargetList.csv' contains the names of each target and the gps coordinates of \
 each point that defines the target.
 
 The script writes the filtered passes to a new .csv named 'TimesFiltered.csv'

 To install required packages, run "pip install -r requirements.txt"
