from FreeCAD import Vector
import Sketcher
import Part
import FreeCAD as App
import FreeCADGui as Gui
import OpticsWorkbench
import os

_icondir_ = os.path.join(os.path.dirname(__file__), '..', 'icons')

def createSketch_Sketch(doc):
    Sketch = doc.addObject('Sketcher::SketchObject', 'Sketch')
    Sketch.addGeometry(Part.LineSegment(Vector (11.836481, 6.837696, 0.0), Vector (15.17516, -0.6152189999999997, 0.0)))
    Sketch.addGeometry(Part.Circle(Vector(0.00, -5.56, 0.00), Vector (0.0, 0.0, 1.0), 1.00))
    Sketch.toggleConstruction(1)
    Sketch.addGeometry(Part.Circle(Vector(0.00, -20.69, 0.00), Vector (0.0, 0.0, 1.0), 1.00))
    Sketch.toggleConstruction(2)
    Sketch.addGeometry(Part.Circle(Vector(20.47, -18.63, 0.00), Vector (0.0, 0.0, 1.0), 1.00))
    Sketch.toggleConstruction(3)
    Sketch.addGeometry(Part.BSplineCurve([Vector(0.00, -5.56, 0.00), Vector(0.00, -20.69, 0.00), Vector(20.47, -18.63, 0.00)]))
    Sketch.addGeometry(Part.Point(Vector(0.00, -5.56, 0.00)))
    Sketch.toggleConstruction(5)
    Sketch.addGeometry(Part.Point(Vector(20.47, -18.63, 0.00)))
    Sketch.toggleConstruction(6)
    Sketch.addConstraint(Sketcher.Constraint('PointOnObject', 4, 1, -2))
    Sketch.addConstraint(Sketcher.Constraint('Equal', 1, 2))
    Sketch.addConstraint(Sketcher.Constraint('PointOnObject', 2, 3, -2))
    Sketch.addConstraint(Sketcher.Constraint('Equal', 1, 3))
    Sketch.addConstraint(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint', 1, 3, 4, 0))
    Sketch.addConstraint(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint', 2, 3, 4, 1))
    Sketch.addConstraint(Sketcher.Constraint('InternalAlignment:Sketcher::BSplineControlPoint', 3, 3, 4, 2))
    return Sketch

def createSketch_Sketch001(doc):
    Sketch001 = doc.addObject('Sketcher::SketchObject', 'Sketch001')
    Sketch001.addGeometry(Part.LineSegment(Vector (-0.1487890000000007, 11.406045000000006, 0.0), Vector (40.936604, 11.406045000000006, 0.0)))
    Sketch001.addGeometry(Part.LineSegment(Vector (40.936604, 11.406045000000006, 0.0), Vector (40.936604, -21.699191999999996, 0.0)))
    Sketch001.addGeometry(Part.LineSegment(Vector (40.936604, -21.699192, 0.0), Vector (-0.14878900000000073, -21.699192, 0.0)))
    Sketch001.addGeometry(Part.LineSegment(Vector (-0.1487890000000007, -21.699192, 0.0), Vector (-0.1487890000000007, 11.406045000000002, 0.0)))
    Sketch001.addConstraint(Sketcher.Constraint('Coincident', 0, 2, 1, 1))
    Sketch001.addConstraint(Sketcher.Constraint('Coincident', 1, 2, 2, 1))
    Sketch001.addConstraint(Sketcher.Constraint('Coincident', 2, 2, 3, 1))
    Sketch001.addConstraint(Sketcher.Constraint('Coincident', 3, 2, 0, 1))
    Sketch001.addConstraint(Sketcher.Constraint('Horizontal', 0))
    Sketch001.addConstraint(Sketcher.Constraint('Horizontal', 2))
    Sketch001.addConstraint(Sketcher.Constraint('Vertical', 1))
    Sketch001.addConstraint(Sketcher.Constraint('Vertical', 3))
    Sketch001.ViewObject.DiffuseColor = [(0.00, 0.00, 0.00, 0.00)]
    Sketch001.ViewObject.ShapeColor = (0.00, 0.00, 0.00, 0.00)
    return Sketch001

def createSketch_Sketch002(doc):
    Sketch002 = doc.addObject('Sketcher::SketchObject', 'Sketch002')
    Sketch002.addGeometry(Part.ArcOfCircle(Part.Circle(Vector(56.12, -5.69, 0.00), Vector (0.0, 0.0, 1.0), 10.64), 0.6054907273817108, 6.799308361137584))
    return Sketch002


def make_optics():
    doc = App.activeDocument()

    Sketch = createSketch_Sketch(doc)
    Sketch001 = createSketch_Sketch001(doc)
    Sketch002 = createSketch_Sketch002(doc)
    
    OpticsWorkbench.makeMirror([Sketch, Sketch002])
    OpticsWorkbench.makeAbsorber([Sketch001])
    
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
                'MenuText': 'Example 1',
                'ToolTip' : '' }
                
Gui.addCommand('Example1', Example1())
