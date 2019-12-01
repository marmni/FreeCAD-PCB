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

from PCBconf import PCBlayers, softLayers
from PCBobjects import *
from formats.dialogMAIN_FORM import dialogMAIN_FORM
from command.PCBgroups import *
from PCBfunctions import mathFunctions, filterHoles


class dialogMAIN(dialogMAIN_FORM):
    def __init__(self, filename=None, parent=None):
        dialogMAIN_FORM.__init__(self, parent)
        self.databaseType = "freepcb"
        #
        self.projektBRD = builtins.open(filename, "r").read().replace("\r\n", "\n").replace("\r", "\n")
        self.layersNames = self.getLayersNames()
        #
        self.generateLayers([i for i in range(31) if i not in [12, 13, 7, 8]])
        self.spisWarstw.sortItems(1)
    
    def getLayersNames(self):
        dane = {}
        # 
        for i in re.findall(r'layer_info:\s+"(.*?)" (.*?) (.*?) (.*?) (.*?) .*?\n', self.projektBRD , re.DOTALL):
            number = int(i[1])
            if int(i[1]) in softLayers[self.databaseType].keys():
                dane[int(i[1])] = {"name": i[0]}
        
        # extra layers
        dane[97] = {"name": softLayers[self.databaseType][97]["description"]}
        dane[98] = {"name": softLayers[self.databaseType][98]["description"]}
        dane[99] = {"name": softLayers[self.databaseType][99]["description"]}
        #
        return dane



