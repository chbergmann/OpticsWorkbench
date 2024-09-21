import numpy as np
import matplotlib.pyplot as plt
import FreeCADGui as Gui
from FreeCAD import activeDocument
import os
import Ray

from PySide.QtCore import QT_TRANSLATE_NOOP

_icondir_ = os.path.join(os.path.dirname(__file__), 'icons')
        
class PlotRayHits():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''
    def plot3D(selectedObjList):
        
        # Figure out the selected absorber; if multiple absorbers selected, or multiple objects then loop through them all
        # and accumulate data from all of them
    
        #print("Selected Objects: ", len(selectedObjList))
        if len(selectedObjList) >0:
            coords = []
            attr_names=[]
            coords_per_beam = []
            for eachObject in selectedObjList:
                #print("Looping through: ", eachObject.Label)
                try:
                    if Ray.isOpticalObject(eachObject):
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
                
                startx = x[0]
                starty = y[0]
                startz = z[0]
                xpresent = False
                ypresent = False
                zpresent = False
                for co in all_coords:
                    if abs(startx - co[0]) > Ray.EPSILON: xpresent = True
                    if abs(starty - co[1]) > Ray.EPSILON: ypresent = True
                    if abs(startz - co[2]) > Ray.EPSILON: zpresent = True
            
                fig = plt.figure()
                
                if xpresent and ypresent and zpresent:  
                    ax = fig.add_subplot(projection='3d')
                    ax.scatter(x, y, z)
                    ax.set_xlabel('X-axis')
                    ax.set_ylabel('Y-axis')
                    ax.set_zlabel('Z-axis')
                else:
                    ax = fig.add_subplot()
                    if not zpresent:
                        ax.scatter(x, y) 
                        ax.set_xlabel('X-axis')
                        ax.set_ylabel('Y-axis')
                    elif not ypresent:
                        ax.scatter(x, z)
                        ax.set_xlabel('X-axis')
                        ax.set_ylabel('Z-axis')
                    else:
                        ax.scatter(y, z)
                        ax.set_xlabel('Y-axis')
                        ax.set_ylabel('Z-axis')
    
                plt.show()
            else:
                print("No ray hits were found")
            
    def Activated(self):
        '''Will be called when the feature is executed.'''
        # Generate commands in the FreeCAD python console to plot ray hits for selected absorber
        Gui.doCommand('import OpticsWorkbench')
        Gui.doCommand('selectedObjList = FreeCADGui.Selection.getSelection()')
        Gui.doCommand('OpticsWorkbench.drawPlot(selectedObjList)')


    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if activeDocument():    
            return(True)
        else:
            return(False)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'scatter3D.svg'),
                'Accel' : '', # a default shortcut (optional)
                'MenuText': QT_TRANSLATE_NOOP('RayHits', '2D/3D Plot'),
                'ToolTip' : QT_TRANSLATE_NOOP('RayHits', 'Show selected absorbers ray hits in scatter plot') }
                

class RayHits2CSV():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''

    def Activated(self):
        '''Will be called when the feature is executed.'''
        # Generate commands in the FreeCAD python console to plot ray hits for selected absorber
        Gui.doCommand('import OpticsWorkbench')
        Gui.doCommand('OpticsWorkbench.Hits2CSV()')


    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if activeDocument():    
            return(True)
        else:
            return(False)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'ExportCSV.svg'),
                'Accel' : '', # a default shortcut (optional)
                'MenuText': QT_TRANSLATE_NOOP('Hits2CSV', 'Ray Hits to Spreadsheet'),
                'ToolTip' : QT_TRANSLATE_NOOP('Hits2CSV', 'Export Ray Hits to Spreadsheet') }
                

Gui.addCommand('RayHits', PlotRayHits())
Gui.addCommand('Hits2CSV', RayHits2CSV())
                