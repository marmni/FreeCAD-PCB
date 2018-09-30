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
import glob
import re
import os
import zipfile
from PySide import QtGui
#
import PCBconf
from PCBobjects import *
from formats.PCBmainForms import *
from command.PCBgroups import *


class dialogMAIN(dialogMAIN_FORM):
    def __init__(self, filename=None, parent=None):
        dialogMAIN_FORM.__init__(self, parent)
        self.databaseType = "fidocadj"
        
        self.projektBRD = builtins.open(filename, "r").read().replace("\r", "")
        self.layersNames = {}
        self.getLayersNames()
        ####
        self.generateLayers()
        self.spisWarstw.sortItems(1)
        #
        self.fidocadjBiblioteki = QtGui.QLineEdit('')
        if PCBconf.supSoftware[self.databaseType]['libPath'] != "":
            self.fidocadjBiblioteki.setText(PCBconf.supSoftware[self.databaseType]['libPath'])
        
        lay = QtGui.QHBoxLayout()
        lay.addWidget(QtGui.QLabel('Library'))
        lay.addWidget(self.fidocadjBiblioteki)
        self.lay.addLayout(lay, 12, 0, 1, 6)
    
    def getLayersNames(self):
        elem = re.findall(r'FJC N (.+?) (.+?)\n', self.projektBRD)
        for i in elem:
            self.layersNames[int(i[0])] = i[1]


