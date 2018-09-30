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

from PCBobjects import *
from formats.PCBmainForms import *
from command.PCBgroups import *


def getUnitsDefinition(projektBRD):
    if re.search(r'THOU', projektBRD):
        return 0.0254
    else:
        return 1


class dialogMAIN(dialogMAIN_FORM):
    def __init__(self, filename=None, parent=None):
        dialogMAIN_FORM.__init__(self, parent)
        self.databaseType = "idf_v3"
        #
        freecadSettings = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB")
        
        self.packageByDecal = QtGui.QCheckBox(u"PCB-Decals")
        self.packageByDecal.setStyleSheet('margin-left:20px')
        self.packageByDecal.setChecked(freecadSettings.GetBool("pcbDecals", True))
        self.lay.addWidget(self.packageByDecal, 9, 2, 1, 3)
        #
        self.projektBRD = builtins.open(filename, "r").read().replace('\r', '')
        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetBool("boardImportThickness", True):
            self.gruboscPlytki.setValue(self.getBoardThickness())
        ##
        self.generateLayers()
        self.spisWarstw.sortItems(1)
        
    def getBoardThickness(self):
        return float(re.findall(r'\.BOARD_OUTLINE .+?\n(.+?)\n', self.projektBRD)[0]) * getUnitsDefinition(self.projektBRD)


