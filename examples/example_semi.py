from FreeCAD import Vector, Placement, Rotation
import Sketcher
import Part
import FreeCAD as App
import FreeCADGui as Gui
import OpticsWorkbench
import os
from PySide.QtCore import QT_TRANSLATE_NOOP

_icondir_ = os.path.join(os.path.dirname(__file__), '..')
_exname_ = QT_TRANSLATE_NOOP('ExampleSemi', 'Example - Semi transparent')

def createSketch_Sketch(doc):
    Sketch = doc.addObject('Sketcher::SketchObject', 'Sketch')
    geo0 = Sketch.addGeometry(Part.LineSegment(Vector (17.57187, 4.200229, 0.0), Vector (3.394269999999999, -5.662041000000004, 0.0)))
    Sketch.AttacherEngine = 'Engine Plane'
    return Sketch

def createSketch_Sketch002(doc):
    Sketch002 = doc.addObject('Sketcher::SketchObject', 'Sketch002')
    geo0 = Sketch002.addGeometry(Part.LineSegment(Vector (35.877303000000005, 5.425019999999973, 0.0), Vector (49.675442217789794, -5.392686170185302, 0.0)))
    geo1 = Sketch002.addGeometry(Part.ArcOfCircle(Part.Circle(Vector(36.78444246898194, -7.626625831826473, 0.0), Vector (0.0, 0.0, 1.0), 13.083132688145355), 0.1715903905166062, 1.640188568091698))
    Sketch002.addConstraint(Sketcher.Constraint('Coincident', geo1, 2, geo0, 1))
    Sketch002.addConstraint(Sketcher.Constraint('Coincident', geo1, 1, geo0, 2))
    Sketch002.AttacherEngine = 'Engine Plane'
    return Sketch002

def createSketch_Sketch003(doc):
    Sketch003 = doc.addObject('Sketcher::SketchObject', 'Sketch003')
    geo0 = Sketch003.addGeometry(Part.LineSegment(Vector (-5.804982, 35.19952, 0.0), Vector (-5.804982, -28.56389, 0.0)))
    geo1 = Sketch003.addGeometry(Part.LineSegment(Vector (-5.804982, -28.56389, 0.0), Vector (72.434807, -28.56389, 0.0)))
    geo2 = Sketch003.addGeometry(Part.LineSegment(Vector (72.434807, -28.56389, 0.0), Vector (72.434807, 35.19952, 0.0)))
    geo3 = Sketch003.addGeometry(Part.LineSegment(Vector (72.434807, 35.19952, 0.0), Vector (-5.804981999999995, 35.19952, 0.0)))
    Sketch003.addConstraint(Sketcher.Constraint('Coincident', geo0, 2, geo1, 1))
    Sketch003.addConstraint(Sketcher.Constraint('Coincident', geo1, 2, geo2, 1))
    Sketch003.addConstraint(Sketcher.Constraint('Coincident', geo2, 2, geo3, 1))
    Sketch003.addConstraint(Sketcher.Constraint('Coincident', geo3, 2, geo0, 1))
    Sketch003.addConstraint(Sketcher.Constraint('Vertical', geo0))
    Sketch003.addConstraint(Sketcher.Constraint('Vertical', geo2))
    Sketch003.addConstraint(Sketcher.Constraint('Horizontal', geo1))
    Sketch003.addConstraint(Sketcher.Constraint('Horizontal', geo3))
    Sketch003.AttacherEngine = 'Engine Plane'
    Sketch003.ViewObject.LineColor = (0.0, 0.0, 0.0, 0.0)
    Sketch003.ViewObject.LineColorArray = [(0.0, 0.0, 0.0, 0.0)]
    return Sketch003


def make_semi():
    App.newDocument(_exname_)
    doc = App.activeDocument()

    Sketch = createSketch_Sketch(doc)
    Mirror_semi40 = OpticsWorkbench.makeMirror([Sketch], True, 40)
    Mirror_semi40.Label = "Mirror_semi40"

    Cube = doc.addObject('Part::Box', 'Cube')
    Cube.Height = 2.0
    Cube.Length = 2.0
    Cube.Placement = Placement(Vector(27.0, -5.0, -1.0), Rotation (0.0, 0.0, 0.0, 1.0))
    Cube.ViewObject.Transparency = 50
    Absorber_semi50 = OpticsWorkbench.makeAbsorber([Cube], True, 50)
    Absorber_semi50.Label = "Absorber_semi50"

    Sketch002 = createSketch_Sketch002(doc)
    Lens_semi80 = OpticsWorkbench.makeLens([Sketch002], material='NBK7/Window glass', collectStatistics=True, transparency=80)
    Lens_semi80.Label = "Lens_semi80"

    Sketch003 = createSketch_Sketch003(doc)
    FullAbsorber = OpticsWorkbench.makeAbsorber([Sketch003], True, 0)
    FullAbsorber.Label = "FullAbsorber"

    doc.recompute()
    OpticsWorkbench.makeRay(beamNrColumns=3, beamDistance = 0.2)
    doc.recompute()
    OpticsWorkbench.Hits2CSV()
    doc.recompute()
    Gui.ActiveDocument=doc


class ExampleSemi():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''

    def Activated(self):
        make_semi()
        Gui.runCommand('Std_OrthographicCamera',1)
        Gui.SendMsgToActiveView("ViewFit")

    def IsActive(self):
        return(True)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'optics_workbench_icon.svg'),
                'Accel' : "", # a default shortcut (optional)
                'MenuText': _exname_,
                'ToolTip' : '' }

Gui.addCommand('ExampleSemi', ExampleSemi())