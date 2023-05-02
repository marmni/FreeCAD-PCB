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

import FreeCAD
import re
#
from PCBconf import softLayers, spisTekstow
from PCBobjects import *
from formats.kicad_v3 import KiCadv3_PCB
from formats.dialogMAIN_FORM import dialogMAIN_FORM


class dialogMAIN(dialogMAIN_FORM):
    def __init__(self, filename=None, parent=None):
        dialogMAIN_FORM.__init__(self, parent)
        self.databaseType = "kicad_v4"
        #
        self.plytkaPCB_otworyH.setChecked(False)
        self.plytkaPCB_otworyH.setDisabled(True)
        #
        self.projektBRD = self.setProjectFile(filename)
        self.layersNames = self.getLayersNames()
        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetBool("boardImportThickness", True):
            self.gruboscPlytki.setValue(self.getBoardThickness())
        ##
        self.generateLayers([44, 45])
        self.spisWarstw.sortItems(1)
        #
        #self.kicadModels = QtGui.QCheckBox(u"Load kicad models (if there are any")

        #lay = QtGui.QHBoxLayout()
        #lay.addWidget(self.kicadModels)
        #self.lay.addLayout(lay, 12, 0, 1, 6)
    
    def getBoardThickness(self):
        return float(re.findall(r'\(thickness (.+?)\)', self.projektBRD)[0])
        
    def getLayersNames(self):
        dane = {}
        
        layers = re.search(r'\[start\]\(layers(.+?)\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL).group(0)
        for i in re.findall(r'\((.*?) (.*?) .*?\)', layers):
            side = "TOP"
            if i[1].startswith("B."):
                side = "BOTTOM"
            dane[int(i[0])] = {"name": i[1], "color": None, "side": side}
        
        ####################
        # EXTRA LAYERS
        ####################
        # measures
        dane[106] = {"name": softLayers[self.databaseType][106]["description"], "color": softLayers[self.databaseType][106]["color"]}
        #  annotations
        dane[905] = {"name": softLayers[self.databaseType][905]["description"], "color": softLayers[self.databaseType][905]["color"], "type": "anno", "number": 0}
        # pad
        dane[107] = {"name": softLayers[self.databaseType][107]["description"], "color": softLayers[self.databaseType][107]["color"]}
        dane[108] = {"name": softLayers[self.databaseType][108]["description"], "color": softLayers[self.databaseType][108]["color"]}
        ####################
        ####################
        return dane


class KiCadv4_PCB(KiCadv3_PCB):
    def __init__(self, filename, parent):
        KiCadv3_PCB.__init__(self, filename, parent)
        
        self.dialogMAIN = dialogMAIN(filename)
        self.databaseType = "kicad_v4"
        #
        self.borderLayerNumber = 44
    
    def defineFunction(self, layerNumber):
        if layerNumber in [107, 108]:  # pady
            return "pads"
        elif layerNumber in [0, 31]:  # paths
            return "paths"
        elif layerNumber == 106:  # MEASURES
            return "measures"
        elif layerNumber in [32, 33]:  # glue
            return "glue"
        elif layerNumber in [900, 901, 902, 903, 904]:  # ConstraintAreas
            return "constraint"
        elif layerNumber == 905:
            return "annotations"
        else:
            return "silk"
    
    def getPads(self, layerNew, layerNumber, layerSide, tentedViasLimit, tentedVias):
        # via
        via_drill = float(self.getSettings('via_drill'))

        for i in re.findall(r'\(via\s+\(at\s+(.*?)\s+(.*?)\)\s+\(size\s+(.*?)\)\s+(\(drill\s+(.*?)\)|)', self.projektBRD):
            x = float(i[0])
            y = float(i[1]) * (-1)
            diameter = float(i[2])

            if i[4] == '':
                drill = via_drill / 2.
            else:
                drill = float(i[4]) / 2.
            
            ##### ##### ##### 
            ##### tented dVias
            if self.filterTentedVias(tentedViasLimit, tentedVias, drill * 2, False):
                continue
            ##### ##### ##### 
            layerNew.addCircle(x, y, diameter / 2.)
            layerNew.setFace()
        
        if not tentedVias:
            # pad
            self.getElements()
            #
            for i in self.elements:
                for j in self.generatePadData(i['dataElement']):
                    if("np_" in j['padType'].lower()):  # mounting holes
                        continue
                    #
                    xs = j['x'] + i['x']
                    ys = j['y'] + i['y']
                    numerWarstwy = j['layers'].split(' ')
                    rot_2 = i['rot'] - j['rot']
                    
                    # kicad_pcb v3 TOP:         self.getLayerName(15) in numerWarstwy and layerNumber == 107
                    # kicad_pcb v3 BOTTOM:      self.getLayerName(0) in numerWarstwy and layerNumber == 18
                    # kicad_pcb v4 TOP:         self.getLayerName(0) in numerWarstwy and layerNumber == 107
                    # kicad_pcb v4 BOTTOM:      self.getLayerName(31) in numerWarstwy and layerNumber == 108
                    dodaj = False
                    if self.databaseType == "kicad" and ((self.getLayerName(15) in numerWarstwy and layerNumber[0] == 107) or (self.getLayerName(0) in numerWarstwy and layerNumber[0] == 108)):
                        dodaj = True
                    elif self.databaseType == "kicad_v4" and ((self.getLayerName(0) in numerWarstwy and layerNumber[0] == 107) or (self.getLayerName(31) in numerWarstwy and layerNumber[0] == 108)):
                        dodaj = True
                    elif any(x in ['*.Cu', '"*.Cu"', 'F&B.Cu', '"F&B.Cu"'] for x in numerWarstwy):
                        dodaj = True
                    #####
                    if dodaj:
                        if j['padShape'] == 'rect':
                            x1 = xs - j['dx'] / 2. + j['xOF']
                            y1 = ys - j['dy'] / 2. + j['yOF']
                            x2 = xs + j['dx'] / 2. + j['xOF']
                            y2 = ys + j['dy'] / 2. + j['yOF']
                            
                            layerNew.addRectangle(x1, y1, x2, y2)
                            layerNew.addRotation(xs, ys, rot_2)
                            layerNew.addRotation(i['x'], i['y'], i['rot'])
                            #layerNew.setChangeSide(i['x'], i['y'], i['side'])
                            layerNew.setFace()
                        elif j['padShape'] == "custom":
                            parentL = {
                                'x': xs, 
                                'y': ys, 
                                'rot': rot_2
                            }
                            layerNew = self.addStandardShapes(j["data"], layerNew, None, display=[False, False, False, True], parent=parentL)
                            layerNew.addRotation(i['x'], i['y'], i['rot'])
                        elif j['padShape'] == 'circle':
                            layerNew.addCircle(xs + j['xOF'], ys + j['yOF'], j['dx'] / 2.)
                            layerNew.addRotation(xs, ys, rot_2)
                            layerNew.addRotation(i['x'], i['y'], i['rot'])
                            #layerNew.setChangeSide(i['x'], i['y'], i['side'])
                            layerNew.setFace()
                        elif j['padShape'] == 'oval':
                            if j['dx'] == j['dy']:
                                layerNew.addCircle(xs + j['xOF'], ys + j['yOF'], j['dx'] / 2.)
                                layerNew.addRotation(xs, ys, rot_2)
                                layerNew.addRotation(i['x'], i['y'], i['rot'])
                                #layerNew.setChangeSide(i['x'], i['y'], i['side'])
                                layerNew.setFace()
                            else:
                                layerNew.addPadLong(xs + j['xOF'], ys + j['yOF'], j['dx'] / 2., j['dy'] / 2., 100)
                                layerNew.addRotation(xs, ys, rot_2)
                                layerNew.addRotation(i['x'], i['y'], i['rot'])
                                #layerNew.setChangeSide(i['x'], i['y'], i['side'])
                                layerNew.setFace()
                        elif j['padShape'] == 'trapezoid':
                            if j[8].strip() == '':
                                xRD = 0
                                yRD = 0
                            else:
                                rect_delta = re.findall(r'\(rect_delta ([-0-9\.]*?) ([-0-9\.]*?) \)', j[8].strip())[0]
                                yRD = float(rect_delta[0]) / 2.
                                xRD = float(rect_delta[1]) / 2.
                            
                            x1 = xs - j['dx'] / 2. + j['xOF']
                            y1 = ys - j['dy'] / 2. + j['yOF']
                            x2 = xs + j['dx'] / 2. + j['xOF']
                            y2 = ys + j['dy'] / 2. + j['yOF']
                            
                            layerNew.addTrapeze([x1, y1], [x2, y2], xRD, yRD)
                            layerNew.addRotation(xs, ys, rot_2)
                            layerNew.addRotation(i['x'], i['y'], i['rot'])
                            #layerNew.setChangeSide(i['x'], i['y'], i['side'])
                            layerNew.setFace()
    
    def getParts(self):
        self.getElements()
        parts = []
        ###########
        for i in self.elements:
            copyL = i.copy()
            #
            if copyL['side'] == 1:
                copyL['side'] = "TOP"
            else:
                copyL['side'] = "BOTTOM"
                copyL['rot'] = (180 - copyL['rot'])
            ####################################
            dataName = self.getAnnotations(re.findall(r'\(fp_text reference(.+?)\)\n\s+\)\n\s+\(', copyL['dataElement'], re.MULTILINE|re.DOTALL), mode='param')
            copyL['EL_Name'] = dataName[0]
            copyL['EL_Name']["text"] = "NAME"
            copyL['EL_Name']["x"] = copyL['EL_Name']["x"] + i["x"]
            copyL['EL_Name']["y"] = copyL['EL_Name']["y"] + i["y"]
            copyL['EL_Name']["rot"] = copyL['EL_Name']["rot"] - i["rot"]
            ####################################
            dataValue = self.getAnnotations(re.findall(r'\(fp_text value(.+?)\)\n\s+\)\n\s+\(', copyL['dataElement'], re.MULTILINE|re.DOTALL), mode='param')
            copyL['EL_Value'] = dataValue[0]
            copyL['EL_Value']["text"] = "VALUE"
            copyL['EL_Value']["x"] = copyL['EL_Value']["x"] + i["x"]
            copyL['EL_Value']["y"] = copyL['EL_Value']["y"] + i["y"]
            copyL['EL_Value']["rot"] = copyL['EL_Value']["rot"] - i["rot"]
            ####################################
            parts.append(copyL)    
        #
        return parts
    
    def getSilkLayerModels(self, layerNew, layerNumber):
        self.getElements()
        #
        for i in self.elements:
            self.addStandardShapes(i['dataElement'], layerNew, layerNumber[1], display=[True, True, True, True], parent=i)
    
    def getElements(self):
        if len(self.elements) == 0:
            for i in re.findall(r'\[start\]\((?:footprint|module)\s+(.+?)\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL):
                [x, y, rot] = re.search(r'\(at\s+([0-9\.-]*?)\s+([0-9\.-]*?)(\s+[0-9\.-]*?|)\)', i).groups()
                layer = re.search(r'\(layer\s+(.+?)\)', i).groups()[0]
                
                name = re.search(r'\(fp_text reference\s+(.*)', i, re.MULTILINE|re.DOTALL).groups()[0]
                name = re.search(r'^(".+?"|.+?)\s', name).groups()[0].replace('"', '')
                value = re.search(r'\(fp_text value\s+(.*)', i, re.MULTILINE|re.DOTALL).groups()[0]
                value  = re.search(r'^(".+?"|.+?)\s', value).groups()[0].replace('"', '')
                
                x = float(x)
                y = float(y) * (-1)
                ########
                package = re.search(r'^(.+?)\(layer', i).groups()[0]
                package = re.sub('locked|placed|pla', '', package).split(':')[-1]
                package = package.replace('"', '').strip()
                
                pathAttribute = ""
                # use different 3D model for current package
                userText = re.findall(r'\(fp_text user\s+(.*)\s+\(at\s+', i)
                
                if any(k for k in ['FREECAD', 'FCM', 'FCMV'] if k in "__".join(userText)):
                    for j in userText:
                        if any(k for k in ['FREECAD', 'FCM', 'FCMV'] if k in j):
                            [userTextName, userTextValue] = j.replace('"', '').strip().split("=")
                            #
                            if userTextValue.strip() == "":
                                FreeCAD.Console.PrintWarning(spisTekstow["loadModelEmptyAttributeInfo"].format(name))
                            elif (userTextName == 'FREECAD' and userTextValue.strip().startswith("--")) or userTextName == 'FCMV':
                                pathAttribute = userTextValue.strip()
                                
                                if not pathAttribute.startswith("--"):
                                    pathAttribute = "--" + pathAttribute
                            elif userTextName in ['FREECAD', 'FCM']:
                                FreeCAD.Console.PrintWarning(spisTekstow["loadModelImportDifferentPackageInfo"].format(name, userTextValue.strip(), package))
                                package = userTextValue.strip()
                ##3D package from KiCad
                #try:
                    #package3D = re.search(r'\(model\s+(.+?).wrl', i).groups()[0]
                    #if package3D and self.partExist(os.path.basename(package3D), "", False):
                        #package = os.path.basename(package3D)
                #except:
                    #pass
                ########
                library = package
                #
                if rot == '':
                    rot = 0.0
                else:
                    rot = float(rot)
                
                if (self.databaseType == "kicad" and self.spisWarstw[layer] == 15) or (self.databaseType == "kicad_v4" and self.spisWarstw[layer] == 0):  # top
                    side = 1  # TOP
                    mirror = 'None'
                else:
                    side = 0  # BOTTOM
                    mirror = 'Local Y axis'
                
                self.elements.append({
                    'name': name, 
                    'library': library, 
                    'package': package, 
                    'value': value, 
                    'pathAttribute': pathAttribute,
                    'x': x, 
                    'y': y, 
                    'rot': rot,
                    'side': side, 
                    'dataElement': i, 
                    'mirror': mirror
                })
