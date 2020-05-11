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
try:
    import builtins
except:
    import __builtin__ as builtins
import re
from math import radians
#import __future__
#
from PCBconf import softLayers
from PCBobjects import *
from formats.dialogMAIN_FORM import dialogMAIN_FORM
from formats.baseModel import baseModel


class dialogMAIN(dialogMAIN_FORM):
    def __init__(self, filename=None, parent=None):
        dialogMAIN_FORM.__init__(self, parent)
        self.databaseType = "hyp"
        #
        self.projektBRD = builtins.open(filename, "r").read().replace('\r', '')
        self.layersNames = self.getLayersNames()
        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetBool("boardImportThickness", True):
            self.gruboscPlytki.setValue(self.getBoardThickness())
        ##
        self.generateLayers([])
        self.spisWarstw.sortItems(1)
    
    def getBoardThickness(self):
        layers = re.search(r'\{STACKUP\s+(.+?)\s+\}', self.projektBRD, re.MULTILINE|re.DOTALL).groups()[0]
        thickness = sum([float(i) for i  in re.findall(r'T=(.+?) ', layers)])

        return float("%.5f" % (thickness * 25.4))
    
    def getLayersNames(self):
        dane = {}
        # extra layers
        dane[1] = {"name": softLayers[self.databaseType][1]["description"], "color": softLayers[self.databaseType][1]["color"]}
        dane[16] = {"name": softLayers[self.databaseType][16]["description"], "color": softLayers[self.databaseType][16]["color"]}
        dane[17] = {"name": softLayers[self.databaseType][17]["description"], "color": softLayers[self.databaseType][17]["color"]}
        dane[18] = {"name": softLayers[self.databaseType][18]["description"], "color": softLayers[self.databaseType][18]["color"]}
        #
        return dane


