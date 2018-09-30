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
from pivy.coin import *
from math import sqrt, atan2, degrees, sin, cos, radians, pi, hypot
import OpenSCAD2Dgeom
from PySide import QtGui
import unicodedata
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
        self.oldROT = 0
        self.oldX = 0
        self.oldY = 0
        self.update_Z = 0
        self.oldSocket = 0
        
        obj.addProperty("App::PropertyString", "Package", "PCB", "Package").Package = ""
        obj.addProperty("App::PropertyEnumeration", "Side", "PCB", "Side").Side = 0
        obj.addProperty("App::PropertyDistance", "X", "PCB", "X").X = 0
        obj.addProperty("App::PropertyDistance", "Y", "PCB", "Y").Y = 0
        obj.addProperty("App::PropertyDistance", "Socket", "PCB", "Socket").Socket = 0
        obj.addProperty("App::PropertyAngle", "Rot", "PCB", "Rot").Rot = 0
        obj.addProperty("App::PropertyBool", "KeepPosition", "PCB", "KeepPosition").KeepPosition = False
        #obj.addProperty("App::PropertyString", "Value", "PCB", "Value").Value = ""
        #obj.addProperty("App::PropertyLinkSub", "Thickness", "Part", "Reference to volume of part").Thickness = (FreeCAD.ActiveDocument.Board, 'Thickness')
        
        obj.addProperty("App::PropertyLink", "PartName", "Base", "PartName").PartName = None
        obj.addProperty("App::PropertyLink", "PartValue", "Base", "PartValue").PartValue = None
        #obj.addProperty("App::PropertyLink", "Socket", "Base", "Socket").Socket = None
        
        obj.setEditorMode("Package", 1)
        obj.setEditorMode("Placement", 2)
        
        obj.Side = objectSides
        self.offsetX = 0
        self.offsetY = 0
        obj.Proxy = self
        self.Object = obj

    def execute(self, fp):
        pass

    def __getstate__(self):
        return [self.Type, self.oldROT, self.update_Z, self.offsetX, self.offsetY, self.oldX, self.oldY, self.oldSocket]

    def __setstate__(self, state):
        if state:
            self.Type = state[0]
            self.oldROT = state[1]
            self.update_Z = state[2]
            self.offsetX = state[3]
            self.offsetY = state[4]
            self.oldX = state[5]
            self.oldY = state[6]
            self.oldSocket = state[7]


class partObject(partsObject):
    def __init__(self, obj):
        partsObject.__init__(self, obj, "PCBpart")

    def changeSide(self, fp):
        ''' ROT Y '''
        gruboscPlytki = getPCBheight()[1]
        
        shape = fp.Shape.copy()
        shape.Placement = fp.Placement
        shape.rotate((fp.Shape.BoundBox.Center.x, fp.Shape.BoundBox.Center.y, gruboscPlytki / 2.), (0.0, 1.0, 0.0), 180)
        fp.Placement = shape.Placement
        
        try:
            for i in fp.OutList:
                i.X = self.odbijWspolrzedne(i.X.Value, fp.X.Value)
                i.Proxy.reverseSide(i)
        except Exception as e:
            #FreeCAD.Console.PrintWarning("4. {0}\n".format(e))
            pass

        #self.updatePosition_Z(fp)
        self.rotateZ(fp)
        
    def updateSocket(self, fp):
        try:
            if fp.Socket.Value >= 0:
                if fp.Side == objectSides[0]:  # TOP
                    fp.Placement.Base.z = fp.Placement.Base.z + (fp.Socket.Value - self.oldSocket)
                else:
                    fp.Placement.Base.z = fp.Placement.Base.z - (fp.Socket.Value - self.oldSocket)
                
                self.oldSocket = fp.Socket.Value
        except Exception as e:
            FreeCAD.Console.PrintWarning("{0} \n".format(e))
        
        
    def updatePosition_Z(self, fp, thickness):
        try:
            if fp.Side == objectSides[0]:  # TOP
                fp.Placement.Base.z = fp.Placement.Base.z + thickness
            #else:
                #fp.Placement.Base.z = fp.Placement.Base.z - fp.Shape.BoundBox.Center.z - self.update_Z
        except:
            pass
        
    def changePosX(self, fp):
        ''' change placement - X, Y '''
        try:
            fp.Placement.Base.x = fp.Placement.Base.x + (fp.X.Value - fp.Shape.BoundBox.Center.x)
            
            for i in fp.OutList:
                i.X = fp.X.Value - (self.oldX - i.X.Value)
                
            self.oldX = fp.X.Value
        except Exception as e:
            #FreeCAD.Console.PrintWarning("1. {0}\n".format(e))
            pass
            
    def changePosY(self, fp):
        ''' change placement - X, Y '''
        try:
            fp.Placement.Base.y = fp.Placement.Base.y + (fp.Y.Value - fp.Shape.BoundBox.Center.y)
            
            for i in fp.OutList:
                i.Y = fp.Y.Value - (self.oldY - i.Y.Value)

            self.oldY = fp.Y.Value
        except Exception as e:
            #FreeCAD.Console.PrintWarning("2. {0}\n".format(e))
            pass
        
    def rotateZ(self, fp):
        ''' ROT Z '''
        shape = fp.Shape.copy()
        shape.Placement = fp.Placement
        if fp.Side == objectSides[0]:
            shape.rotate((fp.Shape.BoundBox.Center.x, fp.Shape.BoundBox.Center.y, fp.Shape.BoundBox.Center.z), (0.0, 0.0, 1.0), fp.Rot.Value - self.oldROT)
        else:
            shape.rotate((fp.Shape.BoundBox.Center.x, fp.Shape.BoundBox.Center.y, fp.Shape.BoundBox.Center.z), (0.0, 0.0, 1.0), -(fp.Rot.Value - self.oldROT))
        fp.Placement = shape.Placement
        
        try:
            for i in fp.OutList:
                if fp.Side == objectSides[0]:
                    [xR, yR] = self.obrocPunkt2([i.X.Value, i.Y.Value], [fp.X.Value, fp.Y.Value], fp.Rot.Value - self.oldROT)
                else:
                    [xR, yR] = self.obrocPunkt2([i.X.Value, i.Y.Value], [fp.X.Value, fp.Y.Value], -(fp.Rot.Value - self.oldROT))
            
                i.X.Value = xR
                i.Y.Value = yR
                if i.Rot.Value == self.oldROT:
                    i.Rot = fp.Rot
                else:
                    i.Rot = fp.Rot.Value - (self.oldROT - i.Rot.Value)
        except:
            pass
        
        self.oldROT = fp.Rot.Value
    
    def ShowHeight(self, mode):
        pass

    def onChanged(self, fp, prop):
        fp.setEditorMode("Label", 2)
        fp.setEditorMode("Placement", 2)
        fp.setEditorMode("Package", 1)
        fp.setEditorMode("PartName", 1)
        fp.setEditorMode("PartValue", 1)
        
        try:
            if hasattr(fp, "Rot") and prop == "Rot":
                self.rotateZ(fp)
            elif hasattr(fp, "Side") and prop == "Side":
                self.changeSide(fp)
            elif hasattr(fp, "X") and prop in ["X"]:
                self.changePosX(fp)
            elif hasattr(fp, "Y") and prop in ["Y"]:
                self.changePosY(fp)
            elif hasattr(fp, "Socket") and prop in ["Socket"]:
                self.updateSocket(fp)
            #elif hasattr(fp, "Socket") and prop in ["Socket"]:
                #if fp.Socket != None:
                    #socketH = 10
                #else:
                    #socketH = 0
                
                #fp.Placement.Base.z = fp.Placement.Base.z + socketH
                #self.updatePosition_Z(fp, getPCBheight()[1])
        except Exception as e:
            #FreeCAD.Console.PrintWarning("3. {0}\n".format(e))
            pass


