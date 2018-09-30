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

import FreeCAD
import FreeCADGui
import Part
import os
import re
import builtins
import glob
import unicodedata
import ImportGui
from PySide import QtCore, QtGui
#
from PCBdataBase import dataBase
from PCBconf import *
from PCBboard import getPCBheight
from PCBobjects import partObject, viewProviderPartObject, partObject_E, viewProviderPartObject_E
from PCBfunctions import wygenerujID, getFromSettings_databasePath, mathFunctions
from command.PCBgroups import createGroup_Parts, makeGroup
from command.PCBannotations import createAnnotation


class partsManaging(mathFunctions):
    def __init__(self, databaseType=None):
        self.objColors = {}
        
        # allSocked - definicja zachowania przy dodawaniu podstawki dla wszystkich obeiktow
        #   -1 - brak podstawek
        #    0 - zapytaj o dodanie podstawki (def)
        #    1 - dodaj podstawki dla wszystkich obiektow
        self.allSocked = 0
        self.databaseType = databaseType
    
    def adjustRotation(self, angle):
        if angle > 360 or angle < 360:  # max = 360deg; min= -360deg
            angle = angle % 360
        
        return angle
        
    def updateView(self):
        FreeCADGui.ActiveDocument.ActiveView.viewAxometric()
        FreeCADGui.ActiveDocument.ActiveView.fitAll()
        
    def getPartShape(self, filePath, step_model, koloroweElemnty):
        #if not partExistPath(filePath)[0]:
            #return step_model
        
        if filePath in self.objColors:
            step_model.Shape = self.objColors[filePath]['shape']
            if koloroweElemnty:
                step_model.ViewObject.DiffuseColor = self.objColors[filePath]['col']
            return step_model
        else:
            self.objColors[filePath] = {}
        
        #active = FreeCAD.ActiveDocument.Label
        
        # colFile
        colFile = os.path.join(os.path.dirname(filePath), os.path.splitext(os.path.basename(filePath))[0] + '.col')
        try:
            if os.path.exists(colFile):
                colFileData = builtins.open(colFile, "r").readlines()
                header = colFileData[0].strip().split("|")
                
                if len(header) >= 2 and header[0] == "2" and str(os.path.getmtime(filePath)) == header[1]:  # col file version
                    shape = Part.Shape()
                    shape.importBrepFromString("".join(colFileData[2:]))
                    
                    step_model.Shape = shape
                    if koloroweElemnty:
                        step_model.ViewObject.DiffuseColor = eval(colFileData[1].strip())
                    
                    self.objColors[filePath]['shape'] = shape
                    self.objColors[filePath]['col'] = eval(colFileData[1].strip())
                    
                    if len(colFileData[2:]) > 20:
                        return step_model
        except Exception as e:
            FreeCAD.Console.PrintWarning("{0} \n".format(e))
        ##
        colFileData = builtins.open(colFile, "w")
        colFileData.write("2|{0}\n".format(os.path.getmtime(filePath)))  # wersja|data
        
        FreeCAD.newDocument('importingPartsPCB')
        #FreeCAD.setActiveDocument('importingPartsPCB')
        FreeCAD.ActiveDocument = FreeCAD.getDocument('importingPartsPCB')
        FreeCADGui.ActiveDocument = FreeCADGui.getDocument('importingPartsPCB')
        ImportGui.insert(u"{0}".format(filePath), "importingPartsPCB")
        
        fuse = []
        for i in FreeCAD.ActiveDocument.Objects:
            #if i.isDerivedFrom("Part::Feature") and i.ViewObject.Visibility:
            if i.ViewObject.Visibility and hasattr(i, 'Shape') and hasattr(i.Shape, 'ShapeType') and i.Shape.ShapeType == 'Solid':
                fuse.append(i)
        try:
            if len(fuse) == 1:
                shape = fuse[0].Shape
                col = fuse[0].ViewObject.DiffuseColor
            else:
                newPart = FreeCAD.ActiveDocument.addObject("Part::MultiFuse","Union").Shapes=fuse
                FreeCAD.ActiveDocument.recompute()
            
                shape = FreeCAD.ActiveDocument.getObject("Union").Shape
                col = FreeCAD.ActiveDocument.getObject("Union").ViewObject.DiffuseColor
        except Exception as e:
            FreeCAD.Console.PrintWarning("{0} \n".format(e))
        
        #FreeCADGui.insert(u"{0}".format(filePath), "importingPartsPCB")
        
        colFileData.write(str(col))
        colFileData.write(shape.exportBrepToString())
        colFileData.close()
        
        FreeCAD.closeDocument("importingPartsPCB")
        #FreeCAD.setActiveDocument(active)
        #FreeCAD.ActiveDocument=FreeCAD.getDocument(active)
        #FreeCADGui.ActiveDocument=FreeCADGui.getDocument(active)
        
        step_model.Shape = shape
        if koloroweElemnty:
            step_model.ViewObject.DiffuseColor = col
        
        self.objColors[filePath]['shape'] = shape
        self.objColors[filePath]['col'] = col
        
        return step_model
        
    def addPart(self, newPart, koloroweElemnty=True, adjustParts=False, groupParts=True, partMinX=0, partMinY=0, partMinZ=0):
        doc = FreeCAD.activeDocument()
        gruboscPlytki = getPCBheight()[1]
        result = ['OK']
        
        #grp = doc.addObject("App::DocumentObjectGroup", "Parts")
        
        # basic data
        partNameTXT = partNameTXT_label = self.generateNewLabel(newPart[0][0])
        if isinstance(partNameTXT, str):
            partNameTXT = unicodedata.normalize('NFKD', partNameTXT).encode('ascii', 'ignore')
        #
        partValueTXT = newPart[0][2]
        #if isinstance(partValueTXT, str):
            #partValueTXT = unicodedata.normalize('NFKD', partValueTXT).encode('ascii', 'ignore')
        partRotation = self.adjustRotation(newPart[0][5])  # rotation around Z
        # check if 3D model exist
        #################################################################
        #################################################################
        fileData = self.partExist(newPart[0], "{0} {1} ({2})".format(partNameTXT_label, partValueTXT, newPart[0][1]))
        #fileData [True, u'/home/mariusz/.FreeCAD/Mod/PCB/parts/resistors/R1206.stp', 8, {'software': u'Eagle', 'name': u'R1206', 'rx': 0.0, 'ry': 0.0, 'rz': 0.0, 'y': 0.02, 'x': 0.0, 'z': 0.28, 'id': 22, 'modelID': 8}, 2].
        
        if fileData[0]:
            if fileData[2] > 0:
                modelData = self.__SQL__.getModelByID(fileData[2])
                
                if modelData[0]:
                    modelData = self.__SQL__.convertToTable(modelData[1])
                else:
                    modelData = {'sockedID': 0, 'socketIDSocket': False}
            else:
                modelData = {'add_socket':'[False,None]'}
            
            filePath = fileData[1]
            correctingValue_X = fileData[3]['x']  # pos_X
            correctingValue_Y = fileData[3]['y']  # pos_Y
            correctingValue_Z = fileData[3]['z']  # pos_Z
            correctingValue_RX = fileData[3]['rx']  # pos_RX
            correctingValue_RY = fileData[3]['ry']  # pos_RY
            correctingValue_RZ = fileData[3]['rz']  # pos_RZ
            
            ################################################################
            # DODANIE OBIEKTU NA PLANSZE
            ################################################################
            step_model = doc.addObject("Part::FeaturePython", "{0} ({1})".format(partNameTXT, fileData[3]['name']))
            step_model.Label = partNameTXT_label
            
            if not koloroweElemnty:
                step_model.Shape = Part.read(filePath)
            else:
                active = FreeCAD.ActiveDocument.Name
                try:
                    step_model = self.getPartShape(filePath, step_model, koloroweElemnty)
                    step_model.Shape.isValid()
                except:
                    step_model.Shape = Part.read(filePath)
                
                FreeCAD.setActiveDocument(active)
                FreeCAD.ActiveDocument=FreeCAD.getDocument(active)
                FreeCADGui.ActiveDocument=FreeCADGui.getDocument(active)
            
            obj = partObject(step_model)
            step_model.Package = u"{0}".format(fileData[3]['name'])
            step_model.Side = "{0}".format(newPart[0][6])
            ################################################################
            # PUTTING OBJECT IN CORRECT POSITION/ORIENTATION
            ################################################################
            # rotate object according to (RX, RY, RZ) set by user
            sX = step_model.Shape.BoundBox.Center.x * (-1) + step_model.Placement.Base.x
            sY = step_model.Shape.BoundBox.Center.y * (-1) + step_model.Placement.Base.y
            sZ = step_model.Shape.BoundBox.Center.z * (-1) + step_model.Placement.Base.z + gruboscPlytki / 2.
            
            rotateX = correctingValue_RX
            rotateY = correctingValue_RY
            rotateZ = correctingValue_RZ
            
            pla = FreeCAD.Placement(step_model.Placement.Base, FreeCAD.Rotation(rotateX, rotateY, rotateZ), FreeCAD.Base.Vector(sX, sY, sZ))
            step_model.Placement = pla
            
            ## placement object to 0, 0, PCB_size / 2. (X, Y, Z)
            sX = step_model.Shape.BoundBox.Center.x * (-1) + step_model.Placement.Base.x
            sY = step_model.Shape.BoundBox.Center.y * (-1) + step_model.Placement.Base.y
            sZ = step_model.Shape.BoundBox.Center.z * (-1) + step_model.Placement.Base.z + gruboscPlytki / 2.

            step_model.Placement.Base.x = sX + correctingValue_X
            step_model.Placement.Base.y = sY + correctingValue_Y
            step_model.Placement.Base.z = sZ
            
            # move object to correct Z
            step_model.Placement.Base.z = step_model.Placement.Base.z + (gruboscPlytki - step_model.Shape.BoundBox.Center.z) + correctingValue_Z
            #################################################################
            # FILTERING OBJECTS BY SIZE L/W/H
            #################################################################
            if partMinX != 0:
                minValue = partMinX
                if step_model.Side == 'TOP':
                    minValue += gruboscPlytki
                
                if step_model.Shape.BoundBox.XLength < minValue:
                    doc.removeObject(step_model.Name)
                    return
            elif partMinY != 0:
                minValue = partMinY
                if step_model.Side == 'TOP':
                    minValue += gruboscPlytki
                
                if step_model.Shape.BoundBox.YLength < minValue:
                    doc.removeObject(step_model.Name)
                    return
            elif partMinZ != 0:
                minValue = partMinZ
                if step_model.Side == 'TOP':
                    minValue += gruboscPlytki
                
                if step_model.Shape.BoundBox.ZLength < minValue:
                    doc.removeObject(step_model.Name)
                    return
            #################################################################
            # SETTTING OBJECT SIDE ON THE PCB
            #################################################################
            if newPart[0][6] == 'BOTTOM':
                # ROT Y - MIRROR
                shape = step_model.Shape.copy()
                shape.Placement = step_model.Placement
                shape.rotate((0, 0, gruboscPlytki / 2.), (0.0, 1.0, 0.0), 180)
                step_model.Placement = shape.Placement
                
                # ROT Z - VALUE FROM EAGLE
                shape = step_model.Shape.copy()
                shape.Placement = step_model.Placement
                shape.rotate((0, 0, 0), (0.0, 0.0, 1.0), -partRotation)
                step_model.Placement = shape.Placement
            else:
                # ROT Z - VALUE FROM EAGLE
                shape = step_model.Shape.copy()
                shape.Placement = step_model.Placement
                shape.rotate((0, 0, 0), (0.0, 0.0, 1.0), partRotation)
                step_model.Placement = shape.Placement
            #################################################################
            # placement object to X, Y set in eagle
            #################################################################
            step_model.Placement.Base.x = step_model.Placement.Base.x + newPart[0][3]
            step_model.Placement.Base.y = step_model.Placement.Base.y + newPart[0][4]
            #################################################################
            # 
            #################################################################
            step_model.X = step_model.Shape.BoundBox.Center.x
            step_model.Y = step_model.Shape.BoundBox.Center.y
            step_model.Proxy.oldX = step_model.Shape.BoundBox.Center.x
            step_model.Proxy.oldY = step_model.Shape.BoundBox.Center.y
            step_model.Proxy.offsetX = correctingValue_X
            step_model.Proxy.offsetY = correctingValue_Y
            step_model.Proxy.oldROT = partRotation
            step_model.Rot = partRotation
            step_model.Proxy.update_Z = step_model.Placement.Base.z
            #################################################################
            # DODANIE PODSTAWKI
            #   dodajPodstawke - definicja zachowania dla danego obiektu
            #     0 - brak podstawki
            #     1 - dodanie podstawki
            #################################################################
            dodajPodstawke = False
            
            if modelData['socketIDSocket'] and self.allSocked == 0 and modelData['socketID'] != fileData[2]:
                socketData = self.__SQL__.convertToTable(self.__SQL__.getModelByID(modelData['socketID'])[1])
                
                if socketData["isSocket"]:
                    dial = QtGui.QMessageBox()
                    dial.setText(u"Add socket to part {0} (Package: {1}, Library: {2})?".format(partNameTXT, newPart[0][1], newPart[0][7]))
                    dial.setWindowTitle("Socket")
                    dial.setIcon(QtGui.QMessageBox.Question)
                    dial.addButton('No', QtGui.QMessageBox.RejectRole)
                    podstawkaTAK = dial.addButton('Yes', QtGui.QMessageBox.YesRole)
                    zawszePodstawki = dial.addButton('Yes for all', QtGui.QMessageBox.YesRole)
                    nigdyPodstawki = dial.addButton('No for all', QtGui.QMessageBox.RejectRole)
                    dial.exec_()
                    
                    if dial.clickedButton() == nigdyPodstawki:
                        self.allSocked = -1
                    elif dial.clickedButton() == zawszePodstawki:
                        self.allSocked = 1
                    elif dial.clickedButton() == podstawkaTAK:
                        dodajPodstawke = True
                    else:
                        dodajPodstawke = False
            #
            if (dodajPodstawke or self.allSocked == 1) and modelData['socketIDSocket']:
                socketData = self.__SQL__.convertToTable(self.__SQL__.getModelByID(modelData['socketID'])[1])
                
                step_model.Socket = socketData["isSocketHeight"]  # ustawienie wysokosci podstawki
                EL_Name = [socketData["name"], newPart[0][3], newPart[0][4], 1.27, newPart[0][5], newPart[0][6], "bottom-left", False, 'None', '', True]
                EL_Value = ["", newPart[0][3], newPart[0][4], 1.27, newPart[0][5], newPart[0][6], "bottom-left", False, 'None', '', True]
                PCB_EL = [[socketData["name"], socketData["name"], "", newPart[0][3], newPart[0][4], newPart[0][5], newPart[0][6], ""], EL_Name, EL_Value]

                self.addPart(PCB_EL, koloroweElemnty, adjustParts, groupParts, partMinX, partMinY, partMinZ)
            ##################################################################
            ## part name object
            ## [txt, x, y, size, rot, side, align, spin, mirror, font]
            ##################################################################
            annotationName = createAnnotation()
            annotationName.defaultName = '{0}_Name'.format(partNameTXT_label)
            annotationName.mode = 'anno_name'
            annotationName.Side = newPart[1][5]
            annotationName.Rot = self.adjustRotation(newPart[1][4])
            annotationName.Text = partNameTXT_label
            annotationName.Spin = newPart[1][7]
            
            if adjustParts and "adjust" in modelData.keys() and "Name" in eval(modelData["adjust"]).keys() and eval(str(eval(modelData["adjust"])["Name"][0])):
                values = eval(modelData["adjust"])["Name"]
                
                if step_model.Side == "BOTTOM":
                    x1 = self.odbijWspolrzedne(newPart[0][3] + values[2], step_model.X.Value)
                    annotationName.Mirror = True
                    
                    [xR, yR] = self.obrocPunkt2([x1, newPart[0][4] + values[3]], [step_model.X.Value, step_model.Y.Value], -step_model.Rot.Value)
                else:
                    annotationName.Mirror = False
                    
                    [xR, yR] = self.obrocPunkt2([newPart[0][3] + values[2], newPart[0][4] + values[3]], [step_model.X.Value, step_model.Y.Value], step_model.Rot.Value)
                
                annotationName.X = xR
                annotationName.Y = yR
                annotationName.Z = values[4]
                annotationName.Align = str(values[7])
                annotationName.Size = values[5]
                annotationName.Color = values[6]
                annotationName.Visibility = eval(values[1])
            else:
                annotationName.X = newPart[1][1]
                annotationName.Y = newPart[1][2]
                annotationName.Z = 0
                annotationName.Align = newPart[1][6]
                annotationName.Size = newPart[1][3]
                annotationName.Mirror = newPart[1][8]
                annotationName.Color = (1., 1., 1.)
                annotationName.Visibility = newPart[1][10]
            
            #annotationName.generate()
            #################################################################
            # part value
            # [txt, x, y, size, rot, side, align, spin, mirror, font]
            #################################################################
            annotationValue = createAnnotation()
            annotationValue.defaultName = '{0}_Value'.format(partNameTXT_label)
            annotationValue.mode = 'anno_value'
            annotationValue.Side = newPart[2][5]
            annotationValue.Rot = self.adjustRotation(newPart[2][4])
            annotationValue.Text = partValueTXT
            annotationValue.Spin = newPart[2][7]
            
            if adjustParts and "adjust" in modelData.keys() and "Value" in eval(modelData["adjust"]).keys() and eval(str(eval(modelData["adjust"])["Value"][0])):
                values = eval(modelData["adjust"])["Value"]
                
                if step_model.Side == "BOTTOM":
                    x1 = self.odbijWspolrzedne(newPart[0][3] + values[2], step_model.X.Value)
                    annotationValue.Mirror = True
                    
                    [xR, yR] = self.obrocPunkt2([x1, newPart[0][4] + values[3]], [step_model.X.Value, step_model.Y.Value], -step_model.Rot.Value)
                else:
                    annotationValue.Mirror = False
                    
                    [xR, yR] = self.obrocPunkt2([newPart[0][3] + values[2], newPart[0][4] + values[3]], [step_model.X.Value, step_model.Y.Value], step_model.Rot.Value)
                
                annotationValue.X = xR
                annotationValue.Y = yR
                annotationValue.Z = values[4]
                annotationValue.Align = str(values[7])
                annotationValue.Size = values[5]
                annotationValue.Color = values[6]
                annotationValue.Visibility = eval(values[1])
            else:
                annotationValue.X = newPart[2][1]
                annotationValue.Y = newPart[2][2]
                annotationValue.Z = 0
                annotationValue.Align = newPart[2][6]
                annotationValue.Size = newPart[2][3]
                annotationValue.Mirror = newPart[2][8]
                annotationValue.Color = (1., 1., 1.)
                annotationValue.Visibility = newPart[2][10]
            
            #annotationValue.generate()
            #
            step_model.PartName = annotationName.Annotation
            step_model.PartValue = annotationValue.Annotation
            ################
            viewProviderPartObject(step_model.ViewObject)
            #################################################################
            # KOLORY DLA ELEMENTOW
            #################################################################
            #if koloroweElemnty:
                #if filePath.upper().endswith('.IGS') or filePath.upper().endswith('IGES'):
                    #step_model = self.getColorFromIGS(filePath, step_model)
                #elif filePath.upper().endswith('.STP') or filePath.upper().endswith('STEP'):
                    #step_model = self.getColorFromSTP(filePath, step_model)
        else:
            #################################################################
            # FILTERING OBJECTS BY SIZE L/W/H
            #################################################################
            if partMinX != 0 or partMinY or partMinZ:
                return
            #################################################################
            #################################################################
            ## DODANIE OBIEKTU NA PLANSZE
            step_model = doc.addObject("Part::FeaturePython", "{0} ({1})".format(partNameTXT, newPart[0][1]))
            step_model.Label = partNameTXT_label
            obj = partObject_E(step_model)
            #step_model.Label = partNameTXT
            step_model.Package = "{0}".format(newPart[0][1])
            #step_model.Value = "{0}".format(i[0][2])
            #####
            # placement object to X, Y set in eagle
            step_model.Placement.Base.x = step_model.Placement.Base.x + newPart[0][3]
            step_model.Placement.Base.y = step_model.Placement.Base.y + newPart[0][4]
            
            # move object to correct Z
            step_model.Placement.Base.z = step_model.Placement.Base.z + gruboscPlytki
            #####
            step_model.Side = "{0}".format(newPart[0][6])
            step_model.X = newPart[0][3]
            step_model.Y = newPart[0][4]
            step_model.Rot = partRotation
            step_model.Proxy.update_Z = 0
            ######
            ######
            # part name object
            # [txt, x, y, size, rot, side, align, spin, mirror, font]
            annotationName = createAnnotation()
            annotationName.defaultName = u'{0}_Name'.format(partNameTXT_label)
            annotationName.mode = 'anno_name'
            annotationName.X = newPart[1][1]
            annotationName.Y = newPart[1][2]
            annotationName.Z = 0
            annotationName.Side = newPart[1][5]
            annotationName.Rot = self.adjustRotation(newPart[1][4])
            annotationName.Text = partNameTXT_label
            annotationName.Align = newPart[1][6]
            annotationName.Size = newPart[1][3]
            annotationName.Spin = newPart[1][7]
            annotationName.Mirror = newPart[1][8]
            annotationName.Visibility = newPart[1][10]
            annotationName.Color = (1., 1., 1.)
            #annotationName.generate()
            # part value
            # [txt, x, y, size, rot, side, align, spin, mirror, font]
            annotationValue = createAnnotation()
            annotationValue.defaultName = u'{0}_Value'.format(partNameTXT_label)
            annotationValue.mode = 'anno_value'
            annotationValue.X = newPart[2][1]
            annotationValue.Y = newPart[2][2]
            annotationValue.Z = 0
            annotationValue.Side = newPart[2][5]
            annotationValue.Rot = self.adjustRotation(newPart[2][4])
            annotationValue.Text = partValueTXT
            annotationValue.Align = newPart[2][6]
            annotationValue.Size = newPart[2][3]
            annotationValue.Spin = newPart[2][7]
            annotationValue.Mirror = newPart[2][8]
            annotationValue.Visibility = newPart[2][10]
            annotationValue.Color = (1., 1., 1.)
            #annotationValue.generate()
            #
            step_model.PartName = annotationName.Annotation
            step_model.PartValue = annotationValue.Annotation
            ######
            ######
            viewProviderPartObject_E(step_model.ViewObject)
            #################################################################
            result = ['Error']
        ######
        result.append(step_model)
        try:
            self.addPartToGroup(groupParts, fileData[4], step_model)
        except:
            self.addPartToGroup(groupParts, False, step_model)  # Missing categoory
        #self.updateView()
        return result
    
    def addPartToGroup(self, groupParts, categoryID, step_model):
        try:
            FreeCAD.ActiveDocument.removeObject(step_model.InList[0].Label)
        except Exception as e:
            pass
        
        try:
            step_model.InList[0].removeObject(step_model)
        except:
            pass
        #
        grp = createGroup_Parts()
        
        if groupParts:
            try:
                if categoryID in [-1, 0]:
                    grp_2 = makeGroup('Others')
                else:
                    categoryData = self.__SQL__.getCategoryByID(int(categoryID))
                    if categoryData:
                        grp_2 = makeGroup(categoryData.name)
                    else:
                        grp_2 = makeGroup('Others')
            except:
                grp_2 = makeGroup('Missing')
            
            grp_2.addObject(step_model)
            grp.addObject(grp_2)
        else:
            grp.addObject(step_model)
    
    def getObjRot(self, obj):
        rx = obj.Placement.Rotation.Q[0]
        ry = obj.Placement.Rotation.Q[1]
        rz = obj.Placement.Rotation.Q[2]
        angle = obj.Placement.Rotation.Angle * 180. / 3.14

        return [rx, ry, rz, angle]
        
    #def axisAngleToEuler(self, x, y, z, angle):
        #angle = angle * 3.14 / 180
        #s = sin(angle)
        #c = cos(angle)
        #t = 1 - c
        
        #if (x * y * t + z * s) > 0.998:
            #heading = 2 * atan2(x * sin(angle / 2), cos(angle / 2))
            #attitude = pi / 2
            #bank = 0
            ##return [heading, attitude, bank]
            #return [bank, heading, attitude]
        #if (x * y * t + z * s) < -0.998:
            #heading = -2 * atan2(x * sin(angle / 2), cos(angle / 2))
            #attitude = -pi / 2
            #bank = 0
            ##return [heading, attitude, bank]
            #return [bank, heading, attitude]
        
        #heading = atan2(y * s- x * z * t , 1 - (y * y + z * z ) * t)
        #attitude = asin(x * y * t + z * s)
        #bank = atan2(x * s - y * z * t , 1 - (x * x + z * z) * t)
        
        ##return [heading, attitude, bank]
        #return [bank, heading, attitude]
    
    #def quaternionToEuler(self, x, y, z, w):
        #test = x * y + z * w
        #if test > 0.499:
            #heading = 2 * atan2(x, w)
            #attitude = pi / 2
            #bank = 0
            
            #return [heading*180/3.14, attitude*180/3.14, bank*180/3.14]
        #if test < -0.499:
            #heading = -2 * atan2(x, w)
            #attitude = - pi / 2;
            #bank = 0
            
            #return [heading*180/3.14, attitude*180/3.14, bank*180/3.14]
        
        #sqx = x * x
        #sqy = y * y
        #sqz = z * z
        
        #heading = atan2(2 * y * w - 2 * x * z , 1 - 2 * sqy - 2 * sqz)
        #attitude = asin(2 * test)
        #bank = atan2(2 * x * w - 2 * y * z , 1 - 2 * sqx - 2 * sqz)
        
        #return [heading*180/3.14, attitude*180/3.14, bank*180/3.14]
        
    #def toQuaternion(self, pitch, yaw, roll):
        #''' Quaternion from Euler angles '''
        #p = pitch / 2.
        #y = yaw / 2.
        #r = roll / 2.
        
        #sin_p = sin(p)
        #sin_y = sin(y)
        #sin_r = sin(r)
        #cos_p = cos(p)
        #cos_y = cos(y)
        #cos_r = cos(r)
        
        #x = sin_r * cos_p * cos_y - cos_r * sin_p * sin_y
        #y = cos_r * sin_p * cos_y + sin_r * cos_p * sin_y
        #z = cos_r * cos_p * sin_y - sin_r * sin_p * cos_y
        #w = cos_r * cos_p * cos_y + sin_r * sin_p * sin_y
        
        #return FreeCAD.Base.Rotation(x, y, z, w)
        
    def generateNewLabel(self, label):
        #if isinstance(label, str):
            #label = unicodedata.normalize('NFKD', label).encode('ascii', 'ignore')
        
        if label.strip() == "":
            return wygenerujID(3, 3)
        else:
            return label
            
    def getColorFromSTP(self, filePath, step_model):
        try:
            ################################################################
            # paletaKolorow zawiera tablice okreslajace kolory poszczegolnych plaszczyzn
            # paletaKolorow = [(R, G, B), (R, G, B), itd]
            ################################################################
            if filePath in self.objColors:
                step_model.ViewObject.DiffuseColor = self.objColors[filePath] # ustawienie kolorow dla obiektu
                return step_model
            #
            colFile = os.path.join(os.path.dirname(filePath), os.path.splitext(os.path.basename(filePath))[0] + '.col')
            if os.path.exists(colFile):
                colFileData = builtins.open(colFile, "r").readlines()
                header = colFileData[0].strip().split("|")
                
                if len(header) >= 2 and header[0] == "2" and str(os.path.getmtime(filePath)) == header[1]:  # col file version
                #if str(os.path.getmtime(filePath)) == colFileData[0].strip():
                    try:
                        step_model.ViewObject.DiffuseColor = eval(colFileData[1].strip())
                        self.objColors[filePath] = eval(colFileData[1].strip())
                        return step_model
                    except:
                        pass
            
            colFileData = builtins.open(colFile, "w")
            colFileData.write("{0}\n".format(os.path.getmtime(filePath)))
            #
            plik = builtins.open(filePath, "r").read().replace('\r\n', '').replace('\r', '').replace('\\n', '').replace('\n', '')
            paletaKolorow = []
            # v2
            defColors = {}
            for k in re.findall("#([0-9]+) = CLOSED_SHELL\('',\((.+?)\).+?;", plik):
                for j in k[1].split(','):
                    try:
                        STYLED_ITEM = re.findall("STYLED_ITEM\('color',\(#([0-9]+)\),{0}\);".format(j.strip()), plik)[0].strip()
                        colNum = j.strip()
                    except:
                        part = re.search("#([0-9]+) = MANIFOLD_SOLID_BREP\('',#{0}\);".format(k[0]), plik).groups()[0]
                        STYLED_ITEM = re.findall("STYLED_ITEM\('color',\(#([0-9]+)\),#{0}\);".format(part.strip()), plik)[0].strip()
                        colNum = part.strip()
                        
                    if colNum in defColors:
                        paletaKolorow.append(defColors[colNum])
                        continue
                    
                    PRESENTATION_STYLE_ASSIGNMENT = int(re.findall("#{0} = PRESENTATION_STYLE_ASSIGNMENT[\s]?\(\([\s]?#([0-9]+?)[\s]?[,|\)]".format(STYLED_ITEM), plik)[0])
                    SURFACE_STYLE_USAGE = int(re.findall("#{0} = SURFACE_STYLE_USAGE[\s]?\(.+?,[\s]?#(.+?)[\s]?\)[\s]?;".format(PRESENTATION_STYLE_ASSIGNMENT), plik)[0])
                    SURFACE_SIDE_STYLE = int(re.findall("#{0} = SURFACE_SIDE_STYLE[\s]?\(.+?,\([\s]?#(.+?)[\s]?\)".format(SURFACE_STYLE_USAGE), plik)[0])
                    SURFACE_STYLE_FILL_AREA = int(re.findall("#{0} = SURFACE_STYLE_FILL_AREA[\s]?\([\s]?#(.+?)[\s]?\)".format(SURFACE_SIDE_STYLE), plik)[0])
                    FILL_AREA_STYLE = int(re.findall("#{0} = FILL_AREA_STYLE[\s]?\(.+?,\([\s]?#(.+?)[\s]?\)".format(SURFACE_STYLE_FILL_AREA), plik)[0])
                    FILL_AREA_STYLE_COLOUR = int(re.findall("#{0} = FILL_AREA_STYLE_COLOUR[\s]?\(.+?,[\s]?#(.+?)[\s]?\)".format(FILL_AREA_STYLE), plik)[0])
                    defKoloru = re.findall("#{0} = (.+?);".format(int(FILL_AREA_STYLE_COLOUR)), plik)[0]
                    
                    matchObj = re.match("DRAUGHTING_PRE_DEFINED_COLOUR[\s]?\([\s]?'(.*)'[\s]?\)", defKoloru)
                    if matchObj:
                        paletaKolorow.append(spisKolorowSTP[matchObj.groups()[0]])
                        defColors[colNum] = spisKolorowSTP[matchObj.groups()[0]]
                    else:
                        matchObj = re.match("COLOUR_RGB[\s]?\([\s]?'',[\s]?(.*),[\s]?(.*),[\s]?(.*)[\s]?\)", defKoloru)
                        if matchObj:
                            paletaKolorow.append((float(matchObj.groups()[0]), float(matchObj.groups()[1]), float(matchObj.groups()[2])))
                            defColors[colNum] = (float(matchObj.groups()[0]), float(matchObj.groups()[1]), float(matchObj.groups()[2]))
            ##
            step_model.ViewObject.DiffuseColor = paletaKolorow  # ustawienie kolorow dla obiektu
            self.objColors[filePath] = paletaKolorow
            colFileData.write(str(paletaKolorow))
            colFileData.close()
        except Exception as e:
            FreeCAD.Console.PrintWarning(u"Error 1b: {0} \n".format(e))
        return step_model

    def getColorFromIGS(self, filePath, step_model):
        try:
            ################################################################
            # paletaKolorow zawiera tablice okreslajace kolory poszczegolnych plaszczyzn
            # paletaKolorow = [(R, G, B), (R, G, B), itd]
            paletaKolorow = []
            ################################################################
            if filePath in self.objColors:
                step_model.ViewObject.DiffuseColor = self.objColors[filePath] # ustawienie kolorow dla obiektu
                return step_model
            #
            colFile = os.path.join(os.path.dirname(filePath), os.path.splitext(os.path.basename(filePath))[0] + '.col')
            if os.path.exists(colFile):
                colFileData = builtins.open(colFile, "r").readlines()
                header = colFileData[0].strip().split("|")
                
                if len(header) >= 2 and header[0] == "2" and str(os.path.getmtime(filePath)) == header[1]:  # col file version
                #if str(os.path.getmtime(filePath)) == colFileData[0].strip():
                    try:
                        step_model.ViewObject.DiffuseColor = eval(colFileData[1].strip())
                        self.objColors[filePath] = eval(colFileData[1].strip())
                        return step_model
                    except:
                        pass
            
            colFileData = builtins.open(colFile, "w")
            colFileData.write("{0}\n".format(os.path.getmtime(filePath)))
            #
            plik = builtins.open(filePath, "r").readlines()
            
            stopka = plik[-1]  # stopka okresla ile lini zawiera naglowek oraz poszczegolne czesci pliku
            dlugoscSTART = int(re.search('S.*G', stopka).group(0)[1:-1])  # S = Start Sender comments
            dlugoscNAGLOWEK = int(re.search('G.*D', stopka).group(0)[1:-1])  # G = Global General file characteristics
            dlugoscMAIN_1 = int(re.search('D.*P', stopka).group(0)[1:-1])  # D = Directory Entry Entity index and common attributes
            #dlugoscMAIN_2 = int(re.search('P.*T', stopka).group(0)[1:-1])  # P = Parameter Data Entity data
            
            dodatkoweDane = plik[dlugoscSTART + dlugoscNAGLOWEK + dlugoscMAIN_1: -1]  # dodatkoweDane = PARAMETER DATA
            # dane = plik[dlugoscSTART+dlugoscNAGLOWEK : dlugoscSTART+dlugoscNAGLOWEK+dlugoscMAIN_1]
            daneKolory = plik[dlugoscSTART + dlugoscNAGLOWEK: dlugoscSTART + dlugoscNAGLOWEK + dlugoscMAIN_1]  # daneKolory = DIRECTORY ENTITY
            
            ################################################################
            # niektore programy elementy grupuja w obiekcie 308 - Subfigure Definition Entity
            # sprawdzamy czy mamy doczynienia z takim rodzajem zapisu
            obj_308 = [pp for pp in daneKolory if re.search("^ *308.*", pp)]
            ################################################################
            nr = 0
            
            for pp in range(len(daneKolory)):
                if len(obj_308):  # np. SolidWorks
                    ################################################################
                    #  408 - Singular Subfigure Instance Entity
                    ################################################################
                    if re.search("^ *408.*", daneKolory[pp]):
                        if not nr:
                            nr = 1
                            ################################################################
                            #  zmienna param_308 zawiera poczatkowa linie elementu 308 (spis poszczegolnych obiektow 144)
                            #  odwolujemy sie do niej za pomoca 408
                            nr_308 = int(re.split(" *", daneKolory[pp])[2])
                            nr_308 = int(dodatkoweDane[nr_308 - 1].split(',')[1])
                            nr_308 = int(re.split(" *", daneKolory[nr_308 - 1])[2])
                            param_308 = dodatkoweDane[nr_308 - 1].split(',')[:-1]
                            ################################################################
                            ################################################################
                            # zmienna param_308 zawiera poczatkowa linie elementu 308 (spis poszczegolnych obiektow 144)
                            # param_308[3] - liczba elementow 144 zawartych w ramach jednego elementu 308
                            # len(param_308) > 3; param_308[2] - nazwa elementu, zbyt dluga powoduje przerzucenie do nastepnej linijki
                            #   parametru param_308[3]
                            if len(param_308) > 3:
                                liczba_144 = int(param_308[3])
                                danu = [param_308[4:]]
                                nan = nr_308
                            else:
                                param_308 = dodatkoweDane[nr_308].split(',')[:-1]
                                try:
                                    liczba_144 = int(param_308[0])
                                    danu = [param_308[1:]]
                                except:
                                    liczba_144 = int(param_308[1])
                                    danu = [param_308[2:]]
                                nan = nr_308 + 1
                            ################################################################
                            ################################################################
                            #  pobieramy poszczegolne elementy 144 zgrupowane w ramach 308
                            for j in range(liczba_144):
                                #param = dodatkoweDane[nan].split(',')
                                if re.search("^.*;.*", dodatkoweDane[nan]):
                                    danu.append(dodatkoweDane[nan].split(','))
                                    danu[-1][-1] = danu[-1][-1].split(';')[0]
                                    break
                                danu.append(dodatkoweDane[nan].split(',')[:-1])
                                nan += 1
                            
                            paramu = []
                            for j in danu:
                                paramu += j
                            ################################################################
                            ################################################################
                            #  wyciagamy kolory poszczegolnych plaszczyzn
                            for j in paramu:
                                kolor = int(re.split(" *", daneKolory[int(j)])[3])
                                if kolor >= 0:  # standardowy kolor IGS
                                    paletaKolorow.append(spisKolorow[kolor])
                                else:  # zdefiniowany w pliku kolor, 314 - Color Definition Entity
                                    kolor = daneKolory[(kolor * -1) - 1]
                                    kolor = int(re.split(" *", kolor)[2])
                                    kolor = dodatkoweDane[kolor - 1].split(',')
                                    
                                    R = float(kolor[1]) / 100.
                                    G = float(kolor[2]) / 100.
                                    B = float(kolor[3]) / 100.
                                    paletaKolorow.append((R, G, B))
                            ################################################################
                        else:
                            nr = 0
                            continue
                ################################################################
                #  144 - Trimmed (Parametric) Surface Entity
                ################################################################
                else:  # np. CATIA
                    if re.search("^ *144.*", daneKolory[pp]):
                        if nr:
                            nr = 0
                            ################################################################
                            #  wyciagamy kolory poszczegolnych plaszczyzn
                            kolor = int(re.split(" *", daneKolory[pp])[3])
                            if kolor >= 0:  # standardowy kolor IGS
                                paletaKolorow.append(spisKolorow[kolor])
                            else:  # zdefiniowany w pliku kolor, 314 - Color Definition Entity
                                kolor = daneKolory[(kolor * -1) - 1]
                                kolor = int(re.split(" *", kolor)[2])
                                kolor = dodatkoweDane[kolor - 1].split(',')
                                
                                R = float(kolor[1]) / 100.
                                G = float(kolor[2]) / 100.
                                B = float(kolor[3]) / 100.
                                paletaKolorow.append((R, G, B))
                            ################################################################
                        else:
                            nr = 1
                            continue
            step_model.ViewObject.DiffuseColor = paletaKolorow  # ustawienie kolorow dla obiektu
            self.objColors[filePath] = paletaKolorow
            colFileData.write(str(paletaKolorow))
            colFileData.close()
        except Exception as e:
            FreeCAD.Console.PrintWarning(u"Error 1a: {0} \n".format(e))
        
        return step_model
    
    def setDatabase(self):
        self.__SQL__ = dataBase()
        self.__SQL__.connect()

    def partExist(self, info, model, showDial=True):
        if not self.databaseType:
            return [False]
        
        try:
            name = info[1]
            
            databaseType = self.databaseType
            if databaseType in ['kicad_v3', 'kicad_v4']:
                databaseType = 'kicad'
            
            #
            #modelInfo = getExtensionInfo(info, 'model')
            #if modelInfo:  # kicad users
                #[found, path] = partExistPath(modelInfo['path'])
                #if found:
                    #at = modelInfo['at']
                    #modelInfo.pop('at')
                    #rotate = modelInfo['rotate']
                    #modelInfo.pop('rotate')

                    ##if databaseType == 'kicad': 
                        ## This is what I think how FreeCAD-PCB places objects.
                        ## 
                        ## 1) After loading the model, it will move the object so that it centers at the origin.
                        ## 2) Rotate the object with the angles stored in the database using x, y and z as rotation 
                        ##    axis. In other word, FreeCAD-PCB stores the rotation as yaw, pitch and roll.
                        ## 3) Move the object to its final position using the translation stored in the database.
                        ##
                        ## However, kicad has no step 1), which is why we need to adjust the placement as follow.
                        ## Do a yaw, pitch, roll rotation of the object center vector. Add the resulting vector
                        ## to the translation.
                        ##pos = FreeCAD.Placement(\
                                    ##FreeCAD.Base.Vector(0.0,0.0,0.0), \
                                    ##FreeCAD.Rotation(rotate[0], rotate[1], rotate[2]), \
                                    ##FreeCAD.Base.Vector(0.0,0.0,0.0)).multVec(shape.BoundBox.Center)
                        ##at[0] += pos.x
                        ##at[1] += pos.y
                        ##at[2] += pos.z

                    #modelSoft = [name,supSoftware[databaseType]['name']]
                    #modelSoft.extend(at)
                    #modelSoft.extend(rotate)
                    #modelInfo['soft'] = str([modelSoft])

                    #return [True, path, '', modelSoft, -1]; 
            #################
            package = self.__SQL__.findPackage(name, supSoftware[databaseType]['name'])
            
            if package:
                modelData = self.__SQL__.getModelByID(package.modelID)
                
                if modelData[0]:
                    modelData = self.__SQL__.convertToTable(modelData[1])
                    filePos = modelData["path3DModels"]
                    
                    # multi models definition for one part
                    if isinstance(model, str):
                        model = unicodedata.normalize('NFKD', model).encode('ascii', 'ignore')
                        #if len(filePos.split(';')) > 1:
                        #return [False]
                    if len(filePos.split(';')) > 1 and showDial:
                        #active = FreeCAD.ActiveDocument.Label
                        dial = modelTypes(model, filePos.split(';'))
                        
                        if dial.exec_():
                            filePos = str(dial.modelsList.currentItem().text())
                        else:
                            return [False]
                        #FreeCAD.setActiveDocument(active)
                        #FreeCAD.ActiveDocument=FreeCAD.getDocument(active)
                        #FreeCADGui.ActiveDocument=FreeCADGui.getDocument(active)
                    ######################################
                    [boolValue, path] = partExistPath(filePos)
                    if boolValue:
                        return [True, path, modelData['id'], self.__SQL__.convertToTable(package), modelData['categoryID']]
                    else:
                        return [False]
                else:
                    return [False]
            return [False]
        except Exception as e:
            FreeCAD.Console.PrintWarning(u"Error partExist(): {0} \n".format(e))
            return [False]
            #FreeCAD.Console.PrintWarning(u"Error 2: {0} \n".format(e))
            #return [False]


