
import os, math
import OpticalObject

import FreeCADGui as Gui
import FreeCAD
import Part
import HelperFcts
from FreeCAD import Vector
from FreeCAD import activeDocument
from Mesh import Facet
import traceback
import test_functions
from PySide.QtGui import QDialog

import OpticsTiboWorkbench
OpticsTiboWB_path = os.path.dirname(OpticsTiboWorkbench.__file__)
OpticsTiboWB_icons_path =  os.path.join( OpticsTiboWB_path, 'Resources', 'icons')

INFINITY = 1677216
EPSILON = 1/INFINITY

def makeEmitter(selection = []):
    base = []
    faces = []
    if len(selection) == 0:
        sphere = FreeCAD.ActiveDocument.addObject("Part::Sphere", "Sphere")
        sphere.Radius = 1.5
        sphere.Label = "EmittingSphere"
        base.append(sphere)
    else:
        for selection_object in selection:
            if selection_object.HasSubObjects:
                for sub_object in selection_object.SubObjects:
                    if isinstance(sub_object, Part.Face):
                        faces.append(sub_object)
            else:
                faces = selection_object.Object.Shape.Faces

        base.append(selection[0].Object)

    print('add emitter')
    fp = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', 'Emitter')
    print('add mesh')
    mesh = FreeCAD.ActiveDocument.addObject("Mesh::Feature","Mesh")
    print('add beams')
    beams = FreeCAD.ActiveDocument.addObject('Part::FeaturePython', "Beams")

    if len(faces) != 0:
        emittingSurfaces = Part.makeCompound(faces)
    else:
        emittingSurfaces = Part.makeCompound(base[0].Shape.Faces)

    mesh.Label = "EmitterMesh"
    mesh.ViewObject.DisplayMode = "Flat Lines"
    mesh.ViewObject.LineColor = (1.0, 1.0, 0.0, 0.0)    
    mesh.ViewObject.Transparency = 100
    
    base.append(mesh)
    base.append(beams)

    EmitterWorker(fp, base, emittingSurfaces)
    EmitterViewProvider(fp.ViewObject)

    beams.ViewObject.LineColor = (1.0, 1.0, 0.0)
    beams.ViewObject.Transparency = 80 
    beams.ViewObject.LineWidth = 1.0   
    BeamViewProvider(beams.ViewObject)
    FreeCAD.ActiveDocument.recompute()
    return fp

