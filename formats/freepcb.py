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
try:
    import builtins
except:
    import __builtin__ as builtins
import re

from PCBconf import softLayers
from PCBobjects import *
from formats.dialogMAIN_FORM import dialogMAIN_FORM
from formats.baseModel import baseModel


class dialogMAIN(dialogMAIN_FORM):
    def __init__(self, filename=None, parent=None):
        dialogMAIN_FORM.__init__(self, parent)
        self.databaseType = "freepcb"
        #
        self.projektBRD = builtins.open(filename, "r").read().replace("\r\n", "\n").replace("\r", "\n")
        self.layersNames = self.getLayersNames()
        #
        self.generateLayers([i for i in range(31) if i not in [12, 13, 7, 8]])
        self.spisWarstw.sortItems(1)
    
    def getLayersNames(self):
        dane = {}
        # 
        for i in re.findall(r'layer_info:\s+"(.*?)" (.*?) (.*?) (.*?) (.*?) .*?\n', self.projektBRD , re.DOTALL):
            number = int(i[1])
            if int(i[1]) in softLayers[self.databaseType].keys():
                dane[int(i[1])] = {"name": i[0]}
        
        # extra layers
        dane[97] = {"name": softLayers[self.databaseType][97]["description"]}
        dane[98] = {"name": softLayers[self.databaseType][98]["description"]}
        dane[99] = {"name": softLayers[self.databaseType][99]["description"]}
        #
        return dane


