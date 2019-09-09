import timezonefinder, pytz, pandas as pd
from datetime import datetime

# %%          Append target lat, target long to raw pass data              %% #

#read raw passes and target list
unfilteredPasses = pd.read_csv('AccessTimes.csv', names=['Start Time','Stop Time','Target Name'])
targetList = pd.read_csv('SPOCTargetList.csv')

#put target names and average coordinates into a dictionary
#format {'targetname':[avgLat(float),avgLong(float)]}
targetDict = {}

#populate the dictionary
for i in range(len(targetList)):
    coord = []
    name = targetList.iloc[i][0]
    
    #reformat target name to be STK-compliant
    name = name.replace(' ','_').replace('.','').replace('(','').replace(')','')
    
    #loop over coordinates and include the ones that aren't blank
    for n in range(1,len(targetList.iloc[i])):
        if not type(targetList.iloc[i][n]) == float:
            coord.append(targetList.iloc[i][n])
    
    #calculate average of coordinates
    avgLat = 0
    avgLong = 0
    pointCount = 0
    
    for point in coord:
        
        point = point.split(',')
        lat = float(point[0])
        long = float(point[1])
        
        avgLat += lat
        avgLong += long
        
        pointCount += 1
    
    avgLat = avgLat/pointCount
    avgLong = avgLong/pointCount
    
    #create dictionary entry
    targetDict[name] = [avgLat,avgLong]

#loop over access times and append average coords
for index, row in unfilteredPasses.iterrows():
    
    match = targetDict.get(row['Target Name'])
    
    latMatch = match[0]
    longMatch = match[1]
    
    unfilteredPasses.loc[index,'Target Lat'] = latMatch
    unfilteredPasses.loc[index,'Target Long'] = longMatch

#drop target name
unfilteredPasses = unfilteredPasses.drop(columns=['Target Name'])

# %%          Convert passes from GMT+0 to GMT time local to target        %% #

tf = timezonefinder.TimezoneFinder()

#using target lat and long
for index, row in unfilteredPasses.iterrows():
    
    lat = float(row['Target Lat'])
    long = float(row['Target Long'])

    
    start = datetime.strptime(row['Start Time'], '%d %b %Y %H:%M:%S.%f')
    stop = datetime.strptime(row['Stop Time'], '%d %b %Y %H:%M:%S.%f')

    # Get the tz-database-style time zone name (e.g. 'America/Vancouver' or None)
    timezone_str = tf.closest_timezone_at(lat=lat, lng=long)
    
    if timezone_str is None:
        print("Could not determine the time zone of target at (",[lat, long],")")
    else:
        # Display the current time in that time zone
        timezone = pytz.timezone(timezone_str)
        dt = datetime.utcnow()
        offset = timezone.utcoffset(dt)
        localStartTime = (start + offset).strftime('%d %b %Y %H:%M:%S.%f')
        localStopTime = (stop + offset).strftime('%d %b %Y %H:%M:%S.%f')
        
        unfilteredPasses.loc[index, 'Start Time'] = localStartTime
        unfilteredPasses.loc[index, 'Stop Time'] = localStopTime

# %%                     Filter targets outside of 9-5                     %% #

#compare times based on minutes since 0:00:00.000
def to_minutes(timestring):
    try:
        hours = int(timestring[:2])
        minutes = int(timestring[3:5])
        seconds = float(timestring[6:14])
    except:
        print("Unable to parse time in format: ",timestring)
        return -1
    
    return 60*hours + minutes + seconds/60

#filter out weird times that didn't save correctly
unfilteredPasses = unfilteredPasses[unfilteredPasses['Start Time'] != 'Start Time']

#times outside of which to filter
am = to_minutes("09:00:00.000")
pm = to_minutes("17:00:00.000")

#loop over accesses, filtering unacceptable accesses
for index, access in unfilteredPasses.iterrows():

    include = True
    
    if((to_minutes(access['Start Time'][-15:]) < am)
        or (to_minutes(access['Start Time'][-15:]) > pm)
        or (to_minutes(access['Stop Time'][-15:]) > pm)
        or (to_minutes(access['Stop Time'][-15:]) < am)):
        
        include = False
    
    if(include == False):
        unfilteredPasses.drop(index, inplace=True)

unfilteredPasses.to_csv("TimesFiltered.csv",index=False)





























