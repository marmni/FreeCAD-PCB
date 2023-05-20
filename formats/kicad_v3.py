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
import Part
import re
from math import sqrt, atan2, sin, cos, atan, tan
try:
    import builtins
except:
    import __builtin__ as builtins
#import os
#
from PCBconf import softLayers, spisTekstow
from PCBobjects import *
from formats.dialogMAIN_FORM import dialogMAIN_FORM
from formats.baseModel import baseModel


class dialogMAIN(dialogMAIN_FORM):
    def __init__(self, filename=None, parent=None):
        dialogMAIN_FORM.__init__(self, parent)
        self.databaseType = "kicad"
        #
        self.plytkaPCB_otworyH.setChecked(False)
        self.plytkaPCB_otworyH.setDisabled(True)
        #
        self.projektBRD = self.setProjectFile(filename)
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
            side = "TOP"
            if i[1].startswith("B."):
                side = "BOTTOM"
            dane[int(i[0])] = {"name": i[1], "color": None, "side": side}
        
        ####################
        # EXTRA LAYERS
        ####################
        # measures
        dane[106] = {"name": softLayers[self.databaseType][106]["description"], "color": softLayers[self.databaseType][106]["color"]}
        #  annotations
        dane[905] = {"name": softLayers[self.databaseType][905]["description"], "color": softLayers[self.databaseType][905]["color"], "type": "anno", "number": 0}
        # pad
        dane[107] = {"name": softLayers[self.databaseType][107]["description"], "color": softLayers[self.databaseType][107]["color"]}
        dane[108] = {"name": softLayers[self.databaseType][108]["description"], "color": softLayers[self.databaseType][108]["color"]}
        # ConstraintAreas
        dane[902] = {"name": softLayers[self.databaseType][902]["description"], "color": softLayers[self.databaseType][903]["color"]}
        dane[903] = {"name": softLayers[self.databaseType][903]["description"], "color": softLayers[self.databaseType][904]["color"]}
        dane[904] = {"name": softLayers[self.databaseType][904]["description"], "color": softLayers[self.databaseType][905]["color"]}
        ####################
        ####################
        return dane


