# -*- coding: utf-8 -*-

import os
from FreeCAD import Vector, Rotation, activeDocument, BoundBox
import Ray
import OpticalObject
from numpy import linspace
from importlib import reload

def recompute():
    activeDocument().recompute()

def get_module_path():
    ''' Returns the current module path.
    Determines where this file is running from, so works regardless of whether
    the module is installed in the app's module directory or the user's app data folder.
    (The second overrides the first.)
    '''
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
    reload(Ray)
    '''Python command to create a light ray.'''
    name = 'Ray'
    if beamNrColumns * beamNrRows > 1:
        name = 'Beam'

    fp = activeDocument().addObject('Part::FeaturePython', name)
    fp.Placement.Base = position
    fp.Placement.Rotation = Rotation(Vector(1, 0, 0), direction)
    Ray.RayWorker(fp, power, spherical, beamNrColumns, beamNrRows, beamDistance, hideFirst, maxRayLength, maxNrReflections, wavelength)
    Ray.RayViewProvider(fp.ViewObject)
    recompute()
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
    reload(Ray)
    doc = activeDocument()
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
    recompute()
    

def restartAll():
    for obj in activeDocument().Objects:
        if isRay(obj):
            obj.Power = True
            obj.touch()
    
    recompute()

def allOff():
    for obj in activeDocument().Objects:
        if isRay(obj):
            obj.Power = False
            
    recompute()

def makeMirror(base = []):
    reload(OpticalObject)
    '''All FreeCAD objects in base will be optical mirrors.'''
    fp = activeDocument().addObject('Part::FeaturePython', 'Mirror')
    OpticalObject.OpticalObjectWorker(fp, base)
    OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    recompute()
    return fp

def makeAbsorber(base = []):
    reload(OpticalObject)
    '''All FreeCAD objects in base will be optical light absorbers.'''
    fp = activeDocument().addObject('Part::FeaturePython', 'Absorber')
    OpticalObject.OpticalObjectWorker(fp, base, type = 'absorber')
    OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    recompute()
    return fp

def makeLens(base = [], RefractionIndex = 0, material = 'Quartz'):
    reload(OpticalObject)
    '''All FreeCAD objects in base will be optical lenses.'''
    fp = activeDocument().addObject('Part::FeaturePython', 'Lens')
    OpticalObject.LensWorker(fp, base, RefractionIndex, material)
    OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    recompute()
    return fp

def isRay(obj):
    return hasattr(obj, 'Power') and hasattr(obj, 'BeamNrColumns')

def isOpticalObject(obj):
    return obj.TypeId == 'Part::FeaturePython' and hasattr(obj, 'OpticalType') and hasattr(obj, 'Base')

def getSceneBoundBox():
    '''Gets the Bounding Box of all objects and the startings position of the rays'''
    from FreeCAD import BoundBox
    doc = activeDocument()
    bb = BoundBox(0)

    for obj in doc.Objects:
        if isRay(obj): 
            p = obj.Placement.Base
            bb.add(BoundBox(p, p))
        elif hasattr(obj, 'Shape') and not isLens(obj): 
            bb.add(obj.Shape.BoundBox)
    return bb
