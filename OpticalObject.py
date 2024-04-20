# -*- coding: utf-8 -*-

__title__ = 'OpticalObject'
__author__ = 'Christian Bergmann'
__license__ = 'LGPL 3.0'
__doc__ = 'Declare your FreeCAD objects to be optical mirrors, lenses or absorbers'

import os
import FreeCADGui as Gui
import FreeCAD
import math

_icondir_ = os.path.join(os.path.dirname(__file__), 'icons')
    
INFINITY = 1677216  
EPSILON = 1/INFINITY
    
class OpticalObjectWorker:
    def __init__(self, 
                 fp,    # an instance of Part::FeaturePython
                 base = [],
                 type = 'mirror'):
        fp.addProperty('App::PropertyEnumeration', 'OpticalType', 'OpticalObject', '').OpticalType = ['mirror', 'absorber'] 
        fp.addProperty('App::PropertyLinkList',  'Base',   'OpticalObject',   'FreeCAD objects to be mirrors or absorbers').Base = base
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
        self.update = False 
        fp.addProperty('App::PropertyEnumeration', 'OpticalType', 'Lens', '').OpticalType = ['lens'] 
        fp.addProperty('App::PropertyLinkList',  'Base',   'Lens',   'FreeCAD objects to be lenses').Base = base
        fp.addProperty('App::PropertyFloat',  'RefractionIndex',   'Lens',   'Refractive Index at 580nm (depends on material)').RefractionIndex = RefractionIndex
        fp.addProperty(
            'App::PropertyFloatList',  
            'Sellmeier',   
            'Lens',   
            'Sellmeier coefficients. [B1, B2, B3, C1, C2, C3]\n C1, C2, C3 in (nm)².\n Usually noted in (µm)² in literature,\n (µm)²=10⁶(nm)².')

        fp.OpticalType = 'lens'  
        
        material_names = list(getMaterials())  

        fp.addProperty('App::PropertyEnumeration', 'Material', 'Lens', '').Material = material_names
        
        self.update = True 
        fp.Proxy = self
        
        if material in material_names:
            fp.Material = material
        else:
            fp.Material = '?'
            

    def execute(self, fp):
        pass
        
    def onChanged(self, fp, prop):
        if not self.update: return
        self.update = False
        
        if not hasattr(fp, 'Sellmeier'): return
        
        if prop == 'Material':
            #sellmeier = self.getMaterials()[fp.Material]
            sellmeier = getMaterials()[fp.Material]
            fp.Sellmeier = sellmeier
            fp.RefractionIndex = refraction_index_from_sellmeier(wavelength=580, sellmeier=fp.Sellmeier)

        if prop == 'Sellmeier':
            fp.RefractionIndex = refraction_index_from_sellmeier(wavelength=580, sellmeier=fp.Sellmeier)
                    
        if prop == 'RefractionIndex':
            fp.Material = '?'
            fp.Sellmeier = []
            
        self.update = True

