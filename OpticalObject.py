# -*- coding: utf-8 -*-

__title__ = "OpticalObject"
__author__ = "Christian Bergmann"
__license__ = "LGPL 3.0"
__doc__ = "Declare your FreeCAD objects to be optical mirrors, lenses or absorbers"

import os
import FreeCADGui
import FreeCAD

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
        pass
        
    def onChanged(self, fp, prop):
        pass


class LensWorker:
    def __init__(self, 
                 fp,    # an instance of Part::FeaturePython
                 base = [],
                 RefractionIndex = 1,
                 material = ''):
        fp.addProperty("App::PropertyEnumeration", "OpticalType", "Lens", "").OpticalType = ['lens'] 
        fp.addProperty("App::PropertyLinkList",  "Base",   "Lens",   "FreeCAD objects to be lenses").Base = base
        fp.addProperty("App::PropertyFloat",  "RefractionIndex",   "Lens",   "depends on material").RefractionIndex = RefractionIndex
        fp.OpticalType = 'lens'  
        
        mat = []
        for m in self.getMaterial():
            mat.append(m[0])
          
        fp.addProperty("App::PropertyEnumeration", "Material", "Lens", "").Material = mat
        
        self.update = True 
        fp.Proxy = self
        
        if material in mat:
            fp.Material = material
        else:
            fp.Material = '?'
            
        
    def getMaterial(self):
        return [('?', 0),
            ('Vacuum',  1),
            ('Air',     1.000293),
            ('Water',   1.333),
            ('Ethanol',     1.36),
            ('Olive oil',   1.47),
            ('Ice',     1.31),
            ('Quartz',   1.46),
            ('PMMA (plexiglas)',  1.49),
            ('Window glass',    1.52),
            ('Polycarbonate',   1.58),
            ('Flint glass',    1.69),
            ('Sapphire',    1.77),
            ('Cubic zirconia',  2.15),
            ('Diamond',     2.42)]
            
    def execute(self, fp):
        pass
        
    def onChanged(self, fp, prop):
        if not self.update: return
        self.update = False
        
        if prop == 'Material':
            for m in self.getMaterial():
                if fp.Material == m[0]:
                    fp.RefractionIndex = m[1]
                    break
                    
        if prop == 'RefractionIndex':
            fp.Material = '?'
            
        self.update = True
        
    
class OpticalObjectViewProvider:
    def __init__(self, vobj):
        '''Set this object to the proxy object of the actual view provider'''
        vobj.Proxy = self
        self.Object = vobj.Object
            
    def getIcon(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        if self.Object.OpticalType == 'mirror':
            return os.path.join(_icondir_, 'mirror.svg')
            
        if self.Object.OpticalType == 'absorber':
            return os.path.join(_icondir_, 'absorber.svg')
            
        return os.path.join(_icondir_, 'lens.svg')

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
                
class OpticalLens():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''  
      
    def Activated(self):
        selection = FreeCADGui.Selection.getSelectionEx()
        FreeCADGui.doCommand("import OpticsWorkbench")
        FreeCADGui.doCommand("objects = []")
        for sel in selection:
            FreeCADGui.doCommand("objects.append(FreeCAD.ActiveDocument.getObject('%s'))"%(sel.ObjectName))
                
        FreeCADGui.doCommand("OpticsWorkbench.makeLens(objects, material='Window glass')")               

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        if FreeCAD.ActiveDocument:
            return(True)
        else:
            return(False)
        
    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'lens.svg'),
                'Accel' : "", # a default shortcut (optional)
                'MenuText': 'Optical Lens',
                'ToolTip' : 'Declare your FreeCAD objects to be optical lenses' }                
                
FreeCADGui.addCommand('Mirror', OpticalMirror())
FreeCADGui.addCommand('Absorber', OpticalAbsorber())
FreeCADGui.addCommand('Lens', OpticalLens())
