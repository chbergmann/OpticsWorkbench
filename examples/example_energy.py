from FreeCAD import Vector, Placement, Rotation
import Sketcher
import Part
import FreeCAD as App
import FreeCADGui as Gui
import OpticsWorkbench
import os
from PySide.QtCore import QT_TRANSLATE_NOOP

_icondir_ = os.path.join(os.path.dirname(__file__), '..')

def createSketch_Sketch(doc):
    Sketch = doc.addObject('Sketcher::SketchObject', 'Sketch')
    geo0 = Sketch.addGeometry(Part.LineSegment(Vector (-50.0, 50.0, 0.0), Vector (-50.0, -50.0, 0.0)))
    geo1 = Sketch.addGeometry(Part.LineSegment(Vector (-50.0, -50.0, 0.0), Vector (50.0, -50.0, 0.0)))
    geo2 = Sketch.addGeometry(Part.LineSegment(Vector (50.0, -50.0, 0.0), Vector (50.0, 50.0, 0.0)))
    geo3 = Sketch.addGeometry(Part.LineSegment(Vector (50.0, 50.0, 0.0), Vector (-50.0, 50.0, 0.0)))
    Sketch.addConstraint(Sketcher.Constraint('Coincident', geo0, 2, geo1, 1))
    Sketch.addConstraint(Sketcher.Constraint('Coincident', geo1, 2, geo2, 1))
    Sketch.addConstraint(Sketcher.Constraint('Coincident', geo2, 2, geo3, 1))
    Sketch.addConstraint(Sketcher.Constraint('Coincident', geo3, 2, geo0, 1))
    Sketch.addConstraint(Sketcher.Constraint('Vertical', geo0))
    Sketch.addConstraint(Sketcher.Constraint('Vertical', geo2))
    Sketch.addConstraint(Sketcher.Constraint('Horizontal', geo1))
    Sketch.addConstraint(Sketcher.Constraint('Horizontal', geo3))
    Sketch.addConstraint(Sketcher.Constraint('Distance', geo0, 1, geo2, 2, 100.0))
    Sketch.addConstraint(Sketcher.Constraint('Distance', geo1, 1, geo3, 2, 100.0))
    Sketch.addConstraint(Sketcher.Constraint('DistanceX', -1, 1, geo2, 2, 50.0))
    Sketch.addConstraint(Sketcher.Constraint('DistanceY', geo2, 2, 50.0))
    Sketch.AttacherEngine = 'Engine Plane'
    Sketch.Visibility = False
    Sketch.ViewObject.Deviation = 0.2000000029802322
    Sketch.ViewObject.Visibility = False
    return Sketch


def make_optics1():
    App.newDocument("Energy Density Example")
    doc = App.activeDocument()
 
    Sketch = createSketch_Sketch(doc)
    Extrude = doc.addObject('Part::Extrusion', 'Extrude')
    Extrude.Base = Sketch
    Extrude.DirMode = 'Normal'
    Extrude.LengthFwd = 1.0
    Extrude.Placement = Placement(Vector(0.0, 0.0, 173.5), Rotation (0.0, 0.0, 0.0, 1.0))
    Extrude.Solid = True
    Extrude.ViewObject.Transparency = 50
    absorber1 = OpticsWorkbench.makeAbsorber([Extrude], True)

    Kugel = doc.addObject('Part::Sphere', 'Kugel')
    Kugel.Placement = Placement(Vector(0.0, 0.0, 79.5), Rotation (0.0, 0.0, 0.0, 1.0))
    Kugel.ViewObject.Deviation = 0.2000000029802322
    
    OpticsWorkbench.makeAbsorber([Kugel], False)

    OpticsWorkbench.makeRay(beamDistance = 0.1,
        beamNrColumns = 16,
        beamNrRows = 16,
        coneAngle = 30.0,
        power = True,
        radiationPattern = 'lambertian',
        rayBundleType = 'spherical')

    OpticsWorkbench.drawEnergyDensity([absorber1])
    
    doc.recompute()
    Gui.SendMsgToActiveView("ViewSelection")
    Gui.SendMsgToActiveView("ViewFit")


class ExampleEnergyDensity():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''

    def Activated(self):
        make_optics1()
        Gui.activeDocument().activeView().viewIsometric()

    def IsActive(self):
        return(True)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'optics_workbench_icon.svg'),
                'Accel' : "", # a default shortcut (optional)
                'MenuText': QT_TRANSLATE_NOOP('ExampleEnergyDensity', 'Example - Energy Density'),
                'ToolTip' : '' }

Gui.addCommand('ExampleEnergyDensity', ExampleEnergyDensity())