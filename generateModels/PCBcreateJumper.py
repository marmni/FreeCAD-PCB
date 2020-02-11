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

__fcstdFile__ = "jumper.FCStd"
__desc__ = "Jumper"


class modelPreview(modelPreviewMain):
     def __init__(self, parent=None):
        modelPreviewMain.__init__(self, "jumper.png", __desc__, parent)
    

class modelGenerateGUI(modelGenerateGUIMain):
    def __init__(self, parent=None):
        modelGenerateGUIMain.__init__(self, __desc__, parent)
        #
        self.diameter = QtGui.QDoubleSpinBox()
        self.diameter.setValue(1)
        self.diameter.setMinimum(0.5)
        self.diameter.setSingleStep(0.5)
        self.diameter.setSuffix("mm")
        #
        self.modelRaster = QtGui.QDoubleSpinBox()
        self.modelRaster.setValue(10)
        self.modelRaster.setMinimum(0.5)
        self.modelRaster.setSingleStep(0.5)
        self.modelRaster.setSuffix("mm")
        #
        self.addMainImageDim("jumperDim.png")
        self.mainFormLay.addRow(QtGui.QLabel("Diameter (a)"), self.diameter)
        self.mainFormLay.addRow(QtGui.QLabel("Raster (r)"), self.modelRaster)


def modelGenerate(doc, widget):
    doc.Spreadsheet.set('B1', str(widget.diameter.value()))
    doc.Spreadsheet.set('B3', str(widget.modelRaster.value()))
    doc.recompute()
