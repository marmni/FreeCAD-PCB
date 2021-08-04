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
import os.path
import codecs
from xml.dom import minidom
from math import degrees

from PCBfunctions import edgeGetArcAngle
from PCBconf import exportData

__currentPath__ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

#***********************************************************************
#*                             GUI
#***********************************************************************
class createSectionsGui(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.form = self
        self.form.setWindowTitle(u"Create sections from selected models")
        self.form.setWindowIcon(QtGui.QIcon(":/data/img/Part_CrossSections.svg"))
        
        self.exportClass = None
        #
        self.componentsList = []
        self.components = []
        for i in FreeCADGui.Selection.getSelection():
            if  hasattr(i, "Shape") and "Part" in i.TypeId: 
                # i.ViewObject.Transparency = 80
                self.componentsList.append(i)
        
        if len(self.componentsList) == 0:
            self.components = None
        elif len(self.componentsList) == 1:
            self.components = self.componentsList[0].Shape
        else:
            self.components = Part.makeCompound([i.Shape for i in self.componentsList])
        #
        self.sectionsLisstTable = sectionsLisstTable(self)
        #
        self.mirrorSections = QtGui.QComboBox()
        self.mirrorSections.addItems(["False", "True"])
        #
        self.guidingPlane = QtGui.QComboBox()
        self.connect(self.guidingPlane, QtCore.SIGNAL("currentIndexChanged (int)"), self.showSecton)
        self.guidingPlane.addItems(["XY", "XZ", "YZ"])
        self.guidingPlane.setCurrentIndex(0)
        #
        addSection = QtGui.QPushButton('')
        #addSection.setFlat(True)
        addSection.setIcon(QtGui.QIcon(":/data/img/categoryAdd.png"))
        addSection.setFixedWidth(24)
        addSection.setToolTip('Add section')
        self.connect(addSection, QtCore.SIGNAL("pressed ()"), self.sectionsLisstTable.addSection)
        #
        self.listaBibliotek = QtGui.QComboBox()
        for i in exportData.keys():
            if exportData[i]["exportComponent"]:
                self.listaBibliotek.addItem(exportData[i]['name'])
                self.listaBibliotek.setItemData(self.listaBibliotek.count() - 1, i, QtCore.Qt.UserRole)
        self.connect(self.listaBibliotek, QtCore.SIGNAL("currentIndexChanged (int)"), self.changeSoftware)
        #
        deleteSection = QtGui.QPushButton('')
        #deleteSection.setFlat(True)
        deleteSection.setIcon(QtGui.QIcon(":/data/img/categoryDelete.png"))
        deleteSection.setFixedWidth(24)
        deleteSection.setToolTip('Delete section')
        self.connect(deleteSection, QtCore.SIGNAL("pressed ()"), self.sectionsLisstTable.deleteSection)
        #
        libraryPathSel = QtGui.QPushButton('...')
        libraryPathSel.setFixedWidth(24)
        libraryPathSel.setToolTip('Define file')
        self.connect(libraryPathSel, QtCore.SIGNAL("clicked ()"), self.changePathF)
        
        self.libraryPath = QtGui.QLineEdit('')
        #
        self.componentName = QtGui.QLineEdit('')
        #
        infoLabel = QtGui.QLabel(u''' 
If library does not exist  - a new library will be created
If there is a library and component with the given name - component will be updated
If library exists but there is no component with the specified name - component will be added
        ''')
        infoLabel.setWordWrap(True)
        #
        lay = QtGui.QGridLayout(self)
        lay.addWidget(QtGui.QLabel(u'Path:'), 0, 0, 1, 1)
        lay.addWidget(self.libraryPath, 0, 1, 1, 1)
        lay.addWidget(libraryPathSel, 0, 2, 1, 1)
        lay.addWidget(QtGui.QLabel(u'Software:'), 1, 0, 1, 1)
        lay.addWidget(self.listaBibliotek, 1, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Component name:'), 2, 0, 1, 1)
        lay.addWidget(self.componentName, 2, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Guiding plane:'), 3, 0, 1, 1)
        lay.addWidget(self.guidingPlane, 3, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Mirror sections:'), 4, 0, 1, 1)
        lay.addWidget(self.mirrorSections, 4, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Sections:'), 5, 0, 1, 1)
        lay.addWidget(self.sectionsLisstTable, 5, 1, 3, 1)
        lay.addWidget(addSection, 5, 2, 1, 1)
        lay.addWidget(deleteSection, 6, 2, 1, 1)
        lay.addWidget(infoLabel, 8, 0, 1, 3)
        #
        self.sectionsLisstTable.addSection()
        self.changeSoftware(0)
        
    def changeSoftware(self, index):
        self.exportClass = eval(exportData[self.listaBibliotek.itemData(self.listaBibliotek.currentIndex(), QtCore.Qt.UserRole)]['exportClass'])
        
        if self.libraryPath.text().strip() != "":
            path = self.libraryPath.text().strip().split('.')
            self.libraryPath.setText(path[0] + exportData[self.exportClass.programName]['formatLIB'].replace("*", ""))
        
    def changePathF(self):
        path = QtGui.QFileDialog().getSaveFileName(self, u"Save as", os.path.expanduser("~"), exportData[self.exportClass.programName]['formatLIB'])
        
        filePath = path[0]
        if not filePath == "":
            filename, file_extension = os.path.splitext(filePath)
            
            if file_extension == "" or not file_extension == exportData[self.exportClass.programName]['formatLIB'].replace("*", ""):
                filePath = filename + exportData[self.exportClass.programName]['formatLIB'].replace("*", "")
            
            self.libraryPath.setText(filePath)
        
    def reject(self):
        self.sectionsLisstTable.removeRoot()
        # self.resetTransparency()
        return True
    
    def accept(self):
        if self.sectionsLisstTable.invisibleRootItem().childCount() == 0:
            FreeCAD.Console.PrintWarning("Add minimum one section.\n")
            return False
        elif self.componentName.text().strip() == "":
            FreeCAD.Console.PrintWarning("Set component name.\n")
            return False
        elif self.libraryPath.text().strip() == "":
            FreeCAD.Console.PrintWarning("Set output file.\n")
            return False
        #
        self.sectionsLisstTable.removeRoot()
        #
        if not self.libraryPath.text().strip() == "":
            filename, file_extension = os.path.splitext(self.libraryPath.text().strip())
            
            if file_extension == "" or not file_extension == exportData[self.exportClass.programName]['formatLIB'].replace("*", ""):
                self.libraryPath.setText(filename + exportData[self.exportClass.programName]['formatLIB'].replace("*", ""))
        # generate sections
        if self.components:
            self.exportClass.libraryPath = self.libraryPath.text().strip()
            if os.path.exists(self.libraryPath.text().strip()):
                self.exportClass.addToExistingLibrary()
            else:
                self.exportClass.createNewLibrary()
            self.exportClass.createComponent(self.componentName.text().strip())
            #
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
                if self.mirrorSections.currentIndex() == 1:
                    comp.Placement = FreeCAD.Placement(FreeCAD.Vector(nX, nZ, 0), FreeCAD.Rotation(FreeCAD.Vector(1,0,0), -90))
                else:
                    comp.Placement = FreeCAD.Placement(FreeCAD.Vector(nX, nZ*-1, 0), FreeCAD.Rotation(FreeCAD.Vector(1,0,0), 90))
            else: # YZ
                if self.mirrorSections.currentIndex() == 1:
                    comp.Placement = FreeCAD.Placement(FreeCAD.Vector(nZ, nY*-1, 0), FreeCAD.Rotation(FreeCAD.Vector(0,1,0), -90))
                else:
                    comp.Placement = FreeCAD.Placement(FreeCAD.Vector(nZ, nY, 0), FreeCAD.Rotation(FreeCAD.Vector(0,1,0), 90))
            # filter / export
            self.dataOut = {}
            self.dataOut["lines"] = []
            self.dataOut["circles"] = []
            self.dataOut["arcs"] = []
            
            self.loopWires(comp.Wires)
            #
            self.exportClass.export()
        #
        #self.resetTransparency()
        #
        return True
        
    # def resetTransparency(self):
        # for i in self.componentsList:
            # try:
                # i.ViewObject.Transparency = 80
            # except Exception as e:
                # print(e)

    def loopWires(self, wires):
        for i in wires:
            for j in i.Edges:
                if j.Curve.__class__.__name__ == "Line":
                    x1 = round(j.Vertexes[0].X, 2)
                    y1 = round(j.Vertexes[0].Y, 2)
                    x2 = round(j.Vertexes[1].X, 2)
                    y2 = round(j.Vertexes[1].Y, 2)
                    
                    if not [x1, y1,x2, y2] in self.dataOut["lines"] or not [x2, y2,x1, y1] in self.dataOut["lines"]:
                        self.dataOut["lines"].append([x1, y1,x2, y2])
                        self.exportClass.addLine(x1, y1, x2, y2)
                    else:
                       continue
                elif j.Curve.__class__.__name__ == "Ellipse":
                    print("ellipse - skipped")
                    continue
                elif j.Curve.__class__.__name__ == "BSplineCurve":
                    newData = j.Curve.toBiArcs(0.001)
                    newWires = [Part.Wire([Part.Edge(p) for p in newData])]
                    self.loopWires(newWires)
                elif j.Curve.__class__.__name__ == "Hyperbola":
                    newData = j.toNurbs()
                    newWires = [Part.Wire([Part.Edge(p) for p in newData.Edges])]
                    self.loopWires(newWires)
                else: # circle/arc
                    c = j.Curve
                    
                    xs = round(c.Center.x, 2)
                    ys = round(c.Center.y, 2)
                    r = round(c.Radius, 2)
                    
                    if (round(j.FirstParameter, 2) == 6.28 and j.LastParameter == 0) or (j.FirstParameter == 0 and round(j.LastParameter, 2) == 6.28): # circle
                        if not [xs, ys, r] in self.dataOut["circles"]:
                            self.dataOut["circles"].append([xs, ys, r])
                            self.exportClass.addCircle(xs, ys, r)
                    else: # arc
                        x1 = round(j.Vertexes[0].X, 2)
                        y1 = round(j.Vertexes[0].Y, 2)
                        x2 = round(j.Vertexes[1].X, 2)
                        y2 = round(j.Vertexes[1].Y, 2)
                        
                        if self.exportClass.programName == 'eagle':
                            [curve, start, stop] = edgeGetArcAngle(j)
                        else:
                            start = degrees(j.FirstParameter)
                            stop = degrees(j.LastParameter)
                            curve = start - stop
                        
                        if not [x1, y1, x2, y2, curve, xs, ys, r, start, stop] in self.dataOut["arcs"]:
                            self.dataOut["arcs"].append([x1, y1, x2, y2, curve, xs, ys, r, start, stop])
                            self.exportClass.addArc(x1, y1, x2, y2, curve, xs, ys, r, start, stop)

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
            redPlastic = SoMaterial()
            redPlastic.ambientColor = (1.0, 0.0, 0.0)
            redPlastic.diffuseColor = (1.0, 0.0, 0.0) 
            redPlastic.specularColor = (0.5, 0.5, 0.5)
            redPlastic.shininess = 0.1
            redPlastic.transparency = 0.7
            self.root.addChild(redPlastic)
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
    
    def deleteSection(self):
        if self.currentItem():
            self.takeTopLevelItem(self.indexOfTopLevelItem(self.currentItem()))
            self.createPlane()
    
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


class exportModel():
    def __init__(self):
        self.dummyFile = None
    
    def convertValues(self, data):
        if self.mainUnit == 'inch':
            data /= 25.4
        elif self.mainUnit == 'mil':
            data /= 0.0254
        
        data = round(data, 2)
        
        return str(data)
    
    def fileExtension(self, path):
        if exportData[self.programName]['formatLIB'] != "":
            extension = exportData[self.programName]['formatLIB'].split('.')[1]
            if not path.endswith(extension):
                path += '.{0}'.format(extension)
        
        return path


class kicad(exportModel):
    def __init__(self):
        exportModel.__init__(self)
        #
        self.libraryPath = None
        self.programName = 'kicad'
        self.mainUnit = 'mm'
    
    def createComponent(self, componentName):
        self.dummyFile.write(u'''(module {0} (layer F.Cu) (tedit 5BC8D926)
  (descr "DESCRIPTION")
  (tags "TAGS")
  (attr smd)
  (fp_text reference REF** (at 0 -2.7) (layer F.SilkS)
    (effects (font (size 1 1) (thickness 0.15)))
  )
  (fp_text value {0} (at 0 2.7) (layer F.Fab)
    (effects (font (size 1 1) (thickness 0.15)))
  )
  '''.format(componentName.replace(" ", "_")))
    
    def addToExistingLibrary(self):
        if self.libraryPath:
            self.dummyFile = codecs.open(self.fileExtension(self.libraryPath), mode="w")

    def createNewLibrary(self):
        if self.libraryPath:
            self.dummyFile = codecs.open(self.fileExtension(self.libraryPath), mode="w")
    
    def export(self):
        self.dummyFile.write(u')')
        self.dummyFile.close()

    def addLine(self, x1, y1, x2, y2):
        if [x1, y1] != [x2, y2]:
            self.dummyFile.write(u'(fp_line (start {0} {1}) (end {2} {3}) (layer F.Fab) (width 0.1))\n'.format(self.convertValues(x1), self.convertValues(y1), self.convertValues(x2), self.convertValues(y2)))
    
    def addArc(self, x1, y1, x2, y2, curve, xs, ys, r, start, stop):
        if curve > 0:
            curve *= -1
            x1 = x1
            y1 = y1
        else:
            x1 = x2
            y1 = y2
        
        self.dummyFile.write(u'(fp_arc (start {0} {1}) (end {2} {3}) (angle {4}) (layer F.Fab) (width 0.1))\n'.format(self.convertValues(xs), self.convertValues(ys), self.convertValues(x1), self.convertValues(y1), curve))
        
    def addCircle(self, xs, ys, r):
        x1 = xs + r
        self.dummyFile.write(u'(fp_circle (center {0} {1}) (end {2} {1}) (layer F.Fab) (width 0.1))\n'.format(self.convertValues(xs), self.convertValues(ys), self.convertValues(x1)))


class geda(exportModel):
    def __init__(self):
        exportModel.__init__(self)
        #
        self.libraryPath = None
        self.programName = 'geda'
        self.mainUnit = 'mil'
    
    def createComponent(self, componentName):
        self.dummyFile.write(u'Element(0x00000000 "" "{0}" "" 0 0 0 0 0 40 0x00000000)\n'.format(componentName.replace(" ", "_")))
        self.dummyFile.write(u'(\n')
    
    def addToExistingLibrary(self):
        if self.libraryPath:
            self.dummyFile = codecs.open(self.fileExtension(self.libraryPath), mode="w")

    def createNewLibrary(self):
        if self.libraryPath:
            self.dummyFile = codecs.open(self.fileExtension(self.libraryPath), mode="w")
    
    def export(self):
        self.dummyFile.write(u')')
        self.dummyFile.close()

    def addLine(self, x1, y1, x2, y2):
        if [x1, y1] != [x2, y2]:
            self.dummyFile.write(u'ElementLine ({0} {1} {2} {3} 10)\n'.format(self.convertValues(x1), self.convertValues(y1), self.convertValues(x2), self.convertValues(y2)))
    
    def addArc(self, x1, y1, x2, y2, curve, xs, ys, r, start, stop):
        if curve > 0:
            self.dummyFile.write(u'ElementArc({0} {1} {2} {2} {3} {4} 10)\n'.format(self.convertValues(xs), self.convertValues(ys), self.convertValues(r), start, curve))
        else:
            self.dummyFile.write(u'ElementArc({0} {1} {2} {2} {3} {4} 10)\n'.format(self.convertValues(xs), self.convertValues(ys), self.convertValues(r), stop, curve))

    def addCircle(self, xs, ys, r):
        self.dummyFile.write(u'ElementArc({0} {1} {2} {2} 0 360 10)\n'.format(self.convertValues(xs), self.convertValues(ys), self.convertValues(r)))


class eagle(exportModel):
    def __init__(self):
        exportModel.__init__(self)
        #
        self.libraryPath = None
        self.programName = 'eagle'
        self.mainUnit = 'mm'
    
    def addLine(self, x1, y1, x2, y2):
        if [x1, y1] != [x2, y2]:
            x = self.dummyFile.createElement("wire")
            x.setAttribute('x1', self.convertValues(x1))
            x.setAttribute('y1', self.convertValues(y1))
            x.setAttribute('x2', self.convertValues(x2))
            x.setAttribute('y2', self.convertValues(y2))
            x.setAttribute('width', self.convertValues(0.127))
            x.setAttribute('layer', "21")
            
            self.package.appendChild(x)
            self.package.appendChild(self.dummyFile.createTextNode('\n'))
    
    def addCircle(self, xs, ys, r):
        x = self.dummyFile.createElement("circle")
        x.setAttribute('x', self.convertValues(xs))
        x.setAttribute('y', self.convertValues(ys))
        x.setAttribute('radius', self.convertValues(r))
        x.setAttribute('width', self.convertValues(0.127))
        x.setAttribute('layer', "21")
        
        self.package.appendChild(x)
        self.package.appendChild(self.dummyFile.createTextNode('\n'))
    
    def addArc(self, x1, y1, x2, y2, curve, xs, ys, r, start, stop):
        x = self.dummyFile.createElement("wire")
        x.setAttribute('x1', self.convertValues(x1))
        x.setAttribute('y1', self.convertValues(y1))
        x.setAttribute('x2', self.convertValues(x2))
        x.setAttribute('y2', self.convertValues(y2))
        x.setAttribute('curve', str(curve))
        x.setAttribute('width', "0.127")
        x.setAttribute('layer', "21")
        
        self.package.appendChild(x)
        self.package.appendChild(self.dummyFile.createTextNode('\n'))

    def createPackage(self, name):
        packages = self.dummyFile.getElementsByTagName('packages')[0]
        #
        for i in packages.getElementsByTagName('package'):
            if i.getAttribute('name') == name:
                packages.removeChild(i)
        #
        self.package = self.dummyFile.createElement("package")
        self.package.setAttribute('name', name)
        
        self.package.appendChild(self.dummyFile.createTextNode('\n'))
        #
        packages.appendChild(self.package)
        packages.appendChild(self.dummyFile.createTextNode('\n'))
        # desc
        description = self.dummyFile.createElement("description")
        description.appendChild(self.dummyFile.createTextNode("Description"))
        
        self.package.appendChild(description)
        self.package.appendChild(self.dummyFile.createTextNode('\n'))
        # name
        componentName = self.dummyFile.createElement("text")
        componentName.setAttribute('x', '0')
        componentName.setAttribute('y', '2')
        componentName.setAttribute('size', '1.27')
        componentName.setAttribute('layer', '25')
        #componentName.setAttribute('ration', '10')
        componentName.appendChild(self.dummyFile.createTextNode("<NAME"))
        
        self.package.appendChild(componentName)
        self.package.appendChild(self.dummyFile.createTextNode('\n'))
        # value
        componentValue = self.dummyFile.createElement("text")
        componentValue.setAttribute('x', '0')
        componentValue.setAttribute('y', '-2')
        componentValue.setAttribute('size', '1.27')
        componentValue.setAttribute('layer', '25')
        #componentValue.setAttribute('ration', '10')
        componentValue.appendChild(self.dummyFile.createTextNode("<VALUE"))
        
        self.package.appendChild(componentValue)
        self.package.appendChild(self.dummyFile.createTextNode('\n'))
        
    def createDeviceset(self, name):
        devicesets = self.dummyFile.getElementsByTagName('devicesets')[0]
        #
        for i in devicesets.getElementsByTagName('deviceset'):
            if i.getAttribute('name') == name:
                devicesets.removeChild(i)
        #
        deviceset = self.dummyFile.createElement("deviceset")
        deviceset.setAttribute('name', name)
        #
        gates = self.dummyFile.createElement("gates")
        
        deviceset.appendChild(self.dummyFile.createTextNode('\n'))
        deviceset.appendChild(gates)
        deviceset.appendChild(self.dummyFile.createTextNode('\n'))
        #
        devices = self.dummyFile.createElement("devices")
        
        device = self.dummyFile.createElement("device")
        device.setAttribute('name', "")
        device.setAttribute('package', name)
        
        technologies = self.dummyFile.createElement("technologies")
        
        technology = self.dummyFile.createElement("technology")
        technology.setAttribute('name', "")
        technologies.appendChild(self.dummyFile.createTextNode('\n'))
        technologies.appendChild(technology)
        technologies.appendChild(self.dummyFile.createTextNode('\n'))
        
        device.appendChild(self.dummyFile.createTextNode('\n'))
        device.appendChild(technologies)
        device.appendChild(self.dummyFile.createTextNode('\n'))
        devices.appendChild(self.dummyFile.createTextNode('\n'))
        devices.appendChild(device)
        devices.appendChild(self.dummyFile.createTextNode('\n'))
        deviceset.appendChild(devices)
        deviceset.appendChild(self.dummyFile.createTextNode('\n'))
        #
        devicesets.appendChild(deviceset)
        devicesets.appendChild(self.dummyFile.createTextNode('\n'))
        
    def createComponent(self, componentName):
        componentName = componentName.upper()
        componentName = componentName.replace(" ", "_")
        
        self.createDeviceset(componentName)
        self.createPackage(componentName)
    
    def addToExistingLibrary(self):
        self.dummyFile = minidom.parse(self.libraryPath)
        
        if self.libraryPath:
            with codecs.open(self.fileExtension(self.libraryPath) + "_copy", "w", "utf-8") as out:
                self.dummyFile.writexml(out)
        #
        #self.mainUnit = self.dummyFile.getElementsByTagName('grid')[0].getAttribute('unit')
        
    def createNewLibrary(self):
        #self.mainUnit = 'mm'
        self.dummyFile = minidom.parse(__currentPath__ + "/save/FreeCAD-PCB.lbr")
    
    def export(self):
        if self.libraryPath:
            fileName = self.fileExtension(self.libraryPath)
        
            with codecs.open(fileName, "w", "utf-8") as out:
                self.dummyFile.writexml(out)
        
