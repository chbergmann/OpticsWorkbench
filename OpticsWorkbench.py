# -*- coding: utf-8 -*-

import os
from FreeCAD import Vector, Rotation, activeDocument
import Ray
import OpticalObject
import SunRay
from numpy import linspace
from importlib import reload
import Plot


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
            wavelength = 580,
            order = 0,
            coneAngle = 360,
            ignoredElements=[],
            baseShape = None):
    reload(Ray)
    '''Python command to create a light ray.'''
    name = 'Ray'
    if beamNrColumns * beamNrRows > 1:
        name = 'Beam'
    if baseShape:
        name = 'Emitter'

    fp = activeDocument().addObject('Part::FeaturePython', name)
    fp.Placement.Base = position
    fp.Placement.Rotation = Rotation(Vector(1, 0, 0), direction)
    Ray.RayWorker(fp, power, spherical, beamNrColumns, beamNrRows, beamDistance, hideFirst, maxRayLength, maxNrReflections, wavelength, order, coneAngle, ignoredElements, baseShape)
    Ray.RayViewProvider(fp.ViewObject)
    recompute()
    return fp
   
    
def makeSunRay(position = Vector(0, 0, 0),
            direction = Vector(1, 0, 0),
            power = True,
            beamNrColumns = 1,
            beamNrRows = 1,
            beamDistance = 0.1,
            spherical = False,
            hideFirst = False,
            maxRayLength = 1000000,
            maxNrReflections = 900,
            wavelength_from = 450,
            wavelength_to = 750,
            num_rays = 70,
            order = 1,
            ignoredElements=[]):
    reload(SunRay)
    rays = []
    for l in linspace(wavelength_from, wavelength_to, num_rays):
        ray = makeRay(position = position,
            direction = direction,
            power = power,
            beamNrColumns=beamNrColumns,
            beamNrRows=beamNrRows,
            beamDistance=beamDistance,
            spherical=spherical,
            hideFirst = hideFirst,
            maxRayLength = maxRayLength,
            maxNrReflections = maxNrReflections,
            wavelength = l,
            order = order,
            ignoredElements = ignoredElements)
        ray.ViewObject.LineWidth = 1
        rays.append(ray)

    fp = activeDocument().addObject('Part::FeaturePython','SunRay')
    SunRay.SunRayWorker(fp, rays)
    SunRay.SunRayViewProvider(fp.ViewObject)
    recompute()
    return fp

    # reload(Ray)
    # doc = activeDocument()
    # rays = []
    # for l in linspace(wavelength_from, wavelength_to, num_rays):
    #     ray = makeRay(position = position,
    #         direction = direction,
    #         power = power,
    #         beamNrColumns=beamNrColumns,
    #         beamNrRows=beamNrRows,
    #         beamDistance=beamDistance,
    #         spherical=spherical,
    #         hideFirst = hideFirst,
    #         maxRayLength = maxRayLength,
    #         maxNrReflections = maxNrReflections,
    #         wavelength = l,
    #         order = order)
    #     ray.ViewObject.LineWidth = 1
    #     rays.append(ray)

    # group = doc.addObject('App::DocumentObjectGroup','SunRay')
    # group.Group = rays
    # recompute()  
    

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
            
        elif Ray.isOpticalObject(obj):
            hitname = 'HitsFrom'
            hitcoordsname = 'HitCoordsFrom'
            for a in dir(obj):
                if a.startswith('HitsFrom') or a.startswith('HitCoordsFrom'):
                    obj.removeProperty(a)
            
    recompute()

def makeMirror(base = [], collectStatistics = False):
    #reload(OpticalObject)
    '''All FreeCAD objects in base will be optical mirrors.'''
    fp = activeDocument().addObject('Part::FeaturePython', 'Mirror')
    OpticalObject.OpticalObjectWorker(fp, base, type = 'mirror', collectStatistics = collectStatistics)
    OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    recompute()
    return fp

def makeSplitter(base = [], collectStatistics = False):
    #reload(OpticalObject)
    '''All FreeCAD objects in base will be optical mirrors.'''
    fp = activeDocument().addObject('Part::FeaturePython', 'Splitter')
    OpticalObject.OpticalObjectWorker(fp, base, type = 'splitter', collectStatistics = collectStatistics)
    OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    recompute()
    return fp

def makeAbsorber(base = [], collectStatistics = False):
    #reload(OpticalObject)
    '''All FreeCAD objects in base will be optical light absorbers.'''
    fp = activeDocument().addObject('Part::FeaturePython', 'Absorber')
    OpticalObject.OpticalObjectWorker(fp, base, type = 'absorber', collectStatistics = collectStatistics) 
    OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    recompute()
    return fp

def makeLens(base = [], RefractionIndex = 0, material = 'Quartz', collectStatistics = False):
    #reload(OpticalObject)
    '''All FreeCAD objects in base will be optical lenses.'''
    fp = activeDocument().addObject('Part::FeaturePython', 'Lens')
    OpticalObject.LensWorker(fp, base, RefractionIndex, material, collectStatistics)
    OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    recompute()
    return fp

def makeGrating(base=[], RefractionIndex=1, material='', lpm = 500, GratingType = "reflection", GratingLinesPlane = Vector(0,1,0), order = 1, collectStatistics = False):
    #reload(OpticalObject)
    '''All FreeCAD objects in base will be diffraction gratings.'''
    fp = activeDocument().addObject('Part::FeaturePython', 'Grating')
    OpticalObject.GratingWorker(fp, base, RefractionIndex, material, lpm, GratingType, GratingLinesPlane, order, collectStatistics)
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
    print("attr_names", attr_names)
    print("coords_per_beam", coords_per_beam)
    print("all_coords", all_coords)
    
    x = -all_coords[:,1]
    y = all_coords[:,2]       
    
    if len(all_coords) > 0:
        plt.scatter(x, y)
        plt.show()


def drawPlot(selectedObjList):
    ## Create the list of selected absorbers; if none then skip
    Plot.PlotRayHits.plot3D(selectedObjList)


def Hits2CSV():
    
    sheet = activeDocument().addObject('Spreadsheet::Sheet', 'RayHits')
            
    sheet.set('A1','Absorber')
    sheet.set('B1','Ray')
    sheet.set('C1','X-axis')
    sheet.set('D1','Y-axis')
    sheet.set('E1','Z-axis')
    row = 1
    
    coords = []
    attr_names=[]
    coords_per_beam = []
    for eachObject in activeDocument().Objects:
        if Ray.isOpticalObject(eachObject):
            #all_coords = np.array([coord for coords in coords_per_beam for coord in coords])
            for attr in dir(eachObject):
                if attr.startswith('HitCoordsFrom'):
                    coords_per_beam = getattr(eachObject, attr)
                    for co in coords_per_beam:
                        row += 1
                        sheet.set('A' + str(row), eachObject.Label)
                        sheet.set('B' + str(row), attr[13:])
                        sheet.set('C' + str(row), str(co[0]))
                        sheet.set('D' + str(row), str(co[1]))
                        sheet.set('E' + str(row), str(co[2]))
    
    sheet.recompute()
    sheet.ViewObject.doubleClicked()
 