class partObject_E(partsObject):
    def __init__(self, obj):
        partsObject.__init__(self, obj, "PCBpart_E")

    def onChanged(self, fp, prop):
        try:
            fp.setEditorMode("Placement", 2)
            fp.setEditorMode("Package", 1)
            fp.setEditorMode("Side", 1)
            fp.setEditorMode("X", 1)
            fp.setEditorMode("Y", 1)
            fp.setEditorMode("Rot", 1)
            fp.setEditorMode("Label", 2)
            fp.setEditorMode("Socket", 1)
        except:
            pass


class viewProviderPartObject:
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
        return [self.Object.PartName, self.Object.PartValue]
        
        #self.heightFlag = SoSeparator()
        #obj.addProperty("App::PropertyBool", "ShowHeight", "Base", "ShowHeight").ShowHeight = False
    
    #def heightDisplay(self, obj, mode):
        #if mode == True:
            #self.heightFlag = SoSeparator()
            ##
            #strzalka_1 = SoCylinder()
            #strzalka_1.radius = 0.2
            #strzalka_1.height = 3
            #self.heightFlag.addChild(strzalka_1)
            ##
            #myTransform_2 = SoTransform()
            #strzalka_2 = SoCone()
            #strzalka_2.bottomRadius = 0.4
            #strzalka_2.height = .8
            #self.heightFlag.addChild(myTransform_2)
            #self.heightFlag.addChild(strzalka_2)
            #myTransform_2.translation = (0, 1.5, 0)
            ##
            #obj.RootNode.addChild(self.heightFlag)
        #else:
            #obj.RootNode.removeChild(self.heightFlag)

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
        Since they have the same names nothing needs to be done. This method is optinal.
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
        #***************************************************************
        #   Author:     Gentleface custom icons design agency (http://www.gentleface.com/)
        #   License:    Creative Commons Attribution-Noncommercial 3.0
        #   Iconset:    Mono Icon Set
        #***************************************************************
        return '''
/* XPM */
static char * C:\\Users\\mariusz\\Desktop\\logo_xpm[] = {
"62 40 12 1",
" 	c None",
".	c #717171",
"+	c #737373",
"@	c #000000",
"#	c #060606",
"$	c #020202",
"%	c #747474",
"&	c #FCFCFC",
"*	c #FFFFFF",
"=	c #FDFDFD",
"-	c #FEFEFE",
";	c #070707",
"                                                              ",
"                                                              ",
"               ...+                                           ",
"              ....  @                                         ",
"             ....  @@@@@                                      ",
"            ....  @@@@@@@@                                    ",
"           ....  @@@@@@@@@@@@                                 ",
"          ....  @@@@@@@@@@@@@@@                               ",
"         ....  @@@@@@@@@@@@@@@@@@@                            ",
"        ....  @@@@@@@@@@@@@@@@@@@@@@#                         ",
"       ....  @@@@@@@@@@@@@@@@@@@@@@@@@@                       ",
"      ....  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@$                    ",
"     ....  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                  ",
"    ....  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@               ",
"   ....  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@             ",
"  ....  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@          ",
"       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@        ",
" . %   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@      ",
" .        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  ..   ",
"   &*       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ +...   ",
"     &**       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ +...  . ",
"       ***       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ +...  .. ",
"         =***       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ +...  ..  ",
"            ***-      @@@@@@@@@@@@@@@@@@@@@@@@@@@@ +...  ..   ",
"               ***   ;   @@@@@@@@@@@@@@@@@@@@@@@@ +...  ..    ",
"                 ***-      $@@@@@@@@@@@@@@@@@@@@ +...  ..     ",
"                    ***       @@@@@@@@@@@@@@@@@ +...  ..      ",
"                      ****       @@@@@@@@@@@@@ +...  ..       ",
"                         ***       @@@@@@@@@@ +...  ..        ",
"                           ****       @@@@@@ +...  ..         ",
"                              ***       @@@ +...  ..          ",
"                                ****        ...  ..           ",
"                                   ***       .  ..            ",
"                                     ****      ..             ",
"                                        *** .. .              ",
"                                            ..                ",
"                                             .                ",
"                                                              ",
"                                                              ",
"                                                              "};
'''


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
        Since they have the same names nothing needs to be done. This method is optinal.
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
        #vp.setEditorMode("BoundingBox", 2)
        vp.setEditorMode("ShapeColor", 2)
        if hasattr(vp, "AngularDeflection"):
            vp.setEditorMode("AngularDeflection", 2)

    def getIcon(self):
        ''' Return the icon in XMP format which will appear in the tree view. This method is optional
        and if not defined a default icon is shown.
        '''
        #***************************************************************
        #   Author:     Gentleface custom icons design agency (http://www.gentleface.com/)
        #   License:    Creative Commons Attribution-Noncommercial 3.0
        #   Iconset:    Mono Icon Set
        #***************************************************************
        return """
/* XPM */
static char * C:\\Users\\mariusz\\Downloads\\Desktop\\logo2_xpm[] = {
"62 40 9 1",
" 	c None",
".	c #717171",
"+	c #737373",
"@	c #FF0000",
"#	c #747474",
"$	c #FCFCFC",
"%	c #FFFFFF",
"&	c #FDFDFD",
"*	c #FEFEFE",
"                                                              ",
"                                                              ",
"               ...+                                           ",
"              ....  @                                         ",
"             ....  @@@@@                                      ",
"            ....  @@@@@@@@                                    ",
"           ....  @@@@@@@@@@@@                                 ",
"          ....  @@@@@@@@@@@@@@@                               ",
"         ....  @@@@@@@@@@@@@@@@@@@                            ",
"        ....  @@@@@@@@@@@@@@@@@@@@@@@                         ",
"       ....  @@@@@@@@@@@@@@@@@@@@@@@@@@                       ",
"      ....  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                    ",
"     ....  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                  ",
"    ....  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@               ",
"   ....  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@             ",
"  ....  @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@          ",
"       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@        ",
" . #   @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@      ",
" .        @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  ..   ",
"   $%       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ +...   ",
"     $%%       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ +...  . ",
"       %%%       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ +...  .. ",
"         &%%%       @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ +...  ..  ",
"            %%%*      @@@@@@@@@@@@@@@@@@@@@@@@@@@@ +...  ..   ",
"               %%%   @   @@@@@@@@@@@@@@@@@@@@@@@@ +...  ..    ",
"                 %%%*      @@@@@@@@@@@@@@@@@@@@@ +...  ..     ",
"                    %%%       @@@@@@@@@@@@@@@@@ +...  ..      ",
"                      %%%%       @@@@@@@@@@@@@ +...  ..       ",
"                         %%%       @@@@@@@@@@ +...  ..        ",
"                           %%%%       @@@@@@ +...  ..         ",
"                              %%%       @@@ +...  ..          ",
"                                %%%%        ...  ..           ",
"                                   %%%       .  ..            ",
"                                     %%%%      ..             ",
"                                        %%% .. .              ",
"                                            ..                ",
"                                             .                ",
"                                                              ",
"                                                              ",
"                                                              "};

"""
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
            #a = (ys - p1[1]) / (xs - p1[0])
            [xT_1, yT_1] = self.shiftPointOnLine(p1[0], p1[1], xs, ys, width)
            [xT_4, yT_4] = self.shiftPointOnLine(p1[0], p1[1], xs, ys, -width)
            ###
            [xT_2, yT_2] = self.obrocPunkt2([xT_1, yT_1], [xs, ys], curve)
            [xT_5, yT_5] = self.obrocPunkt2([xT_4, yT_4], [xs, ys], curve)
            ########
            ########
            wir = []
            ## outer arc
            [xT_3, yT_3] = self.arcMidPoint([xT_1, yT_1], [xT_2, yT_2], curve)
            wir.append(Part.Arc(FreeCAD.Base.Vector(xT_1, yT_1, 0), FreeCAD.Base.Vector(xT_3, yT_3, 0), FreeCAD.Base.Vector(xT_2, yT_2, 0)))
            ## inner arc
            [xT_6, yT_6] = self.arcMidPoint([xT_4, yT_4], [xT_5, yT_5], curve)
            wir.append(Part.Arc(FreeCAD.Base.Vector(xT_4, yT_4, 0), FreeCAD.Base.Vector(xT_6, yT_6, 0), FreeCAD.Base.Vector(xT_5, yT_5, 0)))
            ##
            if cap == 'flat':
                wir.append(Part.LineSegment(FreeCAD.Base.Vector(xT_1, yT_1, 0), FreeCAD.Base.Vector(xT_4, yT_4, 0)))
                wir.append(Part.LineSegment(FreeCAD.Base.Vector(xT_2, yT_2, 0), FreeCAD.Base.Vector(xT_5, yT_5, 0)))
            else:
                #wir.append(Part.Line(FreeCAD.Base.Vector(xT_1, yT_1, 0), FreeCAD.Base.Vector(xT_4, yT_4, 0)))
                #wir.append(Part.Line(FreeCAD.Base.Vector(xT_2, yT_2, 0), FreeCAD.Base.Vector(xT_5, yT_5, 0)))
                
                #start
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
                        #a = (ys - p1[1]) / (xs - p1[0])
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
                        
                wir.append(Part.Arc(FreeCAD.Base.Vector(xT_1, yT_1, 0), FreeCAD.Base.Vector(xT_7, yT_7, 0), FreeCAD.Base.Vector(xT_4, yT_4, 0)))
                
                #end
                #b = (ys - p2[1]) / (xs - p2[0])
                
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
                
                wir.append(Part.Arc(FreeCAD.Base.Vector(xT_2, yT_2, 0), FreeCAD.Base.Vector(xT_8, yT_8, 0), FreeCAD.Base.Vector(xT_5, yT_5, 0)))
            
            ####
            mainObj = Part.Shape(wir)
            mainObj = Part.Wire(mainObj.Edges)
            return self.makeFace(mainObj)

            ######################################
            ######################################
            ######################################
            #cap = 'round'
            
            
            #[x3, y3] = self.arcMidPoint(p1, p2, curve)
            #[xs, ys] = self.arcCenter(p1[0], p1[1], p2[0], p2[1], x3, y3)
            
            ###
            #a = (ys - p1[1]) / (xs - p1[0])

            #[xT_1, yT_1] = self.shiftPointOnLine(p1[0], p1[1], xs, ys, width)
            #[xT_4, yT_4] = self.shiftPointOnLine(p1[0], p1[1], xs, ys, -width)
            
            ##if a > 0:
                ##if p1[1] > ys:
                    ##[xT_1, yT_1] = self.shiftPointOnLine(p1[0], p1[1], xs, ys, width)
                    ##[xT_4, yT_4] = self.shiftPointOnLine(p1[0], p1[1], xs, ys, -width)
                ##else:
                    ##[xT_1, yT_1] = self.shiftPointOnLine(p1[0], p1[1], xs, ys, width)
                    ##[xT_4, yT_4] = self.shiftPointOnLine(p1[0], p1[1], xs, ys, -width)
            ##else:
                ##if p1[1] > ys:
                    ##[xT_1, yT_1] = self.shiftPointOnLine(p1[0], p1[1], xs, ys, -width)
                    ##[xT_4, yT_4] = self.shiftPointOnLine(p1[0], p1[1], xs, ys, width)
                ##else:
                    ##[xT_1, yT_1] = self.shiftPointOnLine(p1[0], p1[1], xs, ys, width)
                    ##[xT_4, yT_4] = self.shiftPointOnLine(p1[0], p1[1], xs, ys, -width)
                    
            ##
            #[xT_2, yT_2] = self.obrocPunkt2([xT_1, yT_1], [xs, ys], curve)
            #[xT_5, yT_5] = self.obrocPunkt2([xT_4, yT_4], [xs, ys], curve)
            
            ### outer arc
            #[xT_3, yT_3] = self.arcMidPoint([xT_1, yT_1], [xT_2, yT_2], curve)
            
            #mainObj = [Part.Arc(FreeCAD.Base.Vector(xT_1, yT_1, 0), FreeCAD.Base.Vector(xT_3, yT_3, 0), FreeCAD.Base.Vector(xT_2, yT_2, 0)).toShape()]
            #self.addObject(Part.Wire(mainObj))
            ### inner arc
            #[xT_6, yT_6] = self.arcMidPoint([xT_4, yT_4], [xT_5, yT_5], curve)
            
            #mainObj = [Part.Arc(FreeCAD.Base.Vector(xT_4, yT_4, 0), FreeCAD.Base.Vector(xT_6, yT_6, 0), FreeCAD.Base.Vector(xT_5, yT_5, 0)).toShape()]
            #self.addObject(Part.Wire(mainObj))
                

            #if cap == 'flat':
                #mainObj = [Part.Line(FreeCAD.Base.Vector(xT_1, yT_1, 0), FreeCAD.Base.Vector(xT_4, yT_4, 0)).toShape()]
                #self.addObject(Part.Wire(mainObj))
                ###
                #mainObj = [Part.Line(FreeCAD.Base.Vector(xT_2, yT_2, 0), FreeCAD.Base.Vector(xT_5, yT_5, 0)).toShape()]
                #self.addObject(Part.Wire(mainObj))
            #else:
                ##start
                #if curve > 0:
                    #if a > 0:
                        #if xT_1 > xs:
                            #[xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], 180)
                        #else:
                            #[xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], -180)
                    #else:
                        #if xT_1 > xs:
                            #[xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], 180)
                        #else:
                            #[xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], -180)
                #else:
                    #if a > 0:
                        #if xT_1 > xs:
                            #[xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], -180)
                        #else:
                            #[xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], 180)
                    #else:
                        #if xT_1 > xs:
                            #[xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], -180)
                        #else:
                            #[xT_7, yT_7] = self.arcMidPoint([xT_1, yT_1], [xT_4, yT_4], 180)
                
                #mainObj = [Part.Arc(FreeCAD.Base.Vector(xT_1, yT_1, 0), FreeCAD.Base.Vector(xT_7, yT_7, 0), FreeCAD.Base.Vector(xT_4, yT_4, 0)).toShape()]
                #self.addObject(Part.Wire(mainObj))
                
                ##end
                #b = (ys - p2[1]) / (xs - p2[0])
                
                #if curve > 0:
                    #if b > 0:
                        #if xT_2 > xs:
                            #if xT_2 > xT_5:
                                #[xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], 180)
                            #else:
                                #[xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], -180)
                        #else:
                            #if xT_2 > xT_5:
                                #[xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], -180)
                            #else:
                                #[xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], 180)
                    #else:
                        #if xT_2 > xs:
                            #if xT_2 > xT_5:
                                #[xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], 180)
                            #else:
                                #[xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], -180)
                        #else:
                            #if xT_2 > xT_5:
                                #[xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], -180)
                            #else:
                                #[xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], 180)
                #else:
                    #if b > 0:
                        #if xT_2 > xs:
                            #if xT_2 > xT_5:
                                #[xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], -180)
                            #else:
                                #[xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], 180)
                        #else:
                            #if xT_2 > xT_5:
                                #[xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], 180)
                            #else:
                                #[xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], -180)
                    #else:
                        #if xT_2 > xs:
                            #if xT_2 > xT_5:
                                #[xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], -180)
                            #else:
                                #[xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], 180)
                        #else:
                            #if xT_2 > xT_5:
                                #[xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], 180)
                            #else:
                                #[xT_8, yT_8] = self.arcMidPoint([xT_2, yT_2], [xT_5, yT_5], -180)
                        
                            
                        
                #mainObj = [Part.Arc(FreeCAD.Base.Vector(xT_2, yT_2, 0), FreeCAD.Base.Vector(xT_8, yT_8, 0), FreeCAD.Base.Vector(xT_5, yT_5, 0)).toShape()]
                #self.addObject(Part.Wire(mainObj))

                ##mainObj = [Part.Circle(FreeCAD.Vector(p1[0], p1[1]), FreeCAD.Vector(0, 0, 1), width).toShape()]
                ##self.addObject(Part.Wire(mainObj))
                ####
                ##mainObj = [Part.Circle(FreeCAD.Vector(p2[0], p2[1]), FreeCAD.Vector(0, 0, 1), width).toShape()]
                ##self.addObject(Part.Wire(mainObj))
            ## center line
            #mainObj = [Part.Arc(FreeCAD.Base.Vector(p1[0], p1[1], 0), FreeCAD.Base.Vector(x3, y3, 0), FreeCAD.Base.Vector(p2[0], p2[1], 0)).toShape()]
            #self.addObject(Part.Wire(mainObj))
            
            ###[x3, y3] = self.arcMidPoint(p2, p1, curve)
            ###mainObj = [Part.Arc(FreeCAD.Base.Vector(p1[0], p1[1], 0), FreeCAD.Base.Vector(x3, y3, 0), FreeCAD.Base.Vector(p2[0], p2[1], 0)).toShape()]
            ###return Part.Wire(mainObj)

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
        wir.append(Part.Arc(FreeCAD.Base.Vector(p1[0], p1[1], 0), FreeCAD.Base.Vector(p2[0], p2[1], 0), FreeCAD.Base.Vector(p3[0], p3[1], 0)))

        p1 = [0 - r, dlugosc]
        p2 = [0, dlugosc + r]
        p3 = [0 + r, dlugosc]
        wir.append(Part.Arc(FreeCAD.Base.Vector(p1[0], p1[1], 0), FreeCAD.Base.Vector(p2[0], p2[1], 0), FreeCAD.Base.Vector(p3[0], p3[1], 0)))

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
            hole = Part.Face(hole)
            
            return mainObj.cut(hole)
        return mainObj
    
    def makeFace(self, mainObj):
        return Part.Face(mainObj)


