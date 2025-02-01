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
    geo0 = Sketch.addGeometry(Part.Circle(Vector(0.00, 12.01, 0.00), Vector (0.0, 0.0, 1.0), 1.00))
    Sketch.toggleConstruction(geo0)
    geo1 = Sketch.addGeometry(Part.Circle(Vector(-1.00, 12.42, 0.00), Vector (0.0, 0.0, 1.0), 1.00))
    Sketch.toggleConstruction(geo1)
    geo2 = Sketch.addGeometry(Part.Circle(Vector(-1.43, 15.03, 0.00), Vector (0.0, 0.0, 1.0), 1.00))
    Sketch.toggleConstruction(geo2)
    geo3 = Sketch.addGeometry(Part.Circle(Vector(-0.15, 15.56, 0.00), Vector (0.0, 0.0, 1.0), 1.00))
    Sketch.toggleConstruction(geo3)
    geo4 = Sketch.addGeometry(Part.Circle(Vector(0.00, 16.62, 0.00), Vector (0.0, 0.0, 1.0), 1.00))
    Sketch.toggleConstruction(geo4)
    geo5 = Sketch.addGeometry(Part.BSplineCurve([Vector(0.00, 12.01, 0.00), Vector(-1.00, 12.42, 0.00), Vector(-1.43, 15.03, 0.00), Vector(-0.15, 15.56, 0.00), Vector(0.00, 16.62, 0.00)]))
    Sketch.addConstraint(Sketcher.Constraint('Weight', geo0, 1.00))
    Sketch.addConstraint(Sketcher.Constraint('PointOnObject', geo5, 1, -2))
    Sketch.addConstraint(Sketcher.Constraint('Equal', geo0, geo1))
    Sketch.addConstraint(Sketcher.Constraint('Equal', geo0, geo2))
    Sketch.addConstraint(Sketcher.Constraint('Equal', geo0, geo3))
    Sketch.addConstraint(Sketcher.Constraint('Equal', geo0, geo4))
    Sketch.addConstraint(Sketcher.Constraint('PointOnObject', geo5, 2, -2))
    Sketch.addConstraint(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint', geo0, 3, geo5, 0))
    Sketch.addConstraint(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint', geo1, 3, geo5, 1))
    Sketch.addConstraint(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint', geo2, 3, geo5, 2))
    Sketch.addConstraint(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint', geo3, 3, geo5, 3))
    Sketch.addConstraint(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint', geo4, 3, geo5, 4))
    Sketch.Placement = Placement(Vector(0.00, 0.00, 0.00), Rotation (0.7071067811865475, 0.0, 0.0, 0.7071067811865476))
    Sketch.Visibility = False
    Sketch.ViewObject.Visibility = False
    return Sketch


def make_candle():
    App.newDocument("Candle Example")
    doc = App.activeDocument()

    Candle1 = doc.addObject('Part::Cylinder', 'Candle1')
    Candle1.Radius = 3.0

    Candle2 = doc.addObject('Part::Cylinder', 'Candle2')
    Candle2.Height = 12.5
    Candle2.Radius = 0.2

    Sketch = createSketch_Sketch(doc)

    Revolve = doc.addObject('Part::Revolution', 'Flame')
    Revolve.Source = Sketch
    Revolve.ViewObject.LineColor = (1.00, 1.00, 1.00, 1.00)
    Revolve.ViewObject.LineColorArray = [(1.00, 1.00, 1.00, 1.00)]
    Revolve.ViewObject.PointColor = (1.00, 1.00, 1.00, 1.00)
    Revolve.ViewObject.PointColorArray = [(1.00, 1.00, 1.00, 1.00)]

    OpticsWorkbench.makeAbsorber([Candle1, Candle2])
    OpticsWorkbench.makeRay(beamNrColumns=10, beamNrRows=10, baseShape=Revolve, maxRayLength=100)
    
    doc.recompute()


class ExampleCandle():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''

    def Activated(self):
        make_candle()
        Gui.activeDocument().activeView().viewIsometric()

    def IsActive(self):
        return(True)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'optics_workbench_icon.svg'),
                'Accel' : "", # a default shortcut (optional)
                'MenuText': QT_TRANSLATE_NOOP('ExampleCandle', 'Example - Candle'),
                'ToolTip' : '' }

Gui.addCommand('ExampleCandle', ExampleCandle())