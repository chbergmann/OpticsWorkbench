# ![WorkbenchIcon](./optics_workbench_icon.svg) Optics Workbench
    
Geometrical optics for FreeCAD.  
Performs simple raytracing through your FreeCAD objects.

[![Total alerts](https://img.shields.io/lgtm/alerts/g/chbergmann/OpticsWorkbench.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/chbergmann/OpticsWorkbench/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/chbergmann/OpticsWorkbench.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/chbergmann/OpticsWorkbench/context:python)

![screenshot](./examples/example2D.png)
  
## Installation

### Auto Installation

Optics workbench is available through the FreeCAD [Addon Manager](https://wiki.freecad.org/AddonManager)

### Manual Installation

<details>
<summary>Expand to view manual installation instructions</summary>

```bash
cd ~/.FreeCAD/Mod/ 
git clone https://github.com/chbergmann/OpticsWorkbench.git
```

</details>

#### Important Note
Once Optics workbench is installed, FreeCAD will need to be restarted. When you restart FreeCAD, "Optics Workbench" workbench should now show up in the [workbench dropdown list](https://freecad.org/wiki/Std_Workbench).
  
## Getting started
- Create some FreeCAD design objects. For 2D simulation Sketches will do the job.
- Select one or more of your design objects and then create Optical Mirror to let your objects act as mirrors
- Select one or more of your design objects and then create Optical Absorber to let your objects act as black walls for the light rays
- Select one or more of your design objects and then create Optical Lenses to let your objects act as lenses. Lenses should be closed shapes. 
Select a material in the Lens properties or provide a refraction index.
- Add some source of light (Ray, Beam). 

## Tools
### ![RayIcon](./icons/ray.svg) Ray (monochrome)
A single ray for raytracing  
Parameters:
- Power: On or Off  
- Spherical: False=Beam in one direction, True=Radial or spherical rays
- BeamNrColumns: Number of rays in a beam per row
- BeamNrRows: Number of rays in a beam per column
- BeamDistance: Distance between two beams
- HideFirstPart: Hide the first part of every ray that comes from the source and goes to the first point of reflection/refraction/nirvana
- MaxRayLength: Maximum length of a ray
- MaxNrReflections: Maximum number of reflections. This prevents endless loops if the ray is inside a mirror box.

### ![SunRayIcon](./icons/raysun.svg) Ray (sun light)
A bunch of rays with different wavelengths of visible light.  
The rays overlap. If they hit a lens, they will be dispersed. See the Example - Dispersion.

### ![2D Beam](./icons/rayarray.svg) 2D Beam
A row of multiple rays for raytracing  
Parameters: see Ray. BeamNrColumns must be > 1 to get a beam

### ![Radial Beam](./icons/sun.svg) 2D Radial Beam
Rays coming from one point going to all directions in a 2D plane  
Parameters: see Ray. BeamNrColumns must be > 1 and BeamNrRows=1 and Spherical=True to get a radial beam

### ![Spherical Beam](./icons/sun3D.svg) Spherical Beam
Rays coming from one point going to all directions  
Parameters: see Ray. BeamNrColumns and BeamNrRows must be > 1 Spherical=True to get a spherical beam

### ![Optical Mirror](./icons/mirror.svg) Optical Mirror
The FreeCAD objects in parameter Base will act as mirrors  
Select some FreeCAD objects, then create Optical Mirror  
After a ray or beam has been added, a parameter 'Hits From Ray/Beam...' will appear. This is a counter of how many reflections you have from each ray. Do not modify this value.

### ![Optical Absorber](./icons/absorber.svg) Optical Absorber
The FreeCAD objects in parameter Base will swallow the rays of light  
Select some FreeCAD objects, then create Optical Absorber  
After a ray or beam has been added, a parameter 'Hits From Ray/Beam...' will appear. This is a counter of how many rays have hit this absorber. Do not modify this value.  
'Hit coordinates from ... (read only)' records the position of each LIGHT RAY when it hits. This way, it is possible to visualize the image on the absorber in a XY diagram.  
  
![screenshot](./examples/ccd_xyplot.png)  
  
To show an XY plot, open a python console and type:  

	import OpticsWorkbench
	OpticsWorkbench.plot_xy(App.ActiveDocument.Absorber)

### ![Optical Lens](./icons/lens.svg) Optical Lens
The FreeCAD objects in parameter Base will act as lenses  
Select some FreeCAD objects, then create Optical Lens  
The Refration Index has to be provided. The parameter Material contains a list with pre defined refraction indexes.  
After a ray or beam has been added, a parameter 'Hits From Ray/Beam...' will appear. This is a counter of how many refractions you have from each ray. Do not modify this value.

### ![Off](./icons/Anonymous_Lightbulb_Off.svg) Switch off lights
Switches off all Rays and Beams

### ![On](./icons/Anonymous_Lightbulb_Lit.svg) (Re)start simulation
Switches on and recalculates all Rays and Beams

### ![Example](./optics_workbench_icon.svg) Example - 2D
generates the screenshot above

### ![Example](./optics_workbench_icon.svg) Example - 3D
![screenshot](./examples/screenshot3D.png)

### ![Example](./optics_workbench_icon.svg) Example - Dispersion
![screenshot](https://pad.ccc-p.org/uploads/upload_210b4dd5466d2837eb76d5e63688a5c1.png)

## Issues and Troubleshooting
see [issues on Github](https://github.com/chbergmann/OpticsWorkbench/issues)

## Discussion
Please offer feedback or connect with the developer via the [dedicated FreeCAD forum thread](https://forum.freecad.org/viewtopic.php?f=8&t=59860).

## License
GNU Lesser General Public License v3.0 ([LICENSE](LICENSE))