class FreePCB(baseModel):
    '''Board importer for  FreePCB software'''
    def __init__(self, filename, parent):
        #self.groups = {}  # layers groups
        #
        self.fileName = filename
        self.dialogMAIN = dialogMAIN(self.fileName)
        self.databaseType = "freepcb"
        self.parent = parent
        #
        self.elements = []
        self.libraries = {}
        self.sections = {}
        self.mnoznik = 1. / 1000000.
    
    def defineFunction(self, layerNumber):
        if layerNumber in [98, 99]:  # pady
            return "pads"
        elif layerNumber in [12, 13]:  # paths
            return "paths"
        elif layerNumber == 97:
            return "annotations"
        else:
            return "silk"

    def getSection(self, sectionName):
        if sectionName in self.sections.keys():
            return self.sections[sectionName]
        else:
            return []
        
    def setProject(self):
        self.projektBRD = builtins.open(self.fileName, "r").read().replace("\r\n", "\n").replace("\r", "\n")
        #
        self.sections["options"] = re.findall(r'\[options\](.*)\[footprints\]', self.projektBRD, re.DOTALL)[0]
        self.sections["footprints"] = re.findall(r'\[footprints\](.*)\[board\]', self.projektBRD, re.DOTALL)[0]
        self.sections["board"] = re.findall(r'\[board\](.*)\[solder_mask_cutouts\]', self.projektBRD, re.DOTALL)[0]
        self.sections["solder_mask_cutouts"] = re.findall(r'\[solder_mask_cutouts\](.*)\[parts\]', self.projektBRD, re.DOTALL)[0]
        self.sections["parts"] = re.findall(r'\[parts\](.*)\[nets\]', self.projektBRD, re.DOTALL)[0]
        self.sections["nets"] = re.findall(r'\[nets\](.*)\[texts\]',  self.projektBRD, re.DOTALL)[0]
        self.sections["texts"] = re.findall(r'\[texts\](.*)\[.*?\]',  self.projektBRD, re.DOTALL)[0]
        
        # for i in re.findall(r'\[(.*?)\]\n(.*?)\[', self.projektBRD , re.DOTALL):
            # self.sections[i[0]] = i[1]
 
    def getParts(self):
        self.getElements()
        parts = []
        #
        for k in self.elements:
            align = "bottom-left"
            
            if k['side'] == "BOTTOM":
                align = "bottom-right"
            ##############################
            nameData = re.search(r'ref_text:\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\n', k['dataElement']).groups()
            
            if float(nameData[2]) == 0:
                rotN = 0
            else:
                rotN = 360 - float(nameData[2])
            
            k['EL_Name'] = {
                "text": "NAME",
                "x": k['x'] + float(nameData[3]) * self.mnoznik,
                "y": k['y'] + float(nameData[4]) * self.mnoznik,
                "z": 0,
                "size": float(nameData[0]) * self.mnoznik,
                "rot": rotN,
                "side": k['side'],
                "align": align,
                "spin": True,
                "font": "Fixed",
                "display": bool(int(nameData[5])),
                "distance": 1,
                "tracking": 0,
                "mode": 'param'
            }
            ##############################
            try:
                valueData = re.search(r'value:\s+".*?"\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\n', k['dataElement']).groups()
            except:
                valueData = [0, 0, 0, 0, 0, 1]
            
            if float(valueData[2]) == 0:
                rotN = 0
            else:
                rotN = 360 - float(valueData[2])
            
            k['EL_Value'] = {
                "text": "VALUE",
                "x": k['x'] + float(valueData[3]) * self.mnoznik,
                "y": k['y'] + float(valueData[4]) * self.mnoznik,
                "z": 0,
                "size": float(valueData[0]) * self.mnoznik,
                "rot": rotN,
                "side": k['side'],
                "align": align,
                "spin": True,
                "font": "Fixed",
                "display": bool(int(valueData[5])),
                "distance": 1,
                "tracking": 0,
                "mode": 'param'
            }
            ##############################
            parts.append(k)
        #
        return parts

    def getPaths(self, layerNew, layerNumber, display=[True, True, True, False]):
        section = self.getSection("nets").split("net:")
        for k in section:
            if not k.strip() == "":
                signal = re.search(r'"(.*?)"',  k.strip(), re.DOTALL).groups()[0]
                #
                data = k.split('connect:')[1:]
        
                for i in data:
                    vtx = re.findall(r'vtx:\s+.*?\s+(.*?)\s+(.*?)\s+.*?\n\s+seg:\s+.*?\s+(.*?)\s+(.*?)\s+', i)
                    lastVTX = re.findall(r'vtx:\s+.*?\s+(.*?)\s+(.*?)\s+.*?\s+.*?\s+.*?\s+.*?', i)[-1]
                    
                    for j in range(len(vtx)):
                        x1 = float(vtx[j][0]) * self.mnoznik
                        y1 = float(vtx[j][1]) * self.mnoznik
                        width = float(vtx[j][3]) * self.mnoznik
                        
                        if int(vtx[j][2]) != int(layerNumber[0]):
                            continue
                        
                        if j == len(vtx) - 1:
                            x2 = float(lastVTX[0]) * self.mnoznik
                            y2 = float(lastVTX[1]) * self.mnoznik
                        else:
                            x2 = float(vtx[j + 1][0]) * self.mnoznik
                            y2 = float(vtx[j + 1][1]) * self.mnoznik
                        #
                        if [x1, y1] != [x2, y2]:
                            layerNew.addLineWidth(x1, y1, x2, y2, width)
                            layerNew.setFace(signalName=signal)

    def getPads(self, layerNew, layerNumber, layerSide, tentedViasLimit, tentedVias):
        # via
        for i in re.findall(r'vtx: .+? (.+?) (.+?) .+? .+? ([1-9][0-9]*) ([1-9][0-9]*)', self.projektBRD):
            x = float(i[0]) * self.mnoznik
            y = float(i[1]) * self.mnoznik
            r = float(i[2]) * self.mnoznik / 2.
            drill = r * 2
            
            ##### ##### ##### 
            ##### tented dVias
            if self.filterTentedVias(tentedViasLimit, tentedVias, drill, False):
                continue
            ##### ##### ##### 
            layerNew.addCircle(x, y, r)
            layerNew.setFace()
        #
        if not tentedVias:
            self.getLibraries()
            self.getElements()
            
            try:
                for i in self.elements:
                    X1 = i['x']
                    Y1 = i['y']
                    ROT = i['rot']
                    
                    if i['side'] == "TOP":
                        SIDE = 1
                    else:
                        SIDE = 0
                    #
                    if layerNumber[0] == 98:  # top
                        if SIDE != 1:
                            padSide = "bottom"
                        else:
                            padSide = "top"
                    elif layerNumber[0] == 99:  # bottom
                        if SIDE != 0:
                            padSide = "bottom"
                        else:
                            padSide = "top"
                    else:
                        continue
                    #
                    if i['package'] in self.libraries.keys():
                        for j in self.libraries[i['package']]["pins"].keys():
                            if padSide in self.libraries[i['package']]["pins"][j].keys():
                                pinData = self.libraries[i['package']]["pins"][j]
                                padData = self.libraries[i['package']]["pins"][j][padSide]
                                #
                                x = pinData["x"] + X1
                                y = pinData["y"] + Y1
                                rot = pinData["rot"]
                                r = padData["width"] / 2.
                                #
                                if padData["shape"] == 1: # circle
                                    layerNew.addCircle(x, y, r)
                                    layerNew.addRotation(X1, Y1, ROT)
                                    layerNew.setChangeSide(X1, Y1, SIDE)
                                    layerNew.setFace()
                                elif padData["shape"] == 2: # square
                                    x1 = x - r
                                    y1 = y - r
                                    x2 = x + r
                                    y2 = y + r
                                
                                    layerNew.addRectangle(x1, y1, x2, y2)
                                    layerNew.addRotation(x, y, rot)
                                    layerNew.addRotation(X1, Y1, ROT)
                                    layerNew.setChangeSide(X1, Y1, SIDE)
                                    layerNew.setFace()
                                elif padData["shape"] == 3:  # rectangle
                                    dx = r
                                    dy = padData["len1"]
                                    
                                    x1 = x - dy
                                    y1 = y - dx
                                    x2 = x + dy
                                    y2 = y + dx
                                    
                                    layerNew.addRectangle(x1, y1, x2, y2)
                                    layerNew.addRotation(x, y, rot)
                                    layerNew.addRotation(X1, Y1, ROT)
                                    layerNew.setChangeSide(X1, Y1, SIDE)
                                    layerNew.setFace()
                                elif padData["shape"] == 4:  # round-rect
                                    dx = r
                                    dy = padData["len1"]
                                    
                                    layerNew.addPadLong(x, y, dy, dx, padData["radius"], 1)
                                    layerNew.addRotation(x, y, rot)
                                    layerNew.addRotation(X1, Y1, ROT)
                                    layerNew.setChangeSide(X1, Y1, SIDE)
                                    layerNew.setFace()
                                elif padData["shape"] == 5:  # oval
                                    dx = r
                                    dy = padData["len1"]
                                    
                                    layerNew.addPadLong(x, y, dy, dx, 100)
                                    layerNew.addRotation(x, y, rot)
                                    layerNew.addRotation(X1, Y1, ROT)
                                    layerNew.setChangeSide(X1, Y1, SIDE)
                                    layerNew.setFace()
                                elif padData["shape"] == 6:  # octagon
                                    layerNew.addOctagon(x, y, r * 2)
                                    layerNew.addRotation(x, y, rot)
                                    layerNew.addRotation(X1, Y1, ROT)
                                    layerNew.setChangeSide(X1, Y1, SIDE)
                                    layerNew.setFace()
            except Exception as e:
                FreeCAD.Console.PrintWarning("getPads() error: {0}\n".format(e))

    def getNormalAnnotations(self):
        adnotacje = []
        #
        try:
            for i in re.findall(r'text:\s*"(.*?)"\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\n', self.getSection("texts"), re.DOTALL):
                side = "TOP"
                rot = 360 - float(i[4])
                align = "bottom-left"
                
                if int(i[3]) in [8, 13]:
                    side = "BOTTOM"
                    align = "bottom-right"
                #
                mirror = False
                if int(i[5]): # mirror - not supported
                    mirror = True
                    # align = "bottom-right"
                #
                adnotacje.append({
                    "text": str(i[0]),
                    "x": float(i[1]) * self.mnoznik,
                    "y": float(i[2]) * self.mnoznik,
                    "z": 0,
                    "size": float(i[6]) * self.mnoznik,
                    "rot": rot,
                    "side": side,
                    "align": align,
                    "spin": True,
                    "font": "Fixed",
                    "display": True,
                    "distance": 1,
                    "tracking": 0,
                    "mode": 'anno',
                    "mirror": mirror
                })
        except Exception as e:
            FreeCAD.Console.PrintWarning(u"{0}\n".format(e))
        #
        return adnotacje
    
    def getLibraries(self):
        if len(self.libraries) == 0:
            for i in re.findall(r'(?=name:([\s\S]*?)(?=name:|$))', self.getSection("footprints"), re.DOTALL):
                name = re.search('^\s*"(.*?)"', i).groups()[0]
                
                try:
                    if re.search('\s*units:\s*(.*?)\n', i).groups()[0] == "MIL":  # mils
                        mnoznik = 0.0254
                    else:
                        mnoznik = self.mnoznik
                except:
                    mnoznik = self.mnoznik
                #
                if not name in self.libraries:
                    self.libraries[name] = {}
                
                self.libraries[name]["units"] = mnoznik
                self.libraries[name]["data"] = i
                #######################################################
                self.libraries[name]["silk"] = []
                for j in re.findall(r'(?=outline_polyline:([\s\S]*?)(?=close_polyline:|)(?=n_pins:|outline_polyline:|$))', i, re.DOTALL):
                    data = j.strip().split("\n")
                    #
                    if "close_polyline:" in data[-1]:
                        closePolyline = True
                        data.pop(-1)
                    else:
                        closePolyline = False
                    #
                    param1 = data[0].strip().split(" ")
                    
                    width = float(param1[0]) * mnoznik
                    x1 = float(param1[1]) * mnoznik
                    y1 = float(param1[2]) * mnoznik
                    
                    for k in data[1:]:
                        param2 = k.strip().split(" ")
                        
                        x2 = float(param2[1]) * mnoznik
                        y2 = float(param2[2]) * mnoznik
                        shape = int(param2[3]) # 0-line | 1-arc_cw | 2-arc_ccw
                        #
                        if shape == 0:
                            self.libraries[name]["silk"].append(['Line', x1, y1, x2, y2, width])
                        elif shape == 1:
                            self.libraries[name]["silk"].append(['Arc', x1, y1, x2, y2, width, -90])
                        else:
                            self.libraries[name]["silk"].append(['Arc', x1, y1, x2, y2, width, 90])
                        #
                        x1 = x2
                        y1 = y2
                    
                    if closePolyline:
                        x2 = float(param1[1]) * mnoznik
                        y2 = float(param1[2]) * mnoznik
                        
                        if shape == 0:
                            self.libraries[name]["silk"].append(['Line', x1, y1, x2, y2, width])
                        elif shape == 1:
                            self.libraries[name]["silk"].append(['Arc', x1, y1, x2, y2, width, -90])
                        else:
                            self.libraries[name]["silk"].append(['Arc', x1, y1, x2, y2, width, 90])
                #######################################################
                self.libraries[name]["pins"] = {}
                for j in re.findall(r'(?=pin:([\s\S]*?)(?=pin:|$))', i, re.DOTALL):
                    pinData = re.search('^\s*(".*?") (.*?) (.*?) (.*?) (.*?)\n', j).groups()
                    
                    if not pinData[0] in self.libraries[name]["pins"].keys():
                        self.libraries[name]["pins"][pinData[0]] = {}
                    
                    self.libraries[name]["pins"][pinData[0]] = {
                        "x": float(pinData[2]) * mnoznik,
                        "y": float(pinData[3]) * mnoznik,
                        "r": float(pinData[1]) * mnoznik / 2.,
                        "rot": 360 - float(pinData[4]),
                    }
                    #
                    topPad = re.search('top_pad: (.*?) (.*?) (.*?) (.*?) (.*?)($|\n)', j).groups()
                    
                    self.libraries[name]["pins"][pinData[0]]["top"] = {
                        "shape": int(topPad[0]), #1-round 2-square
                        "width": float(topPad[1]) * mnoznik,
                        "len1": float(topPad[2]) * mnoznik,
                        "len2": float(topPad[3]) * mnoznik,
                        "radius": float(topPad[4]) * mnoznik,
                    }
                    #
                    if len(re.findall(r'_pad:', j, re.DOTALL)) == 3: # pin
                        bottomPad = re.search('bottom_pad: (.*?) (.*?) (.*?) (.*?) (.*?)($|\n)', j).groups()

                        self.libraries[name]["pins"][pinData[0]]["bottom"] = {
                            "shape": int(bottomPad[0]), #1-round 2-square
                            "width": float(bottomPad[1]) * mnoznik,
                            "len1": float(bottomPad[2]) * mnoznik,
                            "len2": float(bottomPad[3]) * mnoznik,
                            "radius": float(bottomPad[4]) * mnoznik,
                        }
                #######################################################
    
    def getElements(self):
        try:
            if len(self.elements) == 0:
                for i in re.findall(r'part:\s+(.*?)\n(.*?)\n[\n|\[|parts]', self.getSection("parts"), re.DOTALL):
                    
                    try:
                        if re.search(r'units:\s+(.*)', i[0]).groups()[0] == "MIL":  # mils
                            mnoznik = 0.0254
                        else:
                            mnoznik = self.mnoznik
                    except:
                        mnoznik = self.mnoznik
                    #
                    partPos = re.search(r'pos:\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+([0-1])', i[1]).groups()
                    
                    locked = False
                    if int(partPos[4]):
                        locked = True
                    
                    side = "TOP"
                    rot = 360 - float(partPos[3])
                    
                    if int(partPos[2]) == 1:
                        side = "BOTTOM"
                        rot = float(partPos[3])
                    #
                    try:
                        value = re.search(r'value:\s+"(.*?)"', i[1]).groups()[0]
                    except:
                        value = ""
                    
                    self.elements.append({
                        'name': i[0], 
                        'library': "", 
                        'package': re.search(r'shape:\s+"(.*?)"', i[1]).groups()[0], 
                        'value': value, 
                        'x': float(partPos[0]) * mnoznik, 
                        'y': float(partPos[1]) * mnoznik, 
                        'pathAttribute': '',
                        'locked': locked,
                        'populated': False, 
                        'smashed': False, 
                        'rot': rot, 
                        'side': side,
                        'dataElement': i[1]
                    })
        except Exception as e:
            FreeCAD.Console.PrintWarning("getElements() error: {0}\n".format(e))
    
    def getSilkLayer(self, layerNew, layerNumber, display=[True, True, True, True]):
        pass
        
    def getSilkLayerModels(self, layerNew, layerNumber):
        if layerNumber[0] not in [7, 8]:
            return
        #
        self.getLibraries()
        self.getElements()
        
        try:
            for i in self.elements:
                X1 = i['x']
                Y1 = i['y']
                ROT = i['rot']
                
                if i['side'] == "TOP":
                    SIDE = 1
                else:
                    SIDE = 0
                
                if layerNumber[0] == 7 and SIDE != 1:
                    continue
                elif layerNumber[0] == 8 and SIDE != 0:
                    continue
                
                if i['package'] in self.libraries.keys():
                    for j in self.libraries[i['package']]["silk"]:
                        if j[0] == "Line":
                            layerNew.addLineWidth(j[1] + X1, j[2] + Y1, j[3] + X1, j[4] + Y1, j[5])
                            layerNew.addRotation(X1, Y1, ROT)
                            layerNew.setChangeSide(X1, Y1, SIDE)
                            layerNew.setFace()
                        else: # arc
                            if layerNew.addArcWidth([j[1] + X1, j[2] + Y1], [j[3] + X1, j[4] + Y1], j[6], j[5]):
                                layerNew.addRotation(X1, Y1, ROT)
                                layerNew.setChangeSide(X1, Y1, SIDE)
                                layerNew.setFace()
        except Exception as e:
            FreeCAD.Console.PrintWarning("getSilkLayerModels() error: {0}\n".format(e))
    
    def getHoles(self, holesObject, types, Hmin, Hmax):
        ''' holes/vias '''
        holesList = []
        
        # vias
        if types['V']:
            for i in re.findall(r'vtx: .+? (.+?) (.+?) .+? .+? .+? ([1-9][0-9]*)', self.projektBRD):
                x = float(i[0]) * self.mnoznik
                y = float(i[1]) * self.mnoznik
                r = float(i[2]) * self.mnoznik / 2. + 0.001
                
                holesList = self.addHoleToObject(holesObject, Hmin, Hmax, types['IH'], x, y, r, holesList)
        ## pads / holes
        if types['P'] or types['H']:
            self.getLibraries()
            self.getElements()
            
            try:
                for i in self.elements:
                    X1 = i['x']
                    Y1 = i['y']
                    ROT = i['rot']
                    
                    if i['package'] in self.libraries.keys():
                        for j in self.libraries[i['package']]["pins"].keys():
                            if "bottom" in self.libraries[i['package']]["pins"][j].keys():
                                x = self.libraries[i['package']]["pins"][j]["x"]
                                y = self.libraries[i['package']]["pins"][j]["y"]
                                r = self.libraries[i['package']]["pins"][j]["r"] + 0.001
                                
                                if self.libraries[i['package']]["pins"][j]["bottom"]["width"] == 0 and self.libraries[i['package']]["pins"][j]["top"]["width"] == 0 and not types['H']:
                                    continue
                                elif (self.libraries[i['package']]["pins"][j]["bottom"]["width"] != 0 or self.libraries[i['package']]["pins"][j]["top"]["width"] != 0) and not types['P']:
                                    continue
                                
                                [xR, yR] = self.obrocPunkt([x, y], [X1, Y1], ROT)
                                if i["side"] == "BOTTOM":
                                    xR = self.odbijWspolrzedne(xR, X1)
                                
                                holesList = self.addHoleToObject(holesObject, Hmin, Hmax, types['IH'], xR, yR, r, holesList)
            except Exception as e:
                FreeCAD.Console.PrintWarning("getHoles() error. {0}\n".format(e))
        
    def getCornsers(self, data):
        result = []
        #
        try:
            corners = re.findall(r'corner:\s+[0-9]*\s+(.*?)\s+(.*?)\s+([0-9]*)', data, re.MULTILINE|re.DOTALL)
            
            for i in range(len(corners)):
                x1 = float(corners[i][0]) * self.mnoznik
                y1 = float(corners[i][1]) * self.mnoznik
                cType = int(corners[i][2])
                
                if i + 1 < len(corners):
                    x2 = float(corners[i + 1][0]) * self.mnoznik
                    y2 = float(corners[i + 1][1]) * self.mnoznik
                else:
                    x2 = float(corners[0][0]) * self.mnoznik
                    y2 = float(corners[0][1]) * self.mnoznik
                
                if [x1, y1] == [x2, y2]:
                    continue
                
                if cType == 0:
                    result.append(['Line', x1, y1, x2, y2])
                elif cType == 1:
                    result.append(['Arc', x1, y1, x2, y2, -90])
                else:
                    result.append(['Arc', x1, y1, x2, y2, 90])
        except Exception as e:
            FreeCAD.Console.PrintWarning("getCornsers() error: {0}\n".format(e))
        #
        return result

    def getPCB(self, borderObject):
        try:
            for i in re.findall(r'outline:\s+(.*?)\s+.*?\n(.*?)\n\n', self.getSection("board"), re.DOTALL):
                for j in self.getCornsers(i[1]):
                    if j[0] == 'Line':
                        borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(j[1], j[2], 0), FreeCAD.Vector(j[3], j[4], 0)),False)
                    if j[0] == 'Arc':
                        [x3, y3] = self.arcMidPoint([j[1], j[2]], [j[3], j[4]], j[5])
                        arc = Part.ArcOfCircle(FreeCAD.Vector(j[1], j[2], 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(j[3], j[4], 0.0))
                        borderObject.addGeometry(arc)
        except Exception as e:
            FreeCAD.Console.PrintWarning("getPCB() error: {0}\n".format(e))
