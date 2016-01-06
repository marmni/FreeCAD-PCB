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
import FreeCADGui
import re
from math import radians
#
from PCBconf import supSoftware, PCBlayers, softLayers
from PCBobjects import *
from formats.PCBmainForms import *


class dialogMAIN(dialogMAIN_FORM):
    def __init__(self, filename=None, parent=None):
        dialogMAIN_FORM.__init__(self, parent)
        self.databaseType = "diptrace"
        #
        self.projektBRD = __builtin__.open(filename, "r").read().replace('\n', ' ')
        self.layersNames = {}
        
        self.plytkaPCB_elementy.setVisible(False)
        self.plytkaPCB_elementyKolory.setVisible(False)
        self.plytkaPCB_plikER.setVisible(False)
        
        self.spisWarstw.sortItems(1)


class DipTrace_PCB(mainPCB):
    def __init__(self, filename):
        mainPCB.__init__(self, None)
        
        self.dialogMAIN = dialogMAIN(filename)
        self.databaseType = "diptrace"
        self.mnoznik = 1. / 3.
        

    def setProject(self, filename):
        self.projektBRD = __builtin__.open(filename, "r").read().replace('\r\n', '\n').replace('\r', '\n').replace('\\n', '\n')
    
        #unit = re.search(r'\(Units "(.*?)"\)', self.projektBRD).groups()[0]
        #if unit == 'in':
            #self.mnoznik = 0.0254 / 100.
        #elif unit == 'mil':
            #self.mnoznik = 0.0254
        #else:  # mm
            #self.mnoznik = 1
        
    def generate(self, doc, groupBRD, filename):
        self.generatePCB(self.getPCB(), doc, groupBRD, self.dialogMAIN.gruboscPlytki.value())
        # holes/vias/pads
        types = {'H':self.dialogMAIN.plytkaPCB_otworyH.isChecked(), 'V':self.dialogMAIN.plytkaPCB_otworyV.isChecked(), 'P':self.dialogMAIN.plytkaPCB_otworyP.isChecked()}
        self.generateHoles(self.getHoles(types), doc, self.dialogMAIN.holesMin.value(), self.dialogMAIN.holesMax.value())
        #
    
    def getPCB(self):
        PCB = []
        wygenerujPada = True
        ###
        pcb = re.search(r'\(Points\s+(.+?)\s+\)', self.projektBRD, re.MULTILINE|re.DOTALL).groups()[0]
        pcb = re.findall(r'\(pt (.+?) (.+?) "(.+?)"\)', pcb, re.MULTILINE|re.DOTALL)
        PCB_PCB = self.pobierzLinie(pcb)
        ###
        return [PCB_PCB, wygenerujPada]
    
    def getArcParameters(self, x1, y1, x2, y2, x3, y3):
        [xs, ys] = self.arcCenter(x1, y1, x2, y2, x3, y3)
        angle = self.arcGetAngle([xs, ys], [x1, y1], [x3, y3])
        
        return angle
    
    def getHoles(self, types):
        ''' holes/vias '''
        holes = []
        ####
        data = re.search(r'  \(Components\n(.+?)\n  \)\n', self.projektBRD, re.MULTILINE|re.DOTALL).groups(0)
        
        # holes
        if types['H']:
            data = re.findall(r'[ ]{4}\(Component "Hole" .+?\n(.+?)\n[ ]{4}\)\n', self.projektBRD, re.MULTILINE|re.DOTALL)
            for i in data:
                x = float(re.search(r'\(X (.+?)\)', i).groups(0)[0]) * self.mnoznik
                y = float(re.search(r'\(Y (.+?)\)', i).groups(0)[0]) * -1 * self.mnoznik
                r = float(re.search(r'\(Hole "Y" "N" .+? .+? .+? (.+?)\)', i).groups(0)[0]) / 2. * self.mnoznik
                
                if r > 0:
                    holes.append([x, y, r])
        # vias
        if types['V']:
            data = re.findall(r'[ ]{4}\(Component ".+?" .+?\n(.+?)\n[ ]{4}\)\n', self.projektBRD, re.MULTILINE|re.DOTALL)
            for i in data:
                if re.search(r'\(SurfacePad "(.+?)"\)', i).groups(0)[0] == 'N' and re.search(r'\(Pattern "(|.+?)"\)', i).groups(0)[0] == "":
                    x = float(re.search(r'\(X (.+?)\)', i).groups(0)[0]) * self.mnoznik
                    y = float(re.search(r'\(Y (.+?)\)', i).groups(0)[0]) * -1 * self.mnoznik
                    r = float(re.search(r'\(PadHole (.+?)\)', i).groups(0)[0]) / 2. * self.mnoznik
                    
                    if r > 0:
                        holes.append([x, y, r])
                    else:
                        r = re.search(r'\(ViaStyle (.+?)\)', i).groups(0)[0]
                        r = float(re.findall(r'\(ViaStyle ".+?" ".+?" .+? (.+?) .+? .+?\)', self.projektBRD)[int(r)]) / 2.  * self.mnoznik
                        
                        if r > 0:
                            holes.append([x, y, r])
        ####
        return holes
        
    def pobierzLinie(self, pcb):
        PCB_PCB = []
        #
        for i in range(len(pcb)):
            if i + 1 < len(pcb) and pcb[i + 1][2] == 'Y':
                continue
            
            if i + 1 < len(pcb) and pcb[i][2] == 'Y':  # arc
                x1 = float(pcb[i - 1][0]) * self.mnoznik
                y1 = float(pcb[i - 1][1]) * -1 * self.mnoznik
                
                x2 = float(pcb[i][0]) * self.mnoznik
                y2 = float(pcb[i][1]) * -1 * self.mnoznik
                
                if i + 1 >= len(pcb):
                    x3 = float(pcb[0][0]) * self.mnoznik
                    y3 = float(pcb[0][1]) * -1 * self.mnoznik
                else:
                    x3 = float(pcb[i + 1][0]) * self.mnoznik
                    y3 = float(pcb[i + 1][1]) * -1 * self.mnoznik
                    
                angle = self.getArcParameters(x1, y1, x2, y2, x3, y3)
                
                PCB_PCB.append(['Arc', x3, y3, x1, y1, angle])
            else:
                x1 = float(pcb[i][0]) * self.mnoznik
                y1 = float(pcb[i][1]) * -1 * self.mnoznik
                eType = pcb[i][2]
                
                if i + 1 >= len(pcb):
                    x2 = float(pcb[0][0]) * self.mnoznik
                    y2 = float(pcb[0][1]) * -1 * self.mnoznik
                else:
                    x2 = float(pcb[i + 1][0]) * self.mnoznik
                    y2 = float(pcb[i + 1][1]) * -1 * self.mnoznik

                PCB_PCB.append(['Line', x1, y1, x2, y2])
        #
        return PCB_PCB
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
