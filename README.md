# Racebox
Automated race signals and easy finish timing for dinghy racing

* Provides a connection to USB relays in order to control a horn system
* Supports 10-5-Go, 5-4-1-Go and 3-2-1-Go start sequences
* Has a simple way to record finishes on the "Finish Times" tab

Screenshots and more details are over at the [Rotor-Rig.com website](https://www.rotor-rig.com/racebox)

More detailed installation and configuration information is in the [wiki](https://github.com/rotor-rig/racebox/wiki)

Currently the common/inexpensive USB serial relays are supported\
that use the instruction set for the CH340 (or CH341)\
and some USB HID relays are also supported

These relays quite often have the "Songle" name on the components

![USB relay](https://github.com/Ian-Rotor-Rig/racebox/assets/90469594/fbae9351-5044-4e16-924e-9634cf990999)

The 1, 2 and 4 channel relays should work. It is not too hard to extend the\
code in rbrelayconfig.py to support other relays if you have the instruction set.

The PL2303 USB serial relay is supported\
this often has a micro USB socket and www.icstation.com printed underneath\
and/or "Hong Wei" on the relay components.\
In rbconfig.ini in the "Relays" section a line must be added for this:\
**serialdriver = pl2303**

The RT232R USB serial relay is supported\
this is made by [KMTronic](https://www.kmtronic.com/usb-relays.html) using FTDI components\
In rbconfig.ini in the "Relays" section a line must be added for this:\
**serialdriver = rt232r**

## Configuration File
The configuration file **rbconfig.ini** is created when the program is started.\
The options are:

\[Signals\]\
defaulton2off = 0.75 (seconds - the length of a normal hoot)\
finishon2off = 0.25 (seconds - the length of a finish hoot)\
defaultsequence = 0 (the signal sequence selected in the interface 0=first 1=second etc)

\[Relays\]\
serialrelayport = /dev/ttyUSB0 (the serial port used - Windows is COM1 COM2 COM3 etc, Linux is /dev/ttyUSB0, /dev/ttyUSB1 etc)

\[Files\]\
finshfileusedefaultfolder = True (True or False - use the home directory for the current user)\
finishfilefolder = /Documents/ (the folder to save finish times documents in)

## Running Racebox
Once installed Racebox is run like this:\
**python3 racebox.py**

(on Windows it is python rather than python3)

## Required software
python3.x (latest version) including pip and tcl/tk (often installed by default)

### Windows
Download the installer available on the python.org website

The [Python installer](https://www.python.org/downloads) offers two options:\
Use admin privileges when installing py.exe and\
Add python.exe to PATH\
and you should enable both of these.

In addition to Python, install support for serial (via the Command Propmpt):\
**pip install pyserial**

Then - go to the Device Manager and check which serial port the relay is on.\
Edit the **rbconfig.ini** file and change the **serialrelayport =** line to match\
for example, **serialrelayport = COM3**

NB: HID relays on Windows appear to have issues\
it may be better to choose a USB serial relay (such as a CH340) for this operating system

The [Digital Ocean](https://www.digitalocean.com/community/tutorials/install-python-windows-10) guide is excellent\
The required "pip" and "tcl/tk (tkinter)" options are normally installed by default.

### Ubuntu (and many other Linux distros)
Python3 is usually pre-installed. Check by typing in terminal:\
python3 -V

On some distros you may also need to install\
sudo apt install python3-tk\
sudo apt install python3-pip

#### Required software for serial devices
pyserial - to install type:

sudo apt install python3-serial\
OR\
pip3 install pyserial (Ubuntu)\
(you may need to add --break-system-packages as an option at\
the end of the pip3 command - it is a long story)

On Ubuntu the braille display kernel module prevents these serial devices working correctly\
and should be removed. This is caused by a conflict between product ids:

sudo apt remove brltty

#### Required software for HID devices
Read these instructions: [PyPi HID](https://pypi.org/project/hid/)

sudo apt install usbrelay\
(this seems to solve some permissions issues and adds the required hidraw package)

pip3 install hid\
(there is no alternative apt package that provides the correct module)

#### Ubuntu groups
To work on Linux the user must be in the dialout group\
(some docs also suggest plugdev)

sudo usermod -a -G dialout myusername

### HID Relay Miscellaneous Information

The python-hidapi is one way to address HID relays

In Ubuntu, install usbrelay\
sudo apt install usbrelay

Then plug in your relay and type:

usbrelay

this prints:
Device Found
  type: 16c0 05df
  path: /dev/hidraw3
  serial_number: 
  Manufacturer: www.dcttech.com
  Product:      USBRelay2
  Release:      100
  Interface:    0
  Number of Relays = 2
BITFT_1=0
BITFT_2=0

then:

usbrelay BITFT_1=1

turns on the first relay and:

usbrelay BITFT_1=0

turns it off.

NB usbrelay does not show information for USB serial relays, only HID.
