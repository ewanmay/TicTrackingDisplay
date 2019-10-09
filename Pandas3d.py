import csv
import sys
from time import sleep

import DisplayHelper
import ShaderUtils
from direct.gui.DirectGui import *
from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
from Hud import HeadsUpDisplay
from Logger import Logger
from panda3d.core import LQuaternionf
from Enumerations import State, LogMethod
from Database import Database

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.state = State.Start
        self.method = LogMethod.File
        self.model = DisplayHelper.drawModel(self)
        self.parentNode = DisplayHelper.setupCamera(self)
        ShaderUtils.renderShaders(self)
        self.db = Database()
        self.db.setupSchema("./Data/TicDisplay.db")
        self.hud = HeadsUpDisplay(self)
        self.hud.drawStartScreen()
        self.accept('escape', lambda: self.displayMenu())
        self.taskMgr.add(self.readNewRow, "ReadNewRowTask")
        self.taskMgr.add(self.rotateObject, "RotateObjectTask")
        self.taskMgr.add(self.displayHud, "DisplayHudTask")
        self.taskMgr.add(self.thirdPersonCameraTask, 'ThirdPersonCameraTask')
        self.taskMgr.add(self.incrementIterator, 'IncrementIterator')
        # self.taskMgr.add(self.drawGraph, "DrawVelocityGraph")

    def rotateObject(self, task):
        if(self.state != State.Playing):
            return task.cont
        unitQuaternion = LQuaternionf(1., 0., 0., 0.)
        currentQuaternion = self.logger.getCurrentQuaternion()
        # diffQuat = (unitQuaternion - currentQuaternion)
        hpr = currentQuaternion.get_hpr()
        # hpr = hpr * 2 # TODO Remove this, this is just for effect.
        self.model.setHpr(hpr)
        return Task.cont
    
    def displayHud(self, task):
        if(self.state != State.Playing):
            return task.cont
        runTime = self.logger.runTime
        timeDelta = self.logger.timeDelta   
        currentQuaternion = self.logger.getCurrentQuaternion()
        lastQuaternion = self.logger.getLastQuaternion()
        self.hud.updateHud(currentQuaternion, lastQuaternion, timeDelta, runTime)
        return Task.cont

    def incrementIterator(self, task):
        if(self.state != State.Playing):
            return task.cont
        logIndex = self.logger.incrementIterator()
        self.hud.slider['value'] = logIndex        
        logLength = self.logger.getLogLength()
        self.hud.slider['range'] = (0, logLength - 1) 
        if self.method != LogMethod.Serial:
            sleep(self.logger.timeDelta)
        return Task.cont      

    def resetCamera(self):
        self.model.setScale(1.25, 1.25, 1.25)
        self.model.setPos(-8, 42, 0)
        self.cam.setPos(0,-20,0)
        self.parentNode.setHpr(0,0,0)
        self.heading = 0
        self.pitch = 0
    
    def thirdPersonCameraTask(self, task):
        if(self.state != State.Playing):
            return task.cont
        if self.isClicked:
            md = self.win.getPointer(0)
                
            x = md.getX()
            y = md.getY()
            
            self.heading = self.heading - (x - self.clickedX) * 0.5
            self.pitch = self.pitch - (y - self.clickedY) * 0.5
                        
            self.parentNode.setHpr(self.heading, self.pitch,0)        
        return task.cont

    def click(self):
        self.isClicked = True
        md = self.win.getPointer(0)            
        self.clickedX = md.getX()
        self.clickedY = md.getY()

    def clickOut(self):
        self.isClicked = False

    def updateValue(self):
        logIndex = int(round(self.hud.slider['value']))
        if hasattr(self, 'logger'):
            self.logger.setIndex(logIndex)

    def restartSim(self):
        self.logger.setIndex(1)

    def pauseSim(self):
        if self.state == State.Playing:
            self.state = State.Paused
            self.hud.playButton.setText("Play")
        else:
            self.state = State.Playing           
            self.hud.playButton.setText("Pause")
    
    def readNewRow(self, task):
        if(self.state != State.Start):
            self.logger.readNewRow(self.state)        
        return Task.cont
        
    def startSerial(self):
        entry = (None, None, "EntryTest")
        self.method = LogMethod.Serial
        self.logger = Logger(self.method, self.hud.selectedComPort, None, entry, self.db)
        self.state = State.Playing
        self.hud.startSimulation()            

    def startLogs(self):
        entry = (self.hud.selectedEntryId, self.hud.selectedEntry)
        self.method = LogMethod.File
        self.state = State.Playing
        self.logger = Logger(self.method, 0, self.hud.fileInput, entry, self.db)
        self.hud.startSimulation()              

    def startDb(self):
        entry = (self.hud.selectedEntryId, self.hud.selectedEntry)
        self.method = LogMethod.Db
        self.logger = Logger(self.method, 0, self.hud.fileInput, entry, self.db)
        self.state = State.Playing
        self.hud.startSimulation()  

    def displayMenu(self):
        try:
            self.logger.serial.close()
            self.logger.db.conn.close()
        except:
            pass
        self.state = State.Start
        self.hud.drawStartScreen()

    def quit(self):
        sys.exit()

try:
    app = MyApp()
    app.run()
except SystemExit as e:
    print("Goodbye!")
