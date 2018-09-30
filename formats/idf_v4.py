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
    # globalna jednostka dla projektu
    if re.findall(r'Default_Units \("(.*?)"\)', projektBRD)[0] == 'Inch':
        return 2.54
    else:
        return 1


class dialogMAIN(dialogMAIN_FORM):
    def __init__(self, filename=None, parent=None):
        dialogMAIN_FORM.__init__(self, parent)
        self.databaseType = "idf_v4"
        #
        self.plytkaPCB_grupujElementy.setChecked(False)
        self.plytkaPCB_grupujElementy.setDisabled(True)
        
        self.plytkaPCB_elementy.setChecked(False)
        self.plytkaPCB_elementy.setDisabled(True)
        
        self.plytkaPCB_elementyKolory.setChecked(False)
        self.plytkaPCB_elementyKolory.setDisabled(True)
        
        self.plytkaPCB_plikER.setChecked(False)
        self.plytkaPCB_plikER.setDisabled(True)
        
        self.adjustParts.setChecked(False)
        self.adjustParts.setDisabled(True)
        
        self.partMinX.setDisabled(True)
        self.partMinY.setDisabled(True)
        self.partMinZ.setDisabled(True)
        ###
        self.projektBRD = builtins.open(filename, "r").read().replace('\r', '')
        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetBool("boardImportThickness", True):
            self.gruboscPlytki.setValue(self.getBoardThickness())
        ###
        self.generateLayers()
        self.spisWarstw.sortItems(1)
    
    def getBoardThickness(self):
        Top_Height = float(re.findall(r'Top_Height \((.+?)\),', self.projektBRD)[0])
        Bot_Height = float(re.findall(r'Bot_Height \((.+?)\),', self.projektBRD)[0])
        
        return (Top_Height + Bot_Height) * getUnitsDefinition(self.projektBRD)


class IDFv4_PCB(mainPCB):
    def __init__(self, filename):
        mainPCB.__init__(self, None)
        
        self.dialogMAIN = dialogMAIN(filename)
        self.projectSections = []
        self.globalMnoznik = 1
        self.PCBmnoznik = 1
        self.databaseType = "idf_v4"
    
    def getEntityByID(self, ID):
        return re.findall(r'Entity_ID \({0}\),(.*?)\);'.format(ID), self.projektBRD, re.DOTALL)[0].strip()
        
    def getEntityParam(self, entity, param):
        return re.findall(r'{0} \((.*?)\)'.format(param), entity, re.DOTALL)[0].strip()
    
    def getHoles(self, types):
        ''' holes/vias '''
        holes = []
        # holes/via
        if 'Hole' in self.projectSections:
            for i in re.findall(r'Hole \(.*?Type \("(.*?)"\).*?Shape_Type \("(.*?)"\).*?Outline \((.*?)\).*?XY_Loc \((.*?),(.*?)\).*?Rotation \((.*?)\)', self.projektBRD, re.DOTALL):
                if not i[0].startswith('Blind') and not i[0].startswith('Buried'):
                    hType = i[0]
                    hShape = i[1]  # key, slot, round, square
                    outlineID = i[2]
                    x = float(i[3]) * self.PCBmnoznik
                    y = float(i[4]) * self.PCBmnoznik
                    rot = float(i[5])
                    
                    if hShape == 'Round':
                        
                        if hType == 'Thru_Via' and types['V'] or hType == 'Thru_Pin' and types['P'] or not hType in ['Thru_Via', 'Thru_Pin'] and types['H']:
                            r = float(self.getEntityParam(self.getEntityByID(outlineID), 'Radius')) * self.PCBmnoznik
                            holes.append([x, y, r])
                    elif hShape == 'Key':  # example needed
                        pass
                    elif hShape == 'Square':  # example needed
                        pass
                    elif hShape == 'Slot':  # example needed
                        pass
        # pin
        if 'Pad' in self.projectSections:
            pass
        ####
        return holes
    
    def getPCB(self):
        PCB = []
        wygenerujPada = True
        #
        for i in re.findall(r'Shape \(.*?Vertices \(\n(.*?)\n\)', self.projektBRD, re.DOTALL):
            dane = i.split("\n")
            for j in range(1, len(dane)):
                param = dane[j].split(",")
                x1 = float(param[0]) * self.PCBmnoznik
                y1 = float(param[1]) * self.PCBmnoznik
                lType = float(param[2])
                
                param_2 = dane[j - 1].split(",")
                x2 = float(param_2[0]) * self.PCBmnoznik
                y2 = float(param_2[1]) * self.PCBmnoznik
                
                if lType == 0:
                    PCB.append(['Line', x1, y1, x2, y2])
                elif lType == 360:
                    xs = x2
                    ys = y2
                    radius = sqrt((xs - x1) ** 2 + (ys - y1) ** 2)
                    
                    PCB.append(['Circle', xs, ys, radius])
                else:  # arc
                    #[xc, yc, r, startAngle, stopAngle] = self.arcWyznaczSrodek([i[j][0], i[j][1]], [i[j][2], i[j][3]], i[j][4])
                    #doc.Sketch_PCB.addGeometry(Part.ArcOfCircle(Part.Circle(FreeCAD.Vector(xc, yc, 0), FreeCAD.Vector(0, 0, 1), r), startAngle, stopAngle))
                    
                    PCB.append(['Line', x1, y1, x2, y2])
        #
        return [PCB, wygenerujPada]
   
    def setProject(self, filename):
        self.projektBRD = builtins.open(filename, "r").read().replace("\r\n", "\n").replace("\r", "\n")
        
        # globalna jednostka dla projektu
        self.globalMnoznik = getUnitsDefinition(self.projektBRD)
            
        # jednostka w jakiej zapisana jest plytka pcb
        pcbUnit = re.findall(r'Board_Part \(\nEntity_ID.*?Units \("(.*?)"\),', self.projektBRD, re.DOTALL)[0]
        if pcbUnit == 'Global':
            self.PCBmnoznik = self.globalMnoznik
        elif pcbUnit == 'Inch':
            self.PCBmnoznik = 2.54
        else:
            self.PCBmnoznik = 1
        
        # wszystkie sekcje wystepujace w projekcie
        self.projectSections = re.findall(r'"(.*?)"', re.search(r'Board_Part \((.*?)\),', self.projektBRD, re.DOTALL).groups()[0])

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
        ##
        return doc
