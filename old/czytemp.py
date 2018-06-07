#!/usr/bin/python
# -*- coding: utf-8 -*-

import spidev
import time
import sys
import datetime
import math
spi = spidev.SpiDev()
spi.open(0, 0)


def timest(fname, fmt='%Y-%m-%d_{fname}'):
    return datetime.datetime.now().strftime(fmt).format(fname=fname)

def readadc(adcnum):

 # read SPI data from MCP3304 chip, 8 possible adc's (0 thru 7)
 if adcnum > 7 or adcnum < 0:
    return -1

 # Frame format: 0000 1SCC | C000 000 | 000 000
 r = spi.xfer2([((adcnum & 6) >> 1)+12 , (adcnum & 1) << 7, 0])
 adcout = ((r[1] & 15) << 8) + r[2]
 return adcout

def temp_get(adc):
    value = readadc(adc) #read the adc
    volts = (value * 3.0) / 4095 #calculate the voltage
    ohms = ((1/volts)*3000)-1000 #calculate the ohms of the thermististor

    lnohm = math.log1p(ohms) #take ln(ohms)

    #a, b, & c values from http://www.thermistor.com/calculators.php
    #using curve R (-6.2%/C @ 25C) Mil Ratio X
    a =  0.002197222470870
    b =  0.000161097632222
    c =  0.000000125008328

    #Steinhart Hart Equation
    # T = 1/(a + b[ln(ohm)] + c[ln(ohm)]^3)

    t1 = (b*lnohm) # b[ln(ohm)]

    c2 = c*lnohm # c[ln(ohm)]

    t2 = math.pow(c2,3) # c[ln(ohm)]^3

    temp = 1/(a + t1 + t2) #calcualte temperature

    tempc = temp - 273.15 - 4 #K to C
    # the -4 is error correction for bad python math

    return round(tempc,2)
   
print 'zapis do pliku: data_testfile.txt'

while True:
    sys.stdout = open(timest('testfile.txt'), 'a')
    print (str(datetime.datetime.now()),';','temp1:',temp_get(0),'temp2:',temp_get(1),'temp3:',temp_get(2),'temp4:',temp_get(3),'temp5:',temp_get(4),'temp6:',temp_get(5),'temp7:',temp_get(6),'temp8:',temp_get(7))
    time.sleep(10)
    sys.stdout.close()









