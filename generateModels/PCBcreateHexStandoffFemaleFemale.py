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

__fcstdFile__ = "hexStandoffFemaleFemale.FCStd"
__desc__ = "Hex Standoff F/F"


class modelPreview(modelPreviewMain):
     def __init__(self, parent=None):
        modelPreviewMain.__init__(self, "hexStandoffFemaleFemale.png", __desc__, parent)
    

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
        self.length = QtGui.QDoubleSpinBox()
        self.length.setValue(10)
        self.length.setMinimum(0.1)
        self.length.setSingleStep(0.5)
        self.length.setSuffix("mm")
        #
        self.addMainImageDim("hexStandoffFemaleFemaleDim.png")
        self.mainFormLay.addRow(QtGui.QLabel("d1"), self.diameter1)
        self.mainFormLay.addRow(QtGui.QLabel("d2"), self.diameter2)
        self.mainFormLay.addRow(QtGui.QLabel("l"), self.length)
    
    def checkParam(self, dummy):
        self.errors = False
        self.errorsList.setText("")
        #
        if self.diameter1.value() <= self.diameter2.value():
            self.errors = True
            self.errorsList.setText("Error: d1 is smaller (or equal) than d2")


def modelGenerate(doc, widget):
    doc.Spreadsheet.set('B1', str(widget.diameter1.value()))
    doc.Spreadsheet.set('B2', str(widget.diameter2.value()))
    doc.Spreadsheet.set('B3', str(widget.length.value()))
    doc.recompute()
