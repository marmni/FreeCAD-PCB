# -*- coding: utf8 -*-
#****************************************************************************
#*                                                                          
#*   Kerkythea exporter v1.2                                                
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

#****************************************************************************
#*                                                                          
#*                                 BASED ON                                 
#*                                                                          
#* IOANNIS PANTAZOPOULOS                                                    
#*                                                                          
#* Sample code exporting basic Kerkythea XML file.                          
#*                                                                          
#* Version v1.0                                                             
#*                                                                          
#****************************************************************************

__title__ ="Kerkythea exporter v1.2"
__author__ = "marmni <marmni@onet.eu>"
__url__ = ["http://www.freecadweb.org"]


import FreeCAD, FreeCADGui
import random
import builtins
import Mesh
from PySide import QtCore, QtGui
import os
import sys


##############################################
#
##############################################
class point3D:
    def __init__(self, point):
        self.x = "%.4f" % (point[0] * 0.001)
        self.y = "%.4f" % (point[1] * 0.001)
        self.z = "%.4f" % (point[2] * 0.001)
        
    def __str__(self):
        return '<P xyz="{0} {1} {2}"/>'.format(self.x, self.y, self.z)

    #def __eq__(self, other):
        #if self.x == other.x and self.y == other.y and self.z == other.z:
            #return True
        #else:
            #return False 


##############################################
#
##############################################
class indexListPoint3D:
    def __init__(self, point):
        self.i = point[0]
        self.j = point[1]
        self.k = point[2]

    def __str__(self):
        return '<F ijk="{0} {1} {2}"/>'.format(self.i, self.j, self.k)


##############################################
#
##############################################
class Material:
    def __init__(self):
        self.diffuse = None  # Texture()
        self.shininess = 1000.0
        self.ior = 2.0

    def write(self, file):
        file.write('''<Object Identifier="Whitted Material" Label="Whitted Material" Name="" Type="Material">\n''')

        self.diffuse.write(file, "Diffuse")
        self.diffuse.write(file, "Translucent")
        self.diffuse.write(file, "Specular")
        self.diffuse.write(file, "Transmitted")

        file.write('''<Parameter Name="Shininess" Type="Real" Value="{shininess}"/>
<Parameter Name="Transmitted Shininess" Type="Real" Value="{shininess}"/>
<Parameter Name="Index of Refraction" Type="Real" Value="{ior}"/>
</Object>\n'''.format(shininess=self.shininess, ior=self.ior))


##############################################
#
##############################################
class Texture:
    def __init__(self, color):
        self.color = color
        
    def getColorSTR(self):
        return '{0} {1} {2}'.format(self.color[0], self.color[1], self.color[2])

    def toGrayscale(self):
        RGB = 0.299 * self.color[0] + 0.587 * self.color[1] + 0.114 * self.color[2]
        self.color = [RGB, RGB, RGB]

    def write(self, file, identifier):
        file.write('''<Object Identifier="./{identifier}/Constant Texture" Label="Constant Texture" Name="" Type="Texture">
<Parameter Name="Color" Type="RGB" Value="{color}"/>
</Object>\n'''.format(identifier=identifier, color=self.getColorSTR()))


##############################################
#
##############################################
class Model:
    def __init__(self):
        self.vertexList = []
        self.normalList = []
        self.indexList = []
        
        self.name = self.wygenerujID(5, 5)
        self.material = Material()
        
    def addFace(self, face):
        mesh = self.meshFace(face)
        for pp in mesh.Facets:
            num = len(self.vertexList)
            for kk in pp.Points:
                self.vertexList.append(point3D(kk))
            self.indexList.append(indexListPoint3D([num, num + 1, num + 2]))
        
    def meshFace(self, shape):
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
        
    def wygenerujID(self, ll, lc):
        ''' generate random model name '''
        numerID = ""

        for i in range(ll):
            numerID += random.choice('abcdefghij')
        numerID += "_"
        for i in range(lc):
            numerID += str(random.randrange(0, 99, 1))
        
        return numerID

    def write(self, file):
        file.write(u'''
<Object Identifier="./Models/{name}" Label="Default Model" Name="{name}" Type="Model"> 
<Object Identifier="Triangular Mesh" Label="Triangular Mesh" Name="" Type="Surface">
<Parameter Name="Vertex List" Type="Point3D List" Value="{pointListSize}">\n'''.format(name=self.name, pointListSize=len(self.vertexList)))

        for i in self.vertexList:
            file.write('{0}\n'.format(i))

        file.write(u'''</Parameter>
<Parameter Name="Normal List" Type="Point3D List" Value="{pointListSize}">\n'''.format(pointListSize=len(self.vertexList)))
        file.write('<P xyz="0 0 -1"/>\n' * len(self.vertexList))
        file.write(u'''</Parameter>
<Parameter Name="Index List" Type="Triangle Index List" Value="{indexListSize}">\n'''.format(indexListSize=len(self.indexList)))

        for i in self.indexList:
            file.write('{0}\n'.format(i))

        file.write(u'''</Parameter>\n</Object>\n''')

        self.material.write(file)
        
        file.write('</Object>\n')


