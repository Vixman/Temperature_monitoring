#!/usr/bin/python
# -*- coding: utf-8 -*-
# GUI for Temperature Monitor
from Tkinter import *
import ttk
import tkMessageBox
import threading
#from threading import Thread
from lib.monitor import Monitor
import time
import datetime



degreeChar = u'\N{DEGREE SIGN}C'
lock = threading.RLock()
m = Monitor(lock)
root = Tk()
root.wm_title("Monitor Temperatury v.0.3")
tv = [StringVar() for _ in range(8)]
frame = Frame(root)
frame.pack()
sensborder = ttk.LabelFrame(frame, text="Sensors", labelanchor=N+S)
sensborder.grid(columns=3)
dateborder = ttk.LabelFrame(frame, text="Current measurement", labelanchor=N+S)
dateborder.grid(columns=3)
menubar = Menu(root)
state = True
timer = [0, 0, 0]
pattern = "{0:02d}:{1:02d}:{2:02d}"


def tyk():
        t = time.strftime("%H:%M:%S")
        if t != clock["text"]:
                clock["text"] = t
        clock.after(200, tyk)

def update_timer():
        if(state):
                global timer
                timer[2] += 1
                if (timer[2] >= 60):
                        timer[2] = 0
                        timer[1] += 1
                if (timer[1] >= 60):
                        timer[1] = 0
                        timer[0] += 1
                timeString = pattern.format(timer[0], timer[1], timer[2])
                timeText.config(text=timeString)
        root.after(1000, update_timer)
                
def start():
        lock.release()
        global state
        state = True
        global timer
        dur.config(text="Duration: 00:00:00")
        startime.config(text="START:"+str(time.strftime("%d/%m/%y %H:%M:%S")))
        stoptime.config(text="STOP:")
def stop():
        lock.acquire()
        global state
        state = False
        global timer
        timer = pattern.format(timer[0], timer[1], timer[2])
        dur.config(text="Duration: "+str(timer))
        timer = [0, 0, 0]
        timeText.config(text="00:00:00")
        stoptime.config(text="STOP:"+str(time.strftime("%d/%m/%y %H:%M:%S")))
        
def display():
        with lock:
                for x in range(8):
                        tv[x].set(m.values[x]+degreeChar)
        root.after(400, display)
        

def on_x():
        lock.acquire()
        if tkMessageBox.askyesno("EXIT", "Are you sure?"):
                root.destroy()
                
for x in range(8):
        Label(sensborder, text="Sensor %d:   " % (x+1), font=("Helvetica", 28)).grid(row=x, column=0, sticky=W)
        Label(sensborder, textvariable=tv[x], font=("Helvetica", 28)).grid(row=x, column=1, sticky=E)
        
dur = Label(dateborder, text="Duration: ", font=("Helvetica", 18))
dur.grid(row=15, sticky=W)
clock = Label(dateborder, font=("Helvetica", 20, "bold"), bg="white")
clock.grid(row=10, column=0, sticky=W)       
timeText = Label(dateborder, text="00:00:00", font=("Helvetica", 20), bg="white")
timeText.grid(row=10, column=1, sticky=E)
'''start = Button(frame, text="START", font=("Helvetica", 22), fg="green", command=start)
start.grid(row=11, column=0)
stop = Button(frame, text="STOP", font=("Helvetica", 22), fg="red", command=stop)
stop.grid(row=11, column=1)'''
currentime = time.strftime("%d/%m/%y %H:%M:%S")
startime = Label(dateborder, text="START:"+str(currentime), font=("Helvetica", 18))
startime.grid(row=13, columns=2, sticky=W)
stoptime = Label(dateborder, text="STOP:", font=("Helvetica", 18))
stoptime.grid(row=14, columns=2, sticky=W)

monmenu = Menu(menubar, tearoff=0)
monmenu.add_command(label="START", command=start, foreground="green")
monmenu.add_command(label="STOP", command=stop, foreground="red")

menubar.add_cascade(label="Monitoring", menu=monmenu)

filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Save to file")
filemenu.add_command(label="Save to database")
menubar.add_cascade(label="File", menu=filemenu)

root.config(menu=menubar)

root.protocol("WM_DELETE_WINDOW", on_x)

tyk()
update_timer()
m.start()
root.after(400, display)
root.mainloop()