class EmitterWorker:
    def __init__(self, 
                 fp,    # an instance of Part::FeaturePython
                 base = [],
                 emittingSurfaces = None,
                 power = False,
                 Temperature = 2000,
                 hideFirst=False,    
                 maxRayLength = 1000, #♣1000000,
                 maxNrReflections = 5, #200,   
                 MaxLength = 1.0,
                 BeamSpread = 1):
        """ Creates an emitter """

        self.update = False 

        fp.addProperty('App::PropertyEnumeration', 'EmitterType', 'Emitter', '').EmitterType = ['BlackBody', 'Laser', 'LED'] 
        fp.addProperty('App::PropertyLinkList',  'Base',   'Emitter',   'FreeCAD objects to be emitters').Base = base
        fp.addProperty('App::PropertyFloat',  'Emissivity',   'Emitter',   'Emissivity').Emissivity = 1.0
        fp.addProperty('App::PropertyBool', 'Power', 'Ray',  'On or Off').Power = power
        fp.addProperty('App::PropertyBool', 'HideFirstPart', 'Ray',  'hide the first part of every ray').HideFirstPart = hideFirst        
        fp.addProperty('App::PropertyFloat',  'Temperature',   'Emitter',   'Black body temperature').Temperature = Temperature
        fp.addProperty('App::PropertyIntegerConstraint',  'BeamSpread',   'Emitter',   'Beam spread').BeamSpread = BeamSpread
        fp.addProperty('App::PropertyFloat', 'MaxRayLength', 'Ray',  'maximum length of a ray').MaxRayLength = maxRayLength            
        fp.addProperty('App::PropertyIntegerConstraint', 'MaxNrReflections', 'Ray',  'maximum number of reflections').MaxNrReflections = maxNrReflections        
        fp.addProperty('App::PropertyFloat',  'MaxLength',   'Mesh',   'Mesh max length').MaxLength = MaxLength
        fp.addProperty('Part::PropertyPartShape',  'EmittingSurfaces',   'Emitter',   'Emitting surface').EmittingSurfaces = emittingSurfaces
        

        fp.EmitterType = 'BlackBody'         

        self.update = True 
        fp.Proxy = self
        print('init - end emitter')   
           

    def execute(self, fp):
        print('Emitter - execute')
        self.redrawRay(fp)
        
    def onChanged(self, fp, prop):
        proplist = ['MaxLength']
        if prop in proplist:
            print("Emitter - onChanged")
            self.redrawRay(fp)

    def redrawRay(self, fp):
        if not self.update: 
            print('redraw not ready')
            return
        self.update = False
        print('redraw')
        
        mesh = HelperFcts.makeMesh(fp.EmittingSurfaces)

        fp.Base[1].Mesh = mesh

        lineArray = []
        fc : Facet
        for fc in fp.Base[1].Mesh.Facets:
            center = Vector(0,0,0)
            for point in fc.Points:
                center += Vector(point)
            center = center / 3
            self.makeInitialRay(fp, lineArray, center, fc.Normal)
            #line = Part.makeLine(center, center + fc.Normal)
            #lineArray.append(line)

        fp.Base[2].Shape = Part.makeCompound(lineArray)

        self.update = True
    
    
    def makeInitialRay(self, fp, linearray, pos, dir):
        if fp.Power == True:
            self.iter = fp.MaxNrReflections
            ray = Part.makeLine(pos, pos + dir * fp.MaxRayLength / dir.Length)
            linearray.append(ray)
            self.lastRefIdx = []

            try:
                self.traceRay(fp, linearray, True)
            except Exception as ex:
                print(ex)
                traceback.print_exc()
        else:
            linearray.append(Part.makeLine(pos, pos + dir))


    def getIntersections(self, line : Part.Edge ):
        '''returns [(OpticalObject, [(edge/face, intersection point)] )]'''

        isec_struct = []
        origin = PointVec(line.Vertexes[0])
        dir = PointVec(line.Vertexes[1]) - origin
        for optobj in activeDocument().Objects:
            if isOpticalObject(optobj):
                isec_parts = []
                obj : Part.Feature
                for obj in optobj.Base:
                    if obj.Shape.BoundBox.intersect(origin, dir):
                        if len(obj.Shape.Solids) == 0 and len(obj.Shape.Shells) == 0:
                            for edge in obj.Shape.Edges:
                                edgedir = PointVec(edge.Vertexes[1]) - PointVec(edge.Vertexes[0])
                                normal = dir.cross(edgedir)
                                if normal.Length > EPSILON:
                                    plane = Part.Plane(origin, normal)
                                    isec = line.Curve.intersect2d(edge.Curve, plane)
                                    if isec:
                                        for p in isec:
                                            p2 = plane.value(p[0], p[1])
                                            dist = p2 - origin
                                            vert=Part.Vertex(p2)
                                            if dist.Length > EPSILON and vert.distToShape(edge)[0] < EPSILON and vert.distToShape(line)[0] < EPSILON:
                                                isec_parts.append((edge, p2))

                        for face in obj.Shape.Faces:
                            face : Part.Face
                            if face.BoundBox.intersect(origin, dir):
                                isec = line.Curve.intersect(face.Surface)
                                if isec:
                                    for p in isec[0]:
                                        dist = Vector(p.X - origin.x, p.Y - origin.y, p.Z - origin.z)
                                        vert=Part.Vertex(p)
                                        debug1 = vert.distToShape(face)[0]
                                        debug2 = vert.distToShape(line)[0]
                                        if dist.Length > EPSILON and debug1 < EPSILON and debug2 < EPSILON:
                                            isec_parts.append((face, PointVec(p)))

                if len(isec_parts) > 0:
                    isec_struct.append((optobj, isec_parts))

        return isec_struct


    def traceRay(self, fp, linearray, first=False):
        nearest = Vector(INFINITY, INFINITY, INFINITY)
        nearest_parts = []
        doLens = False

        if len(linearray) == 0: return

        line = linearray[len(linearray) - 1]

        if fp.HideFirstPart and first:
            linearray.remove(line)

        isec_struct = self.getIntersections(line)
        origin = PointVec(line.Vertexes[0])
        length = PointVec(line.Vertexes[1])

        for isec in isec_struct:
            for ipoints in isec[1]:
                dist : Vector
                dist = ipoints[1] - origin
                if dist.Length <= nearest.Length + EPSILON:
                    np = (ipoints[1], ipoints[0], isec[0])
                    if abs(dist.Length - nearest.Length) < EPSILON:
                        nearest_parts.append(np)
                    else:
                        nearest_parts = [np]

                    nearest = dist

        if len(nearest_parts) == 0: 
            # TODO the ray did not encounter any objects => limit the visible length
            shortline = Part.makeLine(origin, origin + length / 10)
            linearray[len(linearray) - 1] = shortline
            return

        if len(self.lastRefIdx) == 0:
            oldRefIdx = 1
        else:
            oldRefIdx = self.lastRefIdx[len(self.lastRefIdx) - 1]

        if len(self.lastRefIdx) < 2:
            newRefIdx = 1
        else:
            newRefIdx = self.lastRefIdx[len(self.lastRefIdx) - 2]

        for np in nearest_parts:
            (neworigin, nearest_part, nearest_obj) = np
            shortline = Part.makeLine(origin, neworigin)

            hitname = 'HitsFrom' + fp.Label
            if not hasattr(nearest_obj, hitname):
                nearest_obj.addProperty('App::PropertyQuantity',  hitname,   'OpticalObject',   'Counts the hits from ' + fp.Label + ' (read only)')
                setattr(nearest_obj, hitname, 1)
            else:
                setattr(nearest_obj, hitname, getattr(nearest_obj, hitname) + 1)

            if nearest_obj.OpticalType == "absorber":
                # print("A RAY coming from", fp.Label, "hits the receiver at", tuple(neworigin))
                hitcoordsname = 'HitCoordsFrom' + fp.Label
                if not hasattr(nearest_obj, hitcoordsname):
                    nearest_obj.addProperty('App::PropertyVectorList',  hitcoordsname,   'OpticalObject',   'Hit coordinates from ' + fp.Label + ' (read only)')
                    setattr(nearest_obj, hitcoordsname, [])
                setattr(nearest_obj, hitcoordsname, getattr(nearest_obj, hitcoordsname) + [neworigin,] )

            if fp.HideFirstPart == False or first == False:
                linearray[len(linearray) - 1] = shortline

            self.iter -= 1
            if self.iter == 0: return

            dRay = neworigin - origin
            ray1 = dRay / dRay.Length

            normal = self.getNormal(nearest_obj, nearest_part, origin, neworigin)
            if normal.Length == 0:
                print('Cannot determine the normal on ' + nearest_obj.Label)
                return

            if nearest_obj.OpticalType == 'mirror':
                dNewRay = self.mirror(dRay, normal)
                break

            elif nearest_obj.OpticalType == 'lens':
                doLens = True
                if len(nearest_obj.Sellmeier) == 6:
                    n = OpticalObject.refraction_index_from_sellmeier(fp.Wavelength, nearest_obj.Sellmeier)
                else:
                    n = nearest_obj.RefractionIndex

                if self.isInsideLens(isec_struct, origin, nearest_obj):
                    #print("leave " + nearest_obj.Label)
                    oldRefIdx = n
                    if len(self.lastRefIdx) > 0:
                        self.lastRefIdx.pop(len(self.lastRefIdx) - 1)
                    #print()
                else:
                    #print("enter " + nearest_obj.Label)
                    newRefIdx = n
                    self.lastRefIdx.append(n)

            elif nearest_obj.OpticalType == 'grating':  
                if len(nearest_obj.Sellmeier) == 6:
                    n = OpticalObject.refraction_index_from_sellmeier(fp.Wavelength, nearest_obj.Sellmeier)
                else:
                    n = nearest_obj.RefractionIndex
                
                lpm = nearest_obj.lpm
                grating_lines_plane =nearest_obj.GratingLinesPlane

                if nearest_obj.ray_order_override == True:
                    order = nearest_obj.order
                else:
                    order = fp.Order

                
                if nearest_obj.GratingType == "reflection":
                    grating_type = 0
                elif nearest_obj.GratingType == "transmission - diffraction at 2nd surface":
                    grating_type = 1
                else:
                    grating_type = 2

                if grating_type == 0: #reflection grating
                    dNewRay = self.grating_calculation(grating_type, order, fp.Wavelength, lpm, ray1, normal, grating_lines_plane, oldRefIdx, oldRefIdx)
                
                elif grating_type == 2: #transmission grating with diffraction at first surface
                    if self.isInsideLens(isec_struct, origin, nearest_obj):
                        doLens = True
                        #print("leave t-grating 1s " + nearest_obj.Label)
                        oldRefIdx = n
                        #print("old RefIdx: ", oldRefIdx, "new RefIdx: ", newRefIdx)
                        if len(self.lastRefIdx) > 0:
                            self.lastRefIdx.pop(len(self.lastRefIdx) - 1)
                    else:
                        newRefIdx = n
                        self.lastRefIdx.append(n)
                        #print("enter t-grating 1s " + nearest_obj.Label)
                        #print("old RefIdx: ", oldRefIdx, "new RefIdx: ", newRefIdx)
                        dNewRay = self.grating_calculation(grating_type, order, fp.Wavelength, lpm, ray1, normal, grating_lines_plane, oldRefIdx, newRefIdx)
                
                elif grating_type == 1: #transmission grating with diffraction at second surface
                    if self.isInsideLens(isec_struct, origin, nearest_obj):
                        #print("leave t-grating 2s " + nearest_obj.Label)
                        oldRefIdx = n
                        #print("old RefIdx: ", oldRefIdx, "new RefIdx: ", newRefIdx)
                        dNewRay = self.grating_calculation(grating_type, order, fp.Wavelength, lpm, ray1, normal, grating_lines_plane, oldRefIdx, newRefIdx)
                    else:
                        doLens = True
                        newRefIdx = n
                        self.lastRefIdx.append(n)
                        #print("enter t-grating 2s " + nearest_obj.Label)
                        #print("old RefIdx: ", oldRefIdx, "new RefIdx: ", newRefIdx)                   
               
            else: return

        if doLens:
            dNewRay = self.snellsLaw(ray1, oldRefIdx, newRefIdx, normal)

        newline = Part.makeLine(neworigin, neworigin - dNewRay * fp.MaxRayLength / dNewRay.Length)
        linearray.append(newline)
        self.traceRay(fp, linearray)
        return newline


    def getNormal(self, nearest_obj, nearest_part, origin, neworigin):
        dRay = neworigin - origin
        if hasattr(nearest_part, 'Curve'):
            param = nearest_part.Curve.parameter(neworigin)
            tangent = nearest_part.tangentAt(param)
            normal1 = dRay.cross(tangent)
            normal = tangent.cross(normal1)
            if normal.Length < EPSILON:
                return Vector(0, 0, 0)
            normal = normal / normal.Length

        elif hasattr(nearest_part, 'Surface'):
            uv = nearest_part.Surface.parameter(neworigin)
            normal = nearest_part.normalAt(uv[0], uv[1])
        else:
            return Vector(0, 0, 0)

        cosangle = dRay * normal / (dRay.Length * normal.Length)
        if cosangle < 0:
            normal = -normal

        return normal


    def mirror(self, dRay, normal):
        return 2 * normal * (dRay * normal) - dRay


    def snellsLaw(self, ray, n1, n2, normal):
        root = 1 - n1/n2 * n1/n2 * normal.cross(ray) * normal.cross(ray)
        if root < 0: # total reflection
            return self.mirror(ray, normal)
        return -n1/n2 * normal.cross( (-normal).cross(ray)) - normal * math.sqrt(root)

    def grating_calculation(self, grating_type, order, wavelength, lpm, ray, normal, g_g_p_vector, n1, n2): #from Ludwig 1970
        ### get parameters
        wavelength = wavelength/1000
        ray = ray / ray.Length
        surf_norma = -normal # the normal seems to be in ray direction so change this
        surf_norma = surf_norma/surf_norma.Length # normalize the surface normal
        g_g_p_vector = g_g_p_vector/g_g_p_vector.Length # hypothetical first vector determining the orientation of the grating rules. This vector is normal to a plane that would cause the rules by intersection with the surface of the grating.
        

        # print("Grating normal = ", normal)
        # print("ray = ", ray[0], ray[1], ray[2])
        # print("Grating normal = ", surf_norma)
        # print("wavelength= ", wavelength)
        # print("g_g_p_vector = ", g_g_p_vector)



        P = g_g_p_vector.cross(surf_norma)
        P = P/P.Length
        #print("P",P)
        D = surf_norma.cross(P)
        #print("D", D)
        D = D/D.Length    
        mu = n1/n2
        #print("mu", mu)
        d = 1000/lpm
        #print("d",d)
        T = (order*wavelength)/(n1*d)
        #print("T", T)
        #print("ray", ray[0], ray[1], ray[2])
        V = (mu*(ray[0]*surf_norma[0]+ray[1]*surf_norma[1]+ray[2]*surf_norma[2]))/surf_norma.dot(surf_norma)
        #print("V", V)
        W = (mu**2-1+T**2-2*mu*T*(ray[0]*D[0]+ray[1]*D[1]+ray[2]*D[2]))/surf_norma.dot(surf_norma)
        #print("W", W)
        #print("calc_test ", (ray[0]*D[0]+ray[1]*D[1]+ray[2]*D[2]))
        #print ("W>V**2? ", W>V**2)
        Q = ((-2*V+((2*V)**2-4*W)**0.5)/2,(-2*V-((2*V)**2-4*W)**0.5)/2)
        #print("Q",Q)

        if grating_type == 0: # reflection grating
            #S_ = mu*ray_trans-T*D+max(Q)*surf_norma_trans
            S_0 = mu*ray[0]-T*D[0]+max(Q)*surf_norma[0]
            S_1 = mu*ray[1]-T*D[1]+max(Q)*surf_norma[1]
            S_2 = mu*ray[2]-T*D[2]+max(Q)*surf_norma[2]
            S_=Vector(S_0,S_1,S_2)
        else: # transmission grating
            #S_ = mu*ray-T*D+min(Q)*surf_norma
            S_0 = mu*ray[0]-T*D[0]+min(Q)*surf_norma[0]
            S_1 = mu*ray[1]-T*D[1]+min(Q)*surf_norma[1]
            S_2 = mu*ray[2]-T*D[2]+min(Q)*surf_norma[2]
            S_=Vector(S_0,S_1,S_2)
            
        
        S_=-S_
        #print("S_", S_)
        return S_


    def check2D(self, objlist):
        nvec = Vector(1, 1, 1)
        for obj in objlist:
            bbox = obj.BoundBox
            if bbox.XLength > EPSILON: nvec.x = 0
            if bbox.YLength > EPSILON: nvec.y = 0
            if bbox.ZLength > EPSILON: nvec.z = 0

        return nvec


    def isInsideLens(self, isec_struct, origin, lens):
        for isec in isec_struct:
            if lens == isec[0]:
                return len(isec[1]) % 2 == 1

        return False


