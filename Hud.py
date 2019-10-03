from pyquaternion import Quaternion

import DisplayHelper
from direct.gui.OnscreenText import OnscreenText
from Utils import getAllSerialPorts
from panda3d.core import (CompassEffect, Filename, LightNode, LineSegs,
                          LQuaternionf, LVecBase4, LVector4f, NodePath,
                          PandaNode, Shader, TextNode, WindowProperties)
from StateEnum import State
from tkinter import Tk
from tkinter.filedialog import askopenfilename

class HeadsUpDisplay():
    def __init__(self, app):
        self.time = "0"
        self.fps = "0"
        self.fileInput = ""
        self.selectedComPort = ""
        self.timeDelta = 0
        self.instVel = 0.0
        self.velocityLogs = []
        self.currentLogQuat = ["!"] #TODO remove this 
        self.lastLogQuat = []
        self.velLines = LineSegs("lines")
        self.velLines.setColor(0, 1, 1, 0)                
        segsnode = self.velLines.create(False)
        self.velocityLinesNode = app.render.attachNewNode(segsnode)
        self.simulatorTextDisplays(app)
        self.simulatorInteractives(app)

    def simulatorTextDisplays(self, app):
        self.timeText = OnscreenText(text = 'Time:' + self.time, pos = (-1.25, 0.90), scale = 0.07, align=TextNode.ALeft)
        self.fpsText = OnscreenText(text = 'FPS:' + self.fps, pos = (-1.25, 0.80), scale = 0.07, align=TextNode.ALeft)
        self.velocityText = OnscreenText(text = 'Velocity: ' + str(self.instVel), pos = (.75, 0.80), scale = 0.07, align=TextNode.ALeft)
        self.selectedFile = OnscreenText(text = 'Selected File: ' + self.fileInput, pos = (-.6, 0.2), scale = 0.07, align=TextNode.ALeft)

    def simulatorInteractives(self, app):
        self.playButton = DisplayHelper.buildButton((1.2, 0, -.9), 0.05, "Pause", app.pauseSim) 
        self.restartButton = DisplayHelper.buildButton((1.00, 0, -.9), 0.05, "Restart", app.restartSim)
        self.resetButton = DisplayHelper.buildButton((.80, 0, -.9), 0.05, "Reset", app.resetCamera)
        self.slider = DisplayHelper.buildSlider((0,1), 0, (-.60, 0, -.9), 0.7, 3, app.updateValue)        
        self.startSerialButton = DisplayHelper.buildButton((-.1, 0, -.1), 0.1, "Read from Serial", self.displaySerialOptions) 
        self.startLogsButton = DisplayHelper.buildButton((-.1, 0, .1), 0.1, "Read from Logs", self.displayFileOptions)        
        self.quitButton = DisplayHelper.buildButton((-.05, 0, -.3), .1, "Quit", app.quit)
        self.launchFromFileButton = DisplayHelper.buildButton((.2, 0, 0), 0.1, "Start", app.startLogs)
        self.launchFromSerialButton = DisplayHelper.buildButton((.2, 0, 0), 0.1, "Start", app.startSerial)               
        self.openFilesButton = DisplayHelper.buildButton((-.35, 0, 0), 0.05, "Select File", self.openFiles)
        comsOptions = getAllSerialPorts()
        self.menu = DisplayHelper.buildOptionMenu("Select a coms port", 0.1, self.handleItemSelect, comsOptions, 2, (0.65,0.65,0.65,1), (-.15, 0, 0))
        self.backButton = DisplayHelper.buildButton((-.8, 0, .8), 0.06, "Back To Menu", self.drawStartScreen)


    def getVelocity(self, currentLogQuat, lastLogQuat, timeDelta):
        currentQuat = Quaternion(currentLogQuat[0], currentLogQuat[1],currentLogQuat[2], currentLogQuat[3])
        currentAxis = currentQuat.axis
        currentRadians = currentQuat.radians        
        lastQuat = Quaternion(lastLogQuat[0], lastLogQuat[1],lastLogQuat[2], lastLogQuat[3])
        lastAxis = lastQuat.axis
        lastRadians = lastQuat.radians
        
        angularDisplacement = currentAxis * currentRadians
        lastAngularDisplacement = lastAxis *  lastRadians
        return (lastAngularDisplacement - angularDisplacement) / timeDelta

    def getMagnitude(self, vec):
        return ( vec[0] ** 2 + vec[1] ** 2 + vec[2] ** 2 ) ** 0.5
    
    def updateHud(self, currentLogQuat, lastLogQuat, timeDelta, runTime):
        framesPerSecond = str(round(1/timeDelta))     
        instVel = self.getVelocity(currentLogQuat, lastLogQuat, timeDelta)
        self.timeText.setText("Time: " + runTime)
        self.fpsText.setText("FPS: " + framesPerSecond)      
        self.velocityText.setText("Velocity: " + str(self.getMagnitude(instVel)))
        
        #self.quatText.setText('Q:'.join(self.currentLogQuat)) #TODO remove this
        quatstring = "Q: "
        for i in range( 0 ,4):
            quatstring= quatstring + "{:.1f}".format(currentLogQuat[i]) + ", "
        self.quatText.setText(quatstring) #TODO remove this

        self.velocityLogs.append(self.instVel)  
        
    def getStartIndex(self, logs):
        if len(logs) > 10:
            return len(logs) - 11
        return 0

    def drawStartScreen(self):
        self.timeText.hide()
        self.fpsText.hide()
        self.velocityText.hide()
        self.playButton.hide()
        self.restartButton.hide()
        self.resetButton.hide()
        self.slider.hide()
        self.launchFromFileButton.hide()
        self.launchFromSerialButton.hide()
        self.selectedFile.hide()
        self.menu.hide()
        self.backButton.hide()
        self.openFilesButton.hide()
        self.startSerialButton.show()
        self.startLogsButton.show()
        self.quitButton.show()

    def displayFileOptions(self):
        self.launchFromFileButton.show()
        self.selectedFile.show()
        self.backButton.show()
        self.openFilesButton.show()
        self.startSerialButton.hide()
        self.startLogsButton.hide()
        self.quitButton.hide()
    
    def displaySerialOptions(self):
        self.startSerialButton.hide()
        self.startLogsButton.hide()
        self.quitButton.hide()
        self.backButton.show()
        self.launchFromSerialButton.show()
        self.menu.show()

    def openFiles(self):
        self.fileInput = askopenfilename()
        self.selectedFile.setText('Selected File: ' + self.fileInput)
    # def destroyStartSceen(self):
    #     self.entry = None
    #     self.menu = None

    def handleItemSelect(self, value):
        self.selectedComPort = value
        print(value)

    # def drawGraph(self, task):
    #     lastX = -.9
    #     startY = 1
    #     startIndex = self.getStartIndex(self.velocityLogs)
    #     print(startIndex)
    #     for index, vel in enumerate(self.velocityLogs[startIndex:]):   
    #         mag = self.getMagnitude(vel)
    #         print(mag)
    #         print(index)
    #         if index == startIndex:
    #             self.hud.velLines.moveTo(lastX, startY + mag * index / 2, 0 )
    #         else:
    #             self.hud.velLines.drawTo(lastX + (index), 0, startY + mag)
                
    #     self.lineNode = self.hud.velLines.create(True)
    #     self.lineNodePath = NodePath(self.lineNode)
    #     self.lineNodePath.reparentTo(self.render2d)
    #     return Task.cont
