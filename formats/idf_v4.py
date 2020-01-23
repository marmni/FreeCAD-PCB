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
import builtins
import re

from PCBobjects import *
from formats.PCBmainForms import *
from command.PCBgroups import *
from formats.dialogMAIN_FORM import dialogMAIN_FORM
from PCBconf import softLayers



def parseString(filename, char=['(', ')'], loadFromFile=True):
    if loadFromFile:
        projektBRD = builtins.open(filename, "r").read()[1:]
    else:
        projektBRD = filename
    #
    licznik = 0
    wynik = ""
    txt = ""
    txt_1 = 0
    start = 0

    for i in projektBRD:
        if i in ['"', "'"] and txt_1 == 0:
            txt_1 = 1
        elif i in ['"', "'"] and txt_1 == 1:
            txt_1 = 0
        
        if txt_1 == 0 and licznik == 0:
            if i == char[0]:
                wynik += '[start]'
        
        if txt_1 == 0:
            if i == char[0]:
                licznik += 1
            elif i == char[1]:
                licznik -= 1
        #
        wynik += i
        #
        if txt_1 == 0 and licznik == 0:
            if i == char[1]:
                wynik += '[stop]'
    
    return wynik


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
        ###
        self.projektBRD = builtins.open(filename, "r").read().replace('\r', '')
        self.layersNames = self.getLayersNames()
        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetBool("boardImportThickness", True):
            self.gruboscPlytki.setValue(self.getBoardThickness())
        ###
        self.generateLayers([])
        self.spisWarstw.sortItems(1)
    
    def getBoardThickness(self):
        Top_Height = float(re.findall(r'Top_Height \((.+?)\),', self.projektBRD)[0])
        Bot_Height = float(re.findall(r'Bot_Height \((.+?)\),', self.projektBRD)[0])
        
        return (Top_Height + Bot_Height) * getUnitsDefinition(self.projektBRD)
        
    def getLayersNames(self):
        dane = {}
        # extra layers
        
        #
        return dane


class IDFv4_PCB(mathFunctions):
    def __init__(self, filename, parent):
        self.fileName = filename
        self.dialogMAIN = dialogMAIN(self.fileName)
        self.databaseType = "idf_v4"
        self.parent = parent
        self.mnoznik = 1
        self.projectSections = []
    
    def setProject(self):
        self.projektBRD = builtins.open(self.fileName, "r").read().replace("\r\n", "\n").replace("\r", "\n")
        
        # globalna jednostka dla projektu
        self.globalMnoznik = getUnitsDefinition(self.projektBRD)
            
        # jednostka w jakiej zapisana jest plytka pcb
        pcbUnit = re.findall(r'Board_Part \(\nEntity_ID.*?Units \("(.*?)"\),', self.projektBRD, re.DOTALL)[0]
        if pcbUnit == 'Global':
            self.PCBmnoznik = self.globalMnoznik
        elif pcbUnit == 'Inch':
            self.mnoznik = 2.54
        else:
            self.mnoznik = 1
        
        # wszystkie sekcje wystepujace w projekcie
        self.projectSections = re.findall(r'"(.*?)"', re.search(r'Board_Part \((.*?)\),', self.projektBRD, re.DOTALL).groups()[0])

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
    
    def getPCB(self, borderObject):
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