def partExistPath(filePos):
    #if filePos.startswith('/'):
        #filePos = filePos[1:]
    filePos = filePos.strip()
    #
    if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("partsPaths", "").strip() != '':
        pathsToModels = partPaths + FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("partsPaths", "").split(',')
    else:
        pathsToModels = partPaths
    #
    if filePos.endswith((".igs", ".IGS", ".Igs", ".stp", "STEP", "step", "STP")):
        if len(glob.glob(filePos)):  # absolute path
            return [True, glob.glob(filePos)[0]]
        else:  # relative path - path def in partPaths (conf.py file)
            for i in pathsToModels:
                if i.strip() != '' and len(glob.glob(os.path.join(i.strip(), filePos))):
                    return [True, glob.glob(os.path.join(i, filePos))[0]]
            return [False, False]
    else:
        if len(glob.glob(filePos + ".[i,I]*")):  # absolute path
            return [True, glob.glob(filePos + ".[i,I]*")[0]]
        elif len(glob.glob(filePos + ".[s,S]*")):  # absolute path
            return [True, glob.glob(filePos + ".[s,S]*")[0]]
        else:  # relative path - path def in partPaths (conf.py file)
            for i in pathsToModels:
                if i.strip() != '':
                    if len(glob.glob(os.path.join(i, filePos) + ".[i,I]*")):
                        return [True, glob.glob(os.path.join(i, filePos) + ".[i,I]*")[0]]
                    elif len(glob.glob(os.path.join(i, filePos) + ".[s,S]*")):
                        return [True, glob.glob(os.path.join(i, filePos) + ".[s,S]*")[0]]
            return [False, False]
    #
    return [False, False]


