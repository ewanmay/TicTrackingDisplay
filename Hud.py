import DisplayHelper
from direct.gui.OnscreenText import OnscreenText
#from panda3d.core import LQuaternionf, TextNode, LVector4f, PandaNode, LightNode, LVecBase4, Shader, NodePath, Filename, WindowProperties, CompassEffect, LineSegs
from panda3d.core import TextNode, LineSegs
from pyquaternion import Quaternion

class HeadsUpDisplay():
    def __init__(self, app):
        self.time = "0"
        self.fps = "0"
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
        # TODO remove this
        self.quatText = OnscreenText(text = 'Q:'.join(self.currentLogQuat), pos = (-1.25, 0.70), scale = 0.07, align=TextNode.ALeft)

    def simulatorInteractives(self, app):
        self.playButton = DisplayHelper.buildButton((1.2, 0, -.9), 0.05, "Pause", app.pauseSim) 
        self.restartButton = DisplayHelper.buildButton((1.00, 0, -.9), 0.05, "Restart", app.restartSim)
        self.resetButton = DisplayHelper.buildButton((.80, 0, -.9), 0.05, "Reset", app.resetCamera)
        self.slider = DisplayHelper.buildSlider((0,len(app.logger.logs)-1), 0, (-.60, 0, -.9), 0.7, 3, app.updateValue)

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
