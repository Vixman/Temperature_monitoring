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
import threading
from threading import Thread

spi = spidev.SpiDev()
spi.open(0, 0)
filename = strftime("%d-%b-%Y %H_%M_%S")
interval = 10
pre_seconds = 0
filename_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
temp = "--,-"
degreeChar = u'\N{DEGREE SIGN}C'
#s1 = Label(frame, text=temp+degreeChar)
root = Tk()
v = StringVar()


class App:
    
    def __init__(self, master):
        frame = Frame(master)
        frame.pack()

        for x in range(8):
            Label(frame, text="Sensor %d:   " % (x+1)).grid(row=x)

        degreeChar = u'\N{DEGREE SIGN}C'
        #TODO convert to array
        self.s1 = Label(frame, textvariable=v)
        self.s2 = Label(frame, text="--.-"+degreeChar)
        self.s3 = Label(frame, text="--.-"+degreeChar)
        self.s4 = Label(frame, text="-.--"+degreeChar)
        self.s5 = Label(frame, text="-.--"+degreeChar)
        self.s6 = Label(frame, text="-.--"+degreeChar)
        self.s7 = Label(frame, text="-.--"+degreeChar)
        self.s8 = Label(frame, text="-.--"+degreeChar)

        self.s1.grid(row=0, column=1)
        self.s2.grid(row=1, column=1)
        self.s3.grid(row=2, column=1)
        self.s4.grid(row=3, column=1)
        self.s5.grid(row=4, column=1)
        self.s6.grid(row=5, column=1)
        self.s7.grid(row=6, column=1)
        self.s8.grid(row=7, column=1)

    def say_hi(self):
        print "hi there, everyone!"

app = App(root)

def reset_filename():
    global pre_seconds, filename
    now = datetime.now()
    now_seconds = (now - filename_reset_time).seconds
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

def display():
    app.v.set("54")
    root.after(500, display)

def controls():
    root.after(500, display)
    root.mainloop()

def work():
    while True:
        #write to log
        reset_filename()
        log = open("./data/"+filename+'.csv', 'a') #open a text file for logging
        log.write(strftime("%d/%m/%y,%H:%M:%S"))
      #  app.s1.config(text = ",%3.1f" % get_temperature(0))
        for x in range (0,8):
            log.write(",%3.1f" % (get_temperature(x)))
        log.write(strftime("\n"))
        log.close()
        time.sleep(interval)

make_sure_path_exists("./data")
Thread(target = controls).start()
Thread(target = work).start()
