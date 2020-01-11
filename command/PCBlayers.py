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
from functools import partial
import FreeCAD
from collections import OrderedDict
#
from PCBconf import PCBconstraintAreas
from PCBboard import getPCBheight

#***********************************************************************
#*                               GUI
#***********************************************************************
class przycisk(QtGui.QPushButton):
    def __init__(self, parent=None):
        QtGui.QPushButton.__init__(self, parent)

        self.setFlat(True)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setStyleSheet('''
                QPushButton
                {
                    border: 0px;
                    margin-top: 1px;
                    width: 20px;
                    height: 20px;
                    padding:1px;
                }
                QPushButton:hover:!pressed
                {
                    border: 1px solid #808080; 
                    background-color: #e6e6e6;
                }
            ''')


class layersSettings(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.form = self
        self.form.setWindowTitle(u"Layers settings")
        self.form.setWindowIcon(QtGui.QIcon(":/data/img/layers_TI.svg"))
        #
        self.layerslist = {}
        #
        self.mainLay = QtGui.QGridLayout()
        pcb = getPCBheight()
        try:
            if FreeCAD.activeDocument() and pcb[0]:
                for i in pcb[2].Group:
                    if hasattr(i, "Proxy") and hasattr(i.Proxy, "Type"):
                        if isinstance(i.Proxy.Type, str):
                            if i.Proxy.Type in ["PCBpart", "PCBpart_E"]:
                                if i.Proxy.Type == "PCBpart":
                                    if not "Parts" in self.layerslist.keys():
                                        self.layerslist["Parts"] = []
                                    
                                    self.layerslist["Parts"].append(i)
                                #
                                if not "Parts Name" in self.layerslist.keys():
                                    self.layerslist["Parts Name"] = []
                                
                                if i.PartName:
                                    self.layerslist["Parts Name"].append(i.PartName)
                                #
                                if not "Parts Value" in self.layerslist.keys():
                                    self.layerslist["Parts Value"] = []
                                
                                if i.PartValue:
                                    self.layerslist["Parts Value"].append(i.PartValue)
                            elif i.Proxy.Type == "ShapeString" and i.Proxy.mode == "anno":
                                if not "Annotations" in self.layerslist.keys():
                                    self.layerslist["Annotations"] = []
                                
                                self.layerslist["Annotations"].append(i)
                        elif isinstance(i.Proxy.Type, list):
                            if "layer" in i.Proxy.Type:
                                if not "All layers" in self.layerslist.keys():
                                    self.layerslist["All layers"] = []
                                
                                self.layerslist["All layers"].append(i)
                                #
                                if not i.Proxy.Type[-1] in self.layerslist.keys():
                                    self.layerslist[i.Label] = []
                                
                                self.layerslist[i.Label].append(i)
                ####
                nr = 0
                for i in self.layerslist.keys():
                    self.addRow(i, nr)
                    nr += 1
        except Exception as e:
            print(e)
        
        self.mainLay.setColumnStretch(0, 10)
        self.setLayout(self.mainLay)
    
    def addRow(self, value, nr):
        showAll = przycisk()
        showAll.setToolTip(u"Show All")
        showAll.setIcon(QtGui.QIcon(":/data/img/visible.svg"))
        par = partial(self.showAll, value)
        self.connect(showAll, QtCore.SIGNAL("clicked ()"), par)
        #
        hideAll = przycisk()
        hideAll.setToolTip(u"Hide All")
        hideAll.setIcon(QtGui.QIcon(":/data/img/invisible.svg"))
        par = partial(self.hideAll, value)
        self.connect(hideAll, QtCore.SIGNAL("clicked ()"), par)
        #
        self.mainLay.addWidget(QtGui.QLabel(value), nr, 0, 1, 1)
        self.mainLay.addWidget(showAll, nr, 1, 1, 1)
        self.mainLay.addWidget(hideAll, nr, 2, 1, 1)
    
    def showAll(self, objType):
        if objType in self.layerslist.keys():
            for i in self.layerslist[objType]:
                i.ViewObject.Visibility = True

    def hideAll(self, objType):
        if objType in self.layerslist.keys():
            for i in self.layerslist[objType]:
                i.ViewObject.Visibility = False