class IDFv3_PCB(mainPCB):
    def __init__(self, filename):
        mainPCB.__init__(self, None)
        
        self.dialogMAIN = dialogMAIN(filename)
        self.mnoznik = 1
        self.databaseType = "idf_v3"
        
    def pobierzLinie(self, pcb):
        pcbOBJ = {}
        for i in pcb:
            dane = ' '.join(i.split()).split(" ")
            
            #fam = dane[0]
            x = dane[1]
            y = dane[2]
            eType = dane[3]
            
            if not dane[0] in pcbOBJ.keys():
                pcbOBJ[dane[0]] = []
            pcbOBJ[dane[0]].append([x, y, eType])
        
        PCB_PCB = []
        for i in pcbOBJ.keys():
            PCB_PCB.append([])
            for j in range(1, len(pcbOBJ[i])):
                x1 = float(pcbOBJ[i][j][0]) * self.mnoznik
                y1 = float(pcbOBJ[i][j][1]) * self.mnoznik
                eType = float(pcbOBJ[i][j][2])
                
                x2 = float(pcbOBJ[i][j - 1][0]) * self.mnoznik
                y2 = float(pcbOBJ[i][j - 1][1]) * self.mnoznik
                    
                if eType == 0.0:
                    PCB_PCB[-1].append(['Line', x1, y1, x2, y2])
                elif eType == 360:
                    r = sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
                    PCB_PCB[-1].append(['Circle', x2, y2, r])
                else:
                    PCB_PCB[-1].append(['Arc', x1, y1, x2, y2, eType])
        
        return PCB_PCB
        
    def getPCB(self):
        PCB = []
        wygenerujPada = True
        ###
        pcb = re.search(r'\.BOARD_OUTLINE .*?\n(.*?)\.END_BOARD_OUTLINE', self.projektBRD, re.DOTALL).groups()[0]
        pcb = pcb.strip().split('\n')[1:]
        PCB_PCB = self.pobierzLinie(pcb)
        ###
        for i in PCB_PCB:
            for j in range(len(i)):
                if i[j][0] == 'Arc':
                    x1 = i[j][1]
                    y1 = i[j][2]
                    x2 = i[j][3]
                    y2 = i[j][4]
                    
                    PCB.append(['Arc', x1, y1, x2, y2, i[j][5]])
                    wygenerujPada = False
                elif i[j][0] == 'Circle':
                    x = i[j][1]
                    y = i[j][2]
                    r = i[j][3]
                    
                    PCB.append(['Circle', x, y, r])
                else:
                    x1 = i[j][1]
                    y1 = i[j][2]
                    x2 = i[j][3]
                    y2 = i[j][4]
                    
                    PCB.append(['Line', x1, y1, x2, y2])
        
        return [PCB, wygenerujPada]
    
    def getParts(self, koloroweElemnty, adjustParts, groupParts, partMinX, partMinY, partMinZ, decal):
        PCB_ER = []
        try:
            elementy = re.search(r'\.PLACEMENT\n(.*?)\.END_PLACEMENT\n', self.projektBRD, re.DOTALL).groups()[0]
            #elementy = re.findall(r'(.*?)\s+(.*?)\s+(.*?)[\n |\n]\s+(.*?)\s+(.*?)\s+.*?\s+(.*?)\s+(TOP|BOTTOM)\s+(PLACED|UNPLACED|ECAD|MCAD)\n', elementy, re.DOTALL)
            elementy = re.findall(r'(".*?"|.*?)\s+(".*?"|.*?)\s+(.*?)\s{0,}\n\s{0,}([0-9-.,]*)\s+([0-9-.,]*)\s+.*?\s+([0-9-.,]*)\s+(TOP|BOTTOM)\s+(PLACED|UNPLACED|ECAD|MCAD)\s{0,}\n', elementy, re.DOTALL)
            
            for i in elementy:
                package = i[0].replace('"', '')
                library = i[1].replace('"', '')
                name = i[2].replace('"', '')
                x = float(i[3]) * self.mnoznik
                y = float(i[4]) * self.mnoznik
                rot = float(i[5])
                side = i[6]
                #value = i[2]
                value = ''

                EL_Name = ['', x, y, 1.27, rot, side, "bottom-left", False, 'None', '', True]
                EL_Value = ['', x, y, 1.27, rot, side, "bottom-left", False, 'None', '', True]
                #
                if not decal:
                    newPart = [[name, library, value, x, y, rot, side, package], EL_Name, EL_Value]
                else:
                    newPart = [[name, package, value, x, y, rot, side, library], EL_Name, EL_Value]
                wyn = self.addPart(newPart, koloroweElemnty, adjustParts, groupParts, partMinX, partMinY, partMinZ)
                #
                if wyn[0] == 'Error':  # lista brakujacych elementow
                    partNameTXT = partNameTXT_label = self.generateNewLabel(name)
                    if isinstance(partNameTXT, str):
                        partNameTXT = unicodedata.normalize('NFKD', partNameTXT).encode('ascii', 'ignore')
                    
                    PCB_ER.append([partNameTXT, package, value, library])
        except:
            pass
        #
        return PCB_ER

    def getConstraintAreas(self, layerNumber):
        areas = []
        #
        if layerNumber in [35, 36]:
            dodajObiekt = False
            if layerNumber == 35:  # top
                dodajObiekt = True
                lista = ['P', 'L', 'H']
            elif layerNumber == 36:  # bottom
                dodajObiekt = True
                lista = ['M', 'L', 'H']
                
            if dodajObiekt:
                pcb = re.findall(r'\.PLACE_OUTLINE .*?\n(.*)\.END_PLACE_OUTLINE\n', self.projektBRD, re.DOTALL)
                for k in pcb:
                    k += ".END_PLACE_OUTLINE"
                    pcb2 = re.findall(r'([TOP|BOTTOM|BOTH|ALL])\s+(.*?)\n(.*?)\n[TOP|BOTTOM|BOTH|\.END_PLACE_OUTLINE|ALL|INNER]', k, re.DOTALL)
                    for i in pcb2:
                        if i[0] in lista:
                            areas.append(['polygon', self.pobierzLinie(i[2].strip().split('\n'))[0], float(i[1]) * self.mnoznik])
        elif layerNumber in [37, 38]:
            dodajObiekt = False
            if layerNumber == 37:  # top
                dodajObiekt = True
                lista = ['P', 'L', 'H']
            elif layerNumber == 38:  # bottom
                dodajObiekt = True
                lista = ['M', 'L', 'H']
                
            if dodajObiekt:
                pcb = re.findall(r'\.ROUTE_OUTLINE\s+.*?\n(.*)\.END_ROUTE_OUTLINE\n', self.projektBRD, re.DOTALL)
                for k in pcb:
                    k += ".END_ROUTE_OUTLINE"
                    pcb2 = re.findall(r'([TOP|BOTTOM|BOTH|ALL])\n(.*?)\n[TOP|BOTTOM|BOTH|\.END_ROUTE_OUTLINE|ALL|INNER]', k, re.DOTALL)
                    for i in pcb2:
                        if i[0] in lista:
                            areas.append(['polygon', self.pobierzLinie(i[1].strip().split('\n'))[0]])
        elif layerNumber in [39, 40]:
            dodajObiekt = False
            if layerNumber == 39:  # top
                dodajObiekt = True
                lista = ['P', 'H']
            elif layerNumber == 40:  # bottom
                dodajObiekt = True
                lista = ['M', 'H']
            
            if dodajObiekt:
                pcb = re.findall(r'\.PLACE_KEEPOUT\s+.*?\n(.*?)[\.END_PLACE_KEEPOUT]\n', self.projektBRD, re.DOTALL)
                for k in pcb:
                    pcb2 = re.findall(r'([TOP|BOTTOM|BOTH])\s+(.*?)\n(.*?)\n[TOP|BOTTOM|BOTH|\.END_PLACE_KEEPOUT]', k, re.DOTALL)
                    for i in pcb2:
                        if i[0] in lista:
                            areas.append(['polygon', self.pobierzLinie(i[2].strip().split('\n'))[0], float(i[1]) * self.mnoznik])
        elif layerNumber in [41, 42]:
            dodajObiekt = False
            if layerNumber == 41:  # top
                dodajObiekt = True
                lista = ['P', 'L', 'H']
            elif layerNumber == 42:  # bottom
                dodajObiekt = True
                lista = ['M', 'L', 'H']
                
            if dodajObiekt:
                pcb = re.findall(r'\.ROUTE_KEEPOUT\s+.*?\n(.*?)[\.END_ROUTE_KEEPOUT]\n', self.projektBRD, re.DOTALL)
                for k in pcb:
                    pcb2 = re.findall(r'([TOP|BOTTOM|BOTH|ALL])\n(.*?)\n[TOP|BOTTOM|BOTH|\.END_ROUTE_KEEPOU|ALL|INNER]', k, re.DOTALL)
                    for i in pcb2:
                        if i[0] in lista:
                            areas.append(['polygon', self.pobierzLinie(i[1].strip().split('\n'))[0]])
        #
        return areas
    
    def getAnnotations(self):
        adnotacje = []
        #
        try:
            elem = re.search(r'\.NOTES(.*?)\.END_NOTES', self.projektBRD, re.DOTALL).groups()[0]
            elem = elem.strip().split('\n')
            for i in elem:
                dane = re.search(r'([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+([0-9\.\-]+)\s+"(.*?)"', i, re.DOTALL).groups()

                x = float(dane[0]) * self.mnoznik
                y = float(dane[1]) * self.mnoznik
                size = float(dane[2]) * self.mnoznik
                txt = str(dane[4])
                side = 'TOP'
                rot = 0
                align = "bottom-left"
                spin = True
                mirror = 0
                font = 'proportional'
                
                adnotacje.append([txt, x, y, size, rot, side, align, spin, mirror, font])
        except:
            pass
        #
        return adnotacje
    
    def getHoles(self, types):
        ''' holes/vias '''
        holes = []
        #
        try:
            elem = re.search(r'\.DRILLED_HOLES(.*?)\.END_DRILLED_HOLES', self.projektBRD, re.DOTALL).groups()[0]
            elem = elem.strip().split('\n')
            for i in elem:
                dane = ' '.join(i.split()).split(" ")
                
                drill = float(dane[0]) * self.mnoznik / 2.
                x = float(dane[1]) * self.mnoznik
                y = float(dane[2]) * self.mnoznik
                
                if dane[5] == 'VIA' and types['V'] or dane[5] == 'PIN' and types['P'] or not dane[5] in ['VIA', 'PIN'] and types['H']:
                    holes.append([x, y, drill])
        except:
            pass
        ####
        return holes

    def setProject(self, filename):
        self.projektBRD = builtins.open(filename, "r").read().replace("\r\n", "\n").replace("\r", "\n")
        self.mnoznik = getUnitsDefinition(self.projektBRD)

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
            partsError = self.getParts(self.dialogMAIN.plytkaPCB_elementyKolory.isChecked(), self.dialogMAIN.adjustParts.isChecked(), self.dialogMAIN.plytkaPCB_grupujElementy.isChecked(), self.dialogMAIN.partMinX.value(), self.dialogMAIN.partMinY.value(), self.dialogMAIN.partMinZ.value(), self.dialogMAIN.packageByDecal.isChecked())
            if self.dialogMAIN.plytkaPCB_plikER.isChecked():
                self.generateErrorReport(partsError, filename)
        ##  dodatkowe warstwy
        grp = createGroup_Areas()
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
                
                if ID == 0:  # annotations
                    self.addAnnotations(self.getAnnotations(), doc, color)
                else:
                    self.generateConstraintAreas(self.getConstraintAreas(ID), doc, ID, grp, name, color, transp)
        ##
        return doc
