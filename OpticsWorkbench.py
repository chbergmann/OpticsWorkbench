# -*- coding: utf-8 -*-

import os
import FreeCAD
from FreeCAD import Vector, Rotation
import math
import Ray
import OpticalObject
from numpy import linspace


def get_module_path():
    """ Returns the current module path.
    Determines where this file is running from, so works regardless of whether
    the module is installed in the app's module directory or the user's app data folder.
    (The second overrides the first.)
    """
    return os.path.dirname(__file__)


def makeRay(position = Vector(0, 0, 0),
            direction = Vector(1, 0, 0),
            power = True,
            beamNrColumns = 1,
            beamNrRows = 1,
            beamDistance = 0.1,
            spherical = False,
            hideFirst = False,
            maxRayLength = 1000000,
            maxNrReflections = 200,
            wavelength = 580):
    '''Python command to create a light ray.'''
    name = 'Ray'
    if beamNrColumns * beamNrRows > 1:
        name = 'Beam'

    fp = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', name)
    fp.Placement.Base = position
    fp.Placement.Rotation = Rotation(Vector(1, 0, 0), direction)
    Ray.RayWorker(fp, power, spherical, beamNrColumns, beamNrRows, beamDistance, hideFirst, maxRayLength, maxNrReflections, wavelength)
    Ray.RayViewProvider(fp.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return fp
    
    
def makeSunRay(position = Vector(0, 0, 0),
            direction = Vector(1, 0, 0),
            power = True,
            hideFirst = False,
            maxRayLength = 1000000,
            maxNrReflections = 200,
            wavelength_from = 400,
            wavelength_to = 800,
            num_rays = 100):
    
    doc = FreeCAD.activeDocument()
    rays = []
    for l in linspace(wavelength_from, wavelength_to, num_rays):
        ray = makeRay(position = position,
            direction = direction,
            power = power,
            hideFirst = hideFirst,
            maxRayLength = maxRayLength,
            maxNrReflections = maxNrReflections,
            wavelength = l)
        ray.ViewObject.LineWidth = 1
        rays.append(ray)

    group = doc.addObject('App::DocumentObjectGroup','SunRay')
    group.Group = rays
    doc.recompute()
    

def restartAll():
    for obj in FreeCAD.ActiveDocument.Objects:
        if hasattr(obj, 'Power') and hasattr(obj, 'BeamNrColumns'):
            obj.Power = False
            obj.Power = True

def allOff():
    for obj in FreeCAD.ActiveDocument.Objects:
        if hasattr(obj, 'Power') and hasattr(obj, 'BeamNrColumns'):
            obj.Power = False

def makeMirror(base = []):
    '''All FreeCAD objects in base will be optical mirrors.'''
    fp = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Mirror")
    OpticalObject.OpticalObjectWorker(fp, base)
    OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return fp

def makeAbsorber(base = []):
    '''All FreeCAD objects in base will be optical light absorbers.'''
    fp = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Absorber")
    OpticalObject.OpticalObjectWorker(fp, base, type = 'absorber')
    OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return fp

def makeLens(base = [], RefractionIndex = 0, material = 'Quartz'):
    '''All FreeCAD objects in base will be optical lenses.'''
    fp = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Lens")
    OpticalObject.LensWorker(fp, base, RefractionIndex, material)
    OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return fp
