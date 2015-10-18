#! /usr/bin/python

# A simple Python command line tool to control an Omron MEMS Temp Sensor D6T-44L
# By Greg Griffes http://yottametric.com
# Modified by Iver Jordal
# GNU GPL V3 

# Jan 2015

import smbus
import sys
import getopt
import pigpio
from helpers import *
from time import sleep
import datetime
from astral import Astral
from pytz import timezone


i2c_bus = smbus.SMBus(1)
OMRON_1 = 0x0a  # 7 bit I2C address of Omron MEMS Temp Sensor D6T-44L
OMRON_BUFFER_LENGTH = 35  # Omron data buffer size
data = [0] * OMRON_BUFFER_LENGTH  # initialize the temperature data list

# intialize the pigpio library and socket connection to the daemon (pigpiod)
pi = pigpio.pi()  # use defaults
version = pi.get_pigpio_version()
# print 'PiGPIO version = '+str(version)
pigpio_relay_pin = 4

handle = pi.i2c_open(1, 0x0a)  # open Omron D6T device at address 0x0a on bus 1

previous_celsius_data = []
last_stationary_human_detected = datetime.datetime.now() - datetime.timedelta(minutes=10)

current_state = 1


def is_it_night():
    a = Astral()
    city_name = 'Oslo'
    city = a[city_name]
    sun = city.sun(local=True)
    sunrise = sun['sunrise']
    dusk = sun['dusk']
    now = datetime.datetime.now(timezone('CET'))
    return now < sunrise or now > dusk


def get_max_light_level():
    dim_light = is_it_night()
    return 100 if dim_light else 255


def turn_light_on():
    #print 'turning light on'
    global current_state
    if current_state == 1:
        return
    max_light_level = get_max_light_level()
    for i in range(16, 100):
        x = i / 100.0
        x **= 3
        x = int(x * max_light_level)
        pi.set_PWM_dutycycle(pigpio_relay_pin, x)
        sleep(0.01)
    current_state = 1


def turn_light_off():
    #print 'turning light off'
    global current_state
    if current_state == 0:
        return
    max_light_level = get_max_light_level()
    for i in reversed(range(15, 100)):
        x = i / 100.0
        x **= 3
        x = int(x * max_light_level)
        pi.set_PWM_dutycycle(pigpio_relay_pin, x)
        sleep(0.01)
    current_state = 0


def tick(i2c_bus, OMRON_1, data):
    global previous_celsius_data, last_stationary_human_detected

    i2c_bus.write_byte(OMRON_1, 0x4c)
    (bytes_read, data) = pi.i2c_read_device(handle, len(data))

    celsius_data = []

    for i in range(2, 34, 2):
        temperature_celsius = convert_two_bytes_to_celsius(data[i], data[i + 1])
        celsius_data.append(temperature_celsius)

    stationary = is_stationary_human(celsius_data)
    moving = is_moving_human(celsius_data, previous_celsius_data)
    
    if stationary and not moving:
        last_stationary_human_detected = datetime.datetime.now()
        turn_light_on()
    elif last_stationary_human_detected >= datetime.datetime.now() - datetime.timedelta(seconds=3):
        turn_light_on()
    else:
        turn_light_off()

    previous_celsius_data = celsius_data


try:
    while True:
        tick(i2c_bus, OMRON_1, data)
        sleep(0.25)
finally:
    print 'finally done'
    pi.i2c_close(handle)
    pi.stop()
