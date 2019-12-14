# -*- coding: utf8 -*-
#****************************************************************************
#*                                                                          *
#*   EaglePCB_2_FreeCAD                                                     *
#*   Copyright (c) 2013                                                     *
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
#import PartDesign
import Part
import Draft
import FreeCADGui
import re
import os
#from xml.dom import minidom
from math import sin, cos, fabs, radians
from PyQt4 import QtGui, QtCore
import ConfigParser

from conf import *
from objects import *
from dataBase import dataBase
from mainForms import *

#__currentPath__ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class dialogMAIN(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.setWindowTitle("PCB settings")
        self.setCursor(QtGui.QCursor(QtCore.Qt.WhatsThisCursor))
        #
        self.plytkaPCB = QtGui.QCheckBox(u"Board")
        self.plytkaPCB.setDisabled(True)
        self.plytkaPCB.setChecked(True)
        #######
        self.gruboscPlytki = QtGui.QDoubleSpinBox(self)
        self.gruboscPlytki.setSingleStep(0.1)
        self.gruboscPlytki.setValue(2.0)
        self.gruboscPlytki.setSuffix(" mm")
        #######
        self.plytkaPCB_otwory = QtGui.QCheckBox(u"Holes")
        self.plytkaPCB_otwory.setChecked(True)
        #######
        #self.plytkaPCB_PADS = QtGui.QCheckBox(u"Vias")
        #self.plytkaPCB_PADS.setChecked(True)
        #######
        self.plytkaPCB_plikER = QtGui.QCheckBox(u"Generate report with unknown parts")
        self.plytkaPCB_plikER.setChecked(False)
        #######
        self.plytkaPCB_elementy = QtGui.QCheckBox(u"Parts")
        self.plytkaPCB_elementy.setChecked(True)
        #######
        self.plytkaPCB_elementyKolory = QtGui.QCheckBox(u"Colorize elements")
        self.plytkaPCB_elementyKolory.setChecked(True)
        #######
        #######
        self.connect(self.plytkaPCB_elementy, QtCore.SIGNAL("toggled (bool)"), self.plytkaPCB_plikER.setChecked)
        self.connect(self.plytkaPCB_elementy, QtCore.SIGNAL("toggled (bool)"), self.plytkaPCB_plikER.setEnabled)
        
        self.connect(self.plytkaPCB_elementy, QtCore.SIGNAL("toggled (bool)"), self.plytkaPCB_elementyKolory.setChecked)
        self.connect(self.plytkaPCB_elementy, QtCore.SIGNAL("toggled (bool)"), self.plytkaPCB_elementyKolory.setEnabled)
        #######
        #######
        #przyciski
        buttons = QtGui.QDialogButtonBox()
        buttons.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
        buttons.addButton("Accept", QtGui.QDialogButtonBox.AcceptRole)
        self.connect(buttons, QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        self.connect(buttons, QtCore.SIGNAL("rejected()"), self, QtCore.SLOT("reject()"))
        #
        self.spisWarstw = tabela()
        self.spisWarstw.setColumnCount(5)
        self.spisWarstw.setHorizontalHeaderLabels(["", "ID", "", "", "Name"])
        self.spisWarstw.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.Fixed)
        self.spisWarstw.horizontalHeader().setResizeMode(1, QtGui.QHeaderView.Fixed)
        self.spisWarstw.horizontalHeader().setResizeMode(2, QtGui.QHeaderView.Fixed)
        self.spisWarstw.horizontalHeader().setResizeMode(3, QtGui.QHeaderView.Fixed)
        self.spisWarstw.horizontalHeader().resizeSection(0, 25)
        self.spisWarstw.horizontalHeader().resizeSection(1, 35)
        self.spisWarstw.horizontalHeader().resizeSection(2, 35)
        self.spisWarstw.horizontalHeader().resizeSection(3, 55)
        
        nr = 0
        for i, j in PCBwarstwy["freepcb"].items():
            self.spisWarstw.insertRow(nr)
                
            check = QtGui.QCheckBox()
            check.setStyleSheet("QCheckBox {margin:7px;}")
            self.spisWarstw.setCellWidget(self.spisWarstw.rowCount() - 1, 0, check)
               
            num = QtGui.QLabel(str(i))
            num.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            num.setContentsMargins(0, 0, 5, 0)
            self.spisWarstw.setCellWidget(self.spisWarstw.rowCount() - 1, 1, num)
            
            if j[2]:
                color = kolorWarstwy()
                color.setColor(j[2])
            else:
                color = QtGui.QLabel("")
            self.spisWarstw.setCellWidget(self.spisWarstw.rowCount() - 1, 2, color)
            
            if j[3]:
                transp = transpSpinBox()
                transp.setValue(j[3])
            else:
                transp = QtGui.QLabel("")
            self.spisWarstw.setCellWidget(self.spisWarstw.rowCount() - 1, 3, transp)
            
            name = QtGui.QTableWidgetItem(j[0])
            name.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self.spisWarstw.setItem(self.spisWarstw.rowCount() - 1, 4, name)
            
            nr += 1
        #######
        lay = QtGui.QGridLayout()
        lay.addWidget(self.spisWarstw, 0, 0, 7, 1)
        lay.addWidget(QtGui.QLabel(u"PCB Thickness"), 0, 1, 1, 1, QtCore.Qt.AlignLeft)
        lay.addWidget(self.gruboscPlytki, 0, 2, 1, 1)
        lay.addWidget(self.plytkaPCB, 1, 1, 1, 2)
        lay.addWidget(self.plytkaPCB_otwory, 2, 1, 1, 2)
        #lay.addWidget(self.plytkaPCB_PADS, 3, 1, 1, 2)
        lay.addWidget(self.plytkaPCB_elementy, 3, 1, 1, 2)
        lay.addWidget(self.plytkaPCB_elementyKolory, 4, 1, 1, 2)
        lay.addWidget(self.plytkaPCB_plikER, 5, 1, 1, 2)
        lay.addItem(QtGui.QSpacerItem(10, 20), 6, 1, 1, 2)
        lay.addWidget(buttons, 8, 0, 1, 3, QtCore.Qt.AlignRight)
        lay.setRowStretch(6, 10)
        lay.setColumnMinimumWidth(0, 250)
        lay.setColumnMinimumWidth(1, 120)
        self.setLayout(lay)


