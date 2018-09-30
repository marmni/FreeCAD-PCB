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
import tempfile
import os
from pivy.coin import *
if FreeCAD.GuiUp:
    from PySide import QtCore, QtGui


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
class checkCollisionsGui(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        #
        self.form = self
        self.form.setWindowTitle(u'Check collisions')
        self.form.setWindowIcon(QtGui.QIcon(":/data/img/collisions.png"))
        
        self.root = None
        self.obj = None
        self.tmpFile = None
        self.transaprency = {}
        #
        self.createSolid = QtGui.QCheckBox(u'Create solid on exit')
        #
        self.table1 = collisionObjectTable()
        #
        self.table2 = collisionObjectTable()
        #
        checkButton = QtGui.QPushButton(u"Check")
        self.connect(checkButton, QtCore.SIGNAL("released ()"), self.preview)
        #
        lay = QtGui.QGridLayout(self)
        lay.addWidget(checkButton, 0, 0, 1, 2)
        lay.addWidget(QtGui.QLabel(u'First group'), 1, 0, 1, 1)
        lay.addWidget(self.table1, 2, 0, 1, 1)
        lay.addWidget(QtGui.QLabel(u'Second group'), 1, 1, 1, 1)
        lay.addWidget(self.table2, 2, 1, 1, 1)
        lay.addWidget(self.createSolid, 3, 0, 1, 2)
        #
        self.readObjects()
        self.removeRoot()
    
    def preview(self):
        self.removeRoot()
        
        obiekty_1 = []
        for i in range(self.table1.count()):
            if self.table1.item(i).checkState() == 2:
                try:
                    objName = str(self.table1.item(i).data(QtCore.Qt.UserRole))
                    
                    obj = FreeCAD.ActiveDocument.getObject(objName)
                    if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type") and obj.Proxy.Type in ['assemblyMain']:
                        obiekty_1 = obiekty_1 + obj.OutList
                    else:
                        obiekty_1.append(obj)
                except:
                    pass

        if len(obiekty_1) == 0:
            FreeCAD.Console.PrintWarning("No object selected in first group\n")
            return False
        #
        obiekty_2 = []
        for i in range(self.table2.count()):
            if self.table2.item(i).checkState() == 2:
                try:
                    objName = str(self.table2.item(i).data(QtCore.Qt.UserRole))
                    
                    obj = FreeCAD.ActiveDocument.getObject(objName)
                    if hasattr(obj, "Proxy") and hasattr(obj.Proxy, "Type") and obj.Proxy.Type in ['assemblyMain']:
                        obiekty_2 = obiekty_2 + obj.OutList
                    else:
                        obiekty_2.append(obj)
                except:
                    pass
        
        if len(obiekty_2) == 0:
            FreeCAD.Console.PrintWarning("No object selected in second group\n")
            return False
        #
        obiekty_1 = [i.Shape for i in obiekty_1 if hasattr(i, "Shape")]
        obiekty_2 = [i.Shape for i in obiekty_2 if hasattr(i, "Shape")]
        
        obj1 = Part.makeCompound(obiekty_1)
        obj2 = Part.makeCompound(obiekty_2)
        self.obj = obj1.common(obj2)

        try:
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
            
        except Exception as e:
            FreeCAD.Console.PrintWarning("No collision detected.\n")
            return True
    
    def createSolidObject(self):
        finalObject = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "Collision")
        finalObject.Shape = self.obj
        finalObject.ViewObject.Proxy = 0
        finalObject.ViewObject.ShapeColor = (1.00,0.00,0.00)
        finalObject.ViewObject.DisplayMode = "Shaded"
        
        return finalObject
        
    def readObjects(self):
        for i in FreeCAD.ActiveDocument.Objects:
            if hasattr(i.ViewObject, "Transparency"):
                self.transaprency[i] = i.ViewObject.Transparency
                i.ViewObject.Transparency = 80
            
            if (hasattr(i, "Shape") and i.Shape.Solids != [] and (i.InList == [] or i.InList[0].TypeId == 'App::DocumentObjectGroup')) or hasattr(i, "Proxy") and hasattr(i.Proxy, "Type") and i.Proxy.Type in ["assemblyMain"]:
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
            FreeCAD.Console.PrintWarning("{0} \n".format(e))
        
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
        

##***********************************************************************
##*                             CONSOLE
##***********************************************************************
#class checkCollisions:
    #def __init__(self, group1=[], group2=[]):
        
        #self.group1 = group1
        #self.group2 = group2
    
    #def show(self):
        #pass
    
    #def createSolid(self):
        #pass
        
    #def delete(self):
        #pass
