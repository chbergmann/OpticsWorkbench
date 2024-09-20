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
        
        self.__class__.MenuText = translate("OpticsWorkbench", 'Optics')
        self.__class__.ToolTip = translate("OpticsWorkbench", 'Ray Tracing Simulation')
        self.__class__.Icon = os.path.join(OpticsWorkbench.get_module_path(), 'optics_workbench_icon.svg')

    def Initialize(self):
        '''This function is executed when FreeCAD starts'''
        # import here all the needed files that create your FreeCAD commands
        import Ray
        import OpticalObject
        import Plot
        from examples import example1, example3D, example_dispersion, example_candle
        from PySide.QtCore import QT_TRANSLATE_NOOP
        
        rays = [QT_TRANSLATE_NOOP('OpticsWorkbench', 'Ray (monochrome)'),
            QT_TRANSLATE_NOOP('OpticsWorkbench', 'Ray (sun light)'),
            QT_TRANSLATE_NOOP('OpticsWorkbench', 'Beam'),
            QT_TRANSLATE_NOOP('OpticsWorkbench', '2D Radial Beam'),
            QT_TRANSLATE_NOOP('OpticsWorkbench', 'Spherical Beam')]
        optics = [QT_TRANSLATE_NOOP('OpticsWorkbench', 'Emitter'),
            QT_TRANSLATE_NOOP('OpticsWorkbench', 'Mirror'), 
            QT_TRANSLATE_NOOP('OpticsWorkbench', 'Grating'), 
            QT_TRANSLATE_NOOP('OpticsWorkbench', 'Absorber'), 
            QT_TRANSLATE_NOOP('OpticsWorkbench', 'Lens')]
        actions = [QT_TRANSLATE_NOOP('OpticsWorkbench', 'Off'), QT_TRANSLATE_NOOP('OpticsWorkbench', 'Start')]
        analysis= [QT_TRANSLATE_NOOP('OpticsWorkbench', 'RayHits'), QT_TRANSLATE_NOOP('OpticsWorkbench', 'Hits2CSV')]
        separator = ['Separator']
        examples = [QT_TRANSLATE_NOOP('OpticsWorkbench', 'Example2D'), 
            QT_TRANSLATE_NOOP('OpticsWorkbench', 'Example3D'),
            QT_TRANSLATE_NOOP('OpticsWorkbench', 'ExampleDispersion'), 
            QT_TRANSLATE_NOOP('OpticsWorkbench', 'ExampleCandle')]
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
