# Before you think about this code, consider a simpler solution that anyone can do

Most days in any week, I run my cooler about the same times each day. So, what I would really want is just a programmable controller that runs certain hours. This would still need a way to automatically close windows (though, if the average outdoor temperature overnight will be a bit cooler than the house temperature will be, I sometimes want windows open overnight). Without an electronic solution, *we* can be the controller for the cooler!

I almost always shut my cooler down before going to bed because the house is usually cool enough, and overnight just wastes a lot of electricity, and it doesn't make air as cool as one might expect due to the higher relative humidity at night. A simple room fan is all that is needed overnight. If I do leave it on by accident (or if I get home too late to cool down the house before bed), I often shut it off just as I wake up to lock in the especially cool house, which has only a small bad effect on the midday indoor temperature. If the weather is too hot and humid when I shut it off when I wake up, I sometimes do a quick (1 hour) cool later in the morning.

I also shut it down before it gets too hot during the day. My goal is to seal in coldness before it gets too hot outside for the cooler to cool the air, which only works well if you start up the cooler early enough. Also, the indoor air will be made to have a very high *absolute* humidity if the cooler is run during hottest parts of the day. I suppose locking in the coldness only works if you have good insulation in your home such as double-paned windows and (ideally light colored) blinds or curtains, which you should certainly invest in.


# smart-swamp-cooler-controller
Provides functions for making a smart evaporative-cooler controller by getting the weather forecast from weather.gov then doing various calculations.  
[https://www.weather.gov/documentation/services-web-api](https://www.weather.gov/documentation/services-web-api)

This code is very useful to run on any computer if you want to know if you should run your evaporative (swamp) cooler. Various useful information will be printed...
 - the output temperature and relative humidity of the cooler
 - the output temperature and relative humidity of the cooler in an hour or so
 - whether or not (and why) you should run your cooler

First, set the parameters at the top of the code.

A couple neat things in the code's decision making...
 - The decision to run depends on the near-future forecast because, if it will be cooler soon and the home isn't very hot, just wait to run it!
 - You can also set another lower target temperature for a time period (default is from 5:00 to 7:00) when the output temperature will be especially cool

In the western half of the US, the weather is either dry enough or cool enough to comfortably use an evaporative cooler. Evaporative coolers use far less energy than refrigerated air, especially if there is a smart control system to control them.

If you want to use this code outside the US, you'll have to modify a couple things. First, weather.gov will not work, so hopefully you have a local weather API. Second, you'll want to use Celsius instead of Fahrenheit, keeping in mind that the output-temperature table I have is in Fahrenheit. Regardless, you'd probably want to have some backup APIs and have the Celsius option.

The code has various target temperatures throughout the day: default, for a few hours around sunrise, and during peak hours. However, peak hours may be during the hottest part of the day when cool air is especially wanted. For this reason, the user should set the peak-hour period as short as possible, and, assuming that the output temperature at the vent is cold enough, edit the code to be able to set a cooler target temperature for the hour or two before peak hours. Another (expensive) solution would be to have a battery that is used during peak hours and that is charged outside of peak hours.


# example algorithm for controlling a swamp cooler via something like a Raspberry Pi
The code currently runs on any computer, but the idea is that it could be adapted to directly control an evaporative cooler. Relay(s) in parallel with diodes would be used to control the pump and fan.

On a Raspberry Pi, each relay coil would be controlled by a transistor. For the Raspberry Pi, an external ADC is necessary if using a potentiometer with a thermistor to measure temperature.

The relays would be near the swamp cooler, while the thermostat that has the thermistor and that gets the forecast will be across the home. These two circuits could be connected by DC wires, or they could be two separate circuits connected by some kind of radio signal such as WiFi, but then you would have to power them separately.

Here is some Python-inspired pseudocode showing how the cooler could be controlled...
```
updateTime = 0.0
attemptTime = 0.0
on = False
while 1:
    if time.time() > (attemptTime + 3 * 3600.0):
        internetSuccess, ... = updateForecast()
        attemptTime = time.time()
        if internetSuccess:
            updateTime = time.time()

    validForecast = True
    if time.time() > (updateTime + 24 * 3600.0):
        validForecast = False
        print("  Warning: Cannot connect to weather service! Running in thermostat-only mode.")

    T_in = getT()  # using a connected thermistor for example

    (Do calculations from smartSwampCooler.py to
      get the stop[] array, where each element is a different reason to stop)

    (Print various results.)

    if any(stop):
        on = False
        (turn off pump and fan)
    else:
        if not on:
          (turn on pump)
          sleep(150)
          (turn on fan)
          on = True
          sleep(5*60)   # should run for a while before turning off

    sleep(60)
```

If this algorithm were used to control an actual home's cooler, one might want to have a way to shut windows when the cooler turns off to prevent hot air from coming inside the home. I was then thinking that one-way vents exist, and I had the idea of some kind of rubber flaps to put on the outside of the window opening. Feel free to take this idea and become rich!

Not shown in the code above, the device will also need to synchronize its clock with time server(s) several times per year. Note that time synchronization is enabled by default on Raspberry Pi OS.

Time changes (such as due to daylight saving time) would cause slight issues between the time change and the next forecast update. Luckily, daylight saving time includes all of swamp-cooler season. If time changes were a problem, a fix would be to make the timezone variable be global and updated whenever the forecast updates, or just convert everything to UTC.

