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

__fcstdFile__ = "capacitor1.FCStd"
__desc__ = "Capacitor 1 THT"


class modelPreview(modelPreviewMain):
     def __init__(self, parent=None):
        modelPreviewMain.__init__(self, "capacitor1.png", __desc__, parent)
    

class modelGenerateGUI(modelGenerateGUIMain):
    def __init__(self, parent=None):
        modelGenerateGUIMain.__init__(self, __desc__, parent)
        #
        self.diameter = QtGui.QDoubleSpinBox()
        self.diameter.setValue(0.5)
        self.diameter.setMinimum(0.2)
        self.diameter.setSingleStep(0.2)
        self.diameter.setSuffix("mm")
        #
        self.len_1 = QtGui.QDoubleSpinBox()
        self.len_1.setValue(18)
        self.len_1.setSuffix("mm")
        self.len_1.setMinimum(0.2)
        self.len_1.setSingleStep(0.2)
        self.connect(self.len_1, QtCore.SIGNAL("valueChanged (double)"), self.checkParam)
        #
        self.len_2 = QtGui.QDoubleSpinBox()
        self.len_2.setMinimum(0.5)
        self.len_2.setSuffix("mm")
        self.len_2.setSingleStep(0.5)
        self.len_2.setValue(13)
        #
        self.len_3 = QtGui.QDoubleSpinBox()
        self.len_3.setMinimum(0.5)
        self.len_3.setSuffix("mm")
        self.len_3.setSingleStep(0.5)
        self.len_3.setValue(7)
        #
        self.len_4 = QtGui.QDoubleSpinBox()
        self.len_4.setMinimum(0.5)
        self.len_4.setSuffix("mm")
        self.len_4.setSingleStep(0.5)
        self.connect(self.len_4, QtCore.SIGNAL("valueChanged (double)"), self.checkParam)
        self.len_4.setValue(15)
        #
        self.addMainImageDim("capacitor1Dim.png")
        self.mainFormLay.addRow(QtGui.QLabel("w"), self.len_1)
        self.mainFormLay.addRow(QtGui.QLabel("h"), self.len_2)
        self.mainFormLay.addRow(QtGui.QLabel("d"), self.len_3)
        self.mainFormLay.addRow(QtGui.QLabel("d1"), self.diameter)
        self.mainFormLay.addRow(QtGui.QLabel("Raster (r)"), self.len_4)
    
    def checkParam(self, dummy):
        self.errors = False
        self.errorsList.setText("")
        #
        try:
            if self.len_1.value() <= self.len_4.value():
                self.errors = True
                self.errorsList.setText("Error: w is smaller (or equal) than r\n")
        except:
            pass

def modelGenerate(doc, widget):
    doc.Spreadsheet.set('B1', str(widget.len_1.value()))
    doc.Spreadsheet.set('B2', str(widget.len_2.value()))
    doc.Spreadsheet.set('B3', str(widget.len_3.value()))
    doc.Spreadsheet.set('B4', str(widget.len_4.value()))
    doc.Spreadsheet.set('B5', str(widget.diameter.value()))
    doc.recompute()
