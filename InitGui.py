# -*- coding: utf-8 -*-

__title__ = 'FreeCAD Optics Workbench - Init file'
__author__ = 'Christian Bergmann'
__url__ = ['http://www.freecadweb.org']
__doc__ = 'Optics Workbench workbench'
__version__ = '0.0.1'


class OpticsWorkbench (Workbench):
    def __init__(self):
        import os
        import OpticsWorkbench
        import FreeCADGui

        translate = FreeCAD.Qt.translate
        translations_path = os.path.join(OpticsWorkbench.get_module_path(), "translations")
        FreeCADGui.addLanguagePath(translations_path)
        FreeCADGui.updateLocale()
        
        self.__class__.MenuText = 'Optics'
        self.__class__.ToolTip = translate("Workbench", 'Ray Tracing Simulation')
        self.__class__.Icon = os.path.join(OpticsWorkbench.get_module_path(), 'optics_workbench_icon.svg')

    def Initialize(self):
        '''This function is executed when FreeCAD starts'''
        # import here all the needed files that create your FreeCAD commands
        import Ray
        import OpticalObject
        import Plot
        from examples import example1, example3D, example_dispersion, example_candle, example_semi, example_hierarchy2D, example_hierarchy3D
        from PySide.QtCore import QT_TRANSLATE_NOOP
        
        rays = [QT_TRANSLATE_NOOP('Workbench', 'Ray (monochrome)'),
            QT_TRANSLATE_NOOP('Workbench', 'Ray (sun light)'),
            QT_TRANSLATE_NOOP('Workbench', 'Beam'),
            QT_TRANSLATE_NOOP('Workbench', '2D Radial Beam'),
            QT_TRANSLATE_NOOP('Workbench', 'Spherical Beam')]
        optics = [QT_TRANSLATE_NOOP('Workbench', 'Emitter'),
            QT_TRANSLATE_NOOP('Workbench', 'Mirror'), 
            QT_TRANSLATE_NOOP('Workbench', 'Grating'), 
            QT_TRANSLATE_NOOP('Workbench', 'Absorber'), 
            QT_TRANSLATE_NOOP('Workbench', 'Lens')]
        actions = [QT_TRANSLATE_NOOP('Workbench', 'Off'), QT_TRANSLATE_NOOP('Workbench', 'Start')]
        analysis= [QT_TRANSLATE_NOOP('Workbench', 'RayHits'), QT_TRANSLATE_NOOP('Workbench', 'Hits2CSV')]
        separator = ['Separator']
        examples = [QT_TRANSLATE_NOOP('Workbench', 'Example2D'), 
            QT_TRANSLATE_NOOP('Workbench', 'Example3D'),
            QT_TRANSLATE_NOOP('Workbench', 'ExampleDispersion'), 
            QT_TRANSLATE_NOOP('Workbench', 'ExampleCandle'), 
            QT_TRANSLATE_NOOP('Workbench', 'ExampleSemi'), 
            QT_TRANSLATE_NOOP('Workbench', 'ExampleHierarchy2D'), 
            QT_TRANSLATE_NOOP('Workbench', 'ExampleHierarchy3D')]
        self.list = rays + separator + optics + separator + actions + separator + analysis #A list of command names created in the line above
        self.menu = self.list + separator + examples
        
        self.appendToolbar(self.__class__.MenuText, self.list) # creates a new toolbar with your commands
        self.appendMenu(self.__class__.MenuText, self.menu) # creates a new menu

    def Activated(self):
        '''This function is executed when the workbench is activated'''
        return

    def Deactivated(self):
        '''This function is executed when the workbench is deactivated'''
        return

    def ContextMenu(self, recipient):
        '''This is executed whenever the user right-clicks on screen'''
        # 'recipient' will be either 'view' or 'tree'
        self.appendContextMenu(self.__class__.MenuText, self.list) # add commands to the context menu

    def GetClassName(self):
        # this function is mandatory if this is a full python workbench
        return 'Gui::PythonWorkbench'


Gui.addWorkbench(OpticsWorkbench())
