#!/usr/bin/python
# -*- coding: utf-8 -*-
# A class to log temperature data from the MCP3304
import spidev
import time
import math
import string
import os
from datetime import datetime
from time import strftime
import threading
from threading import Thread
import MySQLdb as mdb

pre_seconds = 0

class Monitor(Thread):

    def __init__(self, lock):
        Thread.__init__(self)
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.values= []
        self.filename = strftime("%d-%b-%Y %H_%M_%S")
        self.interval = 1
        self.temperature = []
        self.sensor = []
        self.filename_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.lock = lock      

    def set_filename(self, name):
        self.filename = name
        
    def reset_filename(self):
        global pre_seconds
        now = datetime.now()
        now_seconds = (now - self.filename_reset_time).seconds
        if now_seconds < pre_seconds:
            self.filename = strftime("%d-%b-%Y %H_%M_%S")
        pre_seconds = now_seconds

    def read_adc(self, adcnum):
        # read SPI data from MCP3304 chip, 8 possible adc's (0 thru 7)
        if adcnum > 7 or adcnum < 0:
            return -1

        # Frame format: 0000 1SCC | C000 000 | 000 000
        r = self.spi.xfer2([((adcnum & 6) >> 1)+12 , (adcnum & 1) << 7, 0])
        adcout = ((r[1] & 15) << 8) + r[2]
        return adcout

    def make_sure_path_exists(path):
        try:
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise

    def get_temperature(self, adc):
        # read thermistor voltage drop and convert it to degrees of Celsius
        value = self.read_adc(adc)               #read the adc
        volts = (value * 3.3) / 4095        #calculate the voltage

        # check if the thermistor is connected to this channel
        if volts > 3.2:
            return ""
    
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
        self.temperature.append("%3.1f" % tempc)
        return "%3.1f" % tempc

    def insertDB(self):
        try:
            with self.lock:
                con = mdb.connect("156.17.189.36",
                                    "user_insert",
                                    "up",
                                    "temp_monitor");
                cursor = con.cursor()

                for i in range(0,len(self.temperature)):
                    sql = "INSERT INTO temperature_records(temp, sensor) \
                    VALUES ('%s', '%s')" % \
                    (self.temperature[i], self.sensor[i])
                    cursor.execute(sql)
                    sql = []
                    con.commit()

                con.close()
        except:
            print "DBerror"

    def save_file(self):
        self.reset_filename()
        log = open("./data/"+self.filename+'.csv', 'a') #open a text file for logging
        log.write(strftime("%d/%m/%y,%H:%M:%S"))
        with self.lock:
            for x in range (0,8):
                self.values.insert(x,self.get_temperature(x))
                log.write(","+self.values[x])
                self.sensor.append(x)
        log.write(strftime("\n"))
        log.close()

    def run(self):
        while True:
            self.save_file()
            time.sleep(self.interval)
            self.insertDB()
