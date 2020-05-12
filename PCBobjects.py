# -*- coding: utf8 -*-
#****************************************************************************
#*                                                                          *
#*   Printed Circuit Board Workbench for FreeCAD             PCB            *
#*                                                                          *
#*   Copyright (c) 2013-2019                                                *
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
import Draft
from pivy.coin import *
from math import sqrt, atan2, degrees, sin, cos, radians, pi, hypot
import OpenSCAD2Dgeom
from PySide import QtGui
import unicodedata
import random
#
from PCBboard import cutToBoardShape, getPCBheight, PCBboardObject, viewProviderPCBboardObject
from PCBfunctions import mathFunctions
from PCBconf import *


PCBboardObject = PCBboardObject
viewProviderPCBboardObject = viewProviderPCBboardObject


#####################################
#####################################
#####################################
#####################################
#####################################
#####################################
objectSides = ["TOP", "BOTTOM"]


class partsObject(mathFunctions):
    def __init__(self, obj, typeL):
        self.Type = typeL
        self.oldX = None
        self.oldY = None
        self.oldZ = None
        self.oldROT = 0
        self.offsetZ = 0
        
        #obj.addExtension('App::OriginGroupExtensionPython', self)
        
        obj.addProperty("App::PropertyString", "Package", "PCB", "Package").Package = ""
        obj.addProperty("App::PropertyEnumeration", "Side", "PCB", "Side").Side = 0
        obj.addProperty("App::PropertyDistance", "X", "PCB", "X").X = 0
        obj.addProperty("App::PropertyDistance", "Y", "PCB", "Y").Y = 0
        obj.addProperty("App::PropertyDistance", "Socket", "PCB", "Socket").Socket = 0
        obj.addProperty("App::PropertyAngle", "Rot", "PCB", "Rot").Rot = 0
        obj.addProperty("App::PropertyBool", "KeepPosition", "PCB", "KeepPosition").KeepPosition = False
        # obj.addProperty("App::PropertyString", "Value", "PCB", "Value").Value = ""
        # obj.addProperty("App::PropertyLinkSub", "Thickness", "Part", "Reference to volume of part").Thickness = (FreeCAD.ActiveDocument.Board, 'Thickness')
        
        obj.addProperty("App::PropertyLink", "PartName", "Base", "PartName").PartName = None
        obj.addProperty("App::PropertyLink", "PartValue", "Base", "PartValue").PartValue = None
        # obj.addProperty("App::PropertyLink", "Socket", "Base", "Socket").Socket = None
        
        obj.setEditorMode("Package", 1)
        obj.setEditorMode("Placement", 2)
        obj.setEditorMode("Label", 2)
        obj.setEditorMode("PartName", 1)
        obj.setEditorMode("PartValue", 1)
        #
        obj.Side = objectSides
        obj.Proxy = self
        self.Object = obj
    
    def onChanged(self, fp, prop):
        fp.setEditorMode("Placement", 2)
        fp.setEditorMode("Label", 2)
        fp.setEditorMode("PartName", 1)
        fp.setEditorMode("PartValue", 1)
        fp.setEditorMode("Package", 1)

    def updatePosition_Z(self, fp, thickness, forceUpdate=False):
        try:
            if fp.Side == objectSides[0]:  # TOP
                fp.Placement.Base.z = thickness + self.offsetZ + fp.Socket.Value
            elif fp.Side == objectSides[1] and forceUpdate:
                fp.Placement.Base.z = -self.offsetZ - fp.Socket.Value
        except:
            pass
    
    def rotateZ(self, fp):
        shape = fp.Shape.copy()
        shape.Placement = fp.Placement

        if fp.Side == "TOP":  # TOP
            shape.rotate((fp.X.Value, fp.Y.Value, 0), (0.0, 0.0, 1.0), fp.Rot.Value - self.oldROT)
        else:  # BOTTOM
            shape.rotate((fp.X.Value, fp.Y.Value, 0), (0.0, 0.0, 1.0), -(fp.Rot.Value - self.oldROT))
        
        fp.Placement = shape.Placement
        self.oldROT = fp.Rot.Value
    
    def changeSide(self, fp):
        shape = fp.Shape.copy()
        shape.Placement = fp.Placement
        shape.rotate((fp.X.Value, fp.Y.Value, 0), (0.0, 1.0, 0.0), 180)
        
        fp.Placement = shape.Placement
        self.oldROT = fp.Rot.Value

    def execute(self, fp):
        pass

    def __getstate__(self):
        return [self.Type, self.oldROT, self.oldX, self.oldY, self.offsetZ, self.oldZ]

    def __setstate__(self, state):
        if state:
            self.Type = state[0]
            self.oldROT = state[1]
            self.oldX = state[2]
            self.oldY = state[3]
            self.offsetZ = state[4]
            self.oldZ = state[5]


class partObject(partsObject):
    def __init__(self, obj):
        partsObject.__init__(self, obj, "PCBpart")

    def onChanged(self, fp, prop):
        fp.setEditorMode("Placement", 2)
        fp.setEditorMode("Label", 2)
        fp.setEditorMode("PartName", 1)
        fp.setEditorMode("PartValue", 1)
        fp.setEditorMode("Package", 1)
        ################################################################
        if self.oldZ == None:
            self.oldZ = fp.Socket.Value
        ################################################################
        if prop in ['X', 'Y', 'Socket', 'Rot', 'Side']:
            for i in fp.OutList:
                if prop == 'X':
                    try:
                        i.X.Value = i.X.Value + (fp.X.Value - self.oldX)
                    except:
                        pass
                elif prop == 'Y':
                    try:
                        i.Y.Value = i.Y.Value + (fp.Y.Value - self.oldY)
                    except:
                        pass
                elif prop == 'Socket':
                    try:
                        i.Z.Value = i.Z.Value + (fp.Socket.Value - self.oldZ)
                    except:
                        pass
                elif prop == 'Rot':
                    if hasattr(fp, "Side"):
                        if fp.Side == "TOP":  # TOP
                            i.Rot.Value = i.Rot.Value + (fp.Rot.Value - self.oldROT)
                            [x, y] = self.obrocPunkt2([i.X.Value, i.Y.Value], [fp.X.Value, fp.Y.Value], fp.Rot.Value - self.oldROT)
                        else:  # BOTTOM
                            i.Rot.Value = i.Rot.Value + (fp.Rot.Value - self.oldROT)
                            [x, y] = self.obrocPunkt2([i.X.Value, i.Y.Value], [fp.X.Value, fp.Y.Value], -(fp.Rot.Value - self.oldROT))
                        
                        i.X.Value = x
                        i.Y.Value = y
                elif prop == 'Side':
                    if hasattr(i, "Side"):
                        if i.Side == "TOP":
                            i.Side = "BOTTOM"
                        else:
                            i.Side = "TOP"
                        
                        i.X.Value = self.odbijWspolrzedne(i.X.Value, fp.X.Value)  # mirror i.X.Value by Y axis
        ################################################################
        try:
            if prop == "Rot":
                self.rotateZ(fp)
            elif prop == "Side":
                self.changeSide(fp)
                # Draft.rotate([fp], 180, FreeCAD.Vector(fp.X.Value, fp.Y.Value, 0), axis=FreeCAD.Vector(0.0, 1.0, 0.0), copy=False)
                self.updatePosition_Z(fp, getPCBheight()[1], True)
                self.rotateZ(fp)
            elif prop == "Label":
                try:
                    fp.PartName.Proxy.react = False
                    fp.PartName.String = fp.Label
                    fp.PartName.Proxy.react = True
                except:
                    pass
            elif prop == "X":
                if self.oldX == None:
                    self.oldX = fp.X.Value
                
                fp.Placement.Base.x += fp.X.Value - self.oldX
                self.oldX = fp.X.Value
            elif prop == "Y":
                if self.oldY == None:
                    self.oldY = fp.Y.Value
                
                fp.Placement.Base.y += fp.Y.Value - self.oldY
                self.oldY = fp.Y.Value
            elif prop == "Socket":
                self.updatePosition_Z(fp, getPCBheight()[1], True)
                self.oldZ = fp.Socket.Value
        except Exception as e:
            # FreeCAD.Console.PrintWarning("3. {0}\n".format(e))
            pass


