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

__fcstdFile__ = "connectorMSTBA_V.fcstd"
__desc__ = "MSTBA"


class modelPreview(modelPreviewMain):
     def __init__(self, parent=None):
        modelPreviewMain.__init__(self, "connectorMSTBA_V.png", __desc__, parent)
    

class modelGenerateGUI(modelGenerateGUIMain):
    def __init__(self, parent=None):
        modelGenerateGUIMain.__init__(self, __desc__, parent)
        #
        self.numberOfPins = QtGui.QSpinBox()
        self.numberOfPins.setValue(2)
        self.numberOfPins.setMinimum(2)
        self.numberOfPins.setSingleStep(1)
        #
        self.addMainImageDim("connectorMSTBA_VDim.png")
        self.mainFormLay.addRow(QtGui.QLabel("Number of pins"), self.numberOfPins)
        self.mainFormLay.addRow(QtGui.QLabel("Raster(r)"), autVariable(5.0))


def modelGenerate(doc, widget):
    doc.Spreadsheet.set('B1', str(widget.numberOfPins.value()))
    doc.recompute()
