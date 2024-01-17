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
from Draft import _DraftObject
if FreeCAD.GuiUp:
    from PySide import QtCore, QtGui
import sys, os
import Part
from pivy.coin import *
from math import pi
import unicodedata
#
from PCBconf import *
from PCBfunctions import kolorWarstwy, getFromSettings_Color_1
from PCBboard import getPCBheight
from command.PCBgroups import createGroup_Annotations

#***********************************************************************
#***********************************************************************
alignParam = ["bottom-left", "bottom-center", "bottom-right", "center-left", "center" , "center-right", "top-left", "top-center", "top-right"]
objectSides = ["TOP", "BOTTOM"]
fonts = ["Vector", "Fixed", "Proportional"]
mirror = ['None', 'Global Y axis', 'Local Y axis', 'Center']
#mirror = ['None', 'Global Y axis', 'Local Y axis']

__fontsDirecory__ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data/fonts")

fontFile = {
    "Vector": os.path.join(__fontsDirecory__, "Hyperspace.ttf"),
    "Fixed": os.path.join(__fontsDirecory__, "CutiveMono-Regular.ttf"),
    "Proportional": os.path.join(__fontsDirecory__, "LiberationMono-Regular.ttf")
}


#***********************************************************************
#*                             CONSOLE
#***********************************************************************
class createAnnotation:
    def __init__(self):
        self.X = 0
        self.Y = 0
        self.Z = 0
        self.tracking = 0
        self.lineDistance = 50
        self.Side = objectSides[0]
        self.Rot = 0
        self.Text = ''
        self.Align = alignParam[0]
        self.Size = 1.27
        self.Spin = True
        
        self.Color = (1., 1., 1.)
        self.Visibility = True
        self.mode = 'anno'
        #self.fontName = fonts[0]
        self.Font = "Fixed"
        #
        self.defaultName = 'PCBannotation_0000'
        self.defaultLabel = self.defaultName
        self.Type = 0  # 0-annotation; 1-object name/value
        self.Annotation = None
    
    def setName(self, value):
        self.defaultLabel = self.defaultName = value
        
        if isinstance(self.defaultName, str):
            self.defaultName = unicodedata.normalize('NFKD', u"{0}".format(self.defaultName)).encode('ascii', 'ignore')
        
    def generate(self, addToGroup=True):
        pcb = getPCBheight()

        if pcb[0]:
            text = self.Text
            if self.mode == 'anno':
                if not type(text) == list:
                    text = text.split('\n')
            else:
                if type(text) == list:
                    text = '_'.join(text)
            #
            self.setName(self.defaultName)
            #
            self.Annotation = FreeCAD.ActiveDocument.addObject("Part::Part2DObjectPython", 'PCBannotation_0000')
            self.Annotation.Label = 'PCBannotation_0000'
            PCBannotation(self.Annotation, self.mode)
            self.Annotation.Placement.Base = FreeCAD.Vector(0, 0, 0)
            #self.Annotation.Proxy.mode = self.mode
            self.Annotation.Justification = self.Align
            self.Annotation.X = self.X
            self.Annotation.Y = self.Y
            self.Annotation.Z = self.Z
            self.Annotation.Side = self.Side.upper()
            self.Annotation.Rot = self.Rot
            self.Annotation.Size = self.Size
            self.Annotation.Spin = self.Spin
            self.Annotation.LineDistance = self.lineDistance
            self.Annotation.Tracking = self.tracking
            self.Annotation.Font = self.Font
            self.Annotation.Proxy.block = False
            self.Annotation.String = text
            viewProviderPCBannotation(self.Annotation.ViewObject)
            
            try:
                self.Annotation.ViewObject.ShapeColor = self.Color
            except:
                self.Annotation.ViewObject.ShapeColor = (1.0, 1.0, 1.0)
            self.Annotation.ViewObject.Visibility = self.Visibility
            
            self.Annotation.Proxy.updatePosition_Z(self.Annotation, pcb[1])
            #Draft.formatObject(obj)
            #obj.recompute()
            #
            if addToGroup:
                grp = createGroup_Annotations()
                grp.addObject(self.Annotation)
            pcb[2].Proxy.addObject(pcb[2], self.Annotation)