class partObject_E(partsObject):
    def __init__(self, obj):
        partsObject.__init__(self, obj, "PCBpart_E")
        obj.setEditorMode("Placement", 2)
        obj.setEditorMode("Package", 1)
        obj.setEditorMode("Side", 1)
        obj.setEditorMode("X", 1)
        obj.setEditorMode("Y", 1)
        obj.setEditorMode("Rot", 1)
        obj.setEditorMode("Label", 2)
        obj.setEditorMode("Socket", 1)
    
    def onChanged(self, fp, prop):
        fp.setEditorMode("Placement", 2)
        fp.setEditorMode("Package", 1)
        fp.setEditorMode("Side", 1)
        fp.setEditorMode("X", 1)
        fp.setEditorMode("Y", 1)
        fp.setEditorMode("Rot", 1)
        fp.setEditorMode("Label", 2)
        fp.setEditorMode("Socket", 1)
        fp.setEditorMode("Label", 2)
        fp.setEditorMode("PartName", 1)
        fp.setEditorMode("PartValue", 1)
        fp.setEditorMode("Package", 1)
        #######
        if prop in ['Rot']:
            for i in fp.OutList:
                if prop == 'Rot':
                    if hasattr(fp, "Side"):
                        if fp.Side == "TOP":  # TOP
                            i.Rot.Value = i.Rot.Value + (fp.Rot.Value - self.oldROT)
                            [x, y] = self.obrocPunkt2([i.X.Value, i.Y.Value], [fp.X.Value, fp.Y.Value], fp.Rot.Value - self.oldROT)
                        else:  # BOTTOM
                            i.Rot.Value = i.Rot.Value + (fp.Rot.Value - self.oldROT)
                            [x, y] = self.obrocPunkt2([i.X.Value, i.Y.Value], [fp.X.Value, fp.Y.Value], -(fp.Rot.Value - self.oldROT))
                        
                        i.X.Value = x
                        i.Y.Value = y
        #
        try:
            if prop == "Label":
                try:
                    fp.PartName.Proxy.react = False
                    fp.PartName.String = fp.Label
                    fp.PartName.Proxy.react = True
                except:
                    pass
        except:
            pass


class viewProviderPartObject:
    def __init__(self, obj):
        ''' Set this object to the proxy object of the actual view provider '''
        #obj.addExtension("Gui::ViewProviderOriginGroupExtensionPython", self)
        obj.Proxy = self
        self.Object = obj.Object
    
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
        
    def attach(self, obj):
        ''' Setup the scene sub-graph of the view provider, this method is mandatory '''
        self.Object = obj.Object
    
    def claimChildren(self):
        try:
            return [self.Object.PartName, self.Object.PartValue]
        except AttributeError:
            return []

    def updateData(self, fp, prop):
        ''' If a property of the handled feature has changed we have the chance to handle this here '''
        return

    def getDisplayModes(self, obj):
        ''' Return a list of display modes. '''
        modes = []
        return modes

    def getDefaultDisplayMode(self):
        ''' Return the name of the default display mode. It must be defined in getDisplayModes. '''
        return "Flat Lines"

    def setDisplayMode(self, mode):
        ''' Map the display mode defined in attach with those defined in getDisplayModes.
        Since they have the same names nothing needs to be done. This method is optional.
        '''
        return mode

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
        vp.setEditorMode("ShapeColor", 2)
        if hasattr(vp, "AngularDeflection"):
            vp.setEditorMode("AngularDeflection", 2)
        #vp.setEditorMode("Side", 1)
        #vp.setEditorMode("X", 1)
        #vp.setEditorMode("Y", 1)
        #vp.setEditorMode("Rot", 1)
        
        #if prop == "ShowHeight":
            #self.heightDisplay(vp, vp.ShowHeight)

    def getIcon(self):
        ''' Return the icon in XMP format which will appear in the tree view. This method is optional
        and if not defined a default icon is shown.
        '''
        return ":/data/img/modelOK.svg"


class viewProviderPartObject_E:
    def __init__(self, obj):
        ''' Set this object to the proxy object of the actual view provider '''
        obj.Proxy = self
        self.Object = obj.Object
    
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
    
    def attach(self, obj):
        ''' Setup the scene sub-graph of the view provider, this method is mandatory '''
        self.Object = obj.Object
    
    def claimChildren(self):
        try:
            return [self.Object.PartName, self.Object.PartValue]
        except AttributeError:
            return []
        
    def updateData(self, fp, prop):
        ''' If a property of the handled feature has changed we have the chance to handle this here '''
        return

    def getDisplayModes(self, obj):
        ''' Return a list of display modes. '''
        modes = []
        return modes

    def getDefaultDisplayMode(self):
        ''' Return the name of the default display mode. It must be defined in getDisplayModes. '''
        return "Flat Lines"

    def setDisplayMode(self, mode):
        ''' Map the display mode defined in attach with those defined in getDisplayModes.
        Since they have the same names nothing needs to be done. This method is optional.
        '''
        return mode

    def onChanged(self, vp, prop):
        ''' Print the name of the property that has changed '''
        vp.setEditorMode("LineColor", 2)
        vp.setEditorMode("DrawStyle", 2)
        vp.setEditorMode("LineWidth", 2)
        vp.setEditorMode("PointColor", 2)
        vp.setEditorMode("PointSize", 2)
        vp.setEditorMode("Deviation", 2)
        vp.setEditorMode("Lighting", 2)
        # vp.setEditorMode("BoundingBox", 2)
        vp.setEditorMode("ShapeColor", 2)
        if hasattr(vp, "AngularDeflection"):
            vp.setEditorMode("AngularDeflection", 2)

    def getIcon(self):
        ''' Return the icon in XMP format which will appear in the tree view. This method is optional
        and if not defined a default icon is shown.
        '''
        return ":/data/img/modelNOK.svg"
        
#####################################
#####################################
#####################################