class layerPolygonObject(objectWire):
    def __init__(self, obj, typeL):
        self.points = []
        self.name = ''
        self.isolate = 0
        self.paths = []
        
        self.Type = typeL
        obj.Proxy = self
        self.obj = obj
    
    def updatePosition_Z(self, fp, dummy=None):
        if 'tPath' in self.Type:
            thickness = getPCBheight()[1]
            
            fp.Placement.Base.z = thickness + 0.01
        else:
            fp.Placement.Base.z = -0.01
    
    def generuj(self, fp):
        pass
        #polygon = 
        
        #polygon.Placement.Base.z = fp.Placement.Base.z
        #fp.Shape = polygon
            
    def onChanged(self, fp, prop):
        pass
    
    def __getstate__(self):
        return self.Type
        
    def __setstate__(self, state):
        self.Type = state
        
    def execute(self, fp):
        pass


class viewProviderLayerPolygonObject:
    def __init__(self, obj):
        ''' Set this object to the proxy object of the actual view provider '''
        obj.Proxy = self
        
    def attach(self, obj):
        ''' Setup the scene sub-graph of the view provider, this method is mandatory '''
        return

    def updateData(self, fp, prop):
        ''' If a property of the handled feature has changed we have the chance to handle this here '''
        return

    def getDisplayModes(self, obj):
        ''' Return a list of display modes. '''
        modes = []
        return modes

    def getDefaultDisplayMode(self):
        ''' Return the name of the default display mode. It must be defined in getDisplayModes. '''
        return "Wire Frame"

    def setDisplayMode(self, mode):
        ''' Map the display mode defined in attach with those defined in getDisplayModes.
        Since they have the same names nothing needs to be done. This method is optinal.
        '''
        return mode

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
        #***************************************************************
        #   Author:     Gentleface custom icons design agency (http://www.gentleface.com/)
        #   License:    Creative Commons Attribution-Noncommercial 3.0
        #   Iconset:    Mono Icon Set
        #***************************************************************
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



