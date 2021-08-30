# -*- coding: utf-8 -*-

__title__ = 'Ray'
__author__ = 'Christian Bergmann'
__license__ = 'LGPL 3.0'
__doc__ = 'A single ray for raytracing'

import os
import FreeCADGui
from FreeCADGui import doCommand, addCommand
import FreeCAD
from FreeCAD import Vector, Rotation, activeDocument
import Part
import math
import traceback
from wavelength_to_rgb.gentable import wavelen2rgb
from OpticalObject import refraction_index_from_sellmeier
from OpticsWorkbench import isOpticalObject


_icondir_ = os.path.join(os.path.dirname(__file__), 'icons')

INFINITY = 1677216
EPSILON = 1/INFINITY
    



class RayWorker:
    def __init__(self,
                 fp,    # an instance of Part::FeaturePython
                 power = True,
                 spherical = False,
                 beamNrColumns = 1,
                 beamNrRows = 1,
                 beamDistance = 0.1,
                 hideFirst=False,
                 maxRayLength = 1000000,
                 maxNrReflections = 200,
                 wavelength = 580):
        fp.addProperty('App::PropertyBool', 'Spherical', 'Ray',  'False=Beam in one direction, True=Radial or spherical rays').Spherical = spherical
        fp.addProperty('App::PropertyBool', 'Power', 'Ray',  'On or Off').Power = power
        fp.addProperty('App::PropertyQuantity', 'BeamNrColumns', 'Ray',  'number of rays in a beam').BeamNrColumns = beamNrColumns
        fp.addProperty('App::PropertyQuantity', 'BeamNrRows', 'Ray',  'number of rays in a beam').BeamNrRows = beamNrRows
        fp.addProperty('App::PropertyFloat', 'BeamDistance', 'Ray',  'distance between two beams').BeamDistance = beamDistance
        fp.addProperty('App::PropertyBool', 'HideFirstPart', 'Ray',  'hide the first part of every ray').HideFirstPart = hideFirst
        fp.addProperty('App::PropertyFloat', 'MaxRayLength', 'Ray',  'maximum length of a ray').MaxRayLength = maxRayLength
        fp.addProperty('App::PropertyFloat', 'MaxNrReflections', 'Ray',  'maximum number of reflections').MaxNrReflections = maxNrReflections
        fp.addProperty('App::PropertyFloat', 'Wavelength', 'Ray',  'Wavelength of the ray in nm').Wavelength = wavelength        

        fp.Proxy = self
        self.lastRefIdx = 1
        self.iter = 0

    def execute(self, fp):
        '''Do something when doing a recomputation, this method is mandatory'''
        self.redrawRay(fp)

    def onChanged(self, fp, prop):
        '''Do something when a property has changed'''
        if not hasattr(fp, 'iter'): return
        
        proplist = ['Spherical', 'Power', 'HideFirstPart', 'BeamNrColumns', 'BeamNrRows', 'BeamDistance', 'MaxRayLength', 'MaxNrReflections', 'Wavelength']
        if prop in proplist:
            self.redrawRay(fp)

    def redrawRay(self, fp):
        pl = fp.Placement

        linearray = []
        for row in range(0, int(fp.BeamNrRows)):
            for n in range(0, int(fp.BeamNrColumns)):
                if fp.Spherical == False:
                    newpos = Vector(0, fp.BeamDistance * n, fp.BeamDistance * row)
                    pos = pl.Base + pl.Rotation.multVec(newpos)
                    dir = pl.Rotation.multVec(Vector(1, 0, 0))
                else:
                    r = Rotation()
                    r.Axis = Vector(0, 0, 1)
                    r. Angle = n * 2 * math.pi / fp.BeamNrColumns
                    pos = pl.Base
                    dir1 = r.multVec(Vector(1,0,0))

                    if row % 2 == 0:
                        r.Axis = Vector(0, 1, 0)
                    else:
                        r.Axis = Vector(1, 0, 0)

                    r. Angle = row * math.pi / fp.BeamNrRows
                    dir = r.multVec(dir1)

                if fp.Power == True:
                    self.iter = fp.MaxNrReflections
                    ray = Part.makeLine(pos, pos + dir * fp.MaxRayLength / dir.Length)
                    linearray.append(ray)
                    self.lastRefIdx = 1
                    insiders = self.isInsideLens(ray.Vertexes[0])
                    if len(insiders) > 0:
                        self.lastRefIdx = insiders[0].RefractionIndex

                    try:
                        self.traceRay(fp, pos, linearray, True)
                    except Exception as ex:
                        print(ex)
                        traceback.print_exc()
                else:
                    linearray.append(Part.makeLine(pos, pos + dir))

        for line in linearray:
            r2 = Rotation(pl.Rotation)
            r2.invert()
            line.Placement.Rotation = r2
            line.Placement.Base = r2.multVec(line.Placement.Base - pl.Base)

        fp.Shape = Part.makeCompound(linearray)
        fp.Placement = pl
        if fp.Power == False:
            fp.ViewObject.LineColor = (0.5, 0.5, 0.0)
        else:
            try:
                rgb = wavelen2rgb(fp.Wavelength)
            except ValueError:
                # set color to white if outside of visible range
                rgb = (255, 255, 255)  
            r = rgb[0] / 255.0
            g = rgb[1] / 255.0
            b = rgb[2] / 255.0 
            fp.ViewObject.LineColor = (float(r), float(g), float(b), (0.0))

        fp.ViewObject.Transparency = 50


    def traceRay(self, fp, origin, linearray, first=False):
        if len(linearray) == 0: return
        nearest = Vector(INFINITY, INFINITY, INFINITY)
        nearest_point = None
        nearest_part = None
        nearest_obj = None
        nearest_shape = None
        line = linearray[len(linearray) - 1]
        if fp.HideFirstPart and first:
            linearray.remove(line)

        dir = PointVec(line.Vertexes[1]) - PointVec(line.Vertexes[0])
        for optobj in activeDocument().Objects:
            if isOpticalObject(optobj):
                for obj in optobj.Base:
                    if obj.Shape.BoundBox.intersect(origin, dir):
                        if len(obj.Shape.Solids) == 0 and len(obj.Shape.Shells) == 0:
                            for edge in obj.Shape.Edges:
                                normal = self.check2D([line, edge])
                                isec = None
                                if normal.Length == 1:
                                    plane = Part.Plane(obj.Placement.Base, normal)
                                    isec = line.Curve.intersect2d(edge.Curve, plane)
                                else:
                                    try:
                                        isec = line.Curve.intersect(edge.Curve)
                                    except Exception as ex:
                                        print(ex)
                                        traceback.print_exc()

                                if isec:
                                    for p in isec:
                                        if normal == Vector(0, 0, 1):
                                            vec = obj.Placement.Rotation.multVec(Vector(p[0], p[1], 0)) + obj.Placement.Base
                                            dist = vec - origin
                                            p2 = Part.Point(vec)
                                        elif normal == Vector(0, 1, 0):
                                            vec = obj.Placement.Rotation.multVec(Vector(p[0], 0, p[1])) + obj.Placement.Base
                                            dist = vec - origin
                                            p2 = Part.Point(vec)
                                        elif normal == Vector(1, 0, 0):
                                            vec = obj.Placement.Rotation.multVec(Vector(0, p[0], p[1])) + obj.Placement.Base
                                            dist = vec - origin
                                            p2 = Part.Point(vec)
                                        else:
                                            p2 = Part.Point(PointVec(p) + obj.Placement.Base)
                                            dist = PointVec(p) + obj.Placement.Base - origin

                                        vert=Part.Vertex(p2)
                                        if dist.Length > EPSILON and dist.Length < nearest.Length and vert.distToShape(edge)[0] < EPSILON and vert.distToShape(line)[0] < EPSILON:
                                            nearest = dist
                                            nearest_point = p2
                                            nearest_part = edge
                                            nearest_obj = optobj
                                            nearest_shape = obj

                        for face in obj.Shape.Faces:
                            if face.BoundBox.intersect(origin, dir):
                                isec = line.Curve.intersect(face.Surface)
                                if isec:
                                    for p in isec[0]:
                                        dist = Vector(p.X - origin.x, p.Y - origin.y, p.Z - origin.z)
                                        vert=Part.Vertex(p)
                                        if dist.Length > EPSILON and dist.Length < nearest.Length and vert.distToShape(face)[0] < EPSILON and vert.distToShape(line)[0] < EPSILON:
                                            nearest = dist
                                            nearest_point = p
                                            nearest_part = face
                                            nearest_obj = optobj
                                            nearest_shape = obj

        if nearest_part:
            neworigin = PointVec(nearest_point)
            shortline = Part.makeLine(origin, neworigin)

            if fp.HideFirstPart == False or first == False:
                linearray[len(linearray) - 1] = shortline

            self.iter -= 1
            if self.iter == 0: return

            newline = None
            dRay = neworigin - origin

            normal = self.getNormal(nearest_obj, nearest_part, origin, neworigin)
            if normal.Length == 0:
                print('Cannot determine the normal on ' + nearest_obj.Label)
                return
                    
            if nearest_obj.OpticalType == 'mirror':      
                dNewRay = self.mirror(dRay, normal)   
                                                
            elif nearest_obj.OpticalType == 'lens':  
                if len(nearest_obj.Sellmeier) == 6:
                    n = refraction_index_from_sellmeier(fp.Wavelength, nearest_obj.Sellmeier)                           
                else:
                    n = nearest_obj.RefractionIndex

                if self.isInsidePart(nearest_shape, shortline.Vertexes[0]):
                    oldRefIdx = n
                    newRefIdx = self.lastRefIdx
                else:
                    oldRefIdx = self.lastRefIdx
                    newRefIdx = n
                      
                ray1 = dRay / dRay.Length
                dNewRay = self.snellsLaw(ray1, oldRefIdx, newRefIdx, normal)

            else: return

            newline = Part.makeLine(neworigin, neworigin - dNewRay * fp.MaxRayLength / dNewRay.Length)
            linearray.append(newline)
            if newline:
                self.traceRay(fp, neworigin, linearray)


    def getNormal(self, nearest_obj, nearest_part, origin, neworigin):
        dRay = neworigin - origin
        if hasattr(nearest_part, 'Curve'):
            param = nearest_part.Curve.parameter(neworigin)
            tangent = nearest_part.tangentAt(param)
            normal1 = dRay.cross(tangent)
            normal = tangent.cross(normal1)
            normal = normal / normal.Length

        elif hasattr(nearest_part, 'Surface'):
            uv = nearest_part.Surface.parameter(neworigin)
            normal = nearest_part.normalAt(uv[0], uv[1])
        else:
            return Vector(0, 0, 0)

        cosangle = dRay * normal / (dRay.Length * normal.Length)
        if cosangle < 0:
            normal = -normal

        return normal


    def mirror(self, dRay, normal):
        return 2 * normal * (dRay * normal) - dRay


    def snellsLaw(self, ray, n1, n2, normal):
        #print('snell ' + str(n1) + '/' + str(n2))
        root = 1 - n1/n2 * normal.cross(ray) * normal.cross(ray)
        if root < 0: # total reflection
            return self.mirror(ray, normal)

        return -n1/n2 * normal.cross( (-normal).cross(ray)) - normal * math.sqrt(root)


    def check2D(self, objlist):
        nvec = Vector(1, 1, 1)
        for obj in objlist:
            bbox = obj.BoundBox
            if bbox.XLength > EPSILON: nvec.x = 0
            if bbox.YLength > EPSILON: nvec.y = 0
            if bbox.ZLength > EPSILON: nvec.z = 0

        return nvec


    def isInsidePart(self, part, vertex):
        return part.Shape.distToShape(Part.Vertex(vertex))[0] < EPSILON
        
    def isInsideLens(self, vertex):
        ret = []
        for optobj in activeDocument().Objects:
            if isOpticalObject(optobj) and optobj.OpticalType == 'lens':
                for obj in optobj.Base:
                    if self.isInsidePart(obj, vertex):
                        ret.append(optobj)

        return ret
        


