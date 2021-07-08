from FreeCAD import Vector, Placement, Rotation
import FreeCAD as App
import FreeCADGui as Gui
import OpticsWorkbench
import os

_icondir_ = os.path.join(os.path.dirname(__file__), '..', 'icons')

def make_Test3D():
    doc = App.activeDocument()

    Cube = doc.addObject('Part::Box', 'Cube')
    Cube.Placement = Placement(Vector(20.00, -6.00, -2.00), Rotation (0.0, 0.0, 0.13052619222005157, 0.9914448613738104))

    Cylinder = doc.addObject('Part::Cylinder', 'Cylinder')
    Cylinder.Placement = Placement(Vector(-18.00, -22.00, -4.00), Rotation (0.0, 0.0, 0.0, 1.0))

    Sphere = doc.addObject('Part::Sphere', 'Sphere')
    Sphere.Placement = Placement(Vector(-16.00, 0.00, -2.00), Rotation (0.0, 0.0, 0.0, 1.0))

    Cone = doc.addObject('Part::Cone', 'Cone')
    Cone.Placement = Placement(Vector(26.00, -23.00, 28.00), Rotation (0.0, 0.0, 0.0, 1.0))

    Torus = doc.addObject('Part::Torus', 'Torus')
    Torus.Placement = Placement(Vector(-44.00, -29.00, -1.50), Rotation (0.0, 0.0, 0.0, 1.0))

    Cylinder001 = doc.addObject('Part::Cylinder', 'Cylinder001')
    Cylinder001.Radius = 5.0
    Cylinder001.Visibility = False
    Cylinder001.ViewObject.Visibility = False

    Cylinder002 = doc.addObject('Part::Cylinder', 'Cylinder002')
    Cylinder002.Radius = 4.0
    Cylinder002.Visibility = False
    Cylinder002.ViewObject.Visibility = False

    Tube = doc.addObject('Part::Cut', 'Tube')
    Tube.Base = Cylinder001
    Tube.Placement = Placement(Vector(0.00, -3.00, 41.00), Rotation (0.0, 0.0, 0.0, 1.0))
    Tube.Tool = Cylinder002
    Tube.ViewObject.DiffuseColor = [(0.80, 0.80, 0.80, 0.00), (0.80, 0.80, 0.80, 0.00), (0.80, 0.80, 0.80, 0.00), (0.80, 0.80, 0.80, 0.00)]
    Tube.ViewObject.Transparency = 70
    
    OpticsWorkbench.makeMirror([Cube, Cylinder, Sphere, Cone, Torus, Tube])
    
    Cube001 = doc.addObject('Part::Box', 'Cube001')
    Cube001.Height = 100.0
    Cube001.Length = 200.0
    Cube001.Placement = Placement(Vector(-122.0, -100.0, -10.00), Rotation (0.0, 0.0, 0.0, 1.0))
    Cube001.Width = 200.0
    Cube001.ViewObject.Transparency = 80
     
    OpticsWorkbench.makeAbsorber([Cube001])
    
    doc.recompute()
    OpticsWorkbench.makeRay(beamNrColumns=30)
    
    doc.recompute()


class Example3D():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''  
      
    def Activated(self):
        make_Test3D()           

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        if App.activeDocument():
            return(True)
        else:
            return(False)
        
    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'pyrate_logo_icon.svg'),
                'Accel' : "", # a default shortcut (optional)
                'MenuText': 'Example 3D',
                'ToolTip' : '' }
                
Gui.addCommand('Example3D', Example3D())