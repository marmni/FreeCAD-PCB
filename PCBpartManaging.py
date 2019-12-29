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
from command.PCBgroups import createGroup_Parts, createGroup_Others, createGroup, createGroup_Missing
from command.PCBannotations import createAnnotation


class partsManaging(mathFunctions):
    def __init__(self, databaseType=None):
        self.objColors = {}
        
        # allSocked - definicja zachowania przy dodawaniu podstawki dla wszystkich obeiktow
        #   -1 - brak podstawek
        #    0 - zapytaj o dodanie podstawki (def)
        #    1 - dodaj podstawki dla wszystkich obiektow
        self.allSocket = 0
        self.databaseType = databaseType
        self.colFileVersion = 3
    
    def adjustRotation(self, angle):
        if angle > 360 or angle < 360:  # max = 360deg; min= -360deg
            angle = angle % 360
        
        return angle
        
    def updateView(self):
        FreeCADGui.ActiveDocument.ActiveView.viewAxometric()
        FreeCADGui.ActiveDocument.ActiveView.fitAll()
        
    def getPartShape(self, filePath, step_model, colorizeElements):
        standardColor = [(0.800000011920929, 0.800000011920929, 0.800000011920929, 0.0)]  # standard gray color
        ################################################################
        ################################################################
        # check if model was already imported
        ################################################################
        ################################################################
        if filePath in self.objColors.keys():
            step_model.Shape = self.objColors[filePath]['shape']
            
            if colorizeElements:
                step_model.ViewObject.DiffuseColor = self.objColors[filePath]['col']
            else:
                step_model.ViewObject.DiffuseColor = standardColor
            
            return step_model
        else:
            self.objColors[filePath] = {}
        ################################################################
        ################################################################
        # reading data from colFile - if exist
        ################################################################
        ################################################################
        colFile = os.path.join(os.path.dirname(filePath), os.path.splitext(os.path.basename(filePath))[0] + '.col')
        #FreeCAD.Console.PrintWarning("3. {0}\n".format(colFile))
        
        try:
            if os.path.exists(colFile):
                colFileData = builtins.open(colFile, "r").readlines()
                header = colFileData[0].strip().split("|")
                
                if len(header) >= 2 and int(header[0]) == self.colFileVersion and str(os.path.getmtime(filePath)) == header[1]:
                    newShape = Part.Shape()
                    newShape.importBrepFromString("".join(colFileData[2:]))
                    step_model.Shape = newShape
                    
                    if colorizeElements:
                        step_model.ViewObject.DiffuseColor = eval(colFileData[1].strip())
                    else:
                        step_model.ViewObject.DiffuseColor = standardColor
                    
                    self.objColors[filePath]['shape'] = newShape
                    self.objColors[filePath]['col'] = eval(colFileData[1].strip())
                    
                    if len(colFileData[2:]) > 20:
                        return step_model
                else:
                    FreeCAD.Console.PrintWarning("Too old *.col file. It is necessary to generate a new one.\n")
            else:  # generate new *.col file
                FreeCAD.Console.PrintWarning("No *.col file. It is necessary to generate a new one.\n")
        except Exception as e:
            FreeCAD.Console.PrintWarning("1. {0}\n".format(e))
        ################################################################
        ################################################################
        # generating new col file
        ################################################################
        ################################################################
        active = FreeCAD.ActiveDocument.Name
        #
        colFileData = builtins.open(colFile, "w")
        colFileData.write("{1}|{0}\n".format(os.path.getmtime(filePath), self.colFileVersion))  # version|date
        
        FreeCAD.newDocument('importingPartsPCB')
        FreeCAD.ActiveDocument = FreeCAD.getDocument('importingPartsPCB')
        FreeCADGui.ActiveDocument = FreeCADGui.getDocument('importingPartsPCB')
        ImportGui.insert(u"{0}".format(filePath), "importingPartsPCB")
        
        fuse = []
        col = standardColor
        for i in FreeCAD.ActiveDocument.Objects:
            if i.ViewObject.Visibility and hasattr(i, 'Shape'):
                fuse.append(i)
        
        try:
            if len(fuse) == 1:
                shape = fuse[0].Shape
                col = fuse[0].ViewObject.DiffuseColor
            else:
                # FC 0.16
                #newPart = FreeCAD.ActiveDocument.addObject("Part::MultiFuse","Union").Shapes=fuse
                #FreeCAD.ActiveDocument.recompute()
                #shape = FreeCAD.ActiveDocument.getObject("Union").Shape
                #col = FreeCAD.ActiveDocument.getObject("Union").ViewObject.DiffuseColor
                # FC 0.18
                newPart = FreeCAD.ActiveDocument.addObject("Part::Compound","Compound")
                newPart.Links = fuse
                newPart.recompute()
                shape = newPart.Shape
                col = newPart.ViewObject.DiffuseColor
            
            step_model.Shape = shape
            if colorizeElements:
                step_model.ViewObject.DiffuseColor = col
            else:
                step_model.ViewObject.DiffuseColor = standardColor
            
            colFileData.write(str(col))
            colFileData.write(shape.exportBrepToString())
            
            self.objColors[filePath]['shape'] = shape
            self.objColors[filePath]['col'] = col
        except Exception as e:
            FreeCAD.Console.PrintWarning("2. {0}\n".format(e))
        
        colFileData.close()
        
        FreeCAD.closeDocument("importingPartsPCB")
        FreeCAD.setActiveDocument(active)
        FreeCAD.ActiveDocument=FreeCAD.getDocument(active)
        FreeCADGui.ActiveDocument=FreeCADGui.getDocument(active)
        
        return step_model
    
    def partPlacement(self, step_model, cX, cY, cZ, cRX, cRY, cRZ, X, Y):

        step_model.Placement = FreeCAD.Placement(FreeCAD.Vector(0, 0, 0), FreeCAD.Rotation(0, 0, 0))  # important for PCBmoveParts and PCBupdateParts
            
        step_model.Placement.Base.x = cX
        step_model.Placement.Base.y = cY
        
        step_model.Placement = FreeCAD.Placement(step_model.Placement.Base, FreeCAD.Rotation(cRZ, cRY, cRX)) # rotation correction
        
        xB0 = step_model.Shape.BoundBox.XLength / 2. - step_model.Shape.BoundBox.XMax
        yB0 = step_model.Shape.BoundBox.YLength / 2. - step_model.Shape.BoundBox.YMax
        
        step_model.Placement.Base.x = xB0 + X # final position X-axis
        step_model.Placement.Base.y = yB0 + Y # final position Y-axis
        step_model.Proxy.offsetZ = cZ
    
    def partStandardDictionary(self):
        return {
            'name': '', 
            'library': '', 
            'package': '', 
            'value': '', 
            'x': 0, 
            'y': 0, 
            'locked': False, 
            'populated': False,  
            'smashed': False, 
            'rot': 0, 
            'side': 'TOP', 
            'dataElement': None,
            'EL_Name': {
                'text': 'NAME', 
                'x': 0,
                'y': 0, 
                'z': 0, 
                'size': 1.27, 
                'rot': 0, 
                'side': 'TOP', 
                'align': 'center', 
                'spin': True, 
                'font': 'Proportional', 
                'display': True, 
                'distance': 50, 
                'tracking': 0, 
                'mode': 'param'
            }, 
            'EL_Value': {
                'text': 'VALUE', 
                'x': 0, 
                'y': 0,
                'z': 0, 
                'size': 1.27, 
                'rot': 0, 
                'side': 'TOP', 
                'align': 'bottom-left', 
                'spin': True, 
                'font': 'Proportional', 
                'display': True, 
                'distance': 50, 
                'tracking': 0, 
                'mode': 'param'
            }
        }
        
    def addPart(self, newPart, koloroweElemnty=True, adjustParts=False, groupParts=True, partMinX=0, partMinY=0, partMinZ=0):
        #newPart = {
            # 'name': 'E$2', 
            # 'library': 'eagle-ltspice', 
            # 'package': 'R0806', 
            # 'value': '', 
            # 'x': 19.0, 
            # 'y': 5.5, 
            # 'locked': False, 
            # 'populated': False,  
            # 'smashed': False, 
            # 'rot': 90, 
            # 'side': 'TOP', 
            # 'dataElement': <DOM Element: element at 0x1bc2634cf20>, 
            # 'EL_Name': {
                # 'text': 'NAME', 
                # 'x': 16.73,
                # 'y': 6.23, 
                # 'z': 0, 
                # 'size': 1.27, 
                # 'rot': 135, 
                # 'side': 'TOP', 
                # 'align': 'center', 
                # 'spin': True, 
                # 'font': 'Proportional', 
                # 'display': True, 
                # 'distance': 50, 
                # 'tracking': 0, 
                # 'mode': 'param'
            # }, 
            # 'EL_Value': {
                # 'text': 'VALUE', 
                # 'x': 21.54, 
                # 'y': 4.23,
                # 'z': 0, 
                # 'size': 1.27, 
                # 'rot': 90, 
                # 'side': 'TOP', 
                # 'align': 'bottom-left', 
                # 'spin': True, 
                # 'font': 'Proportional', 
                # 'display': True, 
                # 'distance': 50, 
                # 'tracking': 0, 
                # 'mode': 'param'}
        # }
        ###############################################################
        doc = FreeCAD.activeDocument()
        pcb = getPCBheight()
        result = ['OK']
        
        partNameTXT = self.generateNewLabel(newPart['name'])
        ###############################################################
        # checking if 3D model exist
        ###############################################################
        fileData = self.partExist(newPart['package'], u"{0} {1} ({2})".format(partNameTXT, newPart['value'], newPart['package']))
        if fileData[0]:
            if fileData[2] > 0:
                modelData = self.__SQL__.getModelByID(fileData[2])
                
                if modelData[0]:
                    modelData = self.__SQL__.convertToTable(modelData[1])
                else:
                    modelData = {'sockedID': 0, 'socketIDSocket': False}
            else:
                modelData = {'add_socket':'[False,None]'}
            #
            newPart['rot'] = self.adjustRotation(newPart['rot'])
            filePath = fileData[1]
            correctingValue_X = fileData[3]['x']  # pos_X
            correctingValue_Y = fileData[3]['y']  # pos_Y
            correctingValue_Z = fileData[3]['z']  # pos_Z
            correctingValue_RX = fileData[3]['rx']  # pos_RX
            correctingValue_RY = fileData[3]['ry']  # pos_RY
            correctingValue_RZ = fileData[3]['rz']  # pos_RZ
            ############################################################
            # ADDING OBJECT
            ############################################################
            step_model = doc.addObject("Part::FeaturePython", "{0} ({1})".format(partNameTXT, fileData[3]['name']))
            step_model.Label = partNameTXT
            step_model = self.getPartShape(filePath, step_model, koloroweElemnty)
            #
            obj = partObject(step_model)
            step_model.Package = u"{0}".format(fileData[3]['name'])
            ############################################################
            # PUTTING OBJECT IN CORRECT POSITION/ORIENTATION
            ############################################################
            self.partPlacement(step_model, correctingValue_X, correctingValue_Y, correctingValue_Z, correctingValue_RX, correctingValue_RY, correctingValue_RZ, newPart["x"], newPart["y"])
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
            # ADDING SOCKET
            #   addSocket = 
            #               False - no socket
            #               True  - add socket
            #
            #################################################################
            addSocket = False
            
            if modelData['socketIDSocket'] and self.allSocket == 0 and modelData['socketID'] != fileData[2]:
                socketData = self.__SQL__.convertToTable(self.__SQL__.getModelByID(modelData['socketID'])[1])
                
                if socketData["isSocket"]:
                    dial = QtGui.QMessageBox()
                    dial.setText(u"Add socket to part {0} (Package: {1}, Library: {2})?".format(partNameTXT, newPart['package'], newPart["library"]))
                    dial.setWindowTitle("Socket")
                    dial.setIcon(QtGui.QMessageBox.Question)
                    dial.addButton('No', QtGui.QMessageBox.RejectRole)
                    podstawkaTAK = dial.addButton('Yes', QtGui.QMessageBox.YesRole)
                    zawszePodstawki = dial.addButton('Yes for all', QtGui.QMessageBox.YesRole)
                    nigdyPodstawki = dial.addButton('No for all', QtGui.QMessageBox.RejectRole)
                    dial.exec_()
                    
                    if dial.clickedButton() == nigdyPodstawki:
                        self.allSocket = -1
                    elif dial.clickedButton() == zawszePodstawki:
                        self.allSocket = 1
                    elif dial.clickedButton() == podstawkaTAK:
                        addSocket = True
                    else:
                        addSocket = False
            #
            if (addSocket or self.allSocket == 1) and modelData['socketIDSocket']:
                socketData = self.__SQL__.convertToTable(self.__SQL__.getModelByID(modelData['socketID'])[1])
                
                step_model.Socket.Value = socketData["isSocketHeight"]  # socket height
                #
                socketModel = self.partStandardDictionary()
                socketModel['name'] = "{0}_socket".format(partNameTXT)
                socketModel['library'] = ""
                socketModel['package'] = socketData["name"]
                socketModel['value'] = ""
                socketModel['x'] = newPart["x"]
                socketModel['y'] = newPart["y"]
                socketModel['rot'] = newPart['rot']
                socketModel['side'] = newPart["side"]
                
                socketModel['EL_Name']["x"] = newPart["x"]
                socketModel['EL_Name']["y"] = newPart["y"]
                socketModel['EL_Name']["rot"] = newPart['rot']
                socketModel['EL_Name']["side"] = newPart["side"]
                
                socketModel['EL_Value']["x"] = newPart["x"]
                socketModel['EL_Value']["y"] = newPart["y"]
                socketModel['EL_Value']["rot"] = newPart['rot']
                socketModel['EL_Value']["side"] = newPart["side"]
                #
                self.addPart(socketModel, koloroweElemnty, adjustParts, groupParts, partMinX, partMinY, partMinZ)
            ############################################################
            # 
            ############################################################
            viewProviderPartObject(step_model.ViewObject)
            #
            step_model.X = newPart["x"]
            step_model.Y = newPart["y"]
            if not self.databaseType in ["freepcb", "kicad_v4", "kicad"]:
                step_model.Rot = newPart['rot'] # after setting X/Y
            if newPart["side"] == "BOTTOM":
                step_model.Side = newPart["side"]
            step_model.Proxy.updatePosition_Z(step_model, pcb[1], True)
        else: # there is no suitable model in library
            #################################################################
            # FILTERING OBJECTS BY SIZE L/W/H
            #################################################################
            if partMinX != 0 or partMinY or partMinZ:
                return
            ############################################################
            # ADDING OBJECT
            ############################################################
            step_model = doc.addObject("Part::FeaturePython", "{0} ({1})".format(partNameTXT, newPart["package"]))
            step_model.Label = partNameTXT
            
            obj = partObject_E(step_model)
            step_model.Package = "{0}".format(newPart["package"])
            
            viewProviderPartObject_E(step_model.ViewObject)
            #
            step_model.X = newPart["x"]
            step_model.Y = newPart["y"]
            step_model.Rot = newPart['rot'] # after setting X/Y
            if newPart["side"] == "BOTTOM":
                step_model.Side = newPart["side"]
            step_model.Proxy.updatePosition_Z(step_model, pcb[1], True)
            #
            result = ['Error']
        ##################################################################
        ## part name object
        ##################################################################
        # 'EL_Name': {
                # 'text': 'NAME', 
                # 'x': 16.73,
                # 'y': 6.23, 
                # 'z': 0, 
                # 'size': 1.27, 
                # 'rot': 135, 
                # 'side': 'TOP', 
                # 'align': 'center', 
                # 'spin': True, 
                # 'font': 'Proportional', 
                # 'display': True, 
                # 'distance': 50, 
                # 'tracking': 0, 
                # 'mode': 'param'
            # }, 
        try:
            annotation = createAnnotation()
            annotation.X = newPart['EL_Name']["x"]
            annotation.Y = newPart['EL_Name']["y"]
            annotation.Z = newPart['EL_Name']["z"]
            annotation.Side = newPart['EL_Name']["side"]
            annotation.Rot = newPart['EL_Name']["rot"]
            annotation.Text = newPart['name']
            annotation.Align = newPart['EL_Name']["align"]
            annotation.Size = newPart['EL_Name']["size"]
            annotation.Spin = newPart['EL_Name']["spin"]
            annotation.tracking = newPart['EL_Name']["tracking"]
            annotation.lineDistance = newPart['EL_Name']["distance"]
            annotation.Color = (1., 1., 1.)
            annotation.Font = newPart['EL_Name']["font"]
            annotation.Visibility = newPart['EL_Name']["display"]
            annotation.mode = newPart['EL_Name']["mode"]
            #
            if adjustParts:
                paramData = self.__SQL__.getParamsByModelID(modelData['id'], 'Name')
                if not isinstance(paramData, list) and paramData[0].active: # param exists and is active
                    try:
                        [x, y] = self.obrocPunkt2([paramData[0].x + step_model.X.Value, paramData[0].y + step_model.Y.Value] , [step_model.X.Value,  step_model.Y.Value], newPart['rot'])
                        annotation.X = x
                        annotation.Y = y
                        annotation.Z = paramData[0].z + step_model.Socket.Value
                        annotation.Color = eval(paramData[0].color)
                        annotation.Visibility = paramData[0].display
                        annotation.Size = paramData[0].size
                        annotation.Align = paramData[0].align
                        annotation.Rot = paramData[0].rz + newPart['rot']
                        annotation.Spin = paramData[0].spin
                    except Exception as e:
                        print(e)
            #
            annotation.generate(False)
            step_model.PartName = annotation.Annotation
        except:
            pass
        ##################################################################
        ## part value object
        ##################################################################
        # 'EL_Value': {
                # 'text': 'VALUE', 
                # 'x': 21.54, 
                # 'y': 4.23,
                # 'z': 0, 
                # 'size': 1.27, 
                # 'rot': 90, 
                # 'side': 'TOP', 
                # 'align': 'bottom-left', 
                # 'spin': True, 
                # 'font': 'Proportional', 
                # 'display': True, 
                # 'distance': 50, 
                # 'tracking': 0, 
                # 'mode': 'param'}
        # }
        try:
            annotation = createAnnotation()
            annotation.X = newPart['EL_Value']["x"]
            annotation.Y = newPart['EL_Value']["y"]
            annotation.Z = newPart['EL_Value']["z"]
            annotation.Side = newPart['EL_Value']["side"]
            annotation.Rot = newPart['EL_Value']["rot"]
            annotation.Text = newPart['value']
            annotation.Align = newPart['EL_Value']["align"]
            annotation.Size = newPart['EL_Value']["size"]
            annotation.Spin = newPart['EL_Value']["spin"]
            annotation.tracking = newPart['EL_Value']["tracking"]
            annotation.lineDistance = newPart['EL_Value']["distance"]
            annotation.Color = (1., 1., 1.)
            annotation.Font = newPart['EL_Value']["font"]
            annotation.Visibility = newPart['EL_Value']["display"]
            annotation.mode = newPart['EL_Value']["mode"]
            #
            if adjustParts:
                paramData = self.__SQL__.getParamsByModelID(modelData['id'], 'Value')
                if not isinstance(paramData, list) and paramData[0].active: # param exists and is active
                    try:
                        [x, y] = self.obrocPunkt2([paramData[0].x + step_model.X.Value, paramData[0].y + step_model.Y.Value] , [step_model.X.Value,  step_model.Y.Value], newPart['rot'])
                        annotation.X = x
                        annotation.Y = y
                        annotation.Z = paramData[0].z + step_model.Socket.Value
                        annotation.Color = eval(paramData[0].color)
                        annotation.Visibility = paramData[0].display
                        annotation.Size = paramData[0].size
                        annotation.Align = paramData[0].align
                        annotation.Rot = paramData[0].rz + newPart['rot']
                        annotation.Spin = paramData[0].spin
                    except Exception as e:
                        print(e)
            #
            annotation.generate(False)
            step_model.PartValue = annotation.Annotation
        except:
            pass
        ##################################################################
        #step_model.Rot = newPart['rot'] # after setting X/Y
        if self.databaseType in ["freepcb", "kicad_v4", "kicad"]:
            step_model.Rot = newPart['rot'] # after setting X/Y
        ##################################################################
        result.append(step_model)
        self.addPartToGroup(groupParts, step_model)
        pcb[2].Proxy.addObject(pcb[2], step_model)
        self.updateView()
        return result
    
    def partGenerateAnnotation(self, data, ):
        pass
    
    def addPartToGroup(self, groupParts, step_model):
        if hasattr(step_model, "Proxy") and hasattr(step_model.Proxy, "Type") and not step_model.Proxy.Type in ["PCBpart", "PCBpart_E"]:
            return
        #
        partsFolder = createGroup_Parts()
        #
        try:
            if groupParts and getPCBheight()[0]:
                if step_model.Proxy.Type == "PCBpart_E":
                    grp_2 = createGroup_Missing()
                else:
                    fileData = self.__SQL__.findPackage(step_model.Package, "*")
                    
                    if fileData:
                        model = self.__SQL__.getModelByID(fileData.modelID)
                        categoryData = self.__SQL__.getCategoryByID(int(model[1].categoryID))
                        
                        if categoryData == 0:
                            grp_2 = createGroup_Others()
                        else:
                            grp_2 = createGroup(categoryData.name)
                    else:
                        grp_2 = createGroup_Missing()
                
                grp_2.addObject(step_model)
                partsFolder.addObject(grp_2)
            else:
                partsFolder.addObject(step_model)
        except Exception as e:
            FreeCAD.Console.PrintWarning("{0} \n".format(e))

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

    def partExist(self, package, model, showDial=True):
        if not self.databaseType:
            return [False]
        
        try:
            databaseType = self.databaseType
            if databaseType in ['kicad', 'kicad_v4']:
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
            package = self.__SQL__.findPackage(package, supSoftware[databaseType]['name'])
            
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
