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
    from PySide import QtCore, QtGui
from math import sqrt
import DraftGeomUtils
import Draft
import Part
import os
import __builtin__
import unicodedata
#
import PCBconf
from PCBpartManaging import partsManaging
from PCBfunctions import kolorWarstwy, mathFunctions
from PCBobjects import layerPolygonObject, viewProviderLayerPolygonObject, layerPathObject, viewProviderLayerPathObject, constraintAreaObject, viewProviderConstraintAreaObject
from PCBboard import PCBboardObject, viewProviderPCBboardObject
from command.PCBgroups import *
from command.PCBannotations import createAnnotation
from command.PCBglue import createGlue


class dialogMAIN_FORM(QtGui.QDialog):
    def __init__(self, filename=None, parent=None):
        reload(PCBconf)
        
        QtGui.QDialog.__init__(self, parent)
        freecadSettings = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB")

        self.setWindowTitle(u"PCB settings")
        self.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        #
        self.plytkaPCB = QtGui.QCheckBox(u"Board")
        self.plytkaPCB.setDisabled(True)
        self.plytkaPCB.setChecked(True)
        
        plytkaPCBInfo = QtGui.QLabel(u"PCB Thickness")
        plytkaPCBInfo.setStyleSheet('margin-left:0px')
        
        #######
        self.gruboscPlytki = QtGui.QDoubleSpinBox(self)
        self.gruboscPlytki.setSingleStep(0.1)
        self.gruboscPlytki.setValue(freecadSettings.GetFloat("boardThickness", 1.5))
        self.gruboscPlytki.setSuffix(u" mm")
        #######
        self.plytkaPCB_otworyH = QtGui.QCheckBox(u"Holes")
        self.plytkaPCB_otworyH.setChecked(freecadSettings.GetBool("boardImportHoles", True))
        
        self.plytkaPCB_otworyV = QtGui.QCheckBox(u"Vias")
        self.plytkaPCB_otworyV.setChecked(freecadSettings.GetBool("boardImportHoles", True))
        
        self.plytkaPCB_otworyP = QtGui.QCheckBox(u"Pads")
        self.plytkaPCB_otworyP.setChecked(freecadSettings.GetBool("boardImportHoles", True))
        
        self.holesMin = QtGui.QDoubleSpinBox(self)
        self.holesMin.setSingleStep(0.1)
        self.holesMin.setValue(0)
        self.holesMin.setSuffix(u" mm")
        
        self.holesMax = QtGui.QDoubleSpinBox(self)
        self.holesMax.setSingleStep(0.1)
        self.holesMax.setValue(0)
        self.holesMax.setSuffix(u" mm")
        #######
        #self.plytkaPCB_PADS = QtGui.QCheckBox(u"Vias")
        #self.plytkaPCB_PADS.setChecked(True)
        #######
        self.plytkaPCB_plikER = QtGui.QCheckBox(u"Generate report")
        self.plytkaPCB_plikER.setChecked(freecadSettings.GetBool("partsReport", False))
        self.plytkaPCB_plikER.setStyleSheet('margin-left:20px')
        self.plytkaPCB_plikER.setEnabled(freecadSettings.GetBool("partsImport", True))
        #######
        self.plytkaPCB_elementy = QtGui.QCheckBox(u"Parts")
        self.plytkaPCB_elementy.setChecked(freecadSettings.GetBool("partsImport", True))
        #######
        self.plytkaPCB_grupujElementy = QtGui.QCheckBox(u"Group parts")
        self.plytkaPCB_grupujElementy.setChecked(freecadSettings.GetBool("groupParts", False))
        self.plytkaPCB_grupujElementy.setStyleSheet('margin-left:20px')
        self.plytkaPCB_grupujElementy.setEnabled(freecadSettings.GetBool("partsImport", True))
        #######
        self.plytkaPCB_elementyKolory = QtGui.QCheckBox(u"Colorize elements")
        self.plytkaPCB_elementyKolory.setChecked(freecadSettings.GetBool("partsColorize", True))
        self.plytkaPCB_elementyKolory.setStyleSheet('margin-left:20px')
        self.plytkaPCB_elementyKolory.setEnabled(freecadSettings.GetBool("partsImport", True))
        #######
        self.adjustParts = QtGui.QCheckBox(u"Adjust part name/value")
        self.adjustParts.setChecked(freecadSettings.GetBool("adjustNameValue", False))
        self.adjustParts.setStyleSheet('margin-left:20px')
        self.adjustParts.setEnabled(freecadSettings.GetBool("partsImport", True))
        #######
        self.partMinX = QtGui.QDoubleSpinBox(self)
        self.partMinX.setSingleStep(0.1)
        self.partMinX.setValue(0)
        self.partMinX.setSuffix(u" mm")
        self.partMinX.setEnabled(freecadSettings.GetBool("partsImport", True))
        
        self.partMinY = QtGui.QDoubleSpinBox(self)
        self.partMinY.setSingleStep(0.1)
        self.partMinY.setValue(0)
        self.partMinY.setSuffix(u" mm")
        self.partMinY.setEnabled(freecadSettings.GetBool("partsImport", True))
        
        self.partMinZ = QtGui.QDoubleSpinBox(self)
        self.partMinZ.setSingleStep(0.1)
        self.partMinZ.setValue(0)
        self.partMinZ.setSuffix(u" mm")
        self.partMinZ.setEnabled(freecadSettings.GetBool("partsImport", True))
        #######
        #######
        #self.connect(self.plytkaPCB_elementy, QtCore.SIGNAL("toggled (bool)"), self.plytkaPCB_plikER.setChecked)
        self.connect(self.plytkaPCB_elementy, QtCore.SIGNAL("toggled (bool)"), self.plytkaPCB_plikER.setEnabled)
        
        #self.connect(self.plytkaPCB_elementy, QtCore.SIGNAL("toggled (bool)"), self.plytkaPCB_elementyKolory.setChecked)
        self.connect(self.plytkaPCB_elementy, QtCore.SIGNAL("toggled (bool)"), self.plytkaPCB_elementyKolory.setEnabled)
        
        #self.connect(self.plytkaPCB_elementy, QtCore.SIGNAL("toggled (bool)"), self.adjustParts.setChecked)
        self.connect(self.plytkaPCB_elementy, QtCore.SIGNAL("toggled (bool)"), self.adjustParts.setEnabled)
        
        #self.connect(self.plytkaPCB_elementy, QtCore.SIGNAL("toggled (bool)"), self.plytkaPCB_grupujElementy.setChecked)
        self.connect(self.plytkaPCB_elementy, QtCore.SIGNAL("toggled (bool)"), self.plytkaPCB_grupujElementy.setEnabled)
        
        self.connect(self.plytkaPCB_elementy, QtCore.SIGNAL("toggled (bool)"), self.partMinX.setEnabled)
        self.connect(self.plytkaPCB_elementy, QtCore.SIGNAL("toggled (bool)"), self.partMinY.setEnabled)
        self.connect(self.plytkaPCB_elementy, QtCore.SIGNAL("toggled (bool)"), self.partMinZ.setEnabled)
        #######
        #######
        # buttons
        buttons = QtGui.QDialogButtonBox()
        buttons.addButton(u"Cancel", QtGui.QDialogButtonBox.RejectRole)
        buttons.addButton(u"Accept", QtGui.QDialogButtonBox.AcceptRole)
        self.connect(buttons, QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        self.connect(buttons, QtCore.SIGNAL("rejected()"), self, QtCore.SLOT("reject()"))
        
        self.selectAll = QtGui.QCheckBox('de/select all layers')
        self.selectAll.setStyleSheet('''border:1px solid rgb(237, 237, 237);''')
        self.connect(self.selectAll, QtCore.SIGNAL("clicked()"), self.selectAllCategories)
        #
        self.spisWarstw = tabela()
        self.spisWarstw.setColumnCount(5)
        self.spisWarstw.setHorizontalHeaderLabels(["", u"ID", "", "", u"Name"])
        self.spisWarstw.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Fixed)
        self.spisWarstw.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Fixed)
        self.spisWarstw.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Fixed)
        self.spisWarstw.horizontalHeader().setResizeMode(3, QtGui.QHeaderView.Fixed)
        self.spisWarstw.horizontalHeader().resizeSection(0, 25)
        self.spisWarstw.horizontalHeader().resizeSection(1, 35)
        self.spisWarstw.horizontalHeader().resizeSection(2, 35)
        self.spisWarstw.horizontalHeader().resizeSection(3, 95)
        self.spisWarstw.hideColumn(1)
        #######
        layHoles = QtGui.QVBoxLayout()
        layHoles.addWidget(self.plytkaPCB_otworyH)
        layHoles.addWidget(self.plytkaPCB_otworyV)
        layHoles.addWidget(self.plytkaPCB_otworyP)
        layHoles.setContentsMargins(20, 10, 0, 0)
        
        layHolesRange = QtGui.QGridLayout()
        layHolesRange.setContentsMargins(20, 10, 0, 0)
        layHolesRange.addWidget(QtGui.QLabel(u"min."), 0, 0, 1, 1)
        layHolesRange.addWidget(self.holesMin, 0, 1, 1, 1)
        layHolesRange.addWidget(QtGui.QLabel(u"max."), 1, 0, 1, 1)
        layHolesRange.addWidget(self.holesMax, 1, 1, 1, 1)
        
        layPartSize = QtGui.QGridLayout()
        layPartSize.setContentsMargins(20, 0, 0, 0)
        layPartSize.addWidget(QtGui.QLabel(u"L"), 0, 0, 1, 1)
        layPartSize.addWidget(self.partMinX, 0, 1, 1, 1)
        layPartSize.addWidget(QtGui.QLabel(u"W"), 1, 0, 1, 1)
        layPartSize.addWidget(self.partMinY, 1, 1, 1, 1)
        layPartSize.addWidget(QtGui.QLabel(u"H"), 2, 0, 1, 1)
        layPartSize.addWidget(self.partMinZ, 2, 1, 1, 1)
        layPartSize.setEnabled
        #
        self.lay = QtGui.QGridLayout()
        #self.lay.addLayout(layLeftSide, 0, 0, 8, 1, QtCore.Qt.AlignTop)
        self.lay.addWidget(self.spisWarstw, 0, 1, 10, 1)
        self.lay.addWidget(self.selectAll, 10, 1, 1, 1)
        #self.lay.addWidget(self.plytkaPCB, 0, 1, 1, 4)
        self.lay.addWidget(plytkaPCBInfo, 1, 2, 1, 1, QtCore.Qt.AlignLeft)
        self.lay.addWidget(self.gruboscPlytki, 1, 3, 1, 3)
        self.lay.addLayout(layHoles, 2, 2, 1, 3, QtCore.Qt.AlignTop)
        self.lay.addLayout(layHolesRange, 2, 5, 1, 1)
        #lay.addWidget(self.plytkaPCB_PADS, 3, 1, 1, 2)
        self.lay.addWidget(self.plytkaPCB_elementy, 4, 2, 1, 3)
        self.lay.addWidget(self.plytkaPCB_elementyKolory, 5, 2, 1, 3)
        self.lay.addWidget(self.plytkaPCB_grupujElementy, 6, 2, 1, 3)
        self.lay.addWidget(self.adjustParts, 7, 2, 1, 3)
        self.lay.addWidget(self.plytkaPCB_plikER, 8, 2, 1, 3)
        self.lay.addLayout(layPartSize, 5, 5, 5, 1)
        self.lay.addItem(QtGui.QSpacerItem(10, 10), 11, 2, 1, 3)
        # lib
        self.lay.addItem(QtGui.QSpacerItem(10, 10), 13, 2, 1, 3)
        self.lay.addWidget(buttons, 14, 0, 1, 7, QtCore.Qt.AlignCenter)
        self.lay.setRowStretch(13, 10)
        self.lay.setColumnMinimumWidth(1, 250)
        self.lay.setColumnMinimumWidth(2, 120)
        self.setLayout(self.lay)
        
    def selectAllCategories(self):
        if self.spisWarstw.rowCount() > 0:
            for i in range(self.spisWarstw.rowCount()):
                if self.selectAll.isChecked():
                    self.spisWarstw.cellWidget(i, 0).setCheckState(QtCore.Qt.Checked)
                else:
                    self.spisWarstw.cellWidget(i, 0).setCheckState(QtCore.Qt.Unchecked)

    def generateLayers(self, forbidden=[-1]):
        for i, j in PCBconf.softLayers[self.databaseType].items():
            try:
                layerData = PCBconf.PCBlayers[j[1]]
                try:
                    if i in self.layersNames and i not in [17, 18]:
                        name = self.layersNames[i]
                    else:
                        name = j[1]
                except:
                    name = j[1]
                    
                self.spisWarstwAddRow(i, layerData[1], layerData[2], name)
            except:
                layerData = PCBconf.PCBconstraintAreas[j[1]]
                try:
                    if i in self.layersNames and i not in forbidden:
                        name = self.layersNames[i]
                    else:
                        name = j[1]
                except:
                    name = j[1]
                
                #   ID,     layerColor,     layerTransparent,   layerName
                self.spisWarstwAddRow(i, layerData[3], layerData[2], name)

    def spisWarstwAddRow(self, ID, layerColor, layerTransparent, layerName):
        self.spisWarstw.insertRow(self.spisWarstw.rowCount())
        
        check = QtGui.QCheckBox()
        check.setStyleSheet("QCheckBox {margin:7px;}")
        self.spisWarstw.setCellWidget(self.spisWarstw.rowCount() - 1, 0, check)
        #
        num = QtGui.QTableWidgetItem(str(ID))
        num.setTextAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        self.spisWarstw.setItem(self.spisWarstw.rowCount() - 1, 1, num)
        #
        if layerColor:
            color = kolorWarstwy()
            color.setColor(layerColor)
            color.setToolTip(u"Click to change color")
        else:
            color = QtGui.QLabel("")
        
        self.spisWarstw.setCellWidget(self.spisWarstw.rowCount() - 1, 2, color)
        #
        if layerTransparent:
            
            if layerTransparent[0] == 'int':
                transparent = transpSpinBox()
            else:
                transparent = transpDoubleSpinBox()
            
            transparent.setRange(layerTransparent[3], layerTransparent[4])
            transparent.setSuffix(layerTransparent[1])
            transparent.setValue(layerTransparent[2])
        else:
            transparent = QtGui.QLabel("")
        
        self.spisWarstw.setCellWidget(self.spisWarstw.rowCount() - 1, 3, transparent)
        #
        name = QtGui.QTableWidgetItem(layerName)
        name.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        name.setToolTip(u"Click to change name")
        self.spisWarstw.setItem(self.spisWarstw.rowCount() - 1, 4, name)


