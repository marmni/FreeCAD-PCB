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
import builtins
import re
#
from PCBconf import PCBlayers, softLayers
from PCBobjects import *
from formats.dialogMAIN_FORM import dialogMAIN_FORM
from command.PCBgroups import *
from PCBfunctions import mathFunctions, filterHoles


def getUnitsDefinition(projektBRD):
    if re.search(r'THOU', projektBRD):
        return 0.0254
    elif re.search(r'MM', projektBRD):
        return 1
    else:
        return 0.000001


class dialogMAIN(dialogMAIN_FORM):
    def __init__(self, filename=None, parent=None):
        dialogMAIN_FORM.__init__(self, parent)
        self.databaseType = "idf_v2"
        #        
        freecadSettings = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB")
        
        self.plytkaPCB_otworyV.setChecked(False)
        self.plytkaPCB_otworyV.setDisabled(True)
        
        self.packageByDecal = QtGui.QCheckBox(u"PCB-Decals")
        self.packageByDecal.setStyleSheet('margin-left:20px')
        self.packageByDecal.setChecked(freecadSettings.GetBool("pcbDecals", True))
        self.lay.addWidget(self.packageByDecal, 9, 3, 1, 3)
        #
        self.projektBRD = builtins.open(filename, "r").read().replace('\r', '')
        self.layersNames = self.getLayersNames()
        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetBool("boardImportThickness", True):
            self.gruboscPlytki.setValue(self.getBoardThickness())
        ###
        self.generateLayers(["HEADER", "BOARD_OUTLINE", "DRILLED_HOLES", "PLACEMENT", "OTHER_OUTLINE", "ROUTE_KEEPOUT", "PLACE_KEEPOUT", "PLACE_REGION"]) # blocked layers
        self.spisWarstw.sortItems(1)
        
    def getBoardThickness(self):
        return float(re.findall(r'\.BOARD_OUTLINE\n(.+?)\n', self.projektBRD)[0]) * getUnitsDefinition(self.projektBRD)
    
    def getLayersNames(self):
        dane = {}
        for i in re.findall('^\.([a-zA-Z0-9_]*)\n(.+?)\.END_[a-zA-Z0-9_]*\n', self.projektBRD, re.MULTILINE|re.DOTALL):
            dane[i[0]] = {"name": i[0]}
        # extra layers
        dane["T_ROUTE_KEEPOUT"] = {"name": softLayers[self.databaseType]["T_ROUTE_KEEPOUT"]["description"]}
        dane["B_ROUTE_KEEPOUT"] = {"name": softLayers[self.databaseType]["B_ROUTE_KEEPOUT"]["description"]}
        dane["V_ROUTE_KEEPOUT"] = {"name": softLayers[self.databaseType]["V_ROUTE_KEEPOUT"]["description"]}
        dane["T_PLACE_KEEPOUT"] = {"name": softLayers[self.databaseType]["T_PLACE_KEEPOUT"]["description"]}
        dane["B_PLACE_KEEPOUT"] = {"name": softLayers[self.databaseType]["B_PLACE_KEEPOUT"]["description"]}
        dane["V_PLACE_KEEPOUT"] = {"name": softLayers[self.databaseType]["V_PLACE_KEEPOUT"]["description"]}
        dane["T_PLACE_REGION"] = {"name": softLayers[self.databaseType]["T_PLACE_REGION"]["description"]}
        dane["B_PLACE_REGION"] = {"name": softLayers[self.databaseType]["B_PLACE_REGION"]["description"]}
        dane["V_PLACE_REGION"] = {"name": softLayers[self.databaseType]["V_PLACE_REGION"]["description"]}
        #
        return dane


