# ![WorkbenchIcon](./icons/pyrate_logo_icon.svg) Optics Workbench
    
Geometrical optics for FreeCAD.  
Performs simple raytracing through your FreeCAD objects.

[![Total alerts](https://img.shields.io/lgtm/alerts/g/chbergmann/OpticsWorkbench.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/chbergmann/OpticsWorkbench/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/chbergmann/OpticsWorkbench.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/chbergmann/OpticsWorkbench/context:python)

![screenshot](./examples/screenshot.jpg)

## Work in progress !
- Lenses are not yet implemented
  
## Installation


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

### ![Radial Beam](./icons/sun.svg) 2D Radial Beam
Rays coming from one point going to all directions in a 2D plane

### ![Optical Mirror](./icons/mirror.svg) Optical Mirror
The selected FreeCAD objects will act as mirrors

### ![Optical Absorber](./icons/absorber.svg) Optical Absorber
The selected FreeCAD objects will swallow the rays of light

### ![Off](./icons/Anonymous_Lightbulb_Off.svg) Switch off lights
Switches off all Rays and Beams

### ![On](./icons/Anonymous_Lightbulb_Lit.svg) (Re)start simulation
Switches on and recalculates all Rays and Beams

### ![Example](./icons/pyrate_logo_icon.svg) Example 2D
generates the screenshot above

### ![Example](./icons/pyrate_logo_icon.svg) Example 3D
![screenshot](./examples/screenshot3D.png)

## Discussion
Please offer feedback or connect with the developer via the [dedicated FreeCAD forum thread](https://forum.freecadweb.org/viewtopic.php?f=8&t=59860).

## License
GNU Lesser General Public License v3.0