def getExtensionInfo(info,name):
    if len(info)==9 and \
        isinstance(info[8],dict) and \
        name in info[8] :
        return info[8][name]
    return None


class modelTypes(QtGui.QDialog):
    def __init__(self, model, paths, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.setWindowTitle(u'Choose model')
        #
        self.modelsList = QtGui.QListWidget()
        for i in paths:
            self.modelsList.addItem(i)
        
        self.modelsList.setCurrentRow(0)
        #
        buttons = QtGui.QDialogButtonBox()
        buttons.setOrientation(QtCore.Qt.Vertical)
        buttons.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
        buttons.addButton("Choose", QtGui.QDialogButtonBox.AcceptRole)
        self.connect(buttons, QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        self.connect(buttons, QtCore.SIGNAL("rejected()"), self, QtCore.SLOT("reject()"))
        #
        lay = QtGui.QGridLayout(self)
        lay.addWidget(QtGui.QLabel(u"Choose one of available models for part"), 0, 0, 1, 1)
        lay.addWidget(QtGui.QLabel(u"<div style='font-weight:bold;'>{0}</div>".format(model)), 1, 0, 1, 1, QtCore.Qt.AlignHCenter)
        lay.addWidget(self.modelsList, 2, 0, 1, 1)
        lay.addWidget(buttons, 2, 1, 1, 1)
