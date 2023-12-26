from datetime import datetime, timedelta
from tkinter import (NSEW, Frame, Label, Spinbox, StringVar,
	Variable, ttk, BOTH, NW, W)
from lib.rbconfig import RaceboxConfig
from lib.rbutility import ENTRY_FONT, FIXED_FONT_LARGE

class SignalsInterface:
	sequenceList = [
        {'name': '10-5-Go', 'interval': 5, 'warning': [-10,-5]},
        {'name': '5-4-1-Go', 'interval': 5, 'warning': [-5,-4,-1]},
        {'name': '3-2-1-Go', 'interval': 4, 'warning': [-3,-2,-1]}
    ]
	
	sequenceListLights = [
        {'name': 'No lights', 'on': 0, 'flash': 0},
        {'name': 'On: 1m, Flash: 10s', 'on': 60, 'flash': 10},		
	]
 
	#signal status definitions
	SIGNAL_OLD = 1
	SIGNAL_NOW = 0
	SIGNAL_FUTURE = -1
 
	SIGNAL_MAX_AGE = 1500 #ms beyond this a signal is too late to be used
	COUNTDOWN_PRECISION = 500 #ms -- how often the time is checked
 
	def __init__(self, fControl: ttk.Frame, relay):

		self.countdownActive = False
		self.relay = relay
		self.config = RaceboxConfig()
		self.on2Off = float(self.config.get('Signals', 'defaultOn2Off'))

		#create internal frames
		fMain = Frame(fControl)
		fMain.pack(expand=False, fill=BOTH, padx=(25,0), pady=(25,0))

		self.fCountdown = Frame(fMain)
		
		self.fSigConfig = Frame(fMain)
		self.fSigConfig.pack(expand=False, fill=BOTH)
		
		fBtnPanel = Frame(fControl)
		fBtnPanel.pack(expand=False, fill=BOTH, padx=(25,0))
		
		self.startBtn = ttk.Button(fBtnPanel, text='Start Countdown', command=self.__changeCountdownStatus, style='Custom.TButton')
		self.startBtn.pack(anchor=NW, pady=(40,0))
  
		self.__initConfigInterface(self.fSigConfig)
		self.__initCountdownInterface(self.fCountdown)
		
	def __updateCountdownBtnPanel(self):
		if self.countdownActive:
			self.fSigConfig.forget()
			self.fCountdown.pack(expand=False, fill=BOTH)
			self.startBtn.config(text='Stop Countdown')
		else:
			self.fCountdown.forget()
			self.fSigConfig.pack(expand=False, fill=BOTH)
			self.startBtn.config(text='Start Countdown')
   
	def __changeCountdownStatus(self):
		if self.countdownActive: self.__stopCountdown()
		else: self.__startCountdown()
   
	def __startCountdown(self):
		self.countdownActive = True
		self.configChange = False
		self.__countdown()
		self.__updateCountdownBtnPanel()
   
	def __stopCountdown(self):
		self.countdownActive = False
		self.__updateCountdownBtnPanel()
  
	def __countdown(self):
		if not self.relay.active: print('no active relay')
		signalsConfig = self.__getSignalsConfig()
		[signals, starts] = self.__getSignalList(signalsConfig)
		self.__countdownLoop(signals, starts, len(starts), signalsConfig['name'])
   
	def __countdownLoop(self, signals, starts, startCount, seqName):
		if not self.countdownActive: return
		if len(signals) > 0:
			tooLate = signals[0] + timedelta(milliseconds=SignalsInterface.SIGNAL_MAX_AGE)
			chk = self.__checkNextSignal(signals[0], tooLate)
			if chk == SignalsInterface.SIGNAL_NOW:
				self.relay.onoff(self.fCountdown, self.on2Off)
			if chk == SignalsInterface.SIGNAL_OLD or chk == SignalsInterface.SIGNAL_NOW:
				if signals[0] == starts[0]: starts.pop(0)
				rm = signals.pop(0)
		if self.configChange:
			signalsConfig = self.__getSignalsConfig()
			[signals, starts] = self.__getSignalList(signalsConfig)		
			startCount = len(starts)	
			self.configChange = False		
		self.__updateCountdownDisplay(signals, starts, startCount, seqName)
		self.fCountdown.after(SignalsInterface.COUNTDOWN_PRECISION, self.__countdownLoop, signals, starts, startCount, seqName)
  
	def __checkNextSignal(self, signal, tooLate):
		now = datetime.now()
		if now >= tooLate: return SignalsInterface.SIGNAL_OLD
		if signal < now < tooLate: return SignalsInterface.SIGNAL_NOW
		return SignalsInterface.SIGNAL_FUTURE

	def __getSignalsConfig(self):
		return {
			'name': self.selectedSequenceName.get(),
			'starts': int(self.startsCount.get()),
			'startHour': int(self.hhValue.get()),
			'startMinute': int(self.mmValue.get())
        }
   
	def __getSignalList(self, config):
		sequenceIndex = -1
		for sequenceIndex, item in enumerate(SignalsInterface.sequenceList):
			if item['name'] == config['name']: break
		if sequenceIndex == -1: return []
		signalList = []
		startList = []
		now = datetime.now()
		firstStart = now.replace(hour=config['startHour'], minute=config['startMinute'], second=0, microsecond=0)
		currentStart = firstStart
		startInterval = SignalsInterface.sequenceList[sequenceIndex]['interval']
		for _ in range(config['starts']):
			for warning in SignalsInterface.sequenceList[sequenceIndex]['warning']:
				warningTime = currentStart - timedelta(minutes=abs(warning))
				if warningTime not in signalList: signalList.append(warningTime)
			if currentStart not in signalList:
				signalList.append(currentStart)
				startList.append(currentStart)
			currentStart = currentStart + timedelta(minutes=startInterval)
		return [signalList, startList]

	def __updateCountdownDisplay(self, signals, starts, startCount, seqName):
		self.lNumberOfStartsValue.config(text=startCount)
		if len(signals) < 1:
			self.lTime2Start.config(text='00:00:00')
			self.lNextStartTime.config(text='00:00:00')
			self.lLastStartValue.config(text='00:00:00')
			return
		self.lNextStartTime.config(text="{:%H:%M:%S}".format(starts[0]))
		self.lLastStartValue.config(text="{:%H:%M:%S}".format(starts[-1]))
		now = datetime.now()
		if now < starts[0]:
			time2Start = starts[0] + timedelta(seconds=1) - now
			t2Shours, remainder = divmod(time2Start.total_seconds(), 3600)
			t2Sminutes, t2Sseconds = divmod(remainder, 60)
			self.lTime2Start.config(text='{:02}:{:02}:{:02}'.format(int(t2Shours), int(t2Sminutes), int(t2Sseconds)))
		else:
			self.lTime2Start.config(text='00:00:00')
		self.lSequenceValue.config(text=seqName)
  
	def __addStart(self):
		currentStarts = int(self.startsCount.get())
		self.startsCount.set(str(currentStarts+1))
		self.configChange = True
      
	def __initCountdownInterface(self, f: ttk.Frame):
		#grid options
		f.rowconfigure(0, minsize=50)
		f.rowconfigure(1, minsize=50)
		f.rowconfigure(2, minsize=40)
		f.rowconfigure(3, minsize=40)
		f.rowconfigure(4, minsize=40)
		f.columnconfigure(0, pad=25)

		#next start time label
		lNextStartTxt = Label(
			f,
			text='Next Start Time'
		)
		lNextStartTxt.grid(column=0,row=0,sticky=W)
		
		self.lNextStartTime = ttk.Label(
			f,
			text='00:00:00',
			style='CourierLargeBold.TLabel',
			background='plum',
			padding=(8,12,8,4) #left top right bottom
		)
		self.lNextStartTime.grid(column=1,row=0, pady=(4,4))
		
		#countdown to next start label
		lTime2StartTxt = Label(
			f,
			text='Time To Start'
		)
		lTime2StartTxt.grid(column=0,row=1,sticky=W)
		
		self.lTime2Start = ttk.Label(
			f,
			text='00:00:00',
			style='CourierLargeBold.TLabel',
			background='orange',
			padding=(8,12,8,4) #left top right bottom   
		)
		self.lTime2Start.grid(column=1,row=1)
		
		#number of starts plain label
		lNumberOfStartsTxt = Label(
			f,
			text='Number Of Starts'
		)
		lNumberOfStartsTxt.grid(column=0,row=2,sticky=W)		
		self.lNumberOfStartsValue = Label(
			f,
			text='0',
			anchor=W
		)
		self.lNumberOfStartsValue.grid(column=1,row=2,sticky=W)	
		
		#final start time plain label
		lLastStartTxt = Label(
			f,
			text='Final Start Time'
		)
		lLastStartTxt.grid(column=0,row=3,sticky=W)		
		self.lLastStartValue = Label(
			f,
			text='00:00:00',
			anchor=W
		)
		self.lLastStartValue.grid(column=1,row=3,sticky=W)	
  
		#start sequence
		lSequenceTxt = Label(
			f,
			text='Sequence'
		)
		lSequenceTxt.grid(column=0,row=4,sticky=W)		
		self.lSequenceValue = Label(
			f,
			text='',
			anchor=W
		)
		self.lSequenceValue.grid(column=1,row=4,sticky=W)	  
		
		#general recall/add start button
		lAddStartTxt = Label(
			f,
			text='General Recall'
		)
		lAddStartTxt.grid(column=0,row=5,sticky=W)		
		lAddStartBtn = ttk.Button(
			f,
			text='Add Start',
   			command=self.__addStart,
   			style='Custom.TButton'
		)
		lAddStartBtn.grid(column=1,row=5,sticky=W)	

	def __initConfigInterface(self, f: ttk.Frame):
		# start time
		fStartTime = Frame(f)
		fStartTime.grid(column=0,row=0,sticky=W) 
		startTimeLabel = Label(
			fStartTime,
			text='First Start'
		)
		startTimeLabel.grid(column=0,row=0,sticky=W) 
	
		fStartTime = Frame(f)
		fStartTime.grid(column=0,row=1,sticky=W) 
		self.hhValue = Variable(value='14')
		hhEntry = Spinbox(fStartTime, from_=0, to=23, textvariable=self.hhValue, format="%02.0f", state='readonly', font=ENTRY_FONT)
		hhEntry.pack(side='left')
		hhEntry.config(width=3)
		self.mmValue = Variable(value='30')
		mmEntry = Spinbox(fStartTime, from_=0, to=59, textvariable=self.mmValue, format="%02.0f", state='readonly', font=ENTRY_FONT)
		mmEntry.pack(side='left', padx=(4, 0))
		mmEntry.config(width=3)
	
		# number of starts
		startsLabel = Label(
			f,
			text='Number Of Starts'
		)
		startsLabel.grid(column=0,row=3,sticky='w', pady=(15, 0))
	
		self.startsCount = StringVar(value=1)
		startsEntry = Spinbox(f, from_=1, to=33, textvariable=self.startsCount, state='readonly', font=ENTRY_FONT)
		startsEntry.grid(column=0,row=4,sticky='w')
		startsEntry.config(width=2)
	
		# start sequence type
		startSigLabel = Label(
			f,
			text='Start Sequence'
		)
		startSigLabel.grid(column=0,row=5,sticky='w', pady=(15, 0))
  
		sequenceNames = []
		for s in SignalsInterface.sequenceList: sequenceNames.append(s['name'])
		### https://www.pythontutorial.net/tkinter/tkinter-combobox/
		self.selectedSequenceName = StringVar()
		startSigEntry = ttk.Combobox(f, values=sequenceNames, textvariable=self.selectedSequenceName, state='readonly', font=ENTRY_FONT)
		defaultSequence = int(self.config.get('Signals', 'defaultSequence'))
		self.selectedSequenceName.set(sequenceNames[defaultSequence])
		startSigEntry.grid(column=0,row=6,sticky=W)			
			
		# light sequence type
		lightSigLabel = Label(
			f,
			text='Lights Sequence'
		)
		lightSigLabel.grid(column=0,row=7,sticky='w', pady=(15, 0))

		lightSeqNames = []
		for s in SignalsInterface.sequenceListLights: lightSeqNames.append(s['name'])
		### https://www.pythontutorial.net/tkinter/tkinter-combobox/
		self.selectedLightSeqName = StringVar()
		startLightSigEntry = ttk.Combobox(f, values=lightSeqNames, textvariable=self.selectedLightSeqName, state='readonly', font=ENTRY_FONT)
		defaultLightSequence = int(self.config.get('Lights', 'defaultSequence'))
		self.selectedLightSeqName.set(lightSeqNames[defaultLightSequence])
		startLightSigEntry.grid(column=0,row=8,sticky=W)			
   