def PointVec(point):
    '''Converts a Part::Point to a FreeCAD::Vector'''
    return Vector(point.X, point.Y, point.Z)

def isOpticalObject(obj):
    return obj.TypeId == 'Part::FeaturePython' and hasattr(obj, 'OpticalType') and hasattr(obj, 'Base')


class BeamViewProvider:
    def __init__(self, vobj):
        '''Set this object to the proxy object of the actual view provider'''
        vobj.Proxy = self
        self.Object = vobj.Object

    def getIcon(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return os.path.join(OpticsTiboWB_icons_path, 'beam.svg')

    def attach(self, vobj):
        '''Setup the scene sub-graph of the view provider, this method is mandatory'''
        self.Object = vobj.Object
        self.onChanged(vobj, '')

    def updateData(self, fp, prop):
        '''If a property of the handled feature has changed we have the chance to handle this here'''
        #print('BeamViewProvider - updateData')
        #print('prop: ' + prop)
        pass

    def claimChildren(self):
        '''Return a list of objects that will be modified by this feature'''
        return []

    def onDelete(self, feature, subelements):
        '''Here we can do something when the feature will be deleted'''
        return True

    def onChanged(self, fp, prop):
        '''Here we can do something when a single property got changed'''
        #print('BeamViewProvider - onChanged')
        #print('prop: ' + prop)
        pass

    def __getstate__(self):
        '''When saving the document this object gets stored using Python's json module.\
                Since we have some un-serializable parts here -- the Coin stuff -- we must define this method\
                to return a tuple of all serializable objects or None.'''
        return None

    def __setstate__(self, state):
        '''When restoring the serialized object from document we have the chance to set some internals here.\
                Since no data were serialized nothing needs to be done here.'''
        return None

class EmitterViewProvider:
    def __init__(self, vobj):
        '''Set this object to the proxy object of the actual view provider'''
        vobj.Proxy = self
        self.Object = vobj.Object

    def getIcon(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return os.path.join(OpticsTiboWB_icons_path, 'emitter.svg')

    def attach(self, vobj):
        '''Setup the scene sub-graph of the view provider, this method is mandatory'''
        self.Object = vobj.Object
        self.onChanged(vobj, '')

    def updateData(self, fp, prop):
        '''If a property of the handled feature has changed we have the chance to handle this here'''
        print('EmitterViewProvider - updateData')
        print('prop: ' + prop)
        #fp.Base[0].Placement = fp.Placement
        #FreeCAD.ActiveDocument.recompute()
        pass

    def claimChildren(self):
        '''Return a list of objects that will be modified by this feature'''
        return self.Object.Base

    def onDelete(self, feature, subelements):
        '''Here we can do something when the feature will be deleted'''
        return True
    
    def doubleClicked(self, vobj):
        task_panel = test_functions.MyCustomTaskPanel(vobj.Object)
        Gui.Control.showDialog(task_panel)

        return True

    def onChanged(self, fp, prop):
        '''Here we can do something when a single property got changed'''
        print('EmitterViewProvider - onChanged')
        print('prop: ' + prop)
        pass

    def __getstate__(self):
        '''When saving the document this object gets stored using Python's json module.\
                Since we have some un-serializable parts here -- the Coin stuff -- we must define this method\
                to return a tuple of all serializable objects or None.'''
        return None

    def __setstate__(self, state):
        '''When restoring the serialized object from document we have the chance to set some internals here.\
                Since no data were serialized nothing needs to be done here.'''
        return None
    
