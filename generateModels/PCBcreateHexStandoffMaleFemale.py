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
from PySide import QtCore, QtGui
from PCBmainModule import modelPreviewMain, modelGenerateGUIMain, modelPictureDim

__fcstdFile__ = "hexStandoffMaleFemale.FCStd"
__desc__ = "Hex Standoff M/F"


class modelPreview(modelPreviewMain):
     def __init__(self, parent=None):
        modelPreviewMain.__init__(self, "hexStandoffMaleFemale.png", __desc__, parent)
    

class modelGenerateGUI(modelGenerateGUIMain):
    def __init__(self, parent=None):
        modelGenerateGUIMain.__init__(self, __desc__, parent)
        #
        self.diameter1 = QtGui.QDoubleSpinBox()
        self.diameter1.setValue(5.6)
        self.diameter1.setMinimum(0.5)
        self.diameter1.setSingleStep(0.5)
        self.diameter1.setSuffix("mm")
        self.connect(self.diameter1, QtCore.SIGNAL("valueChanged (double)"), self.checkParam)
        #
        self.diameter2 = QtGui.QDoubleSpinBox()
        self.diameter2.setMinimum(0.5)
        self.diameter2.setSingleStep(0.5)
        self.diameter2.setSuffix("mm")
        self.connect(self.diameter2, QtCore.SIGNAL("valueChanged (double)"), self.checkParam)
        self.diameter2.setValue(3)
        #
        self.length1 = QtGui.QDoubleSpinBox()
        self.length1.setValue(10)
        self.length1.setMinimum(0.1)
        self.length1.setSingleStep(0.5)
        self.length1.setSuffix("mm")
        self.connect(self.length1, QtCore.SIGNAL("valueChanged (double)"), self.checkParam)
        #
        self.length2 = QtGui.QDoubleSpinBox()
        self.length2.setValue(6)
        self.length2.setMinimum(0.1)
        self.length2.setSingleStep(0.5)
        self.length2.setSuffix("mm")
        #
        self.length3 = QtGui.QDoubleSpinBox()
        self.length3.setValue(6)
        self.length3.setMinimum(0.1)
        self.length3.setSingleStep(0.5)
        self.length3.setSuffix("mm")
        self.connect(self.length3, QtCore.SIGNAL("valueChanged (double)"), self.checkParam)
        #
        self.addMainImageDim("hexStandoffMaleFemaleDim.png")
        self.mainFormLay.addRow(QtGui.QLabel("d1"), self.diameter1)
        self.mainFormLay.addRow(QtGui.QLabel("d2"), self.diameter2)
        self.mainFormLay.addRow(QtGui.QLabel("l1"), self.length1)
        self.mainFormLay.addRow(QtGui.QLabel("l2"), self.length2)
        self.mainFormLay.addRow(QtGui.QLabel("l3"), self.length3)
    
    def checkParam(self, dummy):
        self.errors = False
        self.errorsList.setText("")
        #
        try:
            if self.diameter1.value() <= self.diameter2.value():
                self.errors = True
                self.errorsList.setText("Error: d1 is smaller (or equal) than d2\n")
            
            if self.length1.value() <= self.length3.value():
                self.errors = True
                self.errorsList.setText(self.errorsList.text() + "Error: l1 is smaller (or equal) than l3\n")
        except:
            pass


def modelGenerate(doc, widget):
    doc.Spreadsheet.set('B1', str(widget.diameter1.value()))
    doc.Spreadsheet.set('B2', str(widget.diameter2.value()))
    doc.Spreadsheet.set('B3', str(widget.length1.value()))
    doc.Spreadsheet.set('B4', str(widget.length2.value()))
    doc.Spreadsheet.set('B5', str(widget.length3.value()))
    doc.recompute()