class IDFv2_PCB(mathFunctions):
    def __init__(self, filename, parent):
        self.fileName = filename
        self.dialogMAIN = dialogMAIN(self.fileName)
        self.databaseType = "idf_v2"
        self.parent = parent
        self.mnoznik = 1

    def defineFunction(self, layerNumber):
        return "constraint"
        
    def setProject(self):
        self.projektBRD = builtins.open(self.fileName, "r").read().replace("\r\n", "\n").replace("\r", "\n")
        self.mnoznik = getUnitsDefinition(self.projektBRD)
    
    def getArea(self, areaName):
        data = re.findall(r'\.'+areaName+'\n(.*?)\.END_'+areaName+'\n', self.projektBRD, re.DOTALL)
        if len(data):
            return data[0]
        else:
            return None

    def getConstraintAreas(self, layerNumber):
        area = None
        #################
        if "PLACE_KEEPOUT" in layerNumber:
            if layerNumber.startswith("B_"):
                side = "BOTTOM"
            elif layerNumber.startswith("V_"):
                side = "BOTH"
            else:
                side = "TOP"
            
            area = self.getArea("PLACE_KEEPOUT")
        elif "VIA_KEEPOUT" in layerNumber:
            area = self.getArea("VIA_KEEPOUT")
            side = None
        elif "PLACE_OUTLINE" in layerNumber:
            area = self.getArea("PLACE_OUTLINE")
            side = None
        elif "ROUTE_OUTLINE" in layerNumber:
            area = self.getArea("ROUTE_OUTLINE")
            side = None
        elif "PLACE_REGION" in layerNumber:
            if layerNumber.startswith("B_"):
                side = "BOTTOM"
            elif layerNumber.startswith("V_"):
                side = "BOTH|ALL"
            else:
                side = "TOP"
            
            area = self.getArea("PLACE_REGION")
        elif "ROUTE_KEEPOUT" in layerNumber:
            if layerNumber.startswith("B_"):
                side = "BOTTOM"
            elif layerNumber.startswith("V_"):
                side = "BOTH"
            else:
                side = "TOP"
            
            area = self.getArea("ROUTE_KEEPOUT")
        #################
        areas = []
        
        if area:
            for i in self.pobierzLinie(area):
                if side != None and i[0][0] not in side:
                    continue
                #
                if len(i[0]) <= 3:
                    i.pop(0)
                
                areas.append(['polygon', i])
        #
        return areas

    def getParts(self):
        parts = []
        data = self.getArea("PLACEMENT").split("\n")
        
        for i in [" ".join(data[i:i+2]) for i in range(0, len(data), 2)]:
            param = re.findall(r'(".*?"|.*?)[\s|\n]+', i + "\n", re.DOTALL)
            if len(param) > 1:
                parts.append({
                    'name': param[2].replace('"', ''), 
                    'library': param[1].replace('"', ''), 
                    'package': param[0].replace('"', ''), 
                    'value': '', 
                    'x': float(param[3]) * self.mnoznik, 
                    'y': float(param[4]) * self.mnoznik,
                    'locked': False,
                    'populated': False, 
                    'smashed': False, 
                    'rot': float(param[5]), 
                    'side': param[6],
                    'dataElement': i + "__"
                })
        #
        return parts
    
    def getHoles(self, holesObject, types, Hmin, Hmax):
        ''' holes/vias '''
        if types['IH']:  # detecting collisions between holes - intersections
            holesList = []
        
        try:
            for i in self.getArea("DRILLED_HOLES").strip().split('\n'):
                dane = i.split(" ")
                #
                r = float(dane[0]) * self.mnoznik / 2.
                x = float(dane[1]) * self.mnoznik
                y = float(dane[2]) * self.mnoznik
                #
                if filterHoles(r, Hmin, Hmax):
                    if types['IH']:  # detecting collisions between holes - intersections
                        add = True
                        try:
                            for k in holesList:
                                d = sqrt( (x - k[0]) ** 2 + (y - k[1]) ** 2)
                                if(d < r + k[2]):
                                    add = False
                                    break
                        except Exception as e:
                            FreeCAD.Console.PrintWarning("1. {0}\n".format(e))
                        
                        if (add):
                            if dane[4] in ['BOARD', 'NOREFDES'] and types['H'] or not dane[4] in ['BOARD', 'NOREFDES'] and types['P']:
                                holesList.append([x, y, r])
                                holesObject.addGeometry(Part.Circle(FreeCAD.Vector(x, y, 0.), FreeCAD.Vector(0, 0, 1), r))
                        else:
                            FreeCAD.Console.PrintWarning("Intersection between holes detected. Hole x={:.2f}, y={:.2f} will be omitted.\n".format(i["x"], i["y"]))
                    else:
                        if dane[4] in ['BOARD', 'NOREFDES'] and types['H'] or not dane[4] in ['BOARD', 'NOREFDES'] and types['P']:
                            holesObject.addGeometry(Part.Circle(FreeCAD.Vector(x, y, 0.), FreeCAD.Vector(0, 0, 1), r))
        except Exception as e:
            FreeCAD.Console.PrintWarning("{0}\n".format(e))
        
    def pobierzLinie(self, pcb):
        pcb = re.findall(r'(.*?)\n', pcb, re.MULTILINE|re.DOTALL)
        #
        data = []
        data.append([])
        
        for i in pcb:
            if len(data[-1]) > 1:
                if i == data[-1][0] or i == data[-1][1]:
                    data[-1].append(i)
                    data.append([])
                else:
                    data[-1].append(i)
            else:
                data[-1].append(i)
        #
        dataOut = []
        for i in data:
            if len(i):
                direction = float(i[-1].split(" ")[0])
        
                if len(i[0].split(" ")) <= 3:
                    stop = 1
                    dataOut.append([i[0].split(" ")])
                else:
                    stop = 0
                    dataOut.append([])
                
                
                if direction == 0:  # counter-clockwise direction
                    for j in range(len(i)-1, stop, -1):
                        data_1 = i[j].split(" ")
                        data_2 = i[j - 1].split(" ")
                        
                        x1 = float(data_1[1]) * self.mnoznik
                        y1 = float(data_1[2]) * self.mnoznik
                        eType = float(data_1[3])
                        
                        x2 = float(data_2[1]) * self.mnoznik
                        y2 = float(data_2[2]) * self.mnoznik
                        
                        if eType == 0.0:
                            dataOut[-1].append(['Line', x1, y1, x2, y2])
                        else:
                            dataOut[-1].append(['Arc', x1, y1, x2, y2, eType])
                else:  # clockwise direction
                    for j in range(stop, len(i)-1):
                        data_1 = i[j].split(" ")
                        data_2 = i[j + 1].split(" ")
                        
                        x1 = float(data_1[1]) * self.mnoznik
                        y1 = float(data_1[2]) * self.mnoznik
                        eType = float(data_1[3])
                        
                        x2 = float(data_2[1]) * self.mnoznik
                        y2 = float(data_2[2]) * self.mnoznik
                        
                        if eType == 0.0:
                            dataOut[-1].append(['Line', x1, y1, x2, y2])
                        else:
                            dataOut[-1].append(['Arc', x1, y1, x2, y2, eType])
        #
        return dataOut
        
    def getPCB(self, borderObject):
        for i in self.pobierzLinie(self.getArea("BOARD_OUTLINE")):
            for j in range(1, len(i)):  # dodanie linii/luku
                if i[j][0] == 'Arc':  # luk
                    x1 = i[j][1]
                    y1 = i[j][2]
                    x2 = i[j][3]
                    y2 = i[j][4]
                    
                    [x3, y3] = self.arcMidPoint([x1, y1], [x2, y2], i[j][5] * -1)
                    arc = Part.ArcOfCircle(FreeCAD.Vector(x1, y1, 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(x2, y2, 0.0))
                    borderObject.addGeometry(arc)
                else:  # linia
                    x1 = i[j][1]
                    y1 = i[j][2]
                    x2 = i[j][3]
                    y2 = i[j][4]
                    
                    borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x2, y2, 0)))
