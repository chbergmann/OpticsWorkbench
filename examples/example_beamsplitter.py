import FreeCAD
import PartDesign
import PartDesignGui
import Sketcher
import Ray
import OpticsWorkbench
import OpticalObject

def make_beamsplitter_obj():
    '''macro-recorded way to make beamsplitter object'''
    App.activeDocument().addObject('PartDesign::Body','beamsplitter')
    App.activeDocument().getObject('beamsplitter').newObject('Sketcher::SketchObject','Sketch')
    App.activeDocument().getObject('Sketch').Support = (App.activeDocument().getObject('XY_Plane'),[''])
    App.activeDocument().getObject('Sketch').MapMode = 'FlatFace'
    App.ActiveDocument.recompute()

    App.activeDocument().getObject('Sketch').addGeometry(Part.LineSegment(App.Vector(-8.353604,-6.788798,0),App.Vector(6.451339,13.249314,0)),False)
    App.activeDocument().getObject('Sketch').addGeometry(Part.LineSegment(App.Vector(6.451339,13.249314,0),App.Vector(9.090285,11.191829,0)),False)
    App.activeDocument().getObject('Sketch').addConstraint(Sketcher.Constraint('Coincident',1,1,0,2)) 
    App.activeDocument().getObject('Sketch').addGeometry(Part.LineSegment(App.Vector(9.090285,11.191829,0),App.Vector(-6.340847,-8.712098,0)),False)
    App.activeDocument().getObject('Sketch').addConstraint(Sketcher.Constraint('Coincident',2,1,1,2)) 
    App.activeDocument().getObject('Sketch').addGeometry(Part.LineSegment(App.Vector(-8.353604,-6.788798,0),App.Vector(-6.340847,-8.712098,0)),False)
    App.activeDocument().getObject('Sketch').addConstraint(Sketcher.Constraint('Coincident',3,1,0,1)) 
    App.activeDocument().getObject('Sketch').addConstraint(Sketcher.Constraint('Coincident',3,2,2,2)) 
    App.activeDocument().getObject('Sketch').addGeometry(Part.LineSegment(App.Vector(0.000000,0.000000,0),App.Vector(-15.420615,13.741322,0)),True)
    App.activeDocument().getObject('Sketch').addConstraint(Sketcher.Constraint('Coincident',4,1,-1,1)) 
    App.activeDocument().getObject('Sketch').addConstraint(Sketcher.Constraint('Angle',-1,1,4,1,2.413716))
    App.activeDocument().getObject('Sketch').setDatum(5,App.Units.Quantity('135.000000 deg'))
    App.activeDocument().getObject('Sketch').addConstraint(Sketcher.Constraint('Symmetric',0,1,0,2,4))
    App.activeDocument().getObject('Sketch').addConstraint(Sketcher.Constraint('Parallel',2,0))
    App.activeDocument().getObject('Sketch').addGeometry(Part.LineSegment(App.Vector(0.000000,0.000000,0),App.Vector(17.096584,18.035200,0)),True)
    App.activeDocument().getObject('Sketch').addConstraint(Sketcher.Constraint('Coincident',5,1,4,1)) 
    App.activeDocument().getObject('Sketch').addConstraint(Sketcher.Constraint('Angle',-1,1,5,1,0.812109))
    App.activeDocument().getObject('Sketch').setDatum(9,App.Units.Quantity('45.000000 deg'))
    App.ActiveDocument.recompute()

    App.activeDocument().getObject('Sketch').addConstraint(Sketcher.Constraint('Symmetric',0,2,1,2,5))
    App.activeDocument().getObject('Sketch').addConstraint(Sketcher.Constraint('Equal',3,1))

    App.activeDocument().getObject('Sketch').addConstraint(Sketcher.Constraint('DistanceY',2,2,0,2,18.683485))
    App.activeDocument().getObject('Sketch').setDatum(12,App.Units.Quantity('25.400000 mm'))

    App.activeDocument().getObject('Sketch').addConstraint(Sketcher.Constraint('Distance',1,7.256547))
    App.activeDocument().getObject('Sketch').setDatum(13,App.Units.Quantity('2.000000 mm'))
    App.ActiveDocument.recompute()

    ## Pad our object

    App.activeDocument().getObject('beamsplitter').newObject('PartDesign::Pad','Pad')
    App.activeDocument().getObject('Pad').Profile = App.activeDocument().getObject('Sketch')
    App.activeDocument().getObject('Pad').Length = 25.400000
    App.activeDocument().getObject('Pad').TaperAngle = 0.000000
    App.activeDocument().getObject('Pad').UseCustomVector = 0
    App.activeDocument().getObject('Pad').Direction = (0, 0, 1)
    App.activeDocument().getObject('Pad').ReferenceAxis = (App.activeDocument().getObject('Sketch'), ['N_Axis'])
    App.activeDocument().getObject('Pad').AlongSketchNormal = 1
    App.activeDocument().getObject('Pad').Type = 0
    App.activeDocument().getObject('Pad').UpToFace = None
    App.activeDocument().getObject('Pad').Reversed = 0
    App.activeDocument().getObject('Pad').Midplane = 1
    App.activeDocument().getObject('Pad').Offset = 0
    App.activeDocument().recompute()
    App.activeDocument().getObject('Sketch').Visibility = False
    FreeCADGui.activeDocument().getObject('beamsplitter').Transparency = 50

# We make our base geometry for the optics workbench. Here a 45deg oriented slab

make_beamsplitter_obj()

# Make a Mirror object from our base geometry

objects = []
objects.append(FreeCAD.ActiveDocument.getObject("Pad"))
OpticsWorkbench.makeMirror(objects)
FreeCAD.activeDocument().getObject('Mirror').Label = "reflection element"

# Make a Lens object from our base geometry

objects = []
objects.append(FreeCAD.ActiveDocument.getObject("Pad"))
OpticsWorkbench.makeLens(objects, material="Window glass")
FreeCAD.activeDocument().getObject('Lens').Label = "transmission element"
FreeCAD.activeDocument().getObject('Lens').Material = u"NBK7/Window glass"

## Add rays

OpticsWorkbench.makeRay(beamNrColumns=10, beamDistance=0.4)
FreeCAD.activeDocument().getObject('Beam').Placement = App.Placement(App.Vector(-100,0,0),App.Rotation(App.Vector(0,0,1),0))
FreeCAD.activeDocument().getObject('Beam').MaxRayLength = 200
FreeCAD.activeDocument().getObject('Beam').Wavelength = 488

OpticsWorkbench.makeRay(beamNrColumns=10, beamDistance=0.4)
FreeCAD.activeDocument().getObject('Beam001').Placement = App.Placement(App.Vector(-100,0.2,0),App.Rotation(App.Vector(0,0,1),0))
FreeCAD.activeDocument().getObject('Beam001').MaxRayLength = 200
FreeCAD.activeDocument().getObject('Beam001').Wavelength = 650


FreeCAD.activeDocument().getObject('Beam001').IgnoredOpticalElements = FreeCAD.activeDocument().getObject('Mirror')

### Lets run the calculations
OpticsWorkbench.restartAll()

# rename the rays
FreeCAD.activeDocument().getObject('Beam001').Label = "Transmitted Beam"
FreeCAD.activeDocument().getObject('Beam').Label = "Reflected Beam"


