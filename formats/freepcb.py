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
import ConfigParser

from PCBconf import PCBlayers, softLayers
from PCBobjects import *
from formats.PCBmainForms import *
from command.PCBgroups import *


class dialogMAIN(dialogMAIN_FORM):
    def __init__(self, filename=None, parent=None):
        dialogMAIN_FORM.__init__(self, parent)
        self.databaseType = "freepcb"
        #
        #
        self.plytkaPCB_otworyH.setChecked(False)
        self.plytkaPCB_otworyH.setDisabled(True)
        #
        self.generateLayers()
        self.spisWarstw.sortItems(1)


class FreePCB(mainPCB):
    def __init__(self):
        mainPCB.__init__(self, None)
        
        self.projektBRD_CP = None
        self.dialogMAIN = dialogMAIN()
        self.databaseType = "freepcb"
        self.parts = {}
        self.mnoznik = 1. / 1000000.

    def setProject(self, filename):
        self.projektBRD_CP = ConfigParser.RawConfigParser()
        self.projektBRD_CP.read(filename)
        ##
        self.projektBRD = builtins.open(filename, "r").read().replace("\r\n", "\n").replace("\r", "\n")
        ##
        self.parts = {}
        
        partsList = re.search(r'\[parts\](.*?)\[', self.projektBRD, re.DOTALL).groups()[0].strip().split('part: ')
        for i in partsList:
            if i.strip() != '':
                part = i.strip()
                partName = re.search(r'^(.*?)\n', part).groups()[0]
                partPos = re.search(r'pos: (.*?) (.*?) (.*?) (.*?) (.*?)', part).groups()
                ref_text = re.search(r'ref_text: (.*?) .*? (.*?) (.*?) (.*?)\n', part).groups()

                self.parts[partName] = {}
                self.parts[partName]['pos'] = [float(partPos[0]) * self.mnoznik, float(partPos[1]) * self.mnoznik, float(partPos[3]) * (-1), int(partPos[2])]
                self.parts[partName]['shape'] = re.search(r'shape: "(.*?)"', part).groups()[0]
                self.parts[partName]['package'] = re.search(r'package: "(.*?)"', part).groups()[0]
                self.parts[partName]['ref_text'] = [float(ref_text[2]) * self.mnoznik, float(ref_text[3]) * self.mnoznik, float(ref_text[1]) * (-1), float(ref_text[0]) * self.mnoznik]
        #
        #footprints = {}
        #holesList = {}

        footprintsList = re.search(r'\[footprints\](.*?)\[', self.projektBRD, re.DOTALL).groups()[0].strip().split('name: ')
        for i in footprintsList:
            if i.strip() != '':
                dane = i.strip()
                footprintsListName = re.search(r'^"(.*?)"\n', dane).groups()[0]
                
                try:
                    if re.search(r'units: (.*)', dane).groups()[0] == "MIL":  # mils
                        mnoznik = 0.0254
                    else:
                        mnoznik = 1. / 1000000.
                except:
                    mnoznik = 1. / 1000000.

                ############### HOLES/PADS
                holes = []
                pads = []
                
                dane1 = i.split('n_pins:')[1].split('pin: ')
                for j in dane1:
                    param_pin = re.findall(r'".*" (.+?) (.+?) (.+?) (.*)', j.strip())
                    
                    if param_pin != []:
                        param_pin = param_pin[0]
                        addHole = re.findall(r'[top_pad|inner_pad|bottom_pad]: .+? .+? .+? .+?', j.strip())

                        try:
                            param_pad = re.search(r'.+?: (.+?) (.+?) (.+?) (.+?) (.*)', j.strip()).groups()
                            roudness = float(param_pad[4]) * mnoznik
                        except:
                            param_pad = re.search(r'.+?: (.+?) (.+?) (.+?) (.+?)', j.strip()).groups()
                            roudness = 0
                        
                        pinHD = float(param_pin[0]) * mnoznik / 2.
                        pinX = float(param_pin[1]) * mnoznik
                        pinY = float(param_pin[2]) * mnoznik
                        pinA = float(param_pin[3]) * (-1)
                        padS = param_pad[0]
                        padW = float(param_pad[1]) * mnoznik / 2.
                        padH = float(param_pad[2]) * mnoznik
                        
                        if len(addHole) > 2 and pinHD:
                            holes.append([pinX, pinY, pinHD])
                        pads.append([padS, padW, pinX, pinY, pinA, pinHD, padH, roudness])
                #
                for k in self.parts.keys():
                    if self.parts[k]["shape"] == footprintsListName:
                        if len(holes):
                            self.parts[k]["holes"] = holes
                        if len(pads):
                            self.parts[k]["pads"] = pads
                ############### POLYLINE
                danePolyline = re.split(r'(outline_polyline:|n_pins:)', dane)
                danePolyline = danePolyline[1:danePolyline.index('n_pins:')]
                danePolyline = [o for o in danePolyline if o != "outline_polyline:"]
                linieTop = []
                #danePolyline = re.search(r'outline_polyline: ([\S\D]*) .*:', dane[0]).groups()[0].split("\r\n")
                for param in danePolyline:
                    #param = param.split("\r\n")
                    param = param.split("\n")
                    pierwszy = re.search(r' (.*) (.*) (.*)', param[0]).groups()
                    width = float(pierwszy[0]) * mnoznik
                    param = param[1:-1]
                    p = False
                    
                    if param[-1].strip().startswith('close_polyline'):
                        param = param[:-1]
                    
                    for pp in range(len(param)):
                        if param[pp].strip().startswith("next_corner:"):
                            wsp = re.search(r'next_corner: (.*) (.*) (.*)', param[pp].strip()).groups()
                            typeC = wsp[2]
                            
                            if not p:
                                linieTop.append([typeC, float(pierwszy[1]) * mnoznik, float(pierwszy[2]) * mnoznik, float(wsp[0]) * mnoznik, float(wsp[1]) * mnoznik, width])
                                p = True
                            else:
                                wsp_P = re.search(r'next_corner: (.*) (.*) (.*)', param[pp - 1].strip()).groups()
                                linieTop.append([typeC, float(wsp_P[0]) * mnoznik, float(wsp_P[1]) * mnoznik, float(wsp[0]) * mnoznik, float(wsp[1]) * mnoznik, width])
                       
                                if pp == len(param) - 1:
                                    linieTop.append([typeC, float(wsp[0]) * mnoznik, float(wsp[1]) * mnoznik, float(pierwszy[1]) * mnoznik, float(pierwszy[2]) * mnoznik, width])
                        elif param[pp].strip().startswith("close_polyline:"):
                            wsp = re.search(r'close_polyline: (.*)', param[pp].strip()).groups()
                            if wsp[0] == '0':
                                wsp_P = re.search(r'next_corner: (.*) (.*) (.*)', param[pp - 1].strip()).groups()
                                linieTop.append([typeC, float(wsp_P[0]) * mnoznik, float(wsp_P[1]) * mnoznik, float(pierwszy[1]) * mnoznik, float(pierwszy[2]) * mnoznik, width])
                    #
                    for k in self.parts.keys():
                        if self.parts[k]["shape"] == footprintsListName:
                            if len(linieTop):
                                self.parts[k]["polyline"] = linieTop
                    ###############
        
    def getParts(self, koloroweElemnty, adjustParts, groupParts, partMinX, partMinY, partMinZ):
        PCB_ER = []
        for i, j in self.parts.items():
            name = i
            package = j["shape"]
            value = j['package']
            x = j["pos"][0]
            y = j["pos"][1]
            library = j["shape"]
            rot = j["pos"][2]
            if j["pos"][3]:
                side = "BOTTOM"
            else:
                side = "TOP"
            
            EL_Name = [name, j["ref_text"][0] + x, j["ref_text"][1] + y, j["ref_text"][3], j["ref_text"][2] + rot, side, "bottom-left", False, 'None', '', True]
            EL_Value = [value, x, y, 1.27, rot, side, "bottom-left", False, 'None', '', True]
            
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
    
    def getPaths(self, layerNumber):
        wires = []
        signal = []
        #
        wireList = re.search(r'\[nets\](.+?)\[.*\]', self.projektBRD.replace('\r', '').replace('\n', '')).groups()[0].split("net: ")
        for i in wireList:
            connect = i.split('connect:')[1:]
            for k in connect:
                dane = re.findall(r'vtx: .+? (.+?) (.+?) .+? .+? .+? .+? seg: .+? (.+?) (.+?) .+? .+?', k)
                lastVTX = re.findall(r'vtx: .+? (.+?) (.+?) .+? .+? .+? .+?', k)
                for j in range(len(dane)):
                    x1 = float(dane[j][0]) * self.mnoznik
                    y1 = float(dane[j][1]) * self.mnoznik
                    layer = int(dane[j][2])
                    width = float(dane[j][3]) * self.mnoznik
                    
                    if layer == 10:
                        layer = 12
                    elif layer == 11:
                        layer = 13

                    if j == len(dane) - 1:
                        x2 = float(lastVTX[-1][0]) * self.mnoznik
                        y2 = float(lastVTX[-1][1]) * self.mnoznik
                    else:
                        x2 = float(dane[j + 1][0]) * self.mnoznik
                        y2 = float(dane[j + 1][1]) * self.mnoznik
                        
                    if layer == layerNumber and [x1, y1] != [x2, y2]:
                        wires.append(['line', x1, y1, x2, y2, width])
        ####
        wires.append(signal)
        return wires
    
    def getPads(self, doc, layerNumber, grp, layerName, layerColor):
        layerName = "{0}_{1}".format(layerName, layerNumber)
        layerSide = PCBlayers[softLayers[self.databaseType][layerNumber][1]][0] 
        layerType = PCBlayers[softLayers[self.databaseType][layerNumber][1]][3]
        ####
        layerS = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", layerName)
        layerNew = layerSilkObject(layerS, layerType)
        layerNew.holes = self.showHoles()
        ####
        #via
        viaList = re.findall(r'vtx: .+? (.+?) (.+?) .+? .+? ([1-9][0-9]*) ([1-9][0-9]*)', self.projektBRD)
        for i in viaList:
            x = float(i[0]) * self.mnoznik
            y = float(i[1]) * self.mnoznik
            drill = float(i[3]) * self.mnoznik / 2.
            diameter = float(i[2]) * self.mnoznik / 2.
            
            obj = layerNew.makeFace(layerNew.addCrircle_2(x, y, diameter))
            obj = layerNew.cutHole(obj, [x, y, drill])
            layerNew.addObject(obj)
        ###
        for i, j in self.parts.items():
            X1 = j["pos"][0]  # punkt wzgledem ktorego dokonany zostanie obrot
            Y1 = j["pos"][1]  # punkt wzgledem ktorego dokonany zostanie obrot
            ROT = j["pos"][2]  # kat o jaki zostana obrocone elementy

            if j["pos"][3] == 0:
                warst = 1
            else:
                warst = 0

            try:
                for pad in j["pads"]:
                    x = pad[2] + X1
                    y = pad[3] + Y1
                    drill = pad[5]
                    ROT_2 = pad[4]
                    padS = pad[0]
                    diameter = pad[1]
                    padH = pad[6]
                    roudness = pad[7]
                    
                    if padS == '1':  # circle
                        if drill > 0:
                            obj = layerNew.makeFace(layerNew.addCrircle_2(x, y, diameter))
                            obj = layerNew.cutHole(obj, [x, y, drill])
                            layerNew.changeSide(obj, X1, Y1, warst)
                            layerNew.rotateObj(obj, [X1, Y1, ROT])
                            layerNew.addObject(obj)
                        elif drill == 0 and layerSide == warst:  # smd
                            obj = layerNew.makeFace(layerNew.addCrircle_2(x, y, diameter))
                            layerNew.changeSide(obj, X1, Y1, warst)
                            layerNew.rotateObj(obj, [X1, Y1, ROT])
                            layerNew.addObject(obj)
                    elif padS == '2':  # square
                        a = diameter
                            
                        x1 = x - a
                        y1 = y - a
                        x2 = x + a
                        y2 = y + a

                        if drill > 0:
                            obj = layerNew.makeFace(layerNew.addRectangle_2(x1, y1, x2, y2))
                            obj = layerNew.cutHole(obj, [x, y, drill])
                            layerNew.changeSide(obj, X1, Y1, warst)
                            layerNew.rotateObj(obj, [x, y, ROT_2])
                            layerNew.rotateObj(obj, [X1, Y1, ROT])
                            layerNew.addObject(obj)
                        elif drill == 0 and layerSide == warst:  # smd
                            obj = layerNew.makeFace(layerNew.addRectangle_2(x1, y1, x2, y2))
                            layerNew.changeSide(obj, X1, Y1, warst)
                            layerNew.rotateObj(obj, [x, y, ROT_2])
                            layerNew.rotateObj(obj, [X1, Y1, ROT])
                            layerNew.addObject(obj)
                    elif padS == '3':  # rectangle
                        dx = padH
                        dy = diameter
                        
                        x1 = x - dx
                        y1 = y - dy
                        x2 = x + dx
                        y2 = y + dy

                        if drill > 0:
                            obj = layerNew.makeFace(layerNew.addRectangle_2(x1, y1, x2, y2))
                            obj = layerNew.cutHole(obj, [x, y, drill])
                            layerNew.changeSide(obj, X1, Y1, warst)
                            layerNew.rotateObj(obj, [x, y, ROT_2])
                            layerNew.rotateObj(obj, [X1, Y1, ROT])
                            layerNew.addObject(obj)
                        elif drill == 0 and layerSide == warst:  # smd
                            obj = layerNew.makeFace(layerNew.addRectangle_2(x1, y1, x2, y2))
                            layerNew.changeSide(obj, X1, Y1, warst)
                            layerNew.rotateObj(obj, [x, y, ROT_2])
                            layerNew.rotateObj(obj, [X1, Y1, ROT])
                            layerNew.addObject(obj)
                    elif padS == '4':  # round rectangle
                        dx = padH
                        dy = diameter

                        if drill > 0:
                            obj = layerNew.makeFace(layerNew.addPadLong(x, y, dx, dy, roudness, 1))
                            obj = layerNew.cutHole(obj, [x, y, drill])
                            layerNew.changeSide(obj, X1, Y1, warst)
                            layerNew.rotateObj(obj, [x, y, ROT_2])
                            layerNew.rotateObj(obj, [X1, Y1, ROT])
                            layerNew.addObject(obj)
                        elif drill == 0 and layerSide == warst:  # smd
                            obj = layerNew.makeFace(layerNew.addPadLong(x, y, dx, dy, roudness, 1))
                            layerNew.changeSide(obj, X1, Y1, warst)
                            layerNew.rotateObj(obj, [x, y, ROT_2])
                            layerNew.rotateObj(obj, [X1, Y1, ROT])
                            layerNew.addObject(obj)
                    elif padS == '5':  # oval
                        dx = padH
                        dy = diameter
                        roudness = 100
                        
                        if drill > 0:
                            obj = layerNew.makeFace(layerNew.addPadLong(x, y, dx, dy, roudness))
                            obj = layerNew.cutHole(obj, [x, y, drill])
                            layerNew.rotateObj(obj, [x, y, ROT_2])
                            layerNew.rotateObj(obj, [X1, Y1, ROT])
                            layerNew.changeSide(obj, X1, Y1, warst)
                            layerNew.addObject(obj)
                        elif drill == 0 and layerSide == warst:  # smd
                            obj = layerNew.makeFace(layerNew.addPadLong(x, y, dx, dy, roudness))
                            layerNew.rotateObj(obj, [x, y, ROT_2])
                            layerNew.rotateObj(obj, [X1, Y1, ROT])
                            layerNew.changeSide(obj, X1, Y1, warst)
                            layerNew.addObject(obj)
                    elif padS == '6':  # octagon
                        if drill > 0:
                            obj = layerNew.makeFace(layerNew.addOctagon_2(self.generateOctagon(x, y, diameter * 2)))
                            obj = layerNew.cutHole(obj, [x, y, drill])
                            layerNew.changeSide(obj, X1, Y1, warst)
                            layerNew.rotateObj(obj, [x, y, ROT_2])
                            layerNew.rotateObj(obj, [X1, Y1, ROT])
                            layerNew.addObject(obj)
                        elif drill == 0 and layerSide == warst:  # smd
                            obj = layerNew.makeFace(layerNew.addOctagon_2(self.generateOctagon(x, y, diameter * 2)))
                            layerNew.changeSide(obj, X1, Y1, warst)
                            layerNew.rotateObj(obj, [x, y, ROT_2])
                            layerNew.rotateObj(obj, [X1, Y1, ROT])
                            layerNew.addObject(obj)
            except KeyError:
                continue
        ###
        layerNew.generuj(layerS)
        layerNew.updatePosition_Z(layerS)
        viewProviderLayerSilkObject(layerS.ViewObject)
        layerS.ViewObject.ShapeColor = layerColor
        grp.addObject(layerS)
        #
        doc.recompute()
    
    def getAnnotations(self):
        adnotacje = []
        #
        dane1 = re.findall(r'text: "(.*?)" ([0-9\-]+?) ([0-9\-]+?) ([0-9\-]+?) ([0-9\-]+?) ([0-9\-]+?) ([0-9\-]+?) ([0-9\-]+?)\n', self.projektBRD, re.DOTALL)
        for i in dane1:
            txt = i[0]
            x = float(i[1]) * self.mnoznik
            y = float(i[2]) * self.mnoznik
            rot = float(i[4]) * -1
            size = float(i[6]) * self.mnoznik
            
            if int(i[3]) in [7, 12]:
                side = 'TOP'
            else:
                side = 'BOTTOM'
            align = "bottom-left"
            spin = False
            
            if int(i[5]) != 0:
                # mirror = 3
                mirror = 2
            else:
                mirror = 0
            
            font = 'Hursheys'
            
            adnotacje.append([txt, x, y, size, rot, side, align, spin, mirror, font])
        #
        return adnotacje

    def getHoles(self, types):
        ''' holes/vias '''
        holes = []
        # vias
        if types['V']:
            for i in re.findall(r'vtx: .+? (.+?) (.+?) .+? .+? .+? ([1-9][0-9]*)', self.projektBRD):
                xs = float(i[0]) * self.mnoznik
                ys = float(i[1]) * self.mnoznik
                drill = float(i[2]) * self.mnoznik / 2.
                
                holes.append([xs, ys, drill])
        # pads
        if types['P']:
            for i, j in self.parts.items():
                X1 = j["pos"][0]  # punkt wzgledem ktorego dokonany zostanie obrot
                Y1 = j["pos"][1]  # punkt wzgledem ktorego dokonany zostanie obrot
                ROT = j["pos"][2]  # kat o jaki zostana obrocone elementy

                try:
                    for point in j["holes"]:
                        xs = point[0]
                        ys = point[1]
                        drill = point[2]
                        [xR, yR] = self.obrocPunkt([xs, ys], [X1, Y1], ROT)
                        if j["pos"][3] == 1:  # odbicie wspolrzednych
                            xR = self.odbijWspolrzedne(xR, X1)
                        
                        holes.append([xR, yR, drill])
                except KeyError:
                    continue
        ###
        return holes

    def getPCB(self):
        PCB = []
        ###
        linie = self.projektBRD_CP.get("board", "outline").split("\n")
        linie = linie[1:]
        for i in range(len(linie)):
            dane = linie[i].split(" ")
            
            if i == len(linie) - 1:
                daneN = linie[0].split(" ")
            else:
                daneN = linie[i + 1].split(" ")

            x1 = float(dane[2]) * self.mnoznik
            y1 = float(dane[3]) * self.mnoznik
            x2 = float(daneN[2]) * self.mnoznik
            y2 = float(daneN[3]) * self.mnoznik
            
            if dane[-1] == "0":
                PCB.append(['Line', x1, y1, x2, y2])
            elif dane[-1] in ["1", "2"]:  # clockwise arc / counterclockwise arc
                PCB.append(['Arc', x2, y2, x1, y1, self.returnArcParam(dane[-1])])
                #wygenerujPada = False
        ##
        return [PCB, True]

    def returnArcParam(self, arcType):
        if arcType == '1':
            return -90
        else:  # arcType == '2'
            return 90
    
    def getSilkLayer(self, doc, layerNumber, grp, layerName, layerColor):
        layerName = "{0}_{1}".format(layerName, layerNumber)
        layerSide = PCBlayers[softLayers[self.databaseType][layerNumber][1]][0]
        layerType = PCBlayers[softLayers[self.databaseType][layerNumber][1]][3]
        #
        layerS = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", layerName)
        layerNew = layerSilkObject(layerS, layerType)
        #
        for i in self.parts.keys():
            try:
                X1 = self.parts[i]["pos"][0]
                Y1 = self.parts[i]["pos"][1]
                ROT = self.parts[i]["pos"][2]
                
                if self.parts[i]["pos"][3]:
                    warst = 0  # bottom side
                else:
                    warst = 1  # top side
                
                if layerSide == warst:
                    for j in self.parts[i]["polyline"]:
                        x1 = j[1] + X1
                        y1 = j[2] + Y1
                        x2 = j[3] + X1
                        y2 = j[4] + Y1
                        width = j[5]
                        
                        if j[0] == "0":
                            obj = layerNew.addLine_2(x1, y1, x2, y2, width)
                            layerNew.rotateObj(obj, [X1, Y1, ROT])
                            layerNew.changeSide(obj, X1, Y1, warst)
                            layerNew.addObject(obj)
                        elif j[0] in ["1", "2"]:
                            obj = layerNew.addArc_3([x2, y2], [x1, y1], self.returnArcParam(j[0]), width)
                            layerNew.rotateObj(obj, [X1, Y1, ROT])
                            layerNew.changeSide(obj, X1, Y1, warst)
                            layerNew.addObject(obj)
            except:
                pass
        #####
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
        for i in range(self.dialogMAIN.spisWarstw.rowCount()):
            if self.dialogMAIN.spisWarstw.cellWidget(i, 0).isChecked():
                ID = int(self.dialogMAIN.spisWarstw.item(i, 1).text())
                name = str(self.dialogMAIN.spisWarstw.item(i, 4).text())
                try:
                    color = self.dialogMAIN.spisWarstw.cellWidget(i, 2).getColor()
                except:
                    color = None
                #try:
                    #transp = self.dialogMAIN.spisWarstw.cellWidget(i, 3).value()
                #except:
                    #transp = None
                
                if ID in [21, 22]:
                    self.getSilkLayer(doc, ID, grp, name, color)
                elif ID in [12, 13]:  # paths
                    self.generatePaths(self.getPaths(ID), doc, grp, name, color, ID)
                elif ID in [17, 18]:
                    self.getPads(doc, ID, grp, name, color)
                elif ID == 0:  # annotations
                    self.addAnnotations(self.getAnnotations(), doc, color)
        return doc
