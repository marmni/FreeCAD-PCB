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
import FreeCAD
#
from PCBobjects import layerSilkObject, viewProviderLayerSilkObject
from PCBfunctions import kolorWarstwy, getFromSettings_Color_1
from PCBboard import getPCBheight
from command.PCBgroups import createGroup_Layers


def createDrillcenter(size, color):
    pcb = getPCBheight()
    #
    if not FreeCAD.activeDocument() or not pcb[0]:
        return False
    else:
        doc = FreeCAD.activeDocument()
    
    if size == 0:
        return False
    #
    try:
        obj = None
        for i in FreeCAD.activeDocument().Objects:
            if hasattr(i, "Proxy") and hasattr(i.Proxy, "Type") and 'PCBcenterDrill' in i.Proxy.Type:
                obj = i
                break
    except Exception as e:
        FreeCAD.Console.PrintWarning(str(e) + "\n")
    #
    try:
        if not obj:
            layerS = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", 'centerDrill')
            layerNew = layerSilkObject(layerS, ['PCBcenterDrill'])
            layerNew.defHeight = pcb[1] + 0.000001
            layerNew.side = 2
        else:
            layerS = obj
            layerNew = obj.Proxy
            #
            layerNew.spisObiektowTXT = []
    except:
        FreeCAD.Console.PrintWarning(str(e) + "\n")
        return False
    else:
        for j in doc.Objects:
            if hasattr(j, "Proxy") and hasattr(j.Proxy, "Type") and j.Proxy.Type == "PCBboard":
                try:
                    for k in range(len(j.Holes.Geometry)):
                        if j.Holes.Geometry[k].Construction or str(j.Holes.Geometry[k].__class__) != "<class 'Part.Circle'>":
                            continue
                        
                        x = j.Holes.Geometry[k].Center.x
                        y = j.Holes.Geometry[k].Center.y
                        r1 = j.Holes.Geometry[k].Radius
                        r2 = size / 2.
                        
                        if r1 > r2:
                            layerNew.addCircle(x, y, r1)
                            layerNew.setFace()
                            layerNew.circleCutHole(x, y, r2)
                    break
                except Exception as e:
                    FreeCAD.Console.PrintWarning(str(e) + "\n")
        #######
        layerNew.generuj(layerS)
        #layerNew.updatePosition_Z(layerS, pcb[1])
        viewProviderLayerSilkObject(layerS.ViewObject)
        layerS.ViewObject.ShapeColor = color
        
        grp = createGroup_Layers()
        grp.addObject(layerS)
        pcb[2].addObject(layerS)
        #
        return True
    


class createDrillcenter_Gui(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.form = self
        self.form.setWindowTitle(u"Create drill center")
        self.form.setWindowIcon(QtGui.QIcon(":/data/img/drilling.svg"))
        #
        self.holeSize = QtGui.QDoubleSpinBox()
        self.holeSize.setValue(0.4)
        self.holeSize.setMinimum(0.1)
        self.holeSize.setSuffix('mm')
        self.holeSize.setSingleStep(0.1)
        #
        self.pcbColor = kolorWarstwy()
        self.pcbColor.setColor(getFromSettings_Color_1('CenterDrillColor', 4294967295))
        self.pcbColor.setToolTip(u"Click to change color")
        #
        lay = QtGui.QGridLayout(self)
        lay.addWidget(QtGui.QLabel('Hole size'), 0, 0, 1, 1)
        lay.addWidget(self.holeSize, 0, 1, 1, 1)
        lay.addWidget(QtGui.QLabel(u'Color:'), 1, 0, 1, 1)
        lay.addWidget(self.pcbColor, 1, 1, 1, 1)
        
    def accept(self):
        createDrillcenter(self.holeSize.value(), self.pcbColor.getColor())
        return True
