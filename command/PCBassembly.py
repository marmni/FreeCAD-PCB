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
        if not self.fileName.lower().endswith('.fcstd'):
            FreeCAD.Console.PrintWarning("Wrong file format!\n")
            return
        ##
        mainFile = FreeCAD.ActiveDocument.Label
        #
        a = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", "{0}".format(os.path.basename(self.fileName).split('.')[0]))
        mainAssemblyObject(a)
        a.File = self.fileName
        a.X = self.x
        a.Y = self.y
        a.Z = self.z
        a.RX = self.rx
        a.RY = self.ry
        a.RZ = self.rz
        viewProviderMainAssemblyObject(a.ViewObject)
        #
        try:
            FreeCADGui.ActiveDocument = FreeCADGui.getDocument(mainFile)
            FreeCADGui.ActiveDocument.activeView().viewAxometric()
            FreeCADGui.ActiveDocument.activeView().fitAll()
        except:
            pass
        FreeCAD.ActiveDocument.recompute()

def exportAssembly():
    doc = FreeCAD.ActiveDocument

    tmpobjs = []
    objs = []
    for i in doc.Objects:
        if not i.ViewObject.Visibility or not hasattr(i,'Shape') or not hasattr(i,'Proxy'):
            continue
        if hasattr(i.Proxy, "Type") and i.Proxy.Type in [['PCBannotation'], 'PCBpart_E']:
            continue
        if not i.isDerivedFrom("Sketcher::SketchObject") and len(i.Shape.Solids):

            # We are trying to combining all objects into one single compound object. However,
            # FreeCAD has a bug such that after compound, it will sometimes refuse to display
            # any color if the compound contain some overlapped pads with holes, even though
            # the color of all faces stored in DiffuseColor is still intact. 
            # 
            # The walkaround is to explode the pad object, and recombine all the solid inside
            # using 'Part::Compound'. 
            #
            # Only apply this trick to layerSilkObject(pads) and layerPathObject(path) and 
            # having holes.
            if not doc.Board.Display or len(i.Shape.Solids)==1 or \
                    (i.Proxy.__class__.__name__ != 'layerSilkObject' and \
                     i.Proxy.__class__.__name__ != 'layerPathObject') :
                objs.append(i)
                continue
            subobjs = []
            for j in i.Shape.Solids:
                tmpobj = doc.addObject('Part::Feature','obj')
                tmpobj.Shape = j
                tmpobj.ViewObject.ShapeColor = i.ViewObject.ShapeColor
                tmpobjs.append(tmpobj)
                subobjs.append(tmpobj)
            subobj = doc.addObject('Part::Compound','obj')
            subobj.Links = subobjs
            objs.append(subobj)
            tmpobjs.append(subobj)

    if not len(objs):
        FreeCAD.Console.PrintWarning('no parts found')
        return
    obj = doc.addObject('Part::Compound','Compound')
    obj.Links = objs
    doc.recompute()
    tmpobjs.append(obj)

    import random
    newDoc = FreeCAD.newDocument(doc.Name+'_'+str(random.randrange(10000,99999)))

    copy = newDoc.addObject('Part::Feature','Compound')
    copy.Shape = obj.Shape
    copy.ViewObject.DiffuseColor = obj.ViewObject.DiffuseColor
    copy.ViewObject.DisplayMode = 'Shaded'
    newDoc.recompute()

    for i in objs:
        i.ViewObject.Visibility = True
    for i in reversed(tmpobjs):
        doc.removeObject(i.Name)

    view = FreeCADGui.getDocument(newDoc.Name).activeView()
    view.viewAxometric()
    view.fitAll()

def updateAssembly():
    if len(FreeCADGui.Selection.getSelection()) == 0:
        FreeCAD.Console.PrintWarning("Select assembly!\n")
    
    mainFile = FreeCAD.ActiveDocument.Label
    for i in FreeCADGui.Selection.getSelection():
        if hasattr(i, "Proxy") and hasattr(i, "Type") and i.Proxy.Type == 'assemblyMain':
            i.Proxy.updateParts(i)
            i.Proxy.updateRotation(i)
    #
    FreeCAD.setActiveDocument(mainFile)
    FreeCADGui.ActiveDocument = FreeCADGui.getDocument(mainFile)
    
    FreeCADGui.ActiveDocument.activeView().viewAxometric()
    FreeCADGui.ActiveDocument.activeView().fitAll()
    FreeCAD.ActiveDocument.recompute()
    
