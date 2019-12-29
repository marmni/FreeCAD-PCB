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
from PCBfunctions import kolorWarstwy, mathFunctions, getFromSettings_Color_1
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
        self.gruboscPlytki = QtGui.QDoubleSpinBox()
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
        
        self.plytkaPCB_cutHolesThroughAllLayers = QtGui.QCheckBox(u"Cut holes through all layers")
        self.plytkaPCB_cutHolesThroughAllLayers.setChecked(freecadSettings.GetBool("cutHolesThroughAllLayers", True))
        
        self.holesMin = QtGui.QDoubleSpinBox()
        self.holesMin.setSingleStep(0.1)
        self.holesMin.setValue(0)
        self.holesMin.setSuffix(u" mm")
        
        self.holesMax = QtGui.QDoubleSpinBox()
        self.holesMax.setSingleStep(0.1)
        self.holesMax.setValue(0)
        self.holesMax.setSuffix(u" mm")
        #######
        #self.plytkaPCB_PADS = QtGui.QCheckBox(u"Vias")
        #self.plytkaPCB_PADS.setChecked(True)
        #######
        self.plytkaPCB_plikER = QtGui.QCheckBox(u"Generate report")
        self.plytkaPCB_plikER.setChecked(freecadSettings.GetBool("partsReport", False))
        #self.plytkaPCB_plikER.setStyleSheet('margin-left:20px')
        self.plytkaPCB_plikER.setEnabled(freecadSettings.GetBool("partsImport", True))
        #######
        plytkaPCB_GP_TT = QtGui.QLabel("")
        plytkaPCB_GP_TT.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        plytkaPCB_GP_TT.setPixmap(QtGui.QPixmap(":/data/img/info_16x16.png"))
        plytkaPCB_GP_TT.setToolTip('<b>Group parts</b><br><img src=":/data/img/groupParts.png">')
        
        self.plytkaPCB_grupujElementy = QtGui.QCheckBox(u"Group parts")
        self.plytkaPCB_grupujElementy.setChecked(freecadSettings.GetBool("groupParts", False))
        self.plytkaPCB_grupujElementy.setEnabled(freecadSettings.GetBool("partsImport", True))
        #######
        plytkaPCB_EK_TT = QtGui.QLabel("")
        plytkaPCB_EK_TT.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        plytkaPCB_EK_TT.setPixmap(QtGui.QPixmap(":/data/img/info_16x16.png"))
        plytkaPCB_EK_TT.setToolTip('<b>Colorize elements</b><br><img src=":/data/img/colorizeModels.png">')
        
        self.plytkaPCB_elementyKolory = QtGui.QCheckBox(u"Colorize elements")
        self.plytkaPCB_elementyKolory.setChecked(freecadSettings.GetBool("partsColorize", True))
        #self.plytkaPCB_elementyKolory.setStyleSheet('margin-left:20px')
        self.plytkaPCB_elementyKolory.setEnabled(freecadSettings.GetBool("partsImport", True))
        #######
        plytkaPCB_APNV_TT = QtGui.QLabel("")
        plytkaPCB_APNV_TT.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        plytkaPCB_APNV_TT.setPixmap(QtGui.QPixmap(":/data/img/info_16x16.png"))
        plytkaPCB_APNV_TT.setToolTip('<b>Adjust part name/value</b><br><img src=":/data/img/adjustPartNameValue.png">')
        
        self.adjustParts = QtGui.QCheckBox(u"Adjust part name/value")
        self.adjustParts.setChecked(freecadSettings.GetBool("adjustNameValue", False))
        #self.adjustParts.setStyleSheet('margin-left:20px')
        self.adjustParts.setEnabled(freecadSettings.GetBool("partsImport", True))
        #######
        self.partMinX = QtGui.QDoubleSpinBox()
        self.partMinX.setSingleStep(0.1)
        self.partMinX.setValue(0)
        self.partMinX.setSuffix(u" mm")
        self.partMinX.setEnabled(freecadSettings.GetBool("partsImport", True))
        
        self.partMinY = QtGui.QDoubleSpinBox()
        self.partMinY.setSingleStep(0.1)
        self.partMinY.setValue(0)
        self.partMinY.setSuffix(u" mm")
        self.partMinY.setEnabled(freecadSettings.GetBool("partsImport", True))
        
        self.partMinZ = QtGui.QDoubleSpinBox()
        self.partMinZ.setSingleStep(0.1)
        self.partMinZ.setValue(0)
        self.partMinZ.setSuffix(u" mm")
        self.partMinZ.setEnabled(freecadSettings.GetBool("partsImport", True))
        #######
        # buttons
        buttons = QtGui.QDialogButtonBox()
        buttons.addButton(u"Cancel", QtGui.QDialogButtonBox.RejectRole)
        buttons.addButton(u"Accept", QtGui.QDialogButtonBox.AcceptRole)
        self.connect(buttons, QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        self.connect(buttons, QtCore.SIGNAL("rejected()"), self, QtCore.SLOT("reject()"))
        #
        self.selectAll = QtGui.QCheckBox('de/select all layers')
        self.selectAll.setStyleSheet('''border:1px solid rgb(237, 237, 237);''')
        self.connect(self.selectAll, QtCore.SIGNAL("clicked()"), self.selectAllCategories)
        #
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
        filterholesBox = QtGui.QGroupBox("Filter by diameter")
        filterholesBox.setFixedWidth(200)
        filterholesBoxLay = QtGui.QGridLayout(filterholesBox)
        filterholesBoxLay.addWidget(QtGui.QLabel(u"min."), 0, 0, 1, 1)
        filterholesBoxLay.addWidget(self.holesMin, 0, 1, 1, 1)
        filterholesBoxLay.addWidget(QtGui.QLabel(u"max."), 1, 0, 1, 1)
        filterholesBoxLay.addWidget(self.holesMax, 1, 1, 1, 1)
        filterholesBoxLay.addItem(QtGui.QSpacerItem(1, 10), 2, 1, 1, 1)
        filterholesBoxLay.addWidget(QtGui.QLabel(u"0mm -> skip parameter/limit"), 3, 0, 1, 2, QtCore.Qt.AlignCenter)
        
        holesBox = QtGui.QGroupBox("Holes")
        layHoles = QtGui.QGridLayout(holesBox)
        layHoles.addWidget(self.plytkaPCB_otworyH, 0, 0, 1, 1)
        layHoles.addWidget(self.plytkaPCB_otworyV, 1, 0, 1, 1)
        layHoles.addWidget(self.plytkaPCB_otworyP, 2, 0, 1, 1)
        layHoles.addWidget(self.plytkaPCB_otworyIH, 3, 0, 1, 1)
        layHoles.addWidget(self.plytkaPCB_cutHolesThroughAllLayers, 4, 0, 1, 1)
        
        layHoles.addWidget(filterholesBox, 0, 1, 5, 1)
        layHoles.setColumnStretch(0, 60)
        layHoles.setColumnStretch(1, 40)
        ####################
        filterPartsBox = QtGui.QGroupBox("Filter by size (3D models)")
        filterPartsBox.setFixedWidth(200)
        filterPartsBoxLay = QtGui.QGridLayout(filterPartsBox)
        filterPartsBoxLay.addWidget(QtGui.QLabel(u"Length"), 0, 0, 1, 1)
        filterPartsBoxLay.addWidget(self.partMinX, 0, 1, 1, 1)
        filterPartsBoxLay.addWidget(QtGui.QLabel(u"Width"), 1, 0, 1, 1)
        filterPartsBoxLay.addWidget(self.partMinY, 1, 1, 1, 1)
        filterPartsBoxLay.addWidget(QtGui.QLabel(u"Height"), 2, 0, 1, 1)
        filterPartsBoxLay.addWidget(self.partMinZ, 2, 1, 1, 1)
        filterPartsBoxLay.addItem(QtGui.QSpacerItem(1, 10), 3, 1, 1, 1)
        filterPartsBoxLay.addWidget(QtGui.QLabel(u"0mm -> skip parameter/limit"), 4, 0, 1, 2, QtCore.Qt.AlignCenter)
        
        self.partsBox = QtGui.QGroupBox("Parts")
        self.partsBox.setCheckable(True)
        self.partsBox.setChecked(freecadSettings.GetBool("partsImport", True))
        self.connect(self.partsBox, QtCore.SIGNAL("toggled (bool)"), self.plytkaPCB_plikER.setEnabled)
        self.connect(self.partsBox, QtCore.SIGNAL("toggled (bool)"), self.plytkaPCB_elementyKolory.setEnabled)
        self.connect(self.partsBox, QtCore.SIGNAL("toggled (bool)"), self.adjustParts.setEnabled)
        self.connect(self.partsBox, QtCore.SIGNAL("toggled (bool)"), self.plytkaPCB_grupujElementy.setEnabled)
        self.connect(self.partsBox, QtCore.SIGNAL("toggled (bool)"), filterPartsBox.setEnabled)
        try:
            self.connect(self.partsBox, QtCore.SIGNAL("toggled (bool)"), self.packageByDecal.setEnabled)  # IDF
        except:
            pass
        
        self.layParts = QtGui.QGridLayout(self.partsBox)
        self.layParts.addWidget(plytkaPCB_EK_TT, 0, 0, 1, 1)
        self.layParts.addWidget(self.plytkaPCB_elementyKolory, 0, 1, 1, 1)
        self.layParts.addWidget(plytkaPCB_APNV_TT, 1, 0, 1, 1)
        self.layParts.addWidget(self.adjustParts, 1, 1, 1, 1)
        self.layParts.addWidget(plytkaPCB_GP_TT, 2, 0, 1, 1)
        self.layParts.addWidget(self.plytkaPCB_grupujElementy, 2, 1, 1, 1)
        self.layParts.addWidget(self.plytkaPCB_plikER, 3, 1, 1, 1)
        #4 decals IDF
        self.layParts.addWidget(filterPartsBox, 0, 2, 6, 1)
        self.layParts.setColumnStretch(1, 60)
        self.layParts.setColumnStretch(2, 40)
        ####################
        self.razenBiblioteki = QtGui.QLineEdit('')
        
        otherBox = QtGui.QGroupBox("Other settings")
        self.layOther = QtGui.QGridLayout(otherBox)
        #self.layOther.addWidget(QtGui.QLabel(u"Library"), 0, 0, 1, 1) # library
        #self.layOther.addWidget(self.razenBiblioteki, 0, 1, 1, 2) # library
        self.layOther.addWidget(self.debugImport, 1, 0, 1, 3)
        ##############################################
        mainWidgetLeftSide = QtGui.QWidget()
        layLeftSide = QtGui.QGridLayout(mainWidgetLeftSide)
        layLeftSide.addWidget(self.spisWarstw, 0, 0, 1, 2)
        layLeftSide.addWidget(self.selectAll, 1, 0, 1, 1)
        layLeftSide.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Expanding), 1, 1, 1, 1)
        #
        mainWidgetRightSide = QtGui.QWidget()
        layRightSide = QtGui.QGridLayout(mainWidgetRightSide)
        layRightSide.addWidget(plytkaPCBInfo, 0, 0, 1, 1, QtCore.Qt.AlignLeft)
        layRightSide.addWidget(self.gruboscPlytki, 0, 1, 1, 1)
        layRightSide.addItem(QtGui.QSpacerItem(1, 10), 1, 0, 1, 1)
        layRightSide.addWidget(holesBox, 2, 0, 1, 2, QtCore.Qt.AlignTop)
        layRightSide.addWidget(self.partsBox, 3, 0, 1, 2, QtCore.Qt.AlignTop)
        layRightSide.addWidget(otherBox, 4, 0, 1, 2, QtCore.Qt.AlignTop)
        layRightSide.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding), 5, 1, 1, 1)
        #
        self.splitter = QtGui.QSplitter()
        self.splitter.setStyleSheet('QSplitter::handle {background: rgba(31.8, 33.3, 33.7, 0.1); cursor: col-resize;} ')
        self.splitter.setChildrenCollapsible(False)
        self.splitter.addWidget(mainWidgetLeftSide)
        self.splitter.addWidget(mainWidgetRightSide)
        
        mainLay = QtGui.QGridLayout()
        mainLay.addWidget(self.splitter, 0, 0, 1, 3)
        mainLay.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Expanding), 1, 0, 1, 1)
        mainLay.addWidget(buttons, 1, 1, 1, 1, QtCore.Qt.AlignRight)
        mainLay.addItem(QtGui.QSpacerItem(2, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum), 1, 2, 1, 1)
        self.setLayout(mainLay)
        #
        self.readSize()
    
    def readSize(self):
        try:
            data = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("openWindow", "").strip()
            if data != "":
                data = eval(data)
                
                x = int(data[0])
                y = int(data[1]) + 30
                w = int(data[2])
                h = int(data[3])
                
                self.setGeometry(x, y, w, h)
        except Exception as e:
            FreeCAD.Console.PrintWarning(u"{0} \n".format(e))

    def closeEvent(self, event):
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").SetString('openWindow', str([self.x(), self.y(), self.width(), self.height()]))
        #
        event.accept()

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
            layerName = j['name']
            ######################################
            if self.databaseType == "geda": # gEDA
                layerID = j["type"]
                
                if "bottom" in layerName.lower():
                    layerID += "B"
                elif "top" in layerName.lower():
                    layerID += "T"
            elif self.databaseType in ["idf"]:
                layerID = i
            else:
                layerID = int(i)
            ######################################
            if layerID in forbidden:
                continue
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
                #
                layerSide = [1, False]  # [layer side, block drop down list TRUE/FALSE]
                if "side" in j.keys() and j["side"] == "BOTTOM":
                    layerSide[0] = 0
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
