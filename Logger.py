import csv
from direct.task.Task import Task
import SerialStub as serial
# import serial 
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
            print("Loading logs")
            self.buildLogs()
        else :
            print("Loading serial")
            self.serial = serial.Serial(port, 19200, timeout=0.05 )
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
        #lastLogStringQuat = self.lastLogRow[2:] #TODO remove this
        lastLogStringQuat = self.lastLogRow[4:]
        return QuaternionHelper.CreateQuaternion(lastLogStringQuat)

    def getCurrentQuaternion(self):
        #currentLogStringQuat = self.currentLogRow[2:] #TODO remove this
        currentLogStringQuat = self.currentLogRow[4:]
        currquat = QuaternionHelper.CreateQuaternion(currentLogStringQuat)
        angle = currquat.getAngle()
        return currquat

    def parseSerialLine(self):
        while True:
            try:                
                splitString = self.serial.readline().decode('utf-8')
                splitString = splitString.replace('\t',',').rstrip()
                if len(splitString) > 0 and 'DATA' in splitString:
                    splitString = splitString.split(",")
                    self.serialComing = True

                    if splitString[2] == "DATA" and splitString[3] == "R":
                        formattedString = splitString[3:]
                        formattedString.insert(0, splitString[1]) 
                        print(formattedString)
                        return formattedString
                else:
                    self.serialComing = False
            except:
                continue
            


    def getLogLength(self):
        return len(self.logs)
