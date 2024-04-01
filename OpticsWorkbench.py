# -*- coding: utf-8 -*-

import os
from FreeCAD import Vector, Rotation, activeDocument
import Ray
import OpticalObject
import SunRay
import FreeCADGui
from numpy import linspace
from importlib import reload
import datetime
import csv


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
            ignoredElements=[]):
    reload(Ray)
    '''Python command to create a light ray.'''
    name = 'Ray'
    if beamNrColumns * beamNrRows > 1:
        name = 'Beam'

    fp = activeDocument().addObject('Part::FeaturePython', name)
    fp.Placement.Base = position
    fp.Placement.Rotation = Rotation(Vector(1, 0, 0), direction)
    Ray.RayWorker(fp, power, spherical, beamNrColumns, beamNrRows, beamDistance, hideFirst, maxRayLength, maxNrReflections, wavelength, order, coneAngle, ignoredElements)
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
            
    recompute()

def makeMirror(base = []):
    #reload(OpticalObject)
    '''All FreeCAD objects in base will be optical mirrors.'''
    fp = activeDocument().addObject('Part::FeaturePython', 'Mirror')
    OpticalObject.OpticalObjectWorker(fp, base)
    OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    recompute()
    return fp

def makeAbsorber(base = []):
    #reload(OpticalObject)
    '''All FreeCAD objects in base will be optical light absorbers.'''
    fp = activeDocument().addObject('Part::FeaturePython', 'Absorber')
    OpticalObject.OpticalObjectWorker(fp, base, type = 'absorber')
    OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    recompute()
    return fp

def makeLens(base = [], RefractionIndex = 0, material = 'Quartz'):
    #reload(OpticalObject)
    '''All FreeCAD objects in base will be optical lenses.'''
    fp = activeDocument().addObject('Part::FeaturePython', 'Lens')
    OpticalObject.LensWorker(fp, base, RefractionIndex, material)
    OpticalObject.OpticalObjectViewProvider(fp.ViewObject)
    recompute()
    return fp

def makeGrating(base=[], RefractionIndex=1, material='', lpm = 500, GratingType = "reflection", GratingLinesPlane = Vector(0,1,0), order = 1):
    #reload(OpticalObject)
    '''All FreeCAD objects in base will be diffraction gratings.'''
    fp = activeDocument().addObject('Part::FeaturePython', 'Grating')
    OpticalObject.GratingWorker(fp, base, RefractionIndex, material, lpm, GratingType, GratingLinesPlane, order)
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

# def isOpticalObject(obj):
#     return obj.TypeId == 'Part::FeaturePython' and hasattr(obj, 'OpticalType') and hasattr(obj, 'Base')

def plot3D():
    import numpy as np
    import matplotlib.pyplot as plt
    
    
    #Figure out the selected absorber; if multiple absorbers selected, or multiple objects then loop through them all
    # and accumulate data from all of them

    ## Create the list of selected absorbers; if none then skip
    #selectedObjList = App.activeDocument().getSelection()
    selectedObjList = FreeCADGui.Selection.getSelection()
    # may try Gui.Selection.getSelection()
    print("Selected Objects: ", len(selectedObjList))
    if len(selectedObjList) >0:
        coords = []
        attr_names=[]
        coords_per_beam = []
        for eachObject in selectedObjList:
            print("Looping through: ", eachObject.Label)
            try:
                if eachObject.OpticalType == "absorber":
                    #coords = []
                    attr_names[len(attr_names):] = [attr for attr in dir(eachObject) if attr.startswith('HitCoordsFrom')]
                    coords_per_beam[len(coords_per_beam):] = [getattr(eachObject, attr) for attr in attr_names]
                    #all_coords = np.array([coord for coords in coords_per_beam for coord in coords])
                else:
                    print ("Ignoring: ",eachObject.Label)
            except:
                print ("Ignoring: ",eachObject.Label)
        all_coords = np.array([coord for coords in coords_per_beam for coord in coords])    
        if len(all_coords) > 0:
            x = all_coords[:,0]
            y = all_coords[:,1]
            z = all_coords[:,2]       
        
            currentTime = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            docDirectory = os.path.dirname(FreeCADGui.ActiveDocument.Document.FileName)
            #print(docDirectory)
            docName = FreeCADGui.ActiveDocument.Document.Label+"_Hits_" + currentTime+".csv"
            #print(docName)
            myHitsFileName = os.path.join(docDirectory,docName)
            print("Exporting hits to: "+ myHitsFileName)
            
            ### May need to do more for the cases where writing to folder requires special permissions; should at least catch the exception and put a message
            with open(myHitsFileName,"w+", newline='', encoding='utf-8') as myHitsFile:
                csvWriter = csv.writer(myHitsFile,delimiter=',')
                csvWriter.writerow(["X-axis","Y-axis","Z-axis"])
                csvWriter.writerows(all_coords)
            myHitsFile.close

       
            fig = plt.figure()
            ax = fig.add_subplot(projection='3d')
            ax.scatter(x, y, z)
            ax.set_xlabel('X-axis')
            ax.set_ylabel('Y-axis')
            ax.set_zlabel('Z-axis')

            plt.show()
        else:
            print("No ray hits were found")


