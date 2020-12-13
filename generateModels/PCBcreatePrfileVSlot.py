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

__fcstdFile__ = "profileVSlot.FCStd"
__desc__ = "Profile V-Slot"


class modelPreview(modelPreviewMain):
     def __init__(self, parent=None):
        modelPreviewMain.__init__(self, "profileVSlot.png", __desc__, parent)
    

class modelGenerateGUI(modelGenerateGUIMain):
    def __init__(self, parent=None):
        modelGenerateGUIMain.__init__(self, __desc__, parent)
        #
        self.length = QtGui.QDoubleSpinBox()
        self.length.setValue(100)
        self.length.setMinimum(10)
        self.length.setMaximum(2000)
        self.length.setSingleStep(1)
        self.length.setSuffix("mm")
        #
        self.rows = QtGui.QDoubleSpinBox()
        self.rows.setValue(1)
        self.rows.setMinimum(1)
        self.rows.setSingleStep(1)
        #
        self.addMainImageDim("profileVSlotDim.png")
        self.mainFormLay.addRow(QtGui.QLabel("Length (l)"), self.length)
        self.mainFormLay.addRow(QtGui.QLabel("Rows (r)"), self.rows)


def modelGenerate(doc, widget):
    doc.Spreadsheet.set('B1', str(widget.length.value()))
    doc.Spreadsheet.set('B2', str(widget.rows.value()))
    doc.recompute()
