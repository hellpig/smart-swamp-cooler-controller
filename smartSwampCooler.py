#!/usr/bin/env python3.8
# See if there are any reasons to not run your evaporative cooler
#
# Make sure your computer has a correctly set time for your timezone,
#   or, when setting parameters, set them in the computer's timezone.
#   If using Replit, note that Replit's timezone is UTC, and a
#     Replit account is required to download from websites like weather.gov
#
# Temperatures are in °F
# Relative humidities are in interval [0, 100]
#   T is outside temperature
#   RH is outside relative humidity
#   T_out is output temperature of cooler
#   RH_out is output relative humidity of cooler
#   T_in is temperature inside house


import datetime, time
import urllib.request, json   # for downloading forecasts
import numpy as np            # for calculating T_out and RH_out (at output vent)



########################
#  set parameters
########################

# Peak hours (in your computer's time zone)
# Format is (hours, minutes) with hours in interval [0,23]
start = datetime.time(9, 0)
end = datetime.time(18, 30)

# temperature (°F) in your home from a thermometer far enough from vents and outside walls,
#   and thermometer should be about 1.5 meters from the ground
T_in = 80

# set target temperature (°F)
T_target = 75

# Set minimum temperature and times for running in early morning
#   in computer's time zone
T_min = 67
t1 = datetime.time(5, 0)
t2 = datetime.time(7, 0)

# set max desired relative humidity (RH) inside home in interval [0, 100]
RH_max = 90


# A couple global variables for getSmartValue()
#
# multiplier...
#   if 0, the future forecast does not influence decisions
#   if much larger than 1, the cooler won't run if T_out will soon be even colder
multiplier = 3
min_smartValue = 2   # positive number in F°


# A couple global variables for getForecast()
#
# For following Abq. location:  https://api.weather.gov/points/35.1173,-106.5582
# The following says they update twice daily, but I have observed them doing it
#   every 6 hours, with "forecast" times starting 6 to 7 hours before update
#     https://www.weather.gov/abq/ouroffice-outreach
website = "https://api.weather.gov/gridpoints/ABQ/101,119"
user_agent = "Smart Swamp-Cooler Controller"


'''
# Get the webpage that should be used for your location.
# Be kind: don't run this too frequently!
# lat and long in degrees
# I think this only works in the US? So long is negative.
def getURL(lat, long):
    site = "https://api.weather.gov/points/" + str(lat) + "," + str(long)
    with urllib.request.urlopen( urllib.request.Request(site , headers={'User-Agent': user_agent}) ) as url:
        website = json.load(url)["properties"]["forecastGridData"]
    return website

print(getURL(35.118863340477525, -106.55706562977988))
'''



########################
#  math to get T_out and RH_out (at output vent) from T and RH (outside)
########################
# Setting NN to a large number gives weird results in the case of extreme weather conditions.
#   but an extreme T_out is exactly what we want in this situation!
# If T < 70 °F, do not much trust the extrapolated output.
# Various approximations are made.