#***********************************************************************
#*                               GUI
#***********************************************************************
class createAnnotation_Gui(QtGui.QWidget):
    def __init__(self, searchPhrase=None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        #partsManaging.__init__(self, parent)
        
        self.gruboscPlytki = getPCBheight()[1]
        self.root = None
        self.packageData = {}
        
        self.form = self
        self.form.setWindowTitle("Add annotation")
        self.form.setWindowIcon(QtGui.QIcon(":/data/img/addAnnotation.svg"))
        #
        self.text = QtGui.QTextEdit('')
        self.text.setFixedHeight(100)
        
        self.align = QtGui.QComboBox()
        self.align.addItems(alignParam)
        
        self.spin = QtGui.QComboBox()
        self.spin.addItems(['True', 'False'])
        self.spin.setCurrentIndex(1)
        
        self.fontSize = QtGui.QDoubleSpinBox()
        self.fontSize.setValue(1.27)
        self.fontSize.setSuffix(' mm')
        
        self.fontName = QtGui.QComboBox()
        self.fontName.addItems(fonts)
        self.fontName.setCurrentIndex(self.fontName.findText("Fixed"))
        
        self.tracking = QtGui.QDoubleSpinBox()
        self.tracking.setSingleStep(0.5)
        self.tracking.setRange(-1000, 1000)
        self.tracking.setSuffix(' mm')
        
        self.lineDistance = QtGui.QSpinBox()
        self.lineDistance.setValue(50)
        self.lineDistance.setSingleStep(1)
        self.lineDistance.setRange(-1000, 1000)
        self.lineDistance.setSuffix(' %')
        
        self.val_x = QtGui.QDoubleSpinBox()
        self.val_x.setSingleStep(0.5)
        self.val_x.setRange(-1000, 1000)
        self.val_x.setSuffix(' mm')
        
        self.val_y = QtGui.QDoubleSpinBox()
        self.val_y.setSingleStep(0.5)
        self.val_y.setRange(-1000, 1000)
        self.val_y.setSuffix(' mm')
        
        self.val_z = QtGui.QDoubleSpinBox()
        self.val_z.setSingleStep(0.5)
        self.val_z.setRange(-1000, 1000)
        self.val_z.setSuffix(' mm')
        
        self.rotation = QtGui.QDoubleSpinBox()
        self.rotation.setSingleStep(1)
        self.rotation.setSuffix(' deg')
        self.rotation.setRange(-360, 360)
        
        self.side = QtGui.QComboBox()
        self.side.addItems(objectSides)
        
        self.error = QtGui.QLabel(u'')
        
        self.continueCheckBox = QtGui.QCheckBox(u'Continue')
        
        self.fontColor = kolorWarstwy()
        self.fontColor.setColor(getFromSettings_Color_1('AnnotationsColor', 4294967295))
        self.fontColor.setToolTip(u"Click to change color")
        #
        lay = QtGui.QGridLayout()
        lay.addWidget(QtGui.QLabel(u'Text:'), 0, 0, 1, 1)
        lay.addWidget(self.text, 0, 1, 1, 2)
        
        lay.addWidget(QtGui.QLabel(u'Font:'), 1, 0, 1, 1)
        lay.addWidget(self.fontName, 1, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'FontFile:'), 2, 0, 1, 1)
        
        lay.addWidget(QtGui.QLabel(u'Font size:'), 3, 0, 1, 1)
        lay.addWidget(self.fontSize, 3, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Tracking:'), 4, 0, 1, 1)
        lay.addWidget(self.tracking, 4, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Line Distance:'), 5, 0, 1, 1)
        lay.addWidget(self.lineDistance, 5, 1, 1, 2)
        
        lay.addWidget(QtGui.QLabel(u'Font color:'), 6, 0, 1, 1)
        lay.addWidget(self.fontColor, 6, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Align:'), 7, 0, 1, 1)
        lay.addWidget(self.align, 7, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Side:'), 8, 0, 1, 1)
        lay.addWidget(self.side, 8, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Spin:'), 9, 0, 1, 1)
        lay.addWidget(self.spin, 9, 1, 1, 2)
        
        lay.addWidget(QtGui.QLabel(u'X:'), 10, 0, 1, 1)
        lay.addWidget(self.val_x, 10, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Y:'), 11, 0, 1, 1)
        lay.addWidget(self.val_y, 11, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Z:'), 12, 0, 1, 1)
        lay.addWidget(self.val_z, 12, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Rotation:'), 13, 0, 1, 1)
        lay.addWidget(self.rotation, 13, 1, 1, 2)
        
        lay.addItem(QtGui.QSpacerItem(1, 10), 14, 0, 1, 3)
        lay.addWidget(self.continueCheckBox, 15, 0, 1, 3)
        lay.addItem(QtGui.QSpacerItem(1, 10), 16, 0, 1, 3)
        lay.addWidget(self.error, 17, 0, 1, 3)
        lay.setRowStretch(18, 10)
        self.setLayout(lay)
        #
        self.connect(self.val_x, QtCore.SIGNAL('valueChanged (double)'), self.addArrow)
        self.connect(self.val_y, QtCore.SIGNAL('valueChanged (double)'), self.addArrow)
        #self.connect(self.side, QtCore.SIGNAL('currentIndexChanged (int)'), self.addArrow)

        self.addArrow()

    def addArrow(self):
        pass
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

    def accept(self):
        try:
            #################################################################
            #        polaczyc z innymi podobnymi czesciami kodu !!!!!       #
            #################################################################
            if unicodedata.normalize('NFKD', self.text.toPlainText()).encode('ascii', 'ignore').strip() == "":
                self.error.setText("<span style='color:red;font-weight:bold;'>Mandatory field is empty!</span>")
                return False
            #
            annotation = createAnnotation()
            annotation.X = self.val_x.value()
            annotation.Y = self.val_y.value()
            annotation.Z = self.val_z.value()
            annotation.Side = str(self.side.currentText())
            annotation.Rot = self.rotation.value()
            annotation.Text = self.text.toPlainText()
            annotation.Align = str(self.align.currentText())
            annotation.Size = self.fontSize.value()
            annotation.Spin = bool(self.spin.currentText())
            annotation.tracking = self.tracking.value()
            annotation.lineDistance = self.lineDistance.value()
            annotation.Color = self.fontColor.getColor()
            annotation.Font = str(self.fontName.currentText())
            annotation.generate()
            #annotation.addToAnnotations()
            #
            if self.continueCheckBox.isChecked():
                self.text.setText('')
            else:
                self.removeRoot()
                return True
        except:
            self.removeRoot()

    def removeRoot(self):
        if self.root:
            FreeCADGui.ActiveDocument.ActiveView.getSceneGraph().removeChild(self.root)
        
    def reject(self):
        self.removeRoot()
        return True


#***********************************************************************
#*                             OBJECT
#***********************************************************************



#***********************************************************************
#*             BASED ON _ShapeString() FROM DRAFT MODULE
#***********************************************************************
class PCBannotation(_DraftObject):
    """The ShapeString object"""
    def __init__(self, obj, mode='anno'):
        self.Type = "anno"
        self.mode = mode  # anno/param
        self.przX = 0
        self.przY = 0
        self.block = True
        self.react = True
        
        _DraftObject.__init__(self,obj,"ShapeString")

        if obj.Proxy.mode == 'anno':
            obj.addProperty("App::PropertyStringList", "String", "Draft", "String").String = [""]
        else:
            obj.addProperty("App::PropertyString", "String", "Draft", "String").String = ""
        
        obj.addProperty("App::PropertyFile","FontFile","Draft","Font file name").FontFile = fontFile["Fixed"]
        obj.addProperty("App::PropertyLength","Size","Draft","Height of text").Size=10
        obj.addProperty("App::PropertyLength","Tracking","Draft","Inter-character spacing").Tracking=0
        obj.addProperty("App::PropertyPercent","LineDistance","Draft","LineDistance").LineDistance=50
        obj.addProperty("App::PropertyEnumeration", "Justification", "Draft", "Justification")
        obj.addProperty("App::PropertyBool", "Spin", "Draft", "Spin").Spin = True
        #obj.addProperty("App::PropertyFont", "Font1", "Draft", "Font1")
        obj.addProperty("App::PropertyEnumeration", "Font", "Draft", "Font").Font = 1
        
        obj.addProperty("App::PropertyDistance", "X", "Placement", "X").X = 0
        obj.addProperty("App::PropertyDistance", "Y", "Placement", "Y").Y = 0
        obj.addProperty("App::PropertyDistance", "Z", "Placement", "Z").Z = 0
        obj.addProperty("App::PropertyAngle", "Rot", "Placement", "Rot").Rot = 0
        obj.addProperty("App::PropertyEnumeration", "Side", "Placement", "Side").Side = 0
        
        obj.setEditorMode("MapMode", 2)
        obj.setEditorMode("Label", 2)
        obj.setEditorMode("Placement", 2)
        
        obj.Justification = alignParam
        obj.Justification = 2
        obj.Side = objectSides
        obj.Font = fonts
        ##
        obj.Proxy = self
    
    def __getstate__(self):
        return [self.Type, self.block, self.react, self.mode]

    def __setstate__(self, state):
        self.loads(state)

    def dumps(self):
        return [self.Type, self.block, self.react, self.mode]

    def loads(self, state):
        if state:
            self.Type = state[0]
            self.block  = state[1]
            self.react = state[2]
            self.mode = state[3]
    
    def textAlign(self):
        FreeCAD.Console.PrintWarning("{0}\n".format(self.alignParam))
    
    def updatePosition_Z(self, fp, thickness):
        if fp.Side == objectSides[0]:  # top side
            fp.Placement.Base.z = thickness + 0.035 + fp.Z.Value
        else:  # bottom side
            fp.Placement.Base.z = 0 - 0.035 - fp.Z.Value
    
    def execute(self, obj):
        pass
        
    def generate(self, obj):
        if self.block:
            return
        # test a simple letter to know if we have a sticky font or not
        if obj.String and obj.FontFile:
            sticky = False
            testWire = Part.makeWireString("L",obj.FontFile,obj.Size,obj.Tracking)[0][0]
            if testWire.isClosed:
                try:
                    testFace = Part.Face(testWire)
                except Part.OCCError:
                    sticky = True
                else:
                    if not testFace.isValid():
                        sticky = True
            else:
                sticky = True
        ###################
        if obj.String and obj.FontFile:
            if obj.Placement:
                plm = obj.Placement
            
            if type(obj.String) == list: # multilines
                poz_Y = 0
                shapes = []
                
                for i in range(len(obj.String), 0, -1):
                    line = obj.String[i-1]
                    
                    if line != "":
                        CharList = Part.makeWireString(line,obj.FontFile,obj.Size,obj.Tracking)
                        if len(CharList) == 0:
                            FreeCAD.Console.PrintWarning(translate("draft","ShapeString: string has no wires")+"\n")
                            return
                        SSChars = []
                    
                        for char in CharList:
                            if sticky:
                                for CWire in char:
                                    for k in CWire:
                                        k.Placement.Base.y = poz_Y
                                    
                                    SSChars.append(CWire)
                            else:
                                CharFaces = []
                                for CWire in char:
                                    CWire.Placement.Base.y = poz_Y
                                    
                                    f = Part.Face(CWire)
                                    if f:
                                        CharFaces.append(f)
                                # whitespace (ex: ' ') has no faces. This breaks OpenSCAD2Dgeom...
                                if CharFaces:
                                    # s = OpenSCAD2Dgeom.Overlappingfaces(CharFaces).makeshape()
                                    # s = self.makeGlyph(CharFaces)
                                    s = self.makeFaces(char)
                                    SSChars.append(s)
                        
                        shapes.append(Part.Compound(SSChars))
                    poz_Y += obj.Size.Value + (obj.LineDistance * obj.Size.Value) / 100.
                shape = Part.Compound(shapes)
            else:
                CharList = Part.makeWireString(obj.String,obj.FontFile,obj.Size,obj.Tracking)
                if len(CharList) == 0:
                    FreeCAD.Console.PrintWarning(translate("draft","ShapeString: string has no wires")+"\n")
                    return
                SSChars = []
            
                for char in CharList:
                    if sticky:
                        for CWire in char:
                            SSChars.append(CWire)
                    else:
                        CharFaces = []
                        for CWire in char:
                            f = Part.Face(CWire)
                            if f:
                                CharFaces.append(f)
                        # whitespace (ex: ' ') has no faces. This breaks OpenSCAD2Dgeom...
                        if CharFaces:
                            # s = OpenSCAD2Dgeom.Overlappingfaces(CharFaces).makeshape()
                            # s = self.makeGlyph(CharFaces)
                            s = self.makeFaces(char)
                            SSChars.append(s)
                            
                shape = Part.Compound(SSChars)
            ###################
            obj.Shape = shape
            if plm:
                obj.Placement = plm
        obj.positionBySupport()
        self.changeJustification(obj)
        
    def makeFaces(self, wireChar):
        import Part
        compFaces=[]
        allEdges = []
        wirelist=sorted(wireChar,key=(lambda shape: shape.BoundBox.DiagonalLength),reverse=True)
        fixedwire = []
        for w in wirelist:
            compEdges = Part.Compound(w.Edges)
            compEdges = compEdges.connectEdgesToWires()
            fixedwire.append(compEdges.Wires[0])
        wirelist = fixedwire
        sep_wirelist = []
        while len(wirelist) > 0:
            wire2Face = [wirelist[0]]
            face = Part.Face(wirelist[0])
            for w in wirelist[1:]:
                p = w.Vertexes[0].Point
                u,v = face.Surface.parameter(p)
                if face.isPartOfDomain(u,v):
                    f = Part.Face(w)
                    if face.Orientation == f.Orientation:
                        if f.Surface.Axis * face.Surface.Axis < 0:
                            w.reverse()
                    else:
                        if f.Surface.Axis * face.Surface.Axis > 0:
                            w.reverse()
                    wire2Face.append(w)
                else:
                    sep_wirelist.append(w)
            wirelist = sep_wirelist
            sep_wirelist = []
            face = Part.Face(wire2Face)
            face.validate()
            try:
                # some fonts fail here
                if face.Surface.Axis.z < 0.0:
                    face.reverse()
            except:
                pass
            compFaces.append(face)
        ret = Part.Compound(compFaces)
        return ret
    
    def onChanged(self, fp, prop):
        fp.setEditorMode("Placement", 2)
        fp.setEditorMode("Label", 2)
        fp.setEditorMode("MapMode", 2)
        #
        if hasattr(fp.Proxy, "mode") and self.mode == "param" and self.react:
            if prop == "String":
                for i in fp.InList:
                    if hasattr(i, "Proxy") and hasattr(i.Proxy, "Type") and i.Proxy.Type in ["PCBpart", "PCBpart_E"]:
                        if i.PartName == fp:
                            i.Label = fp.String
        ######################
        try:
            if prop == "Font":  # pre. def. fonts
                fp.FontFile = fontFile[fp.Font]
            
            if self.block:
                return
            
            #FreeCAD.Console.PrintWarning(u"{0}\n".format(prop))
            if prop == "Justification" or prop == "X" or prop == "Y" or prop == "Rot" or prop == "Spin":
                self.changeJustification(fp)
            elif prop == "Z" or prop == "Side":
                #thickness = getPCBheight()
                self.changeJustification(fp)
                # if thickness[0]:
                    # self.updatePosition_Z(fp, thickness[1])
                # else:
                    # self.updatePosition_Z(fp, 0)
            elif prop == "String" or prop == "FontFile" or prop == "Tracking" or prop == "LineDistance" or prop == "Size":  # pre. def. fonts
                if prop == "String" and fp.String == "":
                    fp.String = " "
                
                self.generate(fp)
        except Exception as e:
            pass
        
    def changeJustification(self, fp):
        try:
            fp.Placement = FreeCAD.Placement(fp.Placement.Base, FreeCAD.Rotation(FreeCAD.Vector(0,0,1),0))
            
            if fp.Spin == False and 90 < abs(fp.Rot.Value) < 271: # SPIN IS OFF
                if fp.Justification == "bottom-left":
                    fp.Placement.Base.x = fp.X.Value - fp.Shape.BoundBox.XLength
                    fp.Placement.Base.y = fp.Y.Value - fp.Shape.BoundBox.YLength
                    
                    self.przX = fp.Shape.BoundBox.XLength
                    self.przY = fp.Shape.BoundBox.YLength
                elif fp.Justification == "bottom-right":
                    fp.Placement.Base.x = fp.X.Value
                    fp.Placement.Base.y = fp.Y.Value - fp.Shape.BoundBox.YLength
                    
                    self.przX = 0
                    self.przY = fp.Shape.BoundBox.YLength
                elif fp.Justification == "bottom-center":
                    fp.Placement.Base.x = fp.X.Value - fp.Shape.BoundBox.XLength / 2.
                    fp.Placement.Base.y = fp.Y.Value - fp.Shape.BoundBox.YLength
                    
                    self.przX = fp.Shape.BoundBox.XLength / 2.
                    self.przY = fp.Shape.BoundBox.YLength
                
                
                elif fp.Justification == "center-left":
                    fp.Placement.Base.x = fp.X.Value - fp.Shape.BoundBox.XLength
                    fp.Placement.Base.y = fp.Y.Value - fp.Shape.BoundBox.YLength / 2.
                    
                    self.przX = fp.Shape.BoundBox.XLength
                    self.przY = fp.Shape.BoundBox.YLength / 2.
                elif fp.Justification == "center":
                    fp.Placement.Base.x = fp.X.Value - fp.Shape.BoundBox.XLength / 2.
                    fp.Placement.Base.y = fp.Y.Value - fp.Shape.BoundBox.YLength / 2.
                    
                    self.przX = fp.Shape.BoundBox.XLength / 2.
                    self.przY = fp.Shape.BoundBox.YLength / 2.
                elif fp.Justification == "center-right":
                    fp.Placement.Base.x = fp.X.Value
                    fp.Placement.Base.y = fp.Y.Value - fp.Shape.BoundBox.YLength / 2.
                    
                    self.przX = 0
                    self.przY = fp.Shape.BoundBox.YLength / 2.
                
                
                elif fp.Justification == "top-right":
                    fp.Placement.Base.x = fp.X.Value
                    fp.Placement.Base.y = fp.Y.Value
                    
                    self.przX = 0
                    self.przY = 0
                elif fp.Justification == "top-left":
                    fp.Placement.Base.x = fp.X.Value - fp.Shape.BoundBox.XLength
                    fp.Placement.Base.y = fp.Y.Value
                    
                    self.przX = fp.Shape.BoundBox.XLength
                    self.przY = 0
                elif fp.Justification == "top-center":
                    fp.Placement.Base.x = fp.X.Value - fp.Shape.BoundBox.XLength / 2.
                    fp.Placement.Base.y = fp.Y.Value
                    
                    self.przX = fp.Shape.BoundBox.XLength / 2.
                    self.przY = 0
                
            else:
                if fp.Justification == "bottom-left":
                    fp.Placement.Base.x = fp.X.Value
                    fp.Placement.Base.y = fp.Y.Value
                    
                    self.przX = 0
                    self.przY = 0
                elif fp.Justification == "bottom-center":
                    fp.Placement.Base.x = fp.X.Value - fp.Shape.BoundBox.XLength / 2.
                    fp.Placement.Base.y = fp.Y.Value
                    
                    self.przX = fp.Shape.BoundBox.XLength / 2.
                    self.przY = 0
                elif fp.Justification == "bottom-right":
                    fp.Placement.Base.x = fp.X.Value - fp.Shape.BoundBox.XLength
                    fp.Placement.Base.y = fp.Y.Value
                    
                    self.przX = fp.Shape.BoundBox.XLength
                    self.przY = 0
                    
                    
                elif fp.Justification == "center-left":
                    fp.Placement.Base.x = fp.X.Value
                    fp.Placement.Base.y = fp.Y.Value - fp.Shape.BoundBox.YLength / 2.
                    
                    self.przX = 0
                    self.przY = fp.Shape.BoundBox.YLength / 2.
                elif fp.Justification == "center":
                    fp.Placement.Base.x = fp.X.Value - fp.Shape.BoundBox.XLength / 2.
                    fp.Placement.Base.y = fp.Y.Value - fp.Shape.BoundBox.YLength / 2.
                    
                    self.przX = fp.Shape.BoundBox.XLength / 2.
                    self.przY = fp.Shape.BoundBox.YLength / 2.
                elif fp.Justification == "center-right":
                    fp.Placement.Base.x = fp.X.Value - fp.Shape.BoundBox.XLength
                    fp.Placement.Base.y = fp.Y.Value - fp.Shape.BoundBox.YLength / 2.
                    
                    self.przX = fp.Shape.BoundBox.XLength
                    self.przY = fp.Shape.BoundBox.YLength / 2.
                
                
                elif fp.Justification == "top-left":
                    fp.Placement.Base.x = fp.X.Value
                    fp.Placement.Base.y = fp.Y.Value - fp.Shape.BoundBox.YLength
                    
                    self.przX = 0
                    self.przY = fp.Shape.BoundBox.YLength
                elif fp.Justification == "top-center":
                    fp.Placement.Base.x = fp.X.Value - fp.Shape.BoundBox.XLength / 2.
                    fp.Placement.Base.y = fp.Y.Value - fp.Shape.BoundBox.YLength
                    
                    self.przX = fp.Shape.BoundBox.XLength / 2.
                    self.przY = fp.Shape.BoundBox.YLength
                elif fp.Justification == "top-right":
                    fp.Placement.Base.x = fp.X.Value - fp.Shape.BoundBox.XLength
                    fp.Placement.Base.y = fp.Y.Value - fp.Shape.BoundBox.YLength
                    
                    self.przX = fp.Shape.BoundBox.XLength
                    self.przY = fp.Shape.BoundBox.YLength
            
            if fp.Side == "TOP":
                rotY = 0
                rotZ = fp.Rot.Value
            else:
                rotY = 180
                rotZ = -fp.Rot.Value
            
            if fp.Spin == False and 90 < abs(fp.Rot.Value) < 271:
                fp.Placement = FreeCAD.Placement(fp.Placement.Base, FreeCAD.Rotation(rotZ - 180, rotY ,0), FreeCAD.Vector(self.przX, self.przY, fp.Z.Value))
            else:
                fp.Placement = FreeCAD.Placement(fp.Placement.Base, FreeCAD.Rotation(rotZ, rotY, 0), FreeCAD.Vector(self.przX, self.przY, fp.Z.Value))
            
            if str(fp.Placement.Base.z) == "nan":
                fp.Placement.Base.z = 0
            #
            thickness = getPCBheight()
            if thickness[0]:
                self.updatePosition_Z(fp, thickness[1])
            else:
                self.updatePosition_Z(fp, 0)
            
        except Exception as e:
            #FreeCAD.Console.PrintWarning("3. {0}\n".format(e))
            pass


class viewProviderPCBannotation:
    def __init__(self, obj):
        ''' Set this object to the proxy object of the actual view provider '''
        obj.Proxy = self

    def attach(self, obj):
        ''' Setup the scene sub-graph of the view provider, this method is mandatory '''
        self.Object = obj.Object

    def updateData(self, fp, prop):
        ''' If a property of the handled feature has changed we have the chance to handle this here '''
        return

    def getDisplayModes(self, obj):
        ''' Return a list of display modes. '''
        modes = []
        return modes

    def getDefaultDisplayMode(self):
        ''' Return the name of the default display mode. It must be defined in getDisplayModes. '''
        return "Flat Lines"

    def setDisplayMode(self, mode):
        ''' Map the display mode defined in attach with those defined in getDisplayModes.
        Since they have the same names nothing needs to be done. This method is optional.
        '''
        return mode

    def onChanged(self, vp, prop):
        ''' Print the name of the property that has changed '''
        #FreeCAD.Console.PrintWarning(u"{0}\n".format(prop))
        ####################
        # TEMPORARY SOLUTION
        ####################
        #if not hasattr(vp, "Text"):
            #self.__init__(vp)
        ####################
        ####################
        vp.setEditorMode("LineColor", 2)
        vp.setEditorMode("DrawStyle", 2)
        vp.setEditorMode("LineWidth", 2)
        vp.setEditorMode("PointColor", 2)
        vp.setEditorMode("PointSize", 2)
        vp.setEditorMode("Deviation", 2)
        vp.setEditorMode("Lighting", 2)
        vp.setEditorMode("BoundingBox", 2)
        #vp.setEditorMode("ShapeColor", 2)
        #vp.setEditorMode("Visibility", 2)
        vp.setEditorMode("Transparency", 2)
        vp.setEditorMode("DisplayMode", 2)
        vp.setEditorMode("Selectable", 2)
        vp.setEditorMode("SelectionStyle", 2)
        try:
            vp.setEditorMode("GridSize", 2)
            vp.setEditorMode("GridSnap", 2)
            vp.setEditorMode("GridStyle", 2)
            vp.setEditorMode("ShowGrid", 2)
            vp.setEditorMode("TightGrid", 2)
        except:
            pass
        vp.setEditorMode("AngularDeflection", 2)
        
        if prop == "ShapeColor":
            vp.LineColor = vp.ShapeColor
            vp.PointColor = vp.ShapeColor
        
    def execute(self, obj):
        pass
        
    def getIcon(self):
        ''' Return the icon in XMP format which will appear in the tree view. This method is optional
        and if not defined a default icon is shown.
        '''
        return ":/data/img/addAnnotation.svg"

    def __getstate__(self):
        ''' When saving the document this object gets stored using Python's cPickle module.
        Since we have some un-pickable here -- the Coin stuff -- we must define this method
        to return a tuple of all pickable objects or None.
        '''
        return None

    def __setstate__(self, state):
        ''' When restoring the pickled object from document we have the chance to set some
        internals here. Since no data were pickled nothing needs to be done here.
        '''
        return None

    def dumps(self):
        ''' When saving the document this object gets stored using Python's cPickle module.
        Since we have some un-pickable here -- the Coin stuff -- we must define this method
        to return a tuple of all pickable objects or None.
        '''
        return None

    def loads(self, state):
        ''' When restoring the pickled object from document we have the chance to set some
        internals here. Since no data were pickled nothing needs to be done here.
        '''
        return None
