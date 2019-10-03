import csv
from direct.task.Task import Task
import SerialStub as serial
import QuaternionHelper
from StateEnum import State
class Logger():
    def __init__(self, readFromSerial, port, logFile):
        self.readFromSerial = readFromSerial       
        self.logs = []
        self.logIndex = 1
        self.currentLogRow = []
        self.lastLogRow = []
        self.timeDelta = 0
        self.runTime = 0
        self.logFile = logFile
        self.serialComing = False
        if not readFromSerial:
            self.buildLogs()
        else :
            self.serial = serial.Serial(port)
            self.logs.append(self.parseSerialLine())            
            self.logs.append(self.parseSerialLine())

    def buildLogs(self):
        with open(self.logFile) as csvfile:
          readCSV = csv.reader(csvfile, delimiter=',')
          for row in readCSV:
            self.logs.append(row)
    
        
    def incrementIterator(self):        
        if self.logIndex < len(self.logs) - 1:
            self.logIndex = self.logIndex + 1
        return self.logIndex

    def readNewRow(self, state):
        if(state != State.Playing):
            return
        if self.readFromSerial and self.serialComing:
            self.logs.append(self.parseSerialLine())  
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
        lastLogStringQuat = self.lastLogRow[2:]
        return QuaternionHelper.CreateQuaternion(lastLogStringQuat)

    def getCurrentQuaternion(self):
        currentLogStringQuat = self.currentLogRow[2:]
        currquat = QuaternionHelper.CreateQuaternion(currentLogStringQuat)
        angle = currquat.getAngle()
        return currquat

    def parseSerialLine(self):
        splitString = self.serial.readline().split()
        if len(splitString) > 0:
            self.serialComing = True
            return splitString[0].split(",")
        else:
            self.serialComing = False


    def getLogLength(self):
        return len(self.logs)