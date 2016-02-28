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
    from PySide import QtCore, QtGui
from pivy.coin import *
from math import pi
import unicodedata
#
from PCBconf import *
from PCBfunctions import kolorWarstwy
from PCBboard import getPCBheight
from command.PCBgroups import createGroup_Annotations

#***********************************************************************
#***********************************************************************
alignParam = ["bottom-left", "bottom-center", "bottom-right", "center-left", "center", "center-right", "top-left", "top-center", "top-right"]
objectSides = ["TOP", "BOTTOM"]
fonts = ["Hursheys", "Arial", "Modern", "RadioLand", "OCR A Extended"]
#mirror = ['None', 'Global Y axis', 'Local Y axis', 'Center']
mirror = ['None', 'Global Y axis', 'Local Y axis']

font = QtGui.QFontDatabase()
font.addApplicationFont(":/data/fonts/Hursheys.ttf")
font.addApplicationFont(":/data/fonts/Alexandria.ttf")
font.addApplicationFont(":/data/fonts/Eligible.ttf")
font.addApplicationFont(":/data/fonts/RadioLand.ttf")
font.addApplicationFont(":/data/fonts/ocraextended.ttf")

fontFile = {
    "Hursheys": ":/data/fonts/Hursheys.ttf",
    "Alexandria" : ":/data/fonts/Alexandria.ttf",
    "Eligible" : ":/data/fonts/Eligible.ttf",
    "RadioLand" : ":/data/fonts/RadioLand.ttf",
    "OCR A Extended" : ":/data/fonts/ocraextended.ttf",
}


