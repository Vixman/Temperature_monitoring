#!/usr/bin/python
# -*- coding: utf-8 -*-
# A simple script to log data from the MCP3304
import spidev
import time
import math
from time import strftime
import datetime
import string
import os
from datetime import datetime
from Tkinter import *

spi = spidev.SpiDev()
spi.open(0, 0)
filename = strftime("%d-%b-%Y %H_%M_%S")
interval = 10
pre_seconds = 0
fielname_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
root = Tk()

def reset_filename():
    global pre_seconds, filename
    now = datetime.now()
    now_seconds = (now - fielname_reset_time).seconds
    if now_seconds < pre_seconds:
        filename = strftime("%d-%b-%Y %H_%M_%S")
    pre_seconds = now_seconds

def read_adc(adcnum):
    # read SPI data from MCP3304 chip, 8 possible adc's (0 thru 7)
    if adcnum > 7 or adcnum < 0:
        return -1

    # Frame format: 0000 1SCC | C000 000 | 000 000
    r = spi.xfer2([((adcnum & 6) >> 1)+12 , (adcnum & 1) << 7, 0])
    adcout = ((r[1] & 15) << 8) + r[2]
    return adcout

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError:
        if not os.path.isdir(path):
            raise

def get_temperature(adc):
    # read thermistor voltage drop and convert it to degrees of Celsius
    value = read_adc(adc)               #read the adc
    volts = (value * 3.3) / 4095        #calculate the voltage

    # check if the thermistor is connected to this channel
    if volts > 3.2:
        return 0
    
    ohms = (volts*10000)/(3.3-volts)    #calculate thermistor resistance
    lnohm = math.log1p(ohms)            #take ln(ohms)

    # a, b, & c values from www.rusefi.com/Steinhart-Hart.html
    # 0-50 C
    a =  0.001125256672
    b =  0.0002347204473
    c =  0.00000008563052732

    # Steinhart Hart Equation
    # T = 1/(a + b[ln(ohm)] + c[ln(ohm)]^3)
    t1 = (b*lnohm)                      #b[ln(ohm)]
    c2 = lnohm                          #c[ln(ohm)]
    t2 = c*math.pow(c2,3)               #c[ln(ohm)]^3
    temp = 1/(a + t1 + t2)              #calcualte temperature in K
    tempc = temp - 273.15               #K to C

    #print out info
    print ("%4d/4095 => %5.4f V => %6.1f ? => %5.2f °K => %3.1f °C from adc %d" % (value, volts, ohms, temp, tempc, adc))
    #log.write("%4d,%5.4fV,%6.1f,%5.2f,%3.1f,adc %d" % (value, volts, ohms, temp, tempc, adc))
    
    return tempc

w = Label(root, text="Hello, world!")
w.pack()
root.mainloop()

make_sure_path_exists("./data")
while True:
    #write to log
    reset_filename()
    log = open("./data/"+filename+'.csv', 'a') #open a text file for logging
    log.write(strftime("%d/%m/%y,%H:%M:%S"))
    for x in range (0,8):
        log.write(",%3.1f" % (get_temperature(x)))
    log.write(strftime("\n"))
    log.close()
    time.sleep(interval)
