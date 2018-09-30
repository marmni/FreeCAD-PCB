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
from math import sqrt
import os
#
from PCBconf import PCBlayers, softLayers
from PCBobjects import *
from formats.PCBmainForms import *
from command.PCBgroups import *
from formats.dialogMAIN_FORM import dialogMAIN_FORM
from PCBfunctions import mathFunctions
from PCBconf import kicadColorsDefinition


def setProjectFile(filename):
    projektBRD = builtins.open(filename, "r").read()[1:]
    wynik = ''
    licznik = 0
    txt = ''
    start = 0
    #
    txt_1 = 0

    for i in projektBRD:
        if i in ['"', "'"] and txt_1 == 0:
            txt_1 = 1
        elif i in ['"', "'"] and txt_1 == 1:
            txt_1 = 0
        
        if txt_1 == 0:
            if i == '(':
                licznik += 1
                start = 1
            elif i == ')':
                licznik -= 1
        
        txt += i
        
        if licznik == 0 and start == 1:
            wynik += '[start]' + txt.strip() + '[stop]'
            txt = ''
            start = 0
    
    return wynik
    

class dialogMAIN(dialogMAIN_FORM):
    def __init__(self, filename=None, parent=None):
        dialogMAIN_FORM.__init__(self, parent)
        self.databaseType = "kicad"
        #
        self.plytkaPCB_otworyH.setChecked(False)
        self.plytkaPCB_otworyH.setDisabled(True)
        #
        self.projektBRD = setProjectFile(filename)
        self.layersNames = self.getLayersNames()
        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetBool("boardImportThickness", True):
            self.gruboscPlytki.setValue(self.getBoardThickness())
        ##
        self.generateLayers([28])
        self.spisWarstw.sortItems(1)
        
    def getBoardThickness(self):
        return float(re.findall(r'\(thickness (.+?)\)', self.projektBRD)[0])
        
    def getLayersNames(self):
        dane = {}
        
        layers = re.search(r'\[start\]\(layers(.+?)\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL).group(0)
        for i in re.findall(r'\((.*?) (.*?) .*?\)', layers):
            dane[int(i[0])] = {"name": i[1], "color": None}
        
        ####################
        # EXTRA LAYERS
        ####################
        # measures
        dane[106] = {"name": softLayers["kicad"][106]["name"], "color": softLayers["kicad"][106]["color"]}
        # pad
        dane[107] = {"name": softLayers["kicad"][107]["name"], "color": softLayers["kicad"][107]["color"]}
        dane[108] = {"name": softLayers["kicad"][108]["name"], "color": softLayers["kicad"][108]["color"]}
        ####################
        ####################
        return dane


class KiCadv3_PCB(mathFunctions):
    def __init__(self, filename, parent):
        self.fileName = filename
        self.dialogMAIN = dialogMAIN(self.fileName)
        self.databaseType = "kicad"
        self.parent = parent
        #
        self.spisWarstw = {}
        self.elements = []
        self.borderLayerNumber = 28
    
    def Draft2Sketch(self, elem, sketch):
        return (DraftGeomUtils.geom(elem.toShape().Edges[0], sketch.Placement))
        
    def filterHoles(self, r, Hmin, Hmax):
        if Hmin == 0 and Hmax == 0:
            return True
        elif Hmin != 0 and Hmax == 0 and Hmin <= r * 2:
            return True
        elif Hmax != 0 and Hmin == 0 and r * 2 <= Hmax:
            return True
        elif Hmin <= r * 2 <= Hmax:
            return True
        else:
            return False
    
    def setProject(self):
        self.projektBRD = setProjectFile(self.fileName)
        # layers
        layers = re.search(r'\[start\]\(layers(.+?)\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL).group(0)
        for i in re.findall(r'\((.*?) (.*?) .*?\)', layers):
            self.spisWarstw[i[1]] = int(i[0])

    def getSettings(self, paramName):
        return re.search(r'\({0} (.*?)\)'.format(paramName), self.projektBRD).groups()[0]
    
    def getDimensions(self):
        wymiary = []
        #
        for i in re.findall(r'\[start\]\(dimension\s+(.+?)\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL):
            [x1, y1] = re.search(r'\(feature1\s+\(pts\s+\(xy\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(xy\s+[0-9\.-]*?\s+[0-9\.-]*?\)\)\)', i, re.MULTILINE|re.DOTALL).groups()
            [x2, y2] = re.search(r'\(feature2\s+\(pts\s+\(xy\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(xy\s+[0-9\.-]*?\s+[0-9\.-]*?\)\)\)', i, re.MULTILINE|re.DOTALL).groups()
            [x3, y3] = re.search(r'\(crossbar\s+\(pts\s+\(xy\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(xy\s+[0-9\.-]*?\s+[0-9\.-]*?\)\)\)', i, re.MULTILINE|re.DOTALL).groups()
            #
            x1 = float(x1)
            y1 = float(y1) * (-1)
            x2 = float(x2)
            y2 = float(y2) * (-1)
            x3 = float(x3)
            y3 = float(y3) * (-1)
            
            if x1 > x2:
                wymiary.append([x2, y2, x1, y1, x3, y3, ''])
            else:
                wymiary.append([x1, y1, x2, y2, x3, y3, ''])
        #
        return wymiary
    
    def getGlue(self, layerNumber):
        glue = {}
        # lines
        for i in self.getLine(layerNumber[1], self.projektBRD, "gr_line"):
            if not i['width'] in glue.keys():
                glue[i['width']] = []
            
            glue[i['width']].append(['line', i['x1'], i['y1'], i['x2'], i['y2']])
        # circles
        for i in self.getCircle(layerNumber[1], self.projektBRD, "gr_circle"):
            if not i['width'] in glue.keys():
                glue[i['width']] = []
            
            glue[i['width']].append(['circle', i['x'], i['y'], i['r']])
        # arcs
        for i in self.getArc(layerNumber[1], self.projektBRD, "gr_arc"):
            if not i['width'] in glue.keys():
                glue[i['width']] = []
            
            glue[i['width']].append(['arc', i['x2'], i['y2'], i['x1'], i['y1'], i['curve'], True])
        ##
        return glue
        
    def getPads(self, layerNew, layerNumber, layerSide):
        # via
        via_drill = float(self.getSettings('via_drill'))

        for i in re.findall(r'\(via\s+\(at\s+(.*?)\s+(.*?)\)\s+\(size\s+(.*?)\)\s+(\(drill\s+(.*?)\)|)', self.projektBRD):
            x = float(i[0])
            y = float(i[1]) * (-1)
            diameter = float(i[2])

            if i[4] == '':
                drill = via_drill / 2.
            else:
                drill = float(i[4]) / 2.
            
            layerNew.addCircle(x, y, diameter / 2.)
            layerNew.setFace()
        # pad
        self.getElements()
        #
        for i in self.elements:
            for j in self.getPadsList(i['data']):
                xs = j['x'] + i['x']
                ys = j['y'] + i['y']
                numerWarstwy = j['layers'].split(' ')
                
                rot_2 = j['rot']
                if i['rot'] != 0:
                    rot_2 -= i['rot']
                
                # kicad_pcb v3 TOP:         self.getLayerName(15) in numerWarstwy and layerNumber == 107
                # kicad_pcb v3 BOTTOM:      self.getLayerName(0) in numerWarstwy and layerNumber == 18
                # kicad_pcb v4 TOP:         self.getLayerName(0) in numerWarstwy and layerNumber == 107
                # kicad_pcb v4 BOTTOM:      self.getLayerName(31) in numerWarstwy and layerNumber == 108
                dodaj = False
                if self.databaseType == "kicad" and ((self.getLayerName(15) in numerWarstwy and layerNumber[0] == 107) or (self.getLayerName(0) in numerWarstwy and layerNumber[0] == 108)):
                    dodaj = True
                elif self.databaseType == "kicad_v4" and ((self.getLayerName(0) in numerWarstwy and layerNumber[0] == 107) or (self.getLayerName(31) in numerWarstwy and layerNumber[0] == 108)):
                    dodaj = True
                elif '*.Cu' in numerWarstwy:
                    dodaj = True
                #####
                #####
                if dodaj:
                    if j['padShape'] == 'rect':
                        x1 = xs - j['dx'] / 2. + j['xOF']
                        y1 = ys - j['dy'] / 2. + j['yOF']
                        x2 = xs + j['dx'] / 2. + j['xOF']
                        y2 = ys + j['dy'] / 2. + j['yOF']
                        
                        layerNew.addRectangle(x1, y1, x2, y2)
                        layerNew.addRotation(xs, ys, rot_2)
                        layerNew.addRotation(i['x'], i['y'], i['rot'])
                        layerNew.setFace()
                    elif j['padShape'] == 'circle':
                        layerNew.addCircle(xs + j['xOF'], ys + j['yOF'], j['dx'] / 2.)
                        layerNew.addRotation(xs, ys, rot_2)
                        layerNew.addRotation(i['x'], i['y'], i['rot'])
                        layerNew.setFace()
                    elif j['padShape'] == 'oval':
                        if j['dx'] == j['dy']:
                            layerNew.addCircle(xs + j['xOF'], ys + j['yOF'], j['dx'] / 2.)
                            layerNew.addRotation(xs, ys, rot_2)
                            layerNew.addRotation(i['x'], i['y'], i['rot'])
                            layerNew.setFace()
                        else:
                            layerNew.addPadLong(xs + j['xOF'], ys + j['yOF'], j['dx'] / 2., j['dy'] / 2., 100)
                            layerNew.addRotation(xs, ys, rot_2)
                            layerNew.addRotation(i['x'], i['y'], i['rot'])
                            layerNew.setFace()
                    elif j['padShape'] == 'trapezoid':
                        if j[8].strip() == '':
                            xRD = 0
                            yRD = 0
                        else:
                            rect_delta = re.findall(r'\(rect_delta ([-0-9\.]*?) ([-0-9\.]*?) \)', j[8].strip())[0]
                            yRD = float(rect_delta[0]) / 2.
                            xRD = float(rect_delta[1]) / 2.
                        
                        x1 = xs - j['dx'] / 2. + j['xOF']
                        y1 = ys - j['dy'] / 2. + j['yOF']
                        x2 = xs + j['dx'] / 2. + j['xOF']
                        y2 = ys + j['dy'] / 2. + j['yOF']
                        
                        layerNew.addTrapeze([x1, y1], [x2, y2], xRD, yRD)
                        layerNew.addRotation(xs, ys, rot_2)
                        layerNew.addRotation(i['x'], i['y'], i['rot'])
                        layerNew.setFace()

    def getPadsList(self, model):
        pads = []
        #
        dane2 = re.findall(r'\(pad .* ', model, re.MULTILINE|re.DOTALL)
        if len(dane2):
            dane2 = dane2[0].strip().split('(pad')
        
            for j in dane2:
                if j != '':
                    [x, y, rot] = re.search(r'\(at\s+([0-9\.-]*?)\s+([0-9\.-]*?)(\s+[0-9\.-]*?|)\)', j).groups()
                    pType= re.search(r'^.*?\s+([a-zA-Z_]+?)\s+', j).groups(0)[0]  # pad type - SMD/thru_hole/connect
                    pShape = re.search(r'^.+?\s+.+?\s+([a-zA-Z_]+?)\s+', j).groups(0)[0]  # pad shape - circle/rec/oval/trapezoid
                    [dx, dy] = re.search(r'\(size\s+([0-9\.-]+?)\s+([0-9\.-]+?)\)', j).groups(0)  #
                    #layers = re.search(r'\(layers\s+(.+?)\)', j).groups(0)[0]  #
                    layers = re.search(r'\(layers\s?(.*?|)\)', j).groups(0)[0].strip()  #
                    data = re.search(r'\(drill(\s+[a-zA-Z]*?|)(\s+[-0-9\.]*?|)(\s+[-0-9\.]*?|)(\s+\(offset\s+(.*?)\s+(.*?)\)|)\)', j)
                    #
                    x = float(x)
                    y = float(y) * (-1)
                    dx = float(dx)
                    dy = float(dy)
                    if rot == '':
                        rot = 0.0
                    else:
                        rot = float(rot)
                        
                    if layers == "":
                        layers = ' '.join(self.spisWarstw.keys())
                        
                        
                    if data == None:
                        drill = 0.0
                        hType = None
                        [xOF, yOF] = [0.0, 0.0]
                    else:
                        data = data.groups()
                        
                        if pType == 'smd':
                            drill = 0.0
                            hType = None
                        else:
                            hType = data[0].strip()
                            if hType == '':
                                hType = 'circle'
                                drill = float(data[1]) / 2.0
                            else:
                                drill = "{0} {1}".format(data[1], data[2])
                        
                        if not data[4] or data[4].strip() == '':
                            xOF = 0.0
                        else:
                            xOF = float(data[4])
                        
                        if not data[5] or data[5].strip() == '':
                            yOF = 0.0
                        else:
                            yOF = float(data[5])
                    ##
                    pads.append({'x': x, 'y': y, 'rot': rot, 'padType': pType, 'padShape': pShape, 'r': drill, 'dx': dx, 'dy': dy, 'holeType': hType, 'xOF': xOF, 'yOF': yOF, 'layers': layers})
        #
        return pads

    def getHoles(self, holesObject, types, Hmin, Hmax):
        # vias
        if types['V']:
            via_drill = float(self.getSettings('via_drill'))
            for i in re.findall(r'\(via\s+\(at\s+(.*?)\s+(.*?)\)\s+\(size\s+.*?\)\s+(\(drill\s+(.*?)\)|)', self.projektBRD):
                x = float(i[0])
                y = float(i[1]) * (-1)

                if i[3] == '':
                    r = via_drill / 2.
                else:
                    r = float(i[3]) / 2.
                
                if self.filterHoles(r, Hmin, Hmax):
                    holesObject.addGeometry(Part.Circle(FreeCAD.Vector(x, y, 0.), FreeCAD.Vector(0, 0, 1), r))
        # pads
        if types['P']:
            for i in re.findall(r'\[start\]\(module(.+?)\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL):
                [X1, Y1, ROT] = re.search(r'\(at\s+([0-9\.-]*?)\s+([0-9\.-]*?)(\s+[0-9\.-]*?|)\)', i).groups()
                #
                X1 = float(X1)
                Y1 = float(Y1) * (-1)
                if ROT == '':
                    ROT = 0.0
                else:
                    ROT = float(ROT)
                ##
                for j in self.getPadsList(i):
                    if j['padType'] != 'smd' and j['r'] != 0.0:
                        if j['holeType'] == "circle":
                            [xR, yR] = self.obrocPunkt([j['x'], j['y']], [X1, Y1], ROT)
                            
                            if self.filterHoles(j['r'], Hmin, Hmax):
                                holesObject.addGeometry(Part.Circle(FreeCAD.Vector(xR, yR, 0.), FreeCAD.Vector(0, 0, 1), j['r']))
                        else:
                            dx = float(j['r'].strip().split(' ')[0])
                            dy = float(j['r'].strip().split(' ')[-1])
                            
                            if dx == dy:  # circle
                                if self.filterHoles(r1, Hmin, Hmax):
                                    holesObject.addGeometry(Part.Circle(FreeCAD.Vector(xR, yR, 0.), FreeCAD.Vector(0, 0, 1), w / 2.))
                            else:  # oval
                                x = float(j['x']) + X1
                                y = float(j['y']) * (-1) + Y1
                                curve = 90.
                                
                                if dx > dy:
                                    e = (dy * 50 / 100.) / 2.
                                    x1 = x - dx / 2. + e
                                    y1 = y + dy / 2.
                                    x2 = x + dx / 2. - e
                                    y2 = y - dy / 2.
                                    
                                    holesObject.addGeometry(Part.Line(FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x2, y1, 0)))
                                    holesObject.addGeometry(Part.Line(FreeCAD.Vector(x1, y2, 0), FreeCAD.Vector(x2, y2, 0)))
                                    
                                    [x3, y3] = self.arcMidPoint([x1, y1], [x1, y2], 90)
                                    arc = Part.Arc(FreeCAD.Vector(x1, y1, 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(x1, y2, 0.0))
                                    holesObject.addGeometry(self.Draft2Sketch(arc, holesObject))
                                    
                                    [x3, y3] = self.arcMidPoint([x2, y1], [x2, y2], -90)
                                    arc = Part.Arc(FreeCAD.Vector(x2, y1, 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(x2, y2, 0.0))
                                    holesObject.addGeometry(self.Draft2Sketch(arc, holesObject))
                                else:
                                    e = (dx * 50 / 100.) / 2.
                                    x1 = x - dx / 2.
                                    y1 = y + dy / 2. - e
                                    x2 = x + dx / 2.
                                    y2 = y - dy / 2. + e
                                    
                                    holesObject.addGeometry(Part.Line(FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x1, y2, 0)))
                                    holesObject.addGeometry(Part.Line(FreeCAD.Vector(x2, y1, 0), FreeCAD.Vector(x2, y2, 0)))
                                    
                                    [x3, y3] = self.arcMidPoint([x1, y1], [x2, y1], -90)
                                    arc = Part.Arc(FreeCAD.Vector(x1, y1, 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(x2, y1, 0.0))
                                    holesObject.addGeometry(self.Draft2Sketch(arc, holesObject))
                                    
                                    [x3, y3] = self.arcMidPoint([x1, y2], [x2, y2], 90)
                                    arc = Part.Arc(FreeCAD.Vector(x1, y2, 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(x2, y2, 0.0))
                                    holesObject.addGeometry(self.Draft2Sketch(arc, holesObject))
    
    def getLine(self, layer, source, oType, m=[0,0]):
        data = []
        #
        dane1 = re.findall(r'\({1}\s+\(start\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(end\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)(\s+\(angle\s+[0-9\.-]*?\)\s+|\s+)\(layer\s+{0}\)\s+\(width\s+([0-9\.]*?)\)(\s+\(tstamp\s+.+?\)|)\)'.format(layer, oType), source, re.MULTILINE|re.DOTALL)
        for i in dane1:
            x1 = float(i[0])
            y1 = float(i[1]) * (-1)
            x2 = float(i[2])
            y2 = float(i[3]) * (-1)
            width = float(i[5])
            
            if [x1, y1] == [x2, y2]:
                continue
            if m[0] != 0:
                x1 += m[0]
                x2 += m[0]
            if m[1] != 0:
                y1 += m[1]
                y2 += m[1]
            
            if width == 0:
                width = 0.01
            
            data.append({
                    'x1': x1,
                    'y1': y1,
                    'x2': x2,
                    'y2': y2,
                    'width': width,
                    'layer': layer,
                    'type': oType,
                })
        #
        return data
    
    def getCircle(self, layer, source, oType, m=[0,0]):
        data = []
        #
        dane1 = re.findall(r'\({1}\s+\(center\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(end\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(layer\s+{0}\)(\s+\(width\s+([0-9\.]*?)\)|)(\s+\(tstamp\s+.+?\)|)\)'.format(layer, oType), source, re.MULTILINE|re.DOTALL)
        for i in dane1:
            xs = float(i[0])
            ys = float(i[1]) * (-1)
            x1 = float(i[2])
            y1 = float(i[3]) * (-1)
            r = sqrt((xs - x1) ** 2 + (ys - y1) ** 2)
            
            if i[5] == '':
                width = 0.01
            else:
                width = float(i[5])
            
            if m[0] != 0:
                xs += m[0]
            if m[1] != 0:
                ys += m[1]
            
            data.append({
                    'x': xs,
                    'y': ys,
                    'r': r,
                    'width': width,
                    'layer': layer,
                    'type': oType,
                })
        #
        return data
        
    def getArc(self, layer, source, oType, m=[0,0]):
        data = []
        #
        dane1 = re.findall(r'\({1}\s+\(start\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(end\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(angle\s+([0-9\.-]*?)\)\s+\(layer\s+{0}\)(\s+\(width\s+([0-9\.]*?)\)|)(\s+\(tstamp\s+.+?\)|)\)'.format(layer, oType), source, re.MULTILINE|re.DOTALL)
        for i in dane1:
            xs = float(i[0])
            ys = float(i[1])
            x1 = float(i[2])
            y1 = float(i[3])
            curve = float(i[4])
            [x2, y2] = self.obrocPunkt2([x1, y1], [xs, ys], curve)
            
            if i[6].strip() != '':
                width = float(i[6]) 
            else:
                width = 0
                
            y1 *= -1
            y2 *= -1
            
            if m[0] != 0:
                x1 += m[0]
                x2 += m[0]
            if m[1] != 0:
                y1 += m[1]
                y2 += m[1]
            
            data.append({
                    'x1': x1,
                    'y1': y1,
                    'x2': x2,
                    'y2': y2,
                    'curve': curve,
                    'width': width,
                    'layer': layer,
                    'type': oType,
                })
        #
        return data

    def getPCB(self, borderObject):
        # lines
        for i in self.getLine(self.getLayerName(self.borderLayerNumber), self.projektBRD, 'gr_line'):
            borderObject.addGeometry(Part.Line(FreeCAD.Vector(i['x1'], i['y1'], 0), FreeCAD.Vector(i['x2'], i['y2'], 0)))
        # circles
        for i in self.getCircle(self.getLayerName(self.borderLayerNumber), self.projektBRD, 'gr_circle'):
            borderObject.addGeometry(Part.Circle(FreeCAD.Vector(i['x'], i['y']), FreeCAD.Vector(0, 0, 1), i['r']))
        # arc
        for i in self.getArc(self.getLayerName(self.borderLayerNumber), self.projektBRD, 'gr_arc'):
            [x3, y3] = self.arcMidPoint([i['x2'], i['y2']], [i['x1'], i['y1']], i['curve'])
            arc = Part.Arc(FreeCAD.Vector(i['x2'], i['y2'], 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(i['x1'], i['y1'], 0.0))
            borderObject.addGeometry(self.Draft2Sketch(arc, borderObject))
        ############
        ###### obj
        lType = re.escape(self.getLayerName(self.borderLayerNumber))
        
        for j in re.findall(r'\[start\]\(module(.+?)\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL):
            [X1, Y1, ROT] = re.search(r'\(at\s+([0-9\.-]*?)\s+([0-9\.-]*?)(\s+[0-9\.-]*?|)\)', j).groups()
            layer = re.search(r'\(layer\s+(.+?)\)', j).groups()[0]
            
            X1 = float(X1)
            Y1 = float(Y1) * (-1)
            
            if ROT == '':
                ROT = 0.0
            else:
                ROT = float(ROT)
            
            if self.databaseType == "kicad":  # kicad v3
                if self.spisWarstw[layer] == 15:  # top
                    side = 1
                else:
                    side = 0
            else:  # kicad v4
                if self.spisWarstw[layer] == 0:  # top
                    side = 1
                else:
                    side = 0
            # line
            for i in self.getLine(lType, j, 'fp_line', [X1, Y1]):
                [x1, y1] = self.obrocPunkt2([i['x1'], i['y1']], [X1, Y1], ROT)
                [x2, y2] = self.obrocPunkt2([i['x2'], i['y2']], [X1, Y1], ROT)
                borderObject.addGeometry(Part.Line(FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x2, y2, 0)))
            # circle
            for i in self.getCircle(lType, j, 'fp_circle', [X1, Y1]):
                [x, y] = self.obrocPunkt2([i['x'], i['y']], [X1, Y1], ROT)

                borderObject.addGeometry(Part.Circle(FreeCAD.Vector(x, y), FreeCAD.Vector(0, 0, 1), i['r']))
            # arc
            for i in self.getArc(lType, j, 'fp_arc', [X1, Y1]):
                [x1, y1] = self.obrocPunkt2([i['x1'], i['y1']], [X1, Y1], ROT)
                [x2, y2] = self.obrocPunkt2([i['x2'], i['y2']], [X1, Y1], ROT)
                
                [x3, y3] = self.arcMidPoint([x2, y2], [x1, y1], i['curve'])
                arc = Part.Arc(FreeCAD.Vector(x2, y2, 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(x1, y1, 0.0))
                borderObject.addGeometry(self.Draft2Sketch(arc, borderObject))
                
    def getLayerName(self, value):
        for i, j in self.spisWarstw.items():
            if j == value:
                return i
        return 'eeeeeefsdfstdgdfgdfghdfgdfgdfgfd'
        
    def getAnnotations(self):
        adnotacje = []
        #
        for i in re.findall(r'\[start\]\(gr_text(.+?)\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL):
            try:
                txt = re.search(r'\s(.*?)\s\(at', i).groups(0)[0].replace('"', '').replace('\r\n', '\n').replace('\r', '\n').replace('\\n', '\n')
                [x, y, rot] = re.search(r'\(at\s+([0-9\.-]*?)\s+([0-9\.-]*?)(\s+[0-9\.-]*?|)\)', i).groups()
                layer = re.search(r'\(layer\s+(.+?)\)', i).groups()[0]
                size = re.search(r'\(size\s+([0-9\.]*?)\s+[0-9\.]*?\)', i).groups()[0]
                justify = re.findall(r'( \(justify .*?\)|)\)', i)[-1].strip()
            except:
                continue
            #
            x = float(x)
            y = float(y) * (-1)
            if rot == '':
                rot = 0.0
            else:
                rot = float(rot)
            
            if self.spisWarstw[layer] in [15, 21]:
                side = 'TOP'
            else:
                side = 'BOTTOM'
            
            size = float(size)
            spin = True
            font = 'proportional'
            
            extra = re.findall(r'\(justify( [left|right]+|)( mirror|)\)', justify, re.DOTALL)
            if len(extra):
                if extra[0][0].strip() == 'right':
                    align = 'center-right'
                elif extra[0][0].strip() == 'left':
                    align = 'center-left'
                else:
                    align = 'center'
                
                if extra[0][1].strip() == 'mirror':
                    mirror = 2
                else:
                    mirror = 0
            else:
                align = 'center'
                mirror = False

            adnotacje.append([txt, x, y, size, rot, side, align, spin, mirror, font])
        #
        return adnotacje
    
    def getConstraintAreas(self, layerNumber):
        areas = []
        #
        if 'topSide' in PCBconstraintAreas[softLayers[self.databaseType][layerNumber][1]][1]:  # gorna warstwa
            if self.databaseType == 'kicad':
                lType = re.escape(self.getLayerName(15))
            else:
                lType = re.escape(self.getLayerName(0))
        elif 'bottomSide' in PCBconstraintAreas[softLayers[self.databaseType][layerNumber][1]][1]:  # dolna warstwa
            if self.databaseType == 'kicad':
                lType = re.escape(self.getLayerName(0))
            else:
                lType = re.escape(self.getLayerName(31))
        else:
            lType = '.*?'
        ###  polygon
        for i in re.findall(r'\[start\]\(zone\s+.+?\s+\(layer {0}\)(.*?)\s+\)\[stop\]'.format(lType), self.projektBRD, re.MULTILINE|re.DOTALL):
            data = re.search(r'\(keepout\s+\(tracks\s+(.*?)\)\s+\(vias\s+(.*?)\)\s+\(copperpour\s+(.*?)\)\)', i, re.MULTILINE|re.DOTALL)
            if data:
                info = [j for j in data.groups()]
            else:
                continue
        
            #900: ["tKeepout", "tPlaceKeepout"],
            #901: ["bKeepout", "bPlaceKeepout"],
            #902: ["tRouteKeepout", "tRouteKeepout"],
            #903: ["bRouteKeepout", "bRouteKeepout"],
            #904: ["ViaKeepout", "vRouteKeepout"],
            if layerNumber in [900, 901] and info[0] == 'allowed' and info[1] == 'allowed':
                continue
            
            if layerNumber in [902, 903] and not info[0] == 'not_allowed':  # RouteKeepout
                continue
            elif layerNumber == 904 and not info[1] == 'not_allowed':
                continue
            #
            points = re.findall(r'\(xy\s+(.*?)\s+(.*?)\)', i)
            areas.append(['polygon', []])

            for j in range(len(points)):
                x1 = float(points[j][0])
                y1 = float(points[j][1]) * (-1)
                
                if j + 2 > len(points):
                    x2 = float(points[0][0])
                    y2 = float(points[0][1]) * (-1)
                else:
                    x2 = float(points[j + 1][0])
                    y2 = float(points[j + 1][1]) * (-1)
                
                areas[-1][-1].append(['Line', x1, y1, x2, y2])
        #
        return areas
    
    def defineFunction(self, layerNumber):
        if layerNumber in [107, 108]:  # pady
            return "pads"
        elif layerNumber in [0, 15]:  # paths
            return "paths"
        elif layerNumber == 106:  # MEASURES
            return "measures"
        elif layerNumber in [32, 33]:  # glue
            return "glue"
        elif layerNumber in [900, 901, 902, 903, 904]:  # ConstraintAreas
            return "constraint"
        else:
            return "silk"

    def addStandardShapes(self, dane, layerNew, layerNumber, display=[True, True, True, True], parent=None):
        if parent:
            X = parent['x']
            Y = parent['y']
            oType = 'fp_'
        else:
            X = 0
            Y = 0
            oType = 'gr_'

        # linie/luki
        if display[0]:
            for i in self.getLine(layerNumber, dane, oType + 'line', [X, Y]):
                layerNew.addLineWidth(i['x1'], i['y1'], i['x2'], i['y2'], i['width'])
                if parent:
                    layerNew.addRotation(parent['x'], parent['y'], parent['rot'])
                    layerNew.setChangeSide(parent['x'], parent['y'], parent['side'])
                layerNew.setFace()
                
            for i in self.getArc(layerNumber, dane, oType + 'arc', [X, Y]):
                layerNew.addArcWidth([i['x1'], i['y1']], [i['x2'], i['y2']], -i['curve'], i['width'])
                if parent:
                    layerNew.addRotation(parent['x'], parent['y'], parent['rot'])
                    layerNew.setChangeSide(parent['x'], parent['y'], parent['side'])
                layerNew.setFace()
        # okregi
        if display[1]:
            for i in self.getCircle(layerNumber, dane, oType + 'circle', [X, Y]):
                layerNew.addCircle(i['x'], i['y'], i['r'], i['width'])
                if parent:
                    layerNew.addRotation(parent['x'], parent['y'], parent['rot'])
                    layerNew.setChangeSide(parent['x'], parent['y'], parent['side'])
                layerNew.setFace()
                
                if i['width'] > 0:
                    layerNew.circleCutHole(i['x'], i['y'], i['r'] - i['width'] / 2.)

    def getPaths(self, layerNew, layerNumber, display):
        for i in re.findall(r'\[start\]\(segment\s+\(start\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(end\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(width\s+([0-9\.-]*?)\)\s+\(layer\s+{0}\)(.*?)\[stop\]'.format(layerNumber[1]), self.projektBRD, re.MULTILINE|re.DOTALL):
            x1 = float(i[0])
            y1 = float(i[1]) * (-1)
            x2 = float(i[2])
            y2 = float(i[3]) * (-1)
            width = float(i[4])
            
            if [x1, y1] != [x2, y2]:
                layerNew.addLineWidth(x1, y1, x2, y2, width)
                layerNew.setFace()
    
    def getSilkLayer(self, layerNew, layerNumber, display=[True, True, True, True]):
        self.addStandardShapes(self.projektBRD, layerNew, layerNumber[1], display)
    
    def getSilkLayerModels(self, layerNew, layerNumber):
        self.getElements()
        #
        for i in self.elements:
            if i['side'] == 0:  # bottom side - get mirror
                try:
                    if softLayers[self.databaseType][layerNumber[0]]["mirrorLayer"]:
                        szukanaWarstwa = self.getLayerName(softLayers[self.databaseType][layerNumber[0]]["mirrorLayer"])
                    else:
                        szukanaWarstwa = layerNumber[1]
                except:
                    szukanaWarstwa = layerNumber[1]
            else:
                szukanaWarstwa = layerNumber[1]
            ####
            self.addStandardShapes(i['data'], layerNew, szukanaWarstwa, parent=i)
        
    def getElements(self):
        if len(self.elements) == 0:
            for i in re.findall(r'\[start\]\(module(.+?)\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL):
                [x, y, rot] = re.search(r'\(at\s+([0-9\.-]*?)\s+([0-9\.-]*?)(\s+[0-9\.-]*?|)\)', i).groups()
                layer = re.search(r'\(layer\s+(.+?)\)', i).groups()[0]
                
                name = re.search(r'\(fp_text reference\s+(.*)', i, re.MULTILINE|re.DOTALL).groups()[0]
                name = re.search(r'^(".+?"|.+?)\s', name).groups()[0].replace('"', '')
                value = re.search(r'\(fp_text value\s+(.*)', i, re.MULTILINE|re.DOTALL).groups()[0]
                value  = re.search(r'^(".+?"|.+?)\s', value).groups()[0].replace('"', '')
                
                x = float(x)
                y = float(y) * (-1)
                
                package = re.search(r'\s+(.+?)\(layer', i).groups()[0]
                package = re.sub('locked|placed|pla', '', package).split(':')[-1]
                package = package.replace('"', '').strip()
                ##3D package from KiCad
                #try:
                    #package3D = re.search(r'\(model\s+(.+?).wrl', i).groups()[0]
                    #if package3D and self.partExist(os.path.basename(package3D), "", False):
                        #package = os.path.basename(package3D)
                #except:
                    #pass
                ##
                library = package
                #
                if rot == '':
                    rot = 0.0
                else:
                    rot = float(rot)
                
                if (self.databaseType == "kicad" and self.spisWarstw[layer] == 15) or (self.databaseType == "kicad_v4" and self.spisWarstw[layer] == 0):  # top
                    side = 1  # TOP
                    mirror = 'None'
                else:
                    side = 0  # BOTTOM
                    #rot = (rot + 180) * (-1)
                    if rot < 180:
                        rot = (180 - rot)
                    else:
                        rot = int(rot % 180) * (-1)
                    mirror = 'Local Y axis'
                
                self.elements.append({'name': name, 'library': library, 'package': package, 'value': value, 'x': x, 'y': y, 'rot': rot, 'side': side, 'data': i, 'mirror': mirror})
    
    def getParts(self):
        self.getElements()
        parts = []
        ###########
        for i in self.elements:
            if i['side'] == 1:
                side = "TOP"
            else:
                side = "BOTTOM"
            ###########
            # textReferencere
            textReferencere = re.search(r'\(fp_text reference\s+(.*)', i['data'], re.MULTILINE|re.DOTALL).groups()[0]
            [tr_x, tr_y, tr_rot] = re.search(r'\(at\s+([0-9\.-]*?)\s+([0-9\.-]*?)(\s+[0-9\.-]*?|)\)', textReferencere).groups()
            tr_layer = re.search(r'\(layer\s+(.+?)\)', textReferencere).groups()[0]
            tr_fontSize = re.search(r'\(font\s+(\(size\s+(.+?) .+?\)|)', textReferencere).groups()[0]
            tr_visibility = re.search(r'\(layer\s+.+?\)\s+(hide|)', textReferencere).groups()[0]
            tr_value = re.search(r'^(".+?"|.+?)\s', textReferencere).groups()[0].replace('"', '')
            #
            tr_x = float(tr_x)
            tr_y = float(tr_y) * (-1)
            if tr_rot == '':
                tr_rot = i['rot']
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
            
            EL_Name = [tr_value, tr_x + i['x'], tr_y + i['y'], tr_fontSize, tr_rot, side, "center", False, i['mirror'], '', True]
            ###########
            # textValue
            textValue = re.search(r'\(fp_text value\s+(.*)', i['data'], re.MULTILINE|re.DOTALL).groups()[0]
            [tv_x, tv_y, tv_rot] = re.search(r'\(at\s+([0-9\.-]*?)\s+([0-9\.-]*?)(\s+[0-9\.-]*?|)\)', textValue).groups()
            tv_layer = re.search(r'\(layer\s+(.+?)\)', textValue).groups()[0]
            tv_fontSize = re.search(r'\(font\s+(\(size\s+(.+?) .+?\)|)', textValue).groups()[0]
            tv_visibility = re.search(r'\(layer\s+.+?\)\s+(hide|)', textValue).groups()[0]
            tv_value  = re.search(r'^(".+?"|.+?)\s', textValue).groups()[0].replace('"', '')
            #
            tv_x = float(tv_x)
            tv_y = float(tv_y) * (-1)
            if tv_rot == '':
                tv_rot = i['rot']
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
            
            EL_Value = [tv_value, tv_x + i['x'], tv_y + i['y'], tv_fontSize, tv_rot, side, "center", False, i['mirror'], '', tv_visibility]
            ###########
            ###########
            newPart = [[i['name'], i['package'], i['value'], i['x'], i['y'], i['rot'], side, i['library']], EL_Name, EL_Value]
            parts.append(newPart)
        ###########
        return parts
    
    
    #def getParts(self, koloroweElemnty, adjustParts, groupParts, partMinX, partMinY, partMinZ):
        #PCB_ER = []
        ##
        #for i in re.findall(r'\[start\]\(module(.+?)\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL):
            #[x, y, rot] = re.search(r'\(at\s+([0-9\.-]*?)\s+([0-9\.-]*?)(\s+[0-9\.-]*?|)\)', i).groups()
            #layer = re.search(r'\(layer\s+(.+?)\)', i).groups()[0]
            ###
            ##package = re.search(r'\s+(".+?"|.+?)\s+\(layer', i).groups()[0]
            ##package = re.search(r'\s+(".+?"|.+?)([\s+locked\s+|\s+]+)\(layer', i).groups()[0]
            ##if ':' in package:
                ##package = package.replace('"', '').split(':')[-1]
            ##else:
                ##if '"' in package:
                    ##package = package.replace('"', '')
                ##else:
                    ##package = package
            #package = re.search(r'\s+(.+?)\(layer', i).groups()[0]
            #package = re.sub('locked|placed|pla', '', package).split(':')[-1]
            #package = package.replace('"', '').strip()
            ##3D package from KiCad
            #try:
                #package3D = re.search(r'\(model\s+(.+?).wrl', i).groups()[0]
                #if package3D and self.partExist(os.path.basename(package3D), "", False):
                    #package = os.path.basename(package3D)
            #except:
                #pass
            ##
            #library = package
            
            #x = float(x)
            #y = float(y) * (-1)
            #if rot == '':
                #rot = 0.0
            #else:
                #rot = float(rot)
            
            #if self.spisWarstw[layer] == 15:  # top
                #side = "TOP"
                #mirror = 'None'
            #else:
                #side = "BOTTOM"
                ##rot = (rot + 180) * (-1)
                #if rot < 180:
                    #rot = (180 - rot)
                #else:
                    #rot = int(rot % 180) * (-1)
                #mirror = 'Local Y axis'
            #####
            ## textReferencere
            #textReferencere = re.search(r'\(fp_text reference\s+(.*)', i, re.MULTILINE|re.DOTALL).groups()[0]
            #[tr_x, tr_y, tr_rot] = re.search(r'\(at\s+([0-9\.-]*?)\s+([0-9\.-]*?)(\s+[0-9\.-]*?|)\)', textReferencere).groups()
            #tr_layer = re.search(r'\(layer\s+(.+?)\)', textReferencere).groups()[0]
            #tr_fontSize = re.search(r'\(font\s+(\(size\s+(.+?) .+?\)|)', textReferencere).groups()[0]
            #tr_visibility = re.search(r'\(layer\s+.+?\)\s+(hide|)', textReferencere).groups()[0]
            #tr_value = re.search(r'^(".+?"|.+?)\s', textReferencere).groups()[0].replace('"', '')
            ##
            #tr_x = float(tr_x)
            #tr_y = float(tr_y) * (-1)
            #if tr_rot == '':
                #tr_rot = rot
            #else:
                #tr_rot = float(tr_rot)
            
            #if tr_fontSize == '':
                #tr_fontSize = 0.7
            #else:
                #tr_fontSize = float(tr_fontSize.split()[1])
            
            #if tr_visibility == 'hide':
                #tr_visibility = False
            #else:
                #tr_visibility = True
            
            #EL_Name = [tr_value, tr_x + x, tr_y + y, tr_fontSize, tr_rot, side, "center", False, mirror, '', True]
            #####
            ## textValue
            #textValue = re.search(r'\(fp_text value\s+(.*)', i, re.MULTILINE|re.DOTALL).groups()[0]
            #[tv_x, tv_y, tv_rot] = re.search(r'\(at\s+([0-9\.-]*?)\s+([0-9\.-]*?)(\s+[0-9\.-]*?|)\)', textValue).groups()
            #tv_layer = re.search(r'\(layer\s+(.+?)\)', textValue).groups()[0]
            #tv_fontSize = re.search(r'\(font\s+(\(size\s+(.+?) .+?\)|)', textValue).groups()[0]
            #tv_visibility = re.search(r'\(layer\s+.+?\)\s+(hide|)', textValue).groups()[0]
            #tv_value  = re.search(r'^(".+?"|.+?)\s', textValue).groups()[0].replace('"', '')
            ##
            #tv_x = float(tv_x)
            #tv_y = float(tv_y) * (-1)
            #if tv_rot == '':
                #tv_rot = rot
            #else:
                #tv_rot = float(tv_rot)
            
            #if tv_fontSize == '':
                #tv_fontSize = 0.7
            #else:
                #tv_fontSize = float(tv_fontSize.split()[1])
            
            #if tv_visibility == 'hide':
                #tv_visibility = False
            #else:
                #tv_visibility = True
            
            #EL_Value = [tv_value, tv_x + x, tv_y + y, tv_fontSize, tv_rot, side, "center", False, mirror, '', tv_visibility]
            ##
            #newPart = [[EL_Name[0], package, EL_Value[0], x, y, rot, side, library], EL_Name, EL_Value]
            #wyn = self.addPart(newPart, koloroweElemnty, adjustParts, groupParts, partMinX, partMinY, partMinZ)
            ##
            #if wyn[0] == 'Error':  # lista brakujacych elementow
                #partNameTXT = partNameTXT_label = self.generateNewLabel(EL_Name[0])
                #if isinstance(partNameTXT, str):
                    #partNameTXT = unicodedata.normalize('NFKD', partNameTXT).encode('ascii', 'ignore')
                
                #PCB_ER.append([partNameTXT, package, EL_Value[0], library])
        #####
        #return PCB_ER
