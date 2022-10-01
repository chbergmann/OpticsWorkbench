# -*- coding: utf-8 -*-

import os
from FreeCAD import Vector, Rotation, activeDocument
import Ray
import OpticalObject
import SunRay
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
    reload(SunRay)
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

    fp = activeDocument().addObject('Part::FeaturePython','SunRay')
    SunRay.SunRayWorker(fp, rays)
    SunRay.SunRayViewProvider(fp.ViewObject)
    recompute()
    return fp
    

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
    '''All FreeCAD objects in base will be optical mirrors.'''
    fp = activeDocument().addObject('Part::FeaturePython', 'Mirror')
    OpticalObject.OpticalObjectWorker(fp, base)
    OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    recompute()
    return fp

def makeAbsorber(base = []):
    '''All FreeCAD objects in base will be optical light absorbers.'''
    fp = activeDocument().addObject('Part::FeaturePython', 'Absorber')
    OpticalObject.OpticalObjectWorker(fp, base, type = 'absorber')
    OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    recompute()
    return fp

def makeLens(base = [], RefractionIndex = 0, material = 'Quartz'):
    '''All FreeCAD objects in base will be optical lenses.'''
    fp = activeDocument().addObject('Part::FeaturePython', 'Lens')
    OpticalObject.LensWorker(fp, base, RefractionIndex, material)
    OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    recompute()
    return fp

def isRay(obj):
    return hasattr(obj, 'Power') and hasattr(obj, 'BeamNrColumns')

def plot_xy(absorber):
    import numpy as np
    import matplotlib.pyplot as plt
    
    coords = []
    attr_names = [attr for attr in dir(absorber) if attr.startswith('HitCoordsFrom')]
    coords_per_beam = [getattr(absorber, attr) for attr in attr_names]
    all_coords = np.array([coord for coords in coords_per_beam for coord in coords])
    x = -all_coords[:,1]
    y = all_coords[:,2]       
    
    if len(all_coords) > 0:
        plt.scatter(x, y)
        plt.show()
