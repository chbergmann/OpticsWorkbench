# -*- coding: utf-8 -*-

import os
import FreeCAD
from FreeCAD import Vector, Rotation
from importlib import reload
import math


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
    import Ray      
    reload(Ray)     # causes FreeCAD to reload Ray.py every time a new Ray is created. Useful while developping the feature.
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
    import OpticalObject      
    reload(OpticalObject)     # causes FreeCAD to reload Ray.py every time a new Ray is created. Useful while developping the feature.      
    fp = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Mirror")
    OpticalObject.OpticalObjectWorker(fp, base)
    OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return fp
    
def makeAbsorber(base = []):
    '''All FreeCAD objects in base will be optical light absorbers.'''
    import OpticalObject      
    reload(OpticalObject)     # causes FreeCAD to reload Ray.py every time a new Ray is created. Useful while developping the feature.      
    fp = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Absorber")
    OpticalObject.OpticalObjectWorker(fp, base, type = 'absorber')
    OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return fp

def makeLens(base = [], RefractionIndex = 0, material = 'Quartz'):
    '''All FreeCAD objects in base will be optical lenses.'''
    import OpticalObject      
    reload(OpticalObject)     # causes FreeCAD to reload Ray.py every time a new Ray is created. Useful while developping the feature.      
    fp = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Lens")
    OpticalObject.LensWorker(fp, base, RefractionIndex, material)
    OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return fp

def refraction_index_from_sellmeier(wavelength, sellmeier):
    b1, b2, b3, c1, c2, c3 = sellmeier
    l = wavelength
    n = math.sqrt(1 + b1*l**2/(l**2 - c1) + b2*l**2/(l**2 - c2) + b3*l**2/(l**2 - c3))
    return n