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


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.model = DisplayHelper.drawModel(self)
        self.parentNode = DisplayHelper.setupCamera(self)
        ShaderUtils.renderShaders(self)
        self.accept('escape', lambda: sys.exit())
        # self.logger = Logger(True, 'COM5')
        self.logger = Logger(False, 0)
        self.hud = HeadsUpDisplay(self)
        self.playing = True
        self.taskMgr.add(self.logger.readNewRow, "ReadNewRowTask")
        self.taskMgr.add(self.rotateObject, "RotateObjectTask")
        self.taskMgr.add(self.displayHud, "DisplayHudTask")
        self.taskMgr.add(self.thirdPersonCameraTask, 'ThirdPersonCameraTask')
        self.taskMgr.add(self.incrementIterator, 'IncrementIterator')
        # self.taskMgr.add(self.drawGraph, "DrawVelocityGraph")

    def rotateObject(self, task):
        unitQuaternion = LQuaternionf(1., 0., 0., 0.)
        currentQuaternion = self.logger.getCurrentQuaternion()
        diffQuat = (unitQuaternion - currentQuaternion)
        hpr = diffQuat.get_hpr()
        self.model.setHpr(hpr)
        return Task.cont
    
    def displayHud(self, task):
        runTime = self.logger.runTime
        timeDelta = self.logger.timeDelta   
        currentQuaternion = self.logger.getCurrentQuaternion()
        lastQuaternion = self.logger.getLastQuaternion()
        self.hud.updateHud(currentQuaternion, lastQuaternion, timeDelta, runTime)
        return Task.cont

    def incrementIterator(self, task):
        if self.playing:
            logIndex = self.logger.incrementIterator()
            self.hud.slider['value'] = logIndex        
        logLength = self.logger.getLogLength()
        self.hud.slider['range'] = (0, logLength - 1)
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
        self.logger.setIndex(logIndex)

    def restartSim(self):
        self.logger.setIndex(1)

    def pauseSim(self):
        if self.playing:
            self.playing = False
            self.hud.playButton.setText("Play")
        else:
            self.playing = True            
            self.hud.playButton.setText("Pause")

app = MyApp()
try:
    app.run()
except SystemExit as e:
    print("Goodbye!")
