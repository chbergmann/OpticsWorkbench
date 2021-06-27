# -*- coding: utf-8 -*-

__title__ = "Ray"
__author__ = "Christian Bergmann"
__license__ = "LGPL 3.0"
__doc__ = "A single ray for raytracing"

import os
import FreeCADGui
import FreeCAD
from FreeCAD import Vector
import Part

__dir__ = os.path.dirname(__file__)
__iconpath__ = os.path.join(__dir__, 'ray.svg')
    
INFINITY = 1e7  
EPSILON = 1e-7  
    
class RayWorker:
    def __init__(self, 
                 fp,    # an instance of Part::FeaturePython
                 position = Vector(0, 0, 0),
                 direction = Vector(1, 0, 0),
                 power = True,
                 maxIterations = 10000):
        fp.addProperty("App::PropertyVector", "Position",  "Ray",  "This object will be modified by this feature").Position = position
        fp.addProperty("App::PropertyVector", "Direction", "Ray",  "Colorize the feature green").Direction = direction
        fp.addProperty("App::PropertyBool", "Power", "Ray",  "On or Off").Power = power
        fp.addProperty("App::PropertyQuantity", "MaxIterations", "Ray",  "maximum number of reflections").MaxIterations = maxIterations
        
        fp.Proxy = self
        self.iter = 0
        self.fp = fp
    
    def execute(self, fp):
        '''Do something when doing a recomputation, this method is mandatory'''
        self.redrawRay(fp)
        
    def onChanged(self, fp, prop):
        '''Do something when a property has changed'''
        if prop == "Position" or prop == "Direction" or prop == "Power":
            self.redrawRay(fp)
            
    def redrawRay(self, fp):
        
            
        if fp.Power == False:   
            fp.Shape = Part.makeLine(fp.Position, fp.Direction)
            fp.ViewObject.LineColor = (0.2, 0.2, 0.00)
            return          
        
        linearray = [ Part.makeLine(fp.Position, fp.Direction * INFINITY) ] 
        self.traceRay(fp.Position, linearray)
        
        fp.Shape = Part.makeCompound(linearray)
        fp.ViewObject.LineColor = (1.00,1.00,0.00)
        
    def traceRay(self, origin, linearray):
        if len(linearray) == 0: return
        nearest = Vector(INFINITY, INFINITY, INFINITY)
        nearest_point = None
        nearest_part = None
        line = linearray[len(linearray) - 1]
        
        for obj in FreeCAD.ActiveDocument.Objects:
            if obj.Name != "Ray":
                for edge in obj.Shape.Edges:
                    isec = line.Curve.intersect(edge.Curve)
                    for p in isec:
                        dist = Vector(p.X - origin.x, p.Y - origin.y, p.Z - origin.z)
                        vert=Part.Vertex(p)
                        if vert.distToShape(edge)[0] < EPSILON and dist.Length > EPSILON and dist.Length < nearest.Length:                     
                            nearest = dist
                            nearest_point = p
                            nearest_part = edge
                            
                        
        if nearest_part:
            neworigin = PointVec(nearest_point)
            shortline = Part.makeLine(origin, neworigin)
            linearray[len(linearray) - 1] = shortline
            v = nearest_part.Vertexes[1]
            tangent = Vector(v.X - nearest_point.X, v.Y - nearest_point.Y, v.Z - nearest_point.Z)
            newedge = shortline.mirror(neworigin, tangent)
            vend = PointVec(newedge.Vertexes[0])
            newline = Part.makeLine(neworigin, vend + (vend - neworigin) * INFINITY)
            linearray.append(newline)
            self.iter = self.iter + 1
            if self.iter > self.fp.MaxIterations: return
            self.traceRay(neworigin, linearray)
            
        return
        
                
                  
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
        return __iconpath__

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
        return {'Pixmap'  : __iconpath__,
                'Accel' : "", # a default shortcut (optional)
                'MenuText': "Ray",
                'ToolTip' : __doc__ }

FreeCADGui.addCommand('Ray', Ray())
