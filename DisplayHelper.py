from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import (CompassEffect, Filename, LightNode, LineSegs,
                          LQuaternionf, LVecBase4, LVector4f, NodePath,
                          PandaNode, Shader, TextNode, WindowProperties)


def buildButton(pos, scale, buttonText, func):  
    restartButton = DirectButton(text = buttonText, command=func)
    restartButton.setPos(pos[0], pos[1], pos[2]) 
    restartButton.setScale(scale)
    return restartButton

def buildSlider(sliderRange, sliderValue, pos, scale, sliderPageSize, func):  
    slider = DirectSlider(range=sliderRange, value=sliderValue, pageSize=sliderPageSize, command=func)
    slider.setScale(scale)
    slider.setPos(pos[0], pos[1], pos[2])
    return slider

def buildTextInput(initialText, scale, func, text, numLines, focus, focusFunc, pos):
    entry = DirectEntry(text =text, scale=scale, command=func,
                      initialText=initialText, numLines = numLines, focus=focus, focusInCommand=focusFunc)
    entry.setScale(scale)
    entry.setPos(pos[0], pos[1], pos[2])
    return entry

def buildOptionMenu(text, scale, func, items, initialItem, highlightColor, pos):
    menu = DirectOptionMenu(
        text=text, 
        scale=0.1,
        items=items,
        initialitem=initialItem,
        highlightColor=highlightColor,
        command=func)
    menu.setScale(scale)
    menu.setPos(pos[0], pos[1], pos[2])
    menu.popupMenu.setPos(pos[0], pos[1], pos[2] + 1.5)
    # menu.popupMarker.setPos(pos[0], pos[1], pos[2])
    return menu

def setupCamera(app):
    app.disableMouse() # disable default mouse controls

    # dummy node for camera, we will rotate the dummy node for camera rotation
    parentNode = app.render.attachNewNode('camparent')
    parentNode.reparentTo(app.model) # inherit transforms
    parentNode.setEffect(CompassEffect.make(app.render)) # NOT inherit rotation

    # # the camera
    app.cam.reparentTo(parentNode)
    app.cam.lookAt(parentNode)
    app.cam.setY(-10) # camera distance from model

    # camera zooming
    app.accept('wheel_up', lambda : app.cam.setY(app.cam.getY()+200 * globalClock.getDt()))
    app.accept('wheel_down', lambda : app.cam.setY(app.cam.getY()-200 * globalClock.getDt()))
    app.accept('mouse1', app.click)
    app.accept('mouse1-up', app.clickOut)
    app.clickOut()

    # global vars for camera rotation
    app.heading = 0
    app.pitch = 0    
    return parentNode



def drawModel(app):
    model = app.loader.loadModel("models/teapot")
    model.reparentTo(app.render)
    model.setScale(1.25, 1.25, 1.25)
    model.setPos(-8, 42, 0)
    return model