class objectWire(mathFunctions):
    
    def createArc(self, p1, p2, curve, width=0.02, cap='round'):
        try:
            wir = []
            
            if width <= 0:
                width = 0.02
                
            width /= 2.
                
            [x3, y3] = self.arcMidPoint(p1, p2, curve)
            [xs, ys] = self.arcCenter(p1[0], p1[1], p2[0], p2[1], x3, y3)
            ##
            # a = (ys - p1[1]) / (xs - p1[0])
            [xT_1, yT_1] = self.shiftPointOnLine(p1[0], p1[1], xs, ys, width)
            [xT_4, yT_4] = self.shiftPointOnLine(p1[0], p1[1], xs, ys, -width)
            ###
            [xT_2, yT_2] = self.obrocPunkt2([xT_1, yT_1], [xs, ys], curve)
            [xT_5, yT_5] = self.obrocPunkt2([xT_4, yT_4], [xs, ys], curve)
            ########
            ########
            wir = []
            # outer arc
            [xT_3, yT_3] = self.arcMidPoint([xT_1, yT_1], [xT_2, yT_2], curve)
            wir.append(Part.ArcOfCircle(FreeCAD.Base.Vector(xT_1, yT_1, 0), FreeCAD.Base.Vector(xT_3, yT_3, 0), FreeCAD.Base.Vector(xT_2, yT_2, 0)))
            # inner arc
            [xT_6, yT_6] = self.arcMidPoint([xT_4, yT_4], [xT_5, yT_5], curve)
            wir.append(Part.ArcOfCircle(FreeCAD.Base.Vector(xT_4, yT_4, 0), FreeCAD.Base.Vector(xT_6, yT_6, 0), FreeCAD.Base.Vector(xT_5, yT_5, 0)))
            ##
            if cap == 'flat':
                wir.append(Part.LineSegment(FreeCAD.Base.Vector(xT_1, yT_1, 0), FreeCAD.Base.Vector(xT_4, yT_4, 0)))
                wir.append(Part.LineSegment(FreeCAD.Base.Vector(xT_2, yT_2, 0), FreeCAD.Base.Vector(xT_5, yT_5, 0)))
            else:
                # wir.append(Part.Line(FreeCAD.Base.Vector(xT_1, yT_1, 0), FreeCAD.Base.Vector(xT_4, yT_4, 0)))
                # wir.append(Part.Line(FreeCAD.Base.Vector(xT_2, yT_2, 0), FreeCAD.Base.Vector(xT_5, yT_5, 0)))
                
                # start
                if xs - p1[0] == 0:  # vertical line
                    if curve > 0:
                        [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], 180)
                    else:
                        [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], -180)
                else:
                    a = (ys - p1[1]) / (xs - p1[0])
                    
                    if a == 0:  # horizontal line
                        if curve > 0:
                            [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], 180)
                        else:
                            [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], -180)
                        pass
                    else:
                        # a = (ys - p1[1]) / (xs - p1[0])
                        if curve > 0:
                            if a > 0:
                                if xT_1 > xs:
                                    [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], 180)
                                else:
                                    [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], -180)
                            else:
                                if xT_1 > xs:
                                    [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], 180)
                                else:
                                    [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], -180)
                        else:
                            if a > 0:
                                if xT_1 > xs:
                                    [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], -180)
                                else:
                                    [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], 180)
                            else:
                                if xT_1 > xs:
                                    [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], -180)
                                else:
                                    [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], 180)
                        
                wir.append(Part.ArcOfCircle(FreeCAD.Base.Vector(xT_1, yT_1, 0), FreeCAD.Base.Vector(xT_7, yT_7, 0), FreeCAD.Base.Vector(xT_4, yT_4, 0)))
                
                # end
                # b = (ys - p2[1]) / (xs - p2[0])
                
                if curve > 0:
                    if xT_2 > xs:
                        if xT_2 >= xT_5:
                            [xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], 180)
                        else:
                            [xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], -180)
                    else:
                        if xT_2 >= xT_5:
                            [xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], -180)
                        else:
                            [xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], 180)
                else:
                    if xT_2 > xs:
                        if xT_2 >= xT_5:
                            [xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], -180)
                        else:
                            [xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], 180)
                    else:
                        if xT_2 >= xT_5:
                            [xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], 180)
                        else:
                            [xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], -180)
                
                wir.append(Part.ArcOfCircle(FreeCAD.Base.Vector(xT_2, yT_2, 0), FreeCAD.Base.Vector(xT_8, yT_8, 0), FreeCAD.Base.Vector(xT_5, yT_5, 0)))
            
            ####
            mainObj = Part.Shape(wir)
            mainObj = Part.Wire(mainObj.Edges)
            return self.makeFace(mainObj)
        except Exception as e:
            FreeCAD.Console.PrintWarning(u"{0}\n".format(e))

    def createLine(self, x1, y1, x2, y2, width=0.01):
        if width <= 0:
            width = 0.01
        
        # dlugosc linii
        dlugosc = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        
        # kat nachylenia
        if x1 > x2:
            kat = degrees(atan2(y1 - y2, x1 - x2)) - 90
        else:
            kat = degrees(atan2(y2 - y1, x2 - x1)) - 90
        if x1 > x2:
            kat += 180
        
        # promien luku na obu koncach sciezki
        r = width / 2.
        
        # create wire
        wir = []
        wir.append(Part.LineSegment(FreeCAD.Base.Vector(0 - r, 0, 0), FreeCAD.Base.Vector(0 - r, dlugosc, 0)))
        wir.append(Part.LineSegment(FreeCAD.Base.Vector(0 + r, 0, 0), FreeCAD.Base.Vector(0 + r, dlugosc, 0)))

        p1 = [0 - r, 0]
        p2 = [0, 0 - r]
        p3 = [0 + r, 0]
        wir.append(Part.ArcOfCircle(FreeCAD.Base.Vector(p1[0], p1[1], 0), FreeCAD.Base.Vector(p2[0], p2[1], 0), FreeCAD.Base.Vector(p3[0], p3[1], 0)))

        p1 = [0 - r, dlugosc]
        p2 = [0, dlugosc + r]
        p3 = [0 + r, dlugosc]
        wir.append(Part.ArcOfCircle(FreeCAD.Base.Vector(p1[0], p1[1], 0), FreeCAD.Base.Vector(p2[0], p2[1], 0), FreeCAD.Base.Vector(p3[0], p3[1], 0)))

        mainObj = Part.Shape(wir)
        mainObj = Part.Wire(mainObj.Edges)
        mainObj = Part.Face(mainObj)
        
        pos_1 = FreeCAD.Base.Vector(x1, y1, 0)
        center = FreeCAD.Base.Vector(0, 0, 0)
        rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), kat)
        mainObj.Placement = FreeCAD.Base.Placement(pos_1, rot, center)
        
        return mainObj
        
    def createCircle(self, x, y, r, w=0):
        if w > 0:
            mainObj = Part.Wire([Part.Circle(FreeCAD.Vector(x, y), FreeCAD.Vector(0, 0, 1), r + w / 2.).toShape()])
            mainObj = self.makeFace(mainObj)
            mainObj = self.cutHole(mainObj, [x, y, r - w / 2.])
        
            return mainObj
        else:
            mainObj = [Part.Circle(FreeCAD.Vector(x, y), FreeCAD.Vector(0, 0, 1), r).toShape()]
        
            return self.makeFace(Part.Wire(mainObj))
        
    def cutHole(self, mainObj, hole):
        if hole[2] > 0:
            hole = [Part.Circle(FreeCAD.Vector(hole[0], hole[1]), FreeCAD.Vector(0, 0, 1), hole[2]).toShape()]
            hole = Part.Wire(hole)
            hole = self.makeFace(hole, self.defHeight)
            
            return mainObj.cut(hole)
        return mainObj
    
    def makeFace(self, mainObj, height, extrude=True):
        # shifted from generuj() function
        # extruding each wires separately is much faster than the whole compound
        # testing board - from 48[s] to 21[s]
        
        if extrude:
            if self.side == 1:  # top side
                return Part.Face(mainObj).extrude(FreeCAD.Base.Vector(0, 0, height / 1000.))
            elif self.side == 2:  # both sides
                return Part.Face(mainObj).extrude(FreeCAD.Base.Vector(0, 0, height))
            else:  # bottom side
                return Part.Face(mainObj).extrude(FreeCAD.Base.Vector(0, 0, -height / 1000.))
        else:
            return Part.Face(mainObj)