#***********************************************************************
#*                             CONSOLE
#***********************************************************************
class createAnnotation:
    def __init__(self):
        self.X = 0
        self.Y = 0
        self.Z = 0
        self.Side = objectSides[0]
        self.Rot = 0
        self.Text = ''
        self.Align = alignParam[0]
        self.Size = 1.27
        self.Spin = True
        self.Mirror = mirror[0]
        self.Color = (1., 1., 1.)
        self.Visibility = True
        self.mode = 'anno'
        #self.fontName = fonts[0]
        #
        self.defaultName = 'PCBannotation_0000'
        self.defaultLabel = self.defaultName
        self.Type = 0  # 0-annotation; 1-object name/value
        self.Annotation = None
    
    def setName(self, value):
        self.defaultLabel = self.defaultName = value
        
        if isinstance(self.defaultName, unicode):
            self.defaultName = unicodedata.normalize('NFKD', self.defaultName).encode('ascii', 'ignore')
        
    def generate(self):
        text = self.Text
        if not type(text).__name__ == 'list':
            text = text.split('\n')
            #text = [text]
        
        self.setName(self.defaultName)
        #
        doc = FreeCAD.activeDocument()
        self.Annotation = doc.addObject("Part::FeaturePython", self.defaultName)
        self.Annotation.Label = self.defaultLabel
        if self.Type == 1:
            PCBannotation_Object(self.Annotation)
        else:
            PCBannotation(self.Annotation)
        self.Annotation.X = self.X
        self.Annotation.Y = self.Y
        self.Annotation.Z = self.Z
        self.Annotation.Side = self.Side
        self.Annotation.Rot = self.Rot
        self.Annotation.Proxy.mode = self.mode
        viewProviderPCBannotation(self.Annotation.ViewObject)
        if self.mode == 'anno':
            self.Annotation.ViewObject.Text = text
        else:
            self.Annotation.ViewObject.Text = text[0]
        self.Annotation.ViewObject.Align = self.Align
        self.Annotation.ViewObject.Size = self.Size
        self.Annotation.ViewObject.Spin = self.Spin
        self.Annotation.ViewObject.Mirror = self.Mirror
        try:
            self.Annotation.ViewObject.Color = self.Color
        except:
            self.Annotation.ViewObject.Color = (1.0, 1.0, 1.0)
        self.Annotation.ViewObject.Visibility = self.Visibility
        
        #self.Annotation.ViewObject.Font = self.fontName
    
    def addToAnnotations(self):
        grp = createGroup_Annotations()
        grp.addObject(self.Annotation)


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
        self.form.setWindowIcon(QtGui.QIcon(":/data/img/annotation.png"))
        #
        self.text = QtGui.QLineEdit('')
        
        self.align = QtGui.QComboBox()
        self.align.addItems(alignParam)
        
        self.mirror = QtGui.QComboBox()
        self.mirror.addItems(mirror)
        
        self.spin = QtGui.QComboBox()
        self.spin.addItems(['True', 'False'])
        
        self.fontSize = QtGui.QDoubleSpinBox()
        self.fontSize.setValue(1.27)
        self.fontSize.setSuffix(' mm')
        
        self.fontName = QtGui.QComboBox()
        self.fontName.setDisabled(True)
        
        self.val_x = QtGui.QDoubleSpinBox()
        self.val_x.setSingleStep(0.5)
        self.val_x.setRange(-1000, 1000)
        self.val_x.setSuffix(' mm')
        
        self.val_y = QtGui.QDoubleSpinBox()
        self.val_y.setSingleStep(0.5)
        self.val_y.setRange(-1000, 1000)
        self.val_y.setSuffix(' mm')
        
        self.rotation = QtGui.QDoubleSpinBox()
        self.rotation.setSingleStep(1)
        self.rotation.setSuffix(' deg')
        self.rotation.setRange(-360, 360)
        
        self.side = QtGui.QComboBox()
        self.side.addItems(objectSides)
        
        self.error = QtGui.QLabel(u'')
        
        self.continueCheckBox = QtGui.QCheckBox(u'Continue')
        
        self.fontColor = kolorWarstwy()
        self.fontColor.setColor((0, 0, 0))
        self.fontColor.setToolTip(u"Click to change color")
        #
        lay = QtGui.QGridLayout()
        lay.addWidget(QtGui.QLabel(u'Text:'), 0, 0, 1, 1)
        lay.addWidget(self.text, 0, 1, 1, 2)
        
        lay.addWidget(QtGui.QLabel(u'Font name:'), 1, 0, 1, 1)
        lay.addWidget(self.fontName, 1, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Font size:'), 2, 0, 1, 1)
        lay.addWidget(self.fontSize, 2, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Font color:'), 3, 0, 1, 1)
        lay.addWidget(self.fontColor, 3, 1, 1, 2)
        
        lay.addWidget(QtGui.QLabel(u'Align:'), 4, 0, 1, 1)
        lay.addWidget(self.align, 4, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Mirror:'), 5, 0, 1, 1)
        lay.addWidget(self.mirror, 5, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Spin:'), 6, 0, 1, 1)
        lay.addWidget(self.spin, 6, 1, 1, 2)
        
        lay.addWidget(QtGui.QLabel(u'X:'), 7, 0, 1, 1)
        lay.addWidget(self.val_x, 7, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Y:'), 8, 0, 1, 1)
        lay.addWidget(self.val_y, 8, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Rotation:'), 9, 0, 1, 1)
        lay.addWidget(self.rotation, 9, 1, 1, 2)
        lay.addWidget(QtGui.QLabel(u'Side:'), 10, 0, 1, 1)
        lay.addWidget(self.side, 10, 1, 1, 2)
        
        lay.addItem(QtGui.QSpacerItem(1, 10), 11, 0, 1, 3)
        lay.addWidget(self.continueCheckBox, 12, 0, 1, 3)
        lay.addItem(QtGui.QSpacerItem(1, 10), 13, 0, 1, 3)
        lay.addWidget(self.error, 14, 0, 1, 3)
        lay.setRowStretch(15, 10)
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
        #################################################################
        #        polaczyc z innymi podobnymi czesciami kodu !!!!!       #
        #################################################################
        if unicodedata.normalize('NFKD', self.text.text()).encode('ascii', 'ignore').strip() == "":
            self.error.setText("<span style='color:red;font-weight:bold;'>Mandatory field is empty!</span>")
            return False
        #
        annotation = createAnnotation()
        annotation.X = self.val_x.value()
        annotation.Y = self.val_y.value()
        annotation.Side = str(self.side.currentText())
        annotation.Rot = self.rotation.value()
        annotation.Text = [self.text.text()]
        annotation.Align = str(self.align.currentText())
        annotation.Size = self.fontSize.value()
        annotation.Spin = bool(self.spin.currentText())
        annotation.Mirror = str(self.mirror.currentText())
        annotation.Color = self.fontColor.getColor()
        annotation.generate()
        annotation.addToAnnotations()
        #
        if self.continueCheckBox.isChecked():
            self.text.setText('')
        else:
            self.removeRoot()
            return True

    def removeRoot(self):
        if self.root:
            FreeCADGui.ActiveDocument.ActiveView.getSceneGraph().removeChild(self.root)
        
    def reject(self):
        self.removeRoot()
        return True


#***********************************************************************
#*                             OBJECT
#***********************************************************************
class PCBannotation:
    def __init__(self, obj):
        self.Type = PCBlayers["Annotations"][3]
        obj.Proxy = self
        
        obj.addProperty("App::PropertyDistance", "X", "Placement", "X").X = 0
        obj.addProperty("App::PropertyDistance", "Y", "Placement", "Y").Y = 0
        obj.addProperty("App::PropertyDistance", "Z", "Placement", "Z").Z = 0
        obj.addProperty("App::PropertyAngle", "Rot", "Placement", "Rot").Rot = 0
        obj.addProperty("App::PropertyEnumeration", "Side", "Placement", "Side").Side = 0
        
        obj.setEditorMode("Placement", 2)
        obj.setEditorMode("Z", 2)
        obj.Side = objectSides
        
        self.mode = 'anno'  # anno/anno_name/anno_value
        
    def reverseSide(self, fp):
        if objectSides[0] == fp.Side:
            fp.Side = objectSides[1]
        else:
            fp.Side = objectSides[0]
            
        if fp.ViewObject.Mirror == mirror[0]:
            fp.ViewObject.Mirror = mirror[1]
        else:
            fp.ViewObject.Mirror = mirror[0]
        
        self.changeSide(fp)
        
    def changeSide(self, fp):
        ''' ROT Y '''
        self.rotateZ(fp)
        self.updatePosition_Z(fp)

    def updatePosition_Z(self, fp, dummy=None):
        thickness = getPCBheight()[1]
        
        if fp.Side == objectSides[0]:  # TOP
            fp.Placement.Base.z = thickness + 0.001 + fp.Z.Value
        else:
            fp.Placement.Base.z = -0.001 - fp.Z.Value
        
    def changePos(self, fp):
        ''' change placement - X, Y '''
        fp.Placement.Base.x = fp.X.Value
        fp.Placement.Base.y = fp.Y.Value
        
    def rotateZ(self, fp):
        ''' ROT Z '''
        rotZ = fp.Rot.Value
        rotY = 0

        try:
            if fp.ViewObject.Mirror == 'Global Y axis':
                rotY = 180
                rotZ = fp.Rot.Value * -1
                
            elif fp.ViewObject.Mirror == 'Local Y axis':
                rotZ = fp.Rot.Value
        except:
            # FreeCAD.Console.PrintWarning(str(e) + " -\n")
            pass

        fp.Placement = FreeCAD.Placement(fp.Placement.Base, FreeCAD.Rotation(rotZ, rotY, 0))
        
        try:
            if not fp.ViewObject.Spin:
                fp.ViewObject.Proxy.execute(fp.ViewObject)
        except:
            # FreeCAD.Console.PrintWarning(str(e) + " -\n")
            pass
    
    def onChanged(self, fp, prop):
        try:
            fp.setEditorMode("Placement", 2)
            fp.setEditorMode("Z", 2)
        except:
            pass
        
        try:
            if prop == "Side":
                self.changeSide(fp)
            elif prop in ["Z"]:
                self.changeSide(fp)
            elif prop in ["X", "Y"]:
                self.changePos(fp)
            elif prop == "Rot":
                self.rotateZ(fp)
        except:
            pass

    def execute(self, fp):
        pass

    def __getstate__(self):
        return [self.Type, self.mode]

    def __setstate__(self, state):
        if state:
            self.Type = state[0]
            self.mode = state[1]


class PCBannotation_Object(PCBannotation):
    def __init__(self, obj):
        PCBannotation.__init__(self, obj)
        
        obj.setEditorMode("Z", 0)
    
    def onChanged(self, fp, prop):
        try:
            fp.setEditorMode("Placement", 2)
            fp.setEditorMode("Z", 0)
        except:
            pass
        
        try:
            if prop == "Side":
                self.changeSide(fp)
            elif prop in ["Z"]:
                self.changeSide(fp)
            elif prop in ["X", "Y"]:
                self.changePos(fp)
            elif prop == "Rot":
                self.rotateZ(fp)
        except:
            pass


class viewProviderPCBannotation:
    def __init__(self, obj):
        ''' Set this object to the proxy object of the actual view provider '''
        obj.Proxy = self
        
        if obj.Object.Proxy.mode == 'anno':
            obj.addProperty("App::PropertyStringList", "Text", "Base", "Text").Text = ""
        else:
            obj.addProperty("App::PropertyString", "Text", "Base", "Text").Text = ""
        #
        obj.addProperty("App::PropertyEnumeration", "Align", "Display", "Align").Align = 4
        obj.addProperty("App::PropertyBool", "Spin", "Display", "Spin").Spin = True
        obj.addProperty("App::PropertyEnumeration", "Mirror", "Display", "Mirror").Mirror = 0
        # font
        obj.addProperty("App::PropertyDistance", "Size", "Font", "Size").Size = 1.27
        obj.addProperty("App::PropertyColor", "Color", "Font", "Color").Color = (1., 1., 1.)
        obj.addProperty("App::PropertyEnumeration", "Font", "Font", "Font").Font = 1
        
        obj.Mirror = mirror
        obj.Align = alignParam
        obj.Font = fonts
        
        obj.setEditorMode("Font", 1)
        
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
        Since they have the same names nothing needs to be done. This method is optinal.
        '''
        return mode

    def onChanged(self, vp, prop):
        ''' Print the name of the property that has changed '''
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
        vp.setEditorMode("ShapeColor", 2)
        #vp.setEditorMode("Visibility", 2)
        vp.setEditorMode("Transparency", 2)
        vp.setEditorMode("DisplayMode", 2)
        vp.setEditorMode("Selectable", 2)
        if hasattr(vp, "AngularDeflection"):
            vp.setEditorMode("AngularDeflection", 2)
        if hasattr(vp, "Font"):
            vp.setEditorMode("Font", 1)
        
        #self.Object = vp.Object
        vp.Object.Proxy.rotateZ(vp.Object)
        
        if prop in ['Display', 'Text', 'Size', 'Align', 'Color', 'Font', 'Spin', 'Visibility', 'Mirror']:
            self.execute(vp)
        
        ################################################################
        # change object name
        if prop == 'Text' and vp.Object.Proxy.mode == 'anno_name':
            try:
                if vp.Object.InList[0].PartValue:
                    vp.Object.InList[0].PartValue.Label = vp.Text + '_Value'

                vp.Object.Label = vp.Text + '_Name'
                vp.Object.InList[0].Label = vp.Text
            except:
                pass
        ################################################################
        
    def setText(self, obj):
        if not obj.Visibility:
            text = ['']
        else:
            text = obj.Text
        
        #if obj.Display == 'Value':
            #text = obj.Text
        #elif obj.Display == 'Name':
            ## text = str(obj.Object.Label)
            #text = obj.Text
        #elif obj.Display == 'Both':
            ## text = "{0} = {1}".format(str(obj.Object.Label), obj.Text)
            #text = obj.Text
        
        if obj.Object.Proxy.mode == 'anno':
            for nr in range(len(text)):
                #if not isinstance(text[nr], unicode):
                    #text[nr] = unicode(text[nr], 'utf-8')
                if isinstance(text[nr], unicode):
                    text[nr] = unicodedata.normalize('NFKD', text[nr]).encode('ascii', 'ignore')
        else:
            text = [unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')]
        
        txt = SoMFString()
        txt.setValues([i for i in text if i.strip() != ''])
        txt.finishEditing()
        
        myText3 = SoText3()
        myText3.string = txt
        myText3.justification = SoText3.LEFT
        myText3.parts = SoText3.ALL
        
        return myText3
        
    def setFont(self, obj):
        if obj.Size.Value <= 0:
            fontSize = 0.1
        else:
            fontSize = obj.Size.Value
            
        #fontName = SoSFName()
        
        myFont = SoFont()
        #myFont.setFontPaths(":/data/fonts/Royalty Savior.ttf")
        myFont.name.setValue(obj.Font)
        myFont.size = fontSize
        #
        myLinearProfile = SoLinearProfile()
        index = (0, 1, 2, 3)
        myLinearProfile.index.setValues(0, 4, index)
        
        return [myFont, myLinearProfile]
        
    def execute(self, obj):
        # FreeCAD.Console.PrintError(str(obj.Spin) + "\n")
        try:
            obj.RootNode.removeChild(self.node)
        except:
            pass
        #
        try:
            font = self.setFont(obj)
            text = self.setText(obj)
            #            
            self.node = SoGroup()
            tmp_node = SoGroup()
            ############
            ############
            tmp_node.addChild(font[0])
            tmp_node.addChild(font[1])
            tmp_node.addChild(text)
            
            c = SoGetBoundingBoxAction(SbViewportRegion())
            c.apply(tmp_node)
            boundingBox = c.getBoundingBox()
            ############
            ############
            if obj.Mirror == 'Local Y axis':
                myTransform1 = SoTransform()
                myTransform1.translation = (0, 0, 0)
                
                wect = SbVec3f()
                wect.setValue(0, 1, 0.)
                rot = SoSFRotation()
                rot.setValue(wect, 3.14)
                
                myTransform1.rotation = rot
                self.node.addChild(myTransform1)
            #elif obj.Mirror == 'Center':
                #x = boundingBox.getCenter().getValue()[0]
                #y = boundingBox.getCenter().getValue()[1]
                
                #myTransform4 = SoTransform()
                #myTransform4.translation = (x, y, 0)
                #wect = SbVec3f()
                #wect.setValue(0, 1, 0.)
                #rot = SoSFRotation()
                #rot.setValue(wect, 3.14)
                
                #myTransform4.rotation = rot
                #self.node.addChild(myTransform4)
                
                
                #myTransform5 = SoTransform()
                #myTransform5.translation = (x * -1, y * -1, 0)
                #self.node.addChild(myTransform5)

            #####
            if not obj.Spin and obj.Object.Rot.Value > 90 and obj.Object.Rot.Value <= 270:
                myTransform1 = SoTransform()
                myTransform1.translation = (0, 0, 0)
                
                wect = SbVec3f()
                wect.setValue(0, 0, 1.)
                rot = SoSFRotation()
                rot.setValue(wect, 3.14)
                
                myTransform1.rotation = rot
                self.node.addChild(myTransform1)
            ############
            ############
            # align
            # "bottom-left"    "bottom-center"    "bottom-right"
            # "center-left"    "center"           "center-right"
            # "top-left"       "top-center"       "top-right"
            if not obj.Spin and obj.Object.Rot.Value > 90 and obj.Object.Rot.Value <= 270:
                if obj.Align == 'center':
                    x = boundingBox.getCenter().getValue()[0] * -1
                    y = boundingBox.getCenter().getValue()[1] * -1
                elif obj.Align == 'center-left':
                    x = boundingBox.getMax().getValue()[0] * -1
                    y = boundingBox.getCenter().getValue()[1] * -1
                elif obj.Align == 'center-right':
                    x = boundingBox.getMin().getValue()[0] * -1
                    y = boundingBox.getCenter().getValue()[1] * -1
                elif obj.Align == 'bottom-left':
                    x = boundingBox.getMax().getValue()[0] * -1
                    y = boundingBox.getMax().getValue()[1] * -1
                elif obj.Align == 'bottom-center':
                    x = boundingBox.getCenter().getValue()[0] * -1
                    y = boundingBox.getMax().getValue()[1] * -1
                elif obj.Align == 'top-left':
                    x = boundingBox.getMax().getValue()[0] * -1
                    y = boundingBox.getMin().getValue()[1] * -1
                elif obj.Align == 'top-center':
                    x = boundingBox.getCenter().getValue()[0] * -1
                    y = boundingBox.getMin().getValue()[1] * -1
                elif obj.Align == 'top-right':
                    x = boundingBox.getMin().getValue()[0] * -1
                    y = boundingBox.getMin().getValue()[1] * -1
                else:  # Align = bottom-right
                    x = boundingBox.getMin().getValue()[0] * -1
                    y = boundingBox.getMax().getValue()[1] * -1
            else:
                if obj.Align == 'center':
                    x = boundingBox.getCenter().getValue()[0] * -1
                    y = boundingBox.getCenter().getValue()[1] * -1
                elif obj.Align == 'center-left':
                    x = boundingBox.getMin().getValue()[0] * -1
                    y = boundingBox.getCenter().getValue()[1] * -1
                elif obj.Align == 'center-right':
                    x = boundingBox.getMax().getValue()[0] * -1
                    y = boundingBox.getCenter().getValue()[1] * -1
                elif obj.Align == 'bottom-left':
                    x = boundingBox.getMin().getValue()[0] * -1
                    y = boundingBox.getMin().getValue()[1] * -1
                elif obj.Align == 'bottom-center':
                    x = boundingBox.getCenter().getValue()[0] * -1
                    y = boundingBox.getMin().getValue()[1] * -1
                elif obj.Align == 'top-left':
                    x = boundingBox.getMin().getValue()[0] * -1
                    y = boundingBox.getMax().getValue()[1] * -1
                elif obj.Align == 'top-center':
                    x = boundingBox.getCenter().getValue()[0] * -1
                    y = boundingBox.getMax().getValue()[1] * -1
                elif obj.Align == 'top-right':
                    x = boundingBox.getMax().getValue()[0] * -1
                    y = boundingBox.getMax().getValue()[1] * -1
                else:  # Align = bottom-right
                    x = boundingBox.getMax().getValue()[0] * -1
                    y = boundingBox.getMin().getValue()[1] * -1
            
            myTransform = SoTransform()
            myTransform.translation = (x, y, 0)
            self.node.addChild(myTransform)
            ############
            # font
            fontColor = SoMaterial()
            fontColor.ambientColor = (0.0, 0.0, 0.0)
            fontColor.diffuseColor = (0.0, 0.0, 0.0) 
            fontColor.specularColor = (0.0, 0.0, 0.0)
            fontColor.reflectiveColor = (1.0, 1.0, 1.0)
            fontColor.emissiveColor = (obj.Color[0], obj.Color[1], obj.Color[2])
            fontColor.shininess = 1.0
            fontColor.transparency = 0.0
            self.node.addChild(fontColor)
            self.node.addChild(font[0])
            self.node.addChild(font[1])
            ############
            # text
            self.node.addChild(text)
            ############
            #return self.node
            obj.RootNode.addChild(self.node)
            #FreeCADGui.ActiveDocument.ActiveView.getSceneGraph().addChild(self.node)
        except:
            pass
            #FreeCAD.Console.PrintWarning(str(e) + "\n")
        
    def getIcon(self):
        ''' Return the icon in XMP format which will appear in the tree view. This method is optional
        and if not defined a default icon is shown.
        '''
        return ":/data/img/annotation_TI.svg"

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