class layerPathObject(objectWire):
    def __init__(self, obj, typeL):
        self.spisObiektow = []
        
        self.Type = typeL
        obj.Proxy = self
        self.holes = False
        self.obj = obj
        self.defHeight = 0.035
        self.cutToBoard = False
        
    def changeColor(self):
        import random
        FreeCAD.Console.PrintWarning(u"{0} \n".format(self.signals))
        
        col = []
        for i in self.signals:
            R = random.uniform(0, 1)
            G = random.uniform(0, 1)
            B = random.uniform(0, 1)
            for j in i:
                col.append((R, G, B, 0.0))
            
            
        self.obj.ViewObject.DiffuseColor = col
        self.obj.ViewObject.update()
        
    def updatePosition_Z(self, fp, dummy=None):
        if 'tPath' in self.Type:
            thickness = getPCBheight()[1]
            
            fp.Placement.Base.z = thickness
        else:
            fp.Placement.Base.z = -self.defHeight / 1000.
            
    def updateHoles(self, fp):
        self.generuj(fp)

    def generuj(self, fp):
        if len(self.spisObiektow):
            obiekty = []
            
            if self.cutToBoard:
                board = OpenSCAD2Dgeom.edgestofaces(FreeCAD.ActiveDocument.Board.Border.Shape.Edges)
                board = board.extrude(FreeCAD.Base.Vector(0, 0, 2))
            
            for i in self.spisObiektow:
                if i[0] == 'arc':
                    p1 = [i[1], i[2]]
                    p2 = [i[3], i[4]]
                    curve = i[5]
                    width = i[6]
                    cap = i[7]

                    o = self.createArc(p1, p2, curve, width, cap)
                    if self.cutToBoard:
                        o = board.common(o)
                    o = o.extrude(FreeCAD.Base.Vector(0, 0, self.defHeight / 1000.))
                    obiekty.append(o)
                elif i[0] == 'circle':
                    x = i[1]
                    y = i[2]
                    r = i[3]
                    width = i[4]
                    
                    o = self.createCircle(x, y, r, width)
                    if self.cutToBoard:
                        o = board.common(o)
                    o = o.extrude(FreeCAD.Base.Vector(0, 0, self.defHeight / 1000.))
                    obiekty.append(o)
                elif i[0] == 'line':
                    x1 = i[1]
                    y1 = i[2]
                    x2 = i[3]
                    y2 = i[4]
                    width = i[5]
                    
                    o = self.createLine(x1, y1, x2, y2, width)
                    if self.cutToBoard:
                        o = board.common(o)
                    o = o.extrude(FreeCAD.Base.Vector(0, 0, self.defHeight / 1000.))
                    obiekty.append(o)
            #
            path = Part.makeCompound(obiekty)
            # cut to board shape
            #if self.cutToBoard:
                #path = cutToBoardShape(path)
            ###################################################
            #if FreeCAD.ActiveDocument.Board.Display:
                #holes = OpenSCAD2Dgeom.edgestofaces(FreeCAD.ActiveDocument.Board.Holes.Shape.Edges)
                ##holes = holes.extrude(FreeCAD.Base.Vector(0, 0, 0.2))
            
                #path = shapes.cut(holes)
            #else:
                #path = shapes
            #
            #path = path.extrude(FreeCAD.Base.Vector(0, 0, self.defHeight / 1000.))
            path.Placement.Base.z = fp.Placement.Base.z
            fp.Shape = path
            
    def onChanged(self, fp, prop):
        pass
    
    def __getstate__(self):
        return [self.Type, self.cutToBoard, str(self.spisObiektow), self.defHeight]
        
    def __setstate__(self, state):
        self.Type = state[0]
        self.cutToBoard = state[1]
        self.spisObiektow = eval(state[2])
        self.defHeight = state[3]
        
    def execute(self, fp):
        self.generuj(fp)


