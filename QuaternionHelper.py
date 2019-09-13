import csv
import pyquaternion
from pyquaternion.quaternion import *
from math import pi, sin, cos
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from time import sleep
from direct.actor.Actor import Actor
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import *
from panda3d.ode import OdeWorld, OdeBody, OdeMass
from panda3d.core import LQuaternionf, TextNode

def CreateQuaternion(stringQuat):
  return LQuaternionf(float(stringQuat[0]), float(stringQuat[1]), float(stringQuat[2]), float(stringQuat[3]))


# def Get

