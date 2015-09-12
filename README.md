# How-to

## What

![Image](auto-light-demo.gif)

I've got these led lights beside the mirror in my house, and I want them to turn on automatically when somebody is standing still in front of the mirror. The led strips use 12 V and the current is around 160 mA. Let's create a relay driver that can turn on and off the lights using a Raspberry Pi model B+. The lights will still use their original power source, which is a 12 V DC adapter.

## Circuit
Let's get the needed components to create something that looks like this:
![Circuit](http://i.stack.imgur.com/nr2jb.png)

## GPIO pins
Raspberry Pi has a set of handy GPIO pins which we can use to interface with that circuit. Pin 7 can be used for for saturating the transistor and pin 9 is ground. Google 'raspberry pi gpio pinout' for more information.

## Components
Firstly, get a BC618 transistor, which can handle up to 500 mA of continous current (ought to be good enough for my purpose). This little project also requires two resistors. One of the transistors is a pull down resistor, and can be around 2 to 5 kiloohms. The other resistor will make sure the transistor doesn't draw much current from the RPi, and it can be around 1 kiloohm.

You might want to use a [breadboard](http://en.wikipedia.org/wiki/Breadboard) while testing, before soldering stuff.

## Coding
Now, on the raspberry pi, install python-dev and then [RPi.GPIO](https://pypi.python.org/pypi/RPi.GPIO), and you're ready to start coding. Here's some python code for a basic blinking light:

```python
import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)

GPIO.setup(7, GPIO.OUT)

for i in range(5):
    GPIO.output(7, False)
    sleep(2)
    GPIO.output(7, True)
    sleep(2)

GPIO.cleanup()
```

## Detect humans
Next, you should decide how you're going to detect a human standing still in front of the mirror. I use an OMRON D6T MEMS Thermal Sensor for this. It actually senses the weak heat radiation coming from the human body, so it even works in the dark. Finally, write the sophisticated code that takes input from the sensor, processes it and wisely decides when the light should be on and when it should be off. I have some logic that decides when there's a human standing still in front of the mirror. In other words, the light does not turn on if somebody is moving, because somebody that just moves past the mirror does not need the mirror light. It would actually be just annoying and distracting if it would turn on when it should not. Also, in order to avoid blinking, I decide that I leave the light on for at least 2 seconds after the last time a human standing still in front of the mirror was detected.

## Run script at startup
Run `sudo crontab -e`

Add a line like this:
`@reboot python /home/pi/auto-light/read_thermal.py`

