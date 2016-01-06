# -*- coding: utf8 -*-
#****************************************************************************
#*                                                                          *
#*   Printed Circuit Board Workbench for FreeCAD             PCB            *
#*   Flexible Printed Circuit Board Workbench for FreeCAD    FPCB           *
#*   Copyright (c) 2013, 2014, 2015                                         *
#*   marmni <marmni@onet.eu>                                                *
#*                                                                          *
#*                                                                          *
#*   This program is free software; you can redistribute it and/or modify   *
#*   it under the terms of the GNU Lesser General Public License (LGPL)     *
#*   as published by the Free Software Foundation; either version 2 of      *
#*   the License, or (at your option) any later version.                    *
#*   for detail see the LICENCE text file.                                  *
#*                                                                          *
#*   This program is distributed in the hope that it will be useful,        *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of         *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          *
#*   GNU Library General Public License for more details.                   *
#*                                                                          *
#*   You should have received a copy of the GNU Library General Public      *
#*   License along with this program; if not, write to the Free Software    *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307   *
#*   USA                                                                    *
#*                                                                          *
#****************************************************************************

import FreeCAD
import Part
import OpenSCAD2Dgeom


def getBoardOutline():
    if not FreeCAD.activeDocument():
        return False
    #
    doc = FreeCAD.activeDocument()
    outline = []
    
    for j in doc.Objects:
        if hasattr(j, "Proxy") and hasattr(j.Proxy, "Type") and j.Proxy.Type == "PCBboard":
            try:
                for k in range(len(j.Border.Geometry)):
                    if j.Border.Geometry[k].Construction:
                        continue
                    
                    if type(j.Border.Geometry[k]).__name__ == 'GeomLineSegment':
                        outline.append([
                            'line',
                            j.Border.Geometry[k].StartPoint.x,
                            j.Border.Geometry[k].StartPoint.y,
                            j.Border.Geometry[k].EndPoint.x,
                            j.Border.Geometry[k].EndPoint.y
                        ])
                    elif type(j.Border.Geometry[k]).__name__ == 'GeomCircle':
                        outline.append([
                            'circle',
                            j.Border.Geometry[k].Radius,
                            j.Border.Geometry[k].Center.x, 
                            j.Border.Geometry[k].Center.y
                        ])
                    elif type(j.Border.Geometry[k]).__name__ == 'GeomArcOfCircle':
                        outline.append([
                            'arc',
                            j.Border.Geometry[k].Radius, 
                            j.Border.Geometry[k].Center.x, 
                            j.Border.Geometry[k].Center.y, 
                            j.Border.Geometry[k].FirstParameter, 
                            j.Border.Geometry[k].LastParameter, 
                            j.Border.Geometry[k]
                        ])
                break
            except Exception, e:
                FreeCAD.Console.PrintWarning('1. ' + str(e) + "\n")
    
    return outline
    
def getHoles():
    if not FreeCAD.activeDocument():
        return False
    #
    holes = {}
    
    try:
        for i in FreeCAD.ActiveDocument.Board.Holes.Geometry:
            if str(i.__class__) == "<type 'Part.GeomCircle'>" and not i.Construction:
                x = i.Center[0]
                y = i.Center[1]
                r = i.Radius
                
                if not r in holes.keys():
                    holes[r] = []
                
                holes[r].append([x, y])
    except:
        return False
    #
    return holes

def getGlue():
    if not FreeCAD.activeDocument():
        return False
    #
    doc = FreeCAD.activeDocument()
    outline = []
    
    for j in doc.Objects:
        if hasattr(j, "Proxy") and hasattr(j.Proxy, "Type") and ('tGlue' in j.Proxy.Type or 'bGlue' in j.Proxy.Type):
            try:
                for k in range(len(j.Base.Geometry)):
                    if j.Base.Geometry[k].Construction:
                        continue
                    
                    if type(j.Base.Geometry[k]).__name__ == 'GeomLineSegment':
                        outline.append([
                            'line',
                            j.Base.Geometry[k].StartPoint.x,
                            j.Base.Geometry[k].StartPoint.y,
                            j.Base.Geometry[k].EndPoint.x,
                            j.Base.Geometry[k].EndPoint.y,
                            j.Proxy.Type,
                            j.Width.Value
                        ])
                    elif type(j.Base.Geometry[k]).__name__ == 'GeomCircle':
                        outline.append([
                            'circle',
                            j.Base.Geometry[k].Radius,
                            j.Base.Geometry[k].Center.x, 
                            j.Base.Geometry[k].Center.y,
                            j.Proxy.Type,
                            j.Width.Value
                        ])
                    elif type(j.Base.Geometry[k]).__name__ == 'GeomArcOfCircle':
                        outline.append([
                            'arc',
                            j.Base.Geometry[k].Radius, 
                            j.Base.Geometry[k].Center.x, 
                            j.Base.Geometry[k].Center.y, 
                            j.Base.Geometry[k].FirstParameter, 
                            j.Base.Geometry[k].LastParameter, 
                            j.Base.Geometry[k],
                            j.Proxy.Type,
                            j.Width.Value
                        ])
            except Exception, e:
                FreeCAD.Console.PrintWarning(str(e) + "\n")
                
    return outline
    
