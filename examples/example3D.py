import FreeCAD as App
import FreeCADGui as Gui
import os
from FreeCAD import Vector, Placement, Rotation
import FreeCAD as app
import OpticsWorkbench
from PySide.QtCore import QT_TRANSLATE_NOOP

_icondir_ = os.path.join(os.path.dirname(__file__), '..')

def make_Test3D():
    App.newDocument("Example 3D")
    doc = app.activeDocument()

    Cube = doc.addObject('Part::Box', 'Cube')
    Cube.Placement = Placement(Vector(20.00, -3.17, -2.00), Rotation (-0.0, -0.0, 0.25881904510252074, 0.9659258262890684))

    Sphere = doc.addObject('Part::Sphere', 'Sphere')
    Sphere.Placement = Placement(Vector(3.00, -19.00, 0.00), Rotation (0.0, 0.0, 0.0, 1.0))

    Cone = doc.addObject('Part::Cone', 'Cone')
    Cone.Placement = Placement(Vector(68.90, -46.50, -2.30), Rotation (0.0, 0.0, 0.0, 1.0))

    Cylinder = doc.addObject('Part::Cylinder', 'Cylinder')
    Cylinder.Height = 50.0
    Cylinder.Placement = Placement(Vector(40.00, -26.00, -19.00), Rotation (0.0, 0.0, 0.0, 1.0))
    Cylinder.Radius = 50.0
    Cylinder.ViewObject.Transparency = 90

    Sphere001 = doc.addObject('Part::Sphere', 'Sphere001')
    Sphere001.Radius = 20.0
    Sphere001.Visibility = False
    Sphere001.ViewObject.Visibility = False

    Cube002 = doc.addObject('Part::Box', 'Cube002')
    Cube002.Height = 40.0
    Cube002.Length = 40.0
    Cube002.Placement = Placement(Vector(-20.00, -25.00, -20.00), Rotation (0.0, 0.0, 0.0, 1.0))
    Cube002.Visibility = False
    Cube002.Width = 40.0
    Cube002.ViewObject.Visibility = False

    HalfSphere = doc.addObject('Part::Cut', 'HalfSphere')
    HalfSphere.Base = Sphere001
    HalfSphere.Placement = Placement(Vector(25.86, -24.61, 0.00), Rotation (0.0, 0.0, -0.793353340291235, 0.6087614290087205))
    HalfSphere.Tool = Cube002
    HalfSphere.ViewObject.DiffuseColor = [(0.80, 0.80, 0.80, 0.00), (0.80, 0.80, 0.80, 0.00)]
    HalfSphere.ViewObject.Transparency = 75

    doc.recompute()

    OpticsWorkbench.makeMirror([Cube, Sphere, Cone], True)
    OpticsWorkbench.makeAbsorber([Cylinder])
    OpticsWorkbench.makeLens([HalfSphere])

    doc.recompute()
    OpticsWorkbench.makeRay(beamNrColumns=20, beamNrRows=10, beamDistance=0.05)

    doc.recompute()


class Example3D():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''

    def Activated(self):
        make_Test3D()

    def IsActive(self):
        return(True)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'optics_workbench_icon.svg'),
                'Accel' : "", # a default shortcut (optional)
                'MenuText': QT_TRANSLATE_NOOP('Workbench', 'Example - 3D'),
                'ToolTip' : '' }

Gui.addCommand('Example3D', Example3D())
