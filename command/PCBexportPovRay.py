# -*- coding: utf8 -*-
#****************************************************************************
#*                                                                          
#*   POV-Ray exporter v1.0                                                
#*   Copyright (c) 2014, 2015                                                     
#*   marmni <marmni@onet.eu>                                                
#*                                                                          
#*                                                                          
#*   This program is free software; you can redistribute it and/or modify   
#*   it under the terms of the GNU Lesser General Public License (LGPL)     
#*   as published by the Free Software Foundation; either version 2 of      
#*   the License, or (at your option) any later version.                    
#*   for detail see the LICENCE text file.                                  
#*                                                                          
#*   This program is distributed in the hope that it will be useful,        
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of         
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          
#*   GNU Library General Public License for more details.                   
#*                                                                          
#*   You should have received a copy of the GNU Library General Public      
#*   License along with this program; if not, write to the Free Software    
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307   
#*   USA                                                                    
#*                                                                          
#****************************************************************************

__title__ ="POV-Ray object exporter v1.0"
__author__ = "marmni <marmni@onet.eu>"
__url__ = ["http://www.freecadweb.org"]


import FreeCAD, FreeCADGui
import builtins
import Mesh
from PySide import QtCore, QtGui
import os
from PCBpartManaging import partsManaging

##############################################
#
##############################################
def meshFace(shape):
    faces = []
    triangles = shape.tessellate(1) # the number represents the precision of the tessellation
    for tri in triangles[1]:
        face = []
        for i in range(3):
            vindex = tri[i]
            face.append(triangles[0][vindex])
        faces.append(face)
    m = Mesh.Mesh(faces)
    #Mesh.show(m)
    return m

##############################################
#
##############################################
def meshObjects(projectObjects):
    if len(projectObjects) == 0:
        FreeCAD.Console.PrintWarning("No objects found!\n")
        return ""
    
    outPutString = ""
    #
    for i in projectObjects:  # objects in document
        try:
            objectColors = i.ViewObject.DiffuseColor
            shape = i.Shape.Faces
        except:
            continue
        
        if len(i.Shape.Faces) == 0:
            continue
        
        outPutString += "mesh2 {\n"
        ##################
        indexList = []
        vertexList = []
        colorsDeclaration = {}
        nr = 0
        for j in range(len(i.Shape.Faces)):
            # get face color
            if len(objectColors) == len(i.Shape.Faces):
                modelType = objectColors[j]
            else:
                modelType = objectColors[0]
            
            if not modelType in colorsDeclaration:
                colorsDeclaration[modelType] = []
            ######
            mesh = meshFace(i.Shape.Faces[j])

            for pp in mesh.Facets:
                colorsDeclaration[modelType].append(nr)
                nr += 1
                
                num = len(vertexList)
                for kk in pp.Points:
                    vertexList.append("\t<{0}, {1}, {2}>".format(kk[0], kk[1], -kk[2]))
                indexList.append([num, num + 1, num + 2])
        #
        outPutString += "vertex_vectors {\n"
        outPutString += "\t{0},\n".format(len(vertexList))
        outPutString += (',\n').join(vertexList)
        outPutString += "\n}\n\n"
        ##################
        outPutString += "texture_list {\n"
        outPutString += "\t{0},\n".format(len(colorsDeclaration.keys()))
        
        for j in colorsDeclaration.keys():
            outPutString += "\ttexture{pigment{rgb <%.2f, %.2f, %.2f>}}\n" % (j[0], j[1], j[2])
        
        outPutString += "}\n"
        ##################
        outPutString += "face_indices {\n"
        outPutString += "\t{0},\n".format(len(vertexList) / 3)
        for i in range(len(indexList)):
            faceColor = [k for k, l in colorsDeclaration.items() if i in l]
            faceColor = colorsDeclaration.keys().index(faceColor[0])
            outPutString += "\t<{0}, {1}, {2}>, {3}, \n".format(indexList[i][0], indexList[i][1], indexList[i][2], faceColor)
        
        outPutString += "}\n"
        ##################
        outPutString += "\n}\n"
    
    return outPutString


##############################################
#
##############################################
def exportObjectToPOVRAY(fileName, objectName, projectObjects):
    if len(projectObjects) == 0:
        FreeCAD.Console.PrintWarning("No objects found!\n")

    outPutString = meshObjects(projectObjects)
    if outPutString == "":
        return
    
    if not fileName.lower().endswith('inc'):
        fileName = fileName + '.inc'
    #
    try:
        partsManagingC = partsManaging()
        partsManagingC.setDatabase()
        packageData = partsManagingC.__SQL__.findPackage(objectName, "*")

        if packageData[0]:
            newX = packageData[2][2]
            newY = packageData[2][3]
            newZ = packageData[2][4]
            newRX = packageData[2][5] + 90
            newRY = packageData[2][6]
            newRZ = packageData[2][7]
        else:
            newX = 0
            newY = 0
            newZ = 0
            newRX = 0
            newRY = 0
            newRZ = 0
        #
        objectNameFormat = objectName.replace('-', '')
        #
        plik = builtins.open(fileName, "w")
        plik.write('''// ////////////////////////////////////////////////////////////
// 
// Add to file e3d_tools.inc
// #include "{0}"
// 
// ////////////////////////////////////////////////////////////

// ////////////////////////////////////////////////////////////
// 
// Add to file 3dusrpac.dat
// {1}:0:1:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:0:FC_obj_{2}(::
//
// ////////////////////////////////////////////////////////////

'''.format(fileName, objectName, objectNameFormat))

        plik.write('''
#macro FC_obj_%s(value)
union {
''' % objectNameFormat)

        plik.write(outPutString + "\n")
        plik.write('''}''')
        plik.write('''
    rotate<{0},{1},{2}>
    translate<{3},{5},{4}>
#end'''.format(newRX, newRY, newRZ, newX, newY, newZ))

        plik.close()
    except Exception as e:
        FreeCAD.Console.PrintWarning("{0} \n".format(e))
        return
        
    FreeCAD.Console.PrintWarning("Export finished successfully.\n")


