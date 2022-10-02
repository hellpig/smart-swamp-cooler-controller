# smart-swamp-cooler-controller
Provides functions for making a smart evaporative-cooler controller by getting the weather forecast from weather.gov then doing various calculations.

This code is very useful to run on any computer if you want to know if you should run your evaporative (swamp) cooler. Various useful information will be printed. First, set the parameters at the top.

In the western half of the US, the weather is either dry enough or cool enough to comfortably use an evaporative cooler. Evaporative coolers use far less energy than refrigerated air, especially if there is a smart control system to control them.


# example algorithm for controlling a swamp cooler via something like a Raspberry Pi
Relay(s) in parallel with diodes would be used to control the pump and fan.
Each relay coil would be controlled by a transistor.
For the Raspberry Pi, an ADC is necessary if using a potentiometer with a thermistor to measure temperature.
```
updateTime = 0.0
on = False
while 1:
  if time.time() > (updateTime + 3 * 3600.0) or not internetSuccess:
     internetSuccess, ... = updateForecast()
     updateTime = time.time()

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
