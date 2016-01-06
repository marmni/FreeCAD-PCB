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
import __builtin__
import re
from math import radians

from PCBconf import PCBlayers, softLayers
from PCBobjects import *
from formats.PCBmainForms import *
from command.PCBgroups import *


class dialogMAIN(dialogMAIN_FORM):
    def __init__(self, filename=None, parent=None):
        dialogMAIN_FORM.__init__(self, parent)
        self.databaseType = "geda"
        
        self.projektBRD = __builtin__.open(filename, "r").read().replace('\n', ' ')
        self.layersNames = {}
        self.getLayersNames()
        #        
        self.plytkaPCB_grupujElementy.setChecked(False)
        self.plytkaPCB_grupujElementy.setDisabled(True)
        
        self.plytkaPCB_otworyH.setChecked(False)
        self.plytkaPCB_otworyH.setDisabled(True)
        
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
        self.generateLayers()
        self.spisWarstw.sortItems(1)
        
    def getLayersNames(self):
        for i in re.findall("Layer\((.+?) \"(.+?)\"\)", self.projektBRD):
            self.layersNames[int(i[0])] = i[1]


class gEDA_PCB(mainPCB):
    '''Board importer for gEDA software'''
    def __init__(self, filename):
        mainPCB.__init__(self, None)
        
        self.groups = {}  # layers groups
        
        self.dialogMAIN = dialogMAIN(filename)
        self.databaseType = "geda"
        
    def setUnit(self, value):
        '''Get unit from transferred value and convert to millimeters - if necessary
           Possible value units:
            -   millimeters -> 1.0mm
            -   mils        -> 1.0mil
            -   inches      -> 1.0'''
        data = re.search(r'(.[^a-z]*)(.*)', value).groups()
        
        if data[1] == 'mm':
            multiplier = 1.0
        elif data[1] == 'mil':
            multiplier = 0.0254
        else:
            if self.globalUnit:
                multiplier = 0.0254
            else:
                multiplier = 0.0254 / 100.
            
        #return float(data[0]) * multiplier
        return float("%.3f" % (float(data[0]) * multiplier))

    def setProject(self, filename):
        '''Load project from file'''
        self.projektBRD = __builtin__.open(filename, "r").read().replace('\r\n', '\n')
        ##############
        try:
            re.search('PCB\s*\(.+? (.+?) (.+?)\)', self.projektBRD).groups()
            self.globalUnit = True  # mils
        except:
            self.globalUnit = False
        ##############
        # layers groups
        # c: top
        # s: bottom
        data = re.search('Groups\("(.*?)"\)', self.projektBRD).groups()[0]
        self.groups = {
            'top': re.search('([0-9,]*?),c', data).groups()[0].split(','),
            'bottom': re.search('([0-9,]*?),s', data).groups()[0].split(',')
            }
        ##############
        self.projektBRD = re.sub(r'(.*)\((.*)\)', r'\1[\2]', self.projektBRD)
    
    def getAnnotations(self):
        annotations = []
        #
        for i in re.findall(r'Text\s*\[(.+?) (.+?) ([0-9]+) ([0-9]+) "(.+?)" (.+?)\]', self.projektBRD):
            x = self.setUnit(i[0])
            y = 0 - self.setUnit(i[1])
            #txt = str(i[4])[1:-1]
            txt = str(i[4])
            align = 'top-left'
            size = (float(i[3]) * 40 * 0.0254) / 100
            spin = False
            mirror = 0
            font = 'proportional'
            side = 'TOP'
            
            if int(i[2]) == 0:
                rot = 0
            elif int(i[2]) == 1:
                rot = 90
            elif int(i[2]) == 2:
                rot = 180
            else:
                rot = 270

            annotations.append([txt, x, y, size, rot, side, align, spin, mirror, font])
        #
        return annotations
    
    def getHoles(self, types):
        holes = []
        # vias
        if types['V']:
            for i in self.getAllVias():
                (x, y, drill, r) = self.getViaParameters(i)
                
                holes.append([x, y, drill])
        ### pads
        if types['P']:  # pads
            for elem in self.getAllParts():
                X1 = self.setUnit(elem[4])
                Y1 = self.setUnit(elem[5])
                
                for i in self.getElementPins(elem[-1]):
                    (x, y, drill, r) = self.getPinParameters(i)

                    holes.append([x + X1, y - Y1, drill])  # shift hole according to part position
        #
        return holes

    def getPCB(self):
        PCB = []
        ##
        #line
        for i in self.getAllLines(self.getLayerByNumber(7)):
            (x1, y1, x2, y2, width) = self.getLineParameters(i)

            if [x1, y1] != [x2, y2]:
                PCB.append(['Line', x1, y1, x2, y2])
        #arcs
        for i in self.getAllArcs(self.getLayerByNumber(7)):
            (x1, y1, x2, y2, curve, width) = self.getArcParameters(i)
            
            PCB.append(['Arc', x2, y2, x1, y1, curve])
        #
        if len(PCB) == 0:
            pcbSize = re.search('PCB\s*\[.+? (.+?) (.+?)\]', self.projektBRD).groups()
            self.width = self.setUnit(pcbSize[0])
            self.height = self.setUnit(pcbSize[1])
            
            PCB.append(['Line', 0, 0, self.width, 0])
            PCB.append(['Line', self.width, 0, self.width, -self.height])
            PCB.append(['Line', self.width, -self.height, 0, -self.height])
            PCB.append(['Line', 0, -self.height, 0, 0])
        #
        return [PCB, True]

    def getPads(self, doc, layerNumber, grp, layerName, layerColor, defHeight):
        layerName = "{0}_{1}".format(layerName, layerNumber)
        layerSide = PCBlayers[softLayers["geda"][layerNumber][1]][0]
        layerType = PCBlayers[softLayers["geda"][layerNumber][1]][3]
        
        ####
        layerS = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", layerName)
        layerNew = layerSilkObject(layerS, layerType)
        layerNew.holes = self.showHoles()
        layerNew.defHeight = defHeight
        ####
        ## via
        for i in self.getAllVias():
            (x, y, drill, r) = self.getViaParameters(i)
            
            layerNew.createObject()
            layerNew.addCircle(x, y, r)
            layerNew.setFace()
        ###
        ## pin
        for elem in self.getAllParts():
            X1 = self.setUnit(elem[4])
            Y1 = self.setUnit(elem[5])
            
            for i in self.getElementPins(elem[-1]):
                padType = i[8].replace('"', '')
                (X, Y, drill, diameter) = self.getPinParameters(i)
                X += X1
                Y -= Y1
                
                if "square" in padType or len(padType) > 8 and padType[7] == '1':
                    a = diameter
                    
                    x1 = X - a
                    y1 = Y - a
                    x2 = X + a
                    y2 = Y + a
                    
                    layerNew.createObject()
                    layerNew.addRectangle(x1, y1, x2, y2)
                    layerNew.setFace()
                else:  # circle
                    layerNew.createObject()
                    layerNew.addCircle(X, Y, diameter)
                    layerNew.setFace()
            #
            if layerSide == 1:
                for i in re.findall(r'Pad\[(.+?) (.+?) (.+?) (.+?) (.+?) (.+?) (.+?) "(.+?)" "(.+?)" (.+?)\]', elem[-1]):
                    padType = i[9].replace('"', '')
                    a = self.setUnit(i[4]) / 2.
                    
                    if i[0] == i[2]:
                        x1 = X1 + self.setUnit(i[0]) + a
                        y1 = 0 - Y1 - self.setUnit(i[1]) + a
                        x2 = X1 + self.setUnit(i[2]) - a
                        y2 = 0 - Y1 - self.setUnit(i[3]) - a
                    else:
                        x1 = X1 + self.setUnit(i[0]) - a
                        y1 = 0 - Y1 - self.setUnit(i[1]) + a
                        x2 = X1 + self.setUnit(i[2]) + a
                        y2 = 0 - Y1 - self.setUnit(i[3]) - a
                    
                    if "square" in padType or len(padType) > 8 and padType[7] == '1':
                        layerNew.createObject()
                        layerNew.addRectangle(x1, y1, x2, y2)
                        layerNew.setFace()
                    else:  # long pad
                        xs = x1 - (x1 - x2) / 2.
                        ys = y1 - (y1 - y2) / 2.
                        dx = abs((x1 - x2) / 2.)
                        dy = abs((y1 - y2) / 2.)
                        
                        layerNew.createObject()
                        layerNew.addPadLong(xs, ys, dx, dy, 100)
                        layerNew.setFace()
        ###
        layerNew.generuj(layerS)
        layerNew.updatePosition_Z(layerS)
        viewProviderLayerSilkObject(layerS.ViewObject)
        layerS.ViewObject.ShapeColor = layerColor
        grp.addObject(layerS)
        #
        doc.recompute()
    
    def getPaths(self, layerID):
        wires = []
        signal = []
        
        if layerID == 1:  # top
            layers = self.groups['top']
        else:  # bottom
            layers = self.groups['bottom']
        
        for layerNumber in layers:
            #line
            for i in self.getAllLines(self.getLayerByNumber(layerNumber)):
                (x1, y1, x2, y2, width) = self.getLineParameters(i)

                if [x1, y1] != [x2, y2]:
                    wires.append(['line', x1, y1, x2, y2, width])
            #
            for i in self.getAllArcs(self.getLayerByNumber(layerNumber)):
                if float(i[5]) == 360:  # arcs
                        xs = self.setUnit(i[0])
                        ys = 0 - self.setUnit(i[1])
                        r = self.setUnit(i[2])
                        width = self.setUnit(i[4])
                        
                        wires.append(['circle', xs, ys, r, width])
                else:  # circles
                    (x1, y1, x2, y2, curve, width) = self.getArcParameters(i)
                
                    wires.append(['arc', x1, y1, x2, y2, curve, width, 'round'])
        #
        wires.append(signal)
        return wires
        
    def getElementArcParameters(self, arc):
        return self.getArcParameters([arc[0], arc[1], arc[2], arc[3], arc[6], arc[4], arc[5]])
        
    def getArcParameters(self, arc):
        xs = self.setUnit(arc[0])
        ys = 0 - self.setUnit(arc[1])
        r = self.setUnit(arc[2])
        #height = self.setUnit(arc[3])
        width = self.setUnit(arc[4])
        startAngle = radians(float(arc[5]) + 180)
        stopAngle = startAngle + radians(float(arc[6]))
        
        if startAngle > stopAngle:
            p = stopAngle
            stopAngle = startAngle
            startAngle = p
        
        startAngle = degrees(startAngle)
        stopAngle = degrees(stopAngle)
        
        x1 = xs + r
        y1 = ys
        
        [x1, y1] = self.obrocPunkt2([x1, y1], [xs, ys], startAngle)
        [x2, y2] = self.obrocPunkt2([x1, y1], [xs, ys], stopAngle - startAngle)
        
        return (x1, y1, x2, y2, stopAngle - startAngle, width)
        
    def getLineParameters(self, line):
        x1 = self.setUnit(line[0])
        y1 = 0 - self.setUnit(line[1])
        x2 = self.setUnit(line[2])
        y2 = 0 - self.setUnit(line[3])
        width = self.setUnit(line[4])
        
        return (x1, y1, x2, y2, width)
        
    def getAllLines(self, layer):
        return re.findall('Line\s*\[(.+?) (.+?) (.+?) (.+?) (.+?) .+? .+?\]', layer)
        
    def getAllArcs(self, layer):
        return re.findall('Arc\s*\[(.+?) (.+?) (.+?) (.+?) (.+?) .+? (.+?) (.+?) .+?\]', layer)
        
    def getPinParameters(self, pin):
        return self.getViaParameters(pin)
    
    def getViaParameters(self, via):
        x = self.setUnit(via[0])
        y = 0 - self.setUnit(via[1])
        drill = self.setUnit(via[5]) / 2.
        r = self.setUnit(via[2]) / 2.
        
        return (x, y, drill, r)
    
    def getAllVias(self):
        return re.findall(r'Via\s*\[(.+?) (.+?) (.+?) (.+?) (.+?) (.+?) (.+?) (.+?)\]', self.projektBRD)
    
    def getElementPins(self, part):
        return re.findall(r'Pin\s*\[(.+?) (.+?) (.+?) (.+?) (.+?) (.+?) (.+?) (.+?) (.+?)\]', part)
        
    def getAllParts(self):
        return re.findall(r'Element\s*\[(.+?) "(.*?)" "(.*?)" "(.*?)" (.+?) (.+?) (.+?) (.+?) (.+?) (.+?) (.+?)\]\n\(\n(.+?)\n\t\)\n', self.projektBRD, re.DOTALL|re.MULTILINE)

    def getLayerByNumber(self, layerNumber):
        '''Function returns whole layer section'''
        try:
            layer = re.search('^Layer\s*\[{0} .+?\]\n\(\n([^\)].+?\n)?\)\n'.format(layerNumber), self.projektBRD, re.DOTALL|re.MULTILINE).groups()[0]
            if layer:
                return layer
            else:
                return ''
        except:
            return ''

    def getSilkLayer(self, doc, layerNumber, grp, layerName, layerColor, defHeight):
        layerName = "{0}_{1}".format(layerName, layerNumber)
        layerType = PCBlayers[softLayers["geda"][layerNumber][1]][3]

        layerS = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", layerName)
        layerNew = layerSilkObject(layerS, layerType)
        layerNew.defHeight = defHeight
        ####
        for elem in self.getAllParts():
            X1 = self.setUnit(elem[4])
            Y1 = self.setUnit(elem[5])
            
            # linie
            for i in re.findall(r'ElementLine\s*\[(.+?) (.+?) (.+?) (.+?) (.+?)\]', elem[-1]):
                (x1, y1, x2, y2, width) = self.getLineParameters(i)

                if [x1, y1] != [x2, y2]:
                    layerNew.createObject()
                    layerNew.addLineWidth(x1 + X1, y1 - Y1, x2 + X1, y2 - Y1, width)
                    layerNew.setFace()
            # luki
            for i in re.findall(r'ElementArc\s*\[(.+?) (.+?) (.+?) (.+?) (.+?) (.+?) (.+?)\]', elem[-1]):
                if float(i[5]) == 360:
                    xs = self.setUnit(i[0])
                    ys = 0 - self.setUnit(i[1])
                    radius = self.setUnit(i[2])
                    width = self.setUnit(i[4])
                    
                    layerNew.createObject()
                    layerNew.addCircle(xs + X1, ys - Y1, radius, width)
                    layerNew.setFace()
                else:
                    (x1, y1, x2, y2, curve, width) = self.getElementArcParameters(i)
                    
                    layerNew.createObject()
                    layerNew.addArcWidth([x1 + X1, y1 - Y1], [x2 + X1, y2 - Y1], curve, width)
                    layerNew.setFace()
        #####
        silkLayer = self.getLayerByNumber(10)
        #linie
        for i in self.getAllLines(silkLayer):
            (x1, y1, x2, y2, width) = self.getLineParameters(i)
            
            if [x1, y1] != [x2, y2]:
                layerNew.createObject()
                layerNew.addLineWidth(x1, y1, x2, y2, width)
                layerNew.setFace()
        #luki
        for i in self.getAllArcs(silkLayer):
            if float(i[5]) == 360:
                xs = self.setUnit(i[0])
                ys = 0 - self.setUnit(i[1])
                radius = self.setUnit(i[2])
                width = self.setUnit(i[4])
                
                layerNew.createObject()
                layerNew.addCircle(xs, ys, radius, width)
                layerNew.setFace()
            else:
                (x1, y1, x2, y2, curve, width) = self.getElementArcParameters(i)
                
                layerNew.createObject()
                layerNew.addArcWidth([x1, y1], [x2, y2], curve, width)
                layerNew.setFace()
        #polygon
        for i in re.findall('Polygon\s*\(.+?\)\n\t\(\n.(.+?)\n\t\)\n', silkLayer, re.DOTALL|re.MULTILINE):
            poin = []
            
            punkty = i.strip().split("]")
            punkty = punkty[:-1]
            for j in range(len(punkty)):
                x1 = self.setUnit(re.search('\[(.+?) (.*)', punkty[j]).groups()[0])
                y1 = 0 - self.setUnit(re.search('\[(.+?) (.*)', punkty[j]).groups()[1])
                
                if j == len(punkty) - 1:
                    x2 = self.setUnit(re.search('\[(.+?) (.*)', punkty[0]).groups()[0])
                    y2 = 0 - self.setUnit(re.search('\[(.+?) (.*)', punkty[0]).groups()[1])
                else:
                    x2 = self.setUnit(re.search('\[(.+?) (.*)', punkty[j + 1]).groups()[0])
                    y2 = 0 - self.setUnit(re.search('\[(.+?) (.*)', punkty[j + 1]).groups()[1])
                
                if not [x1, y1] == [x2, y2]:  # remove points, only lines
                    poin.append(['Line', x1, y1, x2, y2])
            
            layerNew.createObject()
            layerNew.addPolygon(poin)
            layerNew.setFace()
        #########
        layerNew.generuj(layerS)
        layerNew.updatePosition_Z(layerS)
        viewProviderLayerSilkObject(layerS.ViewObject)
        layerS.ViewObject.ShapeColor = layerColor
        grp.addObject(layerS)
        #
        doc.recompute()

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
        ##  additional layers
        grp = createGroup_Layers()
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
                
                if ID == 10:
                    self.getSilkLayer(doc, ID, grp, name, color, transp)
                elif ID in [17, 18]:
                    self.getPads(doc, ID, grp, name, color, transp)
                elif ID in [1, 2]:
                    self.generatePaths(self.getPaths(ID), doc, grp, name, color, ID, transp)
                elif ID == 0:
                    self.addAnnotations(self.getAnnotations(), doc, color)
        return doc