##############################################
#
##############################################
class exportObjectToPovRayGui(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        #
        self.form = self
        self.form.setWindowTitle(u"Export object to Pov-Ray")
        #
        tab = QtGui.QTabWidget()
        tab.addTab(self.tabGeneral(), u'General')
        #
        lay = QtGui.QVBoxLayout(self)
        lay.addWidget(tab)
        #
    
    def tabGeneral(self):
        self.patherror = QtGui.QLabel('')
        self.objecterror = QtGui.QLabel('')
        
        self.filePath = QtGui.QLineEdit('')
        self.connect(self.filePath, QtCore.SIGNAL("textChanged (const QString&)"), self.changePathFInfo)
        self.filePath.setText(os.path.join(os.path.expanduser("~"), 'Unnamed.inc'))
        self.filePath.setReadOnly(True)
        
        self.objectName = QtGui.QLineEdit('')

        changePath = QtGui.QPushButton('...')
        changePath.setFixedWidth(30)
        self.connect(changePath, QtCore.SIGNAL("clicked ()"), self.changePathF)

        generalBox = QtGui.QGroupBox(u'General')
        generalBoxLay = QtGui.QGridLayout(generalBox)
        generalBoxLay.addWidget(QtGui.QLabel(u'Path           '), 0, 0, 1, 1)
        generalBoxLay.addWidget(self.filePath, 0, 1, 1, 2)
        generalBoxLay.addWidget(changePath, 0, 3, 1, 1)
        generalBoxLay.addWidget(self.patherror, 1, 0, 1, 4)
        generalBoxLay.addWidget(QtGui.QLabel(u'Object name      '), 2, 0, 1, 1)
        generalBoxLay.addWidget(self.objectName, 2, 1, 1, 3)
        generalBoxLay.addWidget(self.objecterror, 3, 0, 1, 4)
        generalBoxLay.setColumnStretch(1, 10)
        #
        self.exportObjects_All = QtGui.QRadioButton(u'All visible objects')
        self.exportObjects_All.setChecked(True)
        self.exportObjects_Selected = QtGui.QRadioButton(u'All selected objects')
        self.exportObjects_SelectedFaces = QtGui.QRadioButton(u'All selected faces')
        self.exportObjects_SelectedFaces.setDisabled(True)
        
        exportObjectsBox = QtGui.QGroupBox(u'Export objects')
        exportObjectsBoxLay = QtGui.QVBoxLayout(exportObjectsBox)
        exportObjectsBoxLay.addWidget(self.exportObjects_All)
        exportObjectsBoxLay.addWidget(self.exportObjects_Selected)
        exportObjectsBoxLay.addWidget(self.exportObjects_SelectedFaces)
        #####
        widget = QtGui.QWidget()
        lay = QtGui.QGridLayout(widget)
        lay.addWidget(generalBox, 0, 0, 1, 4)
        lay.addWidget(separator(), 1, 0, 1, 4)
        lay.addWidget(exportObjectsBox, 2, 0, 1, 4)
        lay.setRowStretch(10, 10)
        return widget
    
    def changePathFInfo(self):
        if os.path.exists(self.filePath.text()):
            self.patherror.setText('<span style="font-weight:bold; color: red;">You will overwrite existing file!</span>')
        else:
            self.patherror.setText('')
        
    def changePathF(self):
        path = QtGui.QFileDialog().getSaveFileName(self, u"Save as", os.path.expanduser("~"), "*.inc")

        fileName = path[0]
        if not fileName == "":
            if not fileName.lower().endswith('inc'):
                fileName = fileName + '.inc'
            self.filePath.setText(fileName)
            self.changePathFInfo()
    
    def accept(self):
        if self.objectName.text().strip() == "":
            self.objecterror.setText('<span style="font-weight:bold; color: red;">Missing object name!</span>')
            return False
        else:
            self.objecterror.setText('')
        #
        if self.exportObjects_All.isChecked():
            projectObjects = [i for i in FreeCAD.ActiveDocument.Objects if i.ViewObject.Visibility]
        elif self.exportObjects_Selected.isChecked():
            projectObjects = []
            for i in FreeCADGui.Selection.getSelection():
                if i.ViewObject.Visibility and i not in projectObjects:
                    projectObjects.append(i)
        
        if len(projectObjects) == 0:
            FreeCAD.Console.PrintWarning("No objects found!\n")
            return
        #
        exportObjectToPOVRAY(self.filePath.text(), self.objectName.text(), projectObjects)


##############################################
#
##############################################
class separator(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)
        #
        self.setFrameShape(QtGui.QFrame.HLine)
        self.setFrameShadow(QtGui.QFrame.Sunken)
        self.setLineWidth(1)