#class viewProviderLayerPathObject:
    #def __init__(self, obj):
        #''' Set this object to the proxy object of the actual view provider '''
        #obj.Proxy = self
        
    #def attach(self, obj):
        #''' Setup the scene sub-graph of the view provider, this method is mandatory '''
        #return

    #def updateData(self, fp, prop):
        #''' If a property of the handled feature has changed we have the chance to handle this here '''
        #return

    #def getDisplayModes(self, obj):
        #''' Return a list of display modes. '''
        #modes = []
        #return modes

    #def getDefaultDisplayMode(self):
        #''' Return the name of the default display mode. It must be defined in getDisplayModes. '''
        #return "Wire Frame"

    #def setDisplayMode(self, mode):
        #''' Map the display mode defined in attach with those defined in getDisplayModes.
        #Since they have the same names nothing needs to be done. This method is optinal.
        #'''
        #return mode

    #def onChanged(self, vp, prop):
        #vp.setEditorMode("LineColor", 2)
        #vp.setEditorMode("DrawStyle", 2)
        #vp.setEditorMode("LineWidth", 2)
        #vp.setEditorMode("PointColor", 2)
        #vp.setEditorMode("PointSize", 2)
        #vp.setEditorMode("Deviation", 2)
        #vp.setEditorMode("Lighting", 2)
        #vp.setEditorMode("Transparency", 2)
        #vp.setEditorMode("BoundingBox", 2)
        #if hasattr(vp, "AngularDeflection"):
            #vp.setEditorMode("AngularDeflection", 2)
        
        #if prop == "ShapeColor":
            #vp.LineColor = vp.ShapeColor
            #vp.PointColor = vp.ShapeColor

    #def getIcon(self):
        #''' Return the icon in XMP format which will appear in the tree view. This method is optional
        #and if not defined a default icon is shown.
        #'''
        ##***************************************************************
        ##   Author:     Gentleface custom icons design agency (http://www.gentleface.com/)
        ##   License:    Creative Commons Attribution-Noncommercial 3.0
        ##   Iconset:    Mono Icon Set
        ##***************************************************************
        #return ":/data/img/layers_TI.svg"

    #def __getstate__(self):
        #''' When saving the document this object gets stored using Python's cPickle module.
        #Since we have some un-pickable here -- the Coin stuff -- we must define this method
        #to return a tuple of all pickable objects or None.
        #'''
        #return None

    #def __setstate__(self, state):
        #''' When restoring the pickled object from document we have the chance to set some
        #internals here. Since no data were pickled nothing needs to be done here.
        #'''
        #return None
#####################################
#####################################
#####################################

