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

__fcstdFile__ = "connectorDG107V_7_62_01P_14_00AH.fcstd"


class modelPreview(modelPreviewMain):
     def __init__(self, parent=None):
        modelPreviewMain.__init__(self, "connectorDG107V_7_62-01P_14_00AH.png", "DG107V-7.62", parent)
    

class modelGenerateGUI(modelGenerateGUIMain):
    def __init__(self, parent=None):
        modelGenerateGUIMain.__init__(self, parent)
        #
        self.numberOfPins = QtGui.QSpinBox()
        self.numberOfPins.setValue(2)
        self.numberOfPins.setMinimum(2)
        self.numberOfPins.setSingleStep(1)
        #
        self.addMainImageDim("connectorDG107V_7_62-01P_14_00AHDim.png")
        self.mainFormLay.addRow(QtGui.QLabel("Number of pins (l)"), self.numberOfPins)


def modelGenerate(doc, widget):
    print('jest')
    try:
        print(widget.numberOfPins.value())
        doc.Spreadsheet.set('B1', str(widget.numberOfPins.value()))
        doc.recompute()
    except Exception as e:
        print(e)
