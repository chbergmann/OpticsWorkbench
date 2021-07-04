# -*- coding: utf-8 -*-

__title__ = "Ray"
__author__ = "Christian Bergmann"
__license__ = "LGPL 3.0"
__doc__ = "A single ray for raytracing"

import os
import FreeCADGui
import FreeCAD
from FreeCAD import Vector, Rotation
import Part
import math

_icondir_ = os.path.join(os.path.dirname(__file__), 'icons')
    
INFINITY = 1677216  
EPSILON = 1/INFINITY
    
class RayWorker:
    def __init__(self, 
                 fp,    # an instance of Part::FeaturePython
                 direction = Vector(1, 0, 0),
                 power = True,
                 beamNrColumns = 1,
                 beamNrRows = 1,
                 beamDistance = 0.1,                 
                 maxIterations = 1000):
        fp.addProperty("App::PropertyVector", "Direction", "Ray",  "Direction of the ray").Direction = direction
        fp.addProperty("App::PropertyBool", "Power", "Ray",  "On or Off").Power = power
        fp.addProperty("App::PropertyQuantity", "BeamNrColumns", "Ray",  "number of rays in a beam").BeamNrColumns = beamNrColumns
        fp.addProperty("App::PropertyQuantity", "BeamNrRows", "Ray",  "number of rays in a beam").BeamNrRows = beamNrRows
        fp.addProperty("App::PropertyFloat", "BeamDistance", "Ray",  "distance between two beams").BeamDistance = beamDistance
        fp.addProperty("App::PropertyQuantity", "MaxNumberRays", "Ray",  "maximum number of reflections").MaxNumberRays = maxIterations
        
        fp.Proxy = self
        self.iter = 0
    
    def execute(self, fp):
        '''Do something when doing a recomputation, this method is mandatory'''
        self.redrawRay(fp)
        
    def onChanged(self, fp, prop):
        '''Do something when a property has changed'''
        proplist = ["Direction", "Power", "MaxNumberRays", "BeamNrColumns", "BeamNrRows", "BeamDistance"]
        if prop in proplist:
            self.redrawRay(fp)
            
    def redrawRay(self, fp):
        self.iter = 0
        pl = fp.Placement       
        
        linearray = []
        for n in range(0, int(fp.BeamNrColumns)): 
            if fp.Direction.Length > EPSILON:
                newpos = Vector(0, fp.BeamDistance * n, 0)
                pos = pl.Base + pl.Rotation.multVec(newpos)
                dir = pl.Rotation.multVec(fp.Direction)
            else:
                r = Rotation()
                r.Axis = Vector(0, 0, 1)
                r. Angle = n * 2 * math.pi / fp.BeamNrColumns
                pos = pl.Base
                dir = r.multVec(Vector(1,0,0))
                   
            if fp.Power == True: 
                linearray.append(Part.makeLine(pos, pos + dir * INFINITY))
                self.traceRay(fp, pos, linearray)
            else:
                linearray.append(Part.makeLine(pos, pos + dir))                
                         
        for line in linearray:
            r2 = FreeCAD.Rotation(pl.Rotation)
            r2.invert()
            line.Placement.Rotation = r2
            line.Placement.Base = r2.multVec(line.Placement.Base - pl.Base)
        
        fp.Shape = Part.makeCompound(linearray)
        fp.Placement = pl
        if fp.Power == False:
            fp.ViewObject.LineColor = (0.5, 0.5, 0.00)
        else:
            fp.ViewObject.LineColor = (1.00,1.00,0.00)
            
        fp.ViewObject.Transparency = 50
        
        
    def traceRay(self, fp, origin, linearray):
        if len(linearray) == 0: return
        nearest = Vector(INFINITY, INFINITY, INFINITY)
        nearest_point = None
        nearest_part = None
        nearest_obj = None
        line = linearray[len(linearray) - 1]
        
        for obj in FreeCAD.ActiveDocument.Objects:
            if obj.TypeId == 'Part::FeaturePython' and hasattr(obj, 'OpticalType'):
                for edge in obj.Shape.Edges:
                    normal = self.check2D([line, edge])
                    if normal.Length == 1:
                        plane = Part.Plane(obj.Placement.Base, normal)
                        isec = line.Curve.intersect2d(edge.Curve, plane)
                    else:
                        isec = line.Curve.intersect(edge.Curve)

                    if isec:
                        for p in isec:
                            if normal == Vector(0, 0, 1):
                                vec = obj.Placement.Rotation.multVec(Vector(p[0], p[1], 0))
                                dist = vec - origin
                                p = Part.Point(vec)
                            elif normal == Vector(0, 1, 0):
                                vec = obj.Placement.Rotation.multVec(Vector(p[0], 0, p[1]))
                                dist = vec - origin
                                p = Part.Point(vec)
                            elif normal == Vector(1, 0, 0):
                                vec = obj.Placement.Rotation.multVec(Vector(0, p[0], p[1]))
                                dist = vec - origin
                                p = Part.Point(vec)
                            else:
                                dist = Vector(p.X - origin.x, p.Y - origin.y, p.Z - origin.z)                                
                                
                            vert=Part.Vertex(p)                            
                            if vert.distToShape(edge)[0] < EPSILON and vert.distToShape(line)[0] < EPSILON and dist.Length > EPSILON and dist.Length < nearest.Length:                     
                                nearest = dist
                                nearest_point = p
                                nearest_part = edge
                                nearest_obj = obj
                            
                        
        if nearest_part:
            neworigin = PointVec(nearest_point)
            shortline = Part.makeLine(origin, neworigin)
            linearray[len(linearray) - 1] = shortline
            
            if nearest_obj.OpticalType == 'mirror':           
                self.iter = self.iter + 1
                if self.iter > fp.MaxNumberRays: return
                
                tangent = self.findTangent(nearest_part, neworigin)
                newedge = shortline.mirror(neworigin, tangent)
                vend = PointVec(newedge.Vertexes[0])         
                newline = Part.makeLine(neworigin, vend + (vend - neworigin) * INFINITY)
                linearray.append(newline)
                try:
                    self.traceRay(fp, neworigin, linearray)
                except Exception as ex:
                    print(ex)
            
        
    def findTangent(self, shape, point):
        if shape.Curve.TypeId == 'Part::GeomLine':
            return PointVec(shape.Vertexes[1]) - PointVec(shape.Vertexes[0])
        
        inc = (shape.LastParameter - shape.FirstParameter) / 10000
        if inc == 0: return
        nearest = shape.FirstParameter
        minlen = INFINITY
        p = shape.FirstParameter
        while p <= shape.LastParameter:
            v = shape.valueAt(p)
            if (point - v).Length < minlen:
                minlen = (point - v).Length
                nearest = p
                
            p = p + inc
            
        return shape.tangentAt(nearest)


    def check2D(self, objlist):
        nvec = Vector(1, 1, 1)
        for obj in objlist:
            bbox = obj.BoundBox
            if bbox.XLength > EPSILON: nvec.x = 0
            if bbox.YLength > EPSILON: nvec.y = 0
            if bbox.ZLength > EPSILON: nvec.z = 0
            
        return nvec
             
                  