class FreePCB(mathFunctions):
    '''Board importer for gEDA software'''
    def __init__(self, filename, parent):
        #self.groups = {}  # layers groups
        #
        self.fileName = filename
        self.dialogMAIN = dialogMAIN(self.fileName)
        self.databaseType = "freepcb"
        self.parent = parent
        #
        self.elements = []
        self.libraries = {}
        self.sections = {}
        #self.parts = {}
        self.mnoznik = 1. / 1000000.
    
    def defineFunction(self, layerNumber):
        if layerNumber in [98, 99]:  # pady
            return "pads"
        elif layerNumber in [12, 13]:  # paths
            return "paths"
        elif layerNumber == 97:
            return "annotations"
        else:
            return "silk"

    def getSection(self, sectionName):
        if sectionName in self.sections.keys():
            return self.sections[sectionName]
        else:
            return []
        
    def setProject(self):
        self.projektBRD = builtins.open(self.fileName, "r").read().replace("\r\n", "\n").replace("\r", "\n")
        #
        self.sections["options"] = re.findall(r'\[options\](.*)\[footprints\]', self.projektBRD, re.DOTALL)[0]
        self.sections["footprints"] = re.findall(r'\[footprints\](.*)\[board\]', self.projektBRD, re.DOTALL)[0]
        self.sections["board"] = re.findall(r'\[board\](.*)\[solder_mask_cutouts\]', self.projektBRD, re.DOTALL)[0]
        self.sections["solder_mask_cutouts"] = re.findall(r'\[solder_mask_cutouts\](.*)\[parts\]', self.projektBRD, re.DOTALL)[0]
        self.sections["parts"] = re.findall(r'\[parts\](.*)\[nets\]', self.projektBRD, re.DOTALL)[0]
        self.sections["nets"] = re.findall(r'\[nets\](.*)\[texts\]',  self.projektBRD, re.DOTALL)[0]
        self.sections["texts"] = re.findall(r'\[texts\](.*)\[.*?\]',  self.projektBRD, re.DOTALL)[0]
        
        # for i in re.findall(r'\[(.*?)\]\n(.*?)\[', self.projektBRD , re.DOTALL):
            # self.sections[i[0]] = i[1]
        #
        ######################################################

                # ############### POLYLINE
                # danePolyline = re.split(r'(outline_polyline:|n_pins:)', dane)
                # danePolyline = danePolyline[1:danePolyline.index('n_pins:')]
                # danePolyline = [o for o in danePolyline if o != "outline_polyline:"]
                # linieTop = []
                # #danePolyline = re.search(r'outline_polyline: ([\S\D]*) .*:', dane[0]).groups()[0].split("\r\n")
                # for param in danePolyline:
                    # #param = param.split("\r\n")
                    # param = param.split("\n")
                    # pierwszy = re.search(r' (.*) (.*) (.*)', param[0]).groups()
                    # width = float(pierwszy[0]) * mnoznik
                    # param = param[1:-1]
                    # p = False
                    
                    # if param[-1].strip().startswith('close_polyline'):
                        # param = param[:-1]
                    
                    # for pp in range(len(param)):
                        # if param[pp].strip().startswith("next_corner:"):
                            # wsp = re.search(r'next_corner: (.*) (.*) (.*)', param[pp].strip()).groups()
                            # typeC = wsp[2]
                            
                            # if not p:
                                # linieTop.append([typeC, float(pierwszy[1]) * mnoznik, float(pierwszy[2]) * mnoznik, float(wsp[0]) * mnoznik, float(wsp[1]) * mnoznik, width])
                                # p = True
                            # else:
                                # wsp_P = re.search(r'next_corner: (.*) (.*) (.*)', param[pp - 1].strip()).groups()
                                # linieTop.append([typeC, float(wsp_P[0]) * mnoznik, float(wsp_P[1]) * mnoznik, float(wsp[0]) * mnoznik, float(wsp[1]) * mnoznik, width])
                       
                                # if pp == len(param) - 1:
                                    # linieTop.append([typeC, float(wsp[0]) * mnoznik, float(wsp[1]) * mnoznik, float(pierwszy[1]) * mnoznik, float(pierwszy[2]) * mnoznik, width])
                        # elif param[pp].strip().startswith("close_polyline:"):
                            # wsp = re.search(r'close_polyline: (.*)', param[pp].strip()).groups()
                            # if wsp[0] == '0':
                                # wsp_P = re.search(r'next_corner: (.*) (.*) (.*)', param[pp - 1].strip()).groups()
                                # linieTop.append([typeC, float(wsp_P[0]) * mnoznik, float(wsp_P[1]) * mnoznik, float(pierwszy[1]) * mnoznik, float(pierwszy[2]) * mnoznik, width])
                    # #
                    # for k in self.parts.keys():
                        # if self.parts[k]["shape"] == footprintsListName:
                            # if len(linieTop):
                                # self.parts[k]["polyline"] = linieTop
                    # ###############
        
    def getParts(self):
        return
        
        
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
    
    # def getSilkLayer(self, doc, layerNumber, grp, layerName, layerColor):
        # layerName = "{0}_{1}".format(layerName, layerNumber)
        # layerSide = PCBlayers[softLayers[self.databaseType][layerNumber][1]][0]
        # layerType = PCBlayers[softLayers[self.databaseType][layerNumber][1]][3]
        # #
        # layerS = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", layerName)
        # layerNew = layerSilkObject(layerS, layerType)
        # #
        # for i in self.parts.keys():
            # try:
                # X1 = self.parts[i]["pos"][0]
                # Y1 = self.parts[i]["pos"][1]
                # ROT = self.parts[i]["pos"][2]
                
                # if self.parts[i]["pos"][3]:
                    # warst = 0  # bottom side
                # else:
                    # warst = 1  # top side
                
                # if layerSide == warst:
                    # for j in self.parts[i]["polyline"]:
                        # x1 = j[1] + X1
                        # y1 = j[2] + Y1
                        # x2 = j[3] + X1
                        # y2 = j[4] + Y1
                        # width = j[5]
                        
                        # if j[0] == "0":
                            # obj = layerNew.addLine_2(x1, y1, x2, y2, width)
                            # layerNew.rotateObj(obj, [X1, Y1, ROT])
                            # layerNew.changeSide(obj, X1, Y1, warst)
                            # layerNew.addObject(obj)
                        # elif j[0] in ["1", "2"]:
                            # obj = layerNew.addArc_3([x2, y2], [x1, y1], self.returnArcParam(j[0]), width)
                            # layerNew.rotateObj(obj, [X1, Y1, ROT])
                            # layerNew.changeSide(obj, X1, Y1, warst)
                            # layerNew.addObject(obj)
            # except:
                # pass
        # #####
        # layerNew.generuj(layerS)
        # layerNew.updatePosition_Z(layerS)
        # viewProviderLayerSilkObject(layerS.ViewObject)
        # layerS.ViewObject.ShapeColor = layerColor
        # grp.addObject(layerS)
        # #
        # doc.recompute()
    
    def getSilkLayer(self, layerNew, layerNumber, display=[True, True, True, True]):
        pass
    
    def getPaths(self, layerNew, layerNumber, display=[True, True, True, False]):
        data = self.getSection("nets").split('connect:')
        
        if len(data) > 1:
            data = data[1:]
            for i in data:
                vtx = re.findall(r'vtx:\s+.*?\s+(.*?)\s+(.*?)\s+.*?\n\s+seg:\s+.*?\s+(.*?)\s+(.*?)\s+', i)
                lastVTX = re.findall(r'vtx:\s+.*?\s+(.*?)\s+(.*?)\s+.*?\s+.*?\s+.*?\s+.*?', i)[-1]
                
                for j in range(len(vtx)):
                    x1 = float(vtx[j][0]) * self.mnoznik
                    y1 = float(vtx[j][1]) * self.mnoznik
                    width = float(vtx[j][3]) * self.mnoznik
                    
                    if int(vtx[j][2]) != int(layerNumber[0]):
                        continue
                    
                    if j == len(vtx) - 1:
                        x2 = float(lastVTX[0]) * self.mnoznik
                        y2 = float(lastVTX[1]) * self.mnoznik
                    else:
                        x2 = float(vtx[j + 1][0]) * self.mnoznik
                        y2 = float(vtx[j + 1][1]) * self.mnoznik
                    #
                    if [x1, y1] != [x2, y2]:
                        layerNew.addLineWidth(x1, y1, x2, y2, width)
                        layerNew.setFace()

    
    def getPads(self, layerNew, layerNumber, layerSide):
        return
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
        
    def getNormalAnnotations(self):
        pass
    
    # def getAnnotations(self):
        # adnotacje = []
        # #
        # dane1 = re.findall(r'text: "(.*?)" ([0-9\-]+?) ([0-9\-]+?) ([0-9\-]+?) ([0-9\-]+?) ([0-9\-]+?) ([0-9\-]+?) ([0-9\-]+?)\n', self.projektBRD, re.DOTALL)
        # for i in dane1:
            # txt = i[0]
            # x = float(i[1]) * self.mnoznik
            # y = float(i[2]) * self.mnoznik
            # rot = float(i[4]) * -1
            # size = float(i[6]) * self.mnoznik
            
            # if int(i[3]) in [7, 12]:
                # side = 'TOP'
            # else:
                # side = 'BOTTOM'
            # align = "bottom-left"
            # spin = False
            
            # if int(i[5]) != 0:
                # # mirror = 3
                # mirror = 2
            # else:
                # mirror = 0
            
            # font = 'Hursheys'
            
            # adnotacje.append([txt, x, y, size, rot, side, align, spin, mirror, font])
        # #
        # return adnotacje
    
    def getLibraries(self):
        if len(self.libraries) == 0:
            for i in re.findall(r'(?=name:([\s\S]*?)(?=name:|$))', self.getSection("footprints"), re.DOTALL):
                name = re.search('^\s*"(.*?)"', i).groups()[0]
                
                try:
                    if re.search('\s*units:\s*(.*?)\n', i).groups()[0] == "MIL":  # mils
                        mnoznik = 0.0254
                    else:
                        mnoznik = self.mnoznik
                except:
                    mnoznik = self.mnoznik
                #
                if not name in self.libraries:
                    self.libraries[name] = {}
                
                self.libraries[name]["units"] = mnoznik
                self.libraries[name]["data"] = i
                #######################################################
                self.libraries[name]["pins"] = {}
                for j in re.findall(r'(?=pin:([\s\S]*?)(?=pin:|$))', i, re.DOTALL):
                    pinData = re.search('^\s*(".*?") (.*?) (.*?) (.*?) (.*?)\n', j).groups()
                    
                    if not pinData[0] in self.libraries[name]["pins"].keys():
                        self.libraries[name]["pins"][pinData[0]] = {}
                    
                    self.libraries[name]["pins"][pinData[0]] = {
                        "x": float(pinData[2]) * mnoznik,
                        "y": float(pinData[3]) * mnoznik,
                        "r": float(pinData[1]) * mnoznik / 2.,
                        "rot": float(pinData[4]) * mnoznik,
                    }
                    #
                    topPad = re.search('top_pad: (.*?) (.*?) (.*?) (.*?) (.*?)($|\n)', j).groups()
                    
                    self.libraries[name]["pins"][pinData[0]]["top"] = {
                        "shape": int(topPad[0]), #1-round 2-square
                        "width": float(topPad[1]) * mnoznik,
                        "len": float(topPad[2]) * mnoznik,
                        "radius": float(topPad[4]) * mnoznik,
                    }
                    #
                    if len(re.findall(r'_pad:', j, re.DOTALL)) == 3: # pin
                        bottomPad = re.search('bottom_pad: (.*?) (.*?) (.*?) (.*?) (.*?)($|\n)', j).groups()

                        self.libraries[name]["pins"][pinData[0]]["bottom"] = {
                            "shape": int(bottomPad[0]), #1-round 2-square
                            "width": float(bottomPad[1]) * mnoznik,
                            "len": float(bottomPad[2]) * mnoznik,
                            "radius": float(bottomPad[4]) * mnoznik,
                        }
                #######################################################
    
    def getElements(self):
        try:
            if len(self.elements) == 0:
                for i in re.findall(r'part:\s+(.*?)\n(.*?)\n[\n|\[|parts]', self.getSection("parts"), re.DOTALL):
                    
                    try:
                        if re.search(r'units:\s+(.*)', i[0]).groups()[0] == "MIL":  # mils
                            mnoznik = 0.0254
                        else:
                            mnoznik = self.mnoznik
                    except:
                        mnoznik = self.mnoznik
                    #
                    partPos = re.search(r'pos:\s+(.*?)\s+(.*?)\s+(.*?)\s+(.*?)\s+([0-1])', i[1]).groups()
                    
                    locked = False
                    if int(partPos[4]):
                        locked = True
                    
                    side = "TOP"
                    rot = 360 - float(partPos[3])
                    
                    if int(partPos[2]) == 1:
                        side = "BOTTOM"
                        rot = float(partPos[3])
                    #
                    
                    self.elements.append({
                        'name': i[0], 
                        'library': "", 
                        'package': re.search(r'shape:\s+"(.*?)"', i[1]).groups()[0], 
                        'value': "", 
                        'x': float(partPos[0]) * mnoznik, 
                        'y': float(partPos[1]) * mnoznik, 
                        'locked': locked,
                        'populated': False, 
                        'smashed': False, 
                        'rot': rot, 
                        'side': side,
                        'dataElement': i[1]
                    })
        except Exception as e:
            FreeCAD.Console.PrintWarning("3. {0}\n".format(e))
            

    def getHoles(self, holesObject, types, Hmin, Hmax):
        ''' holes/vias '''
        if types['IH']:  # detecting collisions between holes - intersections
            holesList = []
        
        # vias
        if types['V']:
            for i in re.findall(r'vtx: .+? (.+?) (.+?) .+? .+? .+? ([1-9][0-9]*)', self.projektBRD):
                x = float(i[0]) * self.mnoznik
                y = float(i[1]) * self.mnoznik
                r = float(i[2]) * self.mnoznik / 2.
                
                if filterHoles(r, Hmin, Hmax):
                    if types['IH']:  # detecting collisions between holes - intersections
                        add = True
                        try:
                            for k in holesList:
                                d = sqrt( (x - k[0]) ** 2 + (y - k[1]) ** 2)
                                if(d < r + k[2]):
                                    add = False
                                    break
                        except Exception as e:
                            FreeCAD.Console.PrintWarning("1. {0}\n".format(e))
                        
                        if (add):
                            holesList.append([x, y, r])
                            holesObject.addGeometry(Part.Circle(FreeCAD.Vector(x, y, 0.), FreeCAD.Vector(0, 0, 1), r))
                        else:
                            FreeCAD.Console.PrintWarning("Intersection between holes detected. Hole x={:.2f}, y={:.2f} will be omitted.\n".format(x, y))
                    else:
                        holesObject.addGeometry(Part.Circle(FreeCAD.Vector(x, y, 0.), FreeCAD.Vector(0, 0, 1), r))
        
        ## pads / holes
        if types['P'] or types['H']:
            self.getLibraries()
            self.getElements()
            
            try:
                for i in self.elements:
                    X1 = i['x']
                    Y1 = i['y']
                    ROT = i['rot']
                    
                    if i['package'] in self.libraries.keys():
                        for j in self.libraries[i['package']]["pins"].keys():
                            if "bottom" in self.libraries[i['package']]["pins"][j].keys():
                                x = self.libraries[i['package']]["pins"][j]["x"]
                                y = self.libraries[i['package']]["pins"][j]["y"]
                                r = self.libraries[i['package']]["pins"][j]["r"]
                                
                                if self.libraries[i['package']]["pins"][j]["bottom"]["width"] == 0 and self.libraries[i['package']]["pins"][j]["top"]["width"] == 0 and not types['H']:
                                    continue
                                elif (self.libraries[i['package']]["pins"][j]["bottom"]["width"] != 0 or self.libraries[i['package']]["pins"][j]["top"]["width"] != 0) and not types['P']:
                                    continue
                                
                                [xR, yR] = self.obrocPunkt([x, y], [X1, Y1], ROT)
                                if i["side"] == "BOTTOM":
                                    xR = self.odbijWspolrzedne(xR, X1)
                                
                                if filterHoles(r, Hmin, Hmax):
                                    if types['IH']:  # detecting collisions between holes - intersections
                                        add = True
                                        try:
                                            for k in holesList:
                                                d = sqrt( (xR - k[0]) ** 2 + (yR - k[1]) ** 2)
                                                if(d < r + k[2]):
                                                    add = False
                                                    break
                                        except Exception as e:
                                            FreeCAD.Console.PrintWarning("1. {0}\n".format(e))
                                        
                                        if (add):
                                            holesList.append([xR, yR, r])
                                            holesObject.addGeometry(Part.Circle(FreeCAD.Vector(xR, yR, 0.), FreeCAD.Vector(0, 0, 1), r))
                                        else:
                                            FreeCAD.Console.PrintWarning("Intersection between holes detected. Hole x={:.2f}, y={:.2f} will be omitted.\n".format(xR, yR))
                                    else:
                                        holesObject.addGeometry(Part.Circle(FreeCAD.Vector(xR, yR, 0.), FreeCAD.Vector(0, 0, 1), r))
            except Exception as e:
                FreeCAD.Console.PrintWarning("3. {0}\n".format(e))
        
    def getCornsers(self, data):
        result = []
        #
        try:
            corners = re.findall(r'corner:\s+[0-9]*\s+(.*?)\s+(.*?)\s+([0-9]*)', data, re.MULTILINE|re.DOTALL)
            
            for i in range(len(corners)):
                x1 = float(corners[i][0]) * self.mnoznik
                y1 = float(corners[i][1]) * self.mnoznik
                cType = int(corners[i][2])
                
                if i + 1 < len(corners):
                    x2 = float(corners[i + 1][0]) * self.mnoznik
                    y2 = float(corners[i + 1][1]) * self.mnoznik
                else:
                    x2 = float(corners[0][0]) * self.mnoznik
                    y2 = float(corners[0][1]) * self.mnoznik
                
                if cType == 0:
                    result.append(['Line', x1, y1, x2, y2])
                elif cType == 1:
                    result.append(['Arc', x1, y1, x2, y2, -90])
                else:
                    result.append(['Arc', x1, y1, x2, y2, 90])
        except Exception as e:
            FreeCAD.Console.PrintWarning("3. {0}\n".format(e))
        #
        return result

    def getPCB(self, borderObject):
        for i in re.findall(r'outline:\s+(.*?)\s+.*?\n(.*?)\n\n', self.getSection("board"), re.DOTALL):
            for j in self.getCornsers(i[1]):
                
                if j[0] == 'Line':
                    borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(j[1], j[2], 0), FreeCAD.Vector(j[3], j[4], 0)))
                if j[0] == 'Arc':
                    [x3, y3] = self.arcMidPoint([j[1], j[2]], [j[3], j[4]], j[5])
                    arc = Part.ArcOfCircle(FreeCAD.Vector(j[1], j[2], 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(j[3], j[4], 0.0))
                    borderObject.addGeometry(arc)