class transpSpinBox(QtGui.QSpinBox):
    def __init__(self, parent=None):
        QtGui.QSpinBox.__init__(self, parent)

        self.setStyleSheet('''
            QSpinBox
            {
              border:0px;
            }
        ''')
        

class transpDoubleSpinBox(QtGui.QDoubleSpinBox):
    def __init__(self, parent=None):
        QtGui.QDoubleSpinBox.__init__(self, parent)

        self.setStyleSheet('''
            QDoubleSpinBox
            {
              border:0px;
            }
        ''')


class tabela(QtGui.QTableWidget):
    def __init__(self, parent=None):
        QtGui.QTableWidget.__init__(self, parent)

        self.setSortingEnabled(False)
        #self.setGridStyle(Qt.NoPen)
        self.setShowGrid(False)
        self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().hide()
        self.setFrameShape(QtGui.QFrame.NoFrame)
        self.setStyleSheet('''
            QTableWidget QHeaderView
            {
                border:0px;
            }
            QTableWidget
            {
                border: 1px solid #9EB6CE;
                border-top:0px;
            }
            QTableWidget QHeaderView::section
            {
                color:#4C4161;
                font-size:12px;
                border:1px solid #9EB6CE;
                border-left:0px;
                padding:5px 0;
            }
        ''')