def getOutput(T, RH):

    # T_out values from chart
    #   https://learnmetrics.com/evaporative-cooler-chart-swamp-cooler/
    hum1_array = np.array([2.0] + np.arange(5,85,5).tolist())
    T1_array = np.arange(75,130,5)*1.0
    NN = 1000
    T2 = np.array([[54,55,57,58,59,61,62,63,64,65,66,67,68,69,70,71,72],
                   [57,58,60,62,63,64,66,67,68,69,71,72,73,74,75,76,77],
                   [61,62,63,65,67,68,70,71,72,73,74,75,76,77,79,81,NN],
                   [64,65,67,69,70,72,74,76,77,78,79,81,82,83,84,86,NN],
                   [67,68,70,72,74,76,78,79,81,82,84,85,87,NN,NN,NN,NN],
                   [69,71,73,76,78,80,82,83,85,87,88,NN,NN,NN,NN,NN,NN],
                   [72,74,77,79,81,84,86,88,89,NN,NN,NN,NN,NN,NN,NN,NN],
                   [75,77,80,83,85,87,90,92,NN,NN,NN,NN,NN,NN,NN,NN,NN],
                   [78,80,83,86,89,91,94,NN,NN,NN,NN,NN,NN,NN,NN,NN,NN],
                   [81,83,86,90,93,95,NN,NN,NN,NN,NN,NN,NN,NN,NN,NN,NN],
                   [83,86,90,93,96,NN,NN,NN,NN,NN,NN,NN,NN,NN,NN,NN,NN]])

    # get the indices for T and RH that are just beneath (or equal to) the outdoor value
    T_ind = np.array([i if i>=0 else 1000.0 for i in (T - T1_array)]).argmin()
    hum_ind = np.array([i if i>=0 else 1000.0 for i in (RH - hum1_array)]).argmin()


    # calculate T_out via (first order) interpolation or extrapolation

    if T_ind == len(T1_array) - 1:
        dT2_dT1 = (T2[T_ind, hum_ind] - T2[T_ind - 1, hum_ind]) / (T1_array[T_ind] - T1_array[T_ind - 1])
    else:
        dT2_dT1 = (T2[T_ind + 1, hum_ind] - T2[T_ind, hum_ind]) / (T1_array[T_ind + 1] - T1_array[T_ind])

    if hum_ind == len(hum1_array) - 1:
        dT2_dhum = (T2[T_ind, hum_ind] - T2[T_ind, hum_ind - 1]) / (hum1_array[hum_ind] - hum1_array[hum_ind - 1])
    else:
        dT2_dhum = (T2[T_ind, hum_ind + 1] - T2[T_ind, hum_ind]) / (hum1_array[hum_ind + 1] - hum1_array[hum_ind])

    T_out = T2[T_ind, hum_ind] + (T - T1_array[T_ind] ) * dT2_dT1 + (RH - hum1_array[hum_ind] ) * dT2_dhum



    # Math to get RH_out...
    #   energy / volume = energy / volume
    #   L Δρ_water = c ρ_air ΔT
    #   Δρ_water = c ρ_air ΔT / L
    # where...
    #   L is latent heat of vaporization for water
    #   c is the specific heat capacity of air
    #   ρ is density = mass / volume
    # Also...
    #   ρ_water = (RH / 100) * SVD
    # https://en.wikipedia.org/wiki/Saturation_vapor_density
    # https://en.wikipedia.org/wiki/Tetens_equation
    # http://hyperphysics.phy-astr.gsu.edu/hbase/Kinetic/watvap.html


    # some floats to start trying to get RH_out
    A = 17.27      # A and B for Tetens equation
    B = 237.3
    C = 4.58                    # units of g/m^3
    densityAir = 1146.0         # ignoring T dependence (in g/m^3)
    latentHeatWater = 2260.0    # in J/g
    specificHeatAir = 1.0       # approximate (in J/(g K))


    # calculate some values
    T1c = (T - 32) / 1.8   # converting to Celcius
    T2c = (T_out - 32) / 1.8
    deltaT = T1c - T2c
    SVD1 = C * np.exp( A*T1c / (T1c+B) )   # saturated vapor density
    SVD2 = C * np.exp( A*T2c / (T2c+B) )


    # calculate RH_out
    waterDensity1 = (RH/100) * SVD1
    waterAdded = densityAir*specificHeatAir*deltaT / latentHeatWater
    waterDensity2 = waterDensity1 + waterAdded
    RH_out = 100 * waterDensity2/SVD2

    return (T_out, RH_out)




########################
#  to get forecast from online
########################
#   https://www.weather.gov/documentation/services-web-api
# I assume that the forecasts are for the entire duration rather than being
#   for the moment at the start time. I will also assume that the format of
#   giving start time and duration isn't going to change.
# I assume that start times are always on the hour. That is, HH:00:00.
# I assume that times are UTC (what the "+00:00" probably means)


