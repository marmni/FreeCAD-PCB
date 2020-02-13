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

__fcstdFile__ = "connectorpinheader.FCStd"
__desc__ = "Pin header"


class modelPreview(modelPreviewMain):
     def __init__(self, parent=None):
        modelPreviewMain.__init__(self, "connectorGoldpins.png", __desc__, parent)
    

class modelGenerateGUI(modelGenerateGUIMain):
    def __init__(self, parent=None):
        modelGenerateGUIMain.__init__(self, __desc__, parent)
        #
        self.numberOfRows = QtGui.QSpinBox()
        self.numberOfRows.setValue(1)
        self.numberOfRows.setMinimum(1)
        self.numberOfRows.setSingleStep(1)
        #
        self.numberOfCols = QtGui.QSpinBox()
        self.numberOfCols.setValue(1)
        self.numberOfCols.setMinimum(1)
        self.numberOfCols.setSingleStep(1)
        #
        self.pinsHeight1 = QtGui.QDoubleSpinBox()
        self.pinsHeight1.setValue(6.75)
        self.pinsHeight1.setMinimum(0.5)
        self.pinsHeight1.setSingleStep(0.5)
        self.pinsHeight1.setSuffix("mm")
        #
        self.pinsHeight3 = QtGui.QDoubleSpinBox()
        self.pinsHeight3.setValue(2.9)
        self.pinsHeight3.setMinimum(0.5)
        self.pinsHeight3.setSingleStep(0.5)
        self.pinsHeight3.setSuffix("mm")
        #
        self.numberOfSupports = QtGui.QSpinBox()
        self.numberOfSupports.setValue(1)
        self.numberOfSupports.setMinimum(1)
        self.numberOfSupports.setMaximum(3)
        self.numberOfSupports.setSingleStep(1)
        #
        self.supportsSpacing = QtGui.QDoubleSpinBox()
        self.supportsSpacing.setValue(10)
        self.supportsSpacing.setMinimum(3)
        self.supportsSpacing.setSingleStep(0.5)
        self.supportsSpacing.setSuffix("mm")
        #
        self.addMainImageDim("connectorGoldpinsDim.png")
        self.mainFormLay.addRow(QtGui.QLabel("Number of rows"), self.numberOfRows)
        self.mainFormLay.addRow(QtGui.QLabel("Number of cols"), self.numberOfCols)
        self.mainFormLay.addRow(QtGui.QLabel("Raster (r)"), autVariable(2.54))
        self.mainFormLay.addRow(QtGui.QLabel("Pins height (h1)"), self.pinsHeight1)
        self.mainFormLay.addRow(QtGui.QLabel("Pins height (h2)"), autVariable(2.54))
        self.mainFormLay.addRow(QtGui.QLabel("Pins height (h3)"), self.pinsHeight3)
        self.mainFormLay.addRow(QtGui.QLabel("Number of supports"), self.numberOfSupports)
        self.mainFormLay.addRow(QtGui.QLabel("Distance between supports (l)"), self.supportsSpacing)


def modelGenerate(doc, widget):
    doc.Spreadsheet.set('B1', str(widget.pinsHeight3.value()))
    doc.Spreadsheet.set('B3', str(widget.pinsHeight1.value()))
    doc.Spreadsheet.set('B7', str(widget.numberOfRows.value()))
    doc.Spreadsheet.set('B8', str(widget.numberOfCols.value()))
    doc.Spreadsheet.set('B10', str(widget.numberOfSupports.value()))
    doc.Spreadsheet.set('B11', str(widget.supportsSpacing.value()))
    doc.recompute()
