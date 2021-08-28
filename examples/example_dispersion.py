from FreeCAD import Vector
import Sketcher
import Part
import FreeCAD as App
import FreeCADGui as Gui
import OpticsWorkbench
import os
from numpy import linspace


_icondir_ = os.path.join(os.path.dirname(__file__), '..')

def create_prism(doc):
    Sketch_Prism = doc.addObject('Sketcher::SketchObject', 'Sketch_Prism')
    add_line = lambda a,b: Sketch_Prism.addGeometry(Part.LineSegment(Vector (a), Vector(b)))
    a = (1.13, 0.26, 0.0)
    b = (1.50, -.38, 0.0)
    c = (0.76, -.38, 0.0)
    add_line(a, b)
    add_line(b, c)
    add_line(c, a)

    add_constraint = lambda *args: Sketch_Prism.addConstraint(Sketcher.Constraint(*args))
    add_constraint('Coincident', 0, 2, 1, 1)
    add_constraint('Coincident', 1, 2, 2, 1)
    add_constraint('Coincident', 2, 2, 0, 1)
    add_constraint('Equal', 1, 2)
    add_constraint('Equal', 0, 1)
    Sketch_Prism.Visibility = False

    prism = doc.addObject('PartDesign::Pad','prism')
    prism.Profile= Sketch_Prism
    prism.Midplane = 1  # symmetric
    prism.Length = 0.2

    prism.ViewObject.Transparency = 70
    prism.ViewObject.LineWidth = 1
    prism.ViewObject.LineMaterial.Transparency = 30
    prism.ViewObject.PointMaterial.Transparency = 30
    return prism
    

def make_optics():
    App.newDocument("Dispersion Example")
    doc = App.activeDocument()

    prism = create_prism(doc)
    doc.recompute()
    OpticsWorkbench.makeLens(prism, material='Window glass').Label = 'Refractor'
    OpticsWorkbench.makeSunRay(maxRayLength=1.0)
    doc.recompute()

class ExampleDispersion():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''  
      
    def Activated(self):
        make_optics()
        Gui.activeDocument().activeView().viewTop()  
        Gui.SendMsgToActiveView("ViewFit")          

    def IsActive(self):
        return(True)
        
    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {'Pixmap'  : os.path.join(_icondir_, 'optics_workbench_icon.svg'),
                'Accel' : "", # a default shortcut (optional)
                'MenuText': 'Example - Dispersion',
                'ToolTip' : '' }
                
Gui.addCommand('ExampleDispersion', ExampleDispersion())