class layerSilkObject(objectWire):
    def __init__(self, obj, typeL):
        # obj.addProperty("App::PropertyLinkSub", "Holes", "Holes", "Reference to volume of part").Holes = (FreeCAD.ActiveDocument.Board, 'Holes')
        # self.spisObiektow = []
        self.Type = ['layer'] + typeL
        
        obj.addProperty("App::PropertyBool", "Cut", "Holes", "Cut", 8).Cut = False
        obj.addProperty("App::PropertyBool", "CutToBoard", "Shape", "Cut to board", 8).CutToBoard = False
        # obj.addProperty("Part::PropertyPartShape", "cleanShape", "Shape", "cleanShape", 4)

        self.defHeight = 35
        self.spisObiektowTXT = []
        self.side = 1  # 0-bottom   1-top   2-both
        self.cleanShape = None
        self.signalsList = {}
        obj.Proxy = self
    
    def __getstate__(self):
        try:
            return [self.Type, None, self.defHeight, self.side, self.cleanShape.exportBrepToString(), self.signalsList]
        except:
            return [self.Type, None, self.defHeight, self.side, Part.Shape().exportBrepToString(), self.signalsList]
        
    def __setstate__(self, state):
        self.Type = state[0]
        self.defHeight = state[2]
        self.side = state[3]
        
        self.cleanShape = Part.Shape()
        self.cleanShape.importBrepFromString(state[4])
        self.spisObiektowTXT = self.cleanShape.Solids
        
        self.signalsList = state[5]

    def addLine(self, x1, y1, x2, y2):
        if x1 == x2 and y1 == y2:
            self.spisObiektowTXT[-1]['objects'].append(['point', x1, y1])
        else:
            self.spisObiektowTXT[-1]['objects'].append(['line', x1, y1, x2, y2])
    
    def addDrillCenter(self, xs, ys, r1, r2):
        if r1 == 0:
            self.spisObiektowTXT.append(None)
            return
        else:
            # self.spisObiektowTXT[-1]['objects'].append(['drillCenter', xs, ys, r1, r2])
            circle_1 = Part.Circle(FreeCAD.Vector(xs, ys), FreeCAD.Vector(0, 0, 1), r1)
            circle_2 = Part.Circle(FreeCAD.Vector(xs, ys), FreeCAD.Vector(0, 0, 1), r2)
            
            drillCenter = Part.Shape([circle_1, circle_2])
            # drillCenter = Part.Wire(drillCenter.Edges)
            self.spisObiektowTXT.append(drillCenter)

    def createCircle2(self, x, y, r):
        return Part.Circle(FreeCAD.Vector(x, y), FreeCAD.Vector(0, 0, 1), r)
    
    def circleCutHole(self, xs, ys, r):
        self.spisObiektowTXT[-1] = self.cutHole(self.spisObiektowTXT[-1], [xs, ys, r])
    
    def addCircle(self, xs, ys, r, w=0):
        if r == 0:
            self.spisObiektowTXT.append(None)
            return
        else:
            if w > 0:
                object_1 = Part.Circle(FreeCAD.Vector(xs, ys), FreeCAD.Vector(0, 0, 1), r + w / 2.)
            else:
                object_1 = Part.Circle(FreeCAD.Vector(xs, ys), FreeCAD.Vector(0, 0, 1), r)
                
            mainObj = Part.Shape([object_1])
            mainObj = Part.Wire(mainObj.Edges)
            # if w > 0:
                # mainObj = self.cutHole(mainObj, [xs, ys, r - w / 2.])
            self.spisObiektowTXT.append(mainObj)

    def addArc3P(self, p1, p2, p3):
        self.spisObiektowTXT[-1]['objects'].append(['arc3P', p1, p2, p3])

    def addElipse(self, x, y, r1, r2, w=0):
        self.spisObiektowTXT[-1]['objects'].append(['elipse', x, y, r1, r2, w])
        
    ################
    ################
    # def createArc(self, x, y, r, startAngle, stopAngle):
        # return Part.ArcOfCircle(Part.Circle(FreeCAD.Vector(x, y, 0), FreeCAD.Vector(0, 0, 1), r), startAngle, stopAngle)
    
    def createArc3P(self, p1, p2, p3):
        return Part.ArcOfCircle(FreeCAD.Base.Vector(p1[0], p1[1], 0), FreeCAD.Base.Vector(p2[0], p2[1], 0), FreeCAD.Base.Vector(p3[0], p3[1], 0))
    
    def arcMidPoint(self, prev_vertex, vertex, angle):
        if len(prev_vertex) == 3:
            [x1, y1, z1] = prev_vertex
        else:
            [x1, y1] = prev_vertex
            
        if len(vertex) == 3:
            [x2, y2, z2] = vertex
        else:
            [x2, y2] = vertex
        
        angle = radians(angle / 2)
        basic_angle = atan2(y2 - y1, x2 - x1) - pi / 2
        shift = (1 - cos(angle)) * hypot(y2 - y1, x2 - x1) / 2 / sin(angle)
        midpoint = [(x2 + x1) / 2 + shift * cos(basic_angle), (y2 + y1) / 2 + shift * sin(basic_angle)]
        
        return midpoint
    
    def createFace(self, obj, extrude=True, height=None, signalName=None):
        if not height:
            height = self.defHeight
        
        return self.makeFace(obj, height, extrude)

    def setFace(self, extrude=True, height=None, signalName=None):
        if not height:
            height = self.defHeight
        
        self.spisObiektowTXT[-1] = self.makeFace(self.spisObiektowTXT[-1], height, extrude)
        #
        if signalName:
            shapeID = len(self.spisObiektowTXT) - 1
            if not shapeID in self.signalsList.keys():
                self.signalsList[shapeID] = signalName
                
    def addNewObject(self, obj, signalName=None):
        self.spisObiektowTXT.append(obj)
        #
        if signalName and not signalName.strip() == "":
            shapeID = len(self.spisObiektowTXT) - 1
            if not shapeID in self.signalsList.keys():
                self.signalsList[shapeID] = signalName
    
    def cutOffPaths(self, obj, signalName, isolate=0.406):
        data = []
        out = []
        try:
            for i in range(0, len(self.spisObiektowTXT)):
                solid = self.spisObiektowTXT[i]
                #
                if i in self.signalsList.keys() and self.signalsList[i] == signalName:
                    continue
                else:
                    if solid.isValid() and obj.distToShape(solid)[0] == 0.0:
                        try:
                            a = solid.makeOffsetShape(isolate, 0.01, join=0)
                            if not a.isNull():
                                new = obj
                                data.append(new.cut(a))
                                # Part.show(new.cut(a))
                                # obj = obj.cut(a)
                        except Exception as e:
                            print(e)
        except Exception as e:
            print(e)
        
        if len(data):
            for i in range(0, len(data)):
                a = obj
                obj = obj.common([data[i]])
                # Part.show(obj.common([data[i]]))
                
                if not len(obj.Solids):
                    obj = a
            
        return obj
        
    def resetColors(self, fp):
        fp.ViewObject.ShapeColor = fp.ViewObject.ShapeColor
        
    def colorizePaths(self, fp, colorsList):
        data = []
        baseColor = fp.ViewObject.DiffuseColor[0]
        
        try:
            if len(self.signalsList.keys()):
                for i in range(0, len(fp.Shape.Compounds[0].Solids)):
                    solid = fp.Shape.Compounds[0].Solids[i]
                    
                    if i in self.signalsList.keys():
                        signal = self.signalsList[i]
                        
                        if not signal in colorsList.keys():
                            colorsList[signal] = (float(random.randrange(0, 255, 1)), float(random.randrange(0, 255, 1)), float(random.randrange(0, 255, 1)), 0.0)  # RGB
                        #
                        for f in solid.Faces:
                            data.append(colorsList[signal])
                    else:
                        for f in solid.Faces:
                            data.append(baseColor)
                #
                fp.ViewObject.DiffuseColor = data
        except Exception as e:
            print(e)
        
        return colorsList
        
    # def setFace(self, extrude=True, height=None, signalName=None):
        # if not height:
            # height = self.defHeight
        
        # self.spisObiektowTXT[-1] = self.makeFace(self.spisObiektowTXT[-1], height, extrude)
        # #
        # if signalName and not signalName.strip() == "":
            # if not signalName in self.signalsList.keys():
                # self.signalsList[signalName] = []
            # self.signalsList[signalName].append(len(self.spisObiektowTXT) - 1)

    # def colorizePaths(self, fp, colorsList):
        # solidNum = 0
        # data = []
        # baseColor = fp.ViewObject.DiffuseColor[0]
        
        # try:
            # if len(self.signalsList.keys()):
                # for i in range(0, len(fp.Shape.Compounds[0].Solids)):
                    # solid = fp.Shape.Compounds[0].Solids[i]
                    # skipDef = False
                    # #
                    # for k in self.signalsList.keys():
                        # if not k in colorsList.keys():
                            # colorsList[k] = (float(random.randrange(0, 255, 1)), float(random.randrange(0, 255, 1)), float(random.randrange(0, 255, 1)), 0.0) # RGB
                        # #
                        # if solidNum in self.signalsList[k]:
                            # for i in solid.Faces:
                                # data.append(colorsList[k])
                            # skipDef = True
                    # #
                    # if not skipDef:
                        # for i in solid.Faces:
                            # data.append(baseColor)
                    # #
                    # solidNum += 1
                # #
                # fp.ViewObject.DiffuseColor = data
        # except Exception as e:
            # pass
        
        # return colorsList

    def setChangeSide(self, xs, ys, layer):
        if layer == 0:
            self.spisObiektowTXT[-1].rotate(FreeCAD.Vector(xs, ys, 0), FreeCAD.Vector(0, 1, 0), 180)

    def addHole(self, x, y, r):
        self.spisObiektowTXT[-1]['holes'].append([x, y, r])
    
    def addRotation(self, xs, ys, angle):
        self.spisObiektowTXT[-1].rotate(FreeCAD.Vector(xs, ys, 0), FreeCAD.Vector(0, 0, 1), angle)

    def addPlacement(self, point, rot, center):
        pos_1 = FreeCAD.Base.Vector(point[0], point[1], point[2])
        center = FreeCAD.Base.Vector(center[0], center[1], center[2])
        rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), rot)
        
        self.spisObiektowTXT[-1].Placement = FreeCAD.Base.Placement(pos_1, rot, center)

    def createElipse(self, x, y, r1, r2):
        if r1 > r2:
            return Part.Ellipse(FreeCAD.Vector(x, y, 0), r1, r2)
        else:
            return Part.Ellipse(FreeCAD.Vector(x, y, 0), r2, r1)
    
    def createLine2(self, x1, y1, x2, y2):
        if not [x1, y1] == [x2, y2]:
            return Part.LineSegment(FreeCAD.Base.Vector(x1, y1, 0), FreeCAD.Base.Vector(x2, y2, 0))
        else:
            return Part.LineSegment(FreeCAD.Base.Vector(x1, y1, 0), FreeCAD.Base.Vector(x2 + 0.000001, y2 + 0.000001, 0))
    
    def makePoint(self, x, y):
        return Part.Point(FreeCAD.Base.Vector(x, y, 0))

    def makePolygon(self, obj):
        data = []
        holes = []
        
        for i in obj['objects']:
            # if i[0] == 'circle':
                # xs = i[1]
                # ys = i[2]
                # r = i[3]
                # w = i[4]
                
                # if w > 0:
                    # data.append(self.createCircle2(xs, ys, r + w / 2.))
                    # obj['holes'].append([xs, ys, r - w / 2.])
                # else:
                    # data.append(self.createCircle2(xs, ys, r))
            # elif i[0] == 'drillCenter':
                # xs = i[1]
                # ys = i[2]
                # r1 = i[3]
                # r2 = i[4]
                
                # data.append(self.createCircle2(xs, ys, r1))
                # obj['holes'].append([xs, ys, r2])
            if i[0] == 'elipse':
                x = i[1]
                y = i[2]
                r1 = i[3]
                r2 = i[4]
                w = i[4]
                
                if r2 > r1:
                    obj['rotations'].append([x, y,  90])
                    
                if w > 0:
                    data.append(self.createElipse(x, y, r1 + w / 2., r2 + w / 2.))
                else:
                    data.append(self.createElipse(x, y, r1, r2))
            # elif i[0] == 'line':
                # x1 = i[1]
                # y1 = i[2]
                # x2 = i[3]
                # y2 = i[4]
                # data.append(self.createLine2(x1, y1, x2, y2))
            # elif i[0] == 'arc3P':
                # p1 = i[1]
                # p2 = i[2]
                # p3 = i[3]
                
                # data.append(self.createArc3P(p1, p2, p3))
            elif i[0] == 'point':
                x = i[1]
                y = i[2]
                data.append(self.makePoint(x, y))
            elif i[0] == 'skip':
                FreeCAD.Console.PrintWarning("It is not possible to generate pad ({0}). Skipped.\n".format(i[1]))
                continue
            # elif i[0] == 'arcV2':
                # p1 = i[1]
                # p2 = i[2]
                # curve = i[3]
                # width = i[4]
                # cap = i[5]
                
                # data.append(self.makeArc_v2(p1, p2, curve, width, cap))
        #
        if data == []:
            return False
        
        mainObj = Part.Shape(data)
        mainObj = Part.Wire(mainObj.Edges)
        
        if obj['param']['face']:
            mainObj = self.makeFace(mainObj)
        if len(obj['holes']):
            for i in obj['holes']:
                mainObj = self.cutHole(mainObj, i)
        if obj['placement']['shift']:
            pos_1 = FreeCAD.Base.Vector(obj['placement']['point'][0], obj['placement']['point'][1], obj['placement']['point'][2])
            center = FreeCAD.Base.Vector(obj['placement']['center'][0], obj['placement']['center'][1], obj['placement']['center'][2])
            rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), obj['placement']['angle'])
            
            mainObj.Placement = FreeCAD.Base.Placement(pos_1, rot, center)
        if len(obj['rotations']):
            for i in obj['rotations']:
                self.rotateObj(mainObj, i)
        if obj['side']['side']:
            self.changeSide(mainObj, obj['side'])
        
        return mainObj
    
    def generuj(self, fp):
        try:
            if len(self.spisObiektowTXT):
                if self.cleanShape == None:
                    self.cleanShape = Part.makeCompound(self.spisObiektowTXT)
                    # fp.cleanShape = self.cleanShape
                
                pads = self.cleanShape
                ############################################################
                # BASED ON  realthunder PROPOSAL/SOLUTION
                ############################################################
                try:
                    if fp.Cut == True:
                        if FreeCAD.ActiveDocument.Board.Proxy.holesComp == None:
                            FreeCAD.ActiveDocument.Board.Proxy.getHoles(FreeCAD.ActiveDocument.Board)
                        
                        if not FreeCAD.ActiveDocument.Board.Proxy.holesComp == None:
                            holes = FreeCAD.ActiveDocument.Board.Proxy.holesComp.extrude(FreeCAD.Base.Vector(0, 0, FreeCAD.ActiveDocument.Board.Thickness + 2))
                            holes.Placement.Base.z = -1
                            # Part.show(holes)
                            pads = pads.cut(holes)
                except Exception as e:
                    FreeCAD.Console.PrintWarning("3. {0}\n".format(e))
                ############################################################
                if fp.CutToBoard:
                    pads = cutToBoardShape(pads)
                ############################################################
                ############################################################
                # shifted to makeFace() function
                # extruding each wires separately is much faster than the whole compound
                # testing board - from 48[s] to 21[s]
                #
                # if self.side == 1:  # top side
                    # pads = pads.extrude(FreeCAD.Base.Vector(0, 0, self.defHeight / 1000.))
                # elif  self.side == 2:  # both sides
                    # pads = pads.extrude(FreeCAD.Base.Vector(0, 0, self.defHeight))
                # else:  # bottom side
                    # pads = pads.extrude(FreeCAD.Base.Vector(0, 0, -self.defHeight / 1000.))
                ############################################################
                # pads.Placement.Base.z = fp.Placement.Base.z
                fp.Shape = pads
                self.updatePosition_Z(fp, FreeCAD.ActiveDocument.Board.Thickness)
            fp.purgeTouched()
        except Exception as e:
            FreeCAD.Console.PrintWarning("3. {0}\n".format(e))
    ################
    # shapes
    ################
    
    def addRectangle(self, x1, y1, x2, y2):
        if x1 == x2 and y1 == y2:
            self.spisObiektowTXT.append(None)
            return
            # self.spisObiektowTXT[-1]['objects'].append(['skip', "point [{0}, {1}] detected instead rectangle".format(x1, y1)])
        else:
            object_1 = self.createLine2(x1, y1, x2, y1)
            object_2 = self.createLine2(x2, y1, x2, y2)
            object_3 = self.createLine2(x2, y2, x1, y2)
            object_4 = self.createLine2(x1, y2, x1, y1)
            
            mainObj = Part.Shape([object_1, object_2, object_3, object_4])
            mainObj = Part.Wire(mainObj.Edges)
            self.spisObiektowTXT.append(mainObj)
    
    def generateOctagon(self, x, y, height, width=0):
        if width == 0:
            width = height
        
        w_pP = width / 2.
        w_zP = width / (2 + (sqrt(2)))
        w_aP = width * (sqrt(2) - 1)
        
        h_pP = height / 2.
        h_zP = height / (2 + (sqrt(2)))
        h_aP = height * (sqrt(2) - 1)
        
        return [[x - w_pP + w_zP, y - h_pP, 0, x - w_pP + w_zP + w_aP, y - h_pP, 0],
                [x - w_pP + w_zP + w_aP, y - h_pP, 0, x + w_pP, y - h_pP + h_zP, 0],
                [x + w_pP, y - h_pP + h_zP, 0, x + w_pP, y - h_pP + h_zP + h_aP, 0],
                [x + w_pP, y - h_pP + h_zP + h_aP, 0, x + w_pP - w_zP, y + h_pP, 0],
                [x + w_pP - w_zP, y + h_pP, 0, x + w_pP - w_zP - w_aP, y + h_pP, 0],
                [x + w_pP - w_zP - w_aP, y + h_pP, 0, x - w_pP, y + h_pP - h_zP, 0],
                [x - w_pP, y + h_pP - h_zP, 0, x - w_pP, y + h_pP - h_zP - h_aP, 0],
                [x - w_pP, y + h_pP - h_zP - h_aP, 0, x - w_pP + w_zP, y - h_pP, 0]]
    
    def addOctagon(self, x, y, diameter, width=0):
        objects = []
        
        for i in self.generateOctagon(x, y, diameter, width):
            (x1, y1, z1, x2, y2, z2) = i
            objects.append(self.createLine2(x1, y1, x2, y2))
        
        mainObj = Part.Shape(objects)
        mainObj = Part.Wire(mainObj.Edges)
        self.spisObiektowTXT.append(mainObj)
    
    def addPadLong(self, x, y, dx, dy, perc, typ=0):
        if dx == 0 or dy == 0:
            self.spisObiektowTXT.append(None)
            return
        
        objects = []
        
        curve = 90.
        if typ == 0:  # %
            if perc > 100.:
                perc == 100.
            
            if dx > dy:
                e = dy * perc / 100.
            else:
                e = dx * perc / 100.
        else:  # mm
            e = perc
        
        p1 = [x - dx + e, y - dy, 0]
        p2 = [x + dx - e, y - dy, 0]
        p3 = [x + dx, y - dy + e, 0]
        p4 = [x + dx, y + dy - e, 0]
        p5 = [x + dx - e, y + dy, 0]
        p6 = [x - dx + e, y + dy, 0]
        p7 = [x - dx, y + dy - e, 0]
        p8 = [x - dx, y - dy + e, 0]
        #
        punkty = []

        if p1 != p2:
            objects.append(self.createLine2(p1[0], p1[1], p2[0], p2[1]))

        if p2 != p3:
            p9 = self.arcMidPoint(p2, p3, curve)
            objects.append(self.createArc3P(p2, p9, p3))
            
        if p3 != p4:
            objects.append(self.createLine2(p3[0], p3[1], p4[0], p4[1]))

        if p4 != p5:
            p10 = self.arcMidPoint(p4, p5, curve)
            objects.append(self.createArc3P(p4, p10, p5))
            
        if p5 != p6:
            objects.append(self.createLine2(p5[0], p5[1], p6[0], p6[1]))

        if p6 != p7:
            p11 = self.arcMidPoint(p6, p7, curve)
            objects.append(self.createArc3P(p6, p11, p7))

        if p7 != p8:
            objects.append(self.createLine2(p7[0], p7[1], p8[0], p8[1]))

        if p8 != p1:
            p12 = self.arcMidPoint(p8, p1, curve)
            objects.append(self.createArc3P(p8, p12, p1))
        
        mainObj = Part.Shape(objects)
        mainObj = Part.Wire(mainObj.Edges)
        self.spisObiektowTXT.append(mainObj)
    
    def addPadOffset(self, x, y, R, e):
        if R == 0:
            self.spisObiektowTXT.append(None)
            return
        
        object_1 = self.createLine2(x, y + R, x + R + e / 2, y + R)
        object_2 = self.createLine2(x, y - R, x + R + e / 2, y - R)
        
        p1 = [x + R + e / 2, y + R]
        p2 = [x + R + e / 2, y - R]
        p3 = [x + R + e, y]
        object_3 = self.createArc3P(p1, p3, p2)
        
        p1 = [x, y + R]
        p2 = [x, y - R]
        p3 = [x - R, y]
        object_4 = self.createArc3P(p1, p3, p2)
        
        mainObj = Part.Shape([object_1, object_2, object_3, object_4])
        mainObj = Part.Wire(mainObj.Edges)
        self.spisObiektowTXT.append(mainObj)
    
    def addTrapeze(self, p1, p2, xRD, yRD):
        [x1, y1] = p1
        [x2, y2] = p2
        
        self.addLine(x1 - xRD, y1 - yRD, x2 + xRD, y1 + yRD)
        self.addLine(x2 + xRD, y1 + yRD, x2 - xRD, y2 - yRD)
        self.addLine(x2 - xRD, y2 - yRD, x1 + xRD, y2 + yRD)
        self.addLine(x1 + xRD, y2 + yRD, x1 - xRD, y1 - yRD)
    
    def addPolygon(self, polygon, returnObj=False):
        objects = []
        
        for i in polygon:
            if i[0] == 'Line':
                objects.append(self.createLine2(i[1], i[2], i[3], i[4]))
            elif i[0] == 'Arc3P':
                p1 = [i[1], i[2]]
                p2 = [i[3], i[4]]
                curve = i[5]
                
                p3 = self.arcMidPoint(p2, p1, curve)
                objects.append(self.createArc3P(p1, p3, p2))
        
        if objects == []:
            self.spisObiektowTXT.append(None)
            return
            
        mainObj = Part.Shape(objects)
        mainObj = Part.Wire(mainObj.Edges)
        if returnObj:
            return mainObj
        else:
            self.spisObiektowTXT.append(mainObj)
    
    def addArcWidth(self, p1, p2, curve, width=0.02, cap='round', p3=None):
        try:
            if width <= 0:
                width = 0.02
                
            width /= 2.
              
            if p3:
                [x3, y3] = p3
            else:
                [x3, y3] = self.arcMidPoint(p1, p2, curve)
            
            [xs, ys] = self.arcCenter(p1[0], p1[1], p2[0], p2[1], x3, y3)
            r = self.arcRadius(p1[0], p1[1], p2[0], p2[1], curve)
            ######################################
            # temporary solution
            if r * 2 < width * 2:
                FreeCAD.Console.PrintWarning(u"Radius of the arc is smaller than the width. The object will be skipped (temporarily).\n")
                return False
            ######################################
            #
            # a = (ys - p1[1]) / (xs - p1[0])
            [xT_1, yT_1] = self.shiftPointOnLine(p1[0], p1[1], xs, ys, width)
            [xT_4, yT_4] = self.shiftPointOnLine(p1[0], p1[1], xs, ys, -width)
            ###
            [xT_2, yT_2] = self.obrocPunkt2([xT_1, yT_1], [xs, ys], curve)
            [xT_5, yT_5] = self.obrocPunkt2([xT_4, yT_4], [xs, ys], curve)
            ########
            ########
            wir = []
            # outer arc
            [xT_3, yT_3] = self.arcMidPoint([xT_1, yT_1], [xT_2, yT_2], curve)
            object_1 = self.createArc3P([xT_1, yT_1], [xT_3, yT_3], [xT_2, yT_2])
            # inner arc
            [xT_6, yT_6] = self.arcMidPoint([xT_4, yT_4], [xT_5, yT_5], curve)
            object_2 = self.createArc3P([xT_4, yT_4], [xT_6, yT_6], [xT_5, yT_5])
            ##
            if cap == 'flat':
                object_3 = self.createLine2(xT_1, yT_1, xT_4, yT_4)
                object_4 = self.createLine2(xT_2, yT_2, xT_5, yT_5)
            else:
                # start
                if xs - p1[0] == 0:  # vertical line
                    if curve > 0:
                        [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], 180)
                    else:
                        [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], -180)
                else:
                    a = (ys - p1[1]) / (xs - p1[0])
                    
                    if a == 0:  # horizontal line
                        if curve > 0:
                            [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], 180)
                        else:
                            [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], -180)
                        pass
                    else:
                        # a = (ys - p1[1]) / (xs - p1[0])
                        if curve > 0:
                            if a > 0:
                                if xT_1 > xs:
                                    [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], 180)
                                else:
                                    [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], -180)
                            else:
                                if xT_1 > xs:
                                    [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], 180)
                                else:
                                    [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], -180)
                        else:
                            if a > 0:
                                if xT_1 > xs:
                                    [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], -180)
                                else:
                                    [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], 180)
                            else:
                                if xT_1 > xs:
                                    [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], -180)
                                else:
                                    [xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], 180)
                
                object_3 = self.createArc3P([xT_1, yT_1], [xT_7, yT_7], [xT_4, yT_4])
                # end
                # b = (ys - p2[1]) / (xs - p2[0])
                
                if curve > 0:
                    if xT_2 > xs:
                        if xT_2 >= xT_5:
                            [xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], 180)
                        else:
                            [xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], -180)
                    else:
                        if xT_2 >= xT_5:
                            [xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], -180)
                        else:
                            [xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], 180)
                else:
                    if xT_2 > xs:
                        if xT_2 >= xT_5:
                            [xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], -180)
                        else:
                            [xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], 180)
                    else:
                        if xT_2 >= xT_5:
                            [xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], 180)
                        else:
                            [xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], -180)
                
                object_4 = self.createArc3P([xT_2, yT_2], [xT_8, yT_8], [xT_5, yT_5])
            #
            mainObj = Part.Shape([object_1, object_3, object_2, object_4])
            mainObj = Part.Wire(mainObj.Edges)
            self.spisObiektowTXT.append(mainObj)
            # self.addPlacement([x1, y1, 0], kat, [0, 0, 0])
            # return mainObj
            return True
        except Exception as e:
            FreeCAD.Console.PrintWarning(u"{0}\n".format(e))
            return False
            
    def addLineWidth(self, x1, y1, x2, y2, width=0, style=''):
        if style in ["longdash", "shortdash"]:
            lineStyle = style
        else:
            lineStyle = ""
        #####
        if [x1, y1] == [x2, y2]:
            x2 += 0.01
            y2 += 0.01
        
        if width <= 0:
            width = 0.01

        # dlugosc linii
        dlugosc = sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        
        # kat nachylenia
        if x1 > x2:
            kat = degrees(atan2(y1 - y2, x1 - x2)) - 90
        else:
            kat = degrees(atan2(y2 - y1, x2 - x1)) - 90
        if x1 > x2:
            kat += 180
        
        # promien luku na obu koncach sciezki
        r = width / 2.
        
        # create wire
        line_1 = self.createLine2(0 - r, 0, 0 - r, dlugosc)
        line_2 = self.createLine2(0 + r, 0, 0 + r, dlugosc)
        
        p1 = [0 - r, 0]
        p2 = [0, 0 - r]
        p3 = [0 + r, 0]
        arc_1 = self.createArc3P(p1, p2, p3)
        
        p1 = [0 - r, dlugosc]
        p2 = [0, dlugosc + r]
        p3 = [0 + r, dlugosc]
        arc_2 = self.createArc3P(p1, p2, p3)
        #
        # self.addPlacement([x1, y1, 0], kat, [0, 0, 0])
        #
        mainObj = Part.Shape([line_1, arc_1, line_2, arc_2])
        mainObj = Part.Wire(mainObj.Edges)
        self.spisObiektowTXT.append(mainObj)
        self.addPlacement([x1, y1, 0], kat, [0, 0, 0])
        # return mainObj

    def updateHoles(self, fp):
        self.generuj(fp)
    
    def updatePosition_Z(self, fp, thickness):
        if self.side == 1:  # top side
            fp.Placement.Base.z = thickness + 0.000001
        else:  # bottom/both sides
            # fp.Placement.Base.z = -self.defHeight / 1000.
            fp.Placement.Base.z = - 0.000001
            
            if self.side == 2:  # both sides
                self.defHeight = thickness + 0.000001
                self.generuj(fp)
        
        # fp.recompute()
        # fp.purgeTouched()
    
    def onChanged(self, fp, prop):
        if prop == "Cut" or prop == "CutToBoard":
            self.generuj(fp)
        
    def execute(self, fp):
        pass
        # self.generuj(fp)


