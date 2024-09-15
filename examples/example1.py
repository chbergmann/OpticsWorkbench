from FreeCAD import Vector
import Sketcher
import Part
import FreeCAD as App
import FreeCADGui as Gui
import OpticsWorkbench
import os
from PySide.QtCore import QT_TRANSLATE_NOOP

_icondir_ = os.path.join(os.path.dirname(__file__), '..')

def createSketch_Sketch_Mirror1(doc):
    Sketch_Mirror1 = doc.addObject('Sketcher::SketchObject', 'Sketch_Mirror1')
    Sketch_Mirror1.addGeometry(Part.LineSegment(Vector (11.836481, 6.837696, 0.0), Vector (15.17516, -0.6152189999999997, 0.0)))
    Sketch_Mirror1.addGeometry(Part.Circle(Vector(0.00, -5.56, 0.00), Vector (0.0, 0.0, 1.0), 1.00))
    Sketch_Mirror1.toggleConstruction(1)
    Sketch_Mirror1.addGeometry(Part.Circle(Vector(0.00, -15.18, 0.00), Vector (0.0, 0.0, 1.0), 1.00))
    Sketch_Mirror1.toggleConstruction(2)
    Sketch_Mirror1.addGeometry(Part.Circle(Vector(7.19, -16.35, 0.00), Vector (0.0, 0.0, 1.0), 1.00))
    Sketch_Mirror1.toggleConstruction(3)
    Sketch_Mirror1.addGeometry(Part.BSplineCurve([Vector(0.00, -5.56, 0.00), Vector(0.00, -15.18, 0.00), Vector(7.19, -16.35, 0.00)]))
    Sketch_Mirror1.addGeometry(Part.Point(Vector(0.00, -5.56, 0.00)))
    Sketch_Mirror1.addConstraint(Sketcher.Constraint('PointOnObject', 4, 1, -2))
    Sketch_Mirror1.addConstraint(Sketcher.Constraint('Equal', 1, 2))
    Sketch_Mirror1.addConstraint(Sketcher.Constraint('PointOnObject', 2, 3, -2))
    Sketch_Mirror1.addConstraint(Sketcher.Constraint('Equal', 1, 3))
    Sketch_Mirror1.addConstraint(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint', 1, 3, 4, 0))
    Sketch_Mirror1.addConstraint(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint', 2, 3, 4, 1))
    Sketch_Mirror1.addConstraint(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint', 3, 3, 4, 2))
    return Sketch_Mirror1

def createSketch_Sketch_Box(doc):
    Sketch_Box = doc.addObject('Sketcher::SketchObject', 'Sketch_Box')
    Sketch_Box.addGeometry(Part.LineSegment(Vector (-0.14878900000000073, 11.406045000000002, 0.0), Vector (40.936604, 11.406045000000002, 0.0)))
    Sketch_Box.addGeometry(Part.LineSegment(Vector (40.936604, 11.406045000000002, 0.0), Vector (40.936604, -21.699192, 0.0)))
    Sketch_Box.addGeometry(Part.LineSegment(Vector (40.936604, -21.699192, 0.0), Vector (-0.14878900000000073, -21.699192, 0.0)))
    Sketch_Box.addGeometry(Part.LineSegment(Vector (-0.14878900000000073, -21.699192, 0.0), Vector (-0.14878900000000073, 11.406045000000002, 0.0)))
    Sketch_Box.addConstraint(Sketcher.Constraint('Coincident', 0, 2, 1, 1))
    Sketch_Box.addConstraint(Sketcher.Constraint('Coincident', 1, 2, 2, 1))
    Sketch_Box.addConstraint(Sketcher.Constraint('Coincident', 2, 2, 3, 1))
    Sketch_Box.addConstraint(Sketcher.Constraint('Coincident', 3, 2, 0, 1))
    Sketch_Box.addConstraint(Sketcher.Constraint('Horizontal', 0))
    Sketch_Box.addConstraint(Sketcher.Constraint('Horizontal', 2))
    Sketch_Box.addConstraint(Sketcher.Constraint('Vertical', 1))
    Sketch_Box.addConstraint(Sketcher.Constraint('Vertical', 3))
    Sketch_Box.ViewObject.DiffuseColor = [(0.00, 0.00, 0.00, 0.00)]
    Sketch_Box.ViewObject.LineColor = (0.00, 0.00, 0.00, 0.00)
    Sketch_Box.ViewObject.LineColorArray = [(0.00, 0.00, 0.00, 0.00)]
    Sketch_Box.ViewObject.PointColor = (0.00, 0.00, 0.00, 0.00)
    Sketch_Box.ViewObject.PointColorArray = [(0.00, 0.00, 0.00, 0.00)]
    Sketch_Box.ViewObject.ShapeColor = (0.00, 0.00, 0.00, 0.00)
    return Sketch_Box

def createSketch_Sketch_Mirror2(doc):
    Sketch_Mirror2 = doc.addObject('Sketcher::SketchObject', 'Sketch_Mirror2')
    Sketch_Mirror2.addGeometry(Part.ArcOfCircle(Part.Circle(Vector(56.12, -5.69, 0.00), Vector (0.0, 0.0, 1.0), 10.64), 0.6054907273817108, 6.799308361137584))
    return Sketch_Mirror2

def createSketch_Sketch_Lens(doc):
    Sketch_Lens = doc.addObject('Sketcher::SketchObject', 'Sketch_Lens')
    Sketch_Lens.addGeometry(Part.LineSegment(Vector (11.566624790355402, -6.79, 0.0), Vector (11.566624790355402, -16.79, 0.0)))
    Sketch_Lens.addGeometry(Part.ArcOfCircle(Part.Circle(Vector(8.25, -11.79, 0.00), Vector (0.0, 0.0, 1.0), 6.00), 5.298074523841841, 7.268296090517332))
    Sketch_Lens.addConstraint(Sketcher.Constraint('Vertical', 0))
    Sketch_Lens.addConstraint(Sketcher.Constraint('Coincident', 1, 1, 0, 2))
    Sketch_Lens.addConstraint(Sketcher.Constraint('Coincident', 1, 2, 0, 1))
    Sketch_Lens.addConstraint(Sketcher.Constraint('Radius', 1, 6.00))
    Sketch_Lens.addConstraint(Sketcher.Constraint('DistanceY', 0, 2, 0, 1, 10.00))
    return Sketch_Lens

def createSketch_Sketch_Prism(doc):
    Sketch_Prism = doc.addObject('Sketcher::SketchObject', 'Sketch_Prism')
    Sketch_Prism.addGeometry(Part.LineSegment(Vector (21.126467, -13.53020124766231, 0.0), Vector (21.126467, -21.018505, 0.0)))
    Sketch_Prism.addGeometry(Part.LineSegment(Vector (21.126467, -21.018505, 0.0), Vector (31.579980991773073, -17.27435312383116, 0.0)))
    Sketch_Prism.addGeometry(Part.LineSegment(Vector (31.579980991773073, -17.27435312383116, 0.0), Vector (21.126467, -13.53020124766231, 0.0)))
    Sketch_Prism.addConstraint(Sketcher.Constraint('Vertical', 0))
    Sketch_Prism.addConstraint(Sketcher.Constraint('Coincident', 0, 2, 1, 1))
    Sketch_Prism.addConstraint(Sketcher.Constraint('Coincident', 1, 2, 2, 1))
    Sketch_Prism.addConstraint(Sketcher.Constraint('Coincident', 2, 2, 0, 1))
    Sketch_Prism.addConstraint(Sketcher.Constraint('Equal', 1, 2))
    return Sketch_Prism

def make_optics():
    App.newDocument("Example 2D")
    doc = App.activeDocument()

    Sketch_Mirror1 = createSketch_Sketch_Mirror1(doc)
    Sketch_Box = createSketch_Sketch_Box(doc)
    Sketch_Mirror2 = createSketch_Sketch_Mirror2(doc)
    Sketch_Lens = createSketch_Sketch_Lens(doc)
    Sketch_Prism = createSketch_Sketch_Prism(doc)

    OpticsWorkbench.makeMirror([Sketch_Mirror1, Sketch_Mirror2])
    OpticsWorkbench.makeAbsorber([Sketch_Box], True)
    OpticsWorkbench.makeLens([Sketch_Lens, Sketch_Prism], material='NBK7/Window glass')
    
    doc.recompute()
    OpticsWorkbench.makeRay(Vector(75.00, 0.00, 0.00), Vector(-1,0,0))
    OpticsWorkbench.makeRay(beamNrColumns=50)

    doc.recompute()

class Example1():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''

    def Activated(self):
        make_optics()
        Gui.activeDocument().activeView().viewTop()

    def IsActive(self):
        return(True)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'optics_workbench_icon.svg'),
                'Accel' : "", # a default shortcut (optional)
                'MenuText': QT_TRANSLATE_NOOP('Workbench', 'Example - 2D'),
                'ToolTip' : '' }

Gui.addCommand('Example2D', Example1())