class KiCadv3_PCB(baseModel):
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

    def setProject(self):
        self.projektBRD = self.setProjectFile(self.fileName)
        # layers
        layers = re.search(r'\[start\]\(layers(.+?)\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL).group(0)
        for i in re.findall(r'\((.*?) (.*?) .*?\)', layers):
            self.spisWarstw[i[1]] = int(i[0])

    def getSettings(self, paramName):
        try:
            return re.search(r'\({0} (.*?)\)'.format(paramName), self.projektBRD).groups()[0]
        except:
            return False
    
    def getDimensions(self):
        '''
        (dimension (type aligned) (layer "F.Cu") (tstamp 713966d2-586d-40a1-acb1-f49df642ddf4)
            (pts (xy 68.58 170.18) (xy 68.58 152.4))
            (height 10.16)
            (gr_text "17,7800 mm" (at 76.94 161.29 90) (layer "F.Cu") (tstamp 713966d2-586d-40a1-acb1-f49df642ddf4)
              (effects (font (size 1.5 1.5) (thickness 0.3)))
            )
            (format (prefix "") (suffix "") (units 3) (units_format 1) (precision 4))
            (style (thickness 0.2) (arrow_length 1.27) (text_position_mode 0) (extension_height 0.58642) (extension_offset 0.5) keep_text_aligned)
        )
        
        (dimension (type aligned) (layer "F.Cu") (tstamp 35367287-7476-4773-817d-1b88a9bd54c6)
            (pts (xy 60.96 139.7) (xy 81.28 139.7))
            (height -10.16)
            (gr_text "d20,3200 mmf" (at 71.12 127.74) (layer "F.Cu") (tstamp 35367287-7476-4773-817d-1b88a9bd54c6)
              (effects (font (size 1.5 1.5) (thickness 0.3)))
            )
            (format (prefix "d") (suffix "f") (units 3) (units_format 1) (precision 4))
            (style (thickness 1) (arrow_length 2) (text_position_mode 0) (extension_height 0.58642) (extension_offset 0.5) keep_text_aligned)
        )
        
        (dimension 25.4 (width 0.15) (layer Dwgs.User)
            (gr_text "25,400 mm" (at 83.82 133.32) (layer Dwgs.User)
              (effects (font (size 1 1) (thickness 0.15)))
            )
            (feature1 (pts (xy 96.52 142.24) (xy 96.52 134.033579)))
            (feature2 (pts (xy 71.12 142.24) (xy 71.12 134.033579)))
            (crossbar (pts (xy 71.12 134.62) (xy 96.52 134.62)))
            (arrow1a (pts (xy 96.52 134.62) (xy 95.393496 135.206421)))
            (arrow1b (pts (xy 96.52 134.62) (xy 95.393496 134.033579)))
            (arrow2a (pts (xy 71.12 134.62) (xy 72.246504 135.206421)))
            (arrow2b (pts (xy 71.12 134.62) (xy 72.246504 134.033579)))
          )
        '''
        wymiary = []
        #
        for i in re.findall(r'\[start\]\(dimension\s+(.+?)\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL):
            try:
                [x1, y1] = re.search(r'\(feature1\s+\(pts\s+\(xy\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(xy\s+[0-9\.-]*?\s+[0-9\.-]*?\)\)\)', i, re.MULTILINE|re.DOTALL).groups()
                [x2, y2] = re.search(r'\(feature2\s+\(pts\s+\(xy\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(xy\s+[0-9\.-]*?\s+[0-9\.-]*?\)\)\)', i, re.MULTILINE|re.DOTALL).groups()
                [x3, y3] = re.search(r'\(crossbar\s+\(pts\s+\(xy\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(xy\s+[0-9\.-]*?\s+[0-9\.-]*?\)\)\)', i, re.MULTILINE|re.DOTALL).groups()
                lineWidth = float(re.search(r'\(width\s+([0-9\.-]*?)\)', i).groups()[0])
                #
                x1 = float(x1)
                y1 = float(y1) * (-1)
                x2 = float(x2)
                y2 = float(y2) * (-1)
                x3 = float(x3)
                y3 = float(y3) * (-1)
                
                if x1 > x2:
                    wymiary.append([x2, y2, x1, y1, x3, y3, '', lineWidth])
                else:
                    wymiary.append([x1, y1, x2, y2, x3, y3, '', lineWidth])
            except:
                try:
                    [x1, y1, x2, y2] = re.search(r'\(pts\s+\(xy\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(xy\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\)', i, re.MULTILINE|re.DOTALL).groups()
                   
                    lineWidth = float(re.search(r'\(style\s+\(thickness\s+([0-9\.-]*?)\)', i).groups()[0])
                    distance = float(re.search(r'\(height\s+([0-9\.-]*?)\)', i).groups()[0])
                    #
                    x1 = float(x1)
                    y1 = float(y1)
                    x2 = float(x2)
                    y2 = float(y2)
                    #
                    if x2 - x1 == 0:  # vertical line
                        x3 = x1 + distance * -1
                        y3 = y1
                    else:
                        a = (y2 - y1) / (x2 - x1)
                        #
                        if a == 0:  # horizontal line
                            x3 = x1
                            y3 = y1 + distance
                        else:
                            #alfa = atan(a)
                            alfa = tan(a)
                            #
                            if y1 > y2:
                                x3 = x1 + distance * cos(alfa)
                                y3 = y1 + distance * sin(alfa) * -1
                            else:
                                x3 = x1 + distance * cos(alfa)
                                y3 = y1 + distance * sin(alfa)
                    #
                    y1 *= -1
                    y2 *= -1
                    y3 *= -1
                    #
                    wymiary.append([x1, y1, x2, y2, x3, y3, '', lineWidth])
                
                except Exception as e:
                    print(e)      
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
            
            glue[i['width']].append(['arc', i['xS'], i['yS'], i['xE'], i['yE'], i['curve'], True])
        # rectangles
        for i in self.getRectangle(layerNumber[1], self.projektBRD, "gr_rect"):
            if not i['width'] in glue.keys():
                glue[i['width']] = []
            
            glue[i['width']].append(['line', i['x1'], i['y1'], i['x2'], i['y1']])
            glue[i['width']].append(['line', i['x2'], i['y1'], i['x2'], i['y2']])
            glue[i['width']].append(['line', i['x2'], i['y2'], i['x1'], i['y2']])
            glue[i['width']].append(['line', i['x1'], i['y2'], i['x1'], i['y1']])
        # polygon
        for i in self.generatePolygonData(self.projektBRD, 'gr_poly', layerNumber[1]):
            for j in self.getPolygon(i["points"]):
                if not i['width'] in glue.keys():
                    glue[i['width']] = []
            
                glue[i['width']].append(j)
        ##
        return glue

    def getPads(self, layerNew, layerNumber, layerSide, tentedViasLimit, tentedVias):
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
            
            ##### ##### ##### 
            ##### tented dVias
            if self.filterTentedVias(tentedViasLimit, tentedVias, drill * 2, False):
                continue
            ##### ##### ##### 
            layerNew.addCircle(x, y, diameter / 2.)
            layerNew.setFace()
        
        if not tentedVias:
            # pad
            self.getElements()
            #
            for i in self.elements:
                for j in self.generatePadData(i['dataElement']):
                    if("np_" in j['padType'].lower()):  # mounting holes
                        continue
                    #
                    xs = j['x'] + i['x']
                    ys = j['y'] + i['y']
                    numerWarstwy = j['layers'].split(' ')
                    
                    rot_2 = j['rot']
                    if i['rot'] != 0:
                        rot_2 = -i['rot']
                    
                    # kicad_pcb v3 TOP:         self.getLayerName(15) in numerWarstwy and layerNumber == 107
                    # kicad_pcb v3 BOTTOM:      self.getLayerName(0) in numerWarstwy and layerNumber == 18
                    # kicad_pcb v4 TOP:         self.getLayerName(0) in numerWarstwy and layerNumber == 107
                    # kicad_pcb v4 BOTTOM:      self.getLayerName(31) in numerWarstwy and layerNumber == 108
                    dodaj = False
                    if self.databaseType == "kicad" and ((self.getLayerName(15) in numerWarstwy and layerNumber[0] == 107) or (self.getLayerName(0) in numerWarstwy and layerNumber[0] == 108)):
                        dodaj = True

                    elif '*.Cu' in numerWarstwy:
                        dodaj = True
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
                            layerNew.setChangeSide(i['x'], i['y'], i['side'])
                            layerNew.setFace()
                        elif j['padShape'] == 'circle':
                            layerNew.addCircle(xs + j['xOF'], ys + j['yOF'], j['dx'] / 2.)
                            layerNew.addRotation(xs, ys, rot_2)
                            layerNew.addRotation(i['x'], i['y'], i['rot'])
                            layerNew.setChangeSide(i['x'], i['y'], i['side'])
                            layerNew.setFace()
                        elif j['padShape'] == 'oval':
                            if j['dx'] == j['dy']:
                                layerNew.addCircle(xs + j['xOF'], ys + j['yOF'], j['dx'] / 2.)
                                layerNew.addRotation(xs, ys, rot_2)
                                layerNew.addRotation(i['x'], i['y'], i['rot'])
                                layerNew.setChangeSide(i['x'], i['y'], i['side'])
                                layerNew.setFace()
                            else:
                                layerNew.addPadLong(xs + j['xOF'], ys + j['yOF'], j['dx'] / 2., j['dy'] / 2., 100)
                                layerNew.addRotation(xs, ys, rot_2)
                                layerNew.addRotation(i['x'], i['y'], i['rot'])
                                layerNew.setChangeSide(i['x'], i['y'], i['side'])
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
                            layerNew.setChangeSide(i['x'], i['y'], i['side'])
                            layerNew.setFace()

    def generatePadData(self, model):
        pads = []
        #
        # (pad "1" thru_hole circle (at 0 0) (size 1.524 1.524) (drill 0.762) (layers F&B.Cu *.Mask) (tstamp 7e99d2ed-97f3-4a23-8dd2-09e4c1a87a06))
        # (pad "" np_thru_hole circle (at -7.62 5.08) (size 1.7 1.7) (drill 1.7) (layers "*.Cu" "*.Mask") (tstamp b9bf0a0e-cea8-4b10-a154-eb26345d35a7))
        # (pad 1 thru_hole circle (at 0 0) (size 1.778 1.778) (drill 1.143) (layers *.Cu *.Mask))
        
        dane2 = re.findall(r'\(pad .* ', model, re.MULTILINE|re.DOTALL)
        if len(dane2):
            dane2 = dane2[0].strip().split('(pad')
        
            for j in dane2:
                if j != '':
                    try:
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
                        pads.append({
                            'x': x, 
                            'y': y, 
                            'rot': rot, 
                            'padType': pType, 
                            'padShape': pShape, 
                            'r': drill, 
                            'dx': dx, 
                            'dy': dy, 
                            'holeType': hType, 
                            'xOF': xOF, 
                            'yOF': yOF, 
                            'layers': layers, 
                            'data': j
                        })
                    except Exception as e:
                        print(e)
        #
        return pads

    def getHoles(self, holesObject, types, Hmin, Hmax):
        holesList = []
        
        # vias
        if types['V']:
            via_drill = float(self.getSettings('via_drill'))
            if via_drill:
                for i in re.findall(r'\(via\s+\(at\s+(.*?)\s+(.*?)\)\s+\(size\s+.*?\)\s+(\(drill\s+(.*?)\)|)', self.projektBRD):
                    x = float(i[0])
                    y = float(i[1]) * (-1)

                    if i[3] == '':
                        r = via_drill / 2.
                    else:
                        r = float(i[3]) / 2.
                    
                    holesList = self.addHoleToObject(holesObject, Hmin, Hmax, types['IH'], x, y, r, holesList)
        # pads
        if types['P']:
            for i in re.findall(r'\[start\]\((?:footprint|module)\s+(.+?)\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL):
                [X1, Y1, ROT] = re.search(r'\(at\s+([0-9\.-]*?)\s+([0-9\.-]*?)(\s+[0-9\.-]*?|)\)', i).groups()
                #
                X1 = float(X1)
                Y1 = float(Y1) * (-1)
                if ROT == '':
                    ROT = 0.0
                else:
                    ROT = float(ROT)
                ##
                for j in self.generatePadData(i):
                    if j['padType'] != 'smd' and j['r'] != 0.0:
                        if j['holeType'] == "circle":
                            [xR, yR] = self.obrocPunkt([j['x'], j['y']], [X1, Y1], ROT)
                            r = j['r'] + 0.001
                            
                            holesList = self.addHoleToObject(holesObject, Hmin, Hmax, types['IH'], xR, yR, r, holesList)
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
                                    
                                    holesObject.addGeometry(Part.LineSegment(FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x2, y1, 0)))
                                    holesObject.addGeometry(Part.LineSegment(FreeCAD.Vector(x1, y2, 0), FreeCAD.Vector(x2, y2, 0)))
                                    
                                    [x3, y3] = self.arcMidPoint([x1, y1], [x1, y2], 90)
                                    arc = Part.Arc(FreeCAD.Vector(x1, y1, 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(x1, y2, 0.0))
                                    holesObject.addGeometry(arc)
                                    
                                    [x3, y3] = self.arcMidPoint([x2, y1], [x2, y2], -90)
                                    arc = Part.Arc(FreeCAD.Vector(x2, y1, 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(x2, y2, 0.0))
                                    holesObject.addGeometry(arc)
                                else:
                                    e = (dx * 50 / 100.) / 2.
                                    x1 = x - dx / 2.
                                    y1 = y + dy / 2. - e
                                    x2 = x + dx / 2.
                                    y2 = y - dy / 2. + e
                                    
                                    holesObject.addGeometry(Part.LineSegment(FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x1, y2, 0)))
                                    holesObject.addGeometry(Part.LineSegment(FreeCAD.Vector(x2, y1, 0), FreeCAD.Vector(x2, y2, 0)))
                                    
                                    [x3, y3] = self.arcMidPoint([x1, y1], [x2, y1], -90)
                                    arc = Part.Arc(FreeCAD.Vector(x1, y1, 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(x2, y1, 0.0))
                                    holesObject.addGeometry(arc)
                                    
                                    [x3, y3] = self.arcMidPoint([x1, y2], [x2, y2], 90)
                                    arc = Part.Arc(FreeCAD.Vector(x1, y2, 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(x2, y2, 0.0))
                                    holesObject.addGeometry(arc)
    
    def generateLineData(self, x1, y1, x2, y2, width, layer, oType, strokeType, parentCoord):
        try:
            x1 = float(x1)
            y1 = float(y1) * (-1)
            x2 = float(x2)
            y2 = float(y2) * (-1)

            if [x1, y1] == [x2, y2]:
                x2 += 0.01
                y2 += 0.01
            if parentCoord[0] != 0:
                x1 += parentCoord[0]
                x2 += parentCoord[0]
            if parentCoord[1] != 0:
                y1 += parentCoord[1]
                y2 += parentCoord[1]
            
            if width == '':
                width = 0.01
            else:
                width = float(width)
            
            return {
                    'x1': x1,
                    'y1': y1,
                    'x2': x2,
                    'y2': y2,
                    'width': width,
                    'layer': layer,
                    'type': oType,
                    'strokeType': strokeType
            }
        except Exception as e:
            print(e)
    
    def getLine(self, layer, source, oType, parentCoord=[0,0]):
        data = []
        #
        # (gr_line (start 171.45 48.895) (end 171.45 161.29) (layer "Edge.Cuts") (width 0.1) (tstamp 26f08809-b9b6-4e48-9325-b7fd487fd3f4))
        dane1 = re.findall(r'\({1}\s+\(start\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(end\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(layer\s+{0}\)\s+\(width\s+([0-9\.]*?)\)'.format(layer, oType), source, re.MULTILINE|re.DOTALL)
        if len(dane1):
            for i in dane1:
                data.append(self.generateLineData(i[0], i[1], i[2], i[3], i[4], layer, oType, "solid", parentCoord)) 
        else:
            # (gr_line (start 171.45 48.895) (end 171.45 161.29)(stroke (width 0.1) (type solid)) (layer "Edge.Cuts") (tstamp 26f08809-b9b6-4e48-9325-b7fd487fd3f4))
            dane1 = dane1 + re.findall(r'\({1}(\s+locked\s+|\s+)\(start\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(end\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(stroke\s+\(width\s+([0-9\.]*?)\)\s+\(type\s+([a-zA-Z]*)\)\)\s+\(layer\s+{0}\)'.format(layer, oType), source, re.MULTILINE|re.DOTALL)
            for i in dane1:
                data.append(self.generateLineData(i[1], i[2], i[3], i[4], i[5], layer, oType, i[6], parentCoord)) 
        #
        return data
    
    def generateCircleData(self, xs, ys, x1, y1, width, fill, layer, oType, strokeType, parentCoord):
        try:
            xs = float(xs)
            ys = float(ys) * (-1)
            x1 = float(x1)
            y1 = float(y1) * (-1)
            r = sqrt((xs - x1) ** 2 + (ys - y1) ** 2)
            
            if width == '':
                width = 0.01
            else:
                width = float(width)
            
            if parentCoord[0] != 0:
                xs += parentCoord[0]
            if parentCoord[1] != 0:
                ys += parentCoord[1]
            
            return {
                    'x': xs,
                    'y': ys,
                    'r': r,
                    'width': width,
                    'layer': layer,
                    'type': oType,
                    'strokeType': strokeType,
                    'fill': fill,
                }
        except Exception as e:
            print(e)
            
    def getCircle(self, layer, source, oType, parentCoord=[0,0]):
        data = []
        #
        # (gr_circle (center 68.58 139.7) (end 76.2 139.7) (layer Edge.Cuts) (width 0.05))
        dane1 = re.findall(r'\({1}\s+\(center\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(end\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(layer\s+{0}\)(\s+\(width\s+([0-9\.]*?)\)|)(\s+\(tstamp\s+.+?\)|)\)'.format(layer, oType), source, re.MULTILINE|re.DOTALL)
        
        if len(dane1):
            for i in dane1:
                data.append(self.generateCircleData(i[0], i[1], i[2], i[3], i[5], "none", layer, oType, "solid", parentCoord))
        else:
            # (gr_circle (center 162.56 66.04) (end 165.1 68.58)(stroke (width 0.2) (type default)) (fill none) (layer "F.Cu") (tstamp bf3818ca-e060-48cb-957e-401a75320d0e))
            dane1 = re.findall(r'\({1}(\s+locked\s+|\s+)\(center\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(end\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(stroke\s+\(width\s+([0-9\.]*?)\)\s+\(type\s+([a-zA-Z]*)\)\)\s+\(fill\s+([a-zA-Z]*)\)\s+\(layer\s+{0}\)'.format(layer, oType), source, re.MULTILINE|re.DOTALL)

            for i in dane1:
                data.append(self.generateCircleData(i[1], i[2], i[3], i[4], i[5], i[7], layer, oType, i[6], parentCoord))
        #
        return data
    
    
    def generateArcData(self, pointS, pointE, pointM, pointC, curve, width, layer, oType, strokeType, parentCoord):
        try:
            if width.strip() != '':
                width = float(width) 
            else:
                width = 0
            
            [xS, yS] = pointS # start point
            xS = float(xS)
            yS = float(yS)
            #
            [xC, yC] = pointC # arc center
            
            if xC != None and yC != None: # center point + start point + angle
                xC = float(xC)
                yC = float(yC)
            
                curve = float(curve)
                
                [xE, yE] = self.obrocPunkt2([xS, yS], [xC, yC], curve)
                [xM, yM] = self.arcMidPoint([xS, yS], [xE, yE], curve)
            else: # start point + end point + mid point
                [xM, yM] = pointM # middle point
                xM = float(xM)
                yM = float(yM)
                
                [xE, yE] = pointE # end point
                xE = float(xE)
                yE = float(yE)
                
                [xC, yC] = self.arcCenter(xS, yS, xM, yM, xE, yE)
                curve = self.arcGetAngle([xC, yC], [xS, yS], [xE, yE])
            ####
            yE *= -1
            yM *= -1
            yS *= -1
            yC *= -1
            
            if parentCoord[0] != 0:
                xS += parentCoord[0]
                xE += parentCoord[0]
                xM += parentCoord[0]
                xC += parentCoord[0]
            if parentCoord[1] != 0:
                yS += parentCoord[1]
                yE += parentCoord[1]
                yM += parentCoord[1]
                yC += parentCoord[1]
            #
            #print("start = [{0}, {1}] , middle = [{2}, {3}], end = [{4}, {5}] ".format(xS, yS, xM, yM, xE, yE))
            return {
                    'xS': xS,
                    'yS': yS,
                    'xE': xE,
                    'yE': yE,
                    'xM': xM,
                    'yM': yM,
                    'xC': xC,
                    'yC': yC,
                    'curve': curve,
                    'width': width,
                    'layer': layer,
                    'type': oType,
                    'strokeType': strokeType,
                }
        except Exception as e:
            print(e)

    def getArc(self, layer, source, oType, parentCoord=[0,0]):
        data = []
        #
        # (gr_arc (start 78.74 165.1) (end 86.36 165.1) (angle -270) (layer Edge.Cuts) (width 0.05))
        dane1 = re.findall(r'\({1}\s+\(start\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(end\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(angle\s+([0-9\.-]*?)\)\s+\(layer\s+{0}\)(\s+\(width\s+([0-9\.]*?)\)|)(\s+\(tstamp\s+.+?\)|)\)'.format(layer, oType), source, re.MULTILINE|re.DOTALL)
        
        if len(dane1):
            for i in dane1:
                data.append(self.generateArcData([i[2], i[3]], [None, None], [None, None], [i[0], i[1]], i[4], i[6], layer, oType, "default", parentCoord))
        else:
            # (gr_arc (start 91.44 152.4) (mid 114.442776 144.97418) (end 100.123907 164.448278) (stroke (width 0.1) (type default)) (layer "Edge.Cuts") (tstamp 9d6ffd10-7291-4092-96bd-06b7c34444b8))
            dane1 = re.findall(r'\({1}(\s+locked\s+|\s+)\(start\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(mid\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(end\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(stroke\s+\(width\s+([0-9\.]*?)\)\s+\(type\s+([a-zA-Z]*)\)\)\s+\(layer\s+{0}\)'.format(layer, oType), source, re.MULTILINE|re.DOTALL)
        
            if len(dane1):
                for i in dane1:
                    data.append(self.generateArcData([i[1], i[2]], [i[5], i[6]], [i[3], i[4]], [None, None], None, i[7], layer, oType, i[8], parentCoord))
                    pass
        #
        return data
    
    def generateRectangleData(self, x1, y1, x2, y2, width, fill, layer, oType, strokeType, parentCoord):
        x1 = float(x1)
        y1 = float(y1) * (-1)
        x2 = float(x2)
        y2 = float(y2) * (-1)
        width = float(width)
        
        if [x1, y1] == [x2, y2]:
            x2 += 0.01
            y2 += 0.01
        if parentCoord[0] != 0:
            x1 += parentCoord[0]
            x2 += parentCoord[0]
        if parentCoord[1] != 0:
            y1 += parentCoord[1]
            y2 += parentCoord[1]
        
        if width == 0:
            width = 0.01
        
        return {
                'x1': x1,
                'y1': y1,
                'x2': x2,
                'y2': y2,
                'width': width,
                'layer': layer,
                'type': oType,
                "fill": fill,
                'strokeType': strokeType,
            }
    
    def getRectangle(self, layer, source, oType, parentCoord=[0,0]):
        data = []
        #
        # (gr_rect locked (start 101.6 106.68) (end 116.84 116.84) (stroke (width 0.1) (type solid)) (fill solid) (layer "Edge.Cuts") (tstamp 20cd4c63-6b2c-45d2-9152-b9e73c1a089d))
        dane1 = re.findall(r'\({1}(\s+locked\s+|\s+)\(start\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(end\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(stroke\s+\(width\s+([0-9\.]*?)\)\s+\(type\s+([a-zA-Z]*)\)\)\s+\(fill\s+([a-zA-Z]*)\)\s+\(layer\s+{0}\)'.format(layer, oType), source, re.MULTILINE|re.DOTALL)
        
        if len(dane1):
            for i in dane1:
                data.append(self.generateRectangleData(i[1], i[2], i[3], i[4], i[5], i[7], layer, oType, i[6], parentCoord))
        else:
            # (fp_rect (start -1.27 -1.27) (end 8.89 1.27) (layer "F.SilkS") (width 0.12) (fill none) (tstamp bdafabda-3f00-4f9f-ad3b-f8d3c1591c87))
            dane1 = re.findall(r'\({1}(\s+locked\s+|\s+)\(start\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(end\s+([0-9\.-]*?)\s+([0-9\.-]*?)\)\s+\(layer\s+{0}\)\s+\(width\s+([0-9\.]*?)\)\s+\(fill\s+([a-zA-Z]*)\)'.format(layer, oType), source, re.MULTILINE|re.DOTALL)
        
            if len(dane1):
                for i in dane1:
                    data.append(self.generateRectangleData(i[1], i[2], i[3], i[4], i[5], i[6], layer, oType, None, parentCoord))
        #
        return data
    
    def getPCB(self, borderObject):
        # lines
        for i in self.getLine(self.getLayerName(self.borderLayerNumber), self.projektBRD, 'gr_line'):
            borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(i['x1'], i['y1'], 0), FreeCAD.Vector(i['x2'], i['y2'], 0)))
        # circles
        for i in self.getCircle(self.getLayerName(self.borderLayerNumber), self.projektBRD, 'gr_circle'):
            borderObject.addGeometry(Part.Circle(FreeCAD.Vector(i['x'], i['y']), FreeCAD.Vector(0, 0, 1), i['r']))
        # arc
        for i in self.getArc(self.getLayerName(self.borderLayerNumber), self.projektBRD, 'gr_arc'):
            arc = Part.Arc(FreeCAD.Vector(i['xS'], i['yS'], 0.0), FreeCAD.Vector(i['xM'], i['yM'], 0.0), FreeCAD.Vector(i['xE'], i['yE'], 0.0))
            borderObject.addGeometry(arc)
        # rectangles
        for i in self.getRectangle(self.getLayerName(self.borderLayerNumber), self.projektBRD, 'gr_rect'):
            borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(i['x1'], i['y1'], 0), FreeCAD.Vector(i['x2'], i['y1'], 0)))
            borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(i['x2'], i['y1'], 0), FreeCAD.Vector(i['x2'], i['y2'], 0)))
            borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(i['x2'], i['y2'], 0), FreeCAD.Vector(i['x1'], i['y2'], 0)))
            borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(i['x1'], i['y2'], 0), FreeCAD.Vector(i['x1'], i['y1'], 0)))
        ############
        ############
        ###### get Edge.Cuts from objects
        lType = re.escape(self.getLayerName(self.borderLayerNumber))
        
        for j in re.findall(r'\[start\]\((?:footprint|module)\s+(.+?)\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL):
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
                borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x2, y2, 0)))
            # circle
            for i in self.getCircle(lType, j, 'fp_circle', [X1, Y1]):
                [x, y] = self.obrocPunkt2([i['x'], i['y']], [X1, Y1], ROT)

                borderObject.addGeometry(Part.Circle(FreeCAD.Vector(x, y), FreeCAD.Vector(0, 0, 1), i['r']))
            # arc
            for i in self.getArc(lType, j, 'fp_arc', [X1, Y1]):
                [xS, yS] = self.obrocPunkt2([i['xS'], i['yS']], [X1, Y1], ROT)
                [xM, yM] = self.obrocPunkt2([i['xM'], i['yM']], [X1, Y1], ROT)
                [xE, yE] = self.obrocPunkt2([i['xE'], i['yE']], [X1, Y1], ROT)
            
                arc = Part.Arc(FreeCAD.Vector(xS, yS, 0.0), FreeCAD.Vector(xM, yM, 0.0), FreeCAD.Vector(xE, yE, 0.0))
                borderObject.addGeometry(arc)
            # rectangle
            for i in self.getRectangle(self.getLayerName(self.borderLayerNumber), self.projektBRD, 'fp_rect', [X1, Y1]):
                [x1, y1] = self.obrocPunkt2([i['x1'], i['y1']], [X1, Y1], ROT)
                [x2, y2] = self.obrocPunkt2([i['x2'], i['y2']], [X1, Y1], ROT)
            
                borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x2, y1, 0)))
                borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(x2, y1, 0), FreeCAD.Vector(x2, y2, 0)))
                borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(x2, y2, 0), FreeCAD.Vector(x1, y2, 0)))
                borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(x1, y2, 0), FreeCAD.Vector(x1, y1, 0)))
                
    def getLayerName(self, value):
        for i, j in self.spisWarstw.items():
            if j == value:
                return i
        return 'eeeeeefsdfstdgdfgdfghdfgdfgdfgfd'
    
    def getAnnotations(self, data, mode='anno'):
        adnotacje = []
        #
        for i in data:
            try:
                txt = re.search(r'\s(.*?)\s\(at', i).groups(0)[0].replace('"', '').replace('\r\n', '\n').replace('\r', '\n').replace('\\n', '\n')
                [x, y, rot, fix] = re.search(r'\(at\s+([0-9\.-]*?)\s+([0-9\.-]*?)(\s+[0-9\.-]*?|)(\s+[a-z]*?|)\)', i).groups()
                layer = re.search(r'\(layer\s+(.+?)\)', i).groups()[0]
                size = re.search(r'\(size\s+([0-9\.]*?)\s+[0-9\.]*?\)', i).groups()[0]
                justify = re.findall(r'( \(justify .*?\)|)\)', i)[-1].strip()
            except:
                continue
            #
            if rot == '':
                rot = 0.0
            else:
                rot = float(rot)
            
            if layer.startswith('F.') or (self.spisWarstw[layer] in [15, 21] and self.databaseType == "kicad") or (self.spisWarstw[layer] in [0, 33, 35, 37, 39, 40, 41, 42, 43, 44, 45, 47, 49] and self.databaseType == "kicad_v4"):
                side = 'TOP'
            else:
                side = 'BOTTOM'
            
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

            adnotacje.append({
                "text": txt,
                "x": float(x),
                "y": float(y) * (-1),
                "z": 0,
                "size": float(size),
                "rot": rot,
                "side": side,
                "align": align,
                "spin": False,
                "font": 'Proportional',
                "display": True,
                "distance": 1,
                "tracking": 0,
                "mirror": mirror,
                "mode": mode
            })
        #
        return adnotacje
    
    def getNormalAnnotations(self):
        return self.getAnnotations(re.findall(r'\[start\]\(gr_text(.+?)\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL), mode='anno')
        
    def getConstraintAreas(self, layerNumber):
        areas = []
        #
        for i in re.findall(r'\[start\]\(zone\s+.+?\s+\(layer(s\s+|\s+)(["FB\&]*\.Cu["]*)\)(.*?)\s+\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL):
            try:
                #data = re.search(r'\(keepout\s+\(tracks\s+(.*?)\)\s+\(vias\s+(.*?)\)\s+\(copperpour\s+(.*?)\)\)', i[2], re.MULTILINE|re.DOTALL)
                data = re.search(r'\(keepout\s+(.*?)\)\)', i[2], re.DOTALL)
                if data:
                    #info = [j for j in data.groups()]
                    info = {i[0]: i[1] for i in re.findall(r'\(([a-zA-Z]*)\s+([a-zA-Z_]*)', data.groups()[0])}
                else:
                    continue
                #
                layer = i[1].strip()
                #
                #900: ["tKeepout", "tPlaceKeepout"],
                #901: ["bKeepout", "bPlaceKeepout"],
                #902: ["tRouteKeepout", "tRouteKeepout"],
                #903: ["bRouteKeepout", "bRouteKeepout"],
                #904: ["ViaKeepout", "vRouteKeepout"],
                # (keepout (tracks not_allowed) (vias not_allowed) (copperpour allowed))
                # (keepout (tracks not_allowed) (vias not_allowed) (pads allowed) (copperpour allowed) (footprints not_allowed))
                if "F" in layer and "B" in layer:
                    pass
                elif "F" in layer and layerNumber in [901, 903]: # only top/both
                    continue
                elif "B" in layer and layerNumber in [900, 902]: # only bottom/both
                    continue
               
                if layerNumber == 904 and info["vias"] == 'allowed':
                    continue
                elif layerNumber in [902, 903] and info["tracks"] == 'allowed':
                    continue
                elif layerNumber in [900, 901] and info["footprints"] == 'allowed':
                    continue
                #
                points = re.findall(r'\(xy\s+(.*?)\s+(.*?)\)', i[2])
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
            except Exception as e:
                print(e)
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
        elif layerNumber == 905:
            return "annotations"
        else:
            return "silk"

    def getPolygon(self, polygonL, X=0, Y=0):
        poin = []
        for k in range(len(polygonL)):
            x1 = float(polygonL[k][0])
            y1 = float(polygonL[k][1])
            
            try:
                x2 = float(polygonL[k + 1][0])
                y2 = float(polygonL[k + 1][1])
            except:
                x2 = float(polygonL[0][0])
                y2 = float(polygonL[0][1])
            
            if not [x1, y1] == [x2, y2]:  # remove points, only lines
                x1 = x1 + X
                y1 = y1 + Y
                x2 = x2 + X
                y2 = y2 + Y
                
                poin.append(['Line', x1, y1, x2, y2])
        return poin
    
    def generatePolygonData(self, section, oType, layer=False):
        # (gr_poly (pts (xy 69.85 176.53) (xy 58.42 176.53) (xy 59.69 168.91) (xy 63.5 173.99) (xy 67.31 166.37)) (layer F.SilkS) (width 0.1))
        '''
        (gr_poly locked
        (pts
          (xy 109.22 86.36)
          (xy 119.38 86.36)
          (xy 119.38 93.98)
          (xy 109.22 99.06)
          (xy 106.68 88.9)
          (xy 111.76 93.98)
        )
        
        (stroke (width 0.15) (type solid)) (fill solid) (layer "F.Paste") (tstamp db32f21e-4fc8-47a6-8e33-b3bbf2e9fbd9))
        '''
        dataOut = []
        # if layer:
            # data = re.findall(r'\[start\]\({1}\s+(.+?)\s+\(layer\s+{0}\)(.+?)\[stop\]'.format(layer, oType), section, re.MULTILINE|re.DOTALL)
        # else:
            # data = re.findall(r'\[start\]\(gr_poly\s+(.+?)\[stop\]', section, re.MULTILINE|re.DOTALL)
        data = re.findall(r'\[start\]\({0}\s+(.+?)\[stop\]'.format(oType), section, re.MULTILINE|re.DOTALL)
        #
        for i in data:
            if isinstance(i, tuple):
                i = " ".join(i)
            #
            oLayer = re.findall(r'\(layer\s+(.+?)\)', i)[0]
            if layer and oLayer != layer:
                continue
            #
            width = float(re.findall(r'\(width\s+([0-9\.-]*?)\)', i)[0])
            
            fill = re.findall(r'\(fill\s+([a-zA-Z]*?)\)', i)
            if len(fill):
                fill = fill[0]
            else:
                fill = "solid"
            #
            points = []
            pts = re.findall('\(xy\s+[-.0-9]*\s+[-.0-9]*\)', i, re.MULTILINE|re.DOTALL)
            for j in range(len(pts)):
                [cord, x, y] = pts[j].replace(")", "").split(" ")
                x = float(x)
                y = float(y) * -1
                
                points.append([x, y])
            #
            dataOut.append({
                "fill":  fill,
                "width": width,
                "points": points,
            })
        #
        return dataOut

    def addStandardShapes(self, dane, layerNew, layerNumber, display=[True, True, True, True], parent=None):
        if parent:
            X = parent['x']
            Y = parent['y']
            oType = 'fp_'
            Rot = parent['rot']
        else:
            X = 0
            Y = 0
            oType = 'gr_'
            Rot = 0

        # line/arc
        if display[0]:
            for i in self.getLine(layerNumber, dane, oType + 'line', [X, Y]):
                layerNew.addLineWidth(i['x1'], i['y1'], i['x2'], i['y2'], i['width'])
                layerNew.addRotation(X, Y, Rot)
                layerNew.setFace()
                
            for i in self.getArc(layerNumber, dane, oType + 'arc', [X, Y]):
                if layerNew.addArcWidth([i['xS'], i['yS']], [i['xE'], i['yE']], -i['curve'], i['width'], cap='round', p3=[i['xM'], i['yM']]):    
                    layerNew.addRotation(X, Y, Rot)
                    layerNew.setFace()
        # circle
        if display[1]:
            for i in self.getCircle(layerNumber, dane, oType + 'circle', [X, Y]):
                layerNew.addCircle(i['x'], i['y'], i['r'], i['width'])
                layerNew.addRotation(X, Y, Rot)
                layerNew.setFace()
                
                if i['width'] > 0:
                    layerNew.circleCutHole(i['x'], i['y'], i['r'] - i['width'] / 2.)
        # polygon
        if display[3]:
            for i in self.generatePolygonData(dane, oType + 'poly', layerNumber):
                if i["fill"] == "solid":
                    layerNew.addPolygon(self.getPolygon(i["points"], X, Y))
                    layerNew.addRotation(X, Y, Rot)  
                    layerNew.setFace()
                else:
                    for j in self.getPolygon(i["points"], X, Y):
                        layerNew.addLineWidth(j[1], j[2], j[3], j[4], i['width'])
                        layerNew.addRotation(X, Y, Rot)
                        layerNew.setFace()  
        # rectangle
        if display[2]:
            for i in self.getRectangle(layerNumber, dane, oType + 'rect', [X, Y]):
                if i["fill"] == "none":
                    layerNew.addLineWidth(i['x1'], i['y1'], i['x2'], i['y1'], i['width'])
                    layerNew.addRotation(X, Y, Rot)
                    layerNew.setFace()
                    #
                    layerNew.addLineWidth(i['x2'], i['y1'], i['x2'], i['y2'], i['width'])
                    layerNew.addRotation(X, Y, Rot)
                    layerNew.setFace()
                    #
                    layerNew.addLineWidth(i['x2'], i['y2'], i['x1'], i['y2'], i['width'])
                    layerNew.addRotation(X, Y, Rot)
                    layerNew.setFace()
                    #
                    layerNew.addLineWidth(i['x1'], i['y2'], i['x1'], i['y1'], i['width'])
                    layerNew.addRotation(X, Y, Rot)
                    layerNew.setFace()
                else:
                    layerNew.addRectangle(i['x1'], i['y1'], i['x2'], i['y2'])
                    layerNew.addRotation(X, Y, Rot)
                    layerNew.setFace()

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
        self.addStandardShapes(self.projektBRD, layerNew, layerNumber[1], [True, True, True, True])
    
    def getSilkLayerModels(self, layerNew, layerNumber):
        self.getElements()
        #
        for i in self.elements:
            if i['side'] == 0:  # bottom side - get mirror
                try:
                    print(softLayers[self.databaseType][layerNumber[0]]["mirrorLayer"])
                    
                    if softLayers[self.databaseType][layerNumber[0]]["mirrorLayer"]:
                        szukanaWarstwa = self.getLayerName(softLayers[self.databaseType][layerNumber[0]]["mirrorLayer"])
                    else:
                        szukanaWarstwa = layerNumber[1]
                except:
                    szukanaWarstwa = layerNumber[1]
            else:
                szukanaWarstwa = layerNumber[1]
            ####
            self.addStandardShapes(i['dataElement'], layerNew, szukanaWarstwa, parent=i)
        
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
                ########
                package = re.search(r'\s+(.+?)\(layer', i).groups()[0]
                package = re.sub('locked|placed|pla', '', package).split(':')[-1]
                package = package.replace('"', '').strip()
                # use different 3D model for current package
                userText = re.findall(r'\(fp_text user\s+(.*)\s+\(at\s+', i)
                
                if any(k for k in ['FREECAD', 'FCM', 'FCMV'] if k in "__".join(userText)):
                    for j in userText:
                        if any(k for k in ['FREECAD', 'FCM', 'FCMV'] if k in j):
                            [userTextName, userTextValue] = j.replace('"', '').strip().split("=")
                            #
                            if userTextValue.strip() == "":
                                FreeCAD.Console.PrintWarning(spisTekstow["loadModelEmptyAttributeInfo"].format(name))
                            elif (userTextName == 'FREECAD' and userTextValue.strip().startswith("--")) or userTextName == 'FCMV':
                                pathAttribute = userTextValue.strip()
                                
                                if not pathAttribute.startswith("--"):
                                    pathAttribute = "--" + pathAttribute
                            elif userTextName in ['FREECAD', 'FCM']:
                                FreeCAD.Console.PrintWarning(spisTekstow["loadModelImportDifferentPackageInfo"].format(name, userTextValue.strip(), package))
                                package = userTextValue.strip()
                ########
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
                
                self.elements.append({
                    'name': name, 
                    'library': library, 
                    'package': package, 
                    'value': value, 
                    'pathAttribute': pathAttribute,
                    'x': x, 
                    'y': y, 
                    'rot': rot,
                    'side': side, 
                    'dataElement': i, 
                    'mirror': mirror
                })
    
    def getParts(self):
        self.getElements()
        parts = []
        ###########
        for i in self.elements:
            if i['side'] == 1:
                i['side'] = "TOP"
            else:
                i['side'] = "BOTTOM"
            ####################################
            dataName = self.getAnnotations(re.findall(r'\(fp_text reference(.+?)\)\n\s+\)\n\s+\(', i['dataElement'], re.MULTILINE|re.DOTALL), mode='param')
            i['EL_Name'] = dataName[0]
            i['EL_Name']["text"] = "NAME"
            i['EL_Name']["x"] = i['EL_Name']["x"] + i["x"]
            i['EL_Name']["y"] = i['EL_Name']["y"] + i["y"]
            i['EL_Name']["rot"] = i['EL_Name']["rot"] - i["rot"]
            ####################################
            dataValue = self.getAnnotations(re.findall(r'\(fp_text value(.+?)\)\n\s+\)\n\s+\(', i['dataElement'], re.MULTILINE|re.DOTALL), mode='param')
            i['EL_Value'] = dataValue[0]
            i['EL_Value']["text"] = "VALUE"
            i['EL_Value']["x"] = i['EL_Value']["x"] + i["x"]
            i['EL_Value']["y"] = i['EL_Value']["y"] + i["y"]
            i['EL_Value']["rot"] = i['EL_Value']["rot"] - i["rot"]
            ####################################
            parts.append(i)
        #
        return parts