def checkFile(fileName):
    if fileName.startswith('./'):
        fileName = os.path.join(os.path.dirname(FreeCAD.ActiveDocument.FileName), fileName)
    
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
        self.rotZ = 0
        self.rotX = 0
        self.rotY = 0 # side
        self.offsetX = 0
        self.offsetY = 0
        self.offsetZ = 0
    
    def onChanged(self, fp, prop):
        fp.setEditorMode("Placement", 2)
    
    def execute(self, obj):
        pass

    def updateRotation(self, obj, rot, center):
        try:
            sX = -self.offsetX 
            sY = -self.offsetY
            sZ = -self.offsetZ
            
            x = center[0] + self.offsetX 
            y = center[1] + self.offsetY
            z = center[2] + self.offsetZ
            
            pla = FreeCAD.Placement(FreeCAD.Base.Vector(x, y, z), FreeCAD.Rotation(rot[0], rot[1], rot[2]), FreeCAD.Base.Vector(sX, sY, sZ))
            obj.Placement = pla
            
            # rotate object -> ROT property; Z value
            rot = FreeCAD.Rotation(FreeCAD.Vector(0,0,1), self.rotZ)
            pos = FreeCAD.Base.Vector(0, 0, 0)
            nP = FreeCAD.Placement(pos, rot, pos)
            obj.Placement = obj.Placement.multiply(nP)
            # change side
            rot = FreeCAD.Rotation(FreeCAD.Vector(0,1,0), self.rotY)
            pos = FreeCAD.Base.Vector(0, 0, 0)
            nP = FreeCAD.Placement(pos, rot, pos)
            obj.Placement = obj.Placement.multiply(nP)
            #
            rot = FreeCAD.Rotation(FreeCAD.Vector(1,0,0), self.rotX)
            pos = FreeCAD.Base.Vector(0, 0, 0)
            nP = FreeCAD.Placement(pos, rot, pos)
            obj.Placement = obj.Placement.multiply(nP)
            
        except Exception, e:
            pass
            #FreeCAD.Console.PrintWarning("rot. {0} \n".format(e))

    def __getstate__(self):
        return [self.Type, self.rotX, self.rotY, self.rotZ, self.offsetX, self.offsetY, self.offsetZ]

    def __setstate__(self, state):
        if state:
            self.Type = state[0]
            self.rotX = state[1]
            self.rotY = state[2]
            self.rotZ = state[3]
            self.offsetX = state[4]
            self.offsetY = state[5]
            self.offsetZ = state[6]


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
        
        self.center = [0, 0 ,0]

    def execute(self, obj):
        pass
    
    def __getstate__(self):
        return [self.Type, str(self.center)]

    def __setstate__(self, state):
        if state:
            self.Type = state[0]
            self.center = eval(state[1])
    
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
            #
            center = Part.makeCompound([i.Shape for i in newFile[0].Objects if hasattr(i, "Shape")]).BoundBox.Center
            self.center = [center[0], center[1], center[2]]
            #
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
                        viewProviderChildAssemblyObject(child.ViewObject)
                        child.ViewObject.DiffuseColor = i.ViewObject.DiffuseColor
                        
                        child.Proxy.rotZ = i.Placement.Rotation.toEuler()[0]
                        child.Proxy.rotY = i.Placement.Rotation.toEuler()[1]
                        child.Proxy.rotX = i.Placement.Rotation.toEuler()[2]
                        
                        #
                        obj.addObject(child)
                        child.Proxy.offsetX = child.Placement.Base.x - self.center[0]
                        child.Proxy.offsetY = child.Placement.Base.y - self.center[1]
                        child.Proxy.offsetZ = child.Placement.Base.z - self.center[2]
                        
                    except Exception, e:
                        FreeCAD.Console.PrintWarning("1. {0} \n".format(e))
            if newFile[1]:
                FreeCAD.closeDocument(newFile[0].Label)
            FreeCAD.setActiveDocument(mainFile.Label)
            FreeCADGui.ActiveDocument = FreeCADGui.getDocument(mainFile.Label)
            
            FreeCADGui.ActiveDocument.activeView().viewAxometric()
            FreeCADGui.ActiveDocument.activeView().fitAll()

    def updateRotation(self, fp):
        try:
            center =  [fp.X.Value, fp.Y.Value, fp.Z.Value]
           
            for i in fp.OutList:
                i.Proxy.updateRotation(i, [fp.RZ.Value, fp.RY.Value, fp.RX.Value], center)
        except Exception, e:
            pass
            #FreeCAD.Console.PrintWarning("3. {0} \n".format(e))
        
    def onChanged(self, fp, prop):
        try:
            if prop == "File":
                self.updateParts(fp)
            elif prop in ['X', 'Y', 'Z', 'RX', 'RY', 'RZ']:
                self.updateRotation(fp)
        except:
            #FreeCAD.Console.PrintWarning("3. {0}\n".format(e))
            pass


class viewProviderMainAssemblyObject:
    def __init__(self, obj):
        obj.Proxy = self
        self.Object = obj.Object
        
        obj.addProperty("App::PropertyInteger", "Transparency", "Base", "Transparency").Transparency= 0

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
        
        try:
            if prop == 'Transparency' and vp.Transparency >= 0 and vp.Transparency <= 100:
                for i in vp.Object.OutList:
                    i.ViewObject.Transparency = vp.Transparency
        except:
            pass

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
        #vp.setEditorMode("Transparency", 2)
        
        try:
            if prop == 'Transparency' and vp.Transparency >= 0 and vp.Transparency <= 100:
                for i in vp.Object.OutList:
                    col = i.ViewObject.DiffuseColor
                    i.ViewObject.Transparency = vp.Transparency
                    i.ViewObject.DiffuseColor = col
        except:
            pass

    def getIcon(self):
        ''' Return the icon in XMP format which will appear in the tree view. This method is optional
        and if not defined a default icon is shown.
        '''
        return ":/data/img/asmChild.svg"
