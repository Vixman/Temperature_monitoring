#!/usr/bin/python
# -*- coding: utf-8 -*-
#from wxPython.wx import *
import wx
import csv

class Ramka(wx.Frame):

    def OtworzDane(self, event):
        dialog=wx.FileDialog(self, message='Wybierz plik', defaultFile='',wildcard='*.txt',
                         style=wx.OPEN | wx.MULTIPLE | wx.CHANGE_DIR)
        if dialog.ShowModal() == wx.ID_OK:
            plik=dialog.GetPaths()
            print plik
            plik_dane=open(plik[0], 'r')
            odczyt = plik_dane.readlines()
            plik_dane.close()      
            Temp = []
            Daty = []
            reader = csv.reader(odczyt, delimiter=';')
            for row in reader:
                Daty.append(row[0])
                Temp.append(row[1])
            return Daty, Temp


    
    def Zamknij(self, event):
        dialog=wx.MessageDialog(self, 'Czy na pewno?', 'Kończymy pracę', style=wx.OK | wx.CANCEL)
        x=dialog.ShowModal()
        dialog.Destroy()
        if x == wx.ID_OK:
            self.Close()



    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Monitorowanie Temperatury", size=(1024,760))
        panel = wx.Panel(self, wx.ID_ANY)
        self.index = 0
    
            
        MenuListwa=wx.MenuBar()
        ProgMenu=wx.Menu()
        ProgMenuItem1=ProgMenu.Append(wx.ID_ANY,'Temperatura jaj','Czytaj Dane')
        self.Bind(wx.EVT_MENU, self.OtworzDane, ProgMenuItem1)
        MenuListwa.Append(ProgMenu,'Dane')

        ProgMenu=wx.Menu()
        ProgMenuItem1=ProgMenu.Append(wx.ID_EXIT, 'Koniec', 'Koniec programu')
        MenuListwa.Append(ProgMenu, 'Wyjscie')
        self.Bind(wx.EVT_MENU, self.Zamknij, ProgMenuItem1)
        self.SetMenuBar(MenuListwa)

        
        self.list_ctrl = wx.ListCtrl(panel, size=(-1,600),
                         style=wx.LC_REPORT
                         |wx.BORDER_SUNKEN
                         )
        self.list_ctrl.InsertColumn(0, 'Rekord', width=100)
        self.list_ctrl.InsertColumn(1, 'Data', width=200)
        self.list_ctrl.InsertColumn(2, 'Temperatura', width=800)
 
        btn = wx.Button(panel, label='Dodaj rekordy')
        btn.Bind(wx.EVT_BUTTON, self.dodaj_rekordy)
 
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list_ctrl, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Add(btn, 0, wx.ALL|wx.CENTER, 5)
        panel.SetSizer(sizer)
 


    def dodaj_rekordy(self, event):
        while True:
            line = "Rekord %s" % self.index
            self.list_ctrl.InsertStringItem(self.index, line)
            dodaj1 = self.list_ctrl.SetStringItem(self.index, 1, Daty[self.index])
            dodaj2 = self.list_ctrl.SetStringItem(self.index, 2, Temp[self.index])
            for i in Daty:
                dodaj1 += self.list_ctrl.SetStringItem(self.index, 1, Daty[self.index])
            for j in Temp:
                dodaj2 += self.list_ctrl.SetStringItem(self.index, 2, Temp[self.index])
            self.index += 1


			
if __name__ == "__main__":
    app = wx.App(False)         
    frame = Ramka()
    frame.Show()
    frame.Update()
    app.MainLoop()