def PointVec(point):
    '''Converts a Part::Point to a FreeCAD::Vector'''
    return Vector(point.X, point.Y, point.Z)


class RayViewProvider:
    def __init__(self, vobj):
        '''Set this object to the proxy object of the actual view provider'''
        vobj.Proxy = self
        self.Object = vobj.Object

    def getIcon(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        if self.Object.BeamNrColumns * self.Object.BeamNrRows <= 1:
            return os.path.join(_icondir_, 'ray.svg')
        elif self.Object.Spherical:
            return os.path.join(_icondir_, 'sun.svg')
        else:
            return os.path.join(_icondir_, 'rayarray.svg')

    def attach(self, vobj):
        '''Setup the scene sub-graph of the view provider, this method is mandatory'''
        self.Object = vobj.Object
        self.onChanged(vobj, 'Power')

    def updateData(self, fp, prop):
        '''If a property of the handled feature has changed we have the chance to handle this here'''
        pass

    def claimChildren(self):
        '''Return a list of objects that will be modified by this feature'''
        return []

    def onDelete(self, feature, subelements):
        '''Here we can do something when the feature will be deleted'''
        return True

    def onChanged(self, fp, prop):
        '''Here we can do something when a single property got changed'''
        pass

    def __getstate__(self):
        '''When saving the document this object gets stored using Python's json module.\
                Since we have some un-serializable parts here -- the Coin stuff -- we must define this method\
                to return a tuple of all serializable objects or None.'''
        return None

    def __setstate__(self, state):
        '''When restoring the serialized object from document we have the chance to set some internals here.\
                Since no data were serialized nothing needs to be done here.'''
        return None


class Ray():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''

    def Activated(self):
        '''Will be called when the feature is executed.'''
        # Generate commands in the FreeCAD python console to create Ray
        doCommand('import OpticsWorkbench')
        doCommand('OpticsWorkbench.makeRay()')


    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if activeDocument():
            return(True)
        else:
            return(False)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'ray.svg'),
                'Accel' : '', # a default shortcut (optional)
                'MenuText': 'Ray (monochrome)',
                'ToolTip' : __doc__ }


