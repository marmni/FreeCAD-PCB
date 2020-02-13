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
from PCBmainModule import modelPreviewMain, modelGenerateGUIMain, modelPictureDim, autVariable

__fcstdFile__ = "diodeThmDO.FCStd"
__desc__ = "DO-x"


class modelPreview(modelPreviewMain):
     def __init__(self, parent=None):
        modelPreviewMain.__init__(self, "diodeThmDO.png", __desc__, parent)
    

class modelGenerateGUI(modelGenerateGUIMain):
    def __init__(self, parent=None):
        modelGenerateGUIMain.__init__(self, __desc__, parent)
        #
        self.diameter = QtGui.QDoubleSpinBox()
        self.diameter.setValue(2.71)
        self.diameter.setMinimum(0.5)
        self.diameter.setSingleStep(0.5)
        self.diameter.setSuffix("mm")
        self.connect(self.diameter, QtCore.SIGNAL("valueChanged (double)"), self.checkParam)
        #
        self.diameter2 = QtGui.QDoubleSpinBox()
        self.diameter2.setValue(0.85)
        self.diameter2.setMinimum(0.5)
        self.diameter2.setSingleStep(0.5)
        self.diameter2.setSuffix("mm")
        self.connect(self.diameter2, QtCore.SIGNAL("valueChanged (double)"), self.checkParam)
        #
        self.len_1 = QtGui.QDoubleSpinBox()
        self.len_1.setValue(5.2)
        self.len_1.setSuffix("mm")
        self.len_1.setMinimum(0.2)
        self.len_1.setSingleStep(0.2)
        self.connect(self.len_1, QtCore.SIGNAL("valueChanged (double)"), self.checkParam)
        #
        self.len_2 = QtGui.QDoubleSpinBox()
        self.len_2.setMinimum(0.5)
        self.len_2.setSuffix("mm")
        self.len_2.setSingleStep(0.5)
        self.connect(self.len_2, QtCore.SIGNAL("valueChanged (double)"), self.checkParam)
        self.len_2.setValue(10)
        #
        self.addMainImageDim("diodeThmDODim.png")
        self.mainFormLay.addRow(QtGui.QLabel("d1"), self.diameter)
        self.mainFormLay.addRow(QtGui.QLabel("d2"), self.diameter2)
        self.mainFormLay.addRow(QtGui.QLabel("l"), self.len_1)
        self.mainFormLay.addRow(QtGui.QLabel("Raster (r)"), self.len_2)
    
    def checkParam(self, dummy):
        self.errors = False
        self.errorsList.setText("")
        #
        try:
            if self.diameter.value() <= self.diameter2.value():
                self.errors = True
                self.errorsList.setText("Error: d1 is smaller (or equal) than d2\n")
            if self.len_1.value() >= self.len_2.value():
                self.errors = True
                self.errorsList.setText(self.errorsList.text() + "Error: r is smaller (or equal) than l\n")
        except:
            pass


def modelGenerate(doc, widget):
    doc.Spreadsheet.set('B1', str(widget.diameter.value()))
    doc.Spreadsheet.set('B2', str(widget.diameter2.value()))
    doc.Spreadsheet.set('B3', str(widget.len_1.value()))
    doc.Spreadsheet.set('B4', str(widget.len_2.value()))
    doc.recompute()
