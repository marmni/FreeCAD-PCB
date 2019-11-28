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
import builtins
import importlib
import unicodedata
#
import PCBconf
from PCBpartManaging import partsManaging
from PCBfunctions import kolorWarstwy, mathFunctions, getFromSettings_Color_1, configParserRead, configParserWrite
from PCBobjects import layerPolygonObject, viewProviderLayerPolygonObject, constraintAreaObject, viewProviderConstraintAreaObject
from PCBboard import PCBboardObject, viewProviderPCBboardObject
from command.PCBgroups import *
from command.PCBannotations import createAnnotation
from command.PCBglue import createGlue


class dialogMAIN_FORM(QtGui.QDialog):
    def __init__(self, filename=None, parent=None):
        importlib.reload(PCBconf)
        
        QtGui.QDialog.__init__(self, parent)
        freecadSettings = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB")

        self.setWindowTitle(u"PCB settings")
        #self.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
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
        
        self.plytkaPCB_otworyIH = QtGui.QCheckBox(u"Omit intersected holes")  # detecting collisions between holes - intersections
        self.plytkaPCB_otworyIH.setChecked(freecadSettings.GetBool("omitIntersectedHoles", True))
        
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
        
        self.debugImport = QtGui.QCheckBox('Debug import')
        #
        self.spisWarstw = tabela()
        self.spisWarstw.setColumnCount(6)
        self.spisWarstw.setHorizontalHeaderLabels(["", u"ID", "", "Side", "", u"Name"])
        self.spisWarstw.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Fixed)
        self.spisWarstw.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Fixed)
        self.spisWarstw.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Fixed)
        self.spisWarstw.horizontalHeader().setResizeMode(3, QtGui.QHeaderView.Fixed)
        self.spisWarstw.horizontalHeader().resizeSection(0, 25)
        self.spisWarstw.horizontalHeader().resizeSection(1, 35)
        self.spisWarstw.horizontalHeader().resizeSection(2, 35)
        self.spisWarstw.horizontalHeader().resizeSection(3, 85)
        self.spisWarstw.horizontalHeader().resizeSection(4, 95)
        self.spisWarstw.hideColumn(1)
        #######
        layHoles = QtGui.QVBoxLayout()
        layHoles.addWidget(self.plytkaPCB_otworyH)
        layHoles.addWidget(self.plytkaPCB_otworyV)
        layHoles.addWidget(self.plytkaPCB_otworyP)
        layHoles.addWidget(self.plytkaPCB_otworyIH)
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
        layPartSize.setRowStretch(3, 10)
        layPartSize.setEnabled
        #
        self.lay = QtGui.QGridLayout()
        #self.lay.addLayout(layLeftSide, 0, 0, 8, 1, QtCore.Qt.AlignTop)
        self.lay.addWidget(self.spisWarstw, 0, 1, 11, 2)
        self.lay.addWidget(self.selectAll, 10, 1, 1, 1)
        self.lay.addWidget(self.debugImport, 10, 2, 1, 1)
        
        #self.lay.addWidget(self.plytkaPCB, 0, 1, 1, 4)
        self.lay.addWidget(plytkaPCBInfo, 1, 3, 1, 1, QtCore.Qt.AlignLeft)
        self.lay.addWidget(self.gruboscPlytki, 1, 4, 1, 3)
        self.lay.addLayout(layHoles, 2, 3, 1, 3, QtCore.Qt.AlignTop)
        self.lay.addLayout(layHolesRange, 2, 6, 1, 1)
        #lay.addWidget(self.plytkaPCB_PADS, 3, 1, 1, 2)
        self.lay.addWidget(self.plytkaPCB_elementy, 4, 3, 1, 3)
        self.lay.addWidget(self.plytkaPCB_elementyKolory, 5, 3, 1, 3)
        self.lay.addWidget(self.plytkaPCB_grupujElementy, 6, 3, 1, 3)
        self.lay.addWidget(self.adjustParts, 7, 3, 1, 3)
        self.lay.addWidget(self.plytkaPCB_plikER, 8, 3, 1, 3)
        self.lay.addLayout(layPartSize, 5, 6, 5, 1)
        self.lay.addItem(QtGui.QSpacerItem(10, 10), 12, 3, 1, 3)
        # 12 - lib
        self.lay.addItem(QtGui.QSpacerItem(10, 10), 14, 3, 1, 3)
        self.lay.addWidget(buttons, 15, 3, 1, 4, QtCore.Qt.AlignRight)
        self.lay.setRowStretch(9, 10)
        self.lay.setColumnMinimumWidth(2, 200)
        self.lay.setColumnMinimumWidth(3, 120)
        self.setLayout(self.lay)
        self.readSize()
    
    def readSize(self):
        data = configParserRead('openWindow')
        if data:
            try:
                x = int(data['window_x'])
                y = int(data['window_y'])
                w = int(data['window_w'])
                h = int(data['window_h'])
                
                self.setGeometry(x, y, w, h)
            except Exception as e:
                FreeCAD.Console.PrintWarning(u"{0} \n".format(e))
    
    def closeEvent(self, event):
        data = {}
        data['window_x'] = self.x()
        data['window_y'] = self.y()
        data['window_w'] = self.width()
        data['window_h'] = self.height()
        
        configParserWrite('openWindow', data)
        ###########
        event.accept()
        
    #def reject(self):
        ##dialSize = QtCore.QByteArray()
        ##value = freecadSettings.GetString("pcbSettingsDialGeometry", "01d9d0cb0001000000000000000000000000027f000001df00000000000000000000027f000001df000000000000")
        
        ##dialSize.fromHex(eval(value))
        ##self.restoreGeometry(dialSize)
        #FreeCAD.Console.PrintWarning("test")
        
        #return True
        
    def selectAllCategories(self):
        if self.spisWarstw.rowCount() > 0:
            for i in range(self.spisWarstw.rowCount()):
                if self.selectAll.isChecked():
                    self.spisWarstw.cellWidget(i, 0).setCheckState(QtCore.Qt.Checked)
                else:
                    self.spisWarstw.cellWidget(i, 0).setCheckState(QtCore.Qt.Unchecked)

    def generateLayers(self, forbidden=[]):
        ''' '''
        for i, j in self.layersNames.items():
            ######################################
            if self.databaseType == "geda": # gEDA
                layerID = j["type"]
                
                if "bottom" in layerName.lower():
                    layerID += "B"
                elif "top" in layerName.lower():
                    layerID += "T"
            elif self.databaseType == "idf_v2":
                layerID = i
            else:
                layerID = int(i)
            ######################################
            if layerID in forbidden:
                continue
            
            layerName = j['name']
            #
            if layerID in PCBconf.softLayers[self.databaseType]:
                if "name" in PCBconf.softLayers[self.databaseType][layerID].keys():
                    layerName = PCBconf.softLayers[self.databaseType][layerID]["name"]
                
                layerColor = PCBconf.softLayers[self.databaseType][layerID]["color"]
                layerValue = PCBconf.softLayers[self.databaseType][layerID]["value"]
                layerSide = [PCBconf.softLayers[self.databaseType][layerID]["side"], True]  # [layer side, block drop down list TRUE/FALSE]
            else:
                if j['color']:
                    layerColor = j['color']
                else:
                    layerColor = getFromSettings_Color_1('', 4294967295)
                
                layerValue = ['double', u'μm', 34.6, 0, 350]
                layerSide = [1, False]  # [layer side, block drop down list TRUE/FALSE]
            
            ######################################
            # gEDA
            if self.databaseType == "geda":
                layerID += "_" + str(j["number"])
            ######################################
            
            self.spisWarstwAddRow(layerID, layerColor, layerValue, layerName, layerSide)

    def spisWarstwAddRow(self, ID, layerColor, layerTransparent, layerName, layerSide):
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
        if layerSide[0] != -1:
            side = QtGui.QComboBox()
            side.addItem("Top", 1)
            side.addItem("Bottom", 0)
            side.setCurrentIndex(side.findData(layerSide[0]))
            if layerSide[1]:
                side.setDisabled(True)
        else:
            side = QtGui.QLabel("")
        
        self.spisWarstw.setCellWidget(self.spisWarstw.rowCount() - 1, 3, side)
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
        
        self.spisWarstw.setCellWidget(self.spisWarstw.rowCount() - 1, 4, transparent)
        #
        name = QtGui.QTableWidgetItem(layerName)
        name.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        name.setToolTip(u"Click to change name")
        self.spisWarstw.setItem(self.spisWarstw.rowCount() - 1, 5, name)


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