class RaySun():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''

    def Activated(self):
        '''Will be called when the feature is executed.'''
        # Generate commands in the FreeCAD python console to create Ray
        doCommand('import OpticsWorkbench')
        doCommand('OpticsWorkbench.makeSunRay()')

    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if activeDocument():
            return(True)
        else:
            return(False)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'raysun.svg'),
                'Accel' : '', # a default shortcut (optional)
                'MenuText': 'Ray (sun light)',
                'ToolTip' : 'A bunch of rays with different wavelengths of visible light' }

class Beam2D():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''

    def Activated(self):
        '''Will be called when the feature is executed.'''
        # Generate commands in the FreeCAD python console to create Ray
        doCommand('import OpticsWorkbench')
        doCommand('OpticsWorkbench.makeRay(beamNrColumns=50, beamDistance=0.1)')


    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if activeDocument():
            return(True)
        else:
            return(False)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'rayarray.svg'),
                'Accel' : '', # a default shortcut (optional)
                'MenuText': '2D Beam',
                'ToolTip' : 'A row of multiple rays for raytracing' }

class RadialBeam2D():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''

    def Activated(self):
        '''Will be called when the feature is executed.'''
        # Generate commands in the FreeCAD python console to create Ray
        doCommand('import OpticsWorkbench')
        doCommand('OpticsWorkbench.makeRay(beamNrColumns=64, spherical=True)')


    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if activeDocument():
            return(True)
        else:
            return(False)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'sun.svg'),
                'Accel' : '', # a default shortcut (optional)
                'MenuText': '2D Radial Beam',
                'ToolTip' : 'Rays coming from one point going to all directions in a 2D plane' }


