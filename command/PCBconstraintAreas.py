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
if FreeCAD.GuiUp:
    import FreeCADGui
#
import PCBrc
from PCBconf import PCBconstraintAreas
from PCBboard import getPCBheight
from command.PCBgroups import createGroup_Areas

#***********************************************************************
#*                             CONSOLE
#***********************************************************************
def createConstraintArea(obj, typeCA):
    try:
        if not FreeCAD.activeDocument() or getPCBheight()[0]:
            return
        #
        grp = createGroup_Areas()
        
        if obj.isDerivedFrom("Sketcher::SketchObject"):
            if not obj.Shape.isClosed():
                FreeCAD.Console.PrintWarning("Sketcher is not closed!\n")
                return
            #
            obj.ViewObject.Visibility = False
            
            #layerName = PCBconstraintAreas[typeCA][0]
            layerColor = (PCBconstraintAreas[typeCA][3][0] / 255., PCBconstraintAreas[typeCA][3][1] / 255., PCBconstraintAreas[typeCA][3][2] / 255.)
            layerTransparent = PCBconstraintAreas[typeCA][2]
            typeL = PCBconstraintAreas[typeCA][1]
            #numLayer = 0
            #
            a = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", typeCA + "_{0}".format(0))
            constraintAreaObject(a, typeL)
            a.Base = obj
            viewProviderConstraintAreaObject(a.ViewObject)
            
            grp.addObject(a)
            FreeCADGui.activeDocument().getObject(a.Name).ShapeColor = layerColor
            FreeCADGui.activeDocument().getObject(a.Name).Transparency = layerTransparent
            FreeCADGui.activeDocument().getObject(a.Name).DisplayMode = 1
            #grp.Proxy.Object.Group.append(a)
            #grp.Object.Group.append(a)
            
            return a
    except Exception as e:
        FreeCAD.Console.PrintWarning("{0} \n".format(e))


#***********************************************************************
#*                             OBJECT
#***********************************************************************
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
        if 'topSide' in self.Type:
            self.z = getPCBheight()[1]
        elif 'bothSide' in self.Type:  # gorna oraz dolna warstwa
            self.z = -0.5
            self.layerHeight = getPCBheight()[1] + 1.0
        else:  # bottomSide
            self.z = 0.0
        
        fp.Base.Placement.Base.z = self.z
        self.createGeometry(fp)

    def setLayerSide(self):
        if 'topSide' in self.Type:
            self.layerReversed = False
            self.layerHeight = 0.5
            self.z = getPCBheight()[1]
        elif 'bothSide' in self.Type:  # gorna oraz dolna warstwa
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
