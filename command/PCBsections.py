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
if FreeCAD.GuiUp:
    from PySide import QtGui, QtCore
import Part
from pivy.coin import *

from functools import partial
import builtins

from PCBfunctions import edgeGetArcAngle

#***********************************************************************
#*                             GUI
#***********************************************************************
class createSectionsGui(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.form = self
        self.form.setWindowTitle(u"Create sections from selected models")
        self.form.setWindowIcon(QtGui.QIcon(":/data/img/gluePath.png"))
        #
        self.components = []
        for i in FreeCADGui.Selection.getSelection():
            if  hasattr(i, "Shape") and "Part" in i.TypeId: 
                self.components.append(i)
        
        if len(self.components) == 0:
            self.components = None
        elif len(self.components) == 1:
            self.components = self.components[0].Shape
        else:
            self.components = Part.makeCompound([i.Shape for i in self.components])
        #
        self.sectionsLisstTable = sectionsLisstTable(self)
        #
        self.guidingPlane = QtGui.QComboBox()
        self.connect(self.guidingPlane, QtCore.SIGNAL("currentIndexChanged (int)"), self.showSecton)
        self.guidingPlane.addItems(["XY", "XZ", "YZ"])
        self.guidingPlane.setCurrentIndex(0)
        #
        addPlane = QtGui.QPushButton('add')
        self.connect(addPlane, QtCore.SIGNAL("pressed ()"), self.sectionsLisstTable.addSection)
        #
        lay = QtGui.QGridLayout(self)
        lay.addWidget(QtGui.QLabel(u'Guiding plane:'), 0, 0, 1, 1)
        lay.addWidget(self.guidingPlane, 0, 1, 1, 1)
        lay.addWidget(QtGui.QLabel(u'Sections:'), 1, 0, 1, 1)
        lay.addWidget(self.sectionsLisstTable, 1, 1, 1, 1)
        lay.addWidget(addPlane, 2, 1, 1, 1)
        #
        self.sectionsLisstTable.addSection()
        
    def reject(self):
        self.sectionsLisstTable.removeRoot()
        return True
    
    def accept(self):
        self.sectionsLisstTable.removeRoot()
        # generate sections
        if self.components:
            if self.guidingPlane.currentIndex() == 0: # XY
                v = FreeCAD.Vector(0, 0, 1)
            elif self.guidingPlane.currentIndex() == 1: # XZ
                v = FreeCAD.Vector(0, 1, 0)
            else: # YZ
                v = FreeCAD.Vector(1, 0, 0)
            
            data = []
            for i in range(self.sectionsLisstTable.invisibleRootItem().childCount()):
                item = self.sectionsLisstTable.invisibleRootItem().child(i)
                pos = float(self.sectionsLisstTable.itemWidget(item, 1).value())
                #
                if self.guidingPlane.currentIndex() == 0: # XY
                    zValue = self.components.BoundBox.Center.z
                    
                    for j in self.components.slice(v, zValue + pos):
                        j.Placement.Base.z = (zValue + pos) * -1
                        data.append(j)
                elif self.guidingPlane.currentIndex() == 1: # XZ
                    zValue = self.components.BoundBox.Center.y
                    
                    for j in self.components.slice(v, zValue + pos):
                        j.Placement.Base.y = (zValue + pos) * -1
                        data.append(j)
                else: # YZ
                    zValue = self.components.BoundBox.Center.x
                    
                    for j in self.components.slice(v, zValue + pos):
                        j.Placement.Base.x = (zValue + pos) * -1
                        data.append(j)
            
            comp = Part.Compound(data)
            
            nX = comp.BoundBox.Center.x * -1
            nY = comp.BoundBox.Center.y * -1
            nZ = comp.BoundBox.Center.z * -1
            
            if self.guidingPlane.currentIndex() == 0: # XY
                comp.Placement = FreeCAD.Placement(FreeCAD.Vector(nX, nY, nZ), FreeCAD.Rotation(FreeCAD.Vector(1,0,0), 0))
            elif self.guidingPlane.currentIndex() == 1: # XZ
                comp.Placement = FreeCAD.Placement(FreeCAD.Vector(nX, nZ*-1, 0), FreeCAD.Rotation(FreeCAD.Vector(1,0,0), 90))
            else: # YZ
                comp.Placement = FreeCAD.Placement(FreeCAD.Vector(nZ, nY, 0), FreeCAD.Rotation(FreeCAD.Vector(0,1,0), 90))
            # filter
            dataOut = {}
            dataOut["lines"] = []
            dataOut["circles"] = []
            dataOut["arcs"] = []
            
            fileOut = builtins.open("C:/Users/marmn/Desktop/test.txt", "w")
           
            for i in comp.Wires:
                for j in i.Edges:
                    if j.Curve.__class__.__name__ == "Line":
                        x1 = round(j.Vertexes[0].X, 2)
                        y1 = round(j.Vertexes[0].Y, 2)
                        x2 = round(j.Vertexes[1].X, 2)
                        y2 = round(j.Vertexes[1].Y, 2)
                        
                        if not [x1, y1,x2, y2] in dataOut["lines"] or not [x2, y2,x1, y1] in dataOut["lines"]:
                            dataOut["lines"].append([x1, y1,x2, y2])
                            fileOut.write('<wire x1="{0}" y1="{1}" x2="{2}" y2="{3}" width="0.127" layer="21"/>\n'.format(x1, y1, x2, y2))
                        else:
                           continue
                    else: # circle/arc
                        c = j.Curve
                        
                        if round(j.FirstParameter, 2) == 6.28 or round(j.LastParameter, 2) == 6.28: # circle
                            x = round(c.Center.x, 2)
                            y = round(c.Center.y, 2)
                            r = round(c.Radius, 2)
                            
                            if not [x, y, r] in dataOut["circles"]:
                                dataOut["circles"].append([x, y, r])
                                fileOut.write('<circle x="{0}" y="{1}" radius="{2}" width="0.127" layer="21"/>\n'.format(x, y, r))
                        else: # arc
                            x1 = round(j.Vertexes[0].X, 2)
                            y1 = round(j.Vertexes[0].Y, 2)
                            x2 = round(j.Vertexes[1].X, 2)
                            y2 = round(j.Vertexes[1].Y, 2)
                            [curve, start, stop] = edgeGetArcAngle(j)
                            
                            curve = round(curve, 2)
                            
                            if not [x1, y1, x2, y2, curve] in dataOut["arcs"]:
                                dataOut["arcs"].append([x1, y1, x2, y2, curve])
                                fileOut.write('<wire x1="{0}" y1="{1}" x2="{2}" y2="{3}" width="0.127" layer="21" curve="{4}"/>\n'.format(x1, y1, x2, y2, curve))
            fileOut.close()
        #
        return True
    
    def showSecton(self, planeID):
        self.sectionsLisstTable.createPlane()


class sectionsLisstTable(QtGui.QTreeWidget):
    def __init__(self, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        self.sectionNum = 0
        self.parent = parent
        self.root = None
        #
        
        self.setColumnCount(2)
        self.setItemsExpandable(True)
        self.setSortingEnabled(False)
        self.setHeaderLabels(['Number', 'Position'])
        self.setFrameShape(QtGui.QFrame.NoFrame)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setStyleSheet('''
            QTreeWidget QHeaderView
            {
                border:0px;
            }
            QTreeWidget
            {
                border: 1px solid #9EB6CE;
                border-top:0px;
            }
            QTreeWidget QHeaderView::section
            {
                color:#4C4161;
                font-size:12px;
                border:1px solid #9EB6CE;
                border-left:0px;
                padding:5px;
            }
        ''')
        
    def removeRoot(self):
        if self.root:
            try:
                FreeCADGui.ActiveDocument.ActiveView.getSceneGraph().removeChild(self.root)
            except:
                pass
        
    def createPlane(self):
        self.removeRoot()
        if self.parent.components:
            self.root = SoSeparator()
            #
            if self.parent.guidingPlane.currentIndex() == 0: # XY
                myRotation = SoRotationXYZ()
                myRotation.angle = - 3.14 / 2.
                myRotation.axis = SoRotationXYZ.X
                self.root.addChild(myRotation)
                
                myTransform = SoTransform()
                myTransform.translation = (self.parent.components.BoundBox.Center.x, 0, self.parent.components.BoundBox.Center.y)
                self.root.addChild(myTransform)
            elif self.parent.guidingPlane.currentIndex() == 1: # XZ
                myRotation = SoRotationXYZ()
                myRotation.angle = 3.14 / 2.
                myRotation.axis = SoRotationXYZ.Z
                self.root.addChild(myRotation)
                
                myTransform = SoTransform()
                myTransform.translation = (0, -self.parent.components.BoundBox.Center.x, self.parent.components.BoundBox.Center.z)
                self.root.addChild(myTransform)
            else: # YZ
                myRotation = SoRotationXYZ()
                myRotation.angle = -3.14 / 2.
                myRotation.axis = SoRotationXYZ.Y
                self.root.addChild(myRotation)
                
                myTransform = SoTransform()
                myTransform.translation = (self.parent.components.BoundBox.Center.z, self.parent.components.BoundBox.Center.y, 0)
                self.root.addChild(myTransform)
            #
            for i in range(self.invisibleRootItem().childCount()):
                item = self.invisibleRootItem().child(i)
                #
                pos = float(self.itemWidget(item, 1).value())
                
                if self.parent.guidingPlane.currentIndex() == 0: # XY
                    zValue = self.parent.components.BoundBox.Center.z
                    
                    myTransform = SoTransform()
                    myTransform.translation = (0, (zValue + pos) * -1, 0)
                    self.root.addChild(myTransform)
                    #
                    plane = SoCube()
                    plane.width = self.parent.components.BoundBox.XLength
                    plane.height = 0.01
                    plane.depth = self.parent.components.BoundBox.YLength
                    self.root.addChild(plane)
                    #
                    myTransform1 = SoTransform()
                    myTransform1.translation = (0, zValue + pos, 0)
                    self.root.addChild(myTransform1)
                elif self.parent.guidingPlane.currentIndex() == 1: # XZ
                    zValue = self.parent.components.BoundBox.Center.y
                    
                    myTransform = SoTransform()
                    myTransform.translation = (zValue + pos, 0, 0)
                    self.root.addChild(myTransform)
                    #
                    plane = SoCube()
                    plane.width = 0.01
                    plane.height = self.parent.components.BoundBox.XLength
                    plane.depth = self.parent.components.BoundBox.ZLength
                    self.root.addChild(plane)
                    #
                    myTransform1 = SoTransform()
                    myTransform1.translation = ((zValue + pos)* -1, 0, 0)
                    self.root.addChild(myTransform1)
                else: # YZ
                    zValue = self.parent.components.BoundBox.Center.x
                    
                    myTransform = SoTransform()
                    myTransform.translation = (0, 0, (zValue + pos)* -1)
                    self.root.addChild(myTransform)
                    #
                    plane = SoCube()
                    plane.width = self.parent.components.BoundBox.ZLength
                    plane.height = self.parent.components.BoundBox.YLength
                    plane.depth = 0.01
                    self.root.addChild(plane)
                    #
                    myTransform1 = SoTransform()
                    myTransform1.translation = (0, 0, zValue + pos)
                    self.root.addChild(myTransform1)
            #
            FreeCADGui.ActiveDocument.ActiveView.getSceneGraph().addChild(self.root)
    
    def addSection(self):
        try:
            a = QtGui.QTreeWidgetItem()
            a.setText(0, str(self.sectionNum))
            #
            positionValue = QtGui.QDoubleSpinBox()
            self.connect(positionValue, QtCore.SIGNAL("valueChanged (double)"), self.shiftSection)
            positionValue.setSuffix("mm")
            positionValue.setValue(0)
            positionValue.setRange(-1000, 1000)
            #
            self.addTopLevelItem(a)
            
            globals()["zm_d_%s" % self.sectionNum] = positionValue  # workaround bug from pyside
            self.setItemWidget(a, 1, globals()["zm_d_%s" % self.sectionNum])
            # section plane
            self.createPlane()
            #
            self.sectionNum += 1
        except Exception as e:
            FreeCAD.Console.PrintWarning(format(e))
    
    def shiftSection(self, value):
        self.createPlane()
