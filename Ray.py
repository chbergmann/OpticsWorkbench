# -*- coding: utf-8 -*-

__title__ = 'Ray'
__author__ = 'Christian Bergmann'
__license__ = 'LGPL 3.0'

import os
import FreeCADGui as Gui
from FreeCAD import Vector, Rotation, Placement, activeDocument
import Part
import math
import traceback
from wavelength_to_rgb.gentable import wavelen2rgb
import OpticalObject
import FreeCAD

translate = FreeCAD.Qt.translate


def QT_TRANSLATE_NOOP(context, text):
    return text


_icondir_ = os.path.join(os.path.dirname(__file__), 'icons')
__doc__ = QT_TRANSLATE_NOOP('Ray (monochrome)', 'A single ray for raytracing')

INFINITY = 1677216
EPSILON = 1 / INFINITY


class RayWorker:

    def __init__(
            self,
            fp,  # an instance of Part::FeaturePython
            power=True,
            spherical=False,
            beamNrColumns=1,
            beamNrRows=1,
            beamDistance=0.1,
            hideFirst=False,
            maxRayLength=1000000,
            maxNrReflections=200,
            wavelength=580,
            order=0,
            coneAngle=360,
            ignoredElements=[],
            baseShape=None):
        fp.addProperty(
            'App::PropertyBool', 'Spherical', 'Ray',
            translate(
                'Ray',
                'False=Beam in one direction, True=Radial or spherical rays')
        ).Spherical = spherical
        fp.addProperty('App::PropertyBool', 'Power', 'Ray',
                       translate('Ray', 'On or Off')).Power = power
        fp.addProperty(
            'App::PropertyIntegerConstraint', 'BeamNrColumns', 'Ray',
            translate(
                'Ray',
                'number of rays in a beam')).BeamNrColumns = beamNrColumns
        fp.addProperty(
            'App::PropertyIntegerConstraint', 'BeamNrRows', 'Ray',
            translate('Ray',
                      'number of rays in a beam')).BeamNrRows = beamNrRows
        fp.addProperty(
            'App::PropertyFloat', 'BeamDistance', 'Ray',
            translate(
                'Ray',
                'distance between two beams')).BeamDistance = beamDistance
        fp.addProperty(
            'App::PropertyBool', 'HideFirstPart', 'Ray',
            translate(
                'Ray',
                'hide the first part of every ray')).HideFirstPart = hideFirst
        fp.addProperty(
            'App::PropertyFloat', 'MaxRayLength', 'Ray',
            translate('Ray',
                      'maximum length of a ray')).MaxRayLength = maxRayLength
        fp.addProperty('App::PropertyIntegerConstraint', 'MaxNrReflections',
                       'Ray', translate('Ray', 'maximum number of reflections'
                                        )).MaxNrReflections = maxNrReflections
        fp.addProperty(
            'App::PropertyFloat', 'Wavelength', 'Ray',
            translate('Ray',
                      'Wavelength of the ray in nm')).Wavelength = wavelength
        fp.addProperty('App::PropertyIntegerConstraint', 'Order', 'Ray',
                       translate('Ray', 'Order of the ray')).Order = order
        fp.addProperty(
            'App::PropertyFloat', 'ConeAngle', 'Ray',
            translate('Ray', 'Angle of ray in case of Cone in degrees')
        ).ConeAngle = coneAngle
        fp.addProperty(
            'App::PropertyLinkList', 'IgnoredOpticalElements', 'Ray',
            translate('Ray', 'Optical Objects to ignore in raytracing')
        ).IgnoredOpticalElements = ignoredElements
        fp.addProperty(
            'App::PropertyLinkSub', 'Base', 'Ray',
            translate(
                'Ray',
                'FreeCAD object used as optical emitter')).Base = baseShape

        fp.Proxy = self
        self.lastRefIdx = []
        self.iter = 0

    def execute(self, fp):
        '''Do something when doing a recomputation, this method is mandatory'''
        self.redrawRay(fp)

    def onChanged(self, fp, prop):
        '''Do something when a property has changed'''
        if not hasattr(fp, 'Base'):
            fp.addProperty(
                'App::PropertyLinkSub', 'Base', 'Ray',
                translate('Ray',
                          'FreeCAD object used as optical emitter')).Base

    def redrawRay(self, fp):
        hitname = 'HitsFrom' + fp.Label
        hitcoordsname = 'HitCoordsFrom' + fp.Label
        energyname = 'EnergyFrom' + fp.Label
        for optobj in activeDocument().Objects:
            if hasattr(optobj, hitname):
                setattr(optobj, hitname, 0)
            if hasattr(optobj, hitcoordsname):
                setattr(optobj, hitcoordsname, [])
            if hasattr(optobj, energyname):
                setattr(optobj, energyname, [])

        try:  # check if the beam has the parameter coneAngle, this is a legacy check.
            coneAngle = float(fp.ConeAngle)
            if coneAngle > 360:
                coneAngle = 360  # cone angles larger than 360 are not possible, this is a sphere
        except:
            coneAngle = 360

        pl = fp.Placement
        posdirarray = []
        sunObj = None

        if fp.Base:
            fp.Placement = Placement()
            faces = []
            if len(fp.Base[1]) == 0:
                faces += fp.Base[0].Shape.Faces
            else:
                for sub in fp.Base[1]:
                    sobj = fp.Base[0].getSubObject(sub)
                    faces.append(sobj)

            sunObj = Part.makeCompound(faces)
            r2 = Rotation(fp.Placement.Rotation)
            r2.invert()
            sunObj.Placement.Rotation = r2

            posdirarray = self.getPosDirFromFaces(sunObj.Faces, fp.BeamNrRows,
                                                  fp.BeamNrColumns)

        # if a spherical 3d ray is requested create an evenly spaced ray bundle in 3d
        elif fp.Spherical == True and int(fp.BeamNrRows) > 1:
            # make spherical beam pattern that has equally spaced rays.
            # code based from a paper by Markus Deserno from the Max-Plank_Institut fur PolymerForschung,
            # link https://www.cmu.edu/biolphys/deserno/pdf/sphere_equi.pdf
            Ncount = 0  # create counter to check how many beams actually are generated
            N = int(fp.BeamNrColumns * fp.BeamNrRows)  # N = number of rays
            if N == 0:
                return
            r = 1  # use a unit circle with radius 1 to determine the direction vector of each ray
            # required surface area for each ray for a unit circle, by dividing the surface area of the unit circle by the number of rays
            a = 2 * math.pi * (1 - math.cos(math.radians(coneAngle / 2))) / N
            d = math.sqrt(a)  # dont know but it works :-p
            # Angle step between the circles on which the points are projected
            M_angle1 = math.radians(coneAngle / 2) / d
            # Quote from paper: Regular equidistribution can be achieved by choosing circles of latitude at constant intervals d_angle1 and on these circles points with distance d_angle2, such that d_angle1 roughly equal to d_angle2 and that d_angle1*d_angle2 equals the average area per point. This then gives the following algorithm:

            # calculate the distance between the circles of the latitude
            d_angle1 = math.radians(coneAngle / 2) / M_angle1
            # calculate the distance between the points on the circumference of the circle
            d_angle2 = a / d_angle1
            pos = Vector(0, 0, 0)
            for m in range(0, math.ceil(M_angle1)):
                r = Rotation()
                r.Axis = Vector(0, 0, 1)
                angle1 = math.radians(coneAngle / 2) * (m) / M_angle1
                M_angle2 = round(2 * math.pi * math.sin(angle1) / d_angle2)
                # if the beam is 2d, create only two points on the each projecting circle
                if int(fp.BeamNrRows) == 1:
                    M_angle2 = 2
                if M_angle2 == 0:  # if angle is 0 then set one ray in the vertical position
                    angle2 = 0
                    dir = Vector(
                        math.sin(angle1) * math.cos(angle2),
                        math.sin(angle1) * math.sin(angle2), math.cos(angle1))
                    Ncount = Ncount + 1
                    posdirarray.append((pos, dir))

                for n in range(0, M_angle2):
                    angle2 = 2 * math.pi * n / M_angle2
                    dir = Vector(
                        math.sin(angle1) * math.cos(angle2),
                        math.sin(angle1) * math.sin(angle2), math.cos(angle1))
                    Ncount = Ncount + 1

                    posdirarray.append((pos, dir))
            # print("Number of rays created = ",Ncount)

        else:
            for row in range(0, int(fp.BeamNrRows)):
                for n in range(0, int(fp.BeamNrColumns)):
                    if fp.Spherical == False:
                        pos = pl.Rotation.multVec(
                            Vector(0, fp.BeamDistance * n,
                                   fp.BeamDistance * row))
                        dir = Vector(1, 0, 0)
                    else:
                        r = Rotation()
                        r.Axis = Vector(0, 0, 1)
                        r.Angle = n * 2 * math.pi / fp.BeamNrColumns * coneAngle / 360
                        pos = Vector(0, 0, 0)
                        dir1 = r.multVec(Vector(1, 0, 0))

                        if row % 2 == 0:
                            r.Axis = Vector(0, 1, 0)
                        else:
                            r.Axis = Vector(1, 0, 0)

                        r.Angle = row * math.pi / fp.BeamNrRows
                        dir = r.multVec(dir1)

                    posdirarray.append((pos, dir))

        linearray = self.makeInitialRay(fp, posdirarray)

        for line in linearray:
            self.substractPlacement(fp, line)

        if sunObj:
            linearray.append(sunObj)

        # transform global ray coordinate to local
        if fp.Parents:
            ray_placement_matrix = fp.getGlobalPlacement().inverse().Matrix
            ray_placement_matrix *= fp.Placement.Matrix
            for line in linearray:
                line.transformShape(ray_placement_matrix)
        fp.Shape = Part.makeCompound(linearray)
        if fp.Power == False:
            fp.ViewObject.LineColor = (0.5, 0.5, 0.0)
        else:
            try:
                rgb = wavelen2rgb(fp.Wavelength)
            except ValueError:
                # set color to white if outside of visible range
                rgb = (255, 255, 255)
            r = rgb[0] / 255.0
            g = rgb[1] / 255.0
            b = rgb[2] / 255.0
            fp.ViewObject.LineColor = (float(r), float(g), float(b), (0.0))

    def substractPlacement(self, fp, obj):
        r2 = Rotation(fp.Placement.Rotation)
        r2.invert()
        obj.Placement.Rotation = r2
        obj.Placement.Base = r2.multVec(obj.Placement.Base - fp.Placement.Base)

    def getPosDirFromFaces(self, subShapes, BeamNrRows, BeamNrColumns):
        posdirarray = []
        for face in subShapes:
            for row in range(0, int(BeamNrRows)):
                for col in range(0, int(BeamNrColumns)):
                    if len(face.ParameterRange) == 4:
                        param1 = face.ParameterRange[0] + (
                            face.ParameterRange[1] -
                            face.ParameterRange[0]) * (row + 0.5) / BeamNrRows
                        param2 = face.ParameterRange[2] + (
                            face.ParameterRange[3] - face.ParameterRange[2]
                        ) * (col + 0.5) / BeamNrColumns
                        newdir = face.normalAt(param1, param2)
                        newpos = face.valueAt(param1, param2)
                        v = Part.Vertex(newpos)
                        if face.distToShape(v)[0] < EPSILON:
                            posdirarray.append((newpos, newdir))
                    elif len(face.ParameterRange) == 2:
                        param1 = face.ParameterRange[0] + (
                            face.ParameterRange[1] -
                            face.ParameterRange[0]) * (row + 0.5) / BeamNrRows
                        try:
                            newdir = face.normalAt(param1)
                        except:
                            newdir = Vector(1, 0, 0)

                        newpos = face.valueAt(param1)
                        posdirarray.append((newpos, newdir))

        return posdirarray

    def makeInitialRay(self, fp, posdirarray):
        # initialize ray in global coordinate
        pl = fp.getGlobalPlacement()
        linearray = []
        for (pos, dir) in posdirarray:
            ppos = pos + pl.Base
            pdir = pl.Rotation.multVec(dir)
            if fp.Power == True:
                self.iter = fp.MaxNrReflections
                firstLine = Part.makeLine(
                    ppos, ppos + pdir * fp.MaxRayLength / pdir.Length)

                self.lastRefIdx = []

                try:
                    tracedLines = self.traceRay(fp, (firstLine, 100))

                    if fp.HideFirstPart:
                        # Remove/hide first line.
                        tracedLines = tracedLines[1:]

                    linearray.extend(tracedLines)

                except Exception as ex:
                    print(ex)
                    traceback.print_exc()
            else:
                linearray.append(Part.makeLine(ppos, ppos + pdir))

        return linearray

    def getIntersections(self, fp, line):
        '''returns [(OpticalObject, [(edge/face, intersection point)] )]'''
        isec_struct = []
        for optobj in activeDocument().Objects:
            if isRelevantOptic(fp, optobj):
                # transform ray to optobj coordinate to prevent transforming all shapes to global coordinate
                optobj_placement_matrix = optobj.getGlobalPlacement().Matrix
                optobj_line = line.transformed(optobj_placement_matrix.inverse())
                origin = PointVec(optobj_line.Vertexes[0])
                dir = PointVec(optobj_line.Vertexes[1]) - origin
                isec_parts = []
                for obj in optobj.Base:
                    obj_boundbox = obj.Shape.BoundBox
                    if obj_boundbox.isValid() and obj_boundbox.intersect(origin, dir):
                        if len(obj.Shape.Solids) == 0 and len(
                                obj.Shape.Shells) == 0:
                            for edge in obj.Shape.Edges:
                                # get a normal to the plane where the edge is lying in
                                if (len(edge.Vertexes) == 2):
                                    edgedir = PointVec(
                                        edge.Vertexes[1]) - PointVec(
                                            edge.Vertexes[0])
                                else:
                                    # workaround for circles
                                    edgedir = edge.valueAt(0) - edge.valueAt(
                                        0.5)

                                normal = dir.cross(edgedir)
                                if normal.Length > EPSILON:
                                    plane = Part.Plane(origin, normal)
                                    isec = optobj_line.Curve.intersect2d(
                                        edge.Curve, plane)
                                    if isec:
                                        for p in isec:
                                            p2 = plane.value(p[0], p[1])
                                            dist = p2 - origin
                                            vert = Part.Vertex(p2)
                                            if dist.Length > EPSILON and vert.distToShape(
                                                    edge
                                            )[0] < EPSILON and vert.distToShape(
                                                    optobj_line)[0] < EPSILON:
                                                # transform edge and ray back to global coordinate
                                                vert.transformShape(optobj_placement_matrix)
                                                p2 = PointVec(vert)
                                                edge.transformShape(optobj_placement_matrix)
                                                isec_parts.append((edge, p2))

                        for face in obj.Shape.Faces:
                            if face.BoundBox.intersect(origin, dir):
                                isec = optobj_line.Curve.intersect(face.Surface)
                                if isec:
                                    for p in isec[0]:
                                        dist = Vector(p.X - origin.x,
                                                      p.Y - origin.y,
                                                      p.Z - origin.z)
                                        vert = Part.Vertex(p)
                                        if dist.Length > EPSILON and vert.distToShape(
                                                face
                                        )[0] < EPSILON and vert.distToShape(
                                                optobj_line)[0] < EPSILON:
                                            # transform face and ray back to global coordinate
                                            p.transform(optobj_placement_matrix)
                                            face.transformShape(optobj_placement_matrix)
                                            isec_parts.append(
                                                (face, PointVec(p)))

                if len(isec_parts) > 0:
                    isec_struct.append((optobj, isec_parts))

        return isec_struct

    def collectStatistics(self, fp, nearest_obj, neworigin, energy):
        hitname = 'HitsFrom' + fp.Label
        if not hasattr(nearest_obj, hitname):
            nearest_obj.addProperty(
                'App::PropertyQuantity', hitname, 'OpticalObject',
                translate('Ray', 'Counts the hits from') + ' ' +
                fp.Label + ' (' + translate('Ray', 'read only') + ')')
            setattr(nearest_obj, hitname, 1)
        else:
            setattr(nearest_obj, hitname,
                    getattr(nearest_obj, hitname) + 1)

        # print("A RAY coming from", fp.Label, "hits the receiver at", tuple(neworigin))
        hitcoordsname = 'HitCoordsFrom' + fp.Label
        if not hasattr(nearest_obj, hitcoordsname):
            nearest_obj.addProperty(
                'App::PropertyVectorList', hitcoordsname,
                'OpticalObject',
                translate('Ray', 'Hit coordinates from') + ' ' +
                fp.Label + ' (' + translate('Ray', 'read only') + ')')
            setattr(nearest_obj, hitcoordsname, [])
        setattr(nearest_obj, hitcoordsname,
                getattr(nearest_obj, hitcoordsname) + [neworigin])

        energyname = 'EnergyFrom' + fp.Label
        if not hasattr(nearest_obj, energyname):
            nearest_obj.addProperty(
                'App::PropertyFloatList', energyname,
                'OpticalObject',
                translate('Ray', 'Energy from') + ' ' +
                fp.Label + ' (' + translate('Ray', 'read only') + ')')
            setattr(nearest_obj, energyname, [])
        setattr(nearest_obj, energyname,
                getattr(nearest_obj, energyname) + [energy])

    def traceLens(self, fp, nearest_obj, ray1, normal, isec_struct, origin):
        if len(self.lastRefIdx) == 0:
            oldRefIdx = 1
        else:
            oldRefIdx = self.lastRefIdx[len(self.lastRefIdx) - 1]

        if len(self.lastRefIdx) < 2:
            newRefIdx = 1
        else:
            newRefIdx = self.lastRefIdx[len(self.lastRefIdx) - 2]

        if len(nearest_obj.Sellmeier) == 6:
            n = OpticalObject.refraction_index_from_sellmeier(
                fp.Wavelength, nearest_obj.Sellmeier)
        else:
            n = nearest_obj.RefractionIndex

        if self.isInsideLens(isec_struct, origin, nearest_obj):
            # print("leave " + nearest_obj.Label)
            oldRefIdx = n
            if len(self.lastRefIdx) > 0:
                self.lastRefIdx.pop(len(self.lastRefIdx) - 1)
            # print()
        else:
            # print("enter " + nearest_obj.Label)
            newRefIdx = n
            self.lastRefIdx.append(n)

        return self.snellsLaw(ray1, oldRefIdx, newRefIdx, normal)

    def traceGrating(self, fp, nearest_obj, ray1, normal, isec_struct, origin):
        g = None
        doLens = False

        if len(self.lastRefIdx) == 0:
            oldRefIdx = 1
        else:
            oldRefIdx = self.lastRefIdx[len(self.lastRefIdx) - 1]

        if len(self.lastRefIdx) < 2:
            newRefIdx = 1
        else:
            newRefIdx = self.lastRefIdx[len(self.lastRefIdx) - 2]

        if len(nearest_obj.Sellmeier) == 6:
            n = OpticalObject.refraction_index_from_sellmeier(
                fp.Wavelength, nearest_obj.Sellmeier)
        else:
            n = nearest_obj.RefractionIndex

        lpm = nearest_obj.lpm
        grating_lines_plane = nearest_obj.GratingLinesPlane

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

        if grating_type == 0:  # reflection grating
            g = self.grating_calculation(grating_type, order,
                                         fp.Wavelength, lpm, ray1,
                                         normal, grating_lines_plane,
                                         oldRefIdx, oldRefIdx)

        elif grating_type == 2:  # transmission grating with diffraction at first surface
            if self.isInsideLens(isec_struct, origin, nearest_obj):
                doLens = True
                # print("leave t-grating 1s " + nearest_obj.Label)
                oldRefIdx = n
                # print("old RefIdx: ", oldRefIdx, "new RefIdx: ", newRefIdx)
                if len(self.lastRefIdx) > 0:
                    self.lastRefIdx.pop(len(self.lastRefIdx) - 1)
            else:
                newRefIdx = n
                self.lastRefIdx.append(n)
                # print("enter t-grating 1s " + nearest_obj.Label)
                # print("old RefIdx: ", oldRefIdx, "new RefIdx: ", newRefIdx)
                g = self.grating_calculation(grating_type, order,
                                             fp.Wavelength, lpm, ray1,
                                             normal,
                                             grating_lines_plane,
                                             oldRefIdx, newRefIdx)

        elif grating_type == 1:  # transmission grating with diffraction at second surface
            if self.isInsideLens(isec_struct, origin, nearest_obj):
                # print("leave t-grating 2s " + nearest_obj.Label)
                oldRefIdx = n
                # print("old RefIdx: ", oldRefIdx, "new RefIdx: ", newRefIdx)
                g = self.grating_calculation(grating_type, order,
                                             fp.Wavelength, lpm, ray1,
                                             normal,
                                             grating_lines_plane,
                                             oldRefIdx, newRefIdx)
            else:
                doLens = True
                newRefIdx = n
                self.lastRefIdx.append(n)
                # print("enter t-grating 2s " + nearest_obj.Label)
                # print("old RefIdx: ", oldRefIdx, "new RefIdx: ", newRefIdx)

        if doLens:
            return self.snellsLaw(ray1, oldRefIdx, newRefIdx, normal)

        return (g, False)

    def traceRay(self, fp, lineAndEnergy):
        nearest = Vector(INFINITY, INFINITY, INFINITY)
        nearest_parts = []
        line = lineAndEnergy[0]
        energy = lineAndEnergy[1]

        isec_struct = self.getIntersections(fp, line)
        origin = PointVec(line.Vertexes[0])

        for isec in isec_struct:
            for ipoints in isec[1]:
                dist = ipoints[1] - origin
                if dist.Length <= nearest.Length + EPSILON:
                    np = (ipoints[1], ipoints[0], isec[0])
                    if abs(dist.Length - nearest.Length) < EPSILON:
                        if isec[0].OpticalType == 'absorber':
                            nearest_parts = [np]
                        elif len(nearest_parts) == 0 or nearest_parts[0].OpticalType == 'absorber':
                            nearest_parts.append(np)
                    else:
                        nearest_parts = [np]

                    nearest = dist

        if len(nearest_parts) == 0:
            return [line]

        dNewRays = []  # Collects all new ray directions
        for np in nearest_parts:
            (neworigin, nearest_part, nearest_obj) = np
            shortline = Part.makeLine(origin, neworigin)

            if isRelevantOptic(fp, nearest_obj) and nearest_obj.collectStatistics:
                self.collectStatistics(fp, nearest_obj, neworigin, energy)

            # if fp.HideFirstPart == False or first == False:
            # When it is the first part that shall be hidden, linearray[-1]
            # was already removed at this point
            # linearray[-1] = shortline

            # The current line ends at the surface of the current optical
            # element.
            ret = [shortline]

            self.iter -= 1
            if self.iter == 0:
                return ret

            # Compute a new ray that follows --depending on the current optical
            # element-- reflection, refraction or diffraction.
            dRay = neworigin - origin
            ray1 = dRay / dRay.Length

            if hasattr(nearest_obj, 'Transparency'):
                P_pass = energy * (nearest_obj.Transparency) / 100
                P_reflect = energy * (100 - nearest_obj.Transparency) / 100
            else:
                P_pass = energy
                P_reflect = 0

            normal = self.getNormal(nearest_obj, nearest_part, origin,
                                    neworigin)
            if normal.Length == 0:
                print('Cannot determine the normal on ' + nearest_obj.Label)
                return ret

            if nearest_obj.OpticalType == 'mirror':
                if nearest_obj.Transparency < 100:
                    dNewRays.append((self.mirror(dRay, normal), P_reflect))

            if nearest_obj.OpticalType == 'mirror' or nearest_obj.OpticalType == 'absorber':
                if nearest_obj.Transparency > 0:
                    if self.isInsideSolid(origin, nearest_obj):
                        P_pass = energy
                        
                    dNewRays.append((-dRay, P_pass))

            elif nearest_obj.OpticalType == 'lens':
                (newray, totalReflection) = self.traceLens(fp, nearest_obj, ray1, normal, isec_struct, origin)
                if self.isInsideLens(isec_struct, origin, nearest_obj):
                    P_pass = energy
                elif nearest_obj.Transparency < 100 and not totalReflection:
                    dNewRays.append((self.mirror(dRay, normal), P_reflect))

                dNewRays.append((newray, P_pass))            

            elif nearest_obj.OpticalType == 'grating':
                (newray, totalReflection) = self.traceGrating(
                    fp, nearest_obj, ray1, normal, isec_struct, origin)
                dNewRays.append((newray, P_pass))

            else:
                return ret

        newlines = []
        for dNewRay in dNewRays:
            nl = Part.makeLine(
                neworigin,
                neworigin - dNewRay[0] * fp.MaxRayLength / dNewRay[0].Length)
            newlines.append((nl, dNewRay[1]))

        for line in newlines:
            ret.extend(self.traceRay(fp, line))

        return ret

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
        root = 1 - n1 / n2 * n1 / n2 * normal.cross(ray) * normal.cross(ray)
        if root < 0:  # total reflection
            return (self.mirror(ray, normal), True)

        refractedRay = -n1 / n2 * normal.cross(
            (-normal).cross(ray)) - normal * math.sqrt(root)

        return (refractedRay, False)

    def grating_calculation(self, grating_type, order, wavelength, lpm, ray,
                            normal, g_g_p_vector, n1, n2):  # from Ludwig 1970
        # get parameters
        wavelength = wavelength / 1000
        ray = ray / ray.Length
        surf_norma = -normal  # the normal seems to be in ray direction so change this
        surf_norma = surf_norma / surf_norma.Length  # normalize the surface normal
        # hypothetical first vector determining the orientation of the grating rules. This vector is normal to a plane that would cause the rules by intersection with the surface of the grating.
        g_g_p_vector = g_g_p_vector / g_g_p_vector.Length

        # print("Grating normal = ", normal)
        # print("ray = ", ray[0], ray[1], ray[2])
        # print("Grating normal = ", surf_norma)
        # print("wavelength= ", wavelength)
        # print("g_g_p_vector = ", g_g_p_vector)

        P = g_g_p_vector.cross(surf_norma)
        P = P / P.Length
        # print("P",P)
        D = surf_norma.cross(P)
        # print("D", D)
        D = D / D.Length
        mu = n1 / n2
        # print("mu", mu)
        d = 1000 / lpm
        # print("d",d)
        T = (order * wavelength) / (n1 * d)
        # print("T", T)
        # print("ray", ray[0], ray[1], ray[2])
        V = (mu * (ray[0] * surf_norma[0] + ray[1] * surf_norma[1] +
                   ray[2] * surf_norma[2])) / surf_norma.dot(surf_norma)
        # print("V", V)
        W = (mu**2 - 1 + T**2 - 2 * mu * T *
             (ray[0] * D[0] + ray[1] * D[1] + ray[2] * D[2])
             ) / surf_norma.dot(surf_norma)
        # print("W", W)
        # print("calc_test ", (ray[0]*D[0]+ray[1]*D[1]+ray[2]*D[2]))
        # print ("W>V**2? ", W>V**2)
        Q = ((-2 * V + ((2 * V)**2 - 4 * W)**0.5) / 2,
             (-2 * V - ((2 * V)**2 - 4 * W)**0.5) / 2)
        # print("Q",Q)

        if grating_type == 0:  # reflection grating
            # S_ = mu*ray_trans-T*D+max(Q)*surf_norma_trans
            S_0 = mu * ray[0] - T * D[0] + max(Q) * surf_norma[0]
            S_1 = mu * ray[1] - T * D[1] + max(Q) * surf_norma[1]
            S_2 = mu * ray[2] - T * D[2] + max(Q) * surf_norma[2]
            S_ = Vector(S_0, S_1, S_2)
        else:  # transmission grating
            # S_ = mu*ray-T*D+min(Q)*surf_norma
            S_0 = mu * ray[0] - T * D[0] + min(Q) * surf_norma[0]
            S_1 = mu * ray[1] - T * D[1] + min(Q) * surf_norma[1]
            S_2 = mu * ray[2] - T * D[2] + min(Q) * surf_norma[2]
            S_ = Vector(S_0, S_1, S_2)

        S_ = -S_
        # print("S_", S_)
        return S_

    def check2D(self, objlist):
        nvec = Vector(1, 1, 1)
        for obj in objlist:
            bbox = obj.BoundBox
            if bbox.XLength > EPSILON:
                nvec.x = 0
            if bbox.YLength > EPSILON:
                nvec.y = 0
            if bbox.ZLength > EPSILON:
                nvec.z = 0

        return nvec

    def isInsideSolid(self, origin, lens):
        lens_placement_matrix = lens.getGlobalPlacement().Matrix
        origin = lens_placement_matrix.inverse().multVec(origin)
        for b in lens.Base:
            for sol in b.Shape.Solids:
                if sol.isInside(origin, EPSILON, True):
                    return True
                
        return False
                
    def isInsideLens(self, isec_struct, origin, lens):
        lens_placement_matrix = lens.getGlobalPlacement().Matrix
        origin = lens_placement_matrix.inverse().multVec(origin)
        nr_solids = 0
        for b in lens.Base:
            for sol in b.Shape.Solids:
                nr_solids += 1
                if sol.isInside(origin, EPSILON, True):
                    return True

        if nr_solids == 0:
            for isec in isec_struct:
                if lens == isec[0]:                    
                    return len(isec[1]) % 2 == 1

        return False