class FreePCB(mainPCB):
    def __init__(self):
        self.projektBRD_CP = None
        self.dialogMAIN = dialogMAIN()
        self.parts = {}
        self.mnoznik = 1./1000000.
        
        self.setDatabase(databaseList["freepcb"]['path'])

    def setProject(self, filename):         
        self.projektBRD_CP = ConfigParser.RawConfigParser()
        self.projektBRD_CP.read(filename)
        ##
        self.projektBRD = builtins.open(filename, "r").read()
        ##
        partsList = re.search(r'\[parts\]([\S\D]*)\[nets\]', self.projektBRD).groups()[0]
        partsList = re.findall(r'[part:]?([\S\D]*)', partsList)[0].split("part: ")
        partsList = [i.split("\n") for i in partsList][1:]
        
        self.parts = {}
        for i in partsList:
            self.parts[i[0]] = {}
            self.parts[i[0]]["shape"] = re.search(r'\"(.*)\"', i[3].split(": ")[1]).groups()[0]
            #self.parts[i[0]]["pos"] = [float(p)/1000000 for p in str(i[4].split(": ")[1]).split(" ")]
            paramHoles = str(i[4].split(": ")[1]).split(" ")
            self.parts[i[0]]["pos"] = [float(paramHoles[0])/1000000, float(paramHoles[1])/1000000, float(paramHoles[3])*(-1), int(paramHoles[2])]
        
        
        footprintsList = re.search(r'\[footprints\]([\S\D]*)\[board\]', self.projektBRD).groups()[0]
        footprintsList = re.findall(r'[name:]?([\S\D]*)', footprintsList)[0].split("name: ")[1:]

        footprints = {}
        holesList = {}

        for i in footprintsList:
            dane = i.split("pin: ")
            nazwa = re.search(r'\"(.*)\"', dane[0]).groups()[0].strip()
            
            footprints[re.search(r'(.*)', dane[0]).groups()[0].strip()] = {}  # package name
            
            try:
                if re.search(r'units: (.*)\r', dane[0]).groups()[0] == "MIL":  # mils
                    mnoznik = 0.0254
                else:
                    mnoznik = 1./1000000.
            except:
                mnoznik = 1./1000000.
            
            ############### HOLES/PADS
            holes = []
            pads = []
            for j in dane[1:]:
                #param = j.split("\r\n")
                param = j.split("\n")
                param = [d for d in param if str(d).strip() != ""]

                param_pin = re.search(r'".*" (.+?) (.+?) (.+?) (.*)', param[0].strip()).groups()
                #param_pad = re.search(r'.+?: (.+?) (.+?) (.+?) (.+?)[ ]?(.+?)', param[1].strip()).groups()

                pinHD = float(param_pin[0]) * mnoznik / 2.
                pinX = float(param_pin[1]) * mnoznik
                pinY = float(param_pin[2]) * mnoznik
                pinA = float(param_pin[3]) * (-1)
                #padS = param_pad[0]
                #padW = float(param_pad[1]) * mnoznik / 2.
                #padH = float(param_pad[2]) * mnoznik
                
                if len(param) > 2 and pinHD:
                    holes.append([pinX, pinY, pinHD])
                #pads.append([padS, padW, pinX, pinY, pinA, pinHD, padH])
                #
                for k in self.parts.keys():
                    if self.parts[k]["shape"] == nazwa:
                        if len(holes):
                            self.parts[k]["holes"] = holes
                            FreeCAD.Console.PrintWarning(str(holes) + "**************************\n")
                        #if len(pads):
                            #self.parts[k]["pads"] = pads
            ############### 
            ############### POLYLINE
            #danePolyline = re.split(r'(outline_polyline:|n_pins:)', i)
            #danePolyline = danePolyline[1:danePolyline.index('n_pins:')]
            #danePolyline = [o for o in danePolyline if o != "outline_polyline:"]
            #linieTop = []
            ##danePolyline = re.search(r'outline_polyline: ([\S\D]*) .*:', dane[0]).groups()[0].split("\r\n")
            #for param in danePolyline:
                ##param = param.split("\r\n")
                #param = param.split("\n")
                #pierwszy = re.search(r' (.*) (.*) (.*)', param[0]).groups()
                #param = param[1:-1]
                #p = False
                #for pp in range(len(param)):
                    #if param[pp].strip().startswith("next_corner:"):
                        #wsp = re.search(r'next_corner: (.*) (.*) (.*)', param[pp].strip()).groups()
                        
                        #if wsp[2] == '0':
                            #typeC = 'line'
                        #elif wsp[2] == '1':
                            #typeC = 'circle'
                        #elif wsp[2] == '2':
                            #typeC = 'arc'
                        
                        #if not p:
                            #linieTop.append([typeC, float(pierwszy[1])*mnoznik, float(pierwszy[2])*mnoznik, float(wsp[0])*mnoznik, float(wsp[1])*mnoznik])
                            #p = True
                        #else:
                            #if pp == len(param) - 1:
                                #linieTop.append([typeC, float(pierwszy[1])*mnoznik, float(pierwszy[2])*mnoznik, float(wsp[0])*mnoznik, float(wsp[1])*mnoznik])
                            #else:
                                #wsp_P = re.search(r'next_corner: (.*) (.*) (.*)', param[pp-1].strip()).groups()
                                #linieTop.append([typeC, float(wsp_P[0])*mnoznik, float(wsp_P[1])*mnoznik, float(wsp[0])*mnoznik, float(wsp[1])*mnoznik])
                    #elif param[pp].strip().startswith("close_polyline:"):
                        #wsp = re.search(r'close_polyline: (.*)', param[pp].strip()).groups()
                        #if wsp[0] == '0':
                            #wsp_P = re.search(r'next_corner: (.*) (.*) (.*)', param[pp-1].strip()).groups()
                            #linieTop.append([typeC, float(wsp_P[0])*mnoznik, float(wsp_P[1])*mnoznik, float(pierwszy[1])*mnoznik, float(pierwszy[2])*mnoznik])
                ##
                #for k in self.parts.keys():
                    #if self.parts[k]["shape"] == nazwa:
                        #if len(linieTop):
                            #self.parts[k]["polyline"] = []
            ###############

    def elementy(self, doc, groupBRD, gruboscPlytki, koloroweElemnty):
        self.__SQL__.reloadList()
        ##
        PCB_EL = []
        for i, j in self.parts.items():
            name = i
            package = j["shape"]
            #FreeCAD.Console.PrintWarning(package)
            value = ""
            x = j["pos"][0]
            y = j["pos"][1]
            library = j["shape"]
            rot = j["pos"][2]
            if j["pos"][3]:
                side = "BOTTOM"
            else:
                side = "TOP"
            
            PCB_EL.append([name, package, value, x, y, rot, side, library])
        #######
        return self.addParts(PCB_EL, doc, groupBRD, gruboscPlytki, koloroweElemnty)
    
    def pady(self, doc, layerNumber, gruboscPlytki, grp, layerName, layerColor):
        layerName = "{0}_{1}".format(layerName, layerNumber)
        layerSide = PCBwarstwy["eagle"][layerNumber][1]
        
        if layerSide == 1:  # gorna warstwa
            z = gruboscPlytki + 0.03
            #layerType = "LayerPad_Top"
        else:  # dolna warstwa
            z = -0.03
            #layerType = "LayerPad_Bottom"
            
        layerType = PCBwarstwy["freepcb"][layerNumber][4]
        
        ####
        layerS = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", layerName)
        layerNew = layerSilkObject(layerS, layerType)
        layerNew.holes = self.dialogMAIN.plytkaPCB_otwory.isChecked()
        ####
        #via
        viaList = re.findall(r'vtx: .+? (.+?) (.+?) .+? .+? ([1-9][0-9]*) ([1-9][0-9]*)\r', self.projektBRD)
        for i in viaList:
            x = float(i[0]) * self.mnoznik
            y = float(i[1]) * self.mnoznik
            drill = float(i[3]) * self.mnoznik / 2.
            diameter = float(i[2]) * self.mnoznik / 2.
            
            layerNew.addPadRound(x, y, diameter, drill, [])
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
                    
                    if padS == '1':  # circle
                        if drill > 0:
                            layerNew.addPadRound(x, y, diameter, drill, [X1, Y1, ROT], warst)
                        elif drill == 0 and layerSide == warst:  # smd
                            layerNew.addPadRound(x, y, diameter, False, [], warst)
                    elif padS == '2':  # square
                        a = diameter
                            
                        x1 = x - a
                        y1 = y - a
                        x2 = x + a
                        y2 = y + a
                        
                        poin = [[x1, y1, 0, x2, y1, 0], 
                                [x2, y1, 0, x2, y2, 0],
                                [x2, y2, 0, x1, y2, 0],
                                [x1, y2, 0, x1, y1, 0]]
                            
                        if drill > 0:
                            layerNew.addPadSquare(poin, [x, y, drill], [x, y, ROT_2], [X1, Y1, ROT], warst)
                        elif drill == 0 and layerSide == warst:  # smd
                            layerNew.addPadSquare(poin, [], [x, y, ROT_2], [X1, Y1, ROT], warst)
                    elif padS == '3' or padS == '4':  # rectangle / round rectangle (not supported)
                        dx = padH
                        dy = diameter
                        
                        x1 = x - dx
                        y1 = y - dy
                        x2 = x + dx
                        y2 = y + dy
                        
                        poin = [[x1, y1, 0, x2, y1, 0], 
                                [x2, y1, 0, x2, y2, 0],
                                [x2, y2, 0, x1, y2, 0],
                                [x1, y2, 0, x1, y1, 0]]
                        
                        if drill > 0:
                            layerNew.addPadSquare(poin, [x, y, drill], [x, y, ROT_2], [X1, Y1, ROT], warst)
                        elif drill == 0 and layerSide == warst:  # smd
                            layerNew.addPadRectangleSMD(poin, [x, y, ROT_2], [X1, Y1, ROT], warst)
                    elif padS == '5':  # long
                        if drill > 0:
                            layerNew.addPadLong2(x, y, diameter-padH/2, padH/2, padH, [x, y, drill], [x, y, ROT_2+90], [X1, Y1, ROT], warst)
                        elif drill == 0 and layerSide == warst:  # smd
                            layerNew.addPadLong2(x, y, diameter-padH/2, padH/2, padH, [], [x, y, ROT_2+90], [X1, Y1, ROT], warst)
                    elif padS == '6':  # octagon
                        if drill > 0:
                            layerNew.addPadOctagon(self.generateOctagon(x, y, diameter), [x, y, drill], [], [X1, Y1, ROT], warst)
                        elif drill == 0 and layerSide == warst:  # smd
                            layerNew.addPadOctagon(self.generateOctagon(x, y, diameter), [], [], [X1, Y1, ROT], warst)
            except KeyError:
                continue
        ###
        layerNew.generuj(layerS)
        viewProviderLayerSilkObject(layerS.ViewObject)
        layerS.Placement = FreeCAD.Placement(FreeCAD.Vector(0.0, 0.0, z), FreeCAD.Rotation(0.0, 0.0, 0.0, 1.0))
        layerS.ViewObject.ShapeColor = layerColor
        grp.addObject(layerS)
        #
        doc.recompute()

    def holes(self, doc):
        ''' holes/vias '''
        daneHOLES = []
        for i, j in self.parts.items():
            X1 = j["pos"][0]  # punkt wzgledem ktorego dokonany zostanie obrot
            Y1 = j["pos"][1]  # punkt wzgledem ktorego dokonany zostanie obrot
            ROT = j["pos"][2]  # kat o jaki zostana obrocone elementy

            sinKAT = float("%4.10f" % sin(radians(ROT)))
            cosKAT = float("%4.10f" % cos(radians(ROT)))
            
            try:
                for point in j["holes"]:
                    xs = point[0]
                    ys = point[1]
                    drill = point[2]
                    [xR, yR] = self.obrocPunkt([xs, ys], [X1, Y1], sinKAT, cosKAT)
                    
                    daneHOLES.append([xR, yR, drill])
            except KeyError:
                continue
        #via
        viaList = re.findall(r'vtx: .+? (.+?) (.+?) .+? .+? .+? ([1-9][0-9]*)\r', self.projektBRD)
        for i in viaList:
            xs = float(i[0]) * self.mnoznik
            ys = float(i[1]) * self.mnoznik
            drill = float(i[2]) * self.mnoznik / 2.
            
            daneHOLES.append([xs, ys, drill])
        ###
        self.generateHoles(doc, daneHOLES)
        doc.recompute()

    def PCB(self, doc, groupBRD, gruboscPlytki):
        PCB_PCB = []
        
        linie = self.projektBRD_CP.get("board", "outline").split("\n")
        linie = linie[1:]
        for i in range(len(linie)):
            dane = linie[i].split(" ")
            if i == len(linie) - 1:
                daneN = linie[0].split(" ")
            else:
                daneN = linie[i+1].split(" ")
                
            nextX = float(daneN[2]) * self.mnoznik
            nextY = float(daneN[3]) * self.mnoznik
            
            PCB_PCB.append([float(dane[2]) * self.mnoznik, float(dane[3]) * self.mnoznik, nextX, nextY])
        ##
        doc.addObject('Sketcher::SketchObject', 'Sketch_PCB')
        doc.Sketch_PCB.Placement = FreeCAD.Placement(FreeCAD.Vector(0.0, 0.0, 0.0), FreeCAD.Rotation(0.0, 0.0, 0.0, 1.0))
        ##
        nrP = 0
        for i in PCB_PCB:
            doc.Sketch_PCB.addGeometry(Part.Line(FreeCAD.Vector(i[0], i[1], 0), FreeCAD.Vector(i[2], i[3], 0)))
        
        for j in range(len(PCB_PCB)):
            if j < len(PCB_PCB) - 1:
                doc.Sketch_PCB.addConstraint(Sketcher.Constraint('Coincident', j, 2, j + 1, 1))  # kolejny element w tablicy
            else:
                doc.Sketch_PCB.addConstraint(Sketcher.Constraint('Coincident', j, 2, 0, 1))  # pierwszy element w tablicy
        ##
        FreeCADGui.activeDocument().Sketch_PCB.Visibility = False
        # PAD
        doc.recompute()
        doc.addObject("PartDesign::Pad", "Pad_PCB")
        doc.Pad_PCB.Sketch = doc.Sketch_PCB
        doc.Pad_PCB.Length = gruboscPlytki
        doc.Pad_PCB.Reversed = 0
        doc.Pad_PCB.Midplane = 0
        #doc.Pad_PCB.Length2 = 100.0
        doc.Pad_PCB.Type = 0
        doc.Pad_PCB.UpToFace = None
        doc.recompute()
        groupBRD.addObject(doc.Pad_PCB)
        FreeCADGui.activeDocument().getObject("Pad_PCB").ShapeColor = PCB_COLOR
    
    def elementyWarstwy(self, doc, layerNumber, gruboscPlytki, grp, layerName, layerColor):
        layerName = "{0}_{1}".format(layerName, layerNumber)
        layerSide = PCBwarstwy["freepcb"][layerNumber][1]
        
        if layerSide == 1:  # gorna warstwa
            z = gruboscPlytki + 0.02
            #layerType = "LayerSilkT"
        else:  # dolna warstwa
            z = -0.02
            #layerType = "LayerSilkB"
            
        layerType = PCBwarstwy["freepcb"][layerNumber][4]
        
        #ser = doc.addObject('Sketcher::SketchObject', layerName)
        #ser.Placement = FreeCAD.Placement(FreeCAD.Vector(0.0, 0.0, z), FreeCAD.Rotation(0.0, 0.0, 0.0, 1.0))
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
                        if j[0] == "line":
                            x1 = j[1]
                            y1 = j[2]
                            x2 = j[3]
                            y2 = j[4]
                            
                            layerNew.addLine([x1+X1, y1+Y1, 0, x2+X1, y2+Y1, 0], [X1, Y1, ROT], warst)
                        elif j[0] == "circle":
                            pass
                        elif j[0] == "arc":
                            pass
            except:
                pass
        #####
        #ser.ViewObject.LineColor = layerColor
        #ser.ViewObject.PointColor = layerColor
        #ser.ViewObject.PointSize = 1.0
        #grp.addObject(ser)
        #
        layerNew.generuj(layerS)
        viewProviderLayerSilkObject(layerS.ViewObject)
        layerS.Placement = FreeCAD.Placement(FreeCAD.Vector(0.0, 0.0, z), FreeCAD.Rotation(0.0, 0.0, 0.0, 1.0))
        layerS.ViewObject.ShapeColor = layerColor
        grp.addObject(layerS)
        #
        doc.recompute()

    def generate(self, doc, groupBRD, filename):
        self.PCB(doc, groupBRD, self.dialogMAIN.gruboscPlytki.value())
        if self.dialogMAIN.plytkaPCB_otwory.isChecked():
            self.holes(doc)
        if self.dialogMAIN.plytkaPCB_elementy.isChecked():
            PCB_ER = self.elementy(doc, groupBRD, self.dialogMAIN.gruboscPlytki.value(), self.dialogMAIN.plytkaPCB_elementyKolory.isChecked())
            if self.dialogMAIN.plytkaPCB_plikER.isChecked():
                self.brakujaceElementy(PCB_ER, filename)
        ##  dodatkowe warstwy
        grp = makeUnigueGroup('Layers', 'layersGroup')
        for i in range(self.dialogMAIN.spisWarstw.rowCount()):
            if self.dialogMAIN.spisWarstw.cellWidget(i, 0).isChecked():
                ID = int(self.dialogMAIN.spisWarstw.cellWidget(i, 1).text())
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
                    self.elementyWarstwy(doc, ID, self.dialogMAIN.gruboscPlytki.value(), grp, name, color)
                elif ID in [17, 18]:
                    self.pady(doc, ID, self.dialogMAIN.gruboscPlytki.value(), grp, name, color)
        return doc
    
