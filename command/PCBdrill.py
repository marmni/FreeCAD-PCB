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

from PySide import QtCore, QtGui
import FreeCAD
#
from PCBobjects import layerSilkObject, viewProviderLayerSilkObject
from PCBfunctions import kolorWarstwy, getFromSettings_Color_1
from PCBboard import getPCBheight
from command.PCBgroups import createGroup_Layers


def createDrillcenter(size, color):
    if not FreeCAD.activeDocument() or not getPCBheight()[0]:
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
    except Exception, e:
        FreeCAD.Console.PrintWarning(str(e) + "\n")
    #
    try:
        if not obj:
            layerS = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", 'centerDrill')
            layerNew = layerSilkObject(layerS, ['PCBcenterDrill'])
        else:
            layerS = obj
            layerNew = obj.Proxy
            #
            layerNew.spisObiektowTXT = []
    except Exception, e:
        FreeCAD.Console.PrintWarning(str(e) + "\n")
    #
    for j in doc.Objects:
        if hasattr(j, "Proxy") and hasattr(j.Proxy, "Type") and j.Proxy.Type == "PCBboard":
            try:
                for k in range(len(j.Holes.Geometry)):
                    if j.Holes.Geometry[k].Construction:
                        continue
                    
                    x = j.Holes.Geometry[k].Center.x
                    y = j.Holes.Geometry[k].Center.y
                    r1 = j.Holes.Geometry[k].Radius
                    r2 = size / 2.
                    
                    if r1 > r2:
                        layerNew.createObject()
                        layerNew.addDrillCenter(x, y, r1, r2)
                        layerNew.setFace()
                break
            except Exception, e:
                FreeCAD.Console.PrintWarning(str(e) + "\n")
    #######
    layerNew.generuj(layerS)
    layerNew.updatePosition_Z(layerS)
    viewProviderLayerSilkObject(layerS.ViewObject)
    layerS.ViewObject.ShapeColor = color
    
    grp = createGroup_Layers()
    grp.addObject(layerS)
    #
    doc.recompute()
    return True
    


class createDrillcenter_Gui(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.form = self
        self.form.setWindowTitle(u"Create drill center")
        self.form.setWindowIcon(QtGui.QIcon(":/data/img/drill-icon.png"))
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