def getDimensions():
    if not FreeCAD.activeDocument():
        return False
    #
    doc = FreeCAD.activeDocument()
    data = []
    
    for j in doc.Objects:
        if hasattr(j, "Proxy") and hasattr(j.Proxy, "Type") and j.Proxy.Type == "Dimension":
            try:
                [xS, yS, zS] = [j.Start.x, j.Start.y, j.Start.z]
                [xE, yE, zE] = [j.End.x, j.End.y, j.End.z]
                [xM, yM, zM] = [j.Dimline.x, j.Dimline.y, j.Dimline.z]
                
                if [xS, yS] != [xE, yE] and zS == zE:
                    data.append([
                        [xS, yS, zS], 
                        [xE, yE, zE], 
                        [xM, yM, zM], 
                        j.Distance
                    ])
            except Exception, e:
                FreeCAD.Console.PrintWarning(str(e) + "\n")
                
    return data
    
def getAnnotations():
    if not FreeCAD.activeDocument():
        return False
    #
    doc = FreeCAD.activeDocument()
    data = []
    
    for j in doc.Objects:
        if hasattr(j, "Proxy") and hasattr(j.Proxy, "Type") and 'PCBannotation' in j.Proxy.Type:
            try:
                annotation = ''
                for i in j.ViewObject.Text:
                    annotation += u'{0}\n'.format(i)

                data.append([
                    j.X.Value, j.Y.Value, 
                    j.ViewObject.Size.Value, 
                    j.Side, 
                    annotation.strip(), 
                    j.ViewObject.Align, 
                    j.Rot.Value, 
                    j.ViewObject.Mirror, 
                    j.ViewObject.Spin
                ])
            except Exception, e:
                FreeCAD.Console.PrintWarning(str(e) + "\n")
                
    return data
    
def getPCBheight():
    if not FreeCAD.activeDocument():
        return [False, 0]
    #
    try:
        pcb = FreeCAD.ActiveDocument.Board.Thickness.Value
        return [True, pcb]
    except:
        return [False, False]
    
def getPCBsize():
    if not FreeCAD.activeDocument():
        return [0, 0, 0, 0]
    #
    try:
        board = FreeCAD.ActiveDocument.Board
        
        minX = board.Shape.BoundBox.XMin
        minY = board.Shape.BoundBox.YMin
        XLength = board.Shape.BoundBox.XLength
        YLength = board.Shape.BoundBox.YLength
            
        return [minX, minY, XLength, YLength]
    except:
        return [0, 0, 0, 0]

def cutToBoardShape(pads):
    if not FreeCAD.activeDocument():
        return False
    #
    # cut to board shape
    board = OpenSCAD2Dgeom.edgestofaces(FreeCAD.ActiveDocument.Board.Border.Shape.Edges)
    #board = FreeCAD.ActiveDocument.Board.Border.Shape
    #board = Part.Face(board)
    board = board.extrude(FreeCAD.Base.Vector(0, 0, 2))
    board.Placement.Base.z = -1
    #Part.show(board)
    pads = board.common(pads)
    return pads


class PCBboardObject:
    def __init__(self, obj):
        self.Type = 'PCBboard'
        obj.setEditorMode("Placement", 2)
        #  board
        obj.addProperty("App::PropertyDistance", "Thickness", "PCB", "Thickness").Thickness = 1.6
        obj.addProperty("App::PropertyLink", "Border", "PCB", "Border")
        #  holes
        obj.addProperty("App::PropertyBool", "Display", "Holes", "Display").Display = True
        obj.addProperty("App::PropertyLink", "Holes", "Holes", "Holes")
        #  base
        obj.addProperty("App::PropertyBool", "AutoUpdate", "Base", "Auto Update").AutoUpdate = True
        #
        obj.Proxy = self

    def onChanged(self, fp, prop):
        fp.setEditorMode("Placement", 2)
        #
        if fp.AutoUpdate == True:
            if prop == "Thickness" or prop == "Border" or prop == "Holes" or prop == "Display":
                self.execute(fp)
            elif prop == "AutoUpdate":
                self.execute(fp)
            
            if prop == "Shape" or prop == "Display" or prop == "Holes" and fp.Display:
                self.updateObjectaHoles(fp)
            if prop == "Thickness":
                self.updatePosition_Z(fp)
                
    def updateObjectaHoles(self, fp):
        for i in FreeCAD.ActiveDocument.Objects:
            try:
                i.Proxy.updateHoles(i)
            except:
                pass
    
    def updatePosition_Z(self, fp):
        for i in FreeCAD.ActiveDocument.Objects:
            try:
                i.Proxy.updatePosition_Z(i, fp.Thickness.Value - self.oldHeight)
            except:
                pass
                #FreeCAD.Console.PrintWarning(str(e) + "\n")
    
    def execute(self, fp):
        try:
            if fp.Border == None or fp.Holes == None:
                return
            
            if fp.Thickness.Value <= 0:
                fp.Thickness.Value = 0.1
                return
            
            try:
                self.oldHeight = fp.Shape.BoundBox.ZMax
            except:
                self.oldHeight = 0
            # holes
            borderOutline = OpenSCAD2Dgeom.edgestofaces(fp.Border.Shape.Wires)
            
            holes = []
            for i in fp.Holes.Shape.Wires:
                holes.append(Part.Face(i))
            
            if len(holes):
                face = borderOutline.cut(Part.makeCompound(holes))
            else:
                face = borderOutline
            #
            fp.Shape = face.extrude(FreeCAD.Base.Vector(0, 0, fp.Thickness.Value))
        except:
            pass
        ##############
        #try:
            #if fp.AutoUpdate == True:
                #if fp.Display:
                    #d = OpenSCAD2Dgeom.edgestofaces(fp.Border.Shape.Edges + fp.Holes.Shape.Edges)
                #else:
                    #d = OpenSCAD2Dgeom.edgestofaces(fp.Border.Shape.Edges)
                #d = d.extrude(FreeCAD.Base.Vector(0, 0, fp.Thickness.Value))
                #fp.Shape = d
        #except:
            #pass
        
    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state


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
