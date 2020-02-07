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

__fcstdFile__ = "connectorAmpQuickAngle.fcstd"


class modelPreview(modelPreviewMain):
     def __init__(self, parent=None):
        modelPreviewMain.__init__(self, "connectorAmpQuickAngle.png", "Amp Quick Angle", parent)
    

class modelGenerateGUI(modelGenerateGUIMain):
    def __init__(self, parent=None):
        modelGenerateGUIMain.__init__(self, parent)
        #
        self.numberOfPins = QtGui.QSpinBox()
        self.numberOfPins.setValue(2)
        self.numberOfPins.setMinimum(2)
        self.numberOfPins.setSingleStep(1)
        #
        self.modelRaster = QtGui.QDoubleSpinBox()
        self.modelRaster.setValue(2.54)
        self.modelRaster.setMinimum(1.27)
        self.modelRaster.setSingleStep(1.27)
        self.modelRaster.setDisabled(True)
        #
        self.addMainImageDim("connectorAmpQuickAngleDim.png")
        self.mainFormLay.addRow(QtGui.QLabel("Number of pins (l)"), self.numberOfPins)
        self.mainFormLay.addRow(QtGui.QLabel("Raster(a)"), self.modelRaster)


def modelGenerate(doc, widget):
    doc.Spreadsheet.set('B1', str(widget.numberOfPins.value()))
    doc.recompute()
