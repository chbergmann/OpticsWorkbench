import subprocess

import FreeCAD
import os.path
import tempfile
import Mesh
from Part import Shape


def makeMesh(shape: Shape) -> Mesh: 
    """ Make a mesh using Gmsh 
    
        Returns
            - Mesh
    """
    freecad_path = os.path.join(FreeCAD.getHomePath(),"bin")
    gsmh_exe_path = freecad_path + '/gmsh.exe'

    cad_tmp_file = os.path.join(tempfile.gettempdir(), "cad_temp.brep")
    shape.exportBrep(cad_tmp_file)   

    # Characteristic Length
    # no boundary layer settings for this mesh
    # min, max Characteristic Length
    CharacteristicLengthMax = 1e2 #1e+22
    CharacteristicLengthMin = 0
    Optimize = 1
    # High-order meshes optimization (0=none, 1=optimization, 2=elastic+optimization, 3=elastic, 4=fast curving)
    HighOrderOptimize = 0
    ElementOrder = 2
    # Second order nodes are created by linear interpolation instead by curvilinear
    SecondOrderLinear = 1
    # mesh algorithm, only a few algorithms are usable with 3D boundary layer generation
    # 2D mesh algorithm (1=MeshAdapt, 2=Automatic, 5=Delaunay, 6=Frontal, 7=BAMG, 8=DelQuad, 9=Packing of Parallelograms)    
    Algorithm = 2
    # 3D mesh algorithm (1=Delaunay, 2=New Delaunay, 4=Frontal, 7=MMG3D, 9=R-tree, 10=HTX)
    Algorithm3D = 1
    Tolerance = 1e-08

    temp_geo = os.path.join(tempfile.gettempdir(), "cad_temp.geo")
    with open(temp_geo, 'w') as f:
        f.write('Merge "%s";\n'%(cad_tmp_file))
        f.write("Mesh.CharacteristicLengthMax = " + str(CharacteristicLengthMax) + ";\n")
        f.write("Mesh.CharacteristicLengthMin = " + str(CharacteristicLengthMin) + ";\n")
        f.write("Mesh.Optimize = " + str(Optimize) + ";\n")
        f.write("Mesh.HighOrderOptimize = " + str(HighOrderOptimize) + ";\n")
        f.write("Mesh.ElementOrder = " + str(ElementOrder) + ";\n")
        f.write("Mesh.SecondOrderLinear = " + str(SecondOrderLinear) + ";\n")
        f.write("Mesh.Algorithm = " + str(Algorithm) + ";\n")
        f.write("Mesh.Algorithm3D = " + str(Algorithm3D) + ";\n")
        f.write("Geometry.Tolerance = " + str(Tolerance) + ";\n")
        f.write("Mesh  2;\n")
        f.write("Coherence Mesh;\n")        # Remove duplicate vertices

    #./gmsh.exe - -bin -2 /tmp/mesh_cmd.geo -o /tmp/mesh.stl
    gmsh_export_file = os.path.join(tempfile.gettempdir(), "cad_temp.stl")
    
    cmd_array = []
    cmd_array.append(gsmh_exe_path)
    cmd_array.append('-')
    cmd_array.append('-bin')
    cmd_array.append('-2')
    cmd_array.append(temp_geo)
    cmd_array.append('-o')
    cmd_array.append(gmsh_export_file)

    #run dans un autre processus 
    # ouvrir une popup avec un bouton cancel et le log qui s'affiche

    output = subprocess.run(cmd_array, capture_output=True)

    #print(output)
    #check for errors if needed
    # or log to a file
    
    mesh = Mesh.read(gmsh_export_file)
    
    #clean temp file
    os.remove(cad_tmp_file)
    os.remove(temp_geo)
    os.remove(gmsh_export_file)

    return mesh