# -*- coding: utf-8 -*-

__title__ = 'SunRay'
__author__ = 'Christian Bergmann'
__license__ = 'LGPL 3.0'

import os
import FreeCADGui as Gui
import FreeCAD
translate = FreeCAD.Qt.translate

def QT_TRANSLATE_NOOP(context, text):
    return text

_icondir_ = os.path.join(os.path.dirname(__file__), 'icons')
__doc__ = translate('SunRay', 'Declare your FreeCAD objects to be optical mirrors, lenses or absorbers')
    
class SunRayWorker:
    def __init__(self, 
                 fp,    # an instance of Part::FeaturePython
                 rays = []):
        fp.addProperty('App::PropertyLinkList',  'Rays',   'SunRay', 
                        translate('SunRay', 'Create rays of different wavelength')).Rays = rays   
        fp.Proxy = self
        self.update = True
    
    def execute(self, fp):
        if not self.update: return
        self.update = False
        self.displace(fp)
        self.update = True
        
    def onChanged(self, fp, prop):
        proplist = ['Rays']
        if prop in proplist:
            self.execute(fp)
        
    def displace(self, fp):
        for ray in fp.Rays:
            if ray.Placement != fp.Placement:
                ray.Placement = fp.Placement


class SunRayViewProvider:
    def __init__(self, vobj):
        '''Set this object to the proxy object of the actual view provider'''
        vobj.Proxy = self
        self.Object = vobj.Object
            
    def getIcon(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''        
        return os.path.join(_icondir_, 'raysun.svg')

    def attach(self, vobj):
        '''Setup the scene sub-graph of the view provider, this method is mandatory'''
        self.Object = vobj.Object
        self.onChanged(vobj, '')
 
    def updateData(self, fp, prop):
        '''If a property of the handled feature has changed we have the chance to handle this here'''
        pass
    
    def claimChildren(self):
        '''Return a list of objects that will be modified by this feature'''
        return self.Object.Rays
        
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


                
class RaySun():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''  
      
    def Activated(self):
        Gui.doCommand('import OpticsWorkbench')  
        Gui.doCommand('OpticsWorkbench.makeSunRay()')              

    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if FreeCAD.ActiveDocument:
            return(True)
        else:
            return(False)
        
    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'raysun.svg'),
                'Accel' : '', # a default shortcut (optional)
                'MenuText': QT_TRANSLATE_NOOP('SunRay', 'Ray (sun light)'),
                'ToolTip' : QT_TRANSLATE_NOOP('SunRay', 'Declare your FreeCAD objects to be optical mirrors') }

      
Gui.addCommand('Sun Ray', RaySun())