class SphericalBeam():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''

    def Activated(self):
        '''Will be called when the feature is executed.'''
        # Generate commands in the FreeCAD python console to create Ray
        doCommand('import OpticsWorkbench')
        doCommand('OpticsWorkbench.makeRay(beamNrColumns=32, beamNrRows=32, spherical=True)')


    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if activeDocument():
            return(True)
        else:
            return(False)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'sun3D.svg'),
                'Accel' : '', # a default shortcut (optional)
                'MenuText': 'Spherical Beam',
                'ToolTip' : 'Rays coming from one point going to all directions' }


class RedrawAll():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''

    def Activated(self):
        '''Will be called when the feature is executed.'''
        # Generate commands in the FreeCAD python console to create Ray
        doCommand('import OpticsWorkbench')
        doCommand('OpticsWorkbench.restartAll()')


    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if activeDocument():
            return(True)
        else:
            return(False)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'Anonymous_Lightbulb_Lit.svg'),
                'Accel' : '', # a default shortcut (optional)
                'MenuText': '(Re)start simulation',
                'ToolTip' : '(Re)start simulation' }

class AllOff():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''

    def Activated(self):
        '''Will be called when the feature is executed.'''
        # Generate commands in the FreeCAD python console to create Ray
        doCommand('import OpticsWorkbench')
        doCommand('OpticsWorkbench.allOff()')


    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if activeDocument():
            return(True)
        else:
            return(False)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'Anonymous_Lightbulb_Off.svg'),
                'Accel' : '', # a default shortcut (optional)
                'MenuText': 'Switch off lights',
                'ToolTip' : 'Switch off all rays and beams' }

addCommand('Ray (monochrome)', Ray())
addCommand('Ray (sun light)', RaySun())
addCommand('Beam', Beam2D())
addCommand('2D Radial Beam', RadialBeam2D())
addCommand('Spherical Beam', SphericalBeam())
addCommand('Start', RedrawAll())
addCommand('Off', AllOff())