class mainPCB(partsManaging):
    def __init__(self, parent=None):
        #reload(PCBconf)
        partsManaging.__init__(self)

        self.projektBRD = None
        self.setDatabase()
    
    def generateGlue(self, wires, doc, grp, layerName, layerColor, layerNumber):
        if PCBconf.PCBlayers[PCBconf.softLayers[self.databaseType][layerNumber][1]][0] == 1:
            side = 'TOP'
        else:
            side = 'BOTTOM'
        #
        for i, j in wires.items():
            ser = doc.addObject('Sketcher::SketchObject', "Sketch_{0}".format(layerName))
            ser.ViewObject.Visibility = False
            for k in j:
                if k[0] == 'line':
                    ser.addGeometry(Part.Line(FreeCAD.Vector(k[1], k[2], 0), FreeCAD.Vector(k[3], k[4], 0)))
                elif k[0] == 'circle':
                    ser.addGeometry(Part.Circle(FreeCAD.Vector(k[1], k[2]), FreeCAD.Vector(0, 0, 1), k[3]))
                elif k[0] == 'arc':
                    x1 = k[1]
                    y1 = k[2]
                    x2 = k[3]
                    y2 = k[4]
                    [x3, y3] = self.arcMidPoint([x2, y2], [x1, y1], k[5])
                    
                    arc = Part.Arc(FreeCAD.Vector(x1, y1, 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(x2, y2, 0.0))
                    ser.addGeometry(self.Draft2Sketch(arc, ser))
            #
            glue = createGlue()
            glue.base = ser
            glue.width = i
            glue.side = side
            glue.color = layerColor
            glue.generate()
    
    def generateConstraintAreas(self, areas, doc, layerNumber, grp, layerName, layerColor, layerTransparent):
        typeL = PCBconf.PCBconstraintAreas[PCBconf.softLayers[self.databaseType][layerNumber][1]][1]
        mainGroup = doc.addObject("App::DocumentObjectGroup", layerName)
        grp.addObject(mainGroup)
        
        for i in areas:
            ser = doc.addObject('Sketcher::SketchObject', "Sketch_{0}".format(layerName))
            ser.ViewObject.Visibility = False
            #
            if i[0] == 'rect':
                try:
                    height = i[5]
                except:
                    height = 0
                
                x1 = i[1]
                y1 = i[2]
                
                x2 = i[3]
                y2 = i[2]
                
                x3 = i[3]
                y3 = i[4]
                
                x4 = i[1]
                y4 = i[4]
                
                try:
                    if i[6] != 0:
                        xs = (i[1] + i[3]) / 2.
                        ys = (i[2] + i[4]) / 2.
                
                        mat = mathFunctions()
                        (x1, y1) = mat.obrocPunkt2([x1, y1], [xs, ys], i[6])
                        (x2, y2) = mat.obrocPunkt2([x2, y2], [xs, ys], i[6])
                        (x3, y3) = mat.obrocPunkt2([x3, y3], [xs, ys], i[6])
                        (x4, y4) = mat.obrocPunkt2([x4, y4], [xs, ys], i[6])
                except:
                    pass
                
                ser.addGeometry(Part.Line(FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x2, y2, 0)))
                ser.addGeometry(Part.Line(FreeCAD.Vector(x2, y2, 0), FreeCAD.Vector(x3, y3, 0)))
                ser.addGeometry(Part.Line(FreeCAD.Vector(x3, y3, 0), FreeCAD.Vector(x4, y4, 0)))
                ser.addGeometry(Part.Line(FreeCAD.Vector(x4, y4, 0), FreeCAD.Vector(x1, y1, 0)))
            elif i[0] == 'circle':
                try:
                    height = i[5]
                except:
                    height = 0
                
                if i[4] == 0:
                    ser.addGeometry(Part.Circle(FreeCAD.Vector(i[1], i[2]), FreeCAD.Vector(0, 0, 1), i[3]))
                else:
                    ser.addGeometry(Part.Circle(FreeCAD.Vector(i[1], i[2]), FreeCAD.Vector(0, 0, 1), i[3] + i[4] / 2))
                    ser.addGeometry(Part.Circle(FreeCAD.Vector(i[1], i[2]), FreeCAD.Vector(0, 0, 1), i[3] - i[4] / 2))
            elif i[0] == 'polygon':
                try:
                    height = i[2]
                except:
                    height = 0
                
                for j in i[1]:
                    if j[0] == 'Line':
                        ser.addGeometry(Part.Line(FreeCAD.Vector(j[1], j[2], 0), FreeCAD.Vector(j[3], j[4], 0)))
                    elif j[0] == 'Arc':
                        x1 = j[1]
                        y1 = j[2]
                        x2 = j[3]
                        y2 = j[4]
                        [x3, y3] = self.arcMidPoint([x2, y2], [x1, y1], j[5])
                        
                        arc = Part.Arc(FreeCAD.Vector(x1, y1, 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(x2, y2, 0.0))
                        ser.addGeometry(self.Draft2Sketch(arc, ser))
            #
            a = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", layerName + "_{0}".format(0))
            layerObj = constraintAreaObject(a, typeL)
            a.Base = ser
            if height != 0:
                a.Height = height
            viewProviderConstraintAreaObject(a.ViewObject)
            mainGroup.addObject(a)
            FreeCADGui.activeDocument().getObject(a.Name).ShapeColor = layerColor
            FreeCADGui.activeDocument().getObject(a.Name).Transparency = layerTransparent
            FreeCADGui.activeDocument().getObject(a.Name).DisplayMode = 1
            self.updateView()
        
    def generatePolygons(self, data, doc, group, layerName, layerColor, layerNumber):
        for i in data[0]:
            for j in i: # polygons
                layerS = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "{0}_{1}".format(layerName, layerNumber))
                layerNew = layerPolygonObject(layerS, PCBconf.PCBlayers[PCBconf.softLayers[self.databaseType][layerNumber][1]][3])
                layerNew.points = j[3]
                layerNew.name = j[2]
                layerNew.isolate = j[1]
                layerNew.paths = data[1]
                layerNew.generuj(layerS)
                layerNew.updatePosition_Z(layerS)
                viewProviderLayerPolygonObject(layerS.ViewObject)
                layerS.ViewObject.ShapeColor = layerColor
                group.addObject(layerS)
    
    def generatePaths(self, wires, doc, group, layerName, layerColor, layerNumber, defHeight):
        layerS = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "{0}_{1}".format(layerName, layerNumber))
        layerNew = layerPathObject(layerS, PCBconf.PCBlayers[PCBconf.softLayers[self.databaseType][layerNumber][1]][3])
        layerNew.defHeight = defHeight
        if len(wires):
            layerNew.signals = wires[-1]
            layerNew.spisObiektow = wires[:-1]
        layerNew.generuj(layerS)
        layerNew.updatePosition_Z(layerS)
        viewProviderLayerPathObject(layerS.ViewObject)
        layerS.ViewObject.ShapeColor = layerColor
        group.addObject(layerS)
    
    def Draft2Sketch(self, elem, sketch):
        return (DraftGeomUtils.geom(elem.toShape().Edges[0], sketch.Placement))

    def generatePCB(self, PCB, doc, groupBRD, gruboscPlytki):
        doc.addObject('Sketcher::SketchObject', 'PCB_Border')
        doc.PCB_Border.Placement = FreeCAD.Placement(FreeCAD.Vector(0.0, 0.0, 0.0), FreeCAD.Rotation(0.0, 0.0, 0.0, 1.0))
        #
        for i in PCB[0]:
            if i[0] == 'Arc':  # arc by 3 points
                x1 = i[1]
                y1 = i[2]
                x2 = i[3]
                y2 = i[4]
                [x3, y3] = self.arcMidPoint([x2, y2], [x1, y1], i[5])
                
                arc = Part.Arc(FreeCAD.Vector(x1, y1, 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(x2, y2, 0.0))
                doc.PCB_Border.addGeometry(self.Draft2Sketch(arc, doc.PCB_Border))
            elif i[0] == 'Arc_2':  # arc by center / start angle / stop angle / radius
                doc.PCB_Border.addGeometry(Part.ArcOfCircle(Part.Circle(FreeCAD.Vector(i[1], i[2], 0), FreeCAD.Vector(0, 0, 1), i[3]), i[4], i[5]))
            elif i[0] == 'Circle':
                doc.PCB_Border.addGeometry(Part.Circle(FreeCAD.Vector(i[1], i[2]), FreeCAD.Vector(0, 0, 1), i[3]))
            elif i[0] == 'Line':
                doc.PCB_Border.addGeometry(Part.Line(FreeCAD.Vector(i[1], i[2], 0), FreeCAD.Vector(i[3], i[4], 0)))
        #
        #if PCB[1]:
        PCBboard = doc.addObject("Part::FeaturePython", "Board")
        PCBboardObject(PCBboard)
        PCBboard.Thickness = gruboscPlytki
        PCBboard.Border = doc.PCB_Border
        viewProviderPCBboardObject(PCBboard.ViewObject)
        groupBRD.addObject(doc.Board)
        FreeCADGui.activeDocument().getObject(PCBboard.Name).ShapeColor = PCBconf.PCB_COLOR
        FreeCADGui.activeDocument().PCB_Border.Visibility = False
        self.updateView()
            #FreeCADGui.activeDocument().Sketch_PCB.Visibility = False
            ## PAD
            #doc.recompute()
            #obj = doc.addObject("PartDesign::Pad", "Pad_PCB")
            #doc.Pad_PCB.Sketch = doc.Sketch_PCB
            #doc.Pad_PCB.Length = gruboscPlytki
            #doc.Pad_PCB.Reversed = 0
            #doc.Pad_PCB.Midplane = 0
            ##doc.Pad_PCB.Length2 = 100.0
            #doc.Pad_PCB.Type = 0
            #doc.Pad_PCB.UpToFace = None
            #doc.recompute()
            #groupBRD.addObject(doc.Pad_PCB)
            #FreeCADGui.activeDocument().getObject(obj.Name).ShapeColor = PCB_COLOR
        #else:
            #groupBRD.addObject(doc.PCB_Border)
            #FreeCAD.Console.PrintError("Round corners detected. Generate pad: OFF\n")
            #doc.recompute()

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

    #def generateOctagon(self, x, y, diameter):
        #pP = diameter / 2.
        #zP = diameter / (2 + (sqrt(2)))
        #aP = diameter * (sqrt(2) - 1)
        
        #return [[x - pP + zP, y - pP, 0, x - pP + zP + aP, y - pP, 0],
                #[x - pP + zP + aP, y - pP, 0, x + pP, y - pP + zP, 0],
                #[x + pP, y - pP + zP, 0, x + pP, y - pP + zP + aP, 0],
                #[x + pP, y - pP + zP + aP, 0, x + pP - zP, y + pP, 0],
                #[x + pP - zP, y + pP, 0, x + pP - zP - aP, y + pP, 0],
                #[x + pP - zP - aP, y + pP, 0, x - pP, y + pP - zP, 0],
                #[x - pP, y + pP - zP, 0, x - pP, y + pP - zP - aP, 0],
                #[x - pP, y + pP - zP - aP, 0, x - pP + zP, y - pP, 0]]
    
    def showHoles(self):
        if not self.dialogMAIN.plytkaPCB_otworyH.isChecked() and not self.dialogMAIN.plytkaPCB_otworyV.isChecked() and not self.dialogMAIN.plytkaPCB_otworyP.isChecked():
            return False
        else:
            return True
        
    def generateHoles(self, dane, doc, Hmin, Hmax):
        doc.addObject('Sketcher::SketchObject', 'PCB_Holes')
        doc.PCB_Holes.Placement = FreeCAD.Placement(FreeCAD.Vector(0.0, 0.0, 0.0), FreeCAD.Rotation(0.0, 0.0, 0.0, 1.0))
        FreeCADGui.activeDocument().PCB_Holes.Visibility = False
        #
        for i in dane:
            x = float("%4.3f" % i[0])
            y = float("%4.3f" % i[1])
            r = float("%4.3f" % i[2])
            
            if r == 0:
                continue
            
            if len(i) > 3:  # oval
                r2 = float("%4.3f" % i[3])
                
                p1 = i[4]
                p2 = i[5]
                p3 = i[6]
                p4 = i[7]
                
                if r > r2:
                    doc.PCB_Holes.addGeometry(Part.Line(FreeCAD.Vector(p1[0], p1[1], 0), FreeCAD.Vector(p2[0], p2[1], 0)))
                    doc.PCB_Holes.addGeometry(Part.Line(FreeCAD.Vector(p3[0], p3[1], 0), FreeCAD.Vector(p4[0], p4[1], 0)))
                    
                    p5 = self.arcMidPoint(p1, p3, 180)
                    doc.PCB_Holes.addGeometry(Part.Arc(FreeCAD.Vector(p1[0], p1[1], 0.0), FreeCAD.Vector(p5[0], p5[1], 0.0), FreeCAD.Vector(p3[0], p3[1], 0.0)))
                    
                    p5 = self.arcMidPoint(p2, p4, -180)
                    doc.PCB_Holes.addGeometry(Part.Arc(FreeCAD.Vector(p2[0], p2[1], 0.0), FreeCAD.Vector(p5[0], p5[1], 0.0), FreeCAD.Vector(p4[0], p4[1], 0.0)))
                else:
                    doc.PCB_Holes.addGeometry(Part.Line(FreeCAD.Vector(p1[0], p1[1], 0), FreeCAD.Vector(p3[0], p3[1], 0)))
                    doc.PCB_Holes.addGeometry(Part.Line(FreeCAD.Vector(p2[0], p2[1], 0), FreeCAD.Vector(p4[0], p4[1], 0)))
                    
                    p5 = self.arcMidPoint(p1, p2, -180)
                    doc.PCB_Holes.addGeometry(Part.Arc(FreeCAD.Vector(p1[0], p1[1], 0.0), FreeCAD.Vector(p5[0], p5[1], 0.0), FreeCAD.Vector(p2[0], p2[1], 0.0)))
                    
                    p5 = self.arcMidPoint(p3, p4, 180)
                    doc.PCB_Holes.addGeometry(Part.Arc(FreeCAD.Vector(p3[0], p3[1], 0.0), FreeCAD.Vector(p5[0], p5[1], 0.0), FreeCAD.Vector(p4[0], p4[1], 0.0)))
            else:  # circle
                if Hmin == 0 and Hmax == 0:
                    doc.PCB_Holes.addGeometry(Part.Circle(FreeCAD.Vector(x, y, 0.), FreeCAD.Vector(0, 0, 1), r))
                elif Hmin != 0 and Hmax == 0 and Hmin <= r * 2:
                    doc.PCB_Holes.addGeometry(Part.Circle(FreeCAD.Vector(x, y, 0.), FreeCAD.Vector(0, 0, 1), r))
                elif Hmax != 0 and Hmin == 0 and r * 2 <= Hmax:
                    doc.PCB_Holes.addGeometry(Part.Circle(FreeCAD.Vector(x, y, 0.), FreeCAD.Vector(0, 0, 1), r))
                elif Hmin <= r * 2 <= Hmax:
                    doc.PCB_Holes.addGeometry(Part.Circle(FreeCAD.Vector(x, y, 0.), FreeCAD.Vector(0, 0, 1), r))
            ####
            ##hole = [Part.Circle(FreeCAD.Vector(x, y), FreeCAD.Vector(0, 0, 1), r).toShape()]
            ##hole = Part.Wire(hole)
            ##hole = Part.Face(hole)
            #hole = [Part.Circle(FreeCAD.Vector(x, y, -1), FreeCAD.Vector(0, 0, 1), r).toShape()]
            #hole = Part.Wire(hole)
            #hole = Part.Face(hole).extrude(FreeCAD.Base.Vector(0, 0, 2))
            
            #holeModel.append(hole)
        
        #holeModel = Part.makeCompound(holeModel)
        doc.Board.Holes = doc.PCB_Holes
        doc.recompute()
    
    def generateErrorReport(self, PCB_ER, filename):
        ############### ZAPIS DO PLIKU - LISTA BRAKUJACYCH ELEMENTOW
        if PCB_ER and len(PCB_ER):
            if os.path.exists(filename) and os.path.isfile(filename):
                (path, docname) = os.path.splitext(os.path.basename(filename))
                plik = __builtin__.open(u"{0}.err".format(filename), "w")
                a = []
                a = [i for i in PCB_ER if str(i) not in a and not a.append(str(i))]
                PCB_ER = list(a)
                
                FreeCAD.Console.PrintWarning("**************************\n")
                for i in PCB_ER:
                    line = u"Object not found: {0} {2} [Package: {1}, Library: {3}]\n".format(i[0], i[1], i[2], i[3])
                    plik.writelines(line)
                    FreeCAD.Console.PrintWarning(line)
                FreeCAD.Console.PrintWarning("**************************\n")
                plik.close()
            else:
                FreeCAD.Console.PrintWarning("Access Denied. The Specified Path does not exist, or there could be permission problem.")
        else:
            try:
                os.remove("{0}.err".format(filename))
            except:
                pass
        ##############
        
    def addAnnotations(self, annotations, doc, color):
        for i in annotations:
            annotation = createAnnotation()
            annotation.X = float(i[1])
            annotation.Y = float(i[2])
            annotation.Side = str(i[5])
            annotation.Rot = float(i[4])
            annotation.Text = i[0]
            annotation.Align = str(i[6])
            annotation.Size = float(i[3])
            annotation.Spin = i[7]
            annotation.Mirror = i[8]
            annotation.Color = color
            #annotation.fontName = str(i[9])
            annotation.generate()
            annotation.addToAnnotations()
        
    def addDimensions(self, wymiary, doc, layerGRP, layerName, gruboscPlytki, layerColor):
        layerName = "{0}".format(layerName)

        grp = doc.addObject("App::DocumentObjectGroup", layerName)
        for i in wymiary:
            x1 = i[0]
            y1 = i[1]
            x2 = i[2]
            y2 = i[3]
            x3 = i[4]
            y3 = i[5]
            
            dim = Draft.makeDimension(FreeCAD.Vector(x1, y1, gruboscPlytki), FreeCAD.Vector(x2, y2, gruboscPlytki), FreeCAD.Vector(x3, y3, gruboscPlytki))
            dim.ViewObject.LineColor = layerColor
            dim.ViewObject.LineWidth = 1.00
            dim.ViewObject.ExtLines = 0.00
            dim.ViewObject.FontSize = 2.00
            dim.ViewObject.ArrowSize = '0.5 mm'
            dim.ViewObject.ArrowType = "Arrow"
            grp.addObject(dim)
        layerGRP.addObject(grp)