class layerSilkObject(objectWire):
    def __init__(self, obj, typeL):
        #obj.addProperty("App::PropertyLinkSub", "Holes", "Holes", "Reference to volume of part").Holes = (FreeCAD.ActiveDocument.Board, 'Holes')
        self.spisObiektow = []
        self.Type = ['layer'] + typeL
        obj.Proxy = self
        self.holes = False
        self.cutToBoard = False
        
        self.defHeight = 35
        self.spisObiektowTXT = []
        self.side = 1  # 1-top  0-bottom

    ################
    ################
    
    def addLine(self, x1, y1, x2, y2):
        if x1 == x2 and y1 == y2:
            self.spisObiektowTXT[-1]['objects'].append(['point', x1, y1])
        else:
            self.spisObiektowTXT[-1]['objects'].append(['line', x1, y1, x2, y2])
    
    def addDrillCenter(self, xs, ys, r1, r2):
        self.spisObiektowTXT[-1]['objects'].append(['drillCenter', xs, ys, r1, r2])
    
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
            #if w > 0:
                #mainObj = self.cutHole(mainObj, [xs, ys, r - w / 2.])
            self.spisObiektowTXT.append(mainObj)

    #def addArc(self, x, y, r, startAngle, stopAngle):
        #self.spisObiektowTXT[-1]['objects'].append(['arc', x, y, r, startAngle, stopAngle])
    
    def addArc3P(self, p1, p2, p3):
        self.spisObiektowTXT[-1]['objects'].append(['arc3P', p1, p2, p3])
    
    #def addArc_v2(self, p1, p2, curve, width=0, cap='round'):
        #return self.spisObiektowTXT[-1]['objects'].append(['arcV2', p1, p2, curve, width, cap])
        
    def addElipse(self, x, y, r1, r2, w=0):
        self.spisObiektowTXT[-1]['objects'].append(['elipse', x, y, r1, r2, w])
        
    ################
    ################
    #def createArc(self, x, y, r, startAngle, stopAngle):
        #return Part.ArcOfCircle(Part.Circle(FreeCAD.Vector(x, y, 0), FreeCAD.Vector(0, 0, 1), r), startAngle, stopAngle)
    
    def createArc3P(self, p1, p2, p3):
        return Part.Arc(FreeCAD.Base.Vector(p1[0], p1[1], 0), FreeCAD.Base.Vector(p2[0], p2[1], 0), FreeCAD.Base.Vector(p3[0], p3[1], 0))
    
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
    
    def setFace(self, param=True):
        self.spisObiektowTXT[-1] = self.makeFace(self.spisObiektowTXT[-1])
    
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
            #if i[0] == 'circle':
                #xs = i[1]
                #ys = i[2]
                #r = i[3]
                #w = i[4]
                
                #if w > 0:
                    #data.append(self.createCircle2(xs, ys, r + w / 2.))
                    #obj['holes'].append([xs, ys, r - w / 2.])
                #else:
                    #data.append(self.createCircle2(xs, ys, r))
            #elif i[0] == 'drillCenter':
                #xs = i[1]
                #ys = i[2]
                #r1 = i[3]
                #r2 = i[4]
                
                #data.append(self.createCircle2(xs, ys, r1))
                #obj['holes'].append([xs, ys, r2])
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
            #elif i[0] == 'line':
                #x1 = i[1]
                #y1 = i[2]
                #x2 = i[3]
                #y2 = i[4]
                
                #data.append(self.createLine2(x1, y1, x2, y2))
            #elif i[0] == 'arc3P':
                #p1 = i[1]
                #p2 = i[2]
                #p3 = i[3]
                
                #data.append(self.createArc3P(p1, p2, p3))
            elif i[0] == 'point':
                x = i[1]
                y = i[2]
                data.append(self.makePoint(x, y))
            elif i[0] == 'skip':
                FreeCAD.Console.PrintWarning("It is not possible to generate pad ({0}). Skipped.\n".format(i[1]))
                continue
            #elif i[0] == 'arcV2':
                #p1 = i[1]
                #p2 = i[2]
                #curve = i[3]
                #width = i[4]
                #cap = i[5]
                
                #data.append(self.makeArc_v2(p1, p2, curve, width, cap))
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
            center = FreeCAD.Base.Vector(obj['placement']['center'][0], obj['placement']['center'][1],obj['placement']['center'][2])
            rot = FreeCAD.Rotation(FreeCAD.Vector(0, 0, 1), obj['placement']['angle'])
            
            mainObj.Placement = FreeCAD.Base.Placement(pos_1, rot, center)
        if len(obj['rotations']):
            for i in obj['rotations']:
                self.rotateObj(mainObj, i)
        if obj['side']['side']:
            self.changeSide(mainObj, obj['side'])
        
        return mainObj
    
    def generuj(self, fp):
        if len(self.spisObiektowTXT):
            #if self.cutToBoard:
                #board = OpenSCAD2Dgeom.edgestofaces(FreeCAD.ActiveDocument.Board.Border.Shape.Edges)
                #board = board.extrude(FreeCAD.Base.Vector(0, 0, 2))
            
            #pads = []
            #for i in self.spisObiektowTXT:
                #data = self.makePolygon(i)
                
                #if not data:
                    #continue
                
                #pads.append(data)
                
                #if self.cutToBoard:
                    #data = board.common(data)
            pads = Part.makeCompound(self.spisObiektowTXT)
            pads = pads.extrude(FreeCAD.Base.Vector(0, 0, self.defHeight / 1000.))
            
            pads.Placement.Base.z = fp.Placement.Base.z
            fp.Shape = pads
        
        #if len(self.spisObiektowTXT):
            #if 'tSilk' in self.Type or 'bSilk' in self.Type or 'tDocu' in self.Type or 'bDocu' in self.Type or 'PCBcenterDrill' in self.Type:
                #if self.cutToBoard:
                    #board = OpenSCAD2Dgeom.edgestofaces(FreeCAD.ActiveDocument.Board.Border.Shape.Edges)
                    #board = board.extrude(FreeCAD.Base.Vector(0, 0, 2))
                
                #pads = []
                #for i in self.spisObiektowTXT:
                    #data = self.makePolygon(i)
                    #if not data:
                        #continue
                    
                    #if self.cutToBoard:
                        #data = board.common(data)
                    
                    #if 'PCBcenterDrill' in self.Type:
                        #data = data.extrude(FreeCAD.Base.Vector(0, 0, getPCBheight()[1]))
                    #else:
                        #data = data.extrude(FreeCAD.Base.Vector(0, 0, self.defHeight / 1000.))
                    #pads.append(data)
                
                #pads = Part.makeCompound(pads)
                #pads.Placement.Base.z = fp.Placement.Base.z
                #fp.Shape = pads
            #else:
                #pads = []
                #for i in self.spisObiektowTXT:
                    #pads.append(self.makePolygon(i))
                #pads = Part.makeCompound(pads)
                
                #if FreeCAD.ActiveDocument.Board.Display:
                    #try:
                        #holes = []
                        #for i in FreeCAD.ActiveDocument.Board.Holes.Shape.Wires:
                            #holes.append(Part.Face(i))
                        
                        #if len(holes):
                            #pads = pads.cut(Part.makeCompound(holes))
                        #else:
                            #pads = pads
                    #except Exception as e:
                        #FreeCAD.Console.PrintWarning("{0} \n".format(e))
                
                ## cut to board shape
                #if self.cutToBoard:
                    #pads = cutToBoardShape(pads)
                ####################################################
                #pads = pads.extrude(FreeCAD.Base.Vector(0, 0, self.defHeight / 1000.))
                #pads.Placement.Base.z = fp.Placement.Base.z
                #fp.Shape = pads
    
    ################
    # shapes
    ################
    def addRectangle(self, x1, y1, x2, y2):
        if x1 == x2 and y1 == y2:
            self.spisObiektowTXT.append(None)
            return
            #self.spisObiektowTXT[-1]['objects'].append(['skip', "point [{0}, {1}] detected instead rectangle".format(x1, y1)])
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
                [x - w_pP + w_zP + w_aP, y - h_pP, 0, x + w_pP, y -h_pP + h_zP, 0],
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
    
    def addPolygon(self, polygon):
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
        self.spisObiektowTXT.append(mainObj)
    
    def addArcWidth(self, p1, p2, curve, width=0.02, cap='round'):
        try:
            if width <= 0:
                width = 0.02
                
            width /= 2.
                
            [x3, y3] = self.arcMidPoint(p1, p2, curve)
            [xs, ys] = self.arcCenter(p1[0], p1[1], p2[0], p2[1], x3, y3)
            ##
            #a = (ys - p1[1]) / (xs - p1[0])
            [xT_1, yT_1] = self.shiftPointOnLine(p1[0], p1[1], xs, ys, width)
            [xT_4, yT_4] = self.shiftPointOnLine(p1[0], p1[1], xs, ys, -width)
            ###
            [xT_2, yT_2] = self.obrocPunkt2([xT_1, yT_1], [xs, ys], curve)
            [xT_5, yT_5] = self.obrocPunkt2([xT_4, yT_4], [xs, ys], curve)
            ########
            ########
            wir = []
            ## outer arc
            [xT_3, yT_3] = self.arcMidPoint([xT_1, yT_1], [xT_2, yT_2], curve)
            object_1 = self.createArc3P([xT_1, yT_1], [xT_3, yT_3], [xT_2, yT_2])
            ## inner arc
            [xT_6, yT_6] = self.arcMidPoint([xT_4, yT_4], [xT_5, yT_5], curve)
            object_2 = self.createArc3P([xT_4, yT_4], [xT_6, yT_6], [xT_5, yT_5])
            ##
            if cap == 'flat':
                object_3 = self.createLine2(xT_1, yT_1, xT_4, yT_4)
                object_4 = self.createLine2(xT_2, yT_2, xT_5, yT_5)
            else:
                #start
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
                        #a = (ys - p1[1]) / (xs - p1[0])
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
                #end
                #b = (ys - p2[1]) / (xs - p2[0])
                
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
            #self.addPlacement([x1, y1, 0], kat, [0, 0, 0])
            #return mainObj
        except Exception as e:
            FreeCAD.Console.PrintWarning(u"{0}\n".format(e))
    
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
        #self.addPlacement([x1, y1, 0], kat, [0, 0, 0])
        
        #
        mainObj = Part.Shape([line_1,  arc_1, line_2,arc_2])
        mainObj = Part.Wire(mainObj.Edges)
        self.spisObiektowTXT.append(mainObj)
        self.addPlacement([x1, y1, 0], kat, [0, 0, 0])
        #return mainObj

    #def addObject(self, mainObj):
        #self.spisObiektow.append(mainObj)
 
    #def makeLine(self, x1, y1, x2, y2):
        #if not [x1, y1] == [x2, y2]:
            #return Part.Line(FreeCAD.Base.Vector(x1, y1, 0), FreeCAD.Base.Vector(x2, y2, 0)).toShape()
        #else:
            #return Part.Line(FreeCAD.Base.Vector(x1, y1, 0), FreeCAD.Base.Vector(x2 + 0.000001, y2 + 0.000001, 0)).toShape()

    #def rotateObj(self, mainObj, rot):
        #return mainObj.rotate(FreeCAD.Vector(rot[0], rot[1], 0), FreeCAD.Vector(0, 0, 1), rot[2])
    
    #def changeSide(self, mainObj, X1, Y1, warst):
        #if warst == 0:
            #mainObj.rotate(FreeCAD.Vector(X1, Y1, 0), FreeCAD.Vector(0, 1, 0), 180)
    
    #def addElipse(self, center, r1, r2):
        #if r1 > r2:
            #mainObj = [Part.Ellipse(FreeCAD.Vector(center[0], center[1], 0), r1, r2).toShape()]
            
            #return Part.Wire(mainObj)
        #else:
            #mainObj = Part.Wire([Part.Ellipse(FreeCAD.Vector(center[0], center[1], 0), r2, r1).toShape()])
            #self.rotateObj(mainObj, [center[0], center[1], 90])
            
            #return mainObj
            
    ##def addCrircle_2(self, x, y, r):
        ##mainObj = [Part.Circle(FreeCAD.Vector(x, y), FreeCAD.Vector(0, 0, 1), r).toShape()]
        
        ##return Part.Wire(mainObj)
        
    #def addCrircle_2(self, x, y, r, w=0):
        #return self.createCircle(x, y, r, w)
    
    #def makePoint(self, x, y):
        #wir = []
        #wir.append(Part.Point(FreeCAD.Base.Vector(x, y, 0)))
        
        #mainObj = Part.Shape(wir)
        
        #return mainObj
    
    #def addLine_2(self, x1, y1, x2, y2, width=0.01):
        #if x1 == x2 and y1 == y2:
            #return self.makePoint(x1, y1)
        #else:
            #return self.createLine(x1, y1, x2, y2, width)

    #def addBSpline(self, points):
        #spline = Part.BSplineCurve()
        #spline.interpolate(points, False)
        #spline = spline.toShape()
        #return Part.Wire(spline)
    
    ##def addArc(self, x, y, r, startAngle, stopAngle, rot2=[], warst=1):
    #def addArc(self, x, y, r, startAngle, stopAngle):
        #mainObj = [Part.ArcOfCircle(Part.Circle(FreeCAD.Vector(x, y, 0), FreeCAD.Vector(0, 0, 1), r), startAngle, stopAngle).toShape()]
        #return Part.Wire(mainObj)
        
    #def addArc_2(self, p1, p2, curve):
        #[x3, y3] = self.arcMidPoint(p2, p1, curve)
        #mainObj = [Part.Arc(FreeCAD.Base.Vector(p1[0], p1[1], 0), FreeCAD.Base.Vector(x3, y3, 0), FreeCAD.Base.Vector(p2[0], p2[1], 0)).toShape()]
        #return Part.Wire(mainObj)

    #def addArc_3(self, p1, p2, curve, width=0, cap='round'):
        #return self.createArc(p1, p2, curve, width, cap)

    #def addRectangle_2(self, x1, y1, x2, y2):
        #obj = []
        #obj.append(self.makeLine(x1, y1, x2, y1))
        #obj.append(self.makeLine(x2, y1, x2, y2))
        #obj.append(self.makeLine(x2, y2, x1, y2))
        #obj.append(self.makeLine(x1, y2, x1, y1))

        #return Part.Wire(obj)
    
    #def addOctagon_2(self, dane):
        #punkty = []
        #for i in dane:
            #(x1, y1, z1, x2, y2, z2) = i
            #punkty.append(self.makeLine(x1, y1, x2, y2))

        #return Part.Wire(punkty)

    #def addOffset_2(self, x, y, R, e):
        #punkty = []
        
        #punkty.append(Part.Line(FreeCAD.Base.Vector(x, y + R, 0), FreeCAD.Base.Vector(x + R + e / 2, y + R, 0)))
        #punkty.append(Part.Line(FreeCAD.Base.Vector(x, y - R, 0), FreeCAD.Base.Vector(x + R + e / 2, y - R, 0)))

        #p1 = [x + R + e / 2, y + R]
        #p2 = [x + R + e / 2, y - R]
        #p3 = [x + R + e, y]
        #punkty.append(Part.Arc(FreeCAD.Base.Vector(p1[0], p1[1], 0), FreeCAD.Base.Vector(p3[0], p3[1], 0), FreeCAD.Base.Vector(p2[0], p2[1], 0)))

        #p1 = [x, y + R]
        #p2 = [x, y - R]
        #p3 = [x - R, y]
        #punkty.append(Part.Arc(FreeCAD.Base.Vector(p1[0], p1[1], 0), FreeCAD.Base.Vector(p3[0], p3[1], 0), FreeCAD.Base.Vector(p2[0], p2[1], 0)))
        
        #mainObj = Part.Shape(punkty)
        #return Part.Wire(mainObj.Edges)
    
    ##def addLong_2(self, x, y, R, e, DD):
        ##punkty = []

        ##punkty.append(Part.Line(FreeCAD.Base.Vector(x - R + e, y + DD, 0), FreeCAD.Base.Vector(x + R - e, y + DD, 0)))
        ##punkty.append(Part.Line(FreeCAD.Base.Vector(x - R + e, y - DD, 0), FreeCAD.Base.Vector(x + R - e, y - DD, 0)))

        ##p1 = [x + R - e, y + DD]
        ##p2 = [x + R - e, y - DD]
        ##p3 = [x + R + e, y]
        ##punkty.append(Part.Arc(FreeCAD.Base.Vector(p1[0], p1[1], 0), FreeCAD.Base.Vector(p3[0], p3[1], 0), FreeCAD.Base.Vector(p2[0], p2[1], 0)))
        
        ##p1 = [x - R + e, y + DD]
        ##p2 = [x - R + e, y - DD]
        ##p3 = [x - R - e, y]
        ##punkty.append(Part.Arc(FreeCAD.Base.Vector(p1[0], p1[1], 0), FreeCAD.Base.Vector(p3[0], p3[1], 0), FreeCAD.Base.Vector(p2[0], p2[1], 0)))

        ##mainObj = Part.Shape(punkty)
        ##return Part.Wire(mainObj.Edges)
        
    #def addPadLong(self, x, y, dx, dy, perc, typ=0):
        #curve = 90.
        #if typ == 0:  # %
            #if perc > 100.:
                #perc == 100.
            
            #if dx > dy:
                #e = dy * perc / 100.
            #else:
                #e = dx * perc / 100.
        #else:  # mm
            #e = perc
        
        #p1 = [x - dx + e, y - dy, 0]
        #p2 = [x + dx - e, y - dy, 0]
        #p3 = [x + dx, y - dy + e, 0]
        #p4 = [x + dx, y + dy - e, 0]
        #p5 = [x + dx - e, y + dy, 0]
        #p6 = [x - dx + e, y + dy, 0]
        #p7 = [x - dx, y + dy - e, 0]
        #p8 = [x - dx, y - dy + e, 0]
        ##
        #punkty = []

        #if p1 != p2:
            #punkty.append(Part.Line(FreeCAD.Base.Vector(p1[0], p1[1], 0), FreeCAD.Base.Vector(p2[0], p2[1], 0)))

        #if p2 != p3:
            #p9 = self.arcMidPoint(p2, p3, curve)
            #punkty.append(Part.Arc(FreeCAD.Base.Vector(p2[0], p2[1], 0), FreeCAD.Base.Vector(p9[0], p9[1], 0), FreeCAD.Base.Vector(p3[0], p3[1], 0)))
            
        #if p3 != p4:
            #punkty.append(Part.Line(FreeCAD.Base.Vector(p3[0], p3[1], 0), FreeCAD.Base.Vector(p4[0], p4[1], 0)))

        #if p4 != p5:
            #p10 = self.arcMidPoint(p4, p5, curve)
            #punkty.append(Part.Arc(FreeCAD.Base.Vector(p4[0], p4[1], 0), FreeCAD.Base.Vector(p10[0], p10[1], 0), FreeCAD.Base.Vector(p5[0], p5[1], 0)))
            
        #if p5 != p6:
            #punkty.append(Part.Line(FreeCAD.Base.Vector(p5[0], p5[1], 0), FreeCAD.Base.Vector(p6[0], p6[1], 0)))

        #if p6 != p7:
            #p11 = self.arcMidPoint(p6, p7, curve)
            #punkty.append(Part.Arc(FreeCAD.Base.Vector(p6[0], p6[1], 0), FreeCAD.Base.Vector(p11[0], p11[1], 0), FreeCAD.Base.Vector(p7[0], p7[1], 0)))

        #if p7 != p8:
            #punkty.append(Part.Line(FreeCAD.Base.Vector(p7[0], p7[1], 0), FreeCAD.Base.Vector(p8[0], p8[1], 0)))

        #if p8 != p1:
            #p12 = self.arcMidPoint(p8, p1, curve)
            #punkty.append(Part.Arc(FreeCAD.Base.Vector(p8[0], p8[1], 0), FreeCAD.Base.Vector(p12[0], p12[1], 0), FreeCAD.Base.Vector(p1[0], p1[1], 0)))
        
        #obj = Part.Shape(punkty)
        #obj = Part.Wire(obj.Edges)
        
        #return obj
    
    #def arcMidPoint(self, prev_vertex, vertex, angle):
        #if len(prev_vertex) == 3:
            #[x1, y1, z1] = prev_vertex
        #else:
            #[x1, y1] = prev_vertex
            
        #if len(vertex) == 3:
            #[x2, y2, z2] = vertex
        #else:
            #[x2, y2] = vertex
        
        #angle = radians(angle / 2)
        #basic_angle = atan2(y2 - y1, x2 - x1) - pi / 2
        #shift = (1 - cos(angle)) * hypot(y2 - y1, x2 - x1) / 2 / sin(angle)
        #midpoint = [(x2 + x1) / 2 + shift * cos(basic_angle), (y2 + y1) / 2 + shift * sin(basic_angle)]
        
        #return midpoint
    
    #def addPolygonFull(self, dane, fullMAIN=True):
        #punkty = []
        #fullPol = True
        #for i in dane:
            #if i[0] == 'Arc':
                #fullPol = True
                #[elemType, x1, y1, x2, y2, curve] = i
                
                #p1 = [x1, y1]
                #p3 = [x2, y2]
                
                #punkty.append(self.addArc_2(p1, p3, curve))
            #else:
                #(elemType, x1, y1, x2, y2) = i
                #punkty.append(self.makeLine(x1, y1, x2, y2))
        
        #if fullPol and fullMAIN:
            #mainObj = Part.Wire(punkty)
            #mainObj = Part.Face(mainObj)
        #else:
            #mainObj = Part.makeCompound(punkty)
        #return mainObj
        
    def updateHoles(self, fp):
        self.generuj(fp)
        
    def updatePosition_Z(self, fp, dummy=None):
        if self.side:  # top side
            fp.Placement.Base.z = getPCBheight()[1] + self.defHeight / 1000.
        else:
            fp.Placement.Base.z = -self.defHeight / 1000.

        #if 'tSilk' in self.Type or 'tDocu' in self.Type or 'tPad' in self.Type:
            #fp.Placement.Base.z = thickness
        #elif 'PCBcenterDrill' in self.Type:
            #pass
        #else:
            #fp.Placement.Base.z = -self.defHeight  / 1000.

    def onChanged(self, fp, prop):
        pass
        
    def execute(self, fp):
        pass
        #self.generuj(fp)
        
    def __getstate__(self):
        return [self.Type, self.cutToBoard, self.defHeight, self.holes, self.side]
        #return [self.Type, self.cutToBoard, self.spisObiektowTXT, self.defHeight, self.holes, self.side]
        
    def __setstate__(self, state):
        self.Type = state[0]
        self.cutToBoard = state[1]
        self.defHeight = state[2]
        self.holes = state[3]
        self.side = state[4]
        #self.spisObiektowTXT = eval(state[5])


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
        #***************************************************************
        #   Author:     Gentleface custom icons design agency (http://www.gentleface.com/)
        #   License:    Creative Commons Attribution-Noncommercial 3.0
        #   Iconset:    Mono Icon Set
        #***************************************************************
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
        self.layerHeight = None
        self.layerReversed = None
        self.Type = typeL
        self.z = 0
        
        self.setLayerSide()
        if not set(self.Type).intersection(set(['tRestrict', 'bRestrict', 'vRestrict', 'vRouteOutline', 'vPlaceOutline'])):
            obj.addProperty("App::PropertyLength", "Height", "Base", "Height of the element").Height = self.layerHeight
        obj.addProperty("App::PropertyLink", "Base", "Draft", "The base object is the wire is formed from 2 objects")
        obj.setEditorMode("Placement", 2)
        obj.Proxy = self
        
    def updatePosition_Z(self, fp, dummy=None):
        if self.Type.startswith('t'):
            self.z = getPCBheight()[1]
        elif self.Type.startswith('v'):  # gorna oraz dolna warstwa
            self.z = -0.5
            self.layerHeight = getPCBheight()[1] + 1.0
        else:  # bottomSide
            self.z = 0.0
        
        fp.Base.Placement.Base.z = self.z
        self.createGeometry(fp)

    def setLayerSide(self):
        if self.Type.startswith('t'):
            self.layerReversed = False
            self.layerHeight = 0.5
            self.z = getPCBheight()[1]
        elif self.Type.startswith('v'):  # gorna oraz dolna warstwa
            self.layerReversed = False
            self.layerHeight = getPCBheight()[1] + 1.0
            self.z = -0.5
        else:  # bottomSide
            self.layerReversed = True
            self.layerHeight = 0.5
            self.z = 0.0

    def execute(self, fp):
        self.createGeometry(fp)

    def onChanged(self, fp, prop):
        if prop in ["Base"]:
            try:
                if fp.Base.Placement.Base.z != self.z:
                    fp.Base.Placement.Base.z = self.z
            except:
                pass
            
            self.createGeometry(fp)
        elif prop == "Height" and fp.Height.Value > 0:
            self.layerHeight = fp.Height.Value
            #fp.Base.Placement.Base.z = self.z
            self.createGeometry(fp)
    
    def createGeometry(self, fp):
        try:
            if fp.Base:
                if fp.Base.isDerivedFrom("Sketcher::SketchObject"):
                    if fp.Base.Support != None:
                        fp.Base.Support = None
                    
                    d = OpenSCAD2Dgeom.edgestofaces(fp.Base.Shape.Edges)
                    if self.layerReversed:
                        d = d.extrude(FreeCAD.Base.Vector(0, 0, -self.layerHeight))
                    else:
                        d = d.extrude(FreeCAD.Base.Vector(0, 0, self.layerHeight))
                    
                    fp.Shape = d
        except:
            pass

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state
        self.setLayerSide()


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
        Since they have the same names nothing needs to be done. This method is optinal.
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
        #***************************************************************
        #   Author:     Gentleface custom icons design agency (http://www.gentleface.com/)
        #   License:    Creative Commons Attribution-Noncommercial 3.0
        #   Iconset:    Mono Icon Set
        #***************************************************************
        return ":/data/img/constraintsArea_TI.svg"

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
