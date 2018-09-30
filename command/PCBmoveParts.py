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
#
from PCBconf import *
from PCBpartManaging import partsManaging
from PCBboard import getPCBheight

if FreeCAD.GuiUp:
    from PySide import QtCore, QtGui


class moveWizardWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        #
        self.listaBibliotek = QtGui.QComboBox()
        self.listaBibliotekInfo = QtGui.QLabel(' ')
        #
        self.positionX = QtGui.QDoubleSpinBox()
        self.positionX.setSingleStep(0.1)
        self.positionX.setRange(-1000, 1000)
        self.positionX.setSuffix(' mm')
        self.positionY = QtGui.QDoubleSpinBox()
        self.positionY.setSingleStep(0.1)
        self.positionY.setRange(-1000, 1000)
        self.positionY.setSuffix(' mm')
        self.positionZ = QtGui.QDoubleSpinBox()
        self.positionZ.setSingleStep(0.1)
        self.positionZ.setRange(-1000, 1000)
        self.positionZ.setSuffix(' mm')
        self.rotationRX = QtGui.QDoubleSpinBox()
        self.rotationRX.setSingleStep(0.1)
        self.rotationRX.setRange(-360, 360)
        self.rotationRX.setSuffix(' deg')
        self.rotationRY = QtGui.QDoubleSpinBox()
        self.rotationRY.setSingleStep(0.1)
        self.rotationRY.setRange(-360, 360)
        self.rotationRY.setSuffix(' deg')
        self.rotationRZ = QtGui.QDoubleSpinBox()
        self.rotationRZ.setSingleStep(0.1)
        self.rotationRZ.setRange(-360, 360)
        self.rotationRZ.setSuffix(' deg')
        #
        translationFrame = QtGui.QGroupBox(u'Translation:')
        translationFrameLay = QtGui.QFormLayout(translationFrame)
        translationFrameLay.addRow(QtGui.QLabel('X:'), self.positionX)
        translationFrameLay.addRow(QtGui.QLabel('Y:'), self.positionY)
        translationFrameLay.addRow(QtGui.QLabel('Z:'), self.positionZ)
        translationFrameLay.setContentsMargins(5, 5, 5, 5)
        #
        rotationFrame = QtGui.QGroupBox(u'Rotation:')
        rotationFrameLay = QtGui.QFormLayout(rotationFrame)
        rotationFrameLay.addRow(QtGui.QLabel('RX:'), self.rotationRX)
        rotationFrameLay.addRow(QtGui.QLabel('RY:'), self.rotationRY)
        rotationFrameLay.addRow(QtGui.QLabel('RZ:'), self.rotationRZ)
        rotationFrameLay.setContentsMargins(5, 5, 5, 5)
        #
        libraryFrame = QtGui.QGroupBox(u'Library:')
        libraryFrameLay = QtGui.QVBoxLayout(libraryFrame)
        libraryFrameLay.addWidget(self.listaBibliotek)
        libraryFrameLay.addWidget(self.listaBibliotekInfo)
        #
        self.resetButton = QtGui.QPushButton(u'Reset')
        self.resetButton.setMaximumWidth(60)
        #
        lay = QtGui.QGridLayout()
        lay.addWidget(libraryFrame, 0, 0, 1, 2)
        lay.addWidget(translationFrame, 1, 0, 1, 1)
        lay.addWidget(rotationFrame, 1, 1, 1, 1)
        lay.addItem(QtGui.QSpacerItem(1, 10), 2, 0, 1, 2)
        lay.addWidget(self.resetButton, 3, 1, 1, 1, QtCore.Qt.AlignRight)
        lay.setRowStretch(4, 5)
        self.setLayout(lay)



