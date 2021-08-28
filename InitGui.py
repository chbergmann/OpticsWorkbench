# -*- coding: utf-8 -*-

__title__ = "FreeCAD Optics Workbench - Init file"
__author__ = "Christian Bergmann"
__url__ = ["http://www.freecadweb.org"]
__doc__ = "A template for a new workbench"
__version__ = "0.0.1"


class OpticsWorkbench (Workbench):
    def __init__(self):
        import os
        import OpticsWorkbench
        self.__class__.MenuText = "Optics"
        self.__class__.ToolTip = "Ray Tracing Simulation"
        self.__class__.Icon = os.path.join(OpticsWorkbench.get_module_path(), 'optics_workbench_icon.svg')

    def Initialize(self):
        "This function is executed when FreeCAD starts"
        # import here all the needed files that create your FreeCAD commands
        import Ray
        import OpticalObject
        from examples import example1, example3D, example_dispersion
        
        self.list = ["Ray (monochrome)", "Ray (sun light)", "Beam", "2D Radial Beam", "Spherical Beam", "Mirror", "Absorber", 'Lens', "Off", "Start"] # A list of command names created in the line above
        self.menu = self.list + ["Example2D", 'Example3D', 'ExampleDispersion']
        
        self.appendToolbar(self.__class__.MenuText, self.list) # creates a new toolbar with your commands
        self.appendMenu(self.__class__.MenuText, self.menu) # creates a new menu

    def Activated(self):
        "This function is executed when the workbench is activated"
        return

    def Deactivated(self):
        "This function is executed when the workbench is deactivated"
        return

    def ContextMenu(self, recipient):
        "This is executed whenever the user right-clicks on screen"
        # "recipient" will be either "view" or "tree"
        self.appendContextMenu(self.__class__.MenuText, self.list) # add commands to the context menu

    def GetClassName(self):
        # this function is mandatory if this is a full python workbench
        return "Gui::PythonWorkbench"


Gui.addWorkbench(OpticsWorkbench())