##############################################
#
##############################################
class Camera:
    def __init__(self):
        self.name = "Camera_1"
        self.f_number = "Pinhole"
        self.resolution = "1024x768"
        self.focusDistance = "1"
        self.lensSamples = "3"
        self.blades = "3"
        self.diaphragm = "Circular"
        self.projection = "Planar"
        self.orientation = None
        self.position = None

    def addParameter(self, name, pType, value):
        return '<Parameter Name="{0}" Type="{1}" Value="{2}"/>\n'.format(name, pType, value)
        
    def write(self, file):
        r = self.orientation
        x = "%.4f" % (self.position[0] * 0.001)
        y = "%.4f" % (self.position[1] * 0.001)
        z = "%.4f" % (self.position[2] * 0.001)
        
        file.write('<Object Identifier="./Cameras/{0}" Label="Pinhole Camera" Name="{0}" Type="Camera">\n'.format(self.name))
        file.write(self.addParameter("Resolution", "String", self.resolution))
        file.write(self.addParameter("Frame", "Transform", "{0} {1} {2} {3} {4} {5} {6} {7} {8} {9} {10} {11}".format(r[0][0], r[1][0], float(r[2][0]) * -1, x, r[0][1], r[1][1], float(r[2][1]) * -1, y, r[0][2], r[1][2], float(r[2][2]) * -1, z)))
        file.write(self.addParameter("Focus Distance", "Real", self.focusDistance))
        file.write(self.addParameter("f-number", "String", self.f_number))
        file.write(self.addParameter("Lens Samples", "Integer",self.lensSamples ))
        file.write(self.addParameter("Blades", "Integer", self.blades))
        file.write(self.addParameter("Diaphragm", "String", self.diaphragm))
        file.write(self.addParameter("Projection", "String", self.projection))
        file.write('</Object>\n')


##############################################
#
##############################################
class exportTokerkythea:
    def __init__(self):
        self.models = []
        self.cameras = []
        modelsMultiColors = False

    def write(self, file, name):
        try:
            file = builtins.open(file, "w")
            #
            self.writeHeader(file, name)
            
            if self.modelsMultiColors:
                for i, j in self.models.items():
                    file.write('<Object Identifier="./Models/{0}" Label="Default Model" Name="{0}" Type="Model">\n'.format(i.encode('utf-8')))
                    for k in j:
                        k.write(file)
                    file.write('</Object>\n')
            else:
                for i in self.models.values():
                    i.write(file)
            # CAMERA
            #activeCamera = self.cameras[0][0].name
            for i in self.cameras:
                i[0].write(file)
                #if i[1]:
                #    activeCamera = i[0].name
            #
            #file.write('<Parameter Name="./Cameras/Active" Type="String" Value="{0}"/>\n'.format(activeCamera))

            self.writeFooter(file, name)
        except Exception as e:
            FreeCAD.Console.PrintWarning("{0} \n".format(e))
            return
        
        FreeCAD.Console.PrintWarning("Export finished successfully.\n")

    def writeHeader(self, file, name):
        file.write('''<Root Label="Kernel" Name="" Type="Kernel">
<Object Identifier="./Ray Tracers/Metropolis Light Transport" Label="Metropolis Light Transport" Name="Metropolis Light Transport" Type="Ray Tracer">
</Object>
<Object Identifier="./Environments/Octree Environment" Label="Octree Environment" Name="Octree Environment" Type="Environment">
</Object>
<Object Identifier="./Filters/Simple Tone Mapping" Label="Simple Tone Mapping" Name="" Type="Filter">
</Object>
<Object Identifier="./Scenes/{0}" Label="Default Scene" Name="{0}" Type="Scene">\n
'''.format(name.encode('utf-8')))

    def writeFooter(self, file, name):
        file.write('''</Object>
<Parameter Name="Mip Mapping" Type="Boolean" Value="1"/>
<Parameter Name="./Interfaces/Active" Type="String" Value="Null Interface"/>
<Parameter Name="./Modellers/Active" Type="String" Value="XML Modeller"/>
<Parameter Name="./Image Handlers/Active" Type="String" Value="Free Image Support"/>
<Parameter Name="./Ray Tracers/Active" Type="String" Value="Metropolis Light Transport"/>
<Parameter Name="./Irradiance Estimators/Active" Type="String" Value="Null Irradiance Estimator"/>
<Parameter Name="./Direct Light Estimators/Active" Type="String" Value="Null Direct Light Estimator"/>
<Parameter Name="./Environments/Active" Type="String" Value="Octree Environment"/>
<Parameter Name="./Filters/Active" Type="String" Value="Simple Tone Mapping"/>
<Parameter Name="./Scenes/Active" Type="String" Value="{0}"/>
<Parameter Name="./Libraries/Active" Type="String" Value="Material Librarian"/>
</Root>'''.format(name.encode('utf-8')))


