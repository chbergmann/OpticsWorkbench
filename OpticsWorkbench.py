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
    name = 'Ray'
    if beamNrColumns * beamNrRows > 1:
        name = 'Beam'
        
    fp = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', name)
    fp.Placement.Base = position
    Ray.RayWorker(fp, direction, power, beamNrColumns, beamNrRows, beamDistance)
    Ray.RayViewProvider(fp.ViewObject)
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

def makeLens(base = [], RefractionIndex = 0, material = 'Flint glass'):
    '''All FreeCAD objects in base will be optical lenses.'''
    import OpticalObject      
    reload(OpticalObject)     # causes FreeCAD to reload Ray.py every time a new Ray is created. Useful while developping the feature.      
    fp = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Lens")
    OpticalObject.LensWorker(fp, base, RefractionIndex, material)
    OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return fp