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
import FreeCAD, FreeCADGui
if FreeCAD.GuiUp:
    from PySide import QtGui
import Part
from math import degrees
#
from PCBobjects import objectWire
from PCBfunctions import kolorWarstwy, mathFunctions
from command.PCBcreateBoard import pickSketch
from PCBconf import PCBlayers
from PCBboard import getPCBheight, cutToBoardShape
from command.PCBgroups import createGroup_Glue


#***********************************************************************
#*                             GUI
#***********************************************************************
class createGlueGui(QtGui.QWidget):
    def __init__(self, parent=None):
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
        self.pcbColor.setColor(PCBlayers['tGlue'][1])
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
            glue.side = self.side.currentText()
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
        self.side = 'TOP'
        #self.color = 
        self.transparent = 0
    
    def generate(self):
        if self.base == None:
            FreeCAD.Console.PrintWarning("Mandatory field is empty!\n")
        elif not self.base.isDerivedFrom("Sketcher::SketchObject"):
            FreeCAD.Console.PrintWarning("Wrong object!\n")
        #
        grp = createGroup_Glue()
        
        if self.side == 'TOP':
            typeL = PCBlayers["tGlue"][3]
        else:
            typeL  = PCBlayers["bGlue"][3]
        #
        a = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Glue_{0}".format(0))
        PCBgluePath(a, typeL)
        a.Base = self.base
        if self.width == 0:
            a.Width = 1
        else:
            a.Width = self.width
        a.Height = self.height
        a.Flat = self.flat
        
        viewProviderPCBgluePath(a.ViewObject)
        grp.addObject(a)
        FreeCADGui.activeDocument().getObject(a.Name).ShapeColor = self.color
        FreeCADGui.activeDocument().getObject(a.Name).Transparency = self.transparent
        #
        self.base.ViewObject.Visibility = False


#***********************************************************************
#*                             OBJECT
#***********************************************************************
class PCBgluePath(objectWire):
    def __init__(self, obj, typeName):
        self.Type = typeName
        obj.Proxy = self
        self.Object = obj
        self.cutToBoard = True
        
        obj.addProperty("App::PropertyDistance", "Width", "Base", "Width").Width = 0.1
        obj.addProperty("App::PropertyDistance", "Height", "Base", "Height").Height = 0.2
        obj.addProperty("App::PropertyBool", "Flat", "Base", "Flat").Flat = False
        obj.addProperty("App::PropertyLink", "Base", "Base", "Base")

    def __getstate__(self):
        return [self.Type, self.cutToBoard]

    def __setstate__(self, state):
        if state:
            self.Type = state[0]
            self.cutToBoard = state[1]

    def updatePosition_Z(self, fp, dummy=None):
        self.execute(fp)
        
    def generuj(self, fp):
        self.execute(fp)

    def execute(self, obj):
        if 'tGlue' in self.Type:
            z = getPCBheight()[1] + 0.04
            h = obj.Height.Value
            
            if h <= 0:
                h = 0.01
        else:  # bottomSide
            z = -0.04
            h = -obj.Height.Value
            
            if h >= 0:
                h = -0.01
        #
        obiekty = []
        #
        for i in obj.Base.Geometry:
            if i.__class__.__name__ == 'GeomLineSegment':
                x1 = i.StartPoint.x
                y1 = i.StartPoint.y
                x2 = i.EndPoint.x
                y2 = i.EndPoint.y
                #
                obiekty.append(self.createLine(x1, y1, x2, y2, obj.Width.Value))
            elif i.__class__.__name__ == 'GeomCircle':
                x = i.Center.x
                y = i.Center.y
                r = i.Radius
                #
                obiekty.append(self.createCircle(x, y, r, obj.Width.Value))
            elif i.__class__.__name__ == 'GeomArcOfCircle':
                curve = degrees(i.LastParameter - i.FirstParameter)
                xs = i.Center.x
                ys = i.Center.y
                r = i.Radius
                
                math = mathFunctions()
                p1 = [math.cosinus(degrees(i.FirstParameter)) * r, math.sinus(degrees(i.FirstParameter)) * r]
                p1 = [p1[0] + xs, p1[1] + ys]
                p2 = math.obrocPunkt2(p1, [xs, ys], curve)
                #
                obiekty.append(self.createArc(p1, p2, curve, obj.Width.Value))
        #
        #path = obiekty[0]
        #for i in range(1, len(obiekty)):
            #path = path.fuse(obiekty[i])
        #path = path.removeSplitter()
        path = Part.makeCompound(obiekty)
        # cut to board shape
        if self.cutToBoard:
            path = cutToBoardShape(path)
        ###################################################
        if obj.Flat == False:
            path = path.extrude(FreeCAD.Base.Vector(0, 0, h))
        path.Placement.Base.z = z
        obj.Shape = path

    def onChanged(self, fp, prop):
        try:
            if prop in ["Width", "Height", "Flat"]:
                self.execute(fp)
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
