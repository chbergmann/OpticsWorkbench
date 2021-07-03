# -*- coding: utf-8 -*-

__title__ = "OpticalObject"
__author__ = "Christian Bergmann"
__license__ = "LGPL 3.0"
__doc__ = "Declare your FreeCAD objects to be optical mirrors, lenses or absorbers"

import os
import FreeCADGui
import FreeCAD
from FreeCAD import Vector
import Part

_icondir_ = os.path.join(os.path.dirname(__file__), 'icons')
    
INFINITY = 1677216  
EPSILON = 1/INFINITY
    
class OpticalObjectWorker:
    def __init__(self, 
                 fp,    # an instance of Part::FeaturePython
                 base = [],
                 type = 'mirror'):
        fp.addProperty("App::PropertyEnumeration", "OpticalType", "OpticalObject", "").OpticalType = ['mirror', 'absorber'] 
        fp.addProperty("App::PropertyLinkList",  "Base",   "OpticalObject",   "FreeCAD objects to be mirrors").Base = base
        fp.OpticalType = type    
        fp.Proxy = self
    
    def execute(self, fp):
        shapes = []
        for obj in fp.Base:
            shapes.append(obj.Shape)
            
        fp.Shape = Part.makeCompound(shapes)
        
    def onChanged(self, fp, prop):
        if prop == "Base":
            self.execute(fp)
            
    
class OpticalObjectViewProvider:
    def __init__(self, vobj):
        '''Set this object to the proxy object of the actual view provider'''
        vobj.Proxy = self
        self.Object = vobj.Object
            
    def getIcon(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        if self.Object.OpticalType == 'mirror':
            return os.path.join(_icondir_, 'mirror.svg')
            
        return os.path.join(_icondir_, 'absorber.svg')

    def attach(self, vobj):
        '''Setup the scene sub-graph of the view provider, this method is mandatory'''
        self.Object = vobj.Object
        self.onChanged(vobj, "")
 
    def updateData(self, fp, prop):
        '''If a property of the handled feature has changed we have the chance to handle this here'''
        pass
    
    def claimChildren(self):
        '''Return a list of objects that will be modified by this feature'''
        return self.Object.Base
        
    def onDelete(self, feature, subelements):
        '''Here we can do something when the feature will be deleted'''
        return True
    
    def onChanged(self, fp, prop):
        '''Here we can do something when a single property got changed'''
        pass                    
        
def findTangent(shape, point):
    if shape.Curve.TypeId == 'Part::GeomLine':
        return Vector(v.X - nearest_point.X, v.Y - nearest_point.Y, v.Z - nearest_point.Z)
        
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
            
    
                
class OpticalMirror():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''  
      
    def Activated(self):
        selection = FreeCADGui.Selection.getSelectionEx()
        FreeCADGui.doCommand("import OpticsWorkbench")
        FreeCADGui.doCommand("objects = []")
        for sel in selection:
            FreeCADGui.doCommand("objects.append(FreeCAD.ActiveDocument.getObject('%s'))"%(sel.ObjectName))
            
        FreeCADGui.doCommand("OpticsWorkbench.makeMirror(objects)")              

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        if FreeCAD.ActiveDocument:
            return(True)
        else:
            return(False)
        
    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'mirror.svg'),
                'Accel' : "", # a default shortcut (optional)
                'MenuText': 'Optical Mirror',
                'ToolTip' : 'Declare your FreeCAD objects to be optical mirrors' }


class OpticalAbsorber():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''  
      
    def Activated(self):
        selection = FreeCADGui.Selection.getSelectionEx()
        FreeCADGui.doCommand("import OpticsWorkbench")
        FreeCADGui.doCommand("objects = []")
        for sel in selection:
            FreeCADGui.doCommand("objects.append(FreeCAD.ActiveDocument.getObject('%s'))"%(sel.ObjectName))
                
        FreeCADGui.doCommand("OpticsWorkbench.makeAbsorber(objects)")               

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        if FreeCAD.ActiveDocument:
            return(True)
        else:
            return(False)
        
    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'absorber.svg'),
                'Accel' : "", # a default shortcut (optional)
                'MenuText': 'Optical Absorber',
                'ToolTip' : 'Declare your FreeCAD objects to be optical absorbers' }
                
FreeCADGui.addCommand('Mirror', OpticalMirror())
FreeCADGui.addCommand('Absorber', OpticalAbsorber())
