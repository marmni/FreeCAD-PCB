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

import FreeCAD, FreeCADGui
import Part
if FreeCAD.GuiUp:
    from PySide import QtCore, QtGui
from pivy.coin import *
from math import pi
import unicodedata
#
from PCBconf import *
from PCBpartManaging import partsManaging
from PCBboard import getPCBheight
from PCBobjects import partObject, viewProviderPartObject
from command.PCBassignModel import modelsList
from command.PCBgroups import createGroup_Parts, makeGroup
from command.PCBannotations import createAnnotation


class addModel(QtGui.QWidget, partsManaging):
    def __init__(self, searchPhrase=None, parent=None):
        partsManaging.__init__(self)
        QtGui.QWidget.__init__(self, parent)
        
        self.setDatabase()
        freecadSettings = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB")
        #
        
        self.gruboscPlytki = getPCBheight()[1]
        self.root = None
        self.packageData = {}
        #
        self.form = self
        self.form.setWindowTitle("Add model")
        self.form.setWindowIcon(QtGui.QIcon(":/data/img/addModel.png"))
        #
        self.listaBibliotek = QtGui.QComboBox()
        
        #self.package = QtGui.QComboBox()
        #self.package.setInsertPolicy(QtGui.QComboBox.InsertAlphabetically)
        self.package = modelsList()
        self.package.checkItems = False
        self.package.sql = self.__SQL__
        self.package.reloadList()
     
        self.side = QtGui.QComboBox()
        self.side.addItems(['TOP', 'BOTTOM'])
        
        self.value = QtGui.QLineEdit('')
        
        self.label = QtGui.QLineEdit('')
        
        self.rotation = QtGui.QDoubleSpinBox()
        self.rotation.setSingleStep(1)
        self.rotation.setSuffix(' deg')
        self.rotation.setRange(-360, 360)
        
        self.val_x = QtGui.QDoubleSpinBox()
        self.val_x.setSingleStep(0.5)
        self.val_x.setRange(-1000, 1000)
        self.val_x.setSuffix(' mm')
        
        self.val_y = QtGui.QDoubleSpinBox()
        self.val_y.setSingleStep(0.5)
        self.val_y.setRange(-1000, 1000)
        self.val_y.setSuffix(' mm')
        
        self.error = QtGui.QLabel(u'')
        
        self.updateView = QtGui.QCheckBox(u'Update active view')
        
        self.loadModelColors = QtGui.QCheckBox(u'Colorize elements')
        self.loadModelColors.setChecked(freecadSettings.GetBool("partsColorize", True))
        
        self.adjustParts = QtGui.QCheckBox(u'Adjust part name/value')
        self.adjustParts.setChecked(freecadSettings.GetBool("adjustNameValue", False))
        
        self.continueCheckBox = QtGui.QCheckBox(u'Continue')
        
        self.groupParts = QtGui.QCheckBox(u'Group parts')
        self.groupParts.setChecked(freecadSettings.GetBool("groupParts", False))
        #
        lay = QtGui.QGridLayout()
        lay.addWidget(self.package, 0, 0, 14, 1)
        lay.addWidget(QtGui.QLabel(u'Library:'), 0, 1, 1, 1)
        lay.addWidget(self.listaBibliotek, 1, 1, 1, 1)
        lay.addWidget(QtGui.QLabel(u'Label:*'), 2, 1, 1, 1)
        lay.addWidget(self.label, 3, 1, 1, 1)
        lay.addWidget(QtGui.QLabel(u'Value:'), 4, 1, 1, 1)
        lay.addWidget(self.value, 5, 1, 1, 1)
        lay.addWidget(QtGui.QLabel(u'Side:'), 6, 1, 1, 1)
        lay.addWidget(self.side, 7, 1, 1, 1)
        lay.addWidget(QtGui.QLabel(u'Rotation:'), 8, 1, 1, 1)
        lay.addWidget(self.rotation, 9, 1, 1, 1)
        lay.addWidget(QtGui.QLabel(u'X:'), 10, 1, 1, 1)
        lay.addWidget(self.val_x, 11, 1, 1, 1)
        lay.addWidget(QtGui.QLabel(u'Y:'), 12, 1, 1, 1)
        lay.addWidget(self.val_y, 13, 1, 1, 1)
        
        lay_1 = QtGui.QHBoxLayout()
        lay_1.addWidget(self.loadModelColors)
        lay_1.addWidget(self.adjustParts)
        lay_1.setContentsMargins(0, 0, 0, 0)
        lay.addLayout(lay_1, 15, 0, 1, 2)
        
        #lay.addItem(QtGui.QSpacerItem(1, 5), 16, 0, 1, 2)
        
        lay_2 = QtGui.QHBoxLayout()
        lay_2.addWidget(self.groupParts)
        lay_2.addWidget(self.updateView)
        lay_2.setContentsMargins(0, 0, 0, 0)
        lay.addLayout(lay_2, 17, 0, 1, 2)
        
        lay_3 = QtGui.QHBoxLayout()
        lay_3.addWidget(self.continueCheckBox)
        lay_3.setContentsMargins(0, 0, 0, 0)
        lay.addLayout(lay_3, 18, 0, 1, 2)
        
        #lay.addItem(QtGui.QSpacerItem(1, 10), 18, 0, 1, 2)
        #lay.addWidget(self.error, 19, 0, 1, 2)
        lay.setRowStretch(14, 10)
        self.setLayout(lay)
        #
        self.connect(self.package, QtCore.SIGNAL("itemPressed (QTreeWidgetItem *,int)"), self.reloadList)
        #self.connect(self.package, QtCore.SIGNAL('currentIndexChanged (int)'), self.reloadList)
        self.connect(self.val_x, QtCore.SIGNAL('valueChanged (double)'), self.addArrow)
        self.connect(self.val_y, QtCore.SIGNAL('valueChanged (double)'), self.addArrow)
        self.connect(self.side, QtCore.SIGNAL('currentIndexChanged (int)'), self.addArrow)
        self.connect(self.updateView, QtCore.SIGNAL('stateChanged (int)'), self.changeView)
        
        self.readLibs()
        self.addArrow()
        
    def changeView(self):
        if self.updateView.isChecked():
            if self.side.itemText(self.side.currentIndex()) == "TOP":
                FreeCADGui.activeDocument().activeView().viewTop()
            else:
                FreeCADGui.activeDocument().activeView().viewBottom()
        
    def addArrow(self):
        self.changeView()
        #
        self.removeRoot()
        
        height = 15
        
        #if self.side.itemText(self.side.currentIndex()) == "TOP":
            #z = self.gruboscPlytki + height / 2.
            #rot = -pi / 2.
        #else:
            #z = 0 - height / 2.
            #rot = pi / 2.
        
        x = self.val_x.value()
        y = self.val_y.value()
        #
        self.root = SoSeparator()
        
        myTransform = SoTransform()
        myTransform.translation = (x, y, self.gruboscPlytki + height / 2.)
        
        myTransform1 = SoTransform()
        myTransform1.translation = (0, 0, 0)
        
        myRotation = SoRotationXYZ()
        myRotation.angle = -pi / 2.
        myRotation.axis = SoRotationXYZ.X
        
        redPlastic = SoMaterial()
        redPlastic.ambientColor = (1.0, 0.0, 0.0)
        redPlastic.diffuseColor = (1.0, 0.0, 0.0) 
        redPlastic.specularColor = (0.5, 0.5, 0.5)
        redPlastic.shininess = 0.1
        redPlastic.transparency = 0.7
        
        strzalka = SoCone()
        strzalka.bottomRadius = 2
        strzalka.height = height
        ####
        myTransform_2 = SoTransform()
        myTransform_2.translation = (x, y, 0 - height / 2.)
        
        myTransform1_2 = SoTransform()
        myTransform1_2.translation = (0, 0, 0)
        
        myRotation_2 = SoRotationXYZ()
        myRotation_2.angle = pi / 2.
        myRotation_2.axis = SoRotationXYZ.X
        
        redPlastic_2 = SoMaterial()
        redPlastic_2.ambientColor = (1.0, 0.0, 0.0)
        redPlastic_2.diffuseColor = (1.0, 0.0, 0.0) 
        redPlastic_2.specularColor = (0.5, 0.5, 0.5)
        redPlastic_2.shininess = 0.1
        redPlastic_2.transparency = 0.7
        
        strzalka_2 = SoCone()
        strzalka_2.bottomRadius = 2
        strzalka_2.height = height
        ####
        reset = SoResetTransform()
        ####
        self.root.addChild(myTransform)
        self.root.addChild(myRotation)
        self.root.addChild(myTransform1)
        self.root.addChild(redPlastic)
        self.root.addChild(strzalka)
        self.root.addChild(reset)
        self.root.addChild(myTransform_2)
        self.root.addChild(myRotation_2)
        self.root.addChild(myTransform1_2)
        self.root.addChild(redPlastic_2)
        self.root.addChild(strzalka_2)
        #
        FreeCADGui.ActiveDocument.ActiveView.getSceneGraph().addChild(self.root)
        
    def reloadList(self):
        try:
            self.listaBibliotek.clear()
            if str(self.package.currentItem().data(0, QtCore.Qt.UserRole + 1)) == 'C':
                return
            
            modelData = self.__SQL__.getModelByID(self.package.currentItem().data(0, QtCore.Qt.UserRole))
            if not modelData[0]:
                return
            
            modelData = self.__SQL__.convertToTable(modelData[1])
            modelData = self.__SQL__.packagesDataToDictionary(modelData)
            for i in modelData['software']:
                self.listaBibliotek.addItem(u"{0} ({1})".format(i['software'], i['name']))
                self.listaBibliotek.setItemData(self.listaBibliotek.count() - 1, i['name'], QtCore.Qt.UserRole)  # model name
                self.listaBibliotek.setItemData(self.listaBibliotek.count() - 1, str(i['software']).lower(), QtCore.Qt.UserRole + 1)  # soft name
            self.listaBibliotek.setCurrentIndex(0)
        except:
            pass
            #FreeCAD.Console.PrintWarning(u"Error 3: {0} \n".format(e))
    
    def readLibs(self):
        ''' read all available libs from conf file '''
        self.package.reloadList()
        self.reloadList()
        
    def accept(self):
        if u"{0}".format(self.label.text()).strip() == "":
            self.error.setText("<span style='color:red;font-weight:bold;'>Mandatory field is empty!</span>")
            FreeCAD.Console.PrintWarning("Mandatory field is empty!\n")
            return False
        #
        name = self.label.text()
        package = self.listaBibliotek.itemData(self.listaBibliotek.currentIndex(), QtCore.Qt.UserRole)
        value = self.value.text()
        x = self.val_x.value()
        y = self.val_y.value()
        rot = self.rotation.value()
        side = str(self.side.itemText(self.side.currentIndex()))
        library = self.listaBibliotek.itemData(self.listaBibliotek.currentIndex(), QtCore.Qt.UserRole)
        
        EL_Name = ['', x, y + 1.27, 1.27, rot, side, "bottom-left", False, 'None', '', True]
        EL_Value = ['', x, y - 1.27, 1.27, rot, side, "bottom-left", False, 'None', '', True]
        
        koloroweElemnty = self.loadModelColors.isChecked()
        adjustParts = self.adjustParts.isChecked()
        groupParts = self.groupParts.isChecked()
        self.databaseType = self.listaBibliotek.itemData(self.listaBibliotek.currentIndex(), QtCore.Qt.UserRole + 1)
        
        newPart = [[name, package, value, x, y, rot, side, library], EL_Name, EL_Value]
        self.addPart(newPart, koloroweElemnty, adjustParts, groupParts)
        #
        if self.continueCheckBox.isChecked():
            self.label.setText('')
        else:
            self.removeRoot()
            return True
            
    def removeRoot(self):
        if self.root:
            FreeCADGui.ActiveDocument.ActiveView.getSceneGraph().removeChild(self.root)
        
    def reject(self):
        self.removeRoot()
        return True
