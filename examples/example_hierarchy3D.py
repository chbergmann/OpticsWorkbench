from FreeCAD import Vector, Rotation
import Sketcher
import Part
import FreeCAD as App
import FreeCADGui as Gui
from BOPTools import BOPFeatures
import OpticsWorkbench
import os
from PySide.QtCore import QT_TRANSLATE_NOOP

_icondir_ = os.path.join(os.path.dirname(__file__), '..')
_exname_ = QT_TRANSLATE_NOOP('ExampleHierarchy3D', 'Example - Hierarchy 3D')

def makeLens(doc, name):
    sphere = doc.addObject('Part::Sphere', name + '_sphere')
    box = doc.addObject('Part::Box', name + '_box')
    box.Placement.Base = Vector(-2, -5, -5)
    bp = BOPFeatures.BOPFeatures(doc)
    cut = bp.make_cut([sphere.Label, box.Label])
    cut.Label = name + '_cut'
    cut.Placement.Base = Vector(0, 10, 0)
    cut.Placement.Rotation = Rotation(-42, 0, 0)
    lens = OpticsWorkbench.makeLens([cut])
    lens.Label = name
    return lens

def makeMirror(doc, name):
    box = doc.addObject('Part::Box', name + '_box')
    box.Length = 2.0
    box.Placement.Base = Vector(5, -2.0, -5.0)
    box.Placement.Rotation = Rotation(-10, 0, 0)
    mirror = OpticsWorkbench.makeMirror([box])
    mirror.Label = name
    return mirror

def makeRay(name):
    ray = OpticsWorkbench.makeRay(Vector(0, 0, 0), Vector(2.0, 1.0, 0), beamNrColumns=10, beamNrRows=10, beamDistance=0.4)
    ray.Placement.Base = Vector(0, -1.5, -2)
    ray.Label = name
    return ray

def createRayInsideMirrorInside(doc):
    obj = doc.addObject('App::Part', 'ray_inside_mirror_inside')
    mirror = makeMirror(doc, 'mirror_a')
    obj.addObject(mirror)
    lens = makeLens(doc, 'lens_a')
    obj.addObject(lens)
    ray = makeRay('ray_a')
    obj.addObject(ray)
    obj.Placement.Base = Vector(-30.0, -30.0, 0.0)
    ray.MaxRayLength = 24.0
    return obj

def createRayOutsideMirrorOutside(doc):
    obj = doc.addObject('App::DocumentObjectGroup', 'ray_outside_mirror_outside')
    mirror = makeMirror(doc, 'mirror_b')
    mirror.Base[0].Placement.Base += Vector(30.0, -30.0, 0.0)
    obj.addObject(mirror)
    lens = makeLens(doc, 'lens_b')
    lens.Base[0].Placement.Base += Vector(30.0, -30.0, 0.0)
    obj.addObject(lens)
    ray = makeRay('ray_b')
    ray.Placement.Base += Vector(30.0, -30.0, 0.0)
    obj.addObject(ray)
    ray.MaxRayLength = 24.0
    return obj

def createRayInsideMirrorOutside(doc):
    obj = doc.addObject('App::DocumentObjectGroup', 'ray_inside_mirror_outside')
    obj_inside = doc.addObject('App::Part', 'ray_inside')
    obj_inside.Placement.Base = Vector(-30.0, 30.0, 0.0)
    obj.addObject(obj_inside)
    mirror = makeMirror(doc, 'mirror_c')
    mirror.Base[0].Placement.Base += Vector(-30.0, 30.0, 0.0)
    obj.addObject(mirror)
    lens = makeLens(doc, 'lens_c')
    lens.Base[0].Placement.Base += Vector(-30.0, 30.0, 0.0)
    obj.addObject(lens)
    ray = makeRay('ray_c')
    obj_inside.addObject(ray)
    ray.MaxRayLength = 24.0
    return obj

def createRayOutsideMirrorInside(doc):
    obj = doc.addObject('App::DocumentObjectGroup', 'ray_outside_mirror_inside')
    obj_inside = doc.addObject('App::Part', 'mirror_inside')
    obj_inside.Placement.Base = Vector(30.0, 30.0, 0.0)
    obj.addObject(obj_inside)
    mirror = makeMirror(doc, 'mirror_d')
    obj_inside.addObject(mirror)
    lens = makeLens(doc, 'lens_d')
    obj_inside.addObject(lens)
    ray = makeRay('ray_d')
    ray.Placement.Base += Vector(30.0, 30.0, 0.0)
    obj.addObject(ray)
    ray.MaxRayLength = 24.0
    return obj

def make_optics():
    App.newDocument()
    doc = App.activeDocument()

    createRayInsideMirrorInside(doc)
    createRayOutsideMirrorOutside(doc)
    createRayInsideMirrorOutside(doc)
    createRayOutsideMirrorInside(doc)

    doc.recompute()

class ExampleHierarchy3D():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''

    def Activated(self):
        make_optics()
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

Gui.addCommand('ExampleHierarchy3D', ExampleHierarchy3D())
