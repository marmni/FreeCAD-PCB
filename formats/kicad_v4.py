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
import __builtin__
import Part
import re
from math import sqrt

from PCBconf import PCBlayers, softLayers
from PCBobjects import *
from formats.PCBmainForms import *
from formats.kicad_v3 import KiCadv3_PCB, setProjectFile
from command.PCBgroups import *


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
        self.generateLayers()
        self.spisWarstw.sortItems(1)
    
    def getBoardThickness(self):
        return float(re.findall(r'\(thickness (.+?)\)', self.projektBRD)[0])
        
    def getLayersNames(self):
        dane = {}
        
        layers = re.search(r'\[start\]\(layers(.+?)\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL).group(0)
        for i in re.findall(r'\((.*?) (.*?) .*?\)', layers):
            dane[int(i[0])] = i[1]
        
        return dane


class KiCadv4_PCB(KiCadv3_PCB):
    def __init__(self, filename):
        KiCadv3_PCB.__init__(self, filename)
        
        self.dialogMAIN = dialogMAIN(filename)
        self.databaseType = "kicad_v4"
        #
        self.borderLayerNumber = 44
    
    def getParts(self, koloroweElemnty, adjustParts, groupParts, partMinX, partMinY, partMinZ):
        self.__SQL__.reloadList()
        #
        PCB_ER = []
        #
        for i in re.findall(r'\[start\]\(module(.+?)\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL):
            [x, y, rot] = re.search(r'\(at\s+([0-9\.-]*?)\s+([0-9\.-]*?)(\s+[0-9\.-]*?|)\)', i).groups()
            layer = re.search(r'\(layer\s+(.+?)\)', i).groups()[0]
            ##
            ##package = re.search(r'\s+(".+?"|.+?)\s+\(layer', i).groups()[0]
            #package = re.search(r'\s+(".+?"|.+?)([\s+locked\s+|\s+]+)\(layer', i).groups()[0]
            #if ':' in package:
                #package = package.replace('"', '').split(':')[-1]
            #else:
                #if '"' in package:
                    #package = package.replace('"', '')
                #else:
                    #package = package
            package = re.search(r'\s+(".+?"|.+?)\(layer', i).groups()[0]
            package = re.sub('locked|placed|pla', '', package).split(':')[-1]
            package = package.replace('"', '')
            #
            library = package
            
            x = float(x)
            y = float(y) * (-1)
            if rot == '':
                rot = 0.0
            else:
                rot = float(rot)
            
            if self.spisWarstw[layer] == 0:  # top
                side = "TOP"
                mirror = 'None'
            else:
                side = "BOTTOM"
                #rot = (rot + 180) * (-1)
                if rot < 180:
                    rot = (180 - rot)
                else:
                    rot = int(rot % 180) * (-1)
                mirror = 'Local Y axis'
            ####
            # textReferencere
            textReferencere = re.search(r'\(fp_text reference\s+(.*)', i, re.MULTILINE|re.DOTALL).groups()[0]
            [tr_x, tr_y, tr_rot] = re.search(r'\(at\s+([0-9\.-]*?)\s+([0-9\.-]*?)(\s+[0-9\.-]*?|)\)', textReferencere).groups()
            tr_layer = re.search(r'\(layer\s+(.+?)\)', textReferencere).groups()[0]
            tr_fontSize = re.search(r'\(font\s+(\(size\s+(.+?) .+?\)|)', textReferencere).groups()[0]
            tr_visibility = re.search(r'\(layer\s+.+?\)\s+(hide|)', textReferencere).groups()[0]
            tr_value = re.search(r'^(".+?"|.+?)\s', textReferencere).groups()[0].replace('"', '')
            #
            tr_x = float(tr_x)
            tr_y = float(tr_y) * (-1)
            if tr_rot == '':
                tr_rot = rot
            else:
                tr_rot = float(tr_rot)
            
            if tr_fontSize == '':
                tr_fontSize = 0.7
            else:
                tr_fontSize = float(tr_fontSize.split()[1])
            
            if tr_visibility == 'hide':
                tr_visibility = False
            else:
                tr_visibility = True
            
            EL_Name = [tr_value, tr_x + x, tr_y + y, tr_fontSize, tr_rot, side, "center", False, mirror, '', True]
            ####
            # textValue
            textValue = re.search(r'\(fp_text value\s+(.*)', i, re.MULTILINE|re.DOTALL).groups()[0]
            [tv_x, tv_y, tv_rot] = re.search(r'\(at\s+([0-9\.-]*?)\s+([0-9\.-]*?)(\s+[0-9\.-]*?|)\)', textValue).groups()
            tv_layer = re.search(r'\(layer\s+(.+?)\)', textValue).groups()[0]
            tv_fontSize = re.search(r'\(font\s+(\(size\s+(.+?) .+?\)|)', textValue).groups()[0]
            tv_visibility = re.search(r'\(layer\s+.+?\)\s+(hide|)', textValue).groups()[0]
            tv_value  = re.search(r'^(".+?"|.+?)\s', textValue).groups()[0].replace('"', '')
            #
            tv_x = float(tv_x)
            tv_y = float(tv_y) * (-1)
            if tv_rot == '':
                tv_rot = rot
            else:
                tv_rot = float(tv_rot)
            
            if tv_fontSize == '':
                tv_fontSize = 0.7
            else:
                tv_fontSize = float(tv_fontSize.split()[1])
            
            if tv_visibility == 'hide':
                tv_visibility = False
            else:
                tv_visibility = True
            
            EL_Value = [tv_value, tv_x + x, tv_y + y, tv_fontSize, tv_rot, side, "center", False, mirror, '', tv_visibility]
            #
            newPart = [[EL_Name[0], package, EL_Value[0], x, y, rot, side, library], EL_Name, EL_Value]
            wyn = self.addPart(newPart, koloroweElemnty, adjustParts, groupParts, partMinX, partMinY, partMinZ)
            #
            if wyn[0] == 'Error':  # lista brakujacych elementow
                partNameTXT = partNameTXT_label = self.generateNewLabel(EL_Name[0])
                if isinstance(partNameTXT, unicode):
                    partNameTXT = unicodedata.normalize('NFKD', partNameTXT).encode('ascii', 'ignore')
                
                PCB_ER.append([partNameTXT, package, EL_Value[0], library])
        ####
        return PCB_ER

    def generate(self, doc, groupBRD, filename):
        board = self.getPCB()
        if len(board[0]):
            self.generatePCB(board, doc, groupBRD, self.dialogMAIN.gruboscPlytki.value())
        else:
            FreeCAD.Console.PrintWarning('No PCB border detected!\n')
            return False
        # holes/vias/pads
        types = {'H':self.dialogMAIN.plytkaPCB_otworyH.isChecked(), 'V':self.dialogMAIN.plytkaPCB_otworyV.isChecked(), 'P':self.dialogMAIN.plytkaPCB_otworyP.isChecked()}
        self.generateHoles(self.getHoles(types), doc, self.dialogMAIN.holesMin.value(), self.dialogMAIN.holesMax.value())
        #
        if self.dialogMAIN.plytkaPCB_elementy.isChecked():
            partsError = self.getParts(self.dialogMAIN.plytkaPCB_elementyKolory.isChecked(), self.dialogMAIN.adjustParts.isChecked(), self.dialogMAIN.plytkaPCB_grupujElementy.isChecked(), self.dialogMAIN.partMinX.value(), self.dialogMAIN.partMinY.value(), self.dialogMAIN.partMinZ.value())
            if self.dialogMAIN.plytkaPCB_plikER.isChecked():
                self.generateErrorReport(partsError, filename)
        ##  dodatkowe warstwy
        grp = createGroup_Layers()
        grp_2 = createGroup_Areas()
        for i in range(self.dialogMAIN.spisWarstw.rowCount()):
            if self.dialogMAIN.spisWarstw.cellWidget(i, 0).isChecked():
                ID = int(self.dialogMAIN.spisWarstw.item(i, 1).text())
                name = str(self.dialogMAIN.spisWarstw.item(i, 4).text())
                try:
                    color = self.dialogMAIN.spisWarstw.cellWidget(i, 2).getColor()
                except:
                    color = None
                try:
                    transp = self.dialogMAIN.spisWarstw.cellWidget(i, 3).value()
                except:
                    transp = None
                    
                if ID == 106:  # MEASURES
                    self.addDimensions(self.getDimensions(), doc, grp, name, self.dialogMAIN.gruboscPlytki.value(), color)
                elif ID in [32, 33]:  # glue
                    self.generateGlue(self.getGlue(ID), doc, grp, name, color, ID)
                elif ID in [36, 37]:
                    self.getSilkLayer(doc, ID, grp, name, color, transp)
                elif ID in [107, 108]:  # pady
                    self.getPads(doc, ID, grp, name, color, transp)
                elif ID in [0, 31]:  # paths
                    self.generatePaths(self.getPaths(ID), doc, grp, name, color, ID, transp)
                elif ID == 105:  # annotations
                    self.addAnnotations(self.getAnnotations(), doc, color)
                else:
                    self.generateConstraintAreas(self.getConstraintAreas(ID), doc, ID, grp_2, name, color, transp)
        ##
        return doc
