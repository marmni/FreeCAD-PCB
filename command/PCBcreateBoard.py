# -*- coding: utf8 -*-
#****************************************************************************
#*                                                                          *
#*   Printed Circuit Board Workbench for FreeCAD             PCB            *
#*   Flexible Printed Circuit Board Workbench for FreeCAD    FPCB           *
#*   Copyright (c) 2013, 2014, 2015                                         *
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

import FreeCAD
import FreeCADGui
from PySide import QtGui
#
import PCBconf
from PCBpartManaging import partsManaging
from PCBfunctions import kolorWarstwy
from PCBboard import PCBboardObject, viewProviderPCBboardObject
from command.PCBgroups import createGroup_PCB


class SelObserver:
    def __init__(self, main):
        self.main = main
    
    def addSelection(self, doc, obj, sub, pnt):
        self.main.wybrano(FreeCAD.ActiveDocument.getObject(str(obj)))


class pickSketch(QtGui.QPushButton):
    def __init__(self, saveToForm, parent=None):
        QtGui.QPushButton.__init__(self, parent)
        self.setText('...')
        self.setFixedWidth(30)
        self.setFlat(True)
        self.setStyleSheet('''
                QPushButton
                {
                    border: 1px solid #000;
                    width: 13px;
                    height: 19px;
                }
            ''')
        
        self.saveToForm = saveToForm

    def wybrano(self, obj):
        if obj.isDerivedFrom("Sketcher::SketchObject"):
            self.saveToForm.setText(obj.Name)
        FreeCADGui.Selection.removeObserver(self.s)

    def mousePressEvent(self, event):
        self.s = SelObserver(self)
        FreeCADGui.Selection.addObserver(self.s)
        
        return super(pickSketch, self).mousePressEvent(event)


class createPCB(QtGui.QWidget, partsManaging):
    def __init__(self, parent=None):
        reload(PCBconf)
        
        QtGui.QWidget.__init__(self, parent)
        freecadSettings = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB")
        
        self.form = self
        self.form.setWindowTitle(u"Create PCB")
        self.form.setWindowIcon(QtGui.QIcon(":/data/img/board.png"))
        #
        self.gruboscPlytki = QtGui.QDoubleSpinBox(self)
        self.gruboscPlytki.setSingleStep(0.1)
        self.gruboscPlytki.setValue(freecadSettings.GetFloat("boardThickness", 1.5))
        self.gruboscPlytki.setSuffix(u" mm")
        #
        self.pcbBorder = QtGui.QLineEdit('')
        self.pcbBorder.setReadOnly(True)
        
        pickPcbBorder = pickSketch(self.pcbBorder)
        #
        self.pcbHoles = QtGui.QLineEdit('')
        self.pcbHoles.setReadOnly(True)
        
        pickPcbHoles = pickSketch(self.pcbHoles)
        #
        self.pcbColor = kolorWarstwy()
        self.pcbColor.setColor(self.pcbColor.PcbColorToRGB(PCBconf.PCB_COLOR))
        self.pcbColor.setToolTip(u"Click to change color")
        #
        lay = QtGui.QGridLayout()
        lay.addWidget(QtGui.QLabel(u'Border:'), 0, 0, 1, 1)
        lay.addWidget(self.pcbBorder, 0, 1, 1, 1)
        lay.addWidget(pickPcbBorder, 0, 2, 1, 1)
        lay.addWidget(QtGui.QLabel(u'Holes:'), 1, 0, 1, 1)
        lay.addWidget(self.pcbHoles, 1, 1, 1, 1)
        lay.addWidget(pickPcbHoles, 1, 2, 1, 1)
        lay.addWidget(QtGui.QLabel(u'Thickness:'), 2, 0, 1, 1)
        lay.addWidget(self.gruboscPlytki, 2, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Color:'), 3, 0, 1, 1)
        lay.addWidget(self.pcbColor, 3, 1, 1, 2)
        #
        self.setLayout(lay)
    
    def accept(self):
        if self.pcbBorder.text() == '' or self.pcbHoles.text() == '':
            FreeCAD.Console.PrintWarning("Mandatory field is empty!\n")
        elif self.pcbBorder.text() == self.pcbHoles.text():
            FreeCAD.Console.PrintWarning("One sketch used two times!\n")
        else:
            groupBRD = createGroup_PCB()
            
            PCBboard = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Board")
            PCBboardObject(PCBboard)
            PCBboard.Thickness = self.gruboscPlytki.value()
            PCBboard.Border = FreeCAD.ActiveDocument.getObject(self.pcbBorder.text())
            PCBboard.Holes = FreeCAD.ActiveDocument.getObject(self.pcbHoles.text())
            viewProviderPCBboardObject(PCBboard.ViewObject)
            groupBRD.addObject(FreeCAD.ActiveDocument.Board)
            FreeCADGui.activeDocument().getObject(PCBboard.Name).ShapeColor = self.pcbColor.getColor()
            FreeCAD.ActiveDocument.getObject(self.pcbBorder.text()).ViewObject.Visibility = False
            FreeCAD.ActiveDocument.getObject(self.pcbHoles.text()).ViewObject.Visibility = False
            return True