class viewProviderLayerSilkObject:
    def __init__(self, obj):
        ''' Set this object to the proxy object of the actual view provider '''
        obj.Proxy = self
        
    def attach(self, obj):
        ''' Setup the scene sub-graph of the view provider, this method is mandatory '''
        return

    def updateData(self, fp, prop):
        ''' If a property of the handled feature has changed we have the chance to handle this here '''
        return

    def getDefaultDisplayMode(self):
        return "Shaded"

    def onChanged(self, vp, prop):
        vp.setEditorMode("LineColor", 2)
        vp.setEditorMode("DrawStyle", 2)
        vp.setEditorMode("LineWidth", 2)
        vp.setEditorMode("PointColor", 2)
        vp.setEditorMode("PointSize", 2)
        vp.setEditorMode("Deviation", 2)
        vp.setEditorMode("Lighting", 2)
        vp.setEditorMode("Transparency", 2)
        vp.setEditorMode("BoundingBox", 2)
        if hasattr(vp, "AngularDeflection"):
            vp.setEditorMode("AngularDeflection", 2)
        
        if prop == "ShapeColor":
            vp.LineColor = vp.ShapeColor
            vp.PointColor = vp.ShapeColor

    def getIcon(self):
        ''' Return the icon in XMP format which will appear in the tree view. This method is optional
        and if not defined a default icon is shown.
        '''
        return ":/data/img/layers_TI.svg"

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