def PointVec(point):
    """Converts a Part::Point to a FreeCAD::Vector"""
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
        elif self.Object.Direction.Length < EPSILON:
            return os.path.join(_icondir_, 'sun.svg')
        else:
            return os.path.join(_icondir_, 'rayarray.svg')

    def attach(self, vobj):
        '''Setup the scene sub-graph of the view provider, this method is mandatory'''
        self.Object = vobj.Object
        self.onChanged(vobj, "Power")
 
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
        FreeCADGui.doCommand("import OpticsWorkbench")
        FreeCADGui.doCommand("OpticsWorkbench.makeRay()")
                  

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        if FreeCAD.ActiveDocument:
            return(True)
        else:
            return(False)
        
    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'ray.svg'),
                'Accel' : "", # a default shortcut (optional)
                'MenuText': "Ray",
                'ToolTip' : __doc__ }
                
class Beam2D():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''  
      
    def Activated(self):
        '''Will be called when the feature is executed.'''
        # Generate commands in the FreeCAD python console to create Ray
        FreeCADGui.doCommand("import OpticsWorkbench")
        FreeCADGui.doCommand("OpticsWorkbench.makeRay(beamNrColumns=50, beamDistance=0.1)")
                  

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        if FreeCAD.ActiveDocument:
            return(True)
        else:
            return(False)
        
    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'rayarray.svg'),
                'Accel' : "", # a default shortcut (optional)
                'MenuText': "2D Beam",
                'ToolTip' : __doc__ }
                
class RadialBeam2D():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''  
      
    def Activated(self):
        '''Will be called when the feature is executed.'''
        # Generate commands in the FreeCAD python console to create Ray
        FreeCADGui.doCommand("import OpticsWorkbench")
        FreeCADGui.doCommand("OpticsWorkbench.makeRay(beamNrColumns=64, direction=FreeCAD.Vector(0, 0, 0))")
                  

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        if FreeCAD.ActiveDocument:
            return(True)
        else:
            return(False)
        
    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'sun.svg'),
                'Accel' : "", # a default shortcut (optional)
                'MenuText': "2D Radial Beam",
                'ToolTip' : __doc__ }

class RedrawAll():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''  
      
    def Activated(self):
        '''Will be called when the feature is executed.'''
        # Generate commands in the FreeCAD python console to create Ray
        FreeCADGui.doCommand("import OpticsWorkbench")
        FreeCADGui.doCommand("OpticsWorkbench.restartAll()")
                  

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        if FreeCAD.ActiveDocument:
            return(True)
        else:
            return(False)
        
    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'Anonymous_Lightbulb_Lit.svg'),
                'Accel' : "", # a default shortcut (optional)
                'MenuText': "(Re)start simulation",
                'ToolTip' : __doc__ }
                
class AllOff():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''  
      
    def Activated(self):
        '''Will be called when the feature is executed.'''
        # Generate commands in the FreeCAD python console to create Ray
        FreeCADGui.doCommand("import OpticsWorkbench")
        FreeCADGui.doCommand("OpticsWorkbench.allOff()")
                  

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        if FreeCAD.ActiveDocument:
            return(True)
        else:
            return(False)
        
    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'Anonymous_Lightbulb_Off.svg'),
                'Accel' : "", # a default shortcut (optional)
                'MenuText': "Switch off lights",
                'ToolTip' : __doc__ }

FreeCADGui.addCommand('Ray', Ray())
FreeCADGui.addCommand('2D Beam', Beam2D())
FreeCADGui.addCommand('2D Radial Beam', RadialBeam2D())
FreeCADGui.addCommand('Start', RedrawAll())
FreeCADGui.addCommand('Off', AllOff())