def PointVec(point):
    '''Converts a Part::Point to a FreeCAD::Vector'''
    return Vector(point.X, point.Y, point.Z)


def isOpticalObject(obj):
    return obj.TypeId == 'Part::FeaturePython' and hasattr(
        obj, 'OpticalType') and hasattr(obj, 'Base')


def isRelevantOptic(fp, obj):
    '''Determine if given object is a workbench optical component and if it should be considered in the ray calculation'''
    if hasattr(fp, "IgnoredOpticalElements"):
        return (isOpticalObject(obj)
                and (obj not in fp.IgnoredOpticalElements))

    # for older documents where rays do not have the IgnoredOpticalElements field we
    # will just return the old function, which checks only if the object is of "OpticalType"
    return isOpticalObject(obj)


class RayViewProvider:

    def __init__(self, vobj):
        '''Set this object to the proxy object of the actual view provider'''
        vobj.Proxy = self
        self.Object = vobj.Object

    def getIcon(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        if self.Object.Base:
            return os.path.join(_icondir_, 'emitter.svg')
        if self.Object.BeamNrColumns * self.Object.BeamNrRows <= 1:
            return os.path.join(_icondir_, 'ray.svg')
        elif self.Object.Spherical:
            return os.path.join(_icondir_, 'sun.svg')
        else:
            return os.path.join(_icondir_, 'rayarray.svg')

    def attach(self, vobj):
        '''Setup the scene sub-graph of the view provider, this method is mandatory'''
        self.Object = vobj.Object
        self.onChanged(vobj, 'Power')

    def updateData(self, fp, prop):
        '''If a property of the handled feature has changed we have the chance to handle this here'''
        pass

    def claimChildren(self):
        '''Return a list of objects that will be modified by this feature'''
        if not self.Object.Base:
            return []

        return self.Object.Base

    def onDelete(self, feature, subelements):
        '''Here we can do something when the feature will be deleted'''
        return True

    def onChanged(self, fp, prop):
        '''Here we can do something when a single property got changed'''
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


class Ray():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''

    def Activated(self):
        '''Will be called when the feature is executed.'''
        # Generate commands in the FreeCAD python console to create Ray
        Gui.doCommand('import OpticsWorkbench')
        Gui.doCommand('OpticsWorkbench.makeRay()')

    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if activeDocument():
            return (True)
        else:
            return (False)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {
            'Pixmap': os.path.join(_icondir_, 'ray.svg'),
            'Accel': '',  # a default shortcut (optional)
            'MenuText': QT_TRANSLATE_NOOP('Ray (monochrome)',
                                          'Ray (monochrome)'),
            'ToolTip': __doc__
        }


class RaySun():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''

    def Activated(self):
        '''Will be called when the feature is executed.'''
        # Generate commands in the FreeCAD python console to create Ray
        Gui.doCommand('import OpticsWorkbench')
        Gui.doCommand('OpticsWorkbench.makeSunRay()')

    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if activeDocument():
            return (True)
        else:
            return (False)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {
            'Pixmap':
            os.path.join(_icondir_, 'raysun.svg'),
            'Accel':
            '',  # a default shortcut (optional)
            'MenuText':
            QT_TRANSLATE_NOOP('Ray (sun light)', 'Ray (sun light)'),
            'ToolTip':
            QT_TRANSLATE_NOOP(
                'Ray (sun light)',
                'A bunch of rays with different wavelengths of visible light')
        }


class Beam2D():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''

    def Activated(self):
        '''Will be called when the feature is executed.'''
        # Generate commands in the FreeCAD python console to create Ray
        Gui.doCommand('import OpticsWorkbench')
        Gui.doCommand(
            'OpticsWorkbench.makeRay(beamNrColumns=50, beamDistance=0.1)')

    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if activeDocument():
            return (True)
        else:
            return (False)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {
            'Pixmap':
            os.path.join(_icondir_, 'rayarray.svg'),
            'Accel':
            '',  # a default shortcut (optional)
            'MenuText':
            QT_TRANSLATE_NOOP('Beam', '2D Beam'),
            'ToolTip':
            QT_TRANSLATE_NOOP('Beam', 'A row of multiple rays for raytracing')
        }


class RadialBeam2D():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''

    def Activated(self):
        '''Will be called when the feature is executed.'''
        # Generate commands in the FreeCAD python console to create Ray
        Gui.doCommand('import OpticsWorkbench')
        Gui.doCommand(
            'OpticsWorkbench.makeRay(beamNrColumns=64, spherical=True)')

    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if activeDocument():
            return (True)
        else:
            return (False)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {
            'Pixmap':
            os.path.join(_icondir_, 'sun.svg'),
            'Accel':
            '',  # a default shortcut (optional)
            'MenuText':
            QT_TRANSLATE_NOOP('2D Radial Beam', '2D Radial Beam'),
            'ToolTip':
            QT_TRANSLATE_NOOP(
                '2D Radial Beam',
                'Rays coming from one point going to all directions in a 2D plane'
            )
        }


class SphericalBeam():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''

    def Activated(self):
        '''Will be called when the feature is executed.'''
        # Generate commands in the FreeCAD python console to create Ray
        Gui.doCommand('import OpticsWorkbench')
        Gui.doCommand(
            'OpticsWorkbench.makeRay(beamNrColumns=8, beamNrRows=8, spherical=True)'
        )

    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if activeDocument():
            return (True)
        else:
            return (False)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {
            'Pixmap':
            os.path.join(_icondir_, 'sun3D.svg'),
            'Accel':
            '',  # a default shortcut (optional)
            'MenuText':
            QT_TRANSLATE_NOOP('Spherical Beam', 'Spherical Beam'),
            'ToolTip':
            QT_TRANSLATE_NOOP(
                'Spherical Beam',
                'Rays coming from one point going to all directions')
        }


class RedrawAll():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''

    def Activated(self):
        '''Will be called when the feature is executed.'''
        # Generate commands in the FreeCAD python console to create Ray
        Gui.doCommand('import OpticsWorkbench')
        Gui.doCommand('OpticsWorkbench.restartAll()')

    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if activeDocument():
            return (True)
        else:
            return (False)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {
            'Pixmap': os.path.join(_icondir_, 'Anonymous_Lightbulb_Lit.svg'),
            'Accel': '',  # a default shortcut (optional)
            'MenuText': QT_TRANSLATE_NOOP('Start', '(Re)start simulation'),
            'ToolTip': QT_TRANSLATE_NOOP('Start', '(Re)start simulation')
        }


class AllOff():
    '''This class will be loaded when the workbench is activated in FreeCAD. You must restart FreeCAD to apply changes in this class'''

    def Activated(self):
        '''Will be called when the feature is executed.'''
        # Generate commands in the FreeCAD python console to create Ray
        Gui.doCommand('import OpticsWorkbench')
        Gui.doCommand('OpticsWorkbench.allOff()')

    def IsActive(self):
        '''Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional.'''
        if activeDocument():
            return (True)
        else:
            return (False)

    def GetResources(self):
        '''Return the icon which will appear in the tree view. This method is optional and if not defined a default icon is shown.'''
        return {
            'Pixmap': os.path.join(_icondir_, 'Anonymous_Lightbulb_Off.svg'),
            'Accel': '',  # a default shortcut (optional)
            'MenuText': QT_TRANSLATE_NOOP('Off', 'Switch off lights'),
            'ToolTip': QT_TRANSLATE_NOOP('Off',
                                         'Switch off all rays and beams')
        }


Gui.addCommand('Ray (monochrome)', Ray())
Gui.addCommand('Ray (sun light)', RaySun())
Gui.addCommand('Beam', Beam2D())
Gui.addCommand('2D Radial Beam', RadialBeam2D())
Gui.addCommand('Spherical Beam', SphericalBeam())
Gui.addCommand('Start', RedrawAll())
Gui.addCommand('Off', AllOff())
