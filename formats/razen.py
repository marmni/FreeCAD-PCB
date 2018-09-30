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
import json
import os
from math import sqrt, atan2
from PySide import QtGui

import PCBconf
from PCBobjects import *
from formats.PCBmainForms import *


class dialogMAIN(dialogMAIN_FORM):
    def __init__(self, filename=None, parent=None):
        dialogMAIN_FORM.__init__(self, parent)
        self.databaseType = "razen"
        
        ###
        self.generateLayers()
        self.spisWarstw.sortItems(1)
        #
        self.razenBiblioteki = QtGui.QLineEdit('')
        if PCBconf.supSoftware[self.databaseType]['libPath'] != "":
            self.razenBiblioteki.setText(PCBconf.supSoftware[self.databaseType]['libPath'])
        
        lay = QtGui.QHBoxLayout()
        lay.addWidget(QtGui.QLabel('Library'))
        lay.addWidget(self.razenBiblioteki)
        self.lay.addLayout(lay, 12, 0, 1, 6)


class Razen_PCB(mainPCB):
    def __init__(self):
        mainPCB.__init__(self, None)
        
        self.dialogMAIN = dialogMAIN()
        self.databaseType = "razen"
    
    def znajdzBiblioteke(self, library, package):
        libPath = str(self.dialogMAIN.razenBiblioteki.text()).split(';')
        
        for lib in libPath:
            try:
                plikPart = builtins.open(os.path.join(os.path.join(os.path.join(lib, library), package), 'design.rzp'), "r")  # main lib file
                plikPart = json.load(plikPart)
                plikPart = builtins.open(os.path.join(os.path.join(os.path.join(lib, library), package), plikPart['layout']), "r")  # footprints file
                return json.load(plikPart)
            except:
                continue
        return False

    def setProject(self, filename):
        if str(filename).endswith('.rzp'):
            projektBRD = builtins.open(filename, "r")
            projektBRD = json.load(projektBRD)
            
            docname = os.path.dirname(filename)
            projektPCB = projektBRD["layout"]
            
            filename = os.path.join(docname, projektPCB)
            
        projektBRD = builtins.open(filename, "r")
        self.projektBRD = json.load(projektBRD)
        
        try:
            self.fileVersion = self.projektBRD["version"]
        except:
            self.fileVersion = False
    
    def getParts(self, koloroweElemnty, adjustParts, groupParts, partMinX, partMinY, partMinZ):
        PCB_ER = []
        #
        for i in self.projektBRD["elts"]:
            try:
                if i["_t"] == "Footprint":
                    x = self.setUnit(i['pos'][0], self.fileVersion)
                    y = self.setUnit(i['pos'][1], self.fileVersion) * (-1)
                    rot = i['angle'] * (-1)
                    if not i['mirror']:
                        side = "TOP"
                    else:
                        side = "BOTTOM"
                    library = i['lib']
                    value = i['value']
                    package = i['part']
                    name = i['name']
                    
                    ######
                    # name
                    EL_Name = ['', x, y, 0.7, rot, side, "bottom-left", False, 'None', '', True]
                    
                    EL_Name[0] = name
                    EL_Name[10] = i['showname']
                    
                    # value
                    EL_Value = ['', x, y, 0.7, rot, side, "bottom-left", False, 'None', '', True]
                    EL_Value[0] = value
                    ##
                    lineList = self.znajdzBiblioteke(library, package)
                    if lineList:
                        try:
                            fileVersion = lineList["version"]
                        except:
                            fileVersion = None
                        
                        for j in lineList["elts"]:
                            try:
                                if j["_t"] == "Text":
                                    if j["value"] == "$name":
                                        EL_Name[1] = self.setUnit(j["pos"][0], fileVersion) + x
                                        EL_Name[2] = self.setUnit(j["pos"][1], fileVersion) * (-1) + y
                                        EL_Name[3] = j["size"] * 1
                                        EL_Name[4] = j["angle"] * (-1) + rot
                                    elif j["value"] == "$value":
                                        EL_Value[1] = self.setUnit(j["pos"][0], fileVersion) + x
                                        EL_Value[2] = self.setUnit(j["pos"][1], fileVersion) * (-1) + y
                                        EL_Value[3] = j["size"] * 1
                                        EL_Value[4] = j["angle"] * (-1) + rot
                            except Exception as e:
                                FreeCAD.Console.PrintWarning(u"{0} \n".format(e))
                    #
                    newPart = [[name, package, value, x, y, rot, side, library], EL_Name, EL_Value]
                    wyn = self.addPart(newPart, koloroweElemnty, adjustParts, groupParts, partMinX, partMinY, partMinZ)
                    #
                    if wyn[0] == 'Error':  # lista brakujacych elementow
                        partNameTXT = partNameTXT_label = self.generateNewLabel(name)
                        if isinstance(partNameTXT, str):
                            partNameTXT = unicodedata.normalize('NFKD', partNameTXT).encode('ascii', 'ignore')
                        
                        PCB_ER.append([partNameTXT, package, value, library])
            except Exception as e:
                FreeCAD.Console.PrintWarning(u"Error: {0} \n".format(e))
        #######
        return PCB_ER
        
    
    def getAnnotations(self):
        adnotacje = []
        #
        annotations = self.projektBRD["elts"]
        for i in annotations:
            try:
                if i["_t"] == 'Text' and i['value'] != '$name':
                    x = self.setUnit(i['pos'][0], self.fileVersion)
                    y = self.setUnit(i['pos'][1], self.fileVersion) * (-1)
                    size = i['size']
                    rot = i['angle'] * (-1)
                    txt = str(i['value'])
                    
                    if i['layer'] in [25, 1, 21]:
                        side = 'TOP'
                    else:
                        side = 'BOTTOM'
                    
                    align = "bottom-left"
                    spin = False
                    
                    if i['mirror'] == True:
                        mirror = 1
                    else:
                        mirror = 0
                        
                    font = str(i['font'])

                    adnotacje.append([txt, x, y, size, rot, side, align, spin, mirror, font])
            except Exception as e:
                FreeCAD.Console.PrintWarning(str(e) + "\n")
                pass
        #
        return adnotacje
    
    def getHoles(self, types):
        ''' holes/vias '''
        holes = []
        #
        for i in self.projektBRD["elts"]:
            try:
                if i["_t"] == 'Via' and i["drill"] > 0. and types['V']:
                    (x, y, drill, height, width) = self.getViaParameters(i, self.fileVersion)
                    
                    holes.append([x, y, drill])
                elif i["_t"] == 'Drill' and i["diameter"] > 0. and types['H']:
                    (x, y, drill) = self.getHolesPrameters(i, self.fileVersion)
                    
                    holes.append([x, y, drill])
                elif self.dialogMAIN.razenBiblioteki != "" and i["_t"] == "Footprint":
                    library = i['lib']
                    package = i['part']
                    X1 = self.setUnit(i['pos'][0], self.fileVersion)  # punkt wzgledem ktorego dokonany zostanie obrot
                    Y1 = self.setUnit(i['pos'][1], self.fileVersion) * (-1)  # punkt wzgledem ktorego dokonany zostanie obrot
                    
                    if not i['mirror']:
                        ROT = i['angle'] * (-1)
                        warst = 1
                    else:
                        ROT = i['angle']
                        warst = 0
                    
                    padList = self.znajdzBiblioteke(library, package)
                    if not padList:
                        continue
                        
                    try:
                        fileVersion = padList["version"]
                    except:
                        fileVersion = None
                    
                    for j in padList["elts"]:
                        try:
                            if j["_t"] == "Pad" and j["layer"] == 1 and j["drill"] > 0. and types['P']:
                                (xs, ys, drill, height, width) = self.getViaParameters(j, fileVersion)
                                [xR, yR] = self.obrocPunkt([xs, ys], [X1, Y1], ROT)
                                
                                if warst == 0:  # odbicie wspolrzednych
                                    xR = self.odbijWspolrzedne(xR, X1)
                                
                                holes.append([xR, yR, drill])
                            elif j["_t"] == "Drill" and j["diameter"] > 0. and types['H']:
                                (xs, ys, drill) = self.getHolesPrameters(j, fileVersion)
                                [xR, yR] = self.obrocPunkt([xs, ys], [X1, Y1], ROT)
                                
                                if warst == 0:  # odbicie wspolrzednych
                                    xR = self.odbijWspolrzedne(xR, X1)
                                
                                holes.append([xR, yR, drill])
                        except:
                            pass
            except:
                pass
        #######
        return holes
    
    def getPaths(self, layerNumber):
        wires = []
        signal = []
        #
        for i in self.projektBRD["elts"]:
            if (i["_t"] == 'Segment' or i["_t"] == 'Trace') and i["layer"] == layerNumber and i["pta"] != i["ptb"]:
                (x1, y1, x2, y2, width) = self.getLineParameters(i, self.fileVersion)
                
                if [x1, y1] != [x2, y2]:
                    wires.append(['line', x1, y1, x2, y2, width])
            elif i["_t"] == 'Arc' and i["layer"] == layerNumber and i["ofsa"] != i["ofsb"]:
                (x1, y1, x2, y2, curve, width) = self.getArcParameters(i, self.fileVersion)
                
                wires.append(['arc', x2, y2, x1, y1, curve, width, 'round'])
                
        wires.append(signal)
        ####
        return wires
    
    def getPads(self, doc, layerNumber, grp, layerName, layerColor, defHeight):
        layerName = "{0}_{1}".format(layerName, layerNumber)
        #layerSide = PCBconf.PCBlayers[PCBconf.softLayers["razen"][layerNumber][1]][0]
        layerType = PCBconf.PCBlayers[PCBconf.softLayers["razen"][layerNumber][1]][3]
        ####
        layerS = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", layerName)
        layerNew = layerSilkObject(layerS, layerType)
        layerNew.holes = self.showHoles()
        layerNew.defHeight = defHeight
        ####
        # holes/via
        holes = self.projektBRD["elts"]
        for i in holes:
            if i["_t"] == 'Via':
                (x, y, drill, height, width) = self.getViaParameters(i, self.fileVersion)
                
                if drill <= 0:
                    dodajObj = False
                    if layerNumber == 17 and i["layer"] == 1:
                        dodajObj = True
                    elif layerNumber == 18 and i["layer"] == 16:
                        dodajObj = True
                    
                    if not dodajObj:
                        continue
                
                if i["shape"] == "circle" and height == width:
                    layerNew.createObject()
                    layerNew.addCircle(x, y, height)
                    layerNew.setFace()
                elif i["shape"] == "rectangle":
                    x1 = x - width
                    y1 = y - height
                    x2 = x + width
                    y2 = y + height
                    
                    layerNew.createObject()
                    layerNew.addRectangle(x1, y1, x2, y2)
                    layerNew.setFace()
                elif i["shape"] == "octagon":
                    layerNew.createObject()
                    layerNew.addOctagon(x, y, height * 2, width * 2)
                    layerNew.setFace()
                elif i["shape"] == "circle" and height != width:
                    layerNew.createObject()
                    layerNew.addElipse(x, y, width, height)
                    layerNew.setFace()
                elif i["shape"] == "polygon":
                    layerNew.createObject()
                    layerNew.addPolygon(self.getPolygon(i['polygon'], self.fileVersion, x, y))
                    layerNew.setFace()
            #elif i["_t"] == "Polygon":
                #dodajObj = False
                #if layerNumber == 17 and i["layer"] == 1:
                    #dodajObj = True
                #elif layerNumber == 18 and i["layer"] == 16:
                    #dodajObj = True
                
                #if not dodajObj:
                    #continue
                
                #x = self.setUnit(i['pos'][0], self.fileVersion)
                #y = self.setUnit(i['pos'][1], self.fileVersion) * (-1)
                
                #layerNew.createObject()
                #for pp in self.getPolygon(i['pts'], self.fileVersion, x, y):
                    #if pp[0] == 'Line':
                        #layerNew.addLine(pp[1], pp[2], pp[3], pp[4])
                #layerNew.setFace()
            elif i["_t"] == 'Arc' and i["ofsa"] == i["ofsb"]:
                dodajObj = False
                if layerNumber == 17 and i["layer"] == 1:
                    dodajObj = True
                elif layerNumber == 18 and i["layer"] == 16:
                    dodajObj = True
                    
                if not dodajObj:
                    continue
                
                (x, y, r, w) = self.gerCircleParameters(i, self.fileVersion)
                
                layerNew.createObject()
                layerNew.addCircle(x, y, r, w)
                layerNew.setFace()
            elif self.dialogMAIN.razenBiblioteki != "" and i["_t"] == "Footprint":
                library = i['lib']
                package = i['part']
                X1 = self.setUnit(i['pos'][0], self.fileVersion)  # punkt wzgledem ktorego dokonany zostanie obrot
                Y1 = self.setUnit(i['pos'][1], self.fileVersion) * (-1)  # punkt wzgledem ktorego dokonany zostanie obrot
                
                if not i['mirror']:  # top side
                    ROT = i['angle'] * (-1)
                    warst = 1
                else:  # bottom side
                    ROT = i['angle'] * (-1)
                    warst = 0

                padList = self.znajdzBiblioteke(library, package)
                if not padList:
                    continue
                
                try:
                    fileVersion = padList["version"]
                except:
                    fileVersion = None
                
                for j in padList["elts"]:
                    try:
                        if j["_t"] == "Pad":
                            #if j["drill"] <= 0:
                            dodajObj = False
                            if layerNumber == 17 and (j["layer"] == 1 and warst == 1 or j["layer"] == 16 and warst == 0):
                                dodajObj = True
                            elif layerNumber == 18 and (j["layer"] == 16 and warst == 1 or j["layer"] == 1 and warst == 0):
                                dodajObj = True
                                
                            if not dodajObj:
                                continue
                            #####
                            x = self.setUnit(j["pos"][0], fileVersion) + X1
                            y = self.setUnit(j["pos"][1], fileVersion) * (-1) + Y1
                            dx = self.setUnit(j["width"], fileVersion)
                            dy = self.setUnit(j["height"], fileVersion)
                            #drill = j["drill"] * self.setUnit(fileVersion) / 2.
                        
                            if j["shape"] in ["rectangle", "rect"]:
                                x1 = x - dx / 2.
                                y1 = y - dy * (-1) / 2.
                                x2 = x + dx / 2.
                                y2 = y + dy * (-1) / 2.
                                
                                layerNew.createObject()
                                layerNew.addRectangle(x1, y1, x2, y2)
                                layerNew.setChangeSide(X1, Y1, warst)
                                layerNew.addRotation(X1, Y1, ROT)
                                layerNew.setFace()
                            elif j["shape"] == "circle" and dx == dy:
                                layerNew.createObject()
                                layerNew.addCircle(x, y, dx / 2.)
                                layerNew.setChangeSide(X1, Y1, warst)
                                layerNew.addRotation(X1, Y1, ROT)
                                layerNew.setFace()
                            elif j["shape"] == "circle" and dx != dy:
                                layerNew.createObject()
                                layerNew.addElipse(x, y, dx / 2., dy / 2.)
                                layerNew.setChangeSide(X1, Y1, warst)
                                layerNew.addRotation(X1, Y1, ROT)
                                layerNew.setFace()
                            elif j["shape"] == "octagon":
                                layerNew.createObject()
                                layerNew.addOctagon(x, y, dy, dx)
                                layerNew.setChangeSide(X1, Y1, warst)
                                layerNew.addRotation(X1, Y1, ROT)
                                layerNew.setFace()
                    except Exception as e:
                        FreeCAD.Console.PrintWarning("{0} \n".format(e))
        ###
        layerNew.generuj(layerS)
        layerNew.updatePosition_Z(layerS)
        viewProviderLayerSilkObject(layerS.ViewObject)
        layerS.ViewObject.ShapeColor = layerColor
        grp.addObject(layerS)
        #
        doc.recompute()
        
    def getPolygon(self, dane2, version, X=0, Y=0):
        poin = []
        for j in range(0, len(dane2), 2):
            x1 = self.setUnit(dane2[j], version)
            y1 = self.setUnit(dane2[j + 1], version) * (-1)
                                
            try:
                x2 = self.setUnit(dane2[j + 2], version)
                y2 = self.setUnit(dane2[j + 3], version) * (-1)
            except:
                x2 = self.setUnit(dane2[0], version)
                y2 = self.setUnit(dane2[1], version) * (-1)
                            
            if not [x1, y1] == [x2, y2]:  # remove points, only lines
                poin.append(['Line', x1 + X, y1 + Y, x2 + X, y2 + Y])
        return poin

    def getSilkLayer(self, doc, layerNumber, grp, layerName, layerColor, defHeight):
        layerName = "{0}_{1}".format(layerName, layerNumber)
        layerSide = PCBconf.PCBlayers[PCBconf.softLayers["razen"][layerNumber][1]][0]
        layerType = PCBconf.PCBlayers[PCBconf.softLayers["razen"][layerNumber][1]][3]
        
        layerS = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", layerName)
        layerNew = layerSilkObject(layerS, layerType)
        layerNew.defHeight = defHeight
        #####
        if self.dialogMAIN.razenBiblioteki != "":
            parts = self.projektBRD["elts"]
            
            for i in parts:
                try:
                    if i["_t"] == "Segment" and i["layer"] == layerNumber:
                        (x1, y1, x2, y2, width) = self.getLineParameters(i, self.fileVersion)
                        
                        layerNew.createObject()
                        layerNew.addLineWidth(x1, y1, x2, y2, width)
                        layerNew.setFace()
                    elif i["_t"] == "Arc" and i["ofsa"] == i["ofsb"] and i["layer"] == layerNumber:
                        (x, y, r, w) = self.gerCircleParameters(i, self.fileVersion)
                        
                        layerNew.createObject()
                        layerNew.addCircle(x, y, r, w)
                        layerNew.setFace()
                        layerNew.addObject(obj)
                    elif i["_t"] == "Arc" and i["layer"] == layerNumber:
                        (x1, y1, x2, y2, curve, width) = self.getArcParameters(i, self.fileVersion)
                        
                        layerNew.createObject()
                        layerNew.addArcWidth([x2, y2], [x1, y1], curve, width)
                        layerNew.setFace()
                    elif i["_t"] == "Polygon" and i["layer"] == layerNumber:
                        x = self.setUnit(i['pos'][0], self.fileVersion)
                        y = self.setUnit(i['pos'][1], self.fileVersion) * (-1)
                        
                        layerNew.createObject()
                        layerNew.addPolygon(self.getPolygon(i['pts'], self.fileVersion, x, y))
                        layerNew.setFace()
                    elif i["_t"] == "Footprint":
                        library = i['lib']
                        package = i['part']
                        X1 = self.setUnit(i['pos'][0], self.fileVersion)  # punkt wzgledem ktorego dokonany zostanie obrot
                        Y1 = self.setUnit(i['pos'][1], self.fileVersion) * (-1)  # punkt wzgledem ktorego dokonany zostanie obrot
                        ROT = i['angle'] * (-1)
                        
                        lineList = self.znajdzBiblioteke(library, package)
                        if not lineList:
                            continue
                        
                        try:
                            fileVersion = lineList["version"]
                        except:
                            fileVersion = None
                        
                        for j in lineList["elts"]:
                            try:
                                if i['mirror']:
                                    if layerNumber == 21:  # top
                                        szukanaWarstwa = 22
                                    elif layerNumber == 22:  # bottom
                                        szukanaWarstwa = 21
                                else:
                                    szukanaWarstwa = layerNumber
                                ####
                                if j["_t"] == "Segment" and j["layer"] == szukanaWarstwa:
                                    (x1, y1, x2, y2, width) = self.getLineParameters(j, fileVersion)
                                    
                                    layerNew.createObject()
                                    layerNew.addLineWidth(x1 + X1, y1 + Y1, x2 + X1, y2 + Y1, width)
                                    layerNew.addRotation(X1, Y1, ROT)
                                    layerNew.setChangeSide(X1, Y1, warst)
                                    layerNew.setFace()
                                elif j["_t"] == "Arc" and j["layer"] == szukanaWarstwa and j["ofsa"] == j["ofsb"]:
                                    (x, y, radius, width) = self.gerCircleParameters(j, fileVersion)
                                    
                                    layerNew.createObject()
                                    layerNew.addCircle(x + X1, y * (-1) + Y1, radius, width)
                                    layerNew.addRotation(X1, Y1, ROT)
                                    layerNew.setChangeSide(X1, Y1, warst)
                                    layerNew.setFace()
                                elif j["_t"] == "Arc" and j["layer"] == szukanaWarstwa:
                                    (x1, y1, x2, y2, curve, width) = self.getArcParameters(j, fileVersion)
                                    
                                    layerNew.createObject()
                                    layerNew.addArcWidth([x2 + X1, y2 + Y1], [x1 + X1, y1 + Y1], curve, width)
                                    layerNew.addRotation(X1, Y1, ROT)
                                    layerNew.setChangeSide(X1, Y1, warst)
                                    layerNew.setFace()
                                elif j["_t"] == "Polygon" and j["layer"] == szukanaWarstwa:
                                    x = self.setUnit(j['pos'][0], fileVersion)
                                    y = self.setUnit(j['pos'][1], fileVersion) * (-1)
                                    
                                    layerNew.createObject()
                                    layerNew.addPolygon(self.getPolygon(j['pts'], fileVersion, X1 + x, Y1 + y))
                                    layerNew.addRotation(X1, Y1, ROT)
                                    layerNew.setChangeSide(X1, Y1, warst)
                                    layerNew.setFace()
                            except Exception as e:
                                FreeCAD.Console.PrintWarning(str(e) + "1\n")
                                pass
                except Exception as e:
                    FreeCAD.Console.PrintWarning(str(e) + "2\n")
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
        #if self.dialogMAIN.plytkaPCB_elementy.isChecked():
            #partsError = self.addParts(self.getParts(), doc, groupBRD, self.dialogMAIN.gruboscPlytki.value(), self.dialogMAIN.plytkaPCB_elementyKolory.isChecked(), self.dialogMAIN.adjustParts.isChecked(), self.dialogMAIN.plytkaPCB_grupujElementy.isChecked(), self.dialogMAIN.partMinX.value(), self.dialogMAIN.partMinY.value(), self.dialogMAIN.partMinZ.value())
            #if self.dialogMAIN.plytkaPCB_plikER.isChecked():
                #self.generateErrorReport(partsError, filename)
        if self.dialogMAIN.plytkaPCB_elementy.isChecked():
            partsError = self.getParts(self.dialogMAIN.plytkaPCB_elementyKolory.isChecked(), self.dialogMAIN.adjustParts.isChecked(), self.dialogMAIN.plytkaPCB_grupujElementy.isChecked(), self.dialogMAIN.partMinX.value(), self.dialogMAIN.partMinY.value(), self.dialogMAIN.partMinZ.value())
            if self.dialogMAIN.plytkaPCB_plikER.isChecked():
                self.generateErrorReport(partsError, filename)
        #  dodatkowe warstwy
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
                
                if ID in [21, 22]:
                    self.getSilkLayer(doc, ID, grp, name, color, transp)
                elif ID in [1, 16]:  # paths
                    self.generatePaths(self.getPaths(ID), doc, grp, name, color, ID, transp)
                elif ID in [17, 18]:
                    self.getPads(doc, ID, grp, name, color, transp)
                elif ID == 0:  # annotations
                    self.addAnnotations(self.getAnnotations(), doc, color)
        ##
        return doc
        
    def setUnit(self, value, version):
        if version:
            return float("%.1f" % (value / 10000.))
        else:  # no file version def
            return float("%.1f" % (value / 1000.))
            
    def getViaParameters(self, via, version):
        x = self.setUnit(via["pos"][0], version)
        y = self.setUnit(via["pos"][1], version) * (-1)
        width = self.setUnit(via["width"], version) / 2.
        height = self.setUnit(via["height"], version) / 2.
        drill = self.setUnit(via["drill"], version) / 2.
        
        return (x, y, drill, height, width)
        
    def getHolesPrameters(self, hole, version):
        diameter = self.setUnit(hole["diameter"], version) / 2.
        x = self.setUnit(hole["pos"][0], version)
        y = self.setUnit(hole["pos"][1], version) * (-1)
        
        return (x, y, diameter)

    def getLineParameters(self, line, version):
        x1 = self.setUnit(line["pta"][0], version)
        y1 = self.setUnit(line["pta"][1], version) * (-1)
        x2 = self.setUnit(line["ptb"][0], version)
        y2 = self.setUnit(line["ptb"][1], version) * (-1)
        width = self.setUnit(line["width"], version)
        
        return (x1, y1, x2, y2, width)
        
    def gerCircleParameters(self, circle, version):
        x = self.setUnit(circle['pos'][0], version)
        y = self.setUnit(circle['pos'][1], version) * (-1)
        r = sqrt(abs(self.setUnit(circle['ofsa'][0], version)) ** 2 + abs(self.setUnit(circle['ofsa'][1], version)) ** 2)
        width = self.setUnit(circle["width"], version)
        
        if width == 0:
            width = 0.01
        
        return (x, y, r, width)
        
    def getArcParameters(self, arc, version):
        xs = self.setUnit(arc['pos'][0], version)
        ys = self.setUnit(arc['pos'][1], version)
        
        x1 = self.setUnit(arc['ofsa'][0], version)
        y1 = self.setUnit(arc['ofsa'][1], version)
        
        x2 = self.setUnit(arc['ofsb'][0], version)
        y2 = self.setUnit(arc['ofsb'][1], version)
        
        angle = float("%.1f" % ((atan2(y2, x2) - atan2(y1, x1)) * 180 / 3.14))
        #
        x1 = self.setUnit(arc['ofsa'][0], version) + xs
        y1 = self.setUnit(arc['ofsa'][1], version) + ys
        
        [x2R, y2R] = self.obrocPunkt2([x1, y1], [xs, ys], angle)
        
        #FreeCAD.Console.PrintWarning(u"angle = {0}\n".format(angle))
        #FreeCAD.Console.PrintWarning(u"xs = {0}\n".format(xs))
        #FreeCAD.Console.PrintWarning(u"ys = {0}\n".format(ys))
        #FreeCAD.Console.PrintWarning(u"x1 = {0}\n".format(x1))
        #FreeCAD.Console.PrintWarning(u"y1 = {0}\n".format(y1))
        #FreeCAD.Console.PrintWarning(u"x2R = {0}\n".format(x2R))
        #FreeCAD.Console.PrintWarning(u"y2R = {0}\n\n".format(y2R))
        
        x2R = float("%.1f" % x2R)
        y2R = float("%.1f" % y2R)
        
        if angle < 0:
            angle = angle - 360
            
        width = self.setUnit(arc['width'], version)

        return [x1, y1 * -1, x2R, y2R * -1, angle, width]
        
    def getPCB(self):
        PCB = []
        wygenerujPada = True
        ##
        dane1 = self.projektBRD["elts"]
        for i in dane1:
            if i["_t"] == "Segment" and i["layer"] == 20:
                (x1, y1, x2, y2, width) = self.getLineParameters(i, self.fileVersion)
                
                PCB.append(['Line', x1, y1, x2, y2])
            elif i["_t"] == "Arc" and i["layer"] == 20 and i["ofsa"] != i["ofsb"]:
                (x1, y1, x2, y2, curve, width) = self.getArcParameters(i, self.fileVersion)
                
                PCB.append(['Arc', x1, y1, x2, y2, curve])
                wygenerujPada = False
            elif i["_t"] == "Arc" and i["layer"] == 20 and i["ofsa"] == i["ofsb"]:
                (x, y, r, width) = self.gerCircleParameters(i, self.fileVersion)
                
                PCB.append(['Circle', x, y, r])
        #####
        if self.dialogMAIN.razenBiblioteki != "":
            for i in self.projektBRD["elts"]:
                if i["_t"] == "Footprint":
                    if not i['mirror']:
                        warst = 1  # top side
                    else:
                        warst = 0  # bottom side
                    
                    library = i['lib']
                    package = i['part']
                    X1 = self.setUnit(i['pos'][0], self.fileVersion)  # punkt wzgledem ktorego dokonany zostanie obrot
                    Y1 = self.setUnit(i['pos'][1], self.fileVersion) * (-1)  # punkt wzgledem ktorego dokonany zostanie obrot
                    ROT = i['angle'] * (-1)
                    
                    lineList = self.znajdzBiblioteke(library, package)
                    if not lineList:
                        continue
                    
                    try:
                        fileVersion = lineList["version"]
                    except:
                        fileVersion = None
                    
                    for j in lineList["elts"]:
                        try:
                            if j["_t"] == "Segment" and j["layer"] == 20:
                                (x1, y1, x2, y2, width) = self.getLineParameters(j, fileVersion)
                                x1 += X1
                                y1 += Y1
                                x2 += X1
                                y2 += Y1
                                
                                [x1, y1] = self.obrocPunkt2([x1, y1], [X1, Y1], ROT)
                                [x2, y2] = self.obrocPunkt2([x2, y2], [X1, Y1], ROT)
                                if warst == 0:
                                    x1 = self.odbijWspolrzedne(x1, X1)
                                    x2 = self.odbijWspolrzedne(x2, X1)
                                
                                PCB.append(['Line', x1, y1, x2, y2])
                            elif j["_t"] == "Arc" and j["layer"] == 20 and j["ofsa"] == j["ofsb"]:
                                (x, y, r, width) = self.gerCircleParameters(j, fileVersion)
                                
                                [x, y] = self.obrocPunkt2([x, y], [X1, Y1], ROT)
                                if warst == 0:
                                    x = self.odbijWspolrzedne(x, X1)
                                
                                PCB.append(['Circle', x, y, r])
                            elif j["_t"] == "Arc" and j["layer"] == 20:
                                (x1, y1, x2, y2, curve, width) = self.getArcParameters(j, fileVersion)
                                x1 += X1
                                y1 += Y1
                                x2 += X1
                                y2 += Y1
                                
                                [x1, y1] = self.obrocPunkt2([x1, y1], [X1, Y1], ROT)
                                [x2, y2] = self.obrocPunkt2([x2, y2], [X1, Y1], ROT)
                                if warst == 0:
                                    x1 = self.odbijWspolrzedne(x1, X1)
                                    x2 = self.odbijWspolrzedne(x2, X1)
                                    curve *= -1
                                
                                PCB.append(['Arc', x1, y1, x2, y2, curve])
                                wygenerujPada = False
                        except Exception as e:
                            FreeCAD.Console.PrintWarning(str(e) + "1\n")
                            pass
        #
        return [PCB, wygenerujPada]
