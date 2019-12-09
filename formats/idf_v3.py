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
from formats.idf_v2 import IDFv2_PCB


def getUnitsDefinition(projektBRD):
    if re.search(r'THOU', projektBRD):
        return 0.0254
    else:
        return 1




class dialogMAIN(dialogMAIN_FORM):
    def __init__(self, filename=None, parent=None):
        dialogMAIN_FORM.__init__(self, parent)
        self.databaseType = "idf"
        #        
        freecadSettings = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB")
        
        self.packageByDecal = QtGui.QCheckBox(u"PCB-Decals")
        self.packageByDecal.setChecked(freecadSettings.GetBool("pcbDecals", True))
        self.layParts.addWidget(self.packageByDecal, 4, 1, 1, 1)
        #
        self.projektBRD = builtins.open(filename, "r").read().replace('\r', '')
        self.layersNames = self.getLayersNames()
        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetBool("boardImportThickness", True):
            self.gruboscPlytki.setValue(self.getBoardThickness())
        ###
        self.generateLayers(["NOTES", "HEADER", "BOARD_OUTLINE", "DRILLED_HOLES", "PLACEMENT", "OTHER_OUTLINE", "ROUTE_KEEPOUT", "PLACE_KEEPOUT", "PLACE_REGION"]) # blocked layers
        self.spisWarstw.sortItems(1)

    def getBoardThickness(self):
        return float(re.findall('^\.BOARD_OUTLINE\s+[0-9A-Za-z]*\n(.+?)\n', self.projektBRD, re.MULTILINE|re.DOTALL)[0]) * getUnitsDefinition(self.projektBRD)
    
    def getLayersNames(self):
        dane = {}
        for i in re.findall('^\.([a-zA-Z0-9_]*)[\s+0-9A-Za-z]*\n(.+?)\.END_[a-zA-Z0-9_]*\n', self.projektBRD, re.MULTILINE|re.DOTALL):
            dane[i[0]] = {"name": i[0]}
        # extra layers
        dane["ANNOTATIONS"] = {"name": softLayers[self.databaseType]["ANNOTATIONS"]["description"]}
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


class IDFv3_PCB(IDFv2_PCB):
    def __init__(self, filename, parent):
        #IDFv2_PCB.__init__(filename, parent)
        self.fileName = filename
        self.dialogMAIN = dialogMAIN(self.fileName)
        self.databaseType = "idf"
        self.parent = parent
        self.mnoznik = 1
    
    def defineFunction(self, layerNumber):
        if layerNumber == "ANNOTATIONS":
            return "annotations"
        else:
            return "constraint"

    def getParts(self):
        parts = []
        try:
            data = self.getArea("PLACEMENT")[0].split("\n")
            
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
                        'rot': float(param[6]), 
                        'side': param[7],
                        'z': float(param[5]) * self.mnoznik,
                        'dataElement': i + "__"
                    })
        except:
            pass
        #
        return parts

    def getNormalAnnotations(self):
        adnotacje = []
        #
        for i in self.getArea("NOTES")[0].split('\n'):
            dane = re.findall(r'(".*?"|.*?)[\s|\n]+', i + "\n", re.DOTALL)
            if len(dane) <= 1:
                continue
            
            adnotacje.append({
                "text": str(dane[4])[1:-1],
                "x": float(dane[0]) * self.mnoznik,
                "y": float(dane[1]) * self.mnoznik,
                "z": 0,
                "size": float(dane[2]) * self.mnoznik,
                "rot": 0,
                "side": 'TOP',
                "align": "bottom-left",
                "spin": True,
                "font": 'Proportional',
                "display": True,
                "distance": 1,
                "tracking": 0,
                "mode": 'anno'
            })
        #
        return adnotacje

    def getHoles(self, holesObject, types, Hmin, Hmax):
        ''' holes/vias '''
        if types['IH']:  # detecting collisions between holes - intersections
            holesList = []
        
        try:
            for i in self.getArea("DRILLED_HOLES")[0].strip().split('\n'):
                dane = re.sub(r'\s+', ' ', i).split(" ")
                if dane[3] == "NPTH":  # Non-plated (non-conducting) through hole
                    continue
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
                            if dane[5] == 'PIN' and types['P'] or dane[5] == 'VIA' and types['V'] or types['H'] and dane[5] not in ["PIN", "VIA"]:
                                holesList.append([x, y, r])
                                holesObject.addGeometry(Part.Circle(FreeCAD.Vector(x, y, 0.), FreeCAD.Vector(0, 0, 1), r))
                        else:
                            FreeCAD.Console.PrintWarning("Intersection between holes detected. Hole x={:.2f}, y={:.2f} will be omitted.\n".format(x, y))
                    else:
                        if dane[5] == 'PIN' and types['P'] or dane[5] == 'VIA' and types['V'] or types['H'] and dane[5] not in ["PIN", "VIA"]:
                            holesObject.addGeometry(Part.Circle(FreeCAD.Vector(x, y, 0.), FreeCAD.Vector(0, 0, 1), r))
        except Exception as e:
            FreeCAD.Console.PrintWarning("{0}\n".format(e))
