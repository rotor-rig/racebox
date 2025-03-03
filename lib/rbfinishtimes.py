from datetime import datetime
import json
import os
from tkinter import (ALL, BOTH, BOTTOM, CENTER, LEFT, NW, RIGHT, E, SW, W, X, Y,
                     Canvas, Frame, Label, LabelFrame, Scrollbar, Spinbox, StringVar, messagebox, ttk)
import tkinter as tk
from lib.rbconfig import RaceboxConfig
from lib.rbresults import ResultsInterface
from lib.rbutility import (MONTH_ABBREV, TITLE_FONT, STATUS_CODES, STATUS_FINISHED, getAutoSaveFileName,
                           getFinishFileName, getJSONFinishData, getUniqueId, processFinishInfo,
                           saveToCSVFile, setJSONFinishData, onlyNumbers)

class FinishTimesInterface:
    def __init__(self, fControl: ttk.Frame, fResults: ttk.Frame, relay):
        self.pos = 1
        self.finishList = []
        self.relay = relay
        self.config = RaceboxConfig()

        with open('classes.json') as jsonFile:
            self.classList = json.load(jsonFile)
        self.classNames = [c['name'] for c in self.classList]

        self.statusCodes = STATUS_CODES
        self.statusCodes.insert(0, '')

        self.ri = ResultsInterface(fResults)

        asInfo = self.__restoreFinishGridInfo()
        self.raceId = asInfo.get('id', getUniqueId())
        self.finishData = asInfo['data']

        self.fc = fControl

        f = Frame(self.fc)
        f.pack(expand=True, fill=BOTH)

        lf = Frame(f)
        lf.pack(side=LEFT, fill=BOTH, expand=True)

        self.validateNumbers = (lf.register(onlyNumbers), '%S')

        abFrame = LabelFrame(lf, text='Approaching Boats', font=TITLE_FONT)
        abFrame.pack(side=BOTTOM, anchor=SW, ipadx=4, padx=4, pady=(16, 4))
        self.__drawApproachingBoats(abFrame)

        self.raceDetailsFrame = Frame(lf)
        self.raceDetailsFrame.pack(anchor=W, padx=10, pady=10)

        raceNameFrame = Frame(self.raceDetailsFrame)
        raceNameFrame.pack(pady=(2, 12))

        lraceName = Label(raceNameFrame, text='Race name')
        lraceName.pack(side=LEFT, anchor=W)

        self.raceNameValue = StringVar()
        self.raceNameValue.set(asInfo.get('name', ''))
        enRaceName = ttk.Entry(raceNameFrame, textvariable=self.raceNameValue, width=25)
        enRaceName.bind('<KeyRelease>', lambda e: self.autoSaveAction())
        enRaceName.pack(side=LEFT, anchor=W, padx=(4, 0))

        lracedate = Label(raceNameFrame, text='Date')
        lracedate.pack(side=LEFT, anchor=W, padx=(20, 0))

        self.raceDayValue = StringVar(value='01')
        enRaceDay = Spinbox(raceNameFrame, from_=1, to=31, textvariable=self.raceDayValue,
                            format="%02.0f", state='readonly', width=4)
        self.raceDayValue.trace_add('write', callback=lambda a, b, c: self.autoSaveAction())
        enRaceDay.pack(side=LEFT, padx=(4, 0))

        self.raceMonthValue = StringVar(value=MONTH_ABBREV[0])
        enRaceMonth = ttk.Combobox(raceNameFrame, values=MONTH_ABBREV, textvariable=self.raceMonthValue,
                                   state='readonly', width=6)
        enRaceMonth.bind('<KeyRelease>', lambda e: self.autoSaveAction())
        enRaceMonth.bind('<<ComboboxSelected>>', lambda e: self.autoSaveAction())
        enRaceMonth.pack(side=LEFT, padx=(2, 0))

        self.raceYearValue = StringVar(value='1970')
        enRaceYear = Spinbox(raceNameFrame, from_=2020, to=2999, textvariable=self.raceYearValue,
                             format="%04.0f", state='readonly', width=6)
        self.raceYearValue.trace_add('write', callback=lambda a, b, c: self.autoSaveAction())
        enRaceYear.pack(side=LEFT, padx=(2, 0))
        self.setRaceDate(asInfo if 'id' in asInfo else False)

        lraceTimesTitle = Label(self.raceDetailsFrame, text='Finish Times', font=TITLE_FONT)
        lraceTimesTitle.pack(anchor=W, pady=(5, 0))

        self.canvas = Canvas(lf, highlightthickness=0)
        sb = Scrollbar(lf, orient='vertical', command=self.canvas.yview)
        self.finishFrame = Frame(self.canvas)
        cw = self.canvas.create_window((0, 0), window=self.finishFrame, anchor=NW)
        self.canvas.configure(yscrollcommand=sb.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=True, padx=2)
        sb.pack(side=RIGHT, fill=Y)
        self.finishFrame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox(ALL)))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(cw, width=e.width))

        self.rowFrame = Frame(self.finishFrame)
        self.rowFrame.pack(fill=X, expand=True)

        rf = Frame(f)
        rf.pack(side=LEFT, ipadx=10, padx=25, fill=Y)

        btnFinish = ttk.Button(rf, text="Finish", command=self.finishAction, style='Custom.TButton')
        btnFinish.pack(anchor=W, pady=(50, 0))

        btnNoFinish = ttk.Button(rf, text="Non-Finisher", command=self.nonFinishAction, style='Custom.TButton')
        btnNoFinish.pack(anchor=W, pady=(50, 0))

        rbf = LabelFrame(rf, text='Use After Races')
        rbf.pack(side=BOTTOM, anchor=W, pady=(0, 25), ipady=20, ipadx=5)

        btnReset = ttk.Button(rbf, text="Save Finishes", command=self.saveToFileAction, style='Custom.TButton')
        btnReset.pack(expand=True, anchor=CENTER)
        btnReset = ttk.Button(rbf, text="Reset Finish Box", command=self.resetFinishBoxAction, style='Custom.TButton')
        btnReset.pack(expand=True, anchor=CENTER)

        self.__addFinishHdr(self.rowFrame)

        if len(asInfo['data']) > 0:
            for row in range(len(asInfo['data'])):
                self.__addFinishRow(self.rowFrame)
                if asInfo['data'][row]['pos'] != 0:
                    self.pos = asInfo['data'][row]['pos'] + 1
            self.__populateFinishGrid(self.rowFrame, asInfo['data'])

    def setRaceDate(self, dt=False):
        if not dt:
            x = datetime.today()
            dd = '{:02}'.format(x.day)
            mm = MONTH_ABBREV[x.month - 1]
            yy = x.year
        else:
            dd = '{:02}'.format(dt['date']['day'])
            mm = MONTH_ABBREV[dt['date']['month'] - 1]
            yy = dt['date']['year']
        self.raceDayValue.set(value=dd)
        self.raceMonthValue.set(value=mm)
        self.raceYearValue.set(value=yy)

    def finishAction(self, abClass='', abSail=''):
        on2Off = float(self.config.get('Signals', 'finishOn2Off'))
        self.relay.onoff(self.fc, on2Off)
        finishData = self.__addFinishData(True, abClass, abSail)
        self.finishData.append(finishData)
        self.pos += 1
        self.autoSaveAction()
        self.__addFinishRow(self.rowFrame)
        self.__populateFinishGrid(self.rowFrame, self.finishData)

    def nonFinishAction(self):
        finishData = self.__addFinishData(False)
        self.finishData.append(finishData)
        self.autoSaveAction()
        self.__addFinishRow(self.rowFrame)
        self.__populateFinishGrid(self.rowFrame, self.finishData)

    def __addFinishData(self, finisher=True, classValue='', sailValue=''):
        now = datetime.now()
        newFinishData = {
            'pos': self.pos if finisher else 0,
            'clock': {'hh': now.hour, 'mm': now.minute, 'ss': now.second, 'ms': now.microsecond / 1000},
            'class': StringVar(value=classValue),
            'sailnum': StringVar(value=sailValue),
            'race': StringVar(value='1'),
            'status': StringVar(),
            'notes': StringVar()
        }
        if finisher:
            newFinishData['status'].set('Finished')
        return newFinishData

    def __populateFinishGrid(self, f, rowData):
        rows = len(rowData)
        if rows < 1:
            return
        for r in range(rows):
            gridRow = rows - r
            cell = f.grid_slaves(row=gridRow, column=0)
            cell[0].configure(text='{:>3}'.format(rowData[r]['pos']) if rowData[r]['pos'] > 0 else '')

            cell = f.grid_slaves(row=gridRow, column=1)
            cell[0].configure(text='{:02}:{:02}:{:02}'.format(rowData[r]['clock']['hh'], rowData[r]['clock']['mm'],
                                                              rowData[r]['clock']['ss'])
                              if rowData[r]['status'].get() == STATUS_FINISHED else '')

            cell = f.grid_slaves(row=gridRow, column=2)
            cell[0].configure(textvariable=rowData[r]['class'])

            cell = f.grid_slaves(row=gridRow, column=3)
            cell[0].configure(textvariable=rowData[r]['sailnum'])

            cell = f.grid_slaves(row=gridRow, column=4)
            cell[0].configure(textvariable=rowData[r]['race'])

            cell = f.grid_slaves(row=gridRow, column=5)
            cell[0].configure(textvariable=rowData[r]['status'])
            if rowData[r]['status'].get() == STATUS_FINISHED:
                cell[0].configure(state='disabled')
            else:
                cell[0].configure(state='readonly')

            cell = f.grid_slaves(row=gridRow, column=6)
            cell[0].configure(textvariable=rowData[r]['notes'])

    def __addFinishRow(self, f):
        self.rowCount += 1
        rowNumber = self.rowCount
        right = 10
        above = 4

        lPos = Label(f, text='', justify=RIGHT)
        lPos.grid(row=rowNumber, column=0, padx=(0, right), pady=(above, above))

        lTime = Label(f, text='')
        lTime.grid(row=rowNumber, column=1, padx=(0, right), pady=(above, above))

        cbClass = ttk.Combobox(f, values=self.classNames, width=12)
        cbClass.grid(row=rowNumber, column=2, padx=(0, right), pady=(0, above))
        cbClass.bind('<KeyRelease>', lambda e: self.autoSaveAction())
        cbClass.bind('<<ComboboxSelected>>', lambda e: self.autoSaveAction())

        enSailNum = ttk.Entry(f, validate='key', validatecommand=self.validateNumbers, width=12)
        enSailNum.grid(row=rowNumber, column=3, padx=(0, right), pady=(0, above))
        enSailNum.bind('<KeyRelease>', lambda e: self.autoSaveAction())

        enRaceNum = ttk.Entry(f, validate='key', validatecommand=self.validateNumbers, width=8)
        enRaceNum.grid(row=rowNumber, column=4, padx=(0, right), pady=(0, above))
        enRaceNum.bind('<KeyRelease>', lambda e: self.autoSaveAction())

        cbStatus = ttk.Combobox(f, values=self.statusCodes, width=8)
        cbStatus.grid(row=rowNumber, column=5, padx=(0, right), pady=(0, above))
        cbStatus.bind('<<ComboboxSelected>>', lambda e: self.autoSaveAction())

        enNotes = ttk.Entry(f, width=25)
        enNotes.grid(row=rowNumber, column=6, padx=(0, right), pady=(0, above))
        enNotes.bind('<KeyRelease>', lambda e: self.autoSaveAction())

    def __addFinishHdr(self, f):
        self.rowCount = 0
        fileHdr = [['#', E + W], ['Clock', E + W], ['Class', W], ['Sail', W], ['Race', W], ['Status', W], ['Notes', W]]
        for i, h in enumerate(fileHdr):
            l = Label(f, text=h[0])
            l.grid(row=0, column=i, sticky=h[1])

    def resetFinishBoxAction(self):
        if not messagebox.askyesno('Reset', 'Are you sure? You should save finish times first.'):
            return
        self.pos = 1
        self.finishData = []
        self.raceNameValue.set('')
        f = self.rowFrame
        for w in f.winfo_children():
            w.destroy()
        self.__addFinishHdr(self.rowFrame)
        tmpFile = getAutoSaveFileName()
        self.raceId = getUniqueId()
        self.setRaceDate()
        if os.path.exists(tmpFile):
            os.remove(tmpFile)

    def saveToFileAction(self):
        processedFinishInfo = self.getCurrentFinishData()
        saveFinishesToCSV = saveToCSVFile(getFinishFileName('csv'), processedFinishInfo)
       