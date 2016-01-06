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
from functools import partial
import FreeCAD
from collections import OrderedDict
#
from PCBconf import PCBlayers, PCBconstraintAreas

#***********************************************************************
#*                             CONSOLE
#***********************************************************************
def listTXT():
    PCBlayers["Parts"] = [2, [0, 0, 0], None, ['PCBpart'], "Parts"]
    PCBlayers["Parts Name"] = [2, [0, 0, 0], None, ['PCBannotation', 'anno_name'], "Parts Name"]
    PCBlayers["Parts Value"] = [2, [0, 0, 0], None, ['PCBannotation', 'anno_value'], "Parts Value"]
    
    for i, j in PCBconstraintAreas.items():
        PCBlayers[j[0]] = [2, [0, 0, 0], None, j[1], j[4]]
    
    FreeCAD.Console.PrintWarning(u"****************\n")
    FreeCAD.Console.PrintWarning(u"Available layers:\n")
    for i, j in OrderedDict(sorted(PCBlayers.items(), key=lambda t: t[0])).items():
        FreeCAD.Console.PrintWarning(u"Layer name:{0} ; Layer ID: {1}\n".format(i, ', '.join(j[3])))
    FreeCAD.Console.PrintWarning(u"****************\n")
    
    return ''

def list():
    data = {}
    
    PCBlayers["Parts"] = [2, [0, 0, 0], None, ['PCBpart'], "Parts"]
    PCBlayers["Parts Name"] = [2, [0, 0, 0], None, ['PCBannotation', 'anno_name'], "Parts Name"]
    PCBlayers["Parts Value"] = [2, [0, 0, 0], None, ['PCBannotation', 'anno_value'], "Parts Value"]
    
    for i, j in PCBconstraintAreas.items():
        PCBlayers[j[0]] = [2, [0, 0, 0], None, j[1], j[4]]
    for i, j in OrderedDict(sorted(PCBlayers.items(), key=lambda t: t[0])).items():
        data[i] = {'id': j[3], 'info': j[4]}
    
    return data

def toggle(TypeId):
    for i in FreeCAD.activeDocument().Objects:
        if hasattr(i, "Proxy") and hasattr(i.Proxy, "Type"):
            if 'PCBannotation' in i.Proxy.Type and i.Proxy.mode != 'anno':
                if len(TypeId) > 1 and i.Proxy.Type == TypeId[:1] and i.Proxy.mode == TypeId[1]:
                    if i.ViewObject.Visibility:
                        i.ViewObject.Visibility = False
                    else:
                        i.ViewObject.Visibility = True
            elif i.Proxy.Type == TypeId:
                if i.ViewObject.Visibility:
                    i.ViewObject.Visibility = False
                else:
                    i.ViewObject.Visibility = True

def state(TypeId):
    for i in FreeCAD.activeDocument().Objects:
        if hasattr(i, "Proxy") and hasattr(i.Proxy, "Type"):
            if 'PCBannotation' in i.Proxy.Type and i.Proxy.mode != 'anno':
                if len(TypeId) > 1 and i.Proxy.Type == TypeId[:1] and i.Proxy.mode == TypeId[1]:
                    return i.ViewObject.Visibility
            elif i.Proxy.Type == TypeId:
                return i.ViewObject.Visibility
    
def display(TypeId):
    for i in FreeCAD.activeDocument().Objects:
        if hasattr(i, "Proxy") and hasattr(i.Proxy, "Type"):
            if 'PCBannotation' in i.Proxy.Type and i.Proxy.mode != 'anno':
                if len(TypeId) > 1 and i.Proxy.Type == TypeId[:1] and i.Proxy.mode == TypeId[1]:
                    i.ViewObject.Visibility = True
            elif i.Proxy.Type == TypeId:
                i.ViewObject.Visibility = True

def blank(TypeId):
    for i in FreeCAD.activeDocument().Objects:
        if hasattr(i, "Proxy") and hasattr(i.Proxy, "Type"):
            if 'PCBannotation' in i.Proxy.Type and i.Proxy.mode != 'anno':
                if len(TypeId) > 1 and i.Proxy.Type == TypeId[:1] and i.Proxy.mode == TypeId[1]:
                    i.ViewObject.Visibility = False
            elif i.Proxy.Type == TypeId:
                i.ViewObject.Visibility = False


#***********************************************************************
#*                               GUI
#***********************************************************************
class przycisk(QtGui.QPushButton):
    def __init__(self, parent=None):
        QtGui.QPushButton.__init__(self, parent)

        self.setFlat(True)
        self.setStyleSheet('''
                QPushButton
                {
                    border: 0px;
                    margin-top: 2px;
                    width: 15px;
                    height: 15px;
                }
            ''')
        #self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))


class layersSettings(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.form = self
        self.form.setWindowTitle(u"Layers settings")
        self.form.setWindowIcon(QtGui.QIcon(":/data/img/layers.png"))
        #
        nr = 0
        
        lay = QtGui.QGridLayout()
        PCBlayers["Parts"] = [2, [0, 0, 0], None, 'PCBpart', "Parts"]
        PCBlayers["Parts Name"] = [2, [0, 0, 0], None, ['PCBannotation', 'anno_name'], "Parts Name"]
        PCBlayers["Parts Value"] = [2, [0, 0, 0], None, ['PCBannotation', 'anno_value'], "Parts Value"]
        
        #
        for i, j in PCBconstraintAreas.items():
            PCBlayers[j[0]] = [2, [0, 0, 0], None, j[1], j[4]]
        for i, j in OrderedDict(sorted(PCBlayers.items(), key=lambda t: t[0])).items():
            infoPrz = przycisk()
            infoPrz.setToolTip(u"Info")
            infoPrz.setIcon(QtGui.QIcon(":/data/img/info_16x16.png"))
            par = partial(self.showInfo, j[4])
            self.connect(infoPrz, QtCore.SIGNAL("clicked ()"), par)
            
            showAll = przycisk()
            showAll.setToolTip(u"Show All")
            showAll.setIcon(QtGui.QIcon(":/data/img/show.png"))
            par = partial(self.showAll, j[3])
            self.connect(showAll, QtCore.SIGNAL("clicked ()"), par)
                
            hideAll = przycisk()
            hideAll.setToolTip(u"Hide All")
            hideAll.setIcon(QtGui.QIcon(":/data/img/hide.png"))
            par = partial(self.hideAll, j[3])
            self.connect(hideAll, QtCore.SIGNAL("clicked ()"), par)
            #
            lay.addWidget(QtGui.QLabel(i), nr, 0, 1, 1)
            lay.addWidget(showAll, nr, 1, 1, 1)
            lay.addWidget(hideAll, nr, 2, 1, 1)
            lay.addWidget(infoPrz, nr, 3, 1, 1)
            #
            nr += 1
        #
        lay.setColumnStretch(0, 10)
        self.setLayout(lay)
    
    def showInfo(self, info):
        dial = QtGui.QMessageBox(self)
        dial.setText(info)
        dial.setWindowTitle("Info")
        dial.setIcon(QtGui.QMessageBox.Information)
        dial.addButton('Ok', QtGui.QMessageBox.RejectRole)
        dial.exec_()
        
    def showAll(self, objType):
        display(objType)
        
    def hideAll(self, objType):
        blank(objType)