##############################################
#
##############################################

class exportToKerkytheaGui(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        #
        self.form = self
        self.form.setWindowTitle(u"Export to Kerkythea v1.2")
        #
        tab = QtGui.QTabWidget()
        tab.addTab(self.tabGeneral(), u'General')
        tab.addTab(self.tabCamera(), u'Cameras')
        tab.addTab(self.tabLight(), u'Lights')
        #
        lay = QtGui.QVBoxLayout(self)
        lay.addWidget(tab)
        #
        self.connect(self.exportObjectsAs_YES, QtCore.SIGNAL("clicked ()"), self.setColors)
        self.connect(self.exportObjectsAs_NO, QtCore.SIGNAL("clicked ()"), self.setColors)
    
    def accept(self):
        if self.exportObjects_All.isChecked():
            projectObjects = [i for i in FreeCAD.ActiveDocument.Objects if i.ViewObject.Visibility]
        elif self.exportObjects_Selected.isChecked():
            projectObjects = []
            for i in FreeCADGui.Selection.getSelection():
                if i.ViewObject.Visibility and i not in projectObjects:
                    projectObjects.append(i)
        
        if len(projectObjects) == 0:
            FreeCAD.Console.PrintWarning("No objects found\n")
            return
        #

        projectModels = {}
        for i in projectObjects:  # objects in document
            try:
                objectColors = i.ViewObject.DiffuseColor
                shape = i.Shape.Faces
            except:
                continue
                
            for j in range(len(i.Shape.Faces)):  # object faces
                # get face color
                if len(objectColors) == len(i.Shape.Faces):
                    modelType = objectColors[j]
                else:
                    modelType = objectColors[0]
                #
                if self.exportObjectsAs_YES.isChecked():
                    modelID = str(modelType)
                else:
                    modelID = i.Label
                #
                if self.exportObjectColor_SinCol.isChecked():
                    modelsMultiColors = False

                    if not modelID in projectModels:
                        model = Model()
                        if self.exportObjectsAs_NO.isChecked():
                            model.name = modelID
                        model.material.diffuse = Texture(modelType)
                        projectModels[modelID] = model
                    else:
                        model = projectModels[modelID]
                else:
                    modelsMultiColors = True

                    if not modelID in projectModels:
                        projectModels[modelID] = []

                    model = Model()
                    model.name = 'Face {0}'.format(j)
                    model.material.diffuse = Texture(modelType)
                    if self.exportObjectColor_Gray.isChecked():
                        model.material.diffuse.toGrayscale()
                    projectModels[modelID].append(model)
                #
                model.addFace(i.Shape.Faces[j])

        exporter = exportTokerkythea()
        exporter.modelsMultiColors = modelsMultiColors
        exporter.models = projectModels
        # CAMERAS
        for i in range(self.camerasList.count()):
            item = self.camerasList.item(i)
            
            camera = Camera()
            camera.name = item.text()
            camera.f_number = item.data(QtCore.Qt.UserRole)['fNumber']
            camera.resolution = item.data(QtCore.Qt.UserRole)['resolution']
            camera.focusDistance = item.data(QtCore.Qt.UserRole)['focusDistance']
            camera.lensSamples = item.data(QtCore.Qt.UserRole)['lensSamples']
            camera.blades = item.data(QtCore.Qt.UserRole)['blades']
            camera.diaphragm = item.data(QtCore.Qt.UserRole)['diaphragm']
            camera.projection = item.data(QtCore.Qt.UserRole)['projection']
            camera.orientation = item.data(QtCore.Qt.UserRole)['orientation']
            camera.position = item.data(QtCore.Qt.UserRole)['position']
            
            exporter.cameras.append([camera, True])
        #
        exporter.write(self.filePath.text(), FreeCAD.ActiveDocument.Label)
        return True
    
    def showCamera(self, item):
        FreeCADGui.ActiveDocument.ActiveView.setCamera(item.data(QtCore.Qt.UserRole)['cam'])
        
        self.cameraName.setText(item.text())
        self.resolution.setCurrentIndex(self.resolution.findText(item.data(QtCore.Qt.UserRole)['resolution']))
        self.fNumber.setCurrentIndex(self.fNumber.findText(item.data(QtCore.Qt.UserRole)['fNumber']))
        self.focusDistance.setValue(item.data(QtCore.Qt.UserRole)['focusDistance'])
        self.lensSamples.setValue(item.data(QtCore.Qt.UserRole)['lensSamples'])
        self.projection.setCurrentIndex(self.projection.findText(item.data(QtCore.Qt.UserRole)['projection']))
        self.diaphragm.setCurrentIndex(self.diaphragm.findText(item.data(QtCore.Qt.UserRole)['diaphragm']))
        self.blades.setValue(item.data(QtCore.Qt.UserRole)['blades'])
    
    def setColors(self):
        if self.exportObjectsAs_YES.isChecked():
            self.exportObjectColor_SinCol.setChecked(True)
            self.exportObjectColorBox.setDisabled(True)
        else:
            self.exportObjectColorBox.setDisabled(False)

    def tabGeneral(self):
        self.patherror = QtGui.QLabel('')
        
        self.filePath = QtGui.QLineEdit('')
        self.connect(self.filePath, QtCore.SIGNAL("textChanged (const QString&)"), self.changePathFInfo)
        self.filePath.setText(os.path.join(os.path.expanduser("~"), 'Unnamed.xml'))
        self.filePath.setReadOnly(True)
        
        changePath = QtGui.QPushButton('...')
        changePath.setFixedWidth(30)
        self.connect(changePath, QtCore.SIGNAL("clicked ()"), self.changePathF)
        
        generalBox = QtGui.QGroupBox(u'General')
        generalBoxLay = QtGui.QGridLayout(generalBox)
        generalBoxLay.addWidget(QtGui.QLabel(u'Path           '), 0, 0, 1, 1)
        generalBoxLay.addWidget(self.filePath, 0, 1, 1, 2)
        generalBoxLay.addWidget(changePath, 0, 3, 1, 1)
        generalBoxLay.addWidget(self.patherror, 1, 0, 1, 4)

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
        #
        self.exportObjectsAs_YES = QtGui.QRadioButton(u'Yes')
        self.exportObjectsAs_YES.setChecked(True)
        self.exportObjectsAs_NO = QtGui.QRadioButton(u'No')
        
        exportObjectsAsBox = QtGui.QGroupBox(u'Group models by color')
        exportObjectsAsBoxLay = QtGui.QVBoxLayout(exportObjectsAsBox)
        exportObjectsAsBoxLay.addWidget(self.exportObjectsAs_YES)
        exportObjectsAsBoxLay.addWidget(self.exportObjectsAs_NO)
        #
        self.exportObjectColor_MulCol = QtGui.QRadioButton(u'Multi colors')
        self.exportObjectColor_Gray = QtGui.QRadioButton(u'Grayscale')
        self.exportObjectColor_SinCol = QtGui.QRadioButton(u'Single color (random)')
        self.exportObjectColor_SinCol.setChecked(True)

        self.exportObjectColorBox = QtGui.QGroupBox(u'Colors')
        self.exportObjectColorBox.setDisabled(True)
        exportObjectColorBoxLay = QtGui.QVBoxLayout(self.exportObjectColorBox)
        exportObjectColorBoxLay.addWidget(self.exportObjectColor_MulCol)
        exportObjectColorBoxLay.addWidget(self.exportObjectColor_Gray)
        exportObjectColorBoxLay.addWidget(self.exportObjectColor_SinCol)
        #####
        widget = QtGui.QWidget()
        
        lay = QtGui.QGridLayout(widget)
        lay.addWidget(generalBox, 0, 0, 1, 4)
        lay.addWidget(separator(), 1, 0, 1, 4)
        lay.addWidget(exportObjectsBox, 2, 0, 1, 4)
        lay.addWidget(exportObjectsAsBox, 3, 0, 1, 2)
        lay.addWidget(self.exportObjectColorBox, 3, 2, 1, 2)
        lay.setRowStretch(10, 10)
        return widget
        
    def tabLight(self):
        pass
    
    def tabCamera(self):
        self.resolution = QtGui.QComboBox()
        self.resolution.addItems(['200x200', '320x200', '320x240', '500x500', '512x384', '640x480', '768x576', '800x600', '1024x768', '1280x1024', '1600x1200', '2048x1536', '2816x2112'])
        self.resolution.setCurrentIndex(self.resolution.findText('1024x768'))

        self.cameraName = QtGui.QLineEdit(u'Camera 1')

        filmBox = QtGui.QGroupBox(u'General')
        filmBoxLay = QtGui.QGridLayout(filmBox)
        filmBoxLay.addWidget(QtGui.QLabel(u'Camera name'), 0, 0, 1, 1)
        filmBoxLay.addWidget(self.cameraName, 0, 1, 1, 1)
        filmBoxLay.addWidget(QtGui.QLabel(u'Resolution'), 1, 0, 1, 1)
        filmBoxLay.addWidget(self.resolution, 1, 1, 1, 1)

        filmBoxLay.setHorizontalSpacing(50)
        #
        self.fNumber = QtGui.QComboBox()
        self.fNumber.addItems(['1', '1.4', '2', '2.8', '4', '5.6', '8', '16', '22', 'Pinhole'])
        self.fNumber.setCurrentIndex(self.fNumber.findText('Pinhole'))

        self.focusDistance = QtGui.QDoubleSpinBox()
        self.focusDistance.setValue(1.0)
        self.focusDistance.setRange(0.0, 1000.0)

        self.lensSamples = QtGui.QSpinBox()
        self.lensSamples.setValue(3)
        self.lensSamples.setRange(0, 1000)
        #
        self.projection = QtGui.QComboBox()
        self.projection.addItems(['Planar', 'Cylindrical', 'Spherical', 'Parallel'])
        self.projection.setCurrentIndex(self.projection.findText('Planar'))

        self.diaphragm = QtGui.QComboBox()
        self.diaphragm.addItems(['Circular', 'Polygonal'])
        self.diaphragm.setCurrentIndex(self.diaphragm.findText('Circular'))
        
        self.blades = QtGui.QSpinBox()
        self.blades.setValue(3)
        self.blades.setRange(3, 1000)
        #
        layOptions = QtGui.QGridLayout()
        layOptions.addWidget(QtGui.QLabel(u'<b>Lens</b>'), 0, 0, 1, 1)
        layOptions.addWidget(QtGui.QLabel(u'f-number'), 0, 1, 1, 1, QtCore.Qt.AlignHCenter)
        layOptions.addWidget(QtGui.QLabel(u'Focus Distance'), 0, 2, 1, 1, QtCore.Qt.AlignHCenter)
        layOptions.addWidget(QtGui.QLabel(u'Lens Samples'), 0, 3, 1, 1, QtCore.Qt.AlignHCenter)
        layOptions.addWidget(self.fNumber, 1, 1, 1, 1)
        layOptions.addWidget(self.focusDistance, 1, 2, 1, 1)
        layOptions.addWidget(self.lensSamples, 1, 3, 1, 1)
        layOptions.addWidget(QtGui.QLabel(u'<b>Geometry</b>'), 2, 0, 1, 1)
        layOptions.addWidget(QtGui.QLabel(u'Projection'), 2, 1, 1, 1, QtCore.Qt.AlignHCenter)
        layOptions.addWidget(QtGui.QLabel(u'Diaphragm'), 2, 2, 1, 1, QtCore.Qt.AlignHCenter)
        layOptions.addWidget(QtGui.QLabel(u'Blades'), 2, 3, 1, 1, QtCore.Qt.AlignHCenter)
        layOptions.addWidget(self.projection, 3, 1, 1, 1)
        layOptions.addWidget(self.diaphragm, 3, 2, 1, 1)
        layOptions.addWidget(self.blades, 3, 3, 1, 1)
        layOptions.setSpacing(15)
        #
        # buttons
        buttonAdd = QtGui.QPushButton(u'Add')
        self.connect(buttonAdd, QtCore.SIGNAL("clicked ()"), self.addCamera)
        buttonRemove = QtGui.QPushButton(u'Remove')
        self.connect(buttonRemove, QtCore.SIGNAL("clicked ()"), self.removeCamera)
        buttonUpdate = QtGui.QPushButton(u'Update')
        self.connect(buttonUpdate, QtCore.SIGNAL("clicked ()"), self.updateCamera)
        
        layButtons = QtGui.QHBoxLayout()
        layButtons.setContentsMargins(0, 0, 0, 0)
        layButtons.addWidget(buttonAdd)
        layButtons.addWidget(buttonRemove)
        layButtons.addWidget(buttonUpdate)
        #
        self.camerasList = QtGui.QListWidget()
        self.camerasList.setStyleSheet('border:1px solid rgb(237, 237, 237);')
        self.connect(self.camerasList, QtCore.SIGNAL("itemClicked (QListWidgetItem*)"), self.showCamera)
        #####
        widget = QtGui.QWidget()
        lay = QtGui.QVBoxLayout(widget)
        lay.addWidget(filmBox)

        lay.addLayout(layOptions)
        lay.addItem(QtGui.QSpacerItem(1, 5))
        lay.addWidget(separator())
        lay.addItem(QtGui.QSpacerItem(1, 5))
        lay.addLayout(layButtons)
        lay.addItem(QtGui.QSpacerItem(1, 5))
        lay.addWidget(self.camerasList)
        return widget
    
    def addCamera(self):
        cameraName = self.cameraName.text().strip()
        
        if cameraName == '':
            return
        
        if len(self.camerasList.findItems(cameraName, QtCore.Qt.MatchExactly)) == 0:
            item = QtGui.QListWidgetItem(cameraName)
            item.setData(QtCore.Qt.UserRole, self.cameraParam())
            self.camerasList.addItem(item)
        else:
            FreeCAD.Console.PrintWarning("Camera already exist.\n")
    
    def cameraParam(self):
        cam = FreeCADGui.ActiveDocument.ActiveView.getCameraNode()
        camPos = cam.position.getValue()
        cO = cam.orientation.getValue().getMatrix()
        
        cameraPara = {
            'resolution': self.resolution.currentText(),
            'fNumber': self.fNumber.currentText(),
            'focusDistance': self.focusDistance.value(),
            'lensSamples': self.lensSamples.value(),
            'projection': self.projection.currentText(),
            'diaphragm': self.diaphragm.currentText(),
            'blades': self.blades.value(),
            'orientation': [[cO[0][0], cO[0][1], cO[0][2]], [cO[1][0], cO[1][1], cO[1][2]], [cO[2][0], cO[2][1], cO[2][2]]],
            'position': (camPos[0], camPos[1], camPos[2]),
            'cam': FreeCADGui.ActiveDocument.ActiveView.getCamera(),
        }
        
        return cameraPara
        
    def removeCamera(self):
        if self.camerasList.currentRow() != -1:
            dial = QtGui.QMessageBox()
            dial.setText(u"Delete selected camera?")
            dial.setWindowTitle("Caution!")
            dial.setIcon(QtGui.QMessageBox.Question)
            delete_YES = dial.addButton('Yes', QtGui.QMessageBox.YesRole)
            dial.addButton('No', QtGui.QMessageBox.RejectRole)
            dial.exec_()
            
            if dial.clickedButton() == delete_YES:
                self.camerasList.takeItem(self.camerasList.currentRow())
        
    def updateCamera(self):
        if self.camerasList.currentRow() != -1:
            cameraName = self.cameraName.text().strip()
            sameItems = self.camerasList.findItems(cameraName, QtCore.Qt.MatchExactly)
            
            try:
                if len(sameItems) != 0 and sameItems[0] != self.camerasList.currentItem():
                    FreeCAD.Console.PrintWarning("Camera already exist.\n")
                    return
            except Exception as e:
                pass
            
            item = self.camerasList.currentItem()
            item.setText(cameraName)
            item.setData(QtCore.Qt.UserRole, self.cameraParam())
    
    def changePathFInfo(self):
        if os.path.exists(self.filePath.text()):
            self.patherror.setText('<span style="font-weight:bold; color: red;">You will overwrite existing file!</span>')
        else:
            self.patherror.setText('')
    
    def changePathF(self):
        path = QtGui.QFileDialog().getSaveFileName(self, u"Save as", os.path.expanduser("~"), "*.xml")

        fileName = path[0]
        if not fileName == "":
            if not fileName.endswith('xml'):
                fileName = fileName + '.xml'
            self.filePath.setText(fileName)
            self.changePathFInfo()


class separator(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)
        #
        self.setFrameShape(QtGui.QFrame.HLine)
        self.setFrameShadow(QtGui.QFrame.Sunken)
        self.setLineWidth(1)
