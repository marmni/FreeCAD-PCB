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
from math import radians
import __future__

from PCBconf import PCBlayers, softLayers
from PCBobjects import *
from formats.PCBmainForms import *
from command.PCBgroups import *


class dialogMAIN(dialogMAIN_FORM):
    def __init__(self, filename=None, parent=None):
        dialogMAIN_FORM.__init__(self, parent)
        self.databaseType = "hyp"
        #
        self.projektBRD = builtins.open(filename, "r").read().replace('\r', '')
        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetBool("boardImportThickness", True):
            self.gruboscPlytki.setValue(self.getBoardThickness())
        ##
        self.generateLayers()
        self.spisWarstw.sortItems(1)
    
    def getBoardThickness(self):
        layers = re.search(r'\{STACKUP\s+(.+?)\s+\}', self.projektBRD, re.MULTILINE|re.DOTALL).groups()[0]
        thickness = sum([float(i) for i  in re.findall(r'T=(.+?) ', layers)])

        return float("%.5f" % (thickness * 25.4))


class HYP_PCB(mainPCB):
    '''Board importer for gEDA software'''
    def __init__(self, filename):
        mainPCB.__init__(self, None)
        
        self.dialogMAIN = dialogMAIN(filename)
        self.databaseType = "hyp"
        self.layers = []
        
    def setUnit(self, value):
        '''Get unit from transferred value and convert to millimeters - if necessary'''
        return float("%.5f" % (float(value) * 25.4))

    def setProject(self, filename):
        '''Load project from file'''
        self.projektBRD = builtins.open(filename, "r").read().replace('\r\n', '\n')
        self.layers = re.findall(r'\(SIGNAL T=.+? P=.+? L=(.+?)\)', self.projektBRD)

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
        #  dodatkowe warstwy
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
                
                if ID in [1, 16]:  # paths
                    self.generatePaths(self.getPaths(ID), doc, grp, name, color, ID, transp)
                elif ID in [17, 18]:  # pady
                    self.getPads(doc, ID, grp, name, color, transp)
                
        return doc
    
    def getPaths(self, layerNumber):
        wires = []
        signal = []
        
        if layerNumber == 1:
            layer = self.layers[0]
        else:
            layer = self.layers[-1]
        
        # lines
        for i in re.findall(r'\(SEG X1=(.+?) Y1=(.+?) X2=(.+?) Y2=(.+?) W=(.+?) L=%s\)' % layer, self.projektBRD):
            x1 = self.setUnit(i[0])
            y1 = self.setUnit(i[1])
            x2 = self.setUnit(i[2])
            y2 = self.setUnit(i[3])
            width = self.setUnit(i[4])
            
            if [x1, y1] != [x2, y2]:
                wires.append(['line', x1, y1, x2, y2, width])
        # arcs
        for i in re.findall(r'\(ARC X1=(.+?) Y1=(.+?) X2=(.+?) Y2=(.+?) XC=(.+?) YC=(.+?) R=.+? W=(.+?) L=%s\)[^ Circle]' % layer, self.projektBRD):
            x1 = self.setUnit(i[0])
            y1 = self.setUnit(i[1])
            
            x2 = self.setUnit(i[2])
            y2 = self.setUnit(i[3])
            
            xs = self.setUnit(i[4])
            ys = self.setUnit(i[5])
            
            width = self.setUnit(i[6])
            
            angle = self.getArcParameters(x1, y1, x2, y2, xs, ys)
            
            wires.append(['arc', x1, y1, x2, y2, angle, width, 'round'])
        #
        wires.append(signal)
        return wires
    
    def getArcParameters(self, x1, y1, x2, y2, xs, ys):
        angle = degrees(atan2(y2 - ys, x2 - xs) - atan2(y1 - ys, x1 - xs))
        if angle < 0:
            angle = angle + 360
        
        return angle
    
    def getParts(self, koloroweElemnty, adjustParts, groupParts, partMinX, partMinY, partMinZ):
        PCB_ER = []
        #
        for i in re.findall(r'\(.+? REF=(|.+?) .+?=(|.+?) L=(.+?)(| PKG=.+?)\)  R(.+?) X=(.+?) Y=(.+?) :  Lib: (.+?) : (.+?) ', self.projektBRD):
            x = self.setUnit(i[5])
            y = self.setUnit(i[6])
            rot = float(i[4])
            
            if i[2] == self.layers[0]:
                side = 'TOP'
            else:
                side = 'BOTTOM'
                
            name = i[0]
            package = i[8]
            library = i[7]
            value = i[1]
            
            EL_Name = [name, x, y + 1, 1.27, rot, side, "bottom-left", False, 'None', '', True]
            EL_Value = [value, x, y - 1, 1.27, rot, side, "bottom-left", False, 'None', '', True]
            #
            newPart = [[name, package, value, x, y, rot, side, library], EL_Name, EL_Value]
            wyn = self.addPart(newPart, koloroweElemnty, adjustParts, groupParts, partMinX, partMinY, partMinZ)
            #
            if wyn[0] == 'Error':  # lista brakujacych elementow
                partNameTXT = partNameTXT_label = self.generateNewLabel(name)
                if isinstance(partNameTXT, str):
                    partNameTXT = unicodedata.normalize('NFKD', partNameTXT).encode('ascii', 'ignore')
                
                PCB_ER.append([partNameTXT, package, value, library])
        ####
        return PCB_ER
    
    def getPads(self, doc, layerNumber, grp, layerName, layerColor, defHeight):
        layerName = "{0}_{1}".format(layerName, layerNumber)
        layerType = PCBlayers[softLayers[self.databaseType][layerNumber][1]][3]
        ####
        layerS = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", layerName)
        layerNew = layerSilkObject(layerS, layerType)
        layerNew.holes = self.showHoles()
        layerNew.defHeight = defHeight
        
        if layerNumber == 17:
            newLayer = '1'
        elif layerNumber == 18:
            newLayer = '16'
        # vias
        for i in re.findall(r'\(VIA X=(.+?) Y=(.+?) P=(.+?)\) .+?', self.projektBRD):
            x = self.setUnit(i[0])
            y = self.setUnit(i[1])
            padData = re.findall(r'PADSTACK={0},(.+?)\s+(\((.+?)\) .+?\s+|)'.format(i[2]), self.projektBRD)[0]
            
            if padData[2]:
                #r = setUnit(padData[0]) / 2.
                padParameters = padData[2].split(',')
                padType = int(padParameters[1])  # 0:round, 1:square, 2:oblong
                outDiameter = self.setUnit(padParameters[2]) / 2.
                rot = float(padParameters[4])
                
                if padType == 1:  # square
                    a = outDiameter
                    x1 = x - a
                    y1 = y - a
                    x2 = x + a
                    y2 = y + a
                    
                    layerNew.createObject()
                    layerNew.addRectangle(x1, y1, x2, y2)
                    layerNew.addRotation(x, y, rot)
                    layerNew.setFace()
                elif padType == 2:  # oblong
                    e = self.setUnit(padParameters[2])
                    
                    layerNew.createObject()
                    layerNew.addPadLong(x, y, e, e / 2., 100)
                    layerNew.addRotation(x, y, rot)
                    layerNew.setFace()
                else:  # round
                    layerNew.createObject()
                    layerNew.addCircle(x, y, outDiameter)
                    layerNew.addRotation(x, y, rot)
                    layerNew.setFace()
        # pads
        for i in re.findall(r'\(PIN X=(.+?) Y=(.+?) R=.+? P=(.+?)\)(| .+?,) Pad Diameter: (.+?)  Drill: (.+?)\n', self.projektBRD):
            x = self.setUnit(i[0])
            y = self.setUnit(i[1])
            outDiameter = self.setUnit(i[4]) / 2.
            #r = self.setUnit(i[5]) / 2.
            padData = re.findall(r'PADSTACK={0},(.+?)\s+(\((.+?)\) .+?\s+|)'.format(i[2]), self.projektBRD)[0]
            
            padParameters = padData[2].split(',')
            padType = int(padParameters[1])  # 0:round, 1:square, 2:oblong
            rot = float(padParameters[4])
            
            if padType == 1:  # square
                a = outDiameter
                x1 = x - a
                y1 = y - a
                x2 = x + a
                y2 = y + a
                
                layerNew.createObject()
                layerNew.addRectangle(x1, y1, x2, y2)
                layerNew.addRotation(x, y, rot)
                layerNew.setFace()
                #layerNew.addObject(obj)
            elif padType == 2:  # oblong
                e = self.setUnit(padParameters[2])
                
                layerNew.createObject()
                layerNew.addPadLong(x, y, e, e / 2., 100)
                layerNew.addRotation(x, y, rot)
                layerNew.setFace()
            else:  # round
                layerNew.createObject()
                layerNew.addCircle(x, y, outDiameter)
                layerNew.addRotation(x, y, rot)
                layerNew.setFace()
        # smd
        for i in re.findall(r'\(PIN X=(.+?) Y=(.+?) R=(.+?) P=(.+?)\)(| .+?,) Smd Dx: (.+?)  Dy: (.+?)\n', self.projektBRD):
            [layer, padType, rot] = re.findall(r'\{PADSTACK=%s\s+\((.+?),(.+?),.+?,.+?,(.+?)\)' % i[3], self.projektBRD, re.MULTILINE|re.DOTALL)[0]

            if layer == newLayer:
                xs = self.setUnit(i[0])
                ys = self.setUnit(i[1])
                
                dx = self.setUnit(i[5])
                dy = self.setUnit(i[6])
                
                if padType in ['0', '2']:
                    if padType == '2':
                        roundness = 50
                    else:
                        roundness = 100
                    
                    layerNew.createObject()
                    layerNew.addPadLong(xs, ys, dx / 2., dy / 2., roundness)
                    layerNew.addRotation(xs, ys, float(rot))
                    layerNew.setFace()
                else:  # roundness = 0
                    x1 = xs - dx / 2.
                    y1 = ys - dy / 2.
                    x2 = xs + dx / 2.
                    y2 = ys + dy / 2.
                    
                    layerNew.createObject()
                    layerNew.addRectangle(x1, y1, x2, y2)
                    layerNew.addRotation(xs, ys, float(rot))
                    layerNew.setFace()
                    #layerNew.addObject(obj)
        ###
        layerNew.generuj(layerS)
        layerNew.updatePosition_Z(layerS)
        viewProviderLayerSilkObject(layerS.ViewObject)
        layerS.ViewObject.ShapeColor = layerColor
        grp.addObject(layerS)
        #
        doc.recompute()
    
    def getHoles(self, types):
        ''' holes/vias '''
        holes = []
        # holes
        if types['H']:
            for i in re.findall(r'\(PERIMETER_ARC X1=.+? Y1=.+? X2=.+? Y2=.+? XC=(.+?) YC=(.+?) R=(.+?)\) Holes', self.projektBRD):
                x = self.setUnit(i[0])
                y = self.setUnit(i[1])
                r = self.setUnit(i[2])
                
                holes.append([x, y, r])
        # vias
        if types['V']:
            for i in re.findall(r'\(VIA X=(.+?) Y=(.+?) P=(.+?)\) .+?', self.projektBRD):
                x = self.setUnit(i[0])
                y = self.setUnit(i[1])
                r = self.setUnit(re.search(r'PADSTACK={0},(.+?)\n'.format(i[2]), self.projektBRD).groups()[0]) / 2.
                
                holes.append([x, y, r])
        # pads
        if types['P']:  # pads
            for i in re.findall(r'\(PIN X=(.+?) Y=(.+?) R=.+? P=.+?\)(| .+?,) Pad Diameter: .+?  Drill: (.+?)\n', self.projektBRD):
                x = self.setUnit(i[0])
                y = self.setUnit(i[1])
                r = self.setUnit(i[3]) / 2.
                
                holes.append([x, y, r])
        #
        return holes
    
    def getPCB(self):
        PCB = []
        wygenerujPada = True
        
        board = re.search(r'\{BOARD\s+(.+?)\s+\}', self.projektBRD, re.MULTILINE|re.DOTALL).groups()[0]
        #
        wires = re.findall(r'\(PERIMETER_SEGMENT X1=(.+?) Y1=(.+?) X2=(.+?) Y2=(.+?)\) Wires: From Board', board)
        for i in wires:
            x1 = self.setUnit(i[0])
            y1 = self.setUnit(i[1])
            x2 = self.setUnit(i[2])
            y2 = self.setUnit(i[3])
            
            PCB.append(['Line', x1, y1, x2, y2])
        
        circles = re.findall(r'\(PERIMETER_ARC X1=.+? Y1=.+? X2=.+? Y2=.+? XC=(.+?) YC=(.+?) R=(.+?)\) Circles: Board Outline .*', board)
        for i in circles:
            x = self.setUnit(i[0])
            y = self.setUnit(i[1])
            r = self.setUnit(i[2])
            
            PCB.append(['Circle', x, y, r])
            
        arcs = re.findall(r'\(PERIMETER_ARC X1=(.+?) Y1=(.+?) X2=(.+?) Y2=(.+?) XC=(.+?) YC=(.+?) R=.+?\) Arcs: Board Outline .*', board)
        for i in arcs:
            x1 = self.setUnit(i[0])
            y1 = self.setUnit(i[1])
            
            x2 = self.setUnit(i[2])
            y2 = self.setUnit(i[3])
            
            xs = self.setUnit(i[4])
            ys = self.setUnit(i[5])
            
            angle = self.getArcParameters(x1, y1, x2, y2, xs, ys)

            PCB.append(['Arc', x2, y2, x1, y1, angle])
        #
        return [PCB, wygenerujPada]