# Don't run this too frequently!
# returns ( internetSuccess, forecast_startDate, lists )
def getForecast():

    try:
        with urllib.request.urlopen( urllib.request.Request(website, headers={'User-Agent': user_agent}) ) as url:
            data = json.load(url)
    except:
        try:
            print("  Cannot connect to URL. Will retry in 5 seconds.")
            time.sleep(5)
            with urllib.request.urlopen( urllib.request.Request(website, headers={'User-Agent': user_agent}) ) as url:
                data = json.load(url)
            print("  Successfully connected.")
        except:
            print("  Cannot connect to URL.")
            return (False, -1, [], [], [], [])


    # Automatically calculate the UTC offset (timezone) that your computer is using.
    #   MDT = UTC - 6, so MDT will have timezone = -6
    timezone = round( ( datetime.datetime.fromtimestamp(time.time()) - datetime.datetime.utcfromtimestamp(time.time()) ) / datetime.timedelta(hours=1) )


    # check to see if weather.gov was updated recently
    forecast_startDate = datetime.datetime.strptime( data["properties"]["validTimes"][0:16], "%Y-%m-%dT%H:%M" ) + datetime.timedelta(hours = timezone)
    if datetime.datetime.now() - forecast_startDate > datetime.timedelta(hours = 20):
        print("  weather.gov is not updating regularly enough!")
        return (False, -1, [], [], [], [])


    # pull out relevant parts of data

    listT = data["properties"]["temperature"]["values"]
    listRH = data["properties"]["relativeHumidity"]["values"]

    listT_hour = [0] * len(listT)
    listT_temp = [0.0] * len(listT)
    for i,a in enumerate(listT):
      listT_hour[i] = (int(a['validTime'][11:13]) + timezone) % 24  # in local timezone
      listT_temp[i] = a['value'] * 1.8 + 32                       # now in Fahrenheit

    listRH_hour = [0] * len(listRH)
    listRH_hum  = [0.0] * len(listRH)
    for i,a in enumerate(listRH):
      listRH_hour[i] = (int(a['validTime'][11:13]) + timezone) % 24  # in local timezone
      listRH_hum[i]  = a['value']                                 # in interval [0,100]


    # To not have to do "mod 24" all the time, let's fix the hour lists.
    # Note that I had already done "mod 24" a bunch before I added the following code...

    prev = listT_hour[0]
    mult = 0
    for i in range(1, len(listT_hour)):
      listT_hour[i] += 24*mult
      if listT_hour[i] - prev < 0:
        mult += 1
        listT_hour[i] += 24
      prev = listT_hour[i]

    prev = listRH_hour[0]
    mult = 0
    for i in range(1, len(listRH_hour)):
      listRH_hour[i] += 24*mult
      if listRH_hour[i] - prev < 0:
        mult += 1
        listRH_hour[i] += 24
      prev = listRH_hour[i]

    return (True, forecast_startDate, listT_hour, listT_temp, listRH_hour, listRH_hum)




########################
#  to get current T and RH
########################


# returns (indexT, indexRH)
def getCurrent( forecast_startDate, listT_hour, listT_temp, listRH_hour, listRH_hum ):

    # get current time
    now = datetime.datetime.now()
    hour = now.hour
    if forecast_startDate.day < now.day:
      hour += 24
    timeCurrent = hour + now.minute / 60


    # get indices that come just before current time
    indexT = -1
    indexRH = -1
    maxSkip = 5  # often the forecast skips an hour or two
    for i in range(maxSkip):
      if hour-i in listT_hour:
         indexT = listT_hour.index(hour-i)
         break
      if i == maxSkip-1:
         print("yikes!")
         exit()
    for i in range(maxSkip):
      if hour-i in listRH_hour:
         indexRH = listRH_hour.index(hour-i)
         break
      if i == maxSkip-1:
         print("wowsers!")
         exit()

    return (indexT, indexRH)





########################
#  will T_out decrease soon? Calculate smartValue
########################


