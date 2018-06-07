import wx, threading, Queue, sys, time
from wx.lib.newevent import NewEvent
import spidev
import time
import math
from time import strftime
import os

spi = spidev.SpiDev()
spi.open(0, 0)
filename = strftime("%d-%b-%Y %H_%M_%S")

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
    #print ("%4d/4095 => %5.4f V => %6.1f ? => %5.2f °K => %3.1f °C from adc %d" % (value, volts, ohms, temp, tempc, adc))
    #log.write("%4d,%5.4fV,%6.1f,%5.2f,%3.1f,adc %d" % (value, volts, ohms, temp, tempc, adc))
    print ("%3.1f °C sensor %d" % (tempc, adc))
    return tempc

make_sure_path_exists("./data")

ID_BEGIN=100
wxStdOut, EVT_STDDOUT= NewEvent()
wxWorkerDone, EVT_WORKER_DONE= NewEvent()

def LongRunningProcess(lines_of_output):
    while True:
        Temp=[]
        for ch in range(lines_of_output):
            Temp.append(get_temperature(ch))
        print Temp
        time.sleep(10)
        #write to log
        log = open("./data/"+filename+'.csv', 'a') #open a text file for logging
        log.write(strftime("%d/%m/%y,%H:%M:%S"))
        for x in range (0,8):
            log.write(",%3.1f" % (get_temperature(x)))
        log.write(strftime("\n"))
        log.close()

class MainFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(800, 600))
        self.requestQ = Queue.Queue() #create queues
        self.resultQ = Queue.Queue()
                
        #widgets
        p = wx.Panel(self)
        self.output_window = wx.TextCtrl(p, -1, 
                             style=wx.TE_AUTO_SCROLL|wx.TE_MULTILINE|wx.TE_READONLY)
        self.go = wx.Button(p, ID_BEGIN, 'Start')
        self.output_window_timer = wx.Timer(self.output_window, -1)
        #self.stop = wx.Button(p, ID_STOP, 'Stop')

        #frame sizers
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.output_window, 10, wx.EXPAND)
        sizer.Add(self.go, 1, wx.EXPAND)
        #sizer.Add(sef.stop, 1, wx.EXPAND)
        p.SetSizer(sizer)
       
        #events
        wx.EVT_BUTTON(self, ID_BEGIN, self.OnBeginTest)
        self.output_window.Bind(EVT_STDDOUT, self.OnUpdateOutputWindow)
        self.output_window.Bind(wx.EVT_TIMER, self.OnProcessPendingOutputWindowEvents)
        self.Bind(EVT_WORKER_DONE, self.OnWorkerDone)
        
        #thread
        self.worker = Worker(self, self.requestQ, self.resultQ)

    def onToggle(self, event):
        lines_of_output=8
        self.worker.beginTest(LongRunningProcess, lines_of_output)
        self.output_window_timer.Start(50)
        btnLabel = self.go.GetLabel()
        if btnLabel == "Start":
            self.go.SetLabel("Stop")
        else:
            self.output_window_timer.Stop()
            self.go.Enable()
            self.go.SetLabel("Start")


    def OnUpdateOutputWindow(self, event):
        value = event.text
        self.output_window.AppendText(value)
              
    def OnBeginTest(self, event):
        lines_of_output=8
        self.go.Disable()
        self.worker.beginTest(LongRunningProcess, lines_of_output)
        self.output_window_timer.Start(50)
    
    def OnWorkerDone(self, event):
        self.output_window_timer.Stop()
        self.go.Enable()

    def OnProcessPendingOutputWindowEvents(self, event):
        self.output_window.ProcessPendingEvents()

class Worker(threading.Thread):
    requestID = 0
    def __init__(self, parent, requestQ, resultQ, **kwds):
        threading.Thread.__init__(self, **kwds) 
        self.setDaemon(True) 
        self.requestQ = requestQ
        self.resultQ = resultQ
        self.start() 
        
    def beginTest(self, callable, *args, **kwds):
        Worker.requestID +=1
        self.requestQ.put((Worker.requestID, callable, args, kwds))
        return Worker.requestID

    def run(self):
        while True:
            requestID, callable, args, kwds = self.requestQ.get()
            self.resultQ.put((requestID, callable(*args, **kwds))) 
            evt = wxWorkerDone()
            wx.PostEvent(wx.GetApp().frame, evt)
                               
class SysOutListener:       
    def write(self, string):
        sys.__stdout__.write(string)
        evt = wxStdOut(text=string)
        wx.PostEvent(wx.GetApp().frame.output_window, evt)
    
class MyApp(wx.App):
    def OnInit(self):
        self.frame = MainFrame(None, -1, 'Temperature data')
        self.frame.Show(True)
        self.frame.Center()
        return True
 
#entry point
if __name__ == '__main__':
    app = MyApp(0)
    sys.stdout = SysOutListener()
    app.MainLoop()