class moveParts(partsManaging):
    ''' move 3d models of packages '''
    def __init__(self, updateModel, parent=None):
        self.form = moveWizardWidget()
        self.form.setWindowTitle('Placement model')
        self.updateModel = updateModel
        
        self.setDatabase()
        
        self.elemPackage = []
        doc = FreeCAD.activeDocument()
        for i in doc.Objects:
            if hasattr(i, "Proxy") and hasattr(i, "Type") and i.Proxy.Type == "PCBpart" and not i.KeepPosition and i.Package == updateModel:
                self.elemPackage.append([i, i.Placement, i.Proxy.offsetX, i.Proxy.offsetY])
    
    def loadData(self):
        ''' load all packages types to list '''
        packageID = self.form.listaBibliotek.itemData(self.form.listaBibliotek.currentIndex(), QtCore.Qt.UserRole)
        packageData = self.__SQL__.getPackageByID(packageID)
        packageData = self.__SQL__.convertToTable(packageData)
        #
        self.form.positionX.setValue(float(packageData['x']))
        self.form.positionY.setValue(float(packageData['y']))
        self.form.positionZ.setValue(float(packageData['z']))
        self.form.rotationRX.setValue(float(packageData['rx']))
        self.form.rotationRY.setValue(float(packageData['ry']))
        self.form.rotationRZ.setValue(float(packageData['rz']))
        
        self.offsetX = float(packageData['x'])
        self.offsetY = float(packageData['y'])
        
    def readLibs(self):
        ''' read all available libs from selected model '''
        modelData = self.__SQL__.findPackage(self.updateModel, software='*', returnAll=True)
        #
        self.form.listaBibliotek.clear()
        for i in modelData:
            data = self.__SQL__.convertToTable(i)
            self.form.listaBibliotek.addItem(u"{1} ({0})".format(data['name'], data['software']))
            self.form.listaBibliotek.setItemData(self.form.listaBibliotek.count() - 1, data['id'], QtCore.Qt.UserRole)
        #
        self.form.listaBibliotek.setCurrentIndex(0)

    def open(self):
        self.form.connect(self.form.positionX, QtCore.SIGNAL('valueChanged (double)'), self.changePos)
        self.form.connect(self.form.positionY, QtCore.SIGNAL('valueChanged (double)'), self.changePos)
        self.form.connect(self.form.positionZ, QtCore.SIGNAL('valueChanged (double)'), self.changePos)
        self.form.connect(self.form.rotationRX, QtCore.SIGNAL('valueChanged (double)'), self.changePos)
        self.form.connect(self.form.rotationRY, QtCore.SIGNAL('valueChanged (double)'), self.changePos)
        self.form.connect(self.form.rotationRZ, QtCore.SIGNAL('valueChanged (double)'), self.changePos)
        self.form.connect(self.form.resetButton, QtCore.SIGNAL('pressed ()'), self.loadData)
        #
        self.readLibs()
        self.loadData()
        self.changePos(1)
        #
        self.form.connect(self.form.listaBibliotek, QtCore.SIGNAL('currentIndexChanged (int)'), self.loadData)
        
    def changePos(self, val):
        #################################################################
        #        polaczyc z innymi podobnymi czesciami kodu !!!!!       #
        #################################################################
        gruboscPlytki = getPCBheight()[1]
        
        for i in self.elemPackage:
            # rotate object according to (RX, RY, RZ) set by user
            sX = i[0].Shape.BoundBox.Center.x * (-1) + i[0].Placement.Base.x
            sY = i[0].Shape.BoundBox.Center.y * (-1) + i[0].Placement.Base.y
            sZ = i[0].Shape.BoundBox.Center.z * (-1) + i[0].Placement.Base.z + gruboscPlytki / 2.
            
            rotateY = self.form.rotationRY.value()
            rotateX = self.form.rotationRX.value()
            rotateZ = self.form.rotationRZ.value()
            pla = FreeCAD.Placement(i[0].Placement.Base, FreeCAD.Rotation(rotateX, rotateY, rotateZ), FreeCAD.Base.Vector(sX, sY, sZ))
            i[0].Placement = pla
            
            ## placement object to 0, 0, PCB_size / 2. (X, Y, Z)
            sX = i[0].Shape.BoundBox.Center.x * (-1) + i[0].Placement.Base.x
            sY = i[0].Shape.BoundBox.Center.y * (-1) + i[0].Placement.Base.y
            sZ = i[0].Shape.BoundBox.Center.z * (-1) + i[0].Placement.Base.z + gruboscPlytki / 2.

            i[0].Placement.Base.x = sX + self.form.positionX.value() - i[0].Proxy.offsetX
            i[0].Placement.Base.y = sY + self.form.positionY.value() - i[0].Proxy.offsetY
            i[0].Placement.Base.z = sZ
            
            # move object to correct Z
            i[0].Placement.Base.z = i[0].Placement.Base.z + (gruboscPlytki - i[0].Shape.BoundBox.Center.z) + self.form.positionZ.value() 
            
            #
            if i[0].Side == "BOTTOM":
                # ROT Y - MIRROR
                shape = i[0].Shape.copy()
                shape.Placement = i[0].Placement
                shape.rotate((0, 0, gruboscPlytki / 2.), (0.0, 1.0, 0.0), 180)
                i[0].Placement = shape.Placement
                
                # ROT Z - VALUE FROM EAGLE
                shape = i[0].Shape.copy()
                shape.Placement = i[0].Placement
                shape.rotate((0, 0, 0), (0.0, 0.0, 1.0), -i[0].Rot)
                i[0].Placement = shape.Placement
            else:
                # ROT Z - VALUE FROM EAGLE
                shape = i[0].Shape.copy()
                shape.Placement = i[0].Placement
                shape.rotate((0, 0, 0), (0.0, 0.0, 1.0), i[0].Rot)
                i[0].Placement = shape.Placement
            
            # placement object to X, Y set in eagle
            i[0].Placement.Base.x = i[0].Placement.Base.x + i[0].X.Value
            i[0].Placement.Base.y = i[0].Placement.Base.y + i[0].Y.Value
            
        FreeCAD.ActiveDocument.recompute()
            
    def resetObj(self):
        for i in self.elemPackage:
            i[0].Placement = i[1]
            i[0].Proxy.offsetX = i[2] 
            i[0].Proxy.offsetY = i[3]
        
    def reject(self):
        self.resetObj()
        return True
    
    def needsFullSpace(self):
        return True

    def isAllowedAlterSelection(self):
        return False

    def isAllowedAlterView(self):
        return True

    def isAllowedAlterDocument(self):
        return False

    def helpRequested(self):
        pass

    def accept(self):
        ''' update 3d models of packages '''
        packageID = self.form.listaBibliotek.itemData(self.form.listaBibliotek.currentIndex(), QtCore.Qt.UserRole)
        packageData = self.__SQL__.getPackageByID(packageID)
        packageData = self.__SQL__.convertToTable(packageData)
        
        packageData['x'] = self.form.positionX.value()
        packageData['y'] = self.form.positionY.value()
        packageData['z'] = self.form.positionZ.value()
        packageData['rx'] = self.form.rotationRX.value()
        packageData['ry'] = self.form.rotationRY.value()
        packageData['rz'] = self.form.rotationRZ.value()
        
        self.__SQL__.updatePackage(packageID, packageData)
        FreeCAD.ActiveDocument.recompute()
        return True
