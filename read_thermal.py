#! /usr/bin/python

# GNU GPL V3
# 2015

import smbus
import sys
import getopt
import pigpio
from helpers import *
from time import sleep
import datetime
from datetime import datetime, timedelta
from astral import Astral
from pytz import timezone


class AutoLight(object):
    OMRON_BUFFER_LENGTH = 35  # Omron data buffer size
    OMRON_1 = 0x0a  # 7 bit I2C address of Omron MEMS Temp Sensor D6T-44L

    def __init__(self):
        self.i2c_bus = smbus.SMBus(1)
        self.temperature_data = [0] * self.OMRON_BUFFER_LENGTH  # the temperature data list

        # initialize the pigpio library and socket connection to the daemon (pigpiod)
        self.pi = pigpio.pi()  # use defaults
        # version = pi.get_pigpio_version()
        # print 'PiGPIO version = '+str(version)
        self.pigpio_relay_pin = 4

        self.handle = self.pi.i2c_open(1, 0x0a)  # open Omron D6T device at address 0x0a on bus 1

        self.previous_celsius_data = []
        self.time_stationary_detected = datetime.now() - timedelta(minutes=10)
        self.desired_light_level = 0
        self.current_light_level = 0.0

        try:
            self.next_tick_time = datetime.now() - timedelta(seconds=1)
            while True:
                if self.next_tick_time < datetime.now():
                    self.tick()
                    self.next_tick_time = datetime.now() + timedelta(seconds=0.25)
                else:
                    self.update_light_level()
                    # TODO: if noop, let the CPU sleep until next tick
        except Exception, e:
            print e
        finally:
            print 'finally done'
            self.pi.i2c_close(self.handle)
            self.pi.stop()

    @staticmethod
    def is_it_night():
        # TODO: cache result for swift result
        a = Astral()
        city_name = 'Oslo'
        city = a[city_name]
        sun = city.sun(local=True)
        sunrise = sun['sunrise']
        dusk = sun['dusk']
        now = datetime.now(timezone('CET'))
        return now < sunrise or now > dusk

    @staticmethod
    def get_max_light_level():
        return 255
        #dim_light = is_it_night()
        #return 100 if dim_light else 255

    def set_light_level(self, level):
        """
        :param level: from 0 to 100
        :return:
        """
        if level >= 15:
            level += 40
            level /= 140.0
            level **= 3
            level *= 255
        level = int(min(255, max(0, level)))
        self.pi.set_PWM_dutycycle(self.pigpio_relay_pin, level)

    def update_light_level(self):
        diff = self.desired_light_level - self.current_light_level
        if diff > 0:
            self.current_light_level += 1
        elif diff < 0:
            self.current_light_level -= 0.25
        else:
            return
        self.set_light_level(self.current_light_level)
        sleep(0.01)

    def turn_light_on(self):
        #print 'turning light on'
        self.desired_light_level = 100

    def turn_light_off(self):
        #print 'turning light off'
        self.desired_light_level = 0

    def tick(self):
        self.i2c_bus.write_byte(self.OMRON_1, 0x4c)
        bytes_read, self.temperature_data = self.pi.i2c_read_device(self.handle, len(self.temperature_data))

        celsius_data = []

        for i in range(2, 34, 2):
            first_byte = self.temperature_data[i]
            second_byte = self.temperature_data[i + 1]
            temperature_celsius = convert_two_bytes_to_celsius(first_byte, second_byte)
            celsius_data.append(temperature_celsius)

        warm_enough, should_activate = is_human(celsius_data)
        moving = is_moving_human(celsius_data, self.previous_celsius_data)
        now = datetime.now()

        if warm_enough and should_activate and not moving:
            # activate light
            self.time_stationary_detected = now
            self.turn_light_on()
        elif warm_enough and self.time_stationary_detected >= now - timedelta(seconds=10):
            if self.current_light_level > 5:
                if not moving:
                    self.time_stationary_detected = now  # stay alive
                self.turn_light_on()
            else:
                self.turn_light_off()
        elif self.time_stationary_detected >= now - timedelta(seconds=1):
            self.turn_light_on()
        else:
            self.turn_light_off()

        self.previous_celsius_data = celsius_data

if __name__ == '__main__':
    AutoLight()
