# this code is meant to be run as a macro or pasted into the console

import OpticsWorkbench
import math
from FreeCAD import Vector, Rotation
import numpy as np
from numpy import linspace

a=App.activeDocument()

num_rays = 100
for l in linspace(400, 800, num_rays):
  r = OpticsWorkbench.makeRay(position = Vector(0, 0, 0), wavelength=l)
  r.ViewObject.LineWidth = 1

  group = a.getObject('Group')
  r.adjustRelativeLinks(group)
  group.addObject(r)