class GratingWorker: ### 
    def __init__(self, 
                 fp,    # an instance of Part::FeaturePython
                 base = [],
                 RefractionIndex = 1,
                 material = '',
                 lpm = 500,
                 GratingType = "reflection",
                 GratingLinesPlane = FreeCAD.Vector(0,1,0),
                 order = 1, 
                 ray_order_override = False):
        self.update = False 
        fp.addProperty('App::PropertyEnumeration', 'OpticalType', 'Grating', '').OpticalType = ['grating'] 
        fp.addProperty('App::PropertyLinkList',  'Base',   'Grating',   'FreeCAD objects to be diffraction gratings').Base = base
        fp.addProperty('App::PropertyFloat',  'RefractionIndex',   'Grating',   'Refractive Index at 580nm (depends on material)').RefractionIndex = RefractionIndex
        fp.addProperty(
            'App::PropertyFloatList',  
            'Sellmeier',   
            'Grating',   
            'Sellmeier coefficients. [B1, B2, B3, C1, C2, C3]\n C1, C2, C3 in (nm)².\n Usually noted in (µm)² in literature,\n (µm)²=10⁶(nm)².')
        fp.addProperty('App::PropertyFloat', 'lpm', 'Grating', 'lines per millimeter').lpm = lpm
        fp.addProperty('App::PropertyEnumeration', 'GratingType', 'Grating', 'reflection or transmission').GratingType = ["reflection", "transmission - diffraction at 2nd surface", "transmission - diffraction at 1st surface"]
        fp.addProperty('App::PropertyVector', 'GratingLinesPlane', 'Grating', 'Normal of a hypothetical set of planes that intersect the grating surface, to define the rulings of the grating as these intersection lines').GratingLinesPlane = GratingLinesPlane
        fp.addProperty('App::PropertyFloat', 'order', 'Grating', 'order of diffraction, set by grating').order = order
        fp.addProperty('App::PropertyBool', 'ray_order_override', 'Grating', 'if true, order of grating overrides order of ray, if false, ray order is used').ray_order_override = ray_order_override
        fp.OpticalType = 'grating'
        fp.GratingType = GratingType  
        
        material_names = list(getMaterials())
          
        fp.addProperty('App::PropertyEnumeration', 'Material', 'Grating', '').Material = material_names
        
        self.update = True 
        fp.Proxy = self
        
        if material in material_names:
            fp.Material = material
        else:
            fp.Material = '?'
             

    def execute(self, fp):
        pass
        
    def onChanged(self, fp, prop):
        if not self.update: return
        self.update = False
        
        if not hasattr(fp, 'Sellmeier'): return
        
        if prop == 'Material':
            sellmeier = getMaterials()[fp.Material]
            fp.Sellmeier = sellmeier
            fp.RefractionIndex = refraction_index_from_sellmeier(wavelength=580, sellmeier=fp.Sellmeier)

        if prop == 'Sellmeier':
            fp.RefractionIndex = refraction_index_from_sellmeier(wavelength=580, sellmeier=fp.Sellmeier)
                    
        if prop == 'RefractionIndex':
            fp.Material = '?'
            fp.Sellmeier = []
            
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

        if self.Object.OpticalType == 'grating': ### this paragraph was provided by OpenAI chatgpt at feb.01.2023 
            return os.path.join(_icondir_, 'grating.svg')
            
        if self.Object.OpticalType == 'emitter':
            return os.path.join(_icondir_, 'emitter.svg')
            
        return os.path.join(_icondir_, 'lens.svg')

    def attach(self, vobj):
        '''Setup the scene sub-graph of the view provider, this method is mandatory'''
        self.Object = vobj.Object
        self.onChanged(vobj, '')
 
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
    
    def __getstate__(self):
        '''When saving the document this object gets stored using Python's json module.\
                Since we have some un-serializable parts here we must define this method\
                to return a tuple of all serializable objects or None.'''
        return None

    def __setstate__(self, state):
        '''When restoring the serialized object from document we have the chance to set some internals here.\
                Since no data were serialized nothing needs to be done here.'''
        return None


def getMaterials():
        # https://refractiveindex.info/, from glass-spec-sheets directly or fitted with lambda-n data
        return {
            '?':                 (0, 0, 0, 0, 0, 0),
            'Vacuum':            (0, 0, 0, 0, 0, 0),
            'Air':               (4.334446e-4, 3.470339e-5, 1.118728e-4, 1.118728e4, 0, 0),  #https://physics.stackexchange.com/questions/138584/sellmeier-refractive-index-of-standard-air/138617
            # 'Water':             (0, 0, 0, 0, 0, 0),  # 20°C
            # 'Ethanol':           (0, 0, 0, 0, 0, 0),
            # 'Olive oil':         (0, 0, 0, 0, 0, 0),
            # 'Ice':               (0, 0, 0, 0, 0, 0),
            'Quartz':            (0.6961663, 0.4079426, 0.8974794, 4.67914826e+03, 1.35120631e+04, 9.79340025e+07),
            'PMMA (plexiglass)': (1.1819, 0, 0, 11313, 0,  0),
            'NBK7/Window glass':      (1.03961212, 0.231792344, 1.01046945, 6000.69867, 20017.9144,  103560653),
            'NSF2':      (1.47343127, 0.163681849, 1.36920899, 10901.9098, 58568.3687,  127404933),
            'NBKA4':      (1.28834642, 0.132817724, 0.945395373, 7799.80626, 31563.1177,  105965875),
            'SF5':      (1.46141885, 0.247713019, 0.949995832, 11182.6126, 50859.4669,  112041888),
            'DLAK6':      (1.79674556, 0.00384614025, 1.6647332, 10953.7412, 78018.5022,  131153263),
            'B270':      (1.05963142, 0.229442956, 1.10647397, 3520.36549, 32098.963,  95281358),
            'NBAF10':      (1.5851495, 0.143559385, 1.08521269, 9266.81282, 42448.9805,  105613573),
            'NSF10':      (1.62153902, 0.256287842, 1.64447552, 12224.1457, 59573.6775,  147468793),
            'NSF11':      (1.73759695, 0.313747346, 1.89878101, 13188.707, 62306.8142,  155236290),
            'silica glass':      (1.0007668, 0.102419414, 3.0344236, 8391.82477, 8277.39389,  312601508),
            'NSF6HT':      (1.77931763, 0.338149866, 2.08734474, 13371.4182, 61753.3621,  174017590),
            'Polycarbonate':     (1.4182, 0, 0, 21304, 0, 0),
            # 'Flint glass':       (0, 0, 0, 0, 0, 0),
            # 'Sapphire':          (0, 0, 0, 0, 0, 0),
            # 'Cubic zirconia':    (0, 0, 0, 0, 0, 0),
            # 'Diamond':           (0, 0, 0, 0, 0, 0),
        }