#####################################
#####################################
#####################################
class constraintAreaObject:
    def __init__(self, obj, typeL):
        self.Type = typeL
        self.pcbHeight = 1.5
        
        if not self.Type in ['tRestrict', 'bRestrict', 'vRestrict', 'vRouteOutline', 'vPlaceOutline']:
            obj.addProperty("App::PropertyLength", "Height", "Base", "Height of the element").Height = 0.5
        obj.addProperty("App::PropertyLink", "Base", "Draft", "The base object is the wire is formed from 2 objects")
        obj.setEditorMode("Placement", 2)
        obj.Proxy = self
    
    def updatePosition_Z(self, fp, thickness):
        self.pcbHeight = thickness
        
        if self.Type.startswith('t'):  # top side
            fp.Base.Placement.Base.z = self.pcbHeight
            
            fp.recompute()
            fp.Base.recompute()
            fp.purgeTouched()
            fp.Base.purgeTouched()
        elif self.Type.startswith('v'):  # top and bottom side
            fp.Base.Placement.Base.z = -0.5
            self.execute(fp)
            
            fp.recompute()
            fp.Base.recompute()
            fp.purgeTouched()
            fp.Base.purgeTouched()
        else:  # bottomSide
            fp.Base.Placement.Base.z = 0
 
    def execute(self, fp):
        try:
            if fp.Base:
                if fp.Base.isDerivedFrom("Sketcher::SketchObject"):
                    if fp.Base.Support != None:
                        fp.Base.Support = None
                    
                    d = OpenSCAD2Dgeom.edgestofaces(fp.Base.Shape.Edges)
                    if self.Type.startswith('b'):
                        d = d.extrude(FreeCAD.Base.Vector(0, 0, -fp.Height))
                    elif self.Type.startswith('v'):
                        d = d.extrude(FreeCAD.Base.Vector(0, 0, self.pcbHeight + 1))
                    else:
                        d = d.extrude(FreeCAD.Base.Vector(0, 0, fp.Height))
                    
                    fp.Shape = d
                    
                    fp.recompute()
                    fp.Base.recompute()
                    fp.purgeTouched()
                    fp.Base.purgeTouched()
        except:
            pass

    def onChanged(self, fp, prop):
        if prop in ["Base"]:
            self.execute(fp)
        elif prop == "Height" and fp.Height.Value > 0:
            self.execute(fp)

    def __getstate__(self):
        return [self.Type, self.pcbHeight]

    def __setstate__(self, state):
        self.Type = state[0]
        self.pcbHeight = state[1]


