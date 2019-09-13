from panda3d.core import LQuaternionf, TextNode, LVector4f, PandaNode, LightNode, LVecBase4, Shader, NodePath, Filename, WindowProperties, CompassEffect, LineSegs
from direct.gui.OnscreenText import OnscreenText
def renderShaders(app):        
    app.render.setShaderInput("tint", LVector4f(1.0, 0.5, 0.5, 1.0))

    # Check video card capabilities.
    if not app.win.getGsg().getSupportsBasicShaders():
        OnscreenText("Toon Shader: Video driver reports that Cg shaders are not supported.")
        return

    # This shader's job is to render the model with discrete lighting
    # levels.  The lighting calculations built into the shader assume
    # a single nonattenuating point light.

    # tempnode = NodePath(PandaNode("temp node"))
    app.parentNode.setShader(app.loader.loadShader("Lighting/lightingGen.sha"))
    app.cam.node().setInitialState(app.parentNode.getState())

    # This is the object that represents the single "light", as far
    # the shader is concerned.  It's not a real Panda3D LightNode, but
    # the shader doesn't care about that.

    light = app.render.attachNewNode("light")
    light.setPos(30, -50, 0)

    # this call puts the light's nodepath into the render state.
    # this enables the shader to access this light by name.

    app.render.setShaderInput("light", light)

    # The "normals buffer" will contain a picture of the model colorized
    # so that the color of the model is a representation of the model's
    # normal at that point.

    normalsBuffer = app.win.makeTextureBuffer("normalsBuffer", 0, 0)
    normalsBuffer.setClearColor(LVecBase4(0.5, 0.5, 0.5, 1))
    app.normalsBuffer = normalsBuffer

    normalsCamera = app.makeCamera(normalsBuffer, lens=app.cam.node().getLens())        
    normalsCamera.reparentTo(app.cam)
    normalsCamera.lookAt(app.parentNode)
    normalsCamera.node().setScene(app.render)
    tempnode = NodePath(PandaNode("temp node"))
    tempnode.setShader(app.loader.loadShader("Lighting/normalGen.sha"))
    normalsCamera.node().setInitialState(tempnode.getState())
    # normalsCamera.node().reparentTo(app.parentNode)

    # what we actually do to put edges on screen is apply them as a texture to
    # a transparent screen-fitted card

    drawnScene = normalsBuffer.getTextureCard()
    drawnScene.setTransparency(1)
    drawnScene.setColor(1, 1, 1, 0)
    drawnScene.reparentTo(app.render2d)
    app.drawnScene = drawnScene

    # this shader accepts, as input, the picture from the normals buffer.
    # it compares each adjacent pixel, looking for discontinuities.
    # wherever a discontinuity exists, it emits black ink.

    app.separation = 0.001
    app.cutoff = 0.3
    inkGen = app.loader.loadShader("Lighting/inkGen.sha")
    drawnScene.setShader(inkGen)
    drawnScene.setShaderInput("separation", LVecBase4(app.separation, 0, app.separation, 0))
    drawnScene.setShaderInput("cutoff", LVecBase4(app.cutoff))
    # Panda contains a built-in viewer that lets you view the results of
    # your render-to-texture operations.  This code configures the viewer.

    app.accept("v", app.bufferViewer.toggleEnable)
    app.accept("V", app.bufferViewer.toggleEnable)
    app.bufferViewer.setPosition("llcorner")