class HYP_PCB(baseModel):
    def __init__(self, filename, parent):
        self.fileName = filename
        self.dialogMAIN = dialogMAIN(self.fileName)
        self.databaseType = "hyp"
        self.parent = parent
        #
        self.layers = []
    
    def defineFunction(self, layerNumber):
        if layerNumber in [17, 18]:  # pady
            return "pads"
        elif layerNumber in [1, 16]:  # paths
            return "paths"
        
    def setUnit(self, value):
        '''Get unit from transferred value and convert to millimeters - if necessary'''
        return float("%.5f" % (float(value) * 25.4))

    def setProject(self):
        '''Load project from file'''
        self.projektBRD = builtins.open(self.fileName, "r").read().replace('\r\n', '\n')
        self.layers = re.findall(r'\(SIGNAL T=.+? P=.+? L=(.+?)\)', self.projektBRD)

    def getSilkLayer(self, layerNew, layerNumber, display=[True, True, True, True]):
        pass
    
    def getSilkLayerModels(self, layerNew, layerNumber, display=[True, True, True, True]):
        pass
    
    def getPaths(self, layerNew, layerNumber, display=[True, True, True, False]):
        if layerNumber[0] == 1:
            layer = 'Top'
        else:
            layer = 'Bottom'
        #
        for j in re.findall(r'{NET=(.*?)\n(.*?)}', self.projektBRD, re.MULTILINE|re.DOTALL):
            signal = j[0]
            # lines
            for i in re.findall(r'\(SEG X1=(.+?) Y1=(.+?) X2=(.+?) Y2=(.+?) W=(.+?) L=%s\)' % layer, j[1]):
                x1 = self.setUnit(i[0])
                y1 = self.setUnit(i[1])
                x2 = self.setUnit(i[2])
                y2 = self.setUnit(i[3])
                width = self.setUnit(i[4])
                
                if [x1, y1] != [x2, y2]:
                    layerNew.addLineWidth(x1, y1, x2, y2, width)
                    layerNew.setFace(signalName=signal)
            # arcs
            for i in re.findall(r'\(ARC X1=(.+?) Y1=(.+?) X2=(.+?) Y2=(.+?) XC=(.+?) YC=(.+?) R=.+? W=(.+?) L=%s\)[^ Circle]' % layer, j[1]):
                x1 = self.setUnit(i[0])
                y1 = self.setUnit(i[1])
                
                x2 = self.setUnit(i[2])
                y2 = self.setUnit(i[3])
                
                xs = self.setUnit(i[4])
                ys = self.setUnit(i[5])
                
                width = self.setUnit(i[6])
                angle = self.getArcParameters(x1, y1, x2, y2, xs, ys)
                #
                layerNew.addArcWidth([x1, y1], [x2, y2],  angle, width)
                layerNew.setFace(signalName=signal)
    
    def getArcParameters(self, x1, y1, x2, y2, xs, ys):
        angle = degrees(atan2(y2 - ys, x2 - xs) - atan2(y1 - ys, x1 - xs))
        if angle < 0:
            angle = angle + 360
        
        return angle
    
    def getParts(self):
        parts = []
        
        for i in re.findall(r'\(.+? REF=(|.+?) .+?=(|.+?) L=(.+?)(| PKG=.+?)\)  R(.+?) X=(.+?) Y=(.+?) :  Lib: (.+?) : (.+?) ', self.projektBRD):
            if i[2] == self.layers[0]:
                side = 'TOP'
            else:
                side = 'BOTTOM'
            #
            dataO = {
                'name': i[0], 
                'library': i[7], 
                'package': i[8], 
                'value': i[1], 
                'x': self.setUnit(i[5]), 
                'y': self.setUnit(i[6]),
                'locked': False,
                'populated': False, 
                'smashed': False, 
                'rot': float(i[4]), 
                'side': side,
                'dataElement': i
            }
            
            dataO['EL_Name'] = {
                "text": "NAME",
                "x": dataO['x'] - 2,
                "y": dataO['y'] + 2,
                "z": 0,
                "size": 1.27,
                "rot": dataO['rot'],
                "side": dataO['side'],
                "align": "bottom-left",
                "spin": True,
                "font": "Fixed",
                "display": True,
                "distance": 1,
                "tracking": 0,
                "mode": 'param'
            }
            
            dataO['EL_Value'] = {
                "text": "VALUE",
                "x": dataO['x'] - 2,
                "y": dataO['y'] - 2,
                "z": 0,
                "size": 1.27,
                "rot": dataO['rot'],
                "side": dataO['side'],
                "align": "bottom-left",
                "spin": True,
                "font": "Fixed",
                "display": False,
                "distance": 1,
                "tracking": 0,
                "mode": 'param'
            }
            #
            parts.append(dataO)
        #
        return parts
        
    def addPad(self, layerNew, padData, x, y):
        if len(padData):
            padData = padData[0]
            padShape = int(padData[0])  # 0:round, 1:square, 2:long
            outDiameter = self.setUnit(padData[1])
            rot = float(padData[3])
            #
            if padShape == 1:  # square
                a = outDiameter / 2.
                x1 = x - a
                y1 = y - a
                x2 = x + a
                y2 = y + a
                
                layerNew.addRectangle(x1, y1, x2, y2)
                layerNew.addRotation(x, y, rot)
                layerNew.setFace()
            elif padShape == 2:  # long
                e = outDiameter
                
                layerNew.addPadLong(x, y, e, e / 2., 100)
                layerNew.addRotation(x, y, rot)
                layerNew.setFace()
            else:  # round
                layerNew.addCircle(x, y, outDiameter / 2.)
                layerNew.addRotation(x, y, rot)
                layerNew.setFace()
    
    def getPads(self, layerNew, layerNumber, layerSide, tentedViasLimit, tentedVias):
        if layerSide == 1:
            layer = 'Top'
        else:
            layer = 'Bottom'
        # via
        for i in re.findall(r'\(VIA X=(.+?) Y=(.+?) P=(.+?)\) .+?', self.projektBRD):
            x = self.setUnit(i[0])
            y = self.setUnit(i[1])
           
            data = re.findall(r'{PADSTACK=%s,([\w.]+)\n(.*?)}' % i[2], self.projektBRD, re.MULTILINE|re.DOTALL)[0]
            padData = re.findall(r'\(%s,(.*?),(.*?),(.*?),(.*?)\)' % layer, data[1], re.MULTILINE|re.DOTALL)
            ##### ##### ##### 
            ##### tented dVias
            if len(padData):
                if self.filterTentedVias(tentedViasLimit, tentedVias, self.setUnit(data[0]), False):
                    continue
            ##### ##### ##### 
            self.addPad(layerNew, padData, x, y)
        
        if not tentedVias:
            # pads
            for i in re.findall(r'\(PIN X=(.+?) Y=(.+?) R=.+? P=(.+?)\)(| .+?,) Pad Diameter: (.+?)  Drill: (.+?)\n', self.projektBRD):
                x = self.setUnit(i[0])
                y = self.setUnit(i[1])
                #outDiameter = self.setUnit(i[4]) / 2.
                
                data = re.findall(r'{PADSTACK=%s,([\w.]+)\n(.*?)}' % i[2], self.projektBRD, re.MULTILINE|re.DOTALL)[0]
                padData = re.findall(r'\(%s,(.*?),(.*?),(.*?),(.*?)\)' % layer, data[1], re.MULTILINE|re.DOTALL)
                #
                self.addPad(layerNew, padData, x, y)
            # smd
            for i in re.findall(r'\(PIN X=(.+?) Y=(.+?) R=(.+?) P=(.+?)\)(| .+?,) Smd Dx: (.+?)  Dy: (.+?)\n', self.projektBRD):
                data = re.findall(r'{PADSTACK=%s\n(.*?)}' % i[3], self.projektBRD, re.MULTILINE|re.DOTALL)
                padData = re.findall(r'\(%s,(.*?),(.*?),(.*?),(.*?)\)' % layer, data[0], re.MULTILINE|re.DOTALL)
                if len(padData):
                    padData = padData[0]
                    padShape = int(padData[0])  # 0:round, 1:square, 2:long
                    outDiameter = self.setUnit(padData[1])
                    rot = float(padData[3])
                    #
                    xs = self.setUnit(i[0])
                    ys = self.setUnit(i[1])
                    
                    dx = self.setUnit(i[5])
                    dy = self.setUnit(i[6])
                    
                    if padShape in ['0', '2']:
                        if padShape == '2':
                            roundness = 50
                        else:
                            roundness = 100
                        
                        e = outDiameter
                    
                        layerNew.addPadLong(xs, ys, dx / 2., dy / 2., roundness)
                        layerNew.addRotation(xs, ys, rot)
                        layerNew.setFace()
                    else:  # roundness = 0
                        x1 = xs - dx / 2.
                        y1 = ys - dy / 2.
                        x2 = xs + dx / 2.
                        y2 = ys + dy / 2.
                        
                        layerNew.addRectangle(x1, y1, x2, y2)
                        layerNew.addRotation(xs, ys, rot)
                        layerNew.setFace()
    
    def getHoles(self, holesObject, types, Hmin, Hmax):
        ''' holes/vias '''
        holesList = []
        
        # holes
        if types['H']:
            for i in re.findall(r'\(PERIMETER_ARC X1=.+? Y1=.+? X2=.+? Y2=.+? XC=(.+?) YC=(.+?) R=(.+?)\) Holes', self.projektBRD):
                x = self.setUnit(i[0])
                y = self.setUnit(i[1])
                r = self.setUnit(i[2])
                
                holesList = self.addHoleToObject(holesObject, Hmin, Hmax, types['IH'], x, y, r, holesList)
        # vias
        if types['V']:
            for i in re.findall(r'\(VIA X=(.+?) Y=(.+?) P=(.+?)\) .+?', self.projektBRD):
                x = self.setUnit(i[0])
                y = self.setUnit(i[1])
                r = self.setUnit(re.search(r'PADSTACK={0},(.+?)\n'.format(i[2]), self.projektBRD).groups()[0]) / 2.
                
                holesList = self.addHoleToObject(holesObject, Hmin, Hmax, types['IH'], x, y, r, holesList)
        # pads
        if types['P']:  # pads
            for i in re.findall(r'\(PIN X=(.+?) Y=(.+?) R=.+? P=.+?\)(| .+?,) Pad Diameter: .+?  Drill: (.+?)\n', self.projektBRD):
                x = self.setUnit(i[0])
                y = self.setUnit(i[1])
                r = self.setUnit(i[3]) / 2.
                
                holesList = self.addHoleToObject(holesObject, Hmin, Hmax, types['IH'], x, y, r, holesList)

    def getPCB(self, borderObject):
        board = re.search(r'\{BOARD\s+(.+?)\s+\}', self.projektBRD, re.MULTILINE|re.DOTALL).groups()[0]
        #
        for i in re.findall(r'\(PERIMETER_SEGMENT X1=(.+?) Y1=(.+?) X2=(.+?) Y2=(.+?)\) Wires: From Board', board):
            x1 = self.setUnit(i[0])
            y1 = self.setUnit(i[1])
            x2 = self.setUnit(i[2])
            y2 = self.setUnit(i[3])
            
            if [x1, y1] != [x2, y2]:
                borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x2, y2, 0)))
        #
        for i in re.findall(r'\(PERIMETER_ARC X1=.+? Y1=.+? X2=.+? Y2=.+? XC=(.+?) YC=(.+?) R=(.+?)\) Circles: Board Outline .*', board):
            x = self.setUnit(i[0])
            y = self.setUnit(i[1])
            r = self.setUnit(i[2])
            
            borderObject.addGeometry(Part.Circle(FreeCAD.Vector(x, y), FreeCAD.Vector(0, 0, 1), r))
        #
        for i in re.findall(r'\(PERIMETER_ARC X1=(.+?) Y1=(.+?) X2=(.+?) Y2=(.+?) XC=(.+?) YC=(.+?) R=.+?\) Arcs: Board Outline .*', board):
            x1 = self.setUnit(i[0])
            y1 = self.setUnit(i[1])
            
            x2 = self.setUnit(i[2])
            y2 = self.setUnit(i[3])
            
            xs = self.setUnit(i[4])
            ys = self.setUnit(i[5])
            
            angle = self.getArcParameters(x1, y1, x2, y2, xs, ys)
            #
            [x3, y3] = self.arcMidPoint([x1, y1], [x2, y2], angle)
            arc = Part.ArcOfCircle(FreeCAD.Vector(x1, y1, 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(x2, y2, 0.0))
            borderObject.addGeometry(arc)
