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
import FreeCAD, FreeCADGui
import Part
import tempfile
import os
from functools import partial
from pivy.coin import *
if FreeCAD.GuiUp:
    from PySide import QtCore, QtGui
    
from PCBboard import getPCBheight

#***********************************************************************
#*                            
#***********************************************************************
class collisionObjectTable(QtGui.QListWidget):
    def __init__(self, parent=None):
        QtGui.QListWidget.__init__(self, parent)
        
        self.setFrameShape(QtGui.QFrame.NoFrame)


#***********************************************************************
#*                             GUI
#***********************************************************************
class checkCollisionsBaseClass(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        #
        self.form = self
        self.root = None
        self.obj = None
        self.tmpFile = None
        self.transaprency = {}
        #
        self.createSolid = QtGui.QCheckBox(u'Create solid on exit')
        #
        self.infoLabel = QtGui.QLabel("")
        #
        self.table1 = collisionObjectTable()
        self.table2 = collisionObjectTable()
        
        QtCore.QObject.connect(self.table1, QtCore.SIGNAL("itemChanged (QListWidgetItem*)"), partial(self.blankInSecondTable, self.table2))
        QtCore.QObject.connect(self.table2, QtCore.SIGNAL("itemChanged (QListWidgetItem*)"), partial(self.blankInSecondTable, self.table1))
        #
        checkButton = QtGui.QPushButton(u"Check")
        self.connect(checkButton, QtCore.SIGNAL("released ()"), self.preview)
        #
        lay = QtGui.QGridLayout(self)
        lay.addWidget(checkButton, 0, 0, 1, 2)
        lay.addWidget(self.infoLabel, 1, 0, 1, 2)
        lay.addWidget(QtGui.QLabel(u'First group'), 2, 0, 1, 1)
        lay.addWidget(self.table1, 3, 0, 1, 1)
        lay.addWidget(QtGui.QLabel(u'Second group'), 2, 1, 1, 1)
        lay.addWidget(self.table2, 3, 1, 1, 1)
        lay.addWidget(self.createSolid, 4, 0, 1, 2)
        #
        self.readObjects()
        self.removeRoot()
    
    def blankInSecondTable(self, tableOUT, itemIN):
        for i in range(tableOUT.count()):
            if str(tableOUT.item(i).data(QtCore.Qt.UserRole)) == str(itemIN.data(QtCore.Qt.UserRole)):
                tableOUT.item(i).setCheckState(QtCore.Qt.CheckState.Unchecked)
                if itemIN.checkState() == 2:
                    tableOUT.item(i).setHidden(True)
                else:
                    tableOUT.item(i).setHidden(False)

    def accept(self):
        if self.createSolid.isChecked():
            self.createSolidObject()
        
        self.onExit()
        self.removeRoot()
        return True
    
    def reject(self):
        self.onExit()
        self.removeRoot()
        return True
    
    def onExit(self):
        try:
            os.remove(self.tmpFile[1])
        except Exception as e:
            #FreeCAD.Console.PrintWarning("{0} \n".format(e))
            pass
        
        for i, j in self.transaprency.items():
            try:
                i.ViewObject.Transparency = j
            except:
                pass
                
        self.obj = None
        self.tmpFile = None
    
    def removeRoot(self):
        if self.root:
            FreeCADGui.ActiveDocument.ActiveView.getSceneGraph().removeChild(self.root)
            self.root = None
            
    def infoLabelsetText(self, info, infoType):
        self.infoLabel.setText(info)
        
        if infoType == 0: # error
            self.infoLabel.setStyleSheet("QLabel {color : #F00; font-weight: bold;}");
        else: # info OK
            self.infoLabel.setStyleSheet("QLabel {color : #2d8600; font-weight: bold;}");
    
    def getObjectsFromList(self, listObj):
        obiekty_1 = []
        for i in range(listObj.count()):
            if listObj.item(i).checkState() == 2:
                try:
                    objName = str(listObj.item(i).data(QtCore.Qt.UserRole))
                    
                    obj = FreeCAD.ActiveDocument.getObject(objName)
                    if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type") and obj.Proxy.Type in ['assemblyMain']:
                        obiekty_1 = obiekty_1 + obj.OutList
                    else:
                        obiekty_1.append(obj)
                except:
                    pass
        return obiekty_1
        
    def preview(self):
        self.removeRoot()
        #
        obiekty_1 = self.getObjectsFromList(self.table1)
        
        if len(obiekty_1) == 0:
            self.infoLabelsetText("No object selected in first group", 0)
            FreeCAD.Console.PrintWarning("No object selected in first group\n")
            return False
        #
        obiekty_2 = self.getObjectsFromList(self.table2)
       
        if len(obiekty_2) == 0:
            self.infoLabelsetText("No object selected in second group", 0)
            FreeCAD.Console.PrintWarning("No object selected in second group\n")
            return False
        #
        obiekty_1 = [i.Shape for i in obiekty_1 if hasattr(i, "Shape")]
        obiekty_2 = [i.Shape for i in obiekty_2 if hasattr(i, "Shape")]
        
        try:
            obj1 = Part.makeCompound(obiekty_1)
            obj2 = Part.makeCompound(obiekty_2)
            self.obj = obj1.common(obj2)
            
            if len(self.obj.Solids) > 0:
                finalObject = self.createSolidObject()
                self.tmpFile = tempfile.mkstemp("freecad-pcb")
                f=open(self.tmpFile[1],"w")
                f.write(finalObject.ViewObject.toString())
                f.close()
                FreeCAD.ActiveDocument.removeObject(finalObject.Name)
                #
                myInput = SoInput()
                myInput.openFile(self.tmpFile[1])
                fileContents = SoDB.readAll(myInput)
                
                self.root = SoSeparator()
                self.root.addChild(fileContents)
                FreeCADGui.ActiveDocument.ActiveView.getSceneGraph().addChild(self.root)
                self.infoLabelsetText("Collision detected", 0)
            else:
                self.infoLabelsetText("No collision detected", 1)
                FreeCAD.Console.PrintWarning("No collision detected.\n")
                return True
        except Exception as e:
            self.infoLabelsetText("No collision detected", 1)
            FreeCAD.Console.PrintWarning("No collision detected.\n")
            return True
    
    def createSolidObject(self):
        finalObject = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Collision")
        finalObject.Shape = self.obj
        finalObject.ViewObject.Proxy = 0
        finalObject.ViewObject.ShapeColor = (1.00,0.00,0.00)
        finalObject.ViewObject.DisplayMode = "Shaded"
        
        return finalObject


class checkCollisionsGuiALL(checkCollisionsBaseClass):
    def __init__(self, parent=None):
        checkCollisionsBaseClass.__init__(self, parent)
        #
        self.setWindowTitle(u'Detect collisions between objects')
        self.form.setWindowIcon(QtGui.QIcon(":/data/img/collisions.svg"))
    
    def readObjects(self):
        for i in FreeCAD.ActiveDocument.Objects:
            if hasattr(i.ViewObject, "Transparency"):
                self.transaprency[i] = i.ViewObject.Transparency
                i.ViewObject.Transparency = 80
            
            #if (hasattr(i, "Shape") and i.Shape.Solids != [] and (i.InList == [] or i.InList[0].TypeId in ['App::Part', 'App.DocumentObject', 'App::DocumentObjectGroup'])) or hasattr(i, "Proxy") and hasattr(i.Proxy, "Type") and i.Proxy.Type in ["assemblyMain"]:
            if hasattr(i, "Shape") and i.Shape.Solids != [] and not i.TypeId in ['App::Part', 'App.DocumentObject', 'App::DocumentObjectGroup']:
                if hasattr(i, "Proxy") and hasattr(i.Proxy, "Type") and 'layer' in i.Proxy.Type:
                    continue
                #
                a = QtGui.QListWidgetItem(i.Label)
                a.setData(QtCore.Qt.UserRole, i.Name)
                a.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
                try:
                    a.setIcon(i.ViewObject.Icon)
                except AttributeError:
                    pass
                a.setCheckState(QtCore.Qt.Unchecked)
                
                self.table1.addItem(a)
                ###########
                a = QtGui.QListWidgetItem(i.Label)
                a.setData(QtCore.Qt.UserRole, i.Name)
                a.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
                try:
                    a.setIcon(i.ViewObject.Icon)
                except AttributeError:
                    pass
                a.setCheckState(QtCore.Qt.Unchecked)
                
                self.table2.addItem(a)


class checkCollisionsGuiPCB(checkCollisionsBaseClass):
    def __init__(self, parent=None):
        checkCollisionsBaseClass.__init__(self, parent)
        #
        self.setWindowTitle(u'Detect collisions with PCB')
        self.form.setWindowIcon(QtGui.QIcon(":/data/img/collisions.svg"))
        #
        self.table1.setEnabled(False)
        
    def readObjects(self):
        pcb = getPCBheight()
    
        if FreeCAD.activeDocument() and pcb[0]:
            # a = QtGui.QListWidgetItem(pcb[2].Parent.Label)
            # a.setData(QtCore.Qt.UserRole, pcb[2].Parent.Name)
            # a.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
            # a.setIcon(pcb[2].Parent.ViewObject.Icon)
            # a.setCheckState(QtCore.Qt.Checked)
            # self.table1.addItem(a)
            #
            for i in FreeCAD.ActiveDocument.Objects:
                if hasattr(i.ViewObject, "Transparency"):
                    self.transaprency[i] = i.ViewObject.Transparency
                    i.ViewObject.Transparency = 80
                #
                if hasattr(i, "Shape") and i.Shape.Solids != [] and not i.TypeId in ['App::Part', 'App.DocumentObject', 'App::DocumentObjectGroup']:
                    if hasattr(i, "Proxy") and hasattr(i.Proxy, "Type") and 'layer' in i.Proxy.Type:
                        continue
                  #
                    if not i == pcb[2].Parent and not pcb[2].Parent in i.InList:
                        a = QtGui.QListWidgetItem(i.Label)
                        a.setData(QtCore.Qt.UserRole, i.Name)
                        a.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
                        try:
                            a.setIcon(i.ViewObject.Icon)
                        except AttributeError:
                            pass
                        a.setCheckState(QtCore.Qt.Unchecked)
                    
                        self.table2.addItem(a)
                    else:
                        a = QtGui.QListWidgetItem(i.Label)
                        a.setData(QtCore.Qt.UserRole, i.Name)
                        a.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
                        a.setIcon(i.ViewObject.Icon)
                        a.setCheckState(QtCore.Qt.Checked)
                        
                        self.table1.addItem(a)
        else:
            FreeCAD.Console.PrintWarning("File does not exist or is empty\n")
