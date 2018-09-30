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
import Draft
import Part
import re
import os
import sys
from pivy.coin import *
import FreeCADGui
#from DraftSnap import *
#from DraftTrackers import *

__currentPath__ = os.path.dirname(os.path.abspath(__file__))


#def addLog():
    #doc = FreeCAD.activeDocument()
    #a = doc.addObject("Part::FeaturePython", 'Logo')
    #logoObject(a)
    #viewProviderLogoObject(a.ViewObject)
    #return True
###########
###########


class wirePoint:
    def __init__(self):
        self.view = Draft.get3DView()
        self.stack = []
        self.point = None
        # adding 2 callback functions
        self.callbackClick = self.view.addEventCallbackPivy(SoMouseButtonEvent.getClassTypeId(),self.click)
        self.callbackMove = self.view.addEventCallbackPivy(SoLocation2Event.getClassTypeId(),self.move)

    def move(self,event_cb):
        event = event_cb.getEvent()
        mousepos = event.getPosition().getValue()
        ctrl = event.wasCtrlDown()
        self.point = FreeCADGui.Snapper.snap(mousepos,active=ctrl)
        
    def click(self,event_cb):
        event = event_cb.getEvent()
        if event.getState() == SoMouseButtonEvent.DOWN:
            #pass
            if self.point:
                self.stack.append(self.point)
                if len(self.stack) == 1:
                    self.view.removeEventCallbackPivy(SoMouseButtonEvent.getClassTypeId(),self.callbackClick)
                    self.view.removeEventCallbackPivy(SoLocation2Event.getClassTypeId(),self.callbackMove)
                    
                    
                    doc = FreeCAD.activeDocument()
                    a = doc.addObject("Part::FeaturePython", 'wireP')
                    wirePointObject(a)
                    viewProviderWirePointObject(a.ViewObject)

                    a.Placement.Base.x = self.stack[0][0]
                    a.Placement.Base.y = self.stack[0][1]
                    a.Placement.Base.z = self.stack[0][2]

                    #FreeCAD.ActiveDocument.openTransaction("Create Point")
                    #Draft.makePoint((self.stack[0][0]),(self.stack[0][1]),self.stack[0][2])
                    #FreeCAD.ActiveDocument.commitTransaction()
                    FreeCADGui.Snapper.off()


class wireStartEndPoint:
    def __init__(self):
        self.view = Draft.get3DView()
        self.stack = []
        self.point = None
        # adding 2 callback functions
        self.callbackClick = self.view.addEventCallbackPivy(SoMouseButtonEvent.getClassTypeId(),self.click)
        self.callbackMove = self.view.addEventCallbackPivy(SoLocation2Event.getClassTypeId(),self.move)

    def move(self,event_cb):
        event = event_cb.getEvent()
        mousepos = event.getPosition().getValue()
        ctrl = event.wasCtrlDown()
        self.point = FreeCADGui.Snapper.snap(mousepos,active=ctrl)
        
    def click(self,event_cb):
        event = event_cb.getEvent()
        if event.getState() == SoMouseButtonEvent.DOWN:
            #pass
            if self.point:
                self.stack.append(self.point)
                if len(self.stack) == 1:
                    self.view.removeEventCallbackPivy(SoMouseButtonEvent.getClassTypeId(),self.callbackClick)
                    self.view.removeEventCallbackPivy(SoLocation2Event.getClassTypeId(),self.callbackMove)
                    
                    
                    doc = FreeCAD.activeDocument()
                    a = doc.addObject("Part::FeaturePython", 'wireST')
                    wireSEPointObject(a)
                    viewProviderWireSEPointObject(a.ViewObject)

                    a.Placement.Base.x = self.stack[0][0]
                    a.Placement.Base.y = self.stack[0][1]
                    a.Placement.Base.z = self.stack[0][2]

                    #FreeCAD.ActiveDocument.openTransaction("Create Point")
                    #Draft.makePoint((self.stack[0][0]),(self.stack[0][1]),self.stack[0][2])
                    #FreeCAD.ActiveDocument.commitTransaction()
                    FreeCADGui.Snapper.off()


class wireSEPointObject:
    def __init__(self, obj):
        self.Type = 'wireST'
        obj.Proxy = self

    def execute(self, fp):
        pass

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state
            
            
class wirePointObject:
    def __init__(self, obj):
        self.Type = 'wireP'
        obj.Proxy = self

    def execute(self, fp):
        pass

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state


class viewProviderWireSEPointObject:
    def __init__(self, obj):
        ''' Set this object to the proxy object of the actual view provider '''
        obj.Proxy = self
        ###
        root = SoSeparator()
        #
        srodek = SoSphere()
        srodek.radius = 0.4
        root.addChild(srodek) 
        #
        myTransform_1 = SoTransform()
        strzalka_1 = SoCylinder()
        strzalka_1.radius = 0.2
        strzalka_1.height = 3
        root.addChild(myTransform_1)
        root.addChild(strzalka_1)
        myTransform_1.translation = (0, 1.5, 0)
        #
        myTransform_2 = SoTransform()
        strzalka_2 = SoCone()
        strzalka_2.bottomRadius = 0.4
        root.addChild(myTransform_2)
        root.addChild(strzalka_2)
        myTransform_2.translation = (0, 1.5, 0)
            
        obj.RootNode.addChild(root)
        

    def attach(self, obj):
        ''' Setup the scene sub-graph of the view provider, this method is mandatory '''
        self.Object = obj.Object

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
        
        self.Object = vp.Object
        

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
            """

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


class viewProviderWirePointObject:
    def __init__(self, obj):
        ''' Set this object to the proxy object of the actual view provider '''
        obj.Proxy = self
        ###
        root = SoSeparator()
        #
        srodek = SoSphere()
        srodek.radius = 0.4
        root.addChild(srodek) 
        #
        strzalka_1 = SoCylinder()
        strzalka_1.radius = 0.2
        strzalka_1.height = 3
        root.addChild(strzalka_1)
        #
        myTransform_2 = SoTransform()
        strzalka_2 = SoCone()
        strzalka_2.bottomRadius = 0.4
        strzalka_2.height = .8
        root.addChild(myTransform_2)
        root.addChild(strzalka_2)
        myTransform_2.translation = (0, 1.5, 0)
        #
        myTransform_3 = SoTransform()
        strzalka_3 = SoCone()
        strzalka_3.bottomRadius = 0.4
        strzalka_3.height = .8
        root.addChild(myTransform_3)
        root.addChild(strzalka_3)
        myTransform_3.translation = (0, -3, 0)
            
        obj.RootNode.addChild(root)
        

    def attach(self, obj):
        ''' Setup the scene sub-graph of the view provider, this method is mandatory '''
        self.Object = obj.Object

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
        
        self.Object = vp.Object
        

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
            """

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
