# ![WorkbenchIcon](./icons/pyrate_logo_icon.svg) Optics Workbench
    
Geometrical optics for FreeCAD.  
Performs simple raytracing through your FreeCAD objects.

![screenshot](./examples/screenshot.jpg)

## Work in progress !
The current version only supports 2D objects


  
## Installation

### Automatic Installation
**Note: This is the recommended way to install this workbench.**  
The Python Workbench Template will be available soon through the builtin FreeCAD [Addon Manager](https://github.com/FreeCAD/FreeCAD-addons#1-builtin-addon-manager).
Once installed all that is needed is to restart FreeCAD and the workbench will be available in the [workbench dropdown list](https://freecadweb.org/wiki/Std_Workbench) menu.

### Manual Installation

```bash
cd ~/FreeCAD/Mod/ 
git clone https://github.com/chbergmann/OpticsWorkbench.git
```
When you restart FreeCAD, "Optics Workbench" workbench should now show up in the [workbench dropdown list](https://freecadweb.org/wiki/Std_Workbench).
  
## Getting started

## Tools
### ![RayIcon](./icons/ray.svg) Ray
A single ray for raytracing

### ![2D Beam](./icons/rayarray.svg) 2D Beam
A row of multiple rays for raytracing

### ![Optical Mirror](./icons/mirror.svg) Optical Mirror
The selected FreeCAD objects will act as mirrors

### ![Optical Absorber](./icons/absorber.svg) Optical Absorber
The selected FreeCAD objects will swallow the rays of light

### ![Off](./icons/Anonymous_Lightbulb_Lit.svg) Switch off lights
Switches off all Rays and Beams

### ![Off](./icons/Anonymous_Lightbulb_Off.svg) (Re)start simulation
Switches on and recalculates all Rays and Beams

## Discussion
Please offer feedback or connect with the developer via the [dedicated FreeCAD forum thread](https://forum.freecadweb.org).

## License
GNU Lesser General Public License v3.0
