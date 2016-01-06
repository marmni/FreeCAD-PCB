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
if FreeCAD.GuiUp:
    from PySide import QtGui, QtCore
import Part
import os


#***********************************************************************
#*                             GUI
#***********************************************************************
class createAssemblyGui(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        self.form = self
        self.form.setWindowTitle(u"Assembly")
        self.form.setWindowIcon(QtGui.QIcon(":/data/img/:/data/img/asmMain.png"))
        ########################
        # file
        ########################
        self.fileName = QtGui.QLineEdit()
        self.fileName.setReadOnly(True)
        
        pickFile = QtGui.QPushButton('...')
        self.connect(pickFile, QtCore.SIGNAL("released ()"), self.chooseFile)
        ########################
        # rotation / shift
        ########################
        self.pozX = QtGui.QDoubleSpinBox()
        self.pozX.setRange(-1000, 1000)
        self.pozX.setSuffix(" mm")
        self.pozY = QtGui.QDoubleSpinBox()
        self.pozY.setRange(-1000, 1000)
        self.pozY.setSuffix(" mm")
        self.pozZ = QtGui.QDoubleSpinBox()
        self.pozZ.setRange(-1000, 1000)
        self.pozZ.setSuffix(" mm")
        self.pozRX = QtGui.QDoubleSpinBox()
        self.pozRX.setRange(-1000, 1000)
        self.pozRX.setSuffix(" deg")
        self.pozRY = QtGui.QDoubleSpinBox()
        self.pozRY.setRange(-1000, 1000)
        self.pozRY.setSuffix(" deg")
        self.pozRZ = QtGui.QDoubleSpinBox()
        self.pozRZ.setRange(-1000, 1000)
        self.pozRZ.setSuffix(" deg")
        ukladWspolrzednych = QtGui.QLabel("")
        ukladWspolrzednych.setPixmap(QtGui.QPixmap(":/data/img/uklad.png"))
        
        layWspolrzedne = QtGui.QGridLayout()
        layWspolrzedne.setContentsMargins(0, 10, 0, 20)
        layWspolrzedne.addWidget(ukladWspolrzednych, 0, 0, 6, 1, QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        layWspolrzedne.addWidget(QtGui.QLabel("X"), 0, 1, 1, 1, QtCore.Qt.AlignRight)
        layWspolrzedne.addWidget(self.pozX, 0, 2, 1, 1, QtCore.Qt.AlignTop)
        layWspolrzedne.addWidget(QtGui.QLabel("Y"), 1, 1, 1, 1, QtCore.Qt.AlignRight)
        layWspolrzedne.addWidget(self.pozY, 1, 2, 1, 1, QtCore.Qt.AlignTop)
        layWspolrzedne.addWidget(QtGui.QLabel("Z"), 2, 1, 1, 1, QtCore.Qt.AlignRight)
        layWspolrzedne.addWidget(self.pozZ, 2, 2, 1, 1, QtCore.Qt.AlignTop)
        layWspolrzedne.addWidget(QtGui.QLabel("RX"), 3, 1, 1, 1, QtCore.Qt.AlignRight)
        layWspolrzedne.addWidget(self.pozRX, 3, 2, 1, 1, QtCore.Qt.AlignTop)
        layWspolrzedne.addWidget(QtGui.QLabel("RY"), 4, 1, 1, 1, QtCore.Qt.AlignRight)
        layWspolrzedne.addWidget(self.pozRY, 4, 2, 1, 1, QtCore.Qt.AlignTop)
        layWspolrzedne.addWidget(QtGui.QLabel("RZ"), 5, 1, 1, 1, QtCore.Qt.AlignRight)
        layWspolrzedne.addWidget(self.pozRZ, 5, 2, 1, 1, QtCore.Qt.AlignTop)
        layWspolrzedne.setRowStretch(6, 10)
        layWspolrzedne.setColumnStretch(2, 10)
        
        ########################
        # layouts
        ########################
        mainLay = QtGui.QGridLayout()
        mainLay.addWidget(QtGui.QLabel(u"File"), 0, 0, 1, 1)
        mainLay.addWidget(self.fileName, 0, 1, 1, 1)
        mainLay.addWidget(pickFile, 0, 2, 1, 1)
        mainLay.addLayout(layWspolrzedne, 1, 0, 1, 3)
        mainLay.setColumnStretch(1, 10)
        self.setLayout(mainLay)
    
    def chooseFile(self):
        dial = QtGui.QFileDialog().getOpenFileName(self, u"Choose file", "~", "*.fcstd")
        if dial:
            self.fileName.setText(dial[0])
        
    def accept(self):
        if self.fileName.text().strip() == '':
            FreeCAD.Console.PrintWarning("Mandatory field is empty!\n")
        else:
            asm = createAssembly()
            asm.fileName = self.fileName.text().strip()
            asm.x = self.pozX.value()
            asm.y = self.pozY.value()
            asm.z = self.pozZ.value()
            asm.rx = self.pozRX.value()
            asm.ry = self.pozRY.value()
            asm.rz = self.pozRZ.value()
            asm.create()
            
            return True

#***********************************************************************
#*                             CONSOLE
#***********************************************************************
class createAssembly:
    def __init__(self):
        self.fileName = ''
        self.x = 0
        self.y = 0
        self.z = 0
        self.rx = 0
        self.ry = 0
        self.rz = 0
    
    def create(self):
        if self.fileName == '' :
            FreeCAD.Console.PrintWarning("Mandatory field is empty!\n")
            return
        if not self.fileName.endswith('.fcstd'):
            FreeCAD.Console.PrintWarning("Wrong file format!\n")
            return
        ##
        mainFile = FreeCAD.ActiveDocument.Label
        #
        a = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", "{0}".format(os.path.basename(self.fileName).split('.')[0]))
        mainAssemblyObject(a)
        a.File = self.fileName
        viewProviderMainAssemblyObject(a.ViewObject)
        
        #pos = FreeCAD.Placement()
        #pos.Base.x = self.x
        #pos.Base.y = self.y
        #pos.Base.z = self.z
        #a.Placement = pos
        a.X = self.x
        a.Y = self.y
        a.Z = self.z
        #
        #FreeCAD.setActiveDocument(mainFile)
        FreeCADGui.ActiveDocument = FreeCADGui.getDocument(mainFile)
        
        FreeCADGui.ActiveDocument.activeView().viewAxometric()
        FreeCADGui.ActiveDocument.activeView().fitAll()
        FreeCAD.ActiveDocument.recompute()


def updateAssembly():
    mainFile = FreeCAD.ActiveDocument.Label
    for i in FreeCADGui.Selection.getSelection():
        if hasattr(i, "Proxy") and hasattr(i, "Type") and i.Proxy.Type == 'assemblyMain':
            i.Proxy.updateParts(i)
            i.Proxy.updatePosition(i)
    #
    FreeCAD.setActiveDocument(mainFile)
    FreeCADGui.ActiveDocument = FreeCADGui.getDocument(mainFile)
    
    FreeCADGui.ActiveDocument.activeView().viewAxometric()
    FreeCADGui.ActiveDocument.activeView().fitAll()
    FreeCAD.ActiveDocument.recompute()
    
def checkFile(fileName):
    try:
        return [FreeCAD.open(fileName), True]
    except Exception, e: # file is already open
        for i in FreeCAD.listDocuments().values():
            if i.FileName == fileName:
                return [FreeCAD.getDocument(i.Label), False]
        
    return [None, False]

#***********************************************************************
#*                             OBJECT
#***********************************************************************
class childAssemblyObject:
    def __init__(self, obj):
        self.Type = 'assemblyChild'
        obj.Proxy = self
        
        obj.setEditorMode("Placement", 2)
        #
        self.mainX = 0
        self.mainY = 0
        self.mainZ = 0
        self.mainRX = 0
        self.mainRY = 0
        self.mainRZ = 0
        self.angle = 0
    
    def onChanged(self, fp, prop):
        fp.setEditorMode("Placement", 2)
    
    def execute(self, obj):
        pass
    
    def updateRotation(self, obj, prop, rot, center):
        try:
            # placement object to 0, 0, ?
            sX = obj.Placement.Base.x - center[0]
            sY = obj.Placement.Base.y - center[1]
            
            obj.Placement.Base.x = sX
            obj.Placement.Base.y = sY
            
            # rotate
            sX = obj.Shape.BoundBox.Center.x
            sY = obj.Shape.BoundBox.Center.y
            
            
            pla = FreeCAD.Placement(obj.Placement.Base, FreeCAD.Rotation(rot[0], rot[1], rot[2]), FreeCAD.Base.Vector(sX, sY, 0))
            obj.Placement = pla
            
            
            self.mainRX = rot[0]
            self.mainRY = rot[1]
            self.mainRZ = rot[2]
            
        except Exception, e:
            FreeCAD.Console.PrintWarning("rot. {0} \n".format(e))
        
        
        
        
        #pla = FreeCAD.Placement(obj.Placement.Base, FreeCAD.Rotation(rot[0] - self.mainRX, rot[1] - self.mainRY, rot[2] - self.mainRZ), FreeCAD.Base.Vector(center[0], center[1], center[2]))
        #obj.Placement = pla
        
        #self.mainRX = rot[0]
        #self.mainRY = rot[1]
        #self.mainRZ = rot[2]
        
        
        #if prop == 'RX':
            #shape = obj.Shape.copy()
            #shape.Placement = obj.Placement
            #shape.rotate(center, (1.0, 0.0, 0.0), rotation[0] - self.mainRX)
            #obj.Placement = shape.Placement
            
            #self.mainRX = rotation[0]
        #elif prop == 'RY':
            #shape = obj.Shape.copy()
            #shape.Placement = obj.Placement
            #shape.rotate(center, (0.0, 1.0, 0.0), rotation[1] - self.mainRY)
            #obj.Placement = shape.Placement
            
            #self.mainRY = rotation[1]
        #else:  # RZ
            #shape = obj.Shape.copy()
            #shape.Placement = obj.Placement
            #shape.rotate(center, (0.0, 0.0, 1.0), rotation[2] - self.mainRZ)
            #obj.Placement = shape.Placement
            
            #self.mainRZ = rotation[2]
    
    def updatePosition(self, obj, parent):
        try:
            placement = parent
            
            obj.Placement.Base.x = obj.Placement.Base.x + (placement[0] - self.mainX)
            obj.Placement.Base.y = obj.Placement.Base.y + (placement[1] - self.mainY)
            obj.Placement.Base.z = obj.Placement.Base.z + (placement[2] - self.mainZ)
            
            self.mainX = placement[0]
            self.mainY = placement[1]
            self.mainZ = placement[2]
        except Exception, e:
            FreeCAD.Console.PrintWarning("2. {0} \n".format(e))
    
    def __getstate__(self):
        return [self.Type, self.mainX, self.mainY, self.mainZ, self.mainRX, self.mainRY, self.mainRZ, self.angle]

    def __setstate__(self, state):
        if state:
            self.Type = state[0]
            self.mainX = state[1]
            self.mainY = state[2]
            self.mainZ = state[3]
            self.mainRX = state[4]
            self.mainRY = state[5]
            self.mainRZ = state[6]
            self.angle = state[7]


class mainAssemblyObject:
    def __init__(self, obj):
        self.Type = 'assemblyMain'
        obj.Proxy = self
        self.Object = obj
        
        obj.addProperty("App::PropertyFile", "File", "Base", "File").File = ""
        #obj.addProperty("App::PropertyPlacement", "Placement", "Base", "Placement")
        obj.addProperty("App::PropertyDistance", "X", "PCB", "X").X = 0
        obj.addProperty("App::PropertyDistance", "Y", "PCB", "Y").Y = 0
        obj.addProperty("App::PropertyDistance", "Z", "PCB", "Z").Z = 0
        obj.addProperty("App::PropertyAngle", "RX", "PCB", "RX").RX = 0
        obj.addProperty("App::PropertyAngle", "RY", "PCB", "RY").RY = 0
        obj.addProperty("App::PropertyAngle", "RZ", "PCB", "RZ").RZ = 0
    
    def execute(self, obj):
        pass
    
    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state
    
    def updateParts(self, obj):
        if obj.File.strip() != '':
            mainFile = FreeCAD.ActiveDocument
            # delete old parts
            try:
                for i in obj.OutList:
                    FreeCAD.ActiveDocument.removeObject(i.Name)
            except Exception, e:
                FreeCAD.Console.PrintWarning("7. {0} \n".format(e))
            # load new parts
            newFile = checkFile(obj.File)
            if not newFile[0]:
                return

            for i in newFile[0].Objects:
                if not i.ViewObject.Visibility:
                    continue
                
                if hasattr(i, "Proxy") and hasattr(i, "Type") and i.Proxy.Type in [['PCBannotation'], 'PCBpart_E']:
                    continue
                
                if hasattr(i, "Shape") and not i.isDerivedFrom("Sketcher::SketchObject"):
                    try:
                        child = mainFile.addObject("Part::FeaturePython", "{0}".format(i.Label))
                        childAssemblyObject(child)
                        child.Shape = i.Shape
                        #child.Proxy.MainPlacement = obj.Placement
                        viewProviderChildAssemblyObject(child.ViewObject)
                        child.ViewObject.DiffuseColor = i.ViewObject.DiffuseColor
                        
                        obj.addObject(child)
                    except Exception, e:
                        FreeCAD.Console.PrintWarning("1. {0} \n".format(e))
            if newFile[1]:
                FreeCAD.closeDocument(newFile[0].Label)
            
            FreeCAD.setActiveDocument(mainFile.Label)
            FreeCADGui.ActiveDocument = FreeCADGui.getDocument(mainFile.Label)
            
            FreeCADGui.ActiveDocument.activeView().viewAxometric()
            FreeCADGui.ActiveDocument.activeView().fitAll()
            FreeCAD.ActiveDocument.recompute()
            
            # center of assembly
            #bbc =  Part.makeCompound([i.Shape for i in obj.OutList if i.ViewObject.Visibility]).BoundBox.Center
            #self.center = (bbc[0], bbc[1], bbc[2])

    def updatePosition(self, fp):
        try:
            for i in fp.OutList:
                i.Proxy.updatePosition(i, [fp.X.Value, fp.Y.Value, fp.Z.Value])
        except Exception, e:
            FreeCAD.Console.PrintWarning("3. {0} \n".format(e))
    
    def updateRotation(self, fp, prop):
        try:
            #boundBox = Part.makeCompound([i.Shape for i in fp.OutList])
            #center = (boundBox.BoundBox.XLength / 2.0, boundBox.BoundBox.YLength / 2.0, boundBox.BoundBox.ZLength / 2.0)
            #center = [fp.X.Value, fp.Y.Value, fp.Z.Value]
            
            #center = [self.center[0] + fp.X.Value, self.center[1] + fp.Y.Value, self.center[2] + fp.Z.Value]
            center = FreeCAD.ActiveDocument.Board.Shape.BoundBox.Center
            center = [center.x, center.y, center.z]
            
            for i in fp.OutList:
                #updateRotation(self, obj, prop, rotation, center):
                i.Proxy.updateRotation(i, prop, [fp.RX.Value, fp.RY.Value, fp.RZ.Value], center)
        except Exception, e:
            FreeCAD.Console.PrintWarning("3. {0} \n".format(e))
    
    def onChanged(self, fp, prop):
        try:
            if prop == "File":
                self.updateParts(fp)
            elif prop in ['X', 'Y', 'Z']:
                self.updatePosition(fp)
            elif prop in ['RX', 'RY', 'RZ']:
                self.updateRotation(fp, prop)
        except:
            #FreeCAD.Console.PrintWarning("3. {0}\n".format(e))
            pass


class viewProviderMainAssemblyObject:
    def __init__(self, obj):
        obj.Proxy = self
        self.Object = obj.Object

    def attach(self, obj):
        ''' Setup the scene sub-graph of the view provider, this method is mandatory '''
        self.Object = obj.Object

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def onChanged(self, vp, prop):
        ''' Print the name of the property that has changed '''
        if hasattr(vp, "AngularDeflection"):
            vp.setEditorMode("AngularDeflection", 2)
        
        if prop == 'Visibility':
            for i in vp.Object.OutList:
                i.ViewObject.Visibility = vp.Visibility

    def getIcon(self):
        ''' Return the icon in XMP format which will appear in the tree view. This method is optional
        and if not defined a default icon is shown.
        '''
        return ":/data/img/asmMain.png"


class viewProviderChildAssemblyObject:
    def __init__(self, obj):
        obj.Proxy = self
        self.Object = obj.Object

    def attach(self, obj):
        ''' Setup the scene sub-graph of the view provider, this method is mandatory '''
        self.Object = obj.Object

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def onChanged(self, vp, prop):
        ''' Print the name of the property that has changed '''
        vp.setEditorMode("LineColor", 2)
        vp.setEditorMode("DrawStyle", 2)
        vp.setEditorMode("LineWidth", 2)
        vp.setEditorMode("PointColor", 2)
        vp.setEditorMode("PointSize", 2)
        vp.setEditorMode("Deviation", 2)
        vp.setEditorMode("Lighting", 2)
        vp.setEditorMode("BoundingBox", 2)
        vp.setEditorMode("Selectable", 2)
        vp.setEditorMode("DisplayMode", 2)
        if hasattr(vp, "AngularDeflection"):
            vp.setEditorMode("AngularDeflection", 2)
        vp.setEditorMode("ShapeColor", 2)

    def getIcon(self):
        ''' Return the icon in XMP format which will appear in the tree view. This method is optional
        and if not defined a default icon is shown.
        '''
        return ":/data/img/asmChild.svg"
