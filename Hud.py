from pyquaternion import Quaternion

import DisplayHelper
from direct.gui.OnscreenText import OnscreenText
from Utils import getAllSerialPorts
from panda3d.core import (CompassEffect, Filename, LightNode, LineSegs,
                          LQuaternionf, LVecBase4, LVector4f, NodePath,
                          PandaNode, Shader, TextNode, WindowProperties)
from Enumerations import State
from tkinter import Tk
from tkinter.filedialog import askopenfilename

class HeadsUpDisplay():
    def __init__(self, app):
        self.time = "0"
        self.fps = "0"
        self.fileInput = ""
        self.selectedComPort = ""
        self.selectedEntryId = 0
        self.entryDict = {}
        self.timeDelta = 0
        self.instVel = 0.0
        self.velocityLogs = []
        self.currentLogQuat = []
        self.lastLogQuat = []
        self.velLines = LineSegs("lines")
        self.velLines.setColor(0, 1, 1, 0)                
        self.db = app.db
        segsnode = self.velLines.create(False)
        self.velocityLinesNode = app.render.attachNewNode(segsnode)
        self.simulatorTextDisplays(app)
        self.simulatorInteractives(app)

    def simulatorTextDisplays(self, app):
        # SIMULATOR TEXT
        self.timeText = OnscreenText(text = 'Time:' + self.time, pos = (-1.25, 0.90), scale = 0.07, align=TextNode.ALeft)
        self.fpsText = OnscreenText(text = 'FPS:' + self.fps, pos = (-1.25, 0.80), scale = 0.07, align=TextNode.ALeft)
        self.velocityText = OnscreenText(text = 'Velocity: ' + str(self.instVel), pos = (.75, 0.80), scale = 0.1, align=TextNode.ALeft)

        # START SCREEN TEXT
        self.selectedFile = OnscreenText(text = 'Selected File: ' + self.fileInput, pos = (-1.3, 0.2), scale = 0.07, align=TextNode.ALeft, wordwrap=40)
        self.selectedComPortText = OnscreenText(text = 'Select a serial port:', pos = (-1.0, 0.3), scale = 0.12, align=TextNode.ALeft)
        self.titleText = OnscreenText(text = 'Tic Player', pos = (-.625, 0.3), scale = 0.25, align=TextNode.ALeft)
        self.loadingText = OnscreenText(text = 'Waiting for data...', pos = (-.125, -0.1), scale = 0.1, align=TextNode.ALeft)
        self.logNameText = OnscreenText(text = "Log name: ", pos = (-1.0, 0.1), scale = 0.12, align=TextNode.ALeft)

    def simulatorInteractives(self, app):
        # SIMULATOR INTERACTIVES
        self.playButton = DisplayHelper.buildButton((1.2, 0, -.9), 0.05, "Pause", app.pauseSim) 
        self.restartButton = DisplayHelper.buildButton((1.00, 0, -.9), 0.05, "Restart", app.restartSim)
        self.resetButton = DisplayHelper.buildButton((.80, 0, -.9), 0.05, "Reset", app.resetCamera)
        self.slider = DisplayHelper.buildSlider((0,1), 0, (-.60, 0, -.9), 0.7, 3, app.updateValue)        
        
        # START SCREEN INTERACTIVES
        self.startSerialButton = DisplayHelper.buildButton((-.1, 0, -.1), 0.1, "Read from Serial", self.displaySerialOptions) 
        self.startLogsButton = DisplayHelper.buildButton((-.1, 0, .1), 0.1, "Read from Logs", self.displayFileOptions)                
        self.startFromDbButton = DisplayHelper.buildButton((-.1, 0, -.3), 0.1, "Replay Saved", self.displayDbOptions)
        self.quitButton = DisplayHelper.buildButton((-.05, 0, -.5), .1, "Quit", app.quit)
        self.launchFromFileButton = DisplayHelper.buildButton((.2, 0, 0), 0.1, "Start", app.startLogs)
        self.launchFromSerialButton = DisplayHelper.buildButton((-0.1, 0, -.1), 0.1, "Start", app.startSerial)
        self.launchFromDbButton = DisplayHelper.buildButton((-0.1, 0, 0), 0.1, "Start", app.startDb)               
        self.openFilesButton = DisplayHelper.buildButton((-.35, 0, 0), 0.1, "Select File", self.openFiles)
        # BUILD COMS MENU AND DB ENTRIES MENU
        comsOptions = getAllSerialPorts()
        allEntries = self.db.getAllEntries()
        entryOptions = [self.createEntryString(x) for x in allEntries]
        if len(entryOptions) == 0:
            entryOptions = [ "No data found"]
        else:
            self.selectedEntry = entryOptions[0]
            self.selectedEntryId = allEntries[0][0]
        self.menu = DisplayHelper.buildOptionMenu("Select a coms port", 0.15, self.handlePortSelect, comsOptions, 0, (1,1,1,1), (.25, 0, .3))
        self.dbMenu = DisplayHelper.buildOptionMenu("", 0.15, self.handleEntrySelect, entryOptions, 0, (1,1,1,1), (-1, 0, .3))
        self.backButton = DisplayHelper.buildButton((-.8, 0, .8), 0.1, "Back To Menu", self.drawStartScreen)

        lastEntryId = self.db.getLastEntry()
        if lastEntryId is None:
            lastEntryId = 0
        self.logNameInput = DisplayHelper.buildTextInput("Entry_" + str(lastEntryId + 1), 0.12, self.handleTextInput, "", 1, None, None, pos = (-.25, 0, 0.1))

    def refreshEntryOptions(self):
        self.menu.options = getAllSerialPorts()
        allEntries = self.db.getAllEntries()
        self.dbMenu.options = [self.createEntryString(x) for x in allEntries]

    def createEntryString(self, entry):
        entryString = entry[2] + "-" + entry[1]
        self.entryDict[entryString] = entry[0]
        return entryString  

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
        self.velocityLogs.append(self.instVel)  
        
    def getStartIndex(self, logs):
        if len(logs) > 10:
            return len(logs) - 11
        return 0
    
    def handleTextInput(self, value):
        self.logNameText = value

    def showSimulationUi(self):        
        self.timeText.show()
        self.fpsText.show()
        self.velocityText.show()
        self.playButton.show()
        self.restartButton.show()
        self.resetButton.show()
        self.slider.show()

    def hideSimulationUi(self):
        self.timeText.hide()
        self.fpsText.hide()
        self.velocityText.hide()
        self.playButton.hide()
        self.restartButton.hide()
        self.resetButton.hide()
        self.slider.hide()

    def hideLaunchFromSerialUi(self):
        self.menu.hide()
        self.backButton.hide()
        self.launchFromSerialButton.hide()
        self.selectedComPortText.hide()
        self.logNameText.hide()
        self.logNameInput.hide()
        self.loadingText.hide()

    def hideLaunchFromLogsUi(self):
        self.menu.hide()
        self.backButton.hide()
        self.launchFromFileButton.hide()
        self.selectedFile.hide()
        self.openFilesButton.hide()
        self.loadingText.hide()
    
    def drawStartScreen(self):
        self.hideSimulationUi()
        self.hideLaunchFromSerialUi()
        self.hideLaunchFromLogsUi()
        self.hideDbOptions()
        self.startSerialButton.show()
        self.startLogsButton.show()
        self.startFromDbButton.show()
        self.quitButton.show()
        self.titleText.show()

    def displayFileOptions(self):
        self.hideStartScreen()
        self.launchFromFileButton.show()
        self.selectedFile.show()
        self.backButton.show()
        self.openFilesButton.show()
    
    def hideStartScreen(self):
        self.startSerialButton.hide()
        self.startLogsButton.hide()
        self.startFromDbButton.hide()
        self.titleText.hide()
        self.quitButton.hide()
    
    def displaySerialOptions(self):
        self.hideStartScreen()
        self.backButton.show()
        self.launchFromSerialButton.show()
        self.logNameInput.show()
        self.selectedComPortText.show()
        self.logNameText.show()
        self.menu.show()

    def displayDbOptions(self):
        self.refreshEntryOptions()
        self.hideStartScreen()
        self.launchFromDbButton.show()
        self.dbMenu.show()
        self.launchFromDbButton.show()
        self.backButton.show()
    
    def hideDbOptions(self):        
        self.launchFromDbButton.hide()
        self.logNameInput.hide()
        self.dbMenu.hide()
        self.launchFromDbButton.hide()
        self.backButton.hide()
    
    def startSimulation(self):
        self.hideLaunchFromLogsUi()
        self.hideLaunchFromSerialUi()
        self.hideDbOptions()
        self.hideStartScreen()
        self.showSimulationUi()


    def openFiles(self):
        self.fileInput = askopenfilename()
        self.selectedFile.setText('Selected File: ' + self.fileInput)

    # def destroyStartSceen(self):
    #     self.entry = None
    #     self.menu = None

    def handlePortSelect(self, value):
        self.selectedComPort = value
    
    def handleEntrySelect(self, value):        
        self.selectedEntry = value
        self.selectedEntryId = self.entryDict[value]

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