def refraction_index_from_sellmeier(wavelength, sellmeier):
    b1, b2, b3, c1, c2, c3 = sellmeier
    l = wavelength
    n = math.sqrt(1 + b1*l**2/(l**2 - c1) + b2*l**2/(l**2 - c2) + b3*l**2/(l**2 - c3))
    return n
    
                
class OpticalMirror():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''  
      
    def Activated(self):
        selection = Gui.Selection.getSelectionEx()
        Gui.doCommand('import OpticsWorkbench')
        Gui.doCommand('objects = []')
        for sel in selection:
            Gui.doCommand('objects.append(FreeCAD.ActiveDocument.getObject("%s"))'%(sel.ObjectName))
            
        Gui.doCommand('OpticsWorkbench.makeMirror(objects)')              

    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if FreeCAD.ActiveDocument:
            return(True)
        else:
            return(False)
        
    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'mirror.svg'),
                'Accel' : '', # a default shortcut (optional)
                'MenuText': 'Optical Mirror',
                'ToolTip' : 'Declare your FreeCAD objects to be optical mirrors' }


class OpticalAbsorber():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''  
      
    def Activated(self):
        selection = Gui.Selection.getSelectionEx()
        Gui.doCommand('import OpticsWorkbench')
        Gui.doCommand('objects = []')
        for sel in selection:
            Gui.doCommand('objects.append(FreeCAD.ActiveDocument.getObject("%s"))'%(sel.ObjectName))
                
        Gui.doCommand('OpticsWorkbench.makeAbsorber(objects)')               

    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if FreeCAD.ActiveDocument:
            return(True)
        else:
            return(False)
        
    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'absorber.svg'),
                'Accel' : '', # a default shortcut (optional)
                'MenuText': 'Optical Absorber',
                'ToolTip' : 'Declare your FreeCAD objects to be optical absorbers' }
                
class OpticalLens():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''  
      
    def Activated(self):
        selection = Gui.Selection.getSelectionEx()
        Gui.doCommand('import OpticsWorkbench')
        Gui.doCommand('objects = []')
        for sel in selection:
            Gui.doCommand('objects.append(FreeCAD.ActiveDocument.getObject("%s"))'%(sel.ObjectName))
                
        Gui.doCommand('OpticsWorkbench.makeLens(objects, material="Quartz")')               

    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if FreeCAD.ActiveDocument:
            return(True)
        else:
            return(False)
        
    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'lens.svg'),
                'Accel' : '', # a default shortcut (optional)
                'MenuText': 'Optical Lens',
                'ToolTip' : 'Declare your FreeCAD objects to be optical lenses' } 

class OpticalGrating():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''  
      
    def Activated(self):
        selection = Gui.Selection.getSelectionEx()
        Gui.doCommand('import OpticsWorkbench')
        Gui.doCommand('objects = []')
        for sel in selection:
            Gui.doCommand('objects.append(FreeCAD.ActiveDocument.getObject("%s"))'%(sel.ObjectName))
            
        Gui.doCommand('OpticsWorkbench.makeGrating(objects)')              

    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if FreeCAD.ActiveDocument:
            return(True)
        else:
            return(False)
        
    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'grating.svg'),
                'Accel' : '', # a default shortcut (optional)
                'MenuText': 'Diffraction grating',
                'ToolTip' : 'Declare your FreeCAD objects to be diffraction gratings' }               

class OpticalEmitter():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''  
      
    def Activated(self):
        selection = Gui.Selection.getSelectionEx()
        Gui.doCommand('import OpticsWorkbench')
        Gui.doCommand('objects = []')
        for sel in selection:
            Gui.doCommand('objects.append(FreeCAD.ActiveDocument.getObject("%s"))'%(sel.ObjectName))
                
        Gui.doCommand('OpticsWorkbench.makeEmitter(objects)')               

    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if FreeCAD.ActiveDocument:
            return(True)
        else:
            return(False)
        
    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'emitter.svg'),
                'Accel' : '', # a default shortcut (optional)
                'MenuText': 'Optical Emitter',
                'ToolTip' : 'Declare your FreeCAD objects to be optical emitters' }  
                             
Gui.addCommand('Emitter', OpticalEmitter())             
Gui.addCommand('Mirror', OpticalMirror())
Gui.addCommand('Absorber', OpticalAbsorber())
Gui.addCommand('Lens', OpticalLens())
Gui.addCommand('Grating', OpticalGrating())
