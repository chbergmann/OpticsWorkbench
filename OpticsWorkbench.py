# -*- coding: utf-8 -*-

import os
import FreeCAD
from FreeCAD import Vector
from importlib import reload

def get_module_path():
    """ Returns the current module path.
    Determines where this file is running from, so works regardless of whether
    the module is installed in the app's module directory or the user's app data folder.
    (The second overrides the first.)
    """
    return os.path.dirname(__file__)


def makeRay(position = Vector(0, 0, 0), 
            direction = Vector(1, 0, 0), 
            power=True, 
            beamNrColumns = 1,
            beamNrRows = 1,
            beamDistance = 0.1):
    '''Python command to create a light ray.'''
    import Ray      
    reload(Ray)     # causes FreeCAD to reload Ray.py every time a new Ray is created. Useful while developping the feature.      
    fp = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Ray")
    fp.Placement.Base = position
    Ray.RayWorker(fp, direction, power, beamNrColumns, beamNrRows, beamDistance)
    vp = Ray.RayViewProvider(fp.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return fp
    
def restartAll():
    for obj in FreeCAD.ActiveDocument.Objects:
        if hasattr(obj, 'MaxNumberRays'):
            obj.Power = False
            obj.Power = True
            
def allOff():
    for obj in FreeCAD.ActiveDocument.Objects:
        if hasattr(obj, 'MaxNumberRays'):
            obj.Power = False

def makeMirror(base = []):
    '''Python command to create a light ray.'''
    import OpticalObject      
    reload(OpticalObject)     # causes FreeCAD to reload Ray.py every time a new Ray is created. Useful while developping the feature.      
    fp = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Mirror")
    OpticalObject.OpticalObjectWorker(fp, base)
    vp = OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return fp
    
def makeAbsorber(base = []):
    '''Python command to create a light ray.'''
    import OpticalObject      
    reload(OpticalObject)     # causes FreeCAD to reload Ray.py every time a new Ray is created. Useful while developping the feature.      
    fp = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Absorber")
    OpticalObject.OpticalObjectWorker(fp, base, type = 'absorber')
    vp = OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return fp
