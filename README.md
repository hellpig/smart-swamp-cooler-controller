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


# example algorithm for controlling a swamp cooler via something like a Raspberry Pi
The code currently runs on any computer, but the idea is that it could be adapted to directly control an evaporative cooler. Relay(s) in parallel with diodes would be used to control the pump and fan.

On a Raspberry Pi, each relay coil would be controlled by a transistor. For the Raspberry Pi, an external ADC is necessary if using a potentiometer with a thermistor to measure temperature.

The relays would be near the swamp cooler, while the thermostat that has the thermistor and that gets the forecast will be across the home. These two circuits could be connected by wires, or they could be two separate circuits.

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
