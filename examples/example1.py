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
    Sketch.addGeometry(Part.Circle(Vector(0.00, -15.18, 0.00), Vector (0.0, 0.0, 1.0), 1.00))
    Sketch.toggleConstruction(2)
    Sketch.addGeometry(Part.Circle(Vector(7.19, -16.35, 0.00), Vector (0.0, 0.0, 1.0), 1.00))
    Sketch.toggleConstruction(3)
    Sketch.addGeometry(Part.BSplineCurve([Vector(0.00, -5.56, 0.00), Vector(0.00, -15.18, 0.00), Vector(7.19, -16.35, 0.00)]))
    Sketch.addGeometry(Part.Point(Vector(0.00, -5.56, 0.00)))
    Sketch.addGeometry(Part.Point(Vector(20.47, -18.63, 0.00)))
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

def createSketch_Sketch003(doc):
    Sketch003 = doc.addObject('Sketcher::SketchObject', 'Sketch003')
    Sketch003.addGeometry(Part.LineSegment(Vector (11.570197790355408, -6.791990000000003, 0.0), Vector (11.570197790355408, -16.791990000000002, 0.0)))
    Sketch003.addGeometry(Part.ArcOfCircle(Part.Circle(Vector(8.25, -11.79, 0.00), Vector (0.0, 0.0, 1.0), 6.00), 5.298074523841841, 7.268296090517332))
    Sketch003.addConstraint(Sketcher.Constraint('Vertical', 0))
    Sketch003.addConstraint(Sketcher.Constraint('Coincident', 1, 1, 0, 2))
    Sketch003.addConstraint(Sketcher.Constraint('Coincident', 1, 2, 0, 1))
    Sketch003.addConstraint(Sketcher.Constraint('Radius', 1, 6.00))
    Sketch003.addConstraint(Sketcher.Constraint('DistanceY', 0, 2, 0, 1, 10.00))
    return Sketch003
    
def make_optics():
    doc = App.activeDocument()

    Sketch = createSketch_Sketch(doc)
    Sketch001 = createSketch_Sketch001(doc)
    Sketch001.ViewObject.LineColor = (0.00,0.00,0.00)
    Sketch001.ViewObject.PointColor = (0.00,0.00,0.00)
    Sketch002 = createSketch_Sketch002(doc)
    Sketch003 = createSketch_Sketch003(doc)
    
    OpticsWorkbench.makeMirror([Sketch, Sketch002])
    OpticsWorkbench.makeAbsorber([Sketch001])
    OpticsWorkbench.makeLens([Sketch003], material='Flint glass')
    
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
                'MenuText': 'Example 2D',
                'ToolTip' : '' }
                
Gui.addCommand('Example2D', Example1())