class FidoCadJ_PCB(mainPCB):
    def __init__(self, filename):
        mainPCB.__init__(self, None)
        
        self.dialogMAIN = dialogMAIN(filename)
        self.mnoznik = 0.127
        self.databaseType = "fidocadj"
        
    def getPolygons(self, section, layer, m=[0,0], filled=False):
        if section.strip() == "":
            FreeCAD.Console.PrintWarning("Incorrect parameter!\n".format(e))
            return []
        
        if not isinstance(layer, list):
            layer = [layer]
        
        data = []
        for lay in layer:
            if filled:
                dane1 = re.findall(r'PP\s+(.+?)\s+%s\s+' % lay, section)
            else:
                dane1 = re.findall(r'PV\s+(.+?)\s+%s\s+' % lay, section)

            for i in dane1:
                pass
                
        return data
        
    def getLines(self, section, layer, m=[0,0]):
        if section.strip() == "":
            FreeCAD.Console.PrintWarning("Incorrect parameter!\n".format(e))
            return []
        
        if not isinstance(layer, list):
            layer = [layer]
        
        data = []
        for lay in layer:
            dane1 = re.findall(r'LI\s+([-,.0-9]+)\s+([-,.0-9]+)\s+([-,.0-9]+)\s+([-,.0-9]+)\s+%s\s+' % lay, section)
            dane1 += re.findall(r'PL\s+([-,.0-9]+)\s+([-,.0-9]+)\s+([-,.0-9]+)\s+([-,.0-9]+)\s+([-,.0-9]+)\s+%s\s+' % lay, section)
            
            for i in dane1:
                if m[0] == 0:
                    x1 = float(i[0]) * self.mnoznik
                    x2 = float(i[2]) * self.mnoznik
                else:
                    x1 = ((m[0] / 2 - 100 + float(i[0])) + m[0] / 2) * self.mnoznik
                    x2 = ((m[0] / 2 - 100 + float(i[2])) + m[0] / 2) * self.mnoznik
                
                if m[1] == 0:
                    y1 = float(i[1]) * self.mnoznik * (-1.)
                    y2 = float(i[3]) * self.mnoznik * (-1.)
                else:
                    y1 = ((m[1] / 2 - 100 + float(i[1])) + m[1] / 2) * self.mnoznik * (-1)
                    y2 = ((m[1] / 2 - 100 + float(i[3])) + m[1] / 2) * self.mnoznik * (-1)
                
                try:
                    width = float(i[4]) * self.mnoznik
                except:
                    width = 0
                
                if [x1, y1] == [x2, y2]:
                    continue
                    
                if width == 0:
                    width = 0.1
                
                data.append({
                    'x1': x1,
                    'y1': y1,
                    'x2': x2,
                    'y2': y2,
                    'width': width,
                    'layer': lay,
                })
            
        return data
    
    def getCircles(self, section, layer, f=[], m=[0,0], filled=False):
        if section.strip() == "":
            FreeCAD.Console.PrintWarning("Incorrect parameter!\n".format(e))
            return []
        
        if not isinstance(layer, list):
            layer = [layer]
        
        data = []
        for lay in layer:
            if filled:
                dane1 = re.findall(r'EP\s+([-,.0-9]+)\s+([-,.0-9]+)\s+([-,.0-9]+)\s+([-,.0-9]+)\s+%s\s+' % lay, section)
            else:
                dane1 = re.findall(r'EV\s+([-,.0-9]+)\s+([-,.0-9]+)\s+([-,.0-9]+)\s+([-,.0-9]+)\s+%s\s+' % lay, section)

            for i in dane1:
                if m[0] == 0:
                    x1 = float(i[0]) * self.mnoznik
                    x2 = float(i[2]) * self.mnoznik
                else:
                    x1 = ((m[0] / 2 - 100 + float(i[0])) + m[0] / 2) * self.mnoznik
                    x2 = ((m[0] / 2 - 100 + float(i[2])) + m[0] / 2) * self.mnoznik
                
                if m[1] == 0:
                    y1 = float(i[1]) * self.mnoznik * (-1)
                    y2 = float(i[3]) * self.mnoznik * (-1)
                else:
                    y1 = ((m[1] / 2 - 100 + float(i[1])) + m[1] / 2) * self.mnoznik * (-1)
                    y2 = ((m[1] / 2 - 100 + float(i[3])) + m[1] / 2) * self.mnoznik * (-1)
                
                dx = float("%4.4f" % ((x1 - x2) / 2.))
                dy = float("%4.4f" % ((y1 - y2) / 2.))
                
                xs = x1 + dx * (-1)
                ys = y1 + dy * (-1)
                r = abs(dx)
                width = 0.1
                
                out = {'x': xs,
                        'y': ys,
                        'r': r,
                        'dx': abs(dx),
                        'dy': abs(dy),
                        'width': width,
                        'layer': lay,
                        'filled': filled, 
                    }
                
                if abs(dx) == abs(dy):
                    out['type'] = 'circle'
                else:
                    out['type'] = 'elipse'
                
                if 'c' in f and abs(dx) == abs(dy):  # circle
                    data.append(out)
                elif 'e' in f and abs(dx) != abs(dy):  # elipse
                    data.append(out)
                else:
                    data.append(out)
                
        return data
        
    def getRectangles(self, section, layer, m=[0,0], filled=False):
        if section.strip() == "":
            FreeCAD.Console.PrintWarning("Incorrect parameter!\n".format(e))
            return []
        
        if not isinstance(layer, list):
            layer = [layer]
        
        data = []
        for lay in layer:
            if filled:
                dane1 = re.findall(r'RP\s+([-,.0-9]+)\s+([-,.0-9]+)\s+([-,.0-9]+)\s+([-,.0-9]+)\s+%s\s+' % lay, section)
            else:
                dane1 = re.findall(r'RV\s+([-,.0-9]+)\s+([-,.0-9]+)\s+([-,.0-9]+)\s+([-,.0-9]+)\s+%s\s+' % lay, section)

            for i in dane1:
                if m[0] == 0:
                    x1 = float(i[0]) * self.mnoznik
                    x2 = float(i[2]) * self.mnoznik
                else:
                    x1 = ((m[0] / 2 - 100 + float(i[0])) + m[0] / 2) * self.mnoznik
                    x2 = ((m[0] / 2 - 100 + float(i[2])) + m[0] / 2) * self.mnoznik
                
                if m[1] == 0:
                    y1 = float(i[1]) * self.mnoznik * (-1.)
                    y2 = float(i[3]) * self.mnoznik * (-1.)
                else:
                    y1 = ((m[1] / 2 - 100 + float(i[1])) + m[1] / 2) * self.mnoznik * (-1)
                    y2 = ((m[1] / 2 - 100 + float(i[3])) + m[1] / 2) * self.mnoznik * (-1)
                
                if [x1, y1] == [x2, y2]:
                    continue
                
                data.append({
                    'x1': x1,
                    'y1': y1,
                    'x2': x2,
                    'y2': y2,
                    'layer': lay,
                    'filled': filled, 
                })
                
        return data
    
    ##############################
    # MAIN FUNCTIONS
    ##############################
    
    def setProject(self, filename):
        self.projektBRD = builtins.open(filename, "r").read().replace("\r\n", "\n").replace("\r", "\n")
        
    def getParts(self, koloroweElemnty, adjustParts, groupParts, partMinX, partMinY, partMinZ):
        PCB_ER = []
        
        elementy = re.findall(r'MC ([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+) (.+?)\.(.*)(\nFCJ\n)?(TY [0-9]+ [0-9]+ [0-9]+ [0-9]+ [0-9]+ [0-9]+ [0-9]+ \* .*\n)?(TY [0-9]+ [0-9]+ [0-9]+ [0-9]+ [0-9]+ [0-9]+ [0-9]+ \* .*\n)?', self.projektBRD)
        for i in elementy:
            name = 'NoName'
            value = ''
            
            x = float(i[0]) * self.mnoznik
            y = float(i[1]) * self.mnoznik * (-1)
            rot = int(i[2]) * (-90)
            if i[3] == '1':  # bottom
                side = "BOTTOM"
            else:
                side = "TOP"
            library = i[4]
            package = i[5]
            
            ######
            EL_Name = ['', x, y, 0.7, rot, side, "bottom-left", False, 'None', '', True]
            EL_Value = ['', x, y, 0.7, rot, side, "bottom-left", False, 'None', '', True]
            
            if i[-1] != '':
                nameN = re.search('TY ([0-9]+) ([0-9]+) [0-9]+ [0-9]+ [0-9]+ [0-9]+ [0-9]+ \* (.*)\n', i[-2]).groups()
                valueN = re.search('TY ([0-9]+) ([0-9]+) [0-9]+ [0-9]+ [0-9]+ [0-9]+ [0-9]+ \* (.*)\n', i[-1]).groups()
                
                if nameN[2].strip() != '':
                    EL_Name[0] = name = nameN[2]
                    EL_Name[1] = float(nameN[0]) * self.mnoznik
                    EL_Name[2] = float(nameN[1]) * self.mnoznik * (-1)
                if valueN[2].strip() != '':
                    EL_Value[0] = value = valueN[2]
                    EL_Value[1] = float(valueN[0]) * self.mnoznik
                    EL_Value[2] = float(valueN[1]) * self.mnoznik * (-1)
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
                try:
                    transp = self.dialogMAIN.spisWarstw.cellWidget(i, 3).value()
                except:
                    transp = None

                if ID in [17, 18]:  # pady
                    self.getPads(doc, ID, grp, name, color, transp)
                elif ID in [1, 2]:  # paths
                    self.generatePaths(self.getPaths(ID), doc, grp, name, color, ID, transp)
                elif ID in [3, 4]:
                    self.getSilkLayer(doc, ID, grp, name, color, transp)
                elif ID == 0:  # annotations
                    self.addAnnotations(self.getAnnotations(), doc, color)
        
        return doc

    #def pogrupujLinieObramowania(self, linieObramowania):
        #pogrupowaneLinie = []
        #pogrupowaneLinie.append([linieObramowania[0]])
        #del linieObramowania[0]
        
        #if pogrupowaneLinie[0][0][0] == pogrupowaneLinie[0][0][2]:  # wymuszenie ruchu przeciwnie do wskazowek zegara
            #if pogrupowaneLinie[0][0][3] > pogrupowaneLinie[0][0][1]:
                #pogrupowaneLinie[0][0] = [pogrupowaneLinie[0][0][0], pogrupowaneLinie[0][0][3], pogrupowaneLinie[0][0][2], pogrupowaneLinie[0][0][1], pogrupowaneLinie[0][0][4], pogrupowaneLinie[0][0][0], pogrupowaneLinie[0][0][1], pogrupowaneLinie[0][0][2], pogrupowaneLinie[0][0][3]]
        #elif pogrupowaneLinie[0][0][0] > pogrupowaneLinie[0][0][2]:
            #pogrupowaneLinie[0][0] = [pogrupowaneLinie[0][0][2], pogrupowaneLinie[0][0][3], pogrupowaneLinie[0][0][0], pogrupowaneLinie[0][0][1], pogrupowaneLinie[0][0][4], pogrupowaneLinie[0][0][0], pogrupowaneLinie[0][0][1], pogrupowaneLinie[0][0][2], pogrupowaneLinie[0][0][3]]
        #else:
            #pogrupowaneLinie[0][0] = [pogrupowaneLinie[0][0][0], pogrupowaneLinie[0][0][1], pogrupowaneLinie[0][0][2], pogrupowaneLinie[0][0][3], pogrupowaneLinie[0][0][4], pogrupowaneLinie[0][0][0], pogrupowaneLinie[0][0][1], pogrupowaneLinie[0][0][2], pogrupowaneLinie[0][0][3]]
        
        #nr = 0
        ##poz = 0
        
        #while len(linieObramowania):
            #for i in linieObramowania:
                #if i[2] == pogrupowaneLinie[nr][-1][2] and i[3] == pogrupowaneLinie[nr][-1][3]:
                    #t = [i[2], i[3], i[0], i[1], i[4], i[0], i[1], i[2], i[3]]
                    #pogrupowaneLinie[nr].append(t)
                    #del linieObramowania[linieObramowania.index(i)]
                    #break
                #elif i[0] == pogrupowaneLinie[nr][-1][2] and i[1] == pogrupowaneLinie[nr][-1][3]:
                    #t = [i[0], i[1], i[2], i[3], i[4], i[0], i[1], i[2], i[3]]
                    #pogrupowaneLinie[nr].append(t)
                    ##pogrupowaneLinie[nr].append(i)
                    #del linieObramowania[linieObramowania.index(i)]
                    #break
                #else:
                    #continue
            
            #if pogrupowaneLinie[nr][-1][2] == pogrupowaneLinie[nr][0][0] and pogrupowaneLinie[nr][-1][3] == pogrupowaneLinie[nr][0][1]:
                #try:
                    #pogrupowaneLinie.append([linieObramowania[0]])
                    #del linieObramowania[0]
                    
                    #if pogrupowaneLinie[-1][0][0] == pogrupowaneLinie[-1][0][2]:  # wymuszenie ruchu przeciwnie do wskazowek zegara
                        #if pogrupowaneLinie[-1][0][3] > pogrupowaneLinie[-1][0][1]:
                            #pogrupowaneLinie[-1][0] = [pogrupowaneLinie[-1][0][0], pogrupowaneLinie[-1][0][3], pogrupowaneLinie[-1][0][2], pogrupowaneLinie[-1][0][1], pogrupowaneLinie[-1][0][4], pogrupowaneLinie[-1][0][0], pogrupowaneLinie[-1][0][1], pogrupowaneLinie[-1][0][2], pogrupowaneLinie[-1][0][3]]
                    #elif pogrupowaneLinie[-1][0][0] > pogrupowaneLinie[-1][0][2]:
                        #pogrupowaneLinie[-1][0] = [pogrupowaneLinie[-1][0][2], pogrupowaneLinie[-1][0][3], pogrupowaneLinie[-1][0][0], pogrupowaneLinie[-1][0][1], pogrupowaneLinie[-1][0][4], pogrupowaneLinie[-1][0][0], pogrupowaneLinie[-1][0][1], pogrupowaneLinie[-1][0][2], pogrupowaneLinie[-1][0][3]]
                    #else:
                        #pogrupowaneLinie[-1][0] = [pogrupowaneLinie[-1][0][0], pogrupowaneLinie[-1][0][1], pogrupowaneLinie[-1][0][2], pogrupowaneLinie[-1][0][3], pogrupowaneLinie[-1][0][4], pogrupowaneLinie[-1][0][0], pogrupowaneLinie[-1][0][1], pogrupowaneLinie[-1][0][2], pogrupowaneLinie[-1][0][3]]
                    
                    ##if pogrupowaneLinie[-1][0][0] > pogrupowaneLinie[-1][0][2]:  # wymuszenie ruchu przeciwnie do wskazowek zegara
                        ##pogrupowaneLinie[-1][0] = [pogrupowaneLinie[-1][0][2], pogrupowaneLinie[-1][0][3], pogrupowaneLinie[-1][0][0], pogrupowaneLinie[-1][0][1], pogrupowaneLinie[-1][0][4]]

                    #nr += 1
                #except:
                    #linieObramowania = []
        #return pogrupowaneLinie
        
    def znajdzBiblioteke(self, libName):
        libPath = str(self.dialogMAIN.fidocadjBiblioteki.text()).split(';')
        for lib in libPath:
            if lib.endswith(".jar"):
                try:
                    plikJAR = zipfile.ZipFile(lib, 'r')
                    for i in plikJAR.namelist():
                        if i.split('/')[-1].split('.')[0].lower() == libName:
                        #if i.startswith('lib/'):
                            #docname = i.split('/')[1].split('.')[0]
                            #if docname.lower() == libName:
                            return plikJAR.read(i).replace("\r\n", "\n").replace("\r", "\n")
                except Exception as e:
                    FreeCAD.Console.PrintWarning(str(e) + "\n")
                    return False
            else:
                biblioteki = glob.glob(os.path.join(lib, '*.fcl'))
                for i in biblioteki:
                    docname = os.path.splitext(os.path.basename(i))[0]
                    if docname.lower() == libName:
                        return open(i, 'r').read().replace("\r\n", "\n").replace("\r", "\n")
        return False
        
    def getPaths(self, layerNumber):
        wires = []
        signal = []
        #
        for i in self.getLines(self.projektBRD, layerNumber):
            wires.append(['line', i['x1'], i['y1'], i['x2'], i['y2'], i['width']])
        #
        wires.append(signal)
        return wires
        
    def getSilkLayer(self, doc, layerNumber, grp, layerName, layerColor, defHeight):
        layerName = "{0}_{1}".format(layerName, layerNumber)
        #layerSide = PCBconf.PCBlayers[PCBconf.softLayers["fidocadj"][layerNumber][1]][0]
        layerType = PCBconf.PCBlayers[PCBconf.softLayers["fidocadj"][layerNumber][1]][3]
        
        #ser = doc.addObject('Sketcher::SketchObject', layerName)
        #ser.Placement = FreeCAD.Placement(FreeCAD.Vector(0.0, 0.0, z), FreeCAD.Rotation(0.0, 0.0, 0.0, 1.0))
        layerS = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", layerName)
        layerNew = layerSilkObject(layerS, layerType)
        layerNew.defHeight = defHeight
        # empty polygon
        dane1 = re.findall(r'PV (.+?) 3\n', self.projektBRD)
        for i in dane1:
            punkty = i.split(" ")
            for j in range(0, len(punkty), 2):
                x1 = float(punkty[j]) * self.mnoznik
                y1 = float(punkty[j + 1]) * self.mnoznik * (-1)
               
                if j + 3 > len(punkty):
                    x2 = float(punkty[0]) * self.mnoznik
                    y2 = float(punkty[1]) * self.mnoznik * (-1)
                else:
                    x2 = float(punkty[j + 2]) * self.mnoznik
                    y2 = float(punkty[j + 3]) * self.mnoznik * (-1)
                    
                if [x1, y1] != [x2, y2]:
                    layerNew.createObject()
                    layerNew.addLineWidth(x1, y1, x2, y2, 0.1)
                    layerNew.setFace()
        # filled polygon
        dane1 = re.findall(r'PP (.+?) 3\n', self.projektBRD)
        polygonL = []
        for i in dane1:
            punkty = i.split(" ")
            for j in range(0, len(punkty), 2):
                x1 = float(punkty[j]) * self.mnoznik
                y1 = float(punkty[j + 1]) * self.mnoznik * (-1)
               
                if j + 3 > len(punkty):
                    x2 = float(punkty[0]) * self.mnoznik
                    y2 = float(punkty[1]) * self.mnoznik * (-1)
                else:
                    x2 = float(punkty[j + 2]) * self.mnoznik
                    y2 = float(punkty[j + 3]) * self.mnoznik * (-1)
                    
                if [x1, y1] != [x2, y2]:
                    polygonL.append(['Line', x1, y1, x2, y2])
            
            layerNew.createObject()
            layerNew.addPolygon(polygonL)
            layerNew.setFace()
            #layerNew.addObject(layerNew.addPolygonFull(polygonL))
        #
        #dane1 = re.findall(r'CV (.+?) (.*?) 3\n', self.projektBRD)
        #for i in dane1:
            ##closeP = int(i[0])
            #points = i[1].split(" ")
            
            #poin = []
            #for j in range(0, len(points), 2):
                #x = float(points[j]) * self.mnoznik
                #y = float(points[j + 1]) * self.mnoznik * (-1)
                
                #poin.append(FreeCAD.Vector(x, y, 0.0))
            
            #layerNew.addObject(layerNew.addBSpline(poin))
        ##
        #dane1 = re.findall(r'CP (.+?) (.*?) 3\n', self.projektBRD)
        #for i in dane1:
            ##closeP = int(i[0])
            #points = i[1].split(" ")
            
            #poin = []
            #for j in range(0, len(points), 2):
                #x = float(points[j]) * self.mnoznik
                #y = float(points[j + 1]) * self.mnoznik * (-1)
                
                #poin.append(FreeCAD.Vector(x, y, 0.0))
            
            #layerNew.addObject(layerNew.makeFace(layerNew.addBSpline(poin)))
        # lines
        for i in self.getLines(self.projektBRD, 3):
            layerNew.createObject()
            layerNew.addLineWidth(i['x1'], i['y1'], i['x2'], i['y2'], i['width'])
            layerNew.setFace()
        # circles/elipses
        for i in self.getCircles(self.projektBRD, 3) + self.getCircles(self.projektBRD, 3, filled=True):
            if i['filled']:
                if i['type'] == 'circle':
                    layerNew.createObject()
                    layerNew.addCircle(i['x'], i['y'], i['r'])
                    layerNew.setFace()
                else:
                    layerNew.createObject()
                    layerNew.addElipse(i['x'], i['y'], i['dx'] - i['r'] / 2., i['dy'] - i['r'] / 2.)
                    layerNew.setFace()
            else:  # empty circle
                if i['type'] == 'circle':
                    layerNew.createObject()
                    layerNew.addCircle(i['x'], i['y'], i['r'], i['width'])
                    layerNew.setFace()
                else:
                    pass
                    #layerNew.createObject()
                    #layerNew.addElipse(i['x'], i['y'], i['dx'], i['dy'], i['width'])
                    #layerNew.setFace()
        # rectangles
        for i in self.getRectangles(self.projektBRD, 3) + self.getRectangles(self.projektBRD, 3, filled=True):
            x1 = i['x1']
            y1 = i['y1']
            x2 = i['x2']
            y2 = i['y2']
            #
            if i['filled']:
                layerNew.createObject()
                layerNew.addRectangle(x1, y1, x2, y2)
                layerNew.setFace()
            else:
                layerNew.createObject()
                layerNew.addLineWidth(x1, y1, x2, y1, 0.1)
                layerNew.setFace()
                
                layerNew.createObject()
                layerNew.addLineWidth(x2, y1, x2, y2, 0.1)
                layerNew.setFace()
                
                layerNew.createObject()
                layerNew.addLineWidth(x2, y2, x1, y2, 0.1)
                layerNew.setFace()
                
                layerNew.createObject()
                layerNew.addLineWidth(x1, y2, x1, y1, 0.1)
                layerNew.setFace()
        ###################
        elem = re.findall(r'MC ([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+) (.+?)\.(.*)\n', self.projektBRD)
        for i in elem:
            X1 = float(i[0])
            Y1 = float(i[1])
            ROT = int(i[2]) * (-90)
            if i[3] == '1':  # bottom
                warst = 0
                warstWyn = 4
            else:
                warst = 1
                warstWyn = 3
                
            if layerNumber != warstWyn:
                continue
                
            library = i[4]
            package = i[5]
            
            Xr = X1 * self.mnoznik
            Yr = Y1 * self.mnoznik * (-1)
            
            projektLIB = self.znajdzBiblioteke(library)
            if projektLIB:
                try:
                    lib = re.search('\[{0} .+?\]\s+(.+?)\s+\['.format(package.upper()), projektLIB, re.MULTILINE|re.DOTALL).groups()
                    j = lib[0] + '\n'
                except:
                    continue

                # lines
                for k in self.getLines(j, 3, [X1, Y1]):
                    layerNew.createObject()
                    layerNew.addLineWidth(k['x1'], k['y1'], k['x2'], k['y2'], k['width'])
                    layerNew.addRotation(Xr, Yr, ROT)
                    layerNew.setChangeSide(Xr, Yr, warst)
                    layerNew.setFace()
                # rectangles
                for k in self.getRectangles(j, 3, [X1, Y1]) + self.getRectangles(j, 3, [X1, Y1], True):
                    x1 = k['x1']
                    y1 = k['y1']
                    x2 = k['x2']
                    y2 = k['y2']
                    #
                    if k['filled']:
                        layerNew.createObject()
                        layerNew.addRectangle(x1, y1, x2, y2)
                        layerNew.addRotation(Xr, Yr, ROT)
                        layerNew.setChangeSide(Xr, Yr, warst)
                        layerNew.setFace()
                    else:
                        layerNew.createObject()
                        layerNew.addLineWidth(x1, y1, x2, y1, 0.1)
                        layerNew.addRotation(Xr, Yr, ROT)
                        layerNew.setChangeSide(Xr, Yr, warst)
                        layerNew.setFace()
                        
                        layerNew.createObject()
                        layerNew.addLineWidth(x2, y1, x2, y2, 0.1)
                        layerNew.addRotation(Xr, Yr, ROT)
                        layerNew.setChangeSide(Xr, Yr, warst)
                        layerNew.setFace()
                        
                        layerNew.createObject()
                        layerNew.addLineWidth(x2, y2, x1, y2, 0.1)
                        layerNew.addRotation(Xr, Yr, ROT)
                        layerNew.setChangeSide(Xr, Yr, warst)
                        layerNew.setFace()
                        
                        layerNew.createObject()
                        layerNew.addLineWidth(x1, y2, x1, y1, 0.1)
                        layerNew.addRotation(Xr, Yr, ROT)
                        layerNew.setChangeSide(Xr, Yr, warst)
                        layerNew.setFace()
                # empty polygon
                for l in re.findall(r'PV (.+?) 3\n', j):
                    punkty = l.split(" ")
                    for k in range(0, len(punkty), 2):
                        x1 = ((X1 / 2 - 100 + float(punkty[k])) + X1 / 2) * self.mnoznik
                        y1 = ((Y1 / 2 - 100 + float(punkty[k + 1])) + Y1 / 2) * self.mnoznik * (-1)
                       
                        if k + 3 > len(punkty):
                            x2 = ((X1 / 2 - 100 + float(punkty[0])) + X1 / 2) * self.mnoznik
                            y2 = ((Y1 / 2 - 100 + float(punkty[1])) + Y1 / 2) * self.mnoznik * (-1)
                        else:
                            x2 = ((X1 / 2 - 100 + float(punkty[k + 2])) + X1 / 2) * self.mnoznik
                            y2 = ((Y1 / 2 - 100 + float(punkty[k + 3])) + Y1 / 2) * self.mnoznik * (-1)
                            
                        if [x1, y1] != [x2, y2]:
                            layerNew.createObject()
                            layerNew.addLineWidth(x1, y1, x2, y2, 0.1)
                            layerNew.addRotation(Xr, Yr, ROT)
                            layerNew.setChangeSide(Xr, Yr, warst)
                            layerNew.setFace()
                # filled polygon
                polygonL = []
                for l in re.findall(r'PP (.+?) 3\n', j):
                    punkty = l.split(" ")
                    for k in range(0, len(punkty), 2):
                        x1 = ((X1 / 2 - 100 + float(punkty[k])) + X1 / 2) * self.mnoznik
                        y1 = ((Y1 / 2 - 100 + float(punkty[k + 1])) + Y1 / 2) * self.mnoznik * (-1)
                       
                        if k + 3 > len(punkty):
                            x2 = ((X1 / 2 - 100 + float(punkty[0])) + X1 / 2) * self.mnoznik
                            y2 = ((Y1 / 2 - 100 + float(punkty[1])) + Y1 / 2) * self.mnoznik * (-1)
                        else:
                            x2 = ((X1 / 2 - 100 + float(punkty[k + 2])) + X1 / 2) * self.mnoznik
                            y2 = ((Y1 / 2 - 100 + float(punkty[k + 3])) + Y1 / 2) * self.mnoznik * (-1)
                            
                        if [x1, y1] != [x2, y2]:
                            polygonL.append(['Line', x1, y1, x2, y2])
                    
                    layerNew.createObject()
                    layerNew.addPolygon(polygonL)
                    layerNew.addRotation(Xr, Yr, ROT)
                    layerNew.setChangeSide(Xr, Yr, warst)
                    layerNew.setFace()
                # circles/elipses
                for k in self.getCircles(j, 3, m=[X1, Y1]) + self.getCircles(j, 3, m=[X1, Y1], filled=True):
                    if k['filled']:
                        if k['type'] == 'circle':
                            layerNew.createObject()
                            layerNew.addCircle(k['x'], k['y'], k['r'])
                            layerNew.addRotation(Xr, Yr, ROT)
                            layerNew.setChangeSide(Xr, Yr, warst)
                            layerNew.setFace()
                        else:
                            layerNew.createObject()
                            layerNew.addElipse(k['x'], k['y'], k['dx'] - k['r'] / 2., k['dy'] - k['r'] / 2.)
                            layerNew.addRotation(Xr, Yr, ROT)
                            layerNew.setChangeSide(Xr, Yr, warst)
                            layerNew.setFace()
                    else:  # empty circle
                        if k['type'] == 'circle':
                            layerNew.createObject()
                            layerNew.addCircle(k['x'], k['y'], k['r'], k['width'])
                            layerNew.addRotation(Xr, Yr, ROT)
                            layerNew.setChangeSide(Xr, Yr, warst)
                            layerNew.setFace()
                        else:
                            pass
        #####
        layerNew.generuj(layerS)
        layerNew.updatePosition_Z(layerS)
        viewProviderLayerSilkObject(layerS.ViewObject)
        layerS.ViewObject.ShapeColor = layerColor
        grp.addObject(layerS)
        #
        doc.recompute()
    
    def getPads(self, doc, layerNumber, grp, layerName, layerColor, defHeight):
        layerName = "{0}_{1}".format(layerName, layerNumber)
        layerSide = PCBconf.PCBlayers[PCBconf.softLayers["fidocadj"][layerNumber][1]][0]
        layerType = PCBconf.PCBlayers[PCBconf.softLayers["fidocadj"][layerNumber][1]][3]
        ####
        layerS = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", layerName)
        layerNew = layerSilkObject(layerS, layerType)
        layerNew.holes = self.showHoles()
        layerNew.defHeight = defHeight
        #
        # rect
        dane1 = re.findall(r'RP (.+?) (.+?) (.+?) (.+?) ([1-2]+)', self.projektBRD)
        for i in dane1:
            x1 = float(i[0]) * self.mnoznik
            y1 = float(i[1]) * self.mnoznik * (-1)
            x2 = float(i[2]) * self.mnoznik
            y2 = float(i[3]) * self.mnoznik * (-1)
            padLayer = int(i[4])
            
            addPad = False
            if layerNumber == 17:
                if padLayer == 2:
                    addPad = True
            elif layerNumber == 18:
                if padLayer == 1:
                    addPad = True
            
            if addPad:
                layerNew.createObject()
                layerNew.addRectangle(x1, y1, x2, y2)
                layerNew.setFace()
        # circle
        dane1 = re.findall(r'EP (.+?) (.+?) (.+?) (.+?) ([1-2]+)', self.projektBRD)
        for i in dane1:
            x1 = float(i[0]) * self.mnoznik
            y1 = float(i[1]) * self.mnoznik
            x2 = float(i[2]) * self.mnoznik
            y2 = float(i[3]) * self.mnoznik
            padLayer = int(i[4])
            dx = float("%4.4f" % ((x1 - x2) / 2.))
            dy = float("%4.4f" % ((y1 - y2) / 2.))
            
            addPad = False
            if layerNumber == 17:
                if padLayer == 2:
                    addPad = True
            elif layerNumber == 18:
                if padLayer == 1:
                    addPad = True
            
            if addPad:
                xs = x1 + dx * (-1)
                ys = (y1 + dy * (-1)) * (-1)
                
                if abs(dx) == abs(dy):
                    r = abs(dx)
                    
                    layerNew.createObject()
                    layerNew.addCircle(xs, ys, r)
                    layerNew.setFace()
                else:  # elipse
                    layerNew.createObject()
                    layerNew.addElipse(xs, ys, abs(dx), abs(dy))
                    layerNew.setFace()
        ### via/pad
        dane1 = re.findall(r'PA (.+?) (.+?) (.+?) (.+?) (.+?) (.+?) ([1-2]+)', self.projektBRD)
        for i in dane1:
            X = float(i[0]) * self.mnoznik
            Y = float(i[1]) * self.mnoznik * (-1)
            dx = float(i[2]) * self.mnoznik
            dy = float(i[3]) * self.mnoznik
            drill = float(i[4]) * self.mnoznik / 2.
            padStyle = i[5]
            padLayer = int(i[6])
            
            addPad = False
            if layerNumber == 17:
                if padLayer == 2:
                    addPad = True
            elif layerNumber == 18:
                if padLayer == 1:
                    addPad = True
            
            if addPad or drill:
                if padStyle == '1':  # rectangle
                    x1 = X - dx / 2.
                    y1 = Y - dy / 2.
                    x2 = X + dx / 2.
                    y2 = Y + dy / 2.

                    layerNew.createObject()
                    layerNew.addRectangle(x1, y1, x2, y2)
                    layerNew.setFace()
                elif padStyle == '2':  # rectangle - round
                    layerNew.createObject()
                    layerNew.addPadLong(X, Y, dx / 2., dy / 2., 0.2, 1)
                    layerNew.setFace()
                else:  # round / elipse
                    if abs(dx) == abs(dy):
                        layerNew.createObject()
                        layerNew.addCircle(X, Y, dx / 2.)
                        layerNew.setFace()
                    else:
                        layerNew.createObject()
                        layerNew.addElipse(X, Y, abs(dx) / 2., abs(dy) / 2.)
                        layerNew.setFace()
        #
        elem = re.findall(r'MC (.+?) (.+?) (.+?) (.+?) (.+?)\.(.*)', self.projektBRD)

        for i in elem:
            X1 = float(i[0])
            Y1 = float(i[1])
            ROT = int(i[2]) * (-90)
            if i[3] == '1':  # bottom
                warst = 0
            else:
                warst = 1
            library = i[4]
            package = i[5]
            
            Xr = X1 * self.mnoznik
            Yr = Y1 * self.mnoznik * (-1)
            
            projektLIB = self.znajdzBiblioteke(library)
            
            if projektLIB:
                try:
                    lib = re.search('\[{0} .+?\](.+?)\['.format(package.upper()), projektLIB, re.MULTILINE|re.DOTALL).groups()
                    j = lib[0]
                except:
                    continue

                dane1 = re.findall(r'RP ([0-9]+?) ([0-9]+?) ([0-9]+?) ([0-9]+?) ([1-2]+)', j)
                for k in dane1:
                    if layerSide == warst:
                        x1 = ((X1 / 2 - 100 + float(k[0])) + X1 / 2) * self.mnoznik
                        y1 = ((Y1 / 2 - 100 + float(k[1])) + Y1 / 2) * self.mnoznik * (-1)
                        x2 = ((X1 / 2 - 100 + float(k[2])) + X1 / 2) * self.mnoznik
                        y2 = ((Y1 / 2 - 100 + float(k[3])) + Y1 / 2) * self.mnoznik * (-1)
                        
                        layerNew.createObject()
                        layerNew.addRectangle(x1, y1, x2, y2)
                        layerNew.addRotation(Xr, Yr, ROT)
                        layerNew.setChangeSide(Xr, Yr, warst)
                        layerNew.setFace()
                ###
                dane1 = re.findall('PA (.+?) (.+?) (.+?) (.+?) (.+?) (.+?) ([1-2]+)', j)
                for k in dane1:
                    xs = ((X1 / 2 - 100 + float(k[0])) + X1 / 2) * self.mnoznik
                    ys = ((Y1 / 2 - 100 + float(k[1])) + Y1 / 2) * self.mnoznik * (-1)
                    dx = float(k[2]) * self.mnoznik
                    dy = float(k[3]) * self.mnoznik
                    drill = float(k[4]) * self.mnoznik / 2.
                    padStyle = k[5]
                    padLayer = int(k[6])
                    
                    addPad = False
                    if layerNumber == 17:
                        if padLayer == 2:
                            addPad = True
                    elif layerNumber == 18:
                        if padLayer == 1:
                            addPad = True
                    
                    if addPad:
                        if padStyle == '1':
                            x1 = xs - dx / 2.
                            y1 = ys - dy / 2.
                            x2 = xs + dx / 2.
                            y2 = ys + dy / 2.
                                
                            layerNew.createObject()
                            layerNew.addRectangle(x1, y1, x2, y2)
                            layerNew.addRotation(Xr, Yr, ROT)
                            layerNew.setChangeSide(Xr, Yr, warst)
                            layerNew.setFace()
                        elif padStyle == '2':  # rectangle - round
                            layerNew.createObject()
                            layerNew.addPadLong(xs, ys, dx / 2., dy / 2., 0.2, 1)
                            layerNew.addRotation(Xr, Yr, ROT)
                            layerNew.setChangeSide(Xr, Yr, warst)
                            layerNew.setFace()
                        else:  # round
                            layerNew.createObject()
                            layerNew.addCircle(xs, ys, dx / 2.)
                            layerNew.addRotation(Xr, Yr, ROT)
                            layerNew.setChangeSide(Xr, Yr, warst)
                            layerNew.setFace()
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
        dane1 = re.findall(r'TY ([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+) (.+?) (.+?)\n', self.projektBRD)
        for i in dane1:
            x = float(i[0]) * self.mnoznik
            y = float(i[1]) * self.mnoznik * (-1)
            txt = i[8]
            rot = float(i[4])
            size = float(i[3]) * self.mnoznik
            align = "top-left"
            spin = True
            
            if int(i[5]) >= 4:
                mirror = 1
            else:
                mirror = 0
                
            if int(i[6]) == 0:
                if mirror:
                    side = 'BOTTOM'
                else:
                    side = 'TOP'
            elif int(i[6]) in [1]:
                side = 'BOTTOM'
            else:
                side = 'TOP'
                
            font = i[7]
                
            adnotacje.append([txt, x, y, size, rot, side, align, spin, mirror, font])
        #
        return adnotacje
        
    def getHoles(self, types):
        ''' holes/vias '''
        holes = []
        ###
        # holes
        if types['H']:
            for i in re.findall(r'PA (.+?) (.+?) .+? .+? (.+?) .+? ([0]+)', self.projektBRD):
                X = float(i[0]) * self.mnoznik
                Y = float(i[1]) * self.mnoznik * (-1)
                drill = float(i[2]) * self.mnoznik / 2.

                holes.append([X, Y, drill])
        # vias
        if types['V']:
            for i in re.findall(r'PA (.+?) (.+?) .+? .+? (.+?) .+? ([1-2]+)', self.projektBRD):
                X = float(i[0]) * self.mnoznik
                Y = float(i[1]) * self.mnoznik * (-1)
                drill = float(i[2]) * self.mnoznik / 2.
                
                holes.append([X, Y, drill])
        ###
        if types['P']:  # pads
            for i in re.findall(r'MC (.+?) (.+?) (.+?) (.+?) (.+?)\.(.*)', self.projektBRD):
                X1 = float(i[0])
                Y1 = float(i[1])
                ROT = int(i[2]) * 90
                #if i[3] == '1':  # bottom
                    #ROT += 180
                library = i[4]
                package = i[5]
                
                projektLIB = self.znajdzBiblioteke(library)
                if projektLIB:
                    for j in re.search('\[{0} .+?\](.+?)\['.format(package.upper()), projektLIB, re.MULTILINE|re.DOTALL).groups():
                        for k in re.findall('PA (.+?) (.+?) .+? .+? (.+?) .+? ([1-2]+)', j):
                            xs = (X1 - 100 + float(k[0])) - X1
                            ys = (Y1 - 100 + float(k[1])) - Y1
                            drill = float(k[2]) * self.mnoznik / 2.
                            
                            if drill > 0:
                                [xR, yR] = self.obrocPunkt([xs, ys], [X1, Y1], ROT)
                                
                                if i[3] == '1':  # bottom
                                    xR = self.odbijWspolrzedne(xR, X1)
                                
                                xR *= self.mnoznik
                                yR *= self.mnoznik * (-1)
                                
                                holes.append([xR, yR, drill])
        ###
        return holes
    
    def getPCB(self):
        PCB = []
        wygenerujPada = True
        ###
        # linie
        for i in self.getLines(self.projektBRD, 0):
            PCB.append(['Line', i['x1'], i['y1'], i['x2'], i['y2']])
        # kwadraty
        for i in self.getRectangles(self.projektBRD, 0):
            PCB.append(['Line', i['x1'], i['y1'], i['x2'], i['y1']])
            PCB.append(['Line', i['x2'], i['y1'], i['x2'], i['y2']])
            PCB.append(['Line', i['x2'], i['y2'], i['x1'], i['y2']])
            PCB.append(['Line', i['x1'], i['y2'], i['x1'], i['y1']])
        # polyline
        dane1 = re.findall(r'PV (.+?) 0\n', self.projektBRD)
        for i in dane1:
            i += " "
            punkty = re.findall(r'(.+?) (.+?) ', i)
            for j in range(len(punkty)):
                x1 = float(punkty[j][0]) * self.mnoznik
                y1 = float(punkty[j][1]) * self.mnoznik * (-1.)
                
                if j == len(punkty) - 1:
                    x2 = float(punkty[0][0]) * self.mnoznik
                    y2 = float(punkty[0][1]) * self.mnoznik * (-1.)
                else:
                    x2 = float(punkty[j + 1][0]) * self.mnoznik
                    y2 = float(punkty[j + 1][1]) * self.mnoznik * (-1.)
                
                
                PCB.append(['Line', x1, y1, x2, y2])
        # kola
        for i in self.getCircles(self.projektBRD, 0, f=['c']):
            PCB.append(['Circle', i['x'], i['y'], i['r']])
        ###
        elem = re.findall(r'MC ([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+) (.+?)\.(.*)\n', self.projektBRD)
        for i in elem:
            X1 = float(i[0])
            Y1 = float(i[1])
            ROT = int(i[2]) * (-90)
            if i[3] == '1':  # bottom
                warst = 0
            else:
                warst = 1
                
            library = i[4]
            package = i[5]
            
            Xr = X1 * self.mnoznik
            Yr = Y1 * self.mnoznik * (-1)
            
            projektLIB = self.znajdzBiblioteke(library)
            if projektLIB:
                try:
                    lib = re.search('\[{0} .+?\]\s+(.+?)\s+\['.format(package.upper()), projektLIB, re.MULTILINE|re.DOTALL).groups()
                    j = lib[0] + '\n'
                except:
                    continue

                # line
                for k in self.getLines(j, 0, [X1, Y1]):
                    [x1, y1] = self.obrocPunkt2([k['x1'], k['y1']], [Xr, Yr], ROT)
                    [x2, y2] = self.obrocPunkt2([k['x2'], k['y2']], [Xr, Yr], ROT)
                    if warst == 0:
                        x1 = self.odbijWspolrzedne(x1, Xr)
                        x2 = self.odbijWspolrzedne(x2, Xr)
                    
                    PCB.append(['Line', x1, y1, x2, y2])
                # empty rectangle
                for k in self.getRectangles(j, 0, [X1, Y1]):
                    x1 = k['x1']
                    y1 = k['y1']
                    x2 = k['x2']
                    y2 = k['y2']
                    #
                    [x1R, y1R] = self.obrocPunkt2([x1, y1], [Xr, Yr], ROT)
                    [x2R, y2R] = self.obrocPunkt2([x2, y1], [Xr, Yr], ROT)
                    if warst == 0:
                        x1R = self.odbijWspolrzedne(x1R, Xr)
                        x2R = self.odbijWspolrzedne(x2R, Xr)
                    
                    PCB.append(['Line', x1R, y1R, x2R, y2R])
                    #
                    [x1R, y1R] = self.obrocPunkt2([x2, y1], [Xr, Yr], ROT)
                    [x2R, y2R] = self.obrocPunkt2([x2, y2], [Xr, Yr], ROT)
                    if warst == 0:
                        x1R = self.odbijWspolrzedne(x1R, Xr)
                        x2R = self.odbijWspolrzedne(x2R, Xr)
                    
                    PCB.append(['Line', x1R, y1R, x2R, y2R])
                    #
                    [x1R, y1R] = self.obrocPunkt2([x2, y2], [Xr, Yr], ROT)
                    [x2R, y2R] = self.obrocPunkt2([x1, y2], [Xr, Yr], ROT)
                    if warst == 0:
                        x1R = self.odbijWspolrzedne(x1R, Xr)
                        x2R = self.odbijWspolrzedne(x2R, Xr)
                    
                    PCB.append(['Line', x1R, y1R, x2R, y2R])
                    #
                    [x1R, y1R] = self.obrocPunkt2([x1, y2], [Xr, Yr], ROT)
                    [x2R, y2R] = self.obrocPunkt2([x1, y1], [Xr, Yr], ROT)
                    if warst == 0:
                        x1R = self.odbijWspolrzedne(x1R, Xr)
                        x2R = self.odbijWspolrzedne(x2R, Xr)
                    
                    PCB.append(['Line', x1R, y1R, x2R, y2R])
                # empty polygon
                for l in re.findall(r'PV (.+?) 0\n', j):
                    punkty = l.split(" ")
                    for k in range(0, len(punkty), 2):
                        x1 = ((X1 / 2 - 100 + float(punkty[k])) + X1 / 2) * self.mnoznik
                        y1 = ((Y1 / 2 - 100 + float(punkty[k + 1])) + Y1 / 2) * self.mnoznik * (-1)
                       
                        if k + 3 > len(punkty):
                            x2 = ((X1 / 2 - 100 + float(punkty[0])) + X1 / 2) * self.mnoznik
                            y2 = ((Y1 / 2 - 100 + float(punkty[1])) + Y1 / 2) * self.mnoznik * (-1)
                        else:
                            x2 = ((X1 / 2 - 100 + float(punkty[k + 2])) + X1 / 2) * self.mnoznik
                            y2 = ((Y1 / 2 - 100 + float(punkty[k + 3])) + Y1 / 2) * self.mnoznik * (-1)
                            
                        if [x1, y1] != [x2, y2]:
                            [x1R, y1R] = self.obrocPunkt2([x1, y1], [Xr, Yr], ROT)
                            [x2R, y2R] = self.obrocPunkt2([x2, y2], [Xr, Yr], ROT)
                            if warst == 0:
                                x1R = self.odbijWspolrzedne(x1R, Xr)
                                x2R = self.odbijWspolrzedne(x2R, Xr)
                            
                            PCB.append(['Line', x1R, y1R, x2R, y2R])
                # empty circle/elipse
                for k in self.getCircles(j, 0, ['c'], [X1, Y1]):
                    [xs, ys] = self.obrocPunkt2([k['x'], k['y']], [Xr, Yr], ROT)
                    if warst == 0:
                        xs = self.odbijWspolrzedne(xs, Xr)
                        
                    PCB.append(['Circle', xs, ys, k['r']])
        #####
        
        return [PCB, wygenerujPada]
