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
import Sketcher
import builtins
import Part
import re
import os
from math import sqrt

from PCBconf import PCBlayers, softLayers
from PCBobjects import *
from formats.PCBmainForms import *
from formats.kicad_v3 import KiCadv3_PCB, setProjectFile
from command.PCBgroups import *
from formats.dialogMAIN_FORM import dialogMAIN_FORM
from PCBfunctions import mathFunctions
from PCBconf import kicadColorsDefinition


class dialogMAIN(dialogMAIN_FORM):
    def __init__(self, filename=None, parent=None):
        dialogMAIN_FORM.__init__(self, parent)
        self.databaseType = "kicad_v4"
        #
        self.plytkaPCB_otworyH.setChecked(False)
        self.plytkaPCB_otworyH.setDisabled(True)
        #
        self.projektBRD = setProjectFile(filename)
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
        dane[106] = {"name": softLayers[self.databaseType][106]["name"], "color": softLayers[self.databaseType][106]["color"]}
        #  annotations
        dane[905] = {"name": softLayers[self.databaseType][905]["description"], "color": softLayers[self.databaseType][905]["color"], "type": "anno", "number": 0}
        # pad
        dane[107] = {"name": softLayers[self.databaseType][107]["name"], "color": softLayers[self.databaseType][107]["color"]}
        dane[108] = {"name": softLayers[self.databaseType][108]["name"], "color": softLayers[self.databaseType][108]["color"]}
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
