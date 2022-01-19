# -*- coding: utf8 -*-
# ****************************************************************************
# *                                                                          *
# *   Printed Circuit Board Workbench for FreeCAD             PCB            *
# *                                                                          *
# *   Copyright (c) 2013-2019                                                *
# *   marmni <marmni@onet.eu>                                                *
# *                                                                          *
# *                                                                          *
# *   This program is free software; you can redistribute it and/or modify   *
# *   it under the terms of the GNU Lesser General Public License (LGPL)     *
# *   as published by the Free Software Foundation; either version 2 of      *
# *   the License, or (at your option) any later version.                    *
# *   for detail see the LICENCE text file.                                  *
# *                                                                          *
# *   This program is distributed in the hope that it will be useful,        *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of         *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          *
# *   GNU Library General Public License for more details.                   *
# *                                                                          *
# *   You should have received a copy of the GNU Library General Public      *
# *   License along with this program; if not, write to the Free Software    *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307   *
# *   USA                                                                    *
# *                                                                          *
# ****************************************************************************

import FreeCAD
import Part
import OpenSCAD2Dgeom
from math import degrees, atan2
#
from PCBfunctions import sketcherGetGeometry


def getHoles():
    holes = {}
    #
    pcb = getPCBheight()
    if pcb[0]:  # board is available
        board = sketcherGetGeometry(pcb[2].Holes)
        if board[0]:
            for i in board[1]:
                if i['type'] == 'circle':
                    if not i["r"] in holes.keys():
                        holes[i["r"]] = []
                    #
                    holes[i["r"]].append([i["x"], i["y"]])
    #
    return holes


def getPCBheight():
    if not FreeCAD.activeDocument():
        return [False, 0]
    #
    try:
        pcbH = FreeCAD.ActiveDocument.Board.Thickness
        return [True, pcbH, FreeCAD.ActiveDocument.Board]
    except:
        return [False, False, None]


def getPCBsize():
    if not FreeCAD.activeDocument():
        return [0, 0, 0, 0]
    #
    try:
        board = FreeCAD.ActiveDocument.Board
        #
        minX = board.Shape.BoundBox.XMin
        minY = board.Shape.BoundBox.YMin
        XLength = board.Shape.BoundBox.XLength
        YLength = board.Shape.BoundBox.YLength
        #
        return [minX, minY, XLength, YLength]
    except:
        return [0, 0, 0, 0]


def cutToBoardShape(pads):
    if not FreeCAD.activeDocument():
        return pads
    #
    pcb = getPCBheight()
    if pcb[0]:  # board is available
        # cut to board shape
        board = OpenSCAD2Dgeom.edgestofaces(pcb[2].Border.Shape.Edges)
        # board = FreeCAD.ActiveDocument.Board.Border.Shape
        # board = Part.Face(board)
        board = board.extrude(FreeCAD.Base.Vector(0, 0, pcb[2].Thickness + 2))
        board.Placement.Base.z = -1
        # Part.show(board)
        pads = board.common(pads)
        return pads
    #
    return pads


def addObject(self, obj):
    self.Group += [obj]