# returns (smartValue, timeStep, T_out_soon)
def getSmartValue(indexT, indexRH, listT_hour, listT_temp, listRH_hour, listRH_hum, T_out):

    T_soon = listT_temp[indexT + 1]

    # from the centers of the adjacent durations
    timeStep = ((listT_hour[indexT + 2] - listT_hour[indexT])%24) / 2

    # from the centers of the adjacent durations
    timeStep_RH = ((listRH_hour[indexRH + 2] - listRH_hour[indexRH])%24) / 2

    # this is an approximation because I'm lazy
    slope = (listRH_hum[indexRH + 1] - listRH_hum[indexRH]) / timeStep_RH
    RH_soon = listRH_hum[indexRH] + timeStep * slope


    T_out_soon, RH_out_soon  =  getOutput(T_soon, RH_soon)


    smartValue = min_smartValue + multiplier * (T_out - T_out_soon) / timeStep
    if smartValue < min_smartValue:
        smartValue = min_smartValue


    return (smartValue, timeStep, T_out_soon, RH_out_soon)




########################
#  do it!
########################


internetSuccess, forecast_startDate, listT_hour, listT_temp, listRH_hour, listRH_hum  =  getForecast()


if internetSuccess:


    indexT, indexRH = getCurrent( forecast_startDate, listT_hour, listT_temp, listRH_hour, listRH_hum )

    '''
    # get T and RH via interpolation (assuming data is for the moment of start time)
    slope = (listT_temp[indexT + 1] - listT_temp[indexT]) / ((listT_hour[indexT + 1] - listT_hour[indexT])%24)
    T = listT_temp[indexT] + ((timeCurrent - listT_hour[indexT])%24) * slope
    slope = (listRH_hum[indexRH + 1] - listRH_hum[indexRH]) / ((listRH_hour[indexRH + 1] - listRH_hour[indexRH])%24)
    RH = listRH_hum[indexRH] + ((timeCurrent - listRH_hour[indexRH])%24) * slope
    '''

    # get T and RH (assuming data is for the entire duration)
    T = listT_temp[indexT]
    RH = listRH_hum[indexRH]


    # get output values
    T_out, RH_out = getOutput(T, RH)


    # get smartValue
    smartValue, timeStep, T_out_soon, RH_out_soon  =  getSmartValue(indexT, indexRH, listT_hour, listT_temp, listRH_hour, listRH_hum, T_out)



########################
#  should we run the cooler?
########################

stop = [False]*4
# stop[0] has to do with peak hours
# stop[1] has to do with T_target and T_in    <-- requires thermometer
# stop[2] has to do with T_out compared to T_in   <-- requires thermometer
# stop[3] has to with RH_out


now_time = datetime.datetime.now().time()


if start < end:
  stop[0]  =  start < now_time < end
else:
  stop[0]  =  (now_time > start) or (now_time < end)


if (t1 < t2) and (t1 < now_time < t2):
  stop[1] = T_in < T_min
elif (t1 > t2) and ( (now_time > t1) or (now_time < t2) ):
  stop[1] = T_in < T_min
else:
  stop[1] = T_in < T_target



if internetSuccess:

    stop[2]  =  T_out + smartValue >= T_in

    stop[3]  =  RH_out > RH_max



########################
#  print a summary
########################


if internetSuccess:
    #print(T_soon, RH_soon)

    if T < 70:
      print("\n  Warning, T < 70, so extrapolation cannot be trusted.")
      print("    Maybe just open some windows?")

    print("\n  Computer's 24-hour time:", now_time.strftime('%H:%M'))

    print("\n  Outdoor temp (°F):", round(T,2))
    print("  Outdoor relative humidity (from 0 to 100):", round(RH,2))
    print("  Output temp:", round(T_out,2))
    print("  Output relative humidity:", round(RH_out,2))
    print("    ΔT =", round(T - T_out, 2), "    (ΔT determines water usage)")
    print("\n  In", round(timeStep,2), "hour(s), output temp will be:", round(T_out_soon,2))
    print("    Output relative humidity will be:", round(RH_out_soon,2))
    print("    smartValue =", round(smartValue,2))


print()
if any(stop):
  if stop[0]:
    print("  You will be running during peak hours!")
  if stop[1]:
    print("  Your home is cool enough!")
  if stop[2]:
    print("  The cooler will not produce cold enough air!")
  if stop[3]:
    print("  The air will be very humid!")
else:
  print("  Run your cooler!")

print()
