import numpy as np
import matplotlib.pyplot as plt
import FreeCADGui as Gui
from FreeCAD import activeDocument
import os
import Ray
from scipy.stats import gaussian_kde

from PySide.QtCore import QT_TRANSLATE_NOOP

_icondir_ = os.path.join(os.path.dirname(__file__), 'icons')
        
class PlotRayHits():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''
    def plot3D(selectedObjList, showEnergy):
        
        # Figure out the selected absorber; if multiple absorbers selected, or multiple objects then loop through them all
        # and accumulate data from all of them
    
        attr1_names=[]
        attr2_names=[]
        coords_per_beam = []
        energy_attrs = []
        for eachObject in selectedObjList:
            #print("Looping through: ", eachObject.Label)
            try:
                if Ray.isOpticalObject(eachObject):
                    #coords = []
                    attr1_names[len(attr1_names):] = [attr for attr in dir(eachObject) if attr.startswith('HitCoordsFrom')]
                    attr2_names[len(attr2_names):] = [attr for attr in dir(eachObject) if attr.startswith('EnergyFrom')]
                    coords_per_beam[len(coords_per_beam):] = [getattr(eachObject, attr) for attr in attr1_names]
                    energy_attrs[len(energy_attrs):] = [getattr(eachObject, attr) for attr in attr2_names]
                    
                    #all_coords = np.array([coord for coords in coords_per_beam for coord in coords])
                else:
                    print ("Ignoring: ",eachObject.Label)
            except:
                print ("Ignoring: ",eachObject.Label)

        all_coords = np.array([coord for coords in coords_per_beam for coord in coords])    
        all_energies = np.array([energy for energies in energy_attrs for energy in energies])  
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
        else:
            print("No ray hits were found")
            return

        if showEnergy:
            if not xpresent:
                x = all_coords[:,2]
            elif not ypresent:
                y = all_coords[:,2]

            # Berechnung der gewichteten Dichte
            # 'weights' sorgt dafür, dass ein Strahl mit 200W doppelt so stark 
            # gewichtet wird wie einer mit 100W.
            nbins = 300    
            bw = 7.
            kde = gaussian_kde([x, y], bw_method=bw / 30., weights=all_energies)

            # Grid für die Darstellung erstellen
            xi, yi = np.mgrid[x.min():x.max():nbins*1j, y.min():y.max():nbins*1j]
            zi = kde(np.vstack([xi.flatten(), yi.flatten()]))

            # Skalierung auf Prozent:
            # Wir normieren zi so, dass die Summe über die Fläche der Gesamtenergie entspricht
            zi_percent = (zi.reshape(xi.shape) / np.sum(zi)) * 100

            # Visualisierung
            plt.figure(figsize=(10, 7))
            mesh = plt.pcolormesh(xi, yi, zi_percent, shading='auto', cmap='magma')
            cbar = plt.colorbar(mesh)
            cbar.set_label('Energy per area [%]')

            if not zpresent:
                plt.xlabel('X-Position [mm]')
                plt.ylabel('Y-Position [mm]')
            elif not ypresent:
                plt.xlabel('X-Position [mm]')
                plt.ylabel('Z-Position [mm]')
            else:
                plt.xlabel('Y-Position [mm]')
                plt.ylabel('Z-Position [mm]')
            plt.title(f'Energy Density')
            plt.show()
        else:
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
                    y = all_coords[:,2]
                else:
                    ax.scatter(y, z)
                    ax.set_xlabel('Y-axis')
                    ax.set_ylabel('Z-axis')
                    x = all_coords[:,2]
            plt.show()
            
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

class PlotEnergyDensity():               
    def Activated(self):
        '''Will be called when the feature is executed.'''
        # Generate commands in the FreeCAD python console to plot ray hits for selected absorber
        Gui.doCommand('import OpticsWorkbench')
        Gui.doCommand('selectedObjList = FreeCADGui.Selection.getSelection()')
        Gui.doCommand('OpticsWorkbench.drawEnergyDensity(selectedObjList)')


    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if activeDocument():    
            return(True)
        else:
            return(False)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'scatterEn.svg'),
                'Accel' : '', # a default shortcut (optional)
                'MenuText': QT_TRANSLATE_NOOP('RayHits', 'Energy Density Plot'),
                'ToolTip' : QT_TRANSLATE_NOOP('RayHits', 'Show selected absorbers ray energy density in a 2D plot') }
    

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
Gui.addCommand('EnergyDensity', PlotEnergyDensity())
                