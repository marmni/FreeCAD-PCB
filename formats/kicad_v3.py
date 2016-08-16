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
from command.PCBgroups import *


def setProjectFile(filename):
    projektBRD = __builtin__.open(filename, "r").read()[1:]
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


class KiCadv3_PCB(mainPCB):
    def __init__(self, filename):
        mainPCB.__init__(self, None)
        
        self.dialogMAIN = dialogMAIN(filename)
        self.databaseType = "kicad"
        self.spisWarstw = {}
        self.borderLayerNumber = 28

    def setProject(self, filename):
        self.projektBRD = setProjectFile(filename)
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
                wymiary.append([x2, y2, x1, y1, x3, y3])
            else:
                wymiary.append([x1, y1, x2, y2, x3, y3])
        #
        return wymiary
    
    def getParts(self, koloroweElemnty, adjustParts, groupParts, partMinX, partMinY, partMinZ):
        self.__SQL__.reloadList()
        #
        PCB_ER = []
        #
        for i in re.findall(r'\[start\]\(module(.+?)\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL):
            [x, y, rot] = re.search(r'\(at\s+([0-9\.-]*?)\s+([0-9\.-]*?)(\s+[0-9\.-]*?|)\)', i).groups()
            layer = re.search(r'\(layer\s+(.+?)\)', i).groups()[0]
            ##
            #package = re.search(r'\s+(".+?"|.+?)\s+\(layer', i).groups()[0]
            #package = re.search(r'\s+(".+?"|.+?)([\s+locked\s+|\s+]+)\(layer', i).groups()[0]
            #if ':' in package:
                #package = package.replace('"', '').split(':')[-1]
            #else:
                #if '"' in package:
                    #package = package.replace('"', '')
                #else:
                    #package = package
            package = re.search(r'\s+(.+?)\(layer', i).groups()[0]
            package = re.sub('locked|placed|pla', '', package).split(':')[-1]
            package = package.replace('"', '').strip()
            #
            library = package
            
            x = float(x)
            y = float(y) * (-1)
            if rot == '':
                rot = 0.0
            else:
                rot = float(rot)
            
            if self.spisWarstw[layer] == 15:  # top
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
    
    def getGlue(self, layerNumber):
        layer = re.escape(self.getLayerName(layerNumber))
        glue = {}
        # lines
        for i in self.getLine(layer, self.projektBRD, "gr_line"):
            if not i['width'] in glue.keys():
                glue[i['width']] = []
            
            glue[i['width']].append(['line', i['x1'], i['y1'], i['x2'], i['y2']])
        # circles
        for i in self.getCircle(layer, self.projektBRD, "gr_circle"):
            if not i['width'] in glue.keys():
                glue[i['width']] = []
            
            glue[i['width']].append(['circle', i['x'], i['y'], i['r']])
        # arcs
        for i in self.getArc(layer, self.projektBRD, "gr_arc"):
            if not i['width'] in glue.keys():
                glue[i['width']] = []
            
            glue[i['width']].append(['arc', i['x2'], i['y2'], i['x1'], i['y1'], i['curve'], True])
        ##
        return glue
    
    def getPaths(self, layerNumber):
        wires = []
        signal = []
        warst = re.escape(self.getLayerName(layerNumber))
        #
        for i in re.findall(r'\[start\]\(segment\s+\(start\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(end\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(width\s+([0-9\.-]*?)\)\s+\(layer\s+{0}\)(.*?)\[stop\]'.format(warst), self.projektBRD, re.MULTILINE|re.DOTALL):
            x1 = float(i[0])
            y1 = float(i[1]) * (-1)
            x2 = float(i[2])
            y2 = float(i[3]) * (-1)
            width = float(i[4])
            
            if [x1, y1] != [x2, y2]:
                wires.append(['line', x1, y1, x2, y2, width])
        ####
        wires.append(signal)
        return wires
    
    def getPads(self, doc, layerNumber, grp, layerName, layerColor, defHeight):
        layerName = "{0}_{1}".format(layerName, layerNumber)
        #layerSide = PCBlayers[softLayers["kicad"][layerNumber][1]][0]
        layerType = PCBlayers[softLayers[self.databaseType][layerNumber][1]][3]
        ####
        layerS = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", layerName)
        layerNew = layerSilkObject(layerS, layerType)
        layerNew.holes = self.showHoles()
        layerNew.defHeight = defHeight
        ####
        # via
        via_drill = float(self.getSettings('via_drill'))

        for i in re.findall(r'\(via\s+\(at\s+(.*?)\s+(.*?)\)\s+\(size\s+(.*?)\)\s+(\(drill\s+(.*?)\)|)', self.projektBRD):
            x = float(i[0])
            y = float(i[1]) * (-1)
            diameter = float(i[2]) / 2.

            if i[4] == '':
                drill = via_drill / 2.
            else:
                drill = float(i[4]) / 2.
            
            layerNew.createObject()
            layerNew.addCircle(x, y, diameter)
            layerNew.setFace()
        # pad
        for i in re.findall(r'\[start\]\(module(.+?)\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL):
            [X1, Y1, ROT] = re.search(r'\(at\s+([0-9\.-]*?)\s+([0-9\.-]*?)(\s+[0-9\.-]*?|)\)', i).groups()
            #
            X1 = float(X1)
            Y1 = float(Y1) * (-1)
            if ROT == '':
                ROT = 0.0
            else:
                ROT = float(ROT)
            #
            for j in self.getPadsList(i):
                pType = j['padType']
                pShape = j['padShape']
                xs = j['x'] + X1
                ys = j['y'] + Y1
                dx = j['dx']
                dy = j['dy']
                hType = j['holeType']
                drill = j['r']
                xOF = j['xOF']
                yOF = j['yOF']
                numerWarstwy = j['layers'].split(' ')
                
                rot_2 = j['rot']
                if ROT != 0:
                    rot_2 -= ROT
                #
                # kicad_pcb v3 TOP:         self.getLayerName(15) in numerWarstwy and layerNumber == 19
                # kicad_pcb v3 BOTTOM:      self.getLayerName(0) in numerWarstwy and layerNumber == 18
                # kicad_pcb v4 TOP:         self.getLayerName(0) in numerWarstwy and layerNumber == 108
                # kicad_pcb v4 BOTTOM:      self.getLayerName(31) in numerWarstwy and layerNumber == 107
                dodaj = False
                if (self.getLayerName(15) in numerWarstwy and layerNumber == 19) or (self.getLayerName(0) in numerWarstwy and layerNumber == 108):
                    dodaj = True
                elif (self.getLayerName(0) in numerWarstwy and layerNumber == 18) or (self.getLayerName(31) in numerWarstwy and layerNumber == 107):
                    dodaj = True
                elif '*.Cu' in numerWarstwy:
                    dodaj = True
                #####
                #####
                if dodaj:
                    if pShape == 'rect':
                        x1 = xs - dx / 2. + xOF
                        y1 = ys - dy / 2. + yOF
                        x2 = xs + dx / 2. + xOF
                        y2 = ys + dy / 2. + yOF
                        
                        layerNew.createObject()
                        layerNew.addRectangle(x1, y1, x2, y2)
                        layerNew.addRotation(xs, ys, rot_2)
                        layerNew.addRotation(X1, Y1, ROT)
                        layerNew.setFace()
                    elif pShape == 'trapezoid':
                        if j[8].strip() == '':
                            xRD = 0
                            yRD = 0
                        else:
                            rect_delta = re.findall(r'\(rect_delta ([-0-9\.]*?) ([-0-9\.]*?) \)', j[8].strip())[0]
                            yRD = float(rect_delta[0]) / 2.
                            xRD = float(rect_delta[1]) / 2.
                        
                        x1 = xs - dx / 2. + xOF
                        y1 = ys - dy / 2. + yOF
                        x2 = xs + dx / 2. + xOF
                        y2 = ys + dy / 2. + yOF
                        
                        layerNew.createObject()
                        layerNew.addTrapeze([x1, y1], [x2, y2], xRD, yRD)
                        layerNew.addRotation(xs, ys, rot_2)
                        layerNew.addRotation(X1, Y1, ROT)
                        layerNew.setFace()
                    elif pShape == 'oval':
                        if dx == dy:
                            layerNew.createObject()
                            layerNew.addCircle(xs + xOF, ys + yOF, dx / 2.)
                            layerNew.addRotation(xs, ys, rot_2)
                            layerNew.addRotation(X1, Y1, ROT)
                            layerNew.setFace()
                        else:
                            layerNew.createObject()
                            layerNew.addPadLong(xs + xOF, ys + yOF, dx / 2., dy / 2., 100)
                            layerNew.addRotation(xs, ys, rot_2)
                            layerNew.addRotation(X1, Y1, ROT)
                            layerNew.setFace()
                    elif pShape == 'circle':
                        layerNew.createObject()
                        layerNew.addCircle(xs, ys, dx / 2.)
                        layerNew.addRotation(xs, ys, rot_2)
                        layerNew.addRotation(X1, Y1, ROT)
                        layerNew.setFace()
        ###
        layerNew.generuj(layerS)
        layerNew.updatePosition_Z(layerS)
        viewProviderLayerSilkObject(layerS.ViewObject)
        layerS.ViewObject.ShapeColor = layerColor
        grp.addObject(layerS)
        #
        doc.recompute()
    
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
                    data = re.search(r'\(drill(\s+oval\s+|\s+)(.*?)(\s+[-0-9\.]*?|)(\s+\(offset\s+(.*?)\s+(.*?)\)|)\)', j)
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
                    
                    if pType == 'smd' or data == None:
                        drill = 0.0
                        hType = None
                        [xOF, yOF] = [0.0, 0.0]
                    else:
                        data = data.groups()
                        
                        hType = data[0]
                        if hType.strip() == '':
                            hType = 'circle'
                        
                        drill = float(data[1]) / 2.0
                        
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


    def getHoles(self, types):
        ''' holes/vias '''
        holes = []
        ####
        # vias
        if types['V']:
            via_drill = float(self.getSettings('via_drill'))
            
            for i in re.findall(r'\(via\s+\(at\s+(.*?)\s+(.*?)\)\s+\(size\s+.*?\)\s+(\(drill\s+(.*?)\)|)', self.projektBRD):
                x = float(i[0])
                y = float(i[1]) * (-1)

                if i[3] == '':
                    drill = via_drill / 2.
                else:
                    drill = float(i[3]) / 2.
                    
                holes.append([x, y, drill])
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
                        [xR, yR] = self.obrocPunkt([j['x'], j['y']], [X1, Y1], ROT)
                        holes.append([xR, yR, j['r']])
        ####
        return holes
    
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

    def getPCB(self):
        PCB = []
        wygenerujPada = True
        ###
        # lines
        for i in self.getLine(self.getLayerName(self.borderLayerNumber), self.projektBRD, 'gr_line'):
            PCB.append(['Line', i['x1'], i['y1'], i['x2'], i['y2']])
        # circles
        for i in self.getCircle(self.getLayerName(self.borderLayerNumber), self.projektBRD, 'gr_circle'):
            PCB.append(['Circle', i['x'], i['y'], i['r']])
        # arc
        for i in self.getArc(self.getLayerName(self.borderLayerNumber), self.projektBRD, 'gr_arc'):
            PCB.append(['Arc', i['x1'], i['y1'], i['x2'], i['y2'], i['curve']])
            wygenerujPada = False
        # obj
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
            
            if self.databaseType == "kicad":
                if self.spisWarstw[layer] == 15:  # top
                    side = 1
                else:
                    side = 0
            else:  # eagle v4
                if self.spisWarstw[layer] == 0:  # top
                    side = 1
                else:
                    side = 0
            
            # line
            for i in self.getLine(lType, j, 'fp_line', [X1, Y1]):
                [x1, y1] = self.obrocPunkt2([i['x1'], i['y1']], [X1, Y1], ROT)
                [x2, y2] = self.obrocPunkt2([i['x2'], i['y2']], [X1, Y1], ROT)
                #if side == 0:
                    #y1 = self.odbijWspolrzedne(y1, Y1)
                    #y2 = self.odbijWspolrzedne(y2, Y1)
                
                PCB.append(['Line', x1, y1, x2, y2])
            # circle
            for i in self.getCircle(lType, j, 'fp_circle', [X1, Y1]):
                [x, y] = self.obrocPunkt2([i['x'], i['y']], [X1, Y1], ROT)
                #if side == 0:
                    #y = self.odbijWspolrzedne(y, Y1)
                
                PCB.append(['Circle', x, y, i['r']])
            # arc
            for i in self.getArc(lType, j, 'fp_arc', [X1, Y1]):
                [x1, y1] = self.obrocPunkt2([i['x1'], i['y1']], [X1, Y1], ROT)
                [x2, y2] = self.obrocPunkt2([i['x2'], i['y2']], [X1, Y1], ROT)
                #if side == 0:
                    #y1 = self.odbijWspolrzedne(y1, Y1)
                    #y2 = self.odbijWspolrzedne(y2, Y1)
                
                curve = i['curve']
                #if side == 0:
                    #curve *= -1
                
                PCB.append(['Arc', x1, y1, x2, y2, curve])
        ###
        return [PCB, wygenerujPada]

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

    def getSilkLayer(self, doc, layerNumber, grp, layerName, layerColor, defHeight):
        layerName = "{0}_{1}".format(layerName, layerNumber)
        layerSide = PCBlayers[softLayers[self.databaseType][layerNumber][1]][0]
        lType = re.escape(self.getLayerName(layerNumber))
        layerType = PCBlayers[softLayers[self.databaseType][layerNumber][1]][3]
        #
        layerS = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", layerName)
        layerNew = layerSilkObject(layerS, layerType)
        layerNew.defHeight = defHeight
        ##
        # lines
        for i in self.getLine(lType, self.projektBRD, 'gr_line'):
            layerNew.createObject()
            layerNew.addLineWidth(i['x1'], i['y1'], i['x2'], i['y2'], i['width'])
            layerNew.setFace()
        # circles
        for i in self.getCircle(lType, self.projektBRD, 'gr_circle'):
            layerNew.createObject()
            layerNew.addCircle(i['x'], i['y'], i['r'], i['width'])
            layerNew.setFace()
        # arc
        for i in self.getArc(lType, self.projektBRD, 'gr_arc'):
            layerNew.createObject()
            layerNew.addArcWidth([i['x1'], i['y1']], [i['x2'], i['y2']], -i['curve'], i['width'])
            layerNew.setFace()
        # obj
        for j in re.findall(r'\[start\]\(module(.+?)\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL):
            [X1, Y1, ROT] = re.search(r'\(at\s+([0-9\.-]*?)\s+([0-9\.-]*?)(\s+[0-9\.-]*?|)\)', j).groups()
            
            X1 = float(X1)
            Y1 = float(Y1) * (-1)
            
            if ROT == '':
                ROT = 0.0
            else:
                ROT = float(ROT)
            
            # line
            for i in self.getLine(lType, j, 'fp_line', [X1, Y1]):
                layerNew.createObject()
                layerNew.addLineWidth(i['x1'], i['y1'], i['x2'], i['y2'], i['width'])
                layerNew.addRotation(X1, Y1, ROT)
                layerNew.setFace()
            # circle
            for i in self.getCircle(lType, j, 'fp_circle', [X1, Y1]):
                layerNew.createObject()
                layerNew.addCircle(i['x'], i['y'], i['r'], i['width'])
                layerNew.addRotation(X1, Y1, ROT)
                layerNew.setFace()
            # arc
            for i in self.getArc(lType, j, 'fp_arc', [X1, Y1]):
                layerNew.createObject()
                layerNew.addArcWidth([i['x1'], i['y1']], [i['x2'], i['y2']], -i['curve'], i['width'])
                layerNew.addRotation(X1, Y1, ROT)
                layerNew.setFace()
        ##
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
                    
                if ID == 47:  # MEASURES
                    self.addDimensions(self.getDimensions(), doc, grp, name, self.dialogMAIN.gruboscPlytki.value(), color)
                elif ID in [20, 21]:
                    self.getSilkLayer(doc, ID, grp, name, color, transp)
                elif ID in [16, 17]:  # glue
                    self.generateGlue(self.getGlue(ID), doc, grp, name, color, ID)
                elif ID in [19, 18]:  # pady
                    self.getPads(doc, ID, grp, name, color, transp)
                elif ID in [0, 15]:  # paths
                    self.generatePaths(self.getPaths(ID), doc, grp, name, color, ID, transp)
                elif ID == 1:  # annotations
                    self.addAnnotations(self.getAnnotations(), doc, color)
                elif ID == 106:  # MEASURES
                    self.addDimensions(self.getDimensions(), doc, grp, name, self.dialogMAIN.gruboscPlytki.value(), color)
                else:
                    self.generateConstraintAreas(self.getConstraintAreas(ID), doc, ID, grp_2, name, color, transp)
        ##
        return doc