class viewProviderConstraintAreaObject:
    def __init__(self, obj):
        ''' Set this object to the proxy object of the actual view provider '''
        obj.Proxy = self

    def attach(self, obj):
        ''' Setup the scene sub-graph of the view provider, this method is mandatory '''
        self.Object = obj.Object
    
    def claimChildren(self):
        return [self.Object.Base]

    def updateData(self, fp, prop):
        ''' If a property of the handled feature has changed we have the chance to handle this here '''
        return

    def getDisplayModes(self, obj):
        ''' Return a list of display modes. '''
        modes = []
        return modes

    def getDefaultDisplayMode(self):
        ''' Return the name of the default display mode. It must be defined in getDisplayModes. '''
        return "Shaded"

    def setDisplayMode(self, mode):
        ''' Map the display mode defined in attach with those defined in getDisplayModes.
        Since they have the same names nothing needs to be done. This method is optional.
        '''
        return mode

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
        return ":/data/img/constraintsArea.png"

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


#####################################
#####################################
#####################################


class DocumentObserver:
    def slotDeletedObject(self, obj):
        if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type") and obj.Proxy.Type in ["PCBpart", "PCBpart_E"]:
            try:
                FreeCAD.ActiveDocument.removeObject(obj.PartName.Name)
            except:
                pass
            
            try:
                FreeCAD.ActiveDocument.removeObject(obj.PartValue.Name)
            except:
                pass


FreeCAD.addDocumentObserver(DocumentObserver())