class PCBboardObject:
    def __init__(self, obj):
        self.Type = 'PCBboard'
        obj.setEditorMode("Placement", 2)
        obj.setEditorMode("Label", 2)
        #  board
        obj.addProperty("App::PropertyFloatConstraint", "Thickness", "PCB", "Thickness").Thickness = (1.6, 0.5, 10, 0.5)
        obj.addProperty("App::PropertyLink", "Border", "PCB", "Border")
        #  holes
        obj.addProperty("App::PropertyBool", "Display", "Holes", "Display").Display = True
        obj.addProperty("App::PropertyLink", "Holes", "Holes", "Holes")
        #  base
        obj.addProperty("App::PropertyBool", "AutoUpdate", "Base", "Auto Update").AutoUpdate = True
        obj.addProperty("App::PropertyLinkList", "Group", "Base", "Group")
        obj.addProperty("App::PropertyLinkHidden", "Parent", "Base", "Parent", 1)
        # obj.addExtension("Part::AttachExtensionPython", obj)
        #
        self.holesComp = None
        obj.Proxy = self
        # obj.addObject = addObject

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state
            self.holesComp = None

    def addObject(self, fp, obj):
        fp.Group += [obj]

    def onChanged(self, fp, prop):
        fp.setEditorMode("Placement", 2)
        fp.setEditorMode("Label", 2)
        #
        if prop == "Shape":
            self.getHoles(fp)
            self.updateObjectaHoles(fp)
        #
        if fp.AutoUpdate is True:
            # if prop == "Thickness" or prop == "Border" or prop == "Holes" or prop == "Display" or prop == "Cut":
                # self.execute(fp)
            # elif prop == "AutoUpdate":
                # self.execute(fp)
            # if prop == "Shape" or prop == "Holes" or prop == "AutoUpdate" or prop == "Cut" and fp.Display:
                # self.updateObjectaHoles(fp)
            if prop == "Thickness" or prop == "AutoUpdate":
                self.updatePosition_Z(fp)
        else:
            if prop == "Thickness":
                self.execute(fp)

    def updateObjectaHoles(self, fp):
        for i in fp.Group:
            try:
                i.Proxy.updateHoles(i)
            except Exception as e:
                pass

    def updatePosition_Z(self, fp):
        if fp.Thickness < 0.5:
            fp.Thickness = 0.5
        #
        for i in fp.Group:
            try:
                i.Proxy.updatePosition_Z(i, fp.Thickness)
                i.purgeTouched()
            except:
                pass

    def getHoles(self, fp):
        try:
            holes = []
            for i in fp.Holes.Shape.Wires:
                holes.append(Part.Face(i))
            if len(holes):
                holes = Part.makeCompound(holes)
                self.holesComp = holes
        except:
            self.holesComp = None

    def execute(self, fp):
        try:
            if fp.Border is None or fp.Holes is None:
                return
            # elif not fp.AutoUpdate:
                # return
            #
            if fp.Thickness < 0.5:
                fp.Thickness = 0.5
            #
            try:
                self.oldHeight = fp.Shape.BoundBox.ZMax
            except:
                self.oldHeight = 0

            face = OpenSCAD2Dgeom.edgestofaces(fp.Border.Shape.Edges)
            ############################################################
            # BASED ON  realthunder PROPOSAL/SOLUTION
            ############################################################
            try:
                holes = None
                if fp.Display is True:
                    self.getHoles(fp)
                    if self.holesComp is not None:
                        face = face.cut(self.holesComp)
            except Exception as e:
                FreeCAD.Console.PrintWarning("3. {0}\n".format(e))
            ############################################################
            fp.Shape = face.extrude(FreeCAD.Base.Vector(0, 0, fp.Thickness))
            #
            try:
                fp.purgeTouched()
            except:
                pass
        except:
            pass


class viewProviderPCBboardObject:
    def __init__(self, obj):
        ''' Set this object to the proxy object of the actual view provider '''
        obj.Proxy = self

    def getDisplayModes(self, vobj):
        return ["Shaded"]

    def getDefaultDisplayMode(self):
        return "Shaded"

    def attach(self, obj):
        ''' Setup the scene sub-graph of the view provider, this method is mandatory '''
        self.Object = obj.Object

    def claimChildren(self):
        return [self.Object.Border, self.Object.Holes]

    def onChanged(self, vp, prop):
        ''' Print the name of the property that has changed '''
        vp.setEditorMode("LineColor", 2)
        vp.setEditorMode("DrawStyle", 2)
        vp.setEditorMode("LineWidth", 2)
        vp.setEditorMode("PointColor", 2)
        vp.setEditorMode("PointSize", 2)
        vp.setEditorMode("Deviation", 2)
        vp.setEditorMode("Lighting", 2)
        vp.setEditorMode("BoundingBox", 2)
        if hasattr(vp, "AngularDeflection"):
            vp.setEditorMode("AngularDeflection", 2)

    def getIcon(self):
        ''' Return the icon in XMP format which will appear in the tree view. This method is optional
        and if not defined a default icon is shown.
        '''
        return ":/data/img/board.png"

    def __getstate__(self):
        ''' When saving the document this object gets stored using Python's cPickle module.
        Since we have some un-pickable here -- the Coin stuff -- we must define this method
        to return a tuple of all pickable objects or None.
        '''
        return None

    def __setstate__(self, state):
        ''' When restoring the pickled object from document we have the chance to set some
        internals here. Since no data were pickled nothing needs to be done here.
        '''
        return None
