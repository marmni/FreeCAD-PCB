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
import FreeCAD, FreeCADGui
if FreeCAD.GuiUp:
    from PySide import QtGui
import Part
from math import degrees
import importlib
#
from PCBobjects import layerSilkObject
from PCBfunctions import kolorWarstwy, mathFunctions
from command.PCBcreateBoard import pickSketch
import PCBconf
from PCBboard import getPCBheight, cutToBoardShape
from command.PCBgroups import createGroup_Glue


#***********************************************************************
#*                             GUI
#***********************************************************************
class createGlueGui(QtGui.QWidget):
    def __init__(self, parent=None):
        importlib.reload(PCBconf)
        
        QtGui.QWidget.__init__(self, parent)
        
        self.form = self
        self.form.setWindowTitle(u"Create glue path")
        self.form.setWindowIcon(QtGui.QIcon(":/data/img/gluePath.png"))
        #
        self.height = QtGui.QDoubleSpinBox(self)
        self.height.setSingleStep(0.1)
        self.height.setValue(1)
        self.height.setRange(0.1, 1000)
        self.height.setSuffix(u" mm")
        #
        self.width = QtGui.QDoubleSpinBox(self)
        self.width.setSingleStep(0.1)
        self.width.setValue(0.2)
        self.width.setRange(0.1, 1000)
        self.width.setSuffix(u" mm")
        #
        self.transparent = QtGui.QSpinBox(self)
        self.transparent.setSingleStep(1)
        self.transparent.setValue(0)
        self.transparent.setRange(0, 100)
        #
        self.wires = QtGui.QLineEdit('')
        self.wires.setReadOnly(True)
        pickWires = pickSketch(self.wires)
        
        if len(FreeCADGui.Selection.getSelection()):
            if FreeCADGui.Selection.getSelection()[0].isDerivedFrom("Sketcher::SketchObject"):
                self.wires.setText(FreeCADGui.Selection.getSelection()[0].Name)
        #
        self.flat = QtGui.QComboBox()
        self.flat.addItems(['True', 'False'])
        self.flat.setCurrentIndex(self.flat.findText('False'))
        #
        self.side = QtGui.QComboBox()
        self.side.addItems(['TOP', 'BOTTOM'])
        #
        self.pcbColor = kolorWarstwy()
        self.pcbColor.setColor(PCBconf.PCBlayers['tGlue'][1])
        self.pcbColor.setToolTip(u"Click to change color")
        #
        lay = QtGui.QGridLayout(self)
        lay.addWidget(QtGui.QLabel(u'Sketcher:'), 0, 0, 1, 1)
        lay.addWidget(self.wires, 0, 1, 1, 1)
        lay.addWidget(pickWires, 0, 2, 1, 1)
        
        lay.addWidget(QtGui.QLabel(u'Side:'), 2, 0, 1, 1)
        lay.addWidget(self.side, 2, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Flat:'), 3, 0, 1, 1)
        lay.addWidget(self.flat, 3, 1, 1, 2)
        
        lay.addWidget(QtGui.QLabel(u'Height:'), 4, 0, 1, 1)
        lay.addWidget(self.height, 4, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Width:'), 5, 0, 1, 1)
        lay.addWidget(self.width, 5, 1, 1, 2)
        
        lay.addWidget(QtGui.QLabel(u'Color:'), 6, 0, 1, 1)
        lay.addWidget(self.pcbColor, 6, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Transparent:'), 7, 0, 1, 1)
        lay.addWidget(self.transparent, 7, 1, 1, 2)
        
    def accept(self):
        if self.wires.text() == '':
            FreeCAD.Console.PrintWarning("Mandatory field is empty!\n")
        else:
            glue = createGlue()
            glue.base = FreeCAD.ActiveDocument.getObject(self.wires.text())
            glue.width = self.width.value()
            glue.height = self.height.value()
            glue.flat = eval(self.flat.currentText())
            glue.color = self.pcbColor.getColor()
            glue.transparent = self.transparent.value()
            if self.side.currentText() == "TOP":
                glue.side = 1
            else:
                glue.side = 0
            glue.generate()
            
            return True

#***********************************************************************
#*                             CONSOLE
#***********************************************************************
class createGlue:
    def __init__(self):
        self.base = None
        self.width = 0.2
        self.height = 1
        self.flat = False
        self.side = 1
        #self.color = 
        self.transparent = 0
    
    def generate(self):
        if self.base == None:
            FreeCAD.Console.PrintWarning("Mandatory field is empty!\n")
        elif not self.base.isDerivedFrom("Sketcher::SketchObject"):
            FreeCAD.Console.PrintWarning("Wrong object!\n")
        #
        pcb = getPCBheight()
        grp = createGroup_Glue()
        #
        if self.side == 1:  # top
            typeL = PCBconf.PCBlayers["tGlue"][3]
        else:
            typeL  = PCBconf.PCBlayers["bGlue"][3]
        
        a = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Glue_{0}".format(0))
        PCBgluePath(a, typeL)
        a.Base = self.base
        if self.width == 0:
            a.Width = 1
        else:
            a.Width = self.width
        a.Height = self.height
        a.Flat = self.flat
        a.Proxy.Side = self.side
        a.Proxy.updatePosition_Z(a, pcb[1])
        
        viewProviderPCBgluePath(a.ViewObject)
        #
        grp.addObject(a)
        FreeCADGui.activeDocument().getObject(a.Name).ShapeColor = self.color
        FreeCADGui.activeDocument().getObject(a.Name).Transparency = self.transparent
        # #
        self.base.ViewObject.Visibility = False
        # #
        pcb[2].Proxy.addObject(pcb[2], a)


#***********************************************************************
#*                             OBJECT
#***********************************************************************
class PCBgluePath(layerSilkObject):
    def __init__(self, obj, typeName):
        self.Type = typeName
        
        obj.addProperty("App::PropertyDistance", "Width", "Base", "Width").Width = 0.1
        obj.addProperty("App::PropertyDistance", "Height", "Base", "Height").Height = 0.2
        obj.addProperty("App::PropertyBool", "Flat", "Base", "Flat").Flat = False
        obj.addProperty("App::PropertyLink", "Base", "Base", "Base")
        obj.addProperty("App::PropertyLength", "Length", "Info", "Length", 1)
        obj.addProperty("App::PropertyFloat", "Volume", "Info", "Volume", 1)
        
        obj.Proxy = self
        self.Object = obj
        self.cutToBoard = True
        self.side = 1  # 0-bottom   1-top   2-both
    
    def __getstate__(self):
        return [self.Type, self.cutToBoard, self.side]

    def __setstate__(self, state):
        if state:
            self.Type = state[0]
            self.cutToBoard = state[1]
            self.side = state[2]

    def updatePosition_Z(self, fp, thickness):
        if 'tGlue' in self.Type:
            fp.Base.Placement.Base.z = thickness + 0.04
            fp.Placement.Base.z = thickness + 0.04
        else:  # bottomSide
            fp.Base.Placement.Base.z = -0.04
            fp.Placement.Base.z = -0.04
            
        fp.recompute()
        fp.Base.recompute()
        fp.purgeTouched()
        fp.Base.purgeTouched()
    
    def countSeamLength(self, obj):
        obj.Length.Value = 0
        try:
            for i in obj.Base.Geometry:
                if i.Construction:
                    continue
                
                obj.Length.Value += i.length()
        except Exception as e:
            pass
            #FreeCAD.Console.PrintWarning("{0}\n".format(e))
    
    def execute(self, obj):
        try:
            if 'tGlue' in self.Type:
                h = obj.Height.Value
                
                if h <= 0:
                    h = 0.01
            else:  # bottomSide
                h = -obj.Height.Value
                
                if h >= 0:
                    h = -0.01
            ##
            self.spisObiektowTXT = []
            for i in obj.Base.Geometry:
                if i.Construction:
                    continue
                
                if i.__class__.__name__ == 'LineSegment':
                    
                    x1 = i.StartPoint.x
                    y1 = i.StartPoint.y
                    x2 = i.EndPoint.x
                    y2 = i.EndPoint.y
                    #
                    self.addLineWidth(x1, y1, x2, y2, obj.Width.Value)
                    self.setFace(not obj.Flat, h*1000)
                elif i.__class__.__name__ == 'Circle':
                    x = i.Center.x
                    y = i.Center.y
                    r = i.Radius
                    #
                    self.addCircle(x, y, r, 0)
                    self.setFace(not obj.Flat, h*1000)
                elif i.__class__.__name__ == 'ArcOfCircle':
                    curve = degrees(i.LastParameter - i.FirstParameter)
                    
                    points = i.discretize(Distance=i.length()/2)
                    if i.Circle.Axis.z < 0:
                        p1 = [points[2].x, points[2].y]
                        p2 = [points[0].x, points[0].y]
                    else:
                        p1 = [points[0].x, points[0].y]
                        p2 = [points[2].x, points[2].y]
                    p3 = [points[1].x, points[1].y]  # mid point
                    
                    self.addArcWidth(p1, p2, curve, obj.Width.Value, p3)
                    self.setFace(not obj.Flat, h*1000)
            #
            if len(self.spisObiektowTXT) > 0:
                path = Part.makeCompound(self.spisObiektowTXT)
                # if obj.Flat == False:
                    # path = path.extrude(FreeCAD.Base.Vector(0, 0, h))
                obj.Shape = path
            else:
                obj.Shape = Part.Shape()
            
            obj.recompute()
            obj.Base.recompute()
            obj.purgeTouched()
            obj.Base.purgeTouched()
            
            obj.Placement.Base.z = obj.Base.Placement.Base.z
            obj.Volume = obj.Shape.Volume
        except Exception as e:
            FreeCAD.Console.PrintWarning(u"{0}\n".format(e))
        
    def onChanged(self, fp, prop):
        try:
            fp.setEditorMode("Length", 1)
            fp.setEditorMode("Volume", 1)
        except:
            pass
        
        try:
            if prop in ["Width", "Height", "Flat"]:
                self.execute(fp)
            
            if prop in ["Base", "Shape"]:
                self.countSeamLength(fp)
        except:
            #FreeCAD.Console.PrintWarning("3. {0}\n".format(e))
            pass


class viewProviderPCBgluePath:
    def __init__(self, obj):
        obj.addProperty("App::PropertyStringList", "Info", "Base", "Info").Info = ""
        obj.Transparency = 0
        
        obj.Proxy = self
        self.Object = obj.Object

    def attach(self, vobj):
        self.Object = vobj.Object
        return

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
    
    def claimChildren(self):
        return [self.Object.Base]
    
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
        vp.setEditorMode("Selectable", 2)
        vp.setEditorMode("DisplayMode", 2)
        if hasattr(vp, "AngularDeflection"):
            vp.setEditorMode("AngularDeflection", 2)
    def getIcon(self):
        ''' Return the icon in XMP format which will appear in the tree view. This method is optional
        and if not defined a default icon is shown.
        '''
        return ":/data/img/gluePath.png"
