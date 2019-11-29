import csv
from direct.task.Task import Task
# import SerialStub as serial
import sqlite3
import re
import serial
import QuaternionHelper
from Database import Database
from Enumerations import State, LogMethod
from datetime import datetime
class Logger():
    def __init__(self, logMethod, port, log, entry, db):
        self.logMethod = logMethod
        self.logs = []
        self.logIndex = 1
        self.currentLogRow = []
        self.lastLogRow = []
        self.timeDelta = 0
        self.runTime = 0
        self.logFile = log
        self.serialComing = False
        self.logRegex = r'\d{1,40},DATA,-?\d.\d{2},-?\d.\d{2},-?\d.\d{2},-?\d.\d{2},-?\d.\d{2},-?\d.\d{2},-?\d.\d{2}$'
        self.db = db
        
        if logMethod == LogMethod.File:
            self.buildLogs()
        elif logMethod == LogMethod.Db:
            dbLogs = db.getLogsFromEntry(entry[0])
            print(dbLogs)
            self.logs = [(log[1], log[3], log[4], log[5], log[6], log[7]) for log in dbLogs]
        elif logMethod == LogMethod.Serial:
            self.entryId = self.db.createNewEntry((datetime.now().strftime("%d-%m-%Y_%H-%M-%S"), entry[2]))
            self.serial = serial.Serial(port, 230400, timeout=0.05 ) 
            self.logs.append(self.parseSerialLine())            
            self.logs.append(self.parseSerialLine())       
            self.logs.append(self.parseSerialLine())

    def buildLogs(self):
        with open(self.logFile) as csvfile:         
          fileLines = csvfile.readlines()
          for row in fileLines:
            splitString = row.replace('\t',',').rstrip()
            splitString = splitString.split(",")
            formattedString = splitString[3:]
            formattedString.insert(0, splitString[1])            
            self.logs.append(formattedString)

        
    def incrementIterator(self):
        if self.logMethod == LogMethod.Serial:
            self.logIndex = 2
        if self.logIndex < len(self.logs) - 1:
            self.logIndex = self.logIndex + 1
        return self.logIndex

    def readNewRow(self, state):
        if(state != State.Playing):
            return
        if self.logMethod == LogMethod.Serial and self.serialComing:
            # self.logs.append(self.parseSerialLine())  
            self.logs[0] = self.logs[1]
            self.logs[1] = self.logs[2]
            self.logs[2] = self.parseSerialLine()
        self.currentLogRow = self.logs[self.logIndex]
        self.lastLogRow = self.logs[self.logIndex - 1]
        self.timeDelta = (float(self.currentLogRow[0]) - float(self.lastLogRow[0]))/1000
        self.runTime = str(float(self.currentLogRow[0])/1000)
    
    def setIndex(self, index):        
        if(index == 0):
            self.logIndex = 1            
            # self.velocityLogs = []
        else:
            self.logIndex = index

    def getLastQuaternion(self):        
        lastLogStringQuat = self.lastLogRow[1:]
        return QuaternionHelper.CreateQuaternion(lastLogStringQuat)

    def getCurrentQuaternion(self):
        currentLogStringQuat = self.currentLogRow[1:]
        currquat = QuaternionHelper.CreateQuaternion(currentLogStringQuat)
        # currquat = currquat.multiply((0, 1/(2**.5), 0, 1/(2**.5)))
        angle = currquat.getAngle()
        return currquat

    def parseSerialLine(self):
        while True:
            try:
                splitString = self.serial.readline().decode('utf-8')
                splitString = splitString.replace('\t',',').rstrip()
                if re.search(self.logRegex, splitString):       
                    splitString = splitString.split(",")
                    self.serialComing = True
                    
                    # formattedString = splitString[1:]
                    formattedString = splitString[3:]
                    formattedString.insert(0, splitString[1])
                    if self.logMethod == LogMethod.Serial:                        
                        log = Log(formattedString, self.entryId)
                        self.db.createNewLog(log.entry)
                    print(formattedString)
                    return formattedString
                else:
                    self.serialComing = False
            except:
                continue


    def getLogLength(self):
        return len(self.logs)


class Log():
    def __init__(self, data, entryId):
        self.milis = data[0]
        # TODO: Change this back if we need it
        self.side = "N"    
        self.vecW = data[1]
        self.vecX = data[2]
        self.vecY = data[3]        
        self.vecZ = data[4]
        self.entry = (self.milis, entryId, self.side, 
                    self.vecW, self.vecX, self.vecY, self.vecZ)
