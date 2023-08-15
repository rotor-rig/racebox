#from tkinter import *
from tkinter import (TOP, font, ttk, PhotoImage, Button, messagebox, Frame,
	BOTTOM, X,Y,BOTH, Tk, Canvas, W,E,N,S,NW, LEFT, RIGHT, CENTER)
from rbextras import ExtrasInterface
from rbfinishtimes import FinishTimesInterface
from rbsignals import SignalsInterface
from datetime import datetime
from rbserial import USBSerialRelay
from rbhid import USBHIDRelay
from rbconfig import RaceboxConfig

# Create the main window
mainWindow = Tk()
mainWindow.title('Racebox')
mainWindow.minsize(width=600, height=500)

#default font
default_font = font.nametofont("TkDefaultFont")
default_font.configure(size=12)

# window icon
icon = PhotoImage(file='racebox192.png')
mainWindow.iconphoto(False, icon)

# header colour
hdrColour = 'black'

# Styles
s = ttk.Style()
#s.theme_use('alt')
s.configure('Control.TFrame', borderwidth=4, relief='flat')
s.configure('Setup.TFrame', borderwidth=4, relief='flat')
s.configure('Header.TFrame', background=hdrColour)
s.configure('Footer.TFrame', background='black')
s.configure('Custom.TNotebook', tabposition='ne', background='indigo')
s.configure('TNotebook.Tab', background='limegreen', padding=[8, 4]) #lightcolor= not for this theme
s.configure('Custom.TButton', background='silver', padding=(8,4))

#general config
config = RaceboxConfig()

#USB relay
raceboxRelay = USBHIDRelay()
serialPort = config.get('Relays', 'serialRelayPort')
if not raceboxRelay.active: raceboxRelay = USBSerialRelay(serialPort)
if not raceboxRelay.active: print('no USB relay found')

#header
headerFrame = ttk.Frame(mainWindow, style='Header.TFrame')
headerCanvas = Canvas(headerFrame, bg=hdrColour, bd=0, width=50, height=50, highlightthickness=0)
headerCanvas.grid(column=0,row=0,padx=(0,0), ipady=2, sticky=W)
rbLogoSmall = PhotoImage(file='racebox50.png')
headerCanvas.create_image(2,2, anchor=NW, image=rbLogoSmall)

hdrLabel = ttk.Label(
    headerFrame,
    text='Racebox',
    foreground='whitesmoke',
    background=hdrColour,
    font=('Helvetica', 14, 'bold')
)
hdrLabel.grid(column=1,row=0,padx=(0,0))

# main screen
n = ttk.Notebook(mainWindow, style='Custom.TNotebook',padding='0 4 0 0')
signalsFrame = ttk.Frame(n, style='Control.TFrame', padding='10 10 10 10')
finishTimesFrame = ttk.Frame(n, style='Control.TFrame')
extrasFrame = ttk.Frame(n, style='Control.TFrame')
n.add(signalsFrame, text='Auto Signals')
n.add(extrasFrame, text='Manual Signals')
n.add(finishTimesFrame, text='Finish Times')

#add widgets to each control frame
SignalsInterface(signalsFrame, raceboxRelay)
FinishTimesInterface(finishTimesFrame, raceboxRelay)
ExtrasInterface(extrasFrame, raceboxRelay)

#footer
footerFrame = ttk.Frame(mainWindow, style='Footer.TFrame')
footerFrame.grid_columnconfigure(0, weight=1)
footerFrame.grid_columnconfigure(1, weight=1)
footerFrame.grid_columnconfigure(2, weight=1)

logoFrame = ttk.Frame(footerFrame, style='Footer.TFrame')
logoFrame.grid(column=0,row=0,padx=(0,0), sticky=W)

footerCanvas = Canvas(logoFrame, bg="black", bd=0, width=60, height=60, highlightthickness=0)
footerCanvas.grid(column=0,row=0,padx=(0,0))
rotorRigLogoSmall = PhotoImage(file='sail50.png')
footerCanvas.create_image(2,2, anchor=NW, image=rotorRigLogoSmall)

rrLabel = ttk.Label(
    logoFrame,
    text='Rotor-Rig.com',
    foreground='darkorange',
    background='black',
    font=('Sans-Serif', 12)
)
rrLabel.grid(column=1,row=0,padx=(0,0))

timeLabel = ttk.Label(
    footerFrame,
    text='Time',
    foreground='lime',
    background='black',
    font=('Monospace', 14, 'bold')
)
timeLabel.grid(column=1,row=0,padx=(0,0))

#pack the main screen
#packing the header and footer before the middle
#means the middle will be reduced first when window is resized
headerFrame.pack(side=TOP, fill=X)
footerFrame.pack(side=BOTTOM, fill=X)
n.pack(expand=True, fill=BOTH)

def __hootSound():
    on2Off = float(config.get('Signals', 'defaultOn2Off'))
    raceboxRelay.onoff(mainWindow, on2Off)

hootBtn = ttk.Button(footerFrame, text='Hoot', command=__hootSound, style='Custom.TButton')
hootBtn.grid(column=2,row=0, sticky=E, padx=(0,10))

def clockLoop():
    #time
    now = datetime.now()
    nowText = now.strftime('%H:%M:%S')
    timeLabel.config(text=nowText)       
    mainWindow.after(1000, clockLoop)

# Start the timing loop
clockLoop()

# Run forever!
mainWindow.mainloop()
