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
import re
from xml.dom import minidom
import __builtin__
#
from PCBconf import PCBlayers, softLayers
from PCBobjects import *
from formats.PCBmainForms import *
from command.PCBgroups import *


def getSettings(projektBRD, paramName, tryb=True):
    param = projektBRD.getElementsByTagName('designrules')[0].getElementsByTagName('param')
    for i in param:
        if i.getAttribute("name") == paramName:
            if tryb:
                dane = re.search(r'(.[^a-z]*)(.*)', i.getAttribute("value")).groups()
                wartosc = float(dane[0])
                    
                if dane[1] == 'mil':
                    wartosc *= 0.0254
            else:
                wartosc = i.getAttribute("value")
            return wartosc
    return False


class dialogMAIN(dialogMAIN_FORM):
    def __init__(self, filename=None, parent=None):
        dialogMAIN_FORM.__init__(self, parent)
        self.databaseType = "eagle"
        
        self.projektBRD = minidom.parse(filename)
        self.layersNames = self.getLayersNames()
        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetBool("boardImportThickness", True):
            self.gruboscPlytki.setValue(self.getBoardThickness())
        ##
        self.generateLayers([17, 18])
        self.spisWarstw.sortItems(1)
        
    def getBoardThickness(self):
        pcbThickness = 0
        layerSetup = getSettings(self.projektBRD, "layerSetup", False)
        layerSetup = [int(i) for i in re.findall(r'[0-9]+', layerSetup)]
        # isolation
        mtIsolate = getSettings(self.projektBRD, "mtIsolate", False).split(" ")
        if len(layerSetup) > 1:
            layerSetup.remove(max(layerSetup))
        elif layerSetup[0] != 1:
            layerSetup[0] = 1
        
        for i in layerSetup:
            [value, unit] = re.search(r'(.[^a-z]*)(.*)', mtIsolate[i - 1]).groups()
            value = float(value)
            
            if unit == 'mil':
                value= float("%4.3f" % (value * 0.0254))
            else:
                value= float("%4.3f" % value)
                
            pcbThickness += value
        # cooper
        if len(layerSetup):
            mtCopper = getSettings(self.projektBRD, "mtCopper", False).split(" ")
            layerSetup.remove(min(layerSetup))
            
            for i in layerSetup:
                [value, unit] = re.search(r'(.[^a-z]*)(.*)', mtCopper[i - 1]).groups()
                value = float(value)
                
                if unit == 'mil':
                    value= float("%4.3f" % (value * 0.0254))
                else:
                    value= float("%4.3f" % value)
                    
                pcbThickness += value

        return pcbThickness

    def getLayersNames(self):
        programEagle = self.projektBRD.getElementsByTagName("layers")[0].getElementsByTagName("layer")
        dane = {}
        
        for i in programEagle:
            layerNumber = int(i.getAttribute("number"))
            layerName = i.getAttribute("name")
            #layerColor = int(i.getAttribute("color"))
            
            dane[layerNumber] = layerName
        return dane


class EaglePCB(mainPCB):
    def __init__(self, filename):
        mainPCB.__init__(self, None)
        
        self.dialogMAIN = dialogMAIN(filename)
        self.databaseType = "eagle"
        #self.setDatabase(supSoftware["eagle"]['pathToBase'])
        #self.setDatabase(pathToDatabase)
        #
        self.libraries = {}
        self.elements = []
    
    def getLibraries(self):
        if len(self.libraries) == 0:
            data = re.findall("<libraries>(.+?)</libraries>", self.projektBRD, re.MULTILINE|re.DOTALL)[0]
            for i in re.findall('<library name="(.+?)">(.+?)</library>', data, re.MULTILINE|re.DOTALL):
                if not i[0] in self.libraries:
                    self.libraries[i[0]] = {}
                for j in re.findall('<package name="(.+?)">(.+?)</package>', i[1], re.MULTILINE|re.DOTALL):
                    if not j[0] in self.libraries[i[0]]:
                        self.libraries[i[0]][j[0]] = j[1]
    
    def getElements(self):
        if len(self.elements) == 0:
            data = re.findall("<elements>(.+?)</elements>", self.projektBRD, re.MULTILINE|re.DOTALL)[0]
            for i in re.findall('<element name="(|.+?)" library="(.+?)" package="(.+?)" value="(|.+?)" x="(.+?)" y="(.+?)"( locked="(.+?)"|)( populate="(.+?)"|)( smashed="(.+?)"|)( rot="(.+?)"|)(/>|>\n(.+?)\n</element>)', data, re.MULTILINE|re.DOTALL):
                name = i[0]
                library = i[1]
                package = i[2]
                freecad_package = package
                value = i[3]
                x = float(i[4])
                y = float(i[5])
                locked = i[7]
                populated = i[9]
                smashed = i[11]
                attribute = i[14].replace('/>', '')
                
                # <uros@isotel.eu> fix to get a FREECAD attribute out, it's overall all ugly since original
                # code is using regex to parse xml instead of dom parser - all regex should be replaced with the DOM
                try:
                    for attr in minidom.parseString( "<element>" + i[14] ).getElementsByTagName('attribute'):                        
                        if attr.getAttribute('name') == 'FREECAD':
                            freecad_package = attr.getAttribute('value')
                except:
                    pass
                
                try:
                    rot = float(re.search('MR([0-9,.-]*)', i[13]).groups()[0])
                    side = 0  # BOTTOM
                except:
                    try:
                        rot = float(re.search('R([0-9,.-]*)', i[13]).groups()[0])
                        side = 1  # TOP
                    except:
                        rot = 0.
                        side = 1  # TOP
                
                self.elements.append({'name': name, 'library': library, 'package': package, 'value': value, 'x': x, 'y': y, 'locked': locked, 'populated': populated, 'smashed': smashed, 'rot': rot, 'side': side, 'attr': attribute, "freecad_package" : freecad_package})
                #self.elements.append({'name': name, 'library': library, 'package': package, 'value': value, 'x': x, 'y': y, 'locked': locked, 'populated': populated, 'smashed': smashed, 'rot': rot, 'side': side, 'attr': attribute})
    
    def getSection(self, name):
        if name.strip() == "":
            FreeCAD.Console.PrintWarning("Incorrect parameter (Section)!\n")
            return ''
        
        try:
            return re.findall("<{0}>(.+?)</{0}>".format(name), self.projektBRD, re.MULTILINE|re.DOTALL)[0]
        except:
            return ''
    
    def getPolygons(self, section, layer):
        if section.strip() == "":
            #FreeCAD.Console.PrintWarning("Incorrect parameter (Polygon)!\n")
            return []
        
        if not isinstance(layer, list):
            layer = [layer]
            
        data = []
        for lay in layer:
            for i in re.findall('<polygon width=".+?" layer="%s">(.+?)</polygon>' % str(lay), section, re.MULTILINE|re.DOTALL):
                data.append(re.findall('<vertex x="(.+?)" y="(.+?)"( curve="(.+?)"|)/>', i))
        
        return data
    
    def getRectangle(self, section, layer, m=[0,0]):
        if section.strip() == "":
            #FreeCAD.Console.PrintWarning("Incorrect parameter (Rectangle)!\n")
            return []
        
        if not isinstance(layer, list):
            layer = [layer]
            
        data = []
        for lay in layer:
            for i in re.findall('<rectangle\s+x1="(.+?)"\s+y1="(.+?)"\s+x2="(.+?)"\s+y2="(.+?)"\s+layer="%s"(\s+rot="(.+?)"|)/>' % str(lay), section):
                x1 = float(i[0])
                y1 = float(i[1])
                x2 = float(i[2])
                y2 = float(i[3])
                
                if [x1, y1] == [x2, y2]:
                    continue
                if m[0] != 0:
                    x1 += m[0]
                    x2 += m[0]
                if m[1] != 0:
                    y1 += m[1]
                    y2 += m[1]
                
                if i[5] == "":
                    rot = 0.
                else:
                    rot = float(re.search('R([0-9,.-]*)', i[5]).groups()[0])
                    
                xs = x1 + (abs(x1 - x2) / 2.)
                ys = y1 + (abs(y1 - x2) / 2.)
                
                data.append({
                    'x1': x1,
                    'y1': y1,
                    'x2': x2,
                    'y2': y2,
                    'xs': xs,
                    'ys': ys,
                    'rot': rot,
                    'layer': lay,
                })
        
        return data
    
    def getCircles(self, section, layer, m=[0,0]):
        if section.strip() == "":
            #FreeCAD.Console.PrintWarning("Incorrect parameter (Cirlce)!\n")
            return []
        
        if not isinstance(layer, list):
            layer = [layer]
        
        data = []
        for lay in layer:
            for i in re.findall('<circle\s+x="(.+?)"\s+y="(.+?)"\s+radius="(.+?)"\s+width="(.+?)"\s+layer="%s"/>' % str(lay), section):
                x = float(i[0])
                y = float(i[1])
                r = float(i[2])
                w = float(i[3])
                
                if w == 0:
                    w = 0.01
                if m[0] != 0:
                    x += m[0]
                if m[1] != 0:
                    y += m[1]
                
                data.append({
                    'x': x,
                    'y': y,
                    'r': r,
                    'width': w,
                    'layer': lay,
                })
        
        return data
            
    def getWires(self, section, layer, m=[0,0]):
        if section.strip() == "":
            #FreeCAD.Console.PrintWarning("Incorrect parameter (Wire)!\n")
            return []
        
        if not isinstance(layer, list):
            layer = [layer]
        
        data = []
        for lay in layer:
            for i in re.findall('<wire\s+x1="(.+?)"\s+y1="(.+?)"\s+x2="(.+?)"\s+y2="(.+?)"\s+width="(.+?)"\s+layer="%s"(\s+style="(.+?)"|)(\s+curve="(.+?)"|)(\s+cap="(.+?)"|)/>' % str(lay), section):
                x1 = float(i[0])
                y1 = float(i[1])
                x2 = float(i[2])
                y2 = float(i[3])
                width = float(i[4])
                style = i[6]
                
                if [x1, y1] == [x2, y2]:
                    continue
                if m[0] != 0:
                    x1 += m[0]
                    x2 += m[0]
                if m[1] != 0:
                    y1 += m[1]
                    y2 += m[1]
                
                if i[8] == '':
                    curve = 0
                else:
                    curve = float(i[8])
                
                if i[10] == '':
                    cap = 'round'
                else:
                    cap = i[10]
                    
                if width == 0:
                    width = 0.01
                
                data.append({
                    'x1': x1,
                    'y1': y1,
                    'x2': x2,
                    'y2': y2,
                    'width': width,
                    'style': style,
                    'curve': curve,
                    'cap': cap,
                    'layer': lay,
                })
            
        return data
    
    ##############################
    # MAIN FUNCTIONS
    ##############################
    def setProject(self, filename):
        #self.projektBRD = minidom.parse(filename)
        self.projektBRD = __builtin__.open(filename).read()

    def getPCB(self):
        PCB = []
        wygenerujPada = True
        dane = self.getSection('plain')
        #
        for i in self.getWires(dane, 20):
            if not i['curve']:
                PCB.append(['Line', i['x1'], i['y1'], i['x2'], i['y2']])
            else:
                PCB.append(['Arc', i['x2'], i['y2'], i['x1'], i['y1'], i['curve']])
        #
        for i in self.getCircles(dane, 20):
            PCB.append(['Circle', i['x'], i['y'], i['r']])
        #
        self.getLibraries()
        self.getElements()
        
        for i in self.elements:
            ROT = i['rot']
            #######
            #linie/luki
            for j in self.getWires(self.libraries[i['library']][i['package']], 20, [i['x'], i['y']]):
                [x1, y1] = self.obrocPunkt2([j['x1'], j['y1']], [i['x'], i['y']], ROT)
                [x2, y2] = self.obrocPunkt2([j['x2'], j['y2']], [i['x'], i['y']], ROT)
                if i['side'] == 0:
                    x1 = self.odbijWspolrzedne(x1, i['x'])
                    x2 = self.odbijWspolrzedne(x2, i['x'])
                
                if not j['curve']:
                    PCB.append(['Line', x1, y1, x2, y2])
                else:
                    curve = j['curve']
                    if i['side'] == 0:
                        curve *= -1
                    
                    PCB.append(['Arc', x2, y2, x1, y1, curve])
            #okregi
            for j in self.getCircles(self.libraries[i['library']][i['package']], 20, [i['x'], i['y']]):
                [x, y] = self.obrocPunkt2([j['x'], j['y']], [i['x'], i['y']], ROT)
                if i['side'] == 0:
                    x = self.odbijWspolrzedne(x, i['x'])
                
                PCB.append(['Circle', x, y, j['r']])
        #
        return [PCB, wygenerujPada]
    
    def getGlue(self, layerNumber):
        glue = {}
        dane = self.getSection('plain')
        # line/arc
        for i in self.getWires(dane, layerNumber):
            
            if not i['width'] in glue.keys():
                glue[i['width']] = []
            
            if not i['curve']:
                glue[i['width']].append(['line', i['x1'], i['y1'], i['x2'], i['y2']])
            else:
                glue[i['width']].append(['arc', i['x2'], i['y2'], i['x1'], i['y1'], i['curve'], i['cap']])
        # circle
        for i in self.getCircles(dane, layerNumber):
            if not i['width'] in glue.keys():
                glue[i['width']] = []
            
            glue[i['width']].append(['circle', i['x'], i['y'], i['r']])
        #
        return glue

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
        #  dodatkowe warstwy
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
                elif ID in [1, 16]:  # paths
                    self.generatePaths(self.getPaths(ID), doc, grp, name, color, ID, transp)
                elif ID in [17, 18]:  # pady
                    self.getPads(doc, ID, grp, name, color, transp)
                #elif ID in [116, 117]:  # centerDrill
                    #self.centerDrill(doc, ID, grp, name, color)
                elif ID in [21, 22, 51, 52]:  # silk
                    self.getSilkLayer(doc, ID, grp, name, color, transp)
                elif ID in [35, 36]:  # glue
                    self.generateGlue(self.getGlue(ID), doc, grp, name, color, ID)
                elif ID == 0:  # annotations
                    data = re.findall("<plain>(.+?)</plain>", self.projektBRD, re.MULTILINE|re.DOTALL)[0]
                    self.addAnnotations(self.getAnnotations(re.findall('<text (.+?)</text>', data, re.MULTILINE|re.DOTALL)), doc, color)
                #elif ID in [998, 999]:  # polygons
                    #self.generatePolygons(self.getPolygons(ID), doc, grp, name, color, ID)
                else:
                    self.generateConstraintAreas(self.getConstraintAreas(ID), doc, ID, grp_2, name, color, transp)
        return doc
    
    ##############################
    # OTHER STUF
    ##############################
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
                
                
                if polygonL[k][3] == "":
                    poin.append(['Line', x1, y1, x2, y2])
                else:
                    curve = float(polygonL[k][3])
                    poin.append(['Arc3P', x2, y2, x1, y1, curve])
        return poin

    ##############################
    # LAYERS
    ##############################
    def getHoles(self, types):
        ''' holes/vias '''
        holes = []
        # holes
        if types['H']:
            data = re.findall("<plain>(.+?)</plain>", self.projektBRD, re.MULTILINE|re.DOTALL)[0]
            for i in re.findall('<hole x="(.+?)" y="(.+?)" drill="(.+?)"/>', data):
                holes.append([float(i[0]), float(i[1]), float(i[2]) / 2.])
        # vias
        if types['V']:
            data = re.findall("<signals>(.+?)</signals>", self.projektBRD, re.MULTILINE|re.DOTALL)[0]
            for i in re.findall('<via x="(.+?)" y="(.+?)" .+? drill="(.+?)"(|.+?)/>', data):
                holes.append([float(i[0]), float(i[1]), float(i[2]) / 2.])
        ### pady
        self.getLibraries()
        self.getElements()
        
        for i in self.elements:
            if types['H']:  # holes
                for j in re.findall('<hole x="(.+?)" y="(.+?)" drill="(.+?)"/>', self.libraries[i['library']][i['package']]):
                    xs = float(j[0])
                    ys = float(j[1])
                    drill = float(j[2]) / 2.
                    
                    [xR, yR] = self.obrocPunkt([xs, ys], [i['x'], i['y']], i['rot'])
                    if i['side'] == 0:  # odbicie wspolrzednych
                        xR = self.odbijWspolrzedne(xR, i['x'])
                    
                    holes.append([xR, yR, drill])
            if types['P']:  # pads
                for j in re.findall('<pad .+? x="(.+?)" y="(.+?)" drill="(.+?)".+?', self.libraries[i['library']][i['package']]):
                    xs = float(j[0])
                    ys = float(j[1])
                    drill = float(j[2]) / 2.
                    
                    [xR, yR] = self.obrocPunkt([xs, ys], [i['x'], i['y']], i['rot'])
                    if i['side'] == 0:  # odbicie wspolrzednych
                        xR = self.odbijWspolrzedne(xR, i['x'])
                    
                    holes.append([xR, yR, drill])
        ####
        return holes

    def getParts(self, koloroweElemnty, adjustParts, groupParts, partMinX, partMinY, partMinZ):
        self.__SQL__.reloadList()
        #
        self.getLibraries()
        self.getElements()
        PCB_ER = []
        
        for i in self.elements:
            if i['side'] == 1:
                side = "TOP"
            else:
                side = "BOTTOM"
            ######
            EL_Name = ['', i['x'], i['y'], 1.27, i['rot'], side, "bottom-left", False, 'None', '', True]
            EL_Value = ['', i['x'], i['y'], 1.27, i['rot'], side, "bottom-left", False, 'None', '', True]
            # [txt, x, y, size, rot, side, align, spin, mirror, font, display]
            if i['smashed'] == "yes":
                for j in self.getAnnotations(re.findall('<attribute (.+?)\n', i['attr']), mode='attr'):
                    if j[0] == 'NAME':
                        EL_Name = j
                    elif j[0] == 'VALUE':
                        EL_Value = j
            else:
                for j in self.getAnnotations(re.findall('<text (.+?)</text>', self.libraries[i['library']][i['package']], re.MULTILINE|re.DOTALL)):
                    x1 = i['x'] + j[1]
                    y1 = i['y'] + j[2]
                    
                    if side == "BOTTOM":
                        x1 = self.odbijWspolrzedne(x1, i['x'])
                        j[5] = "BOTTOM"
                        j[8] = True
                        
                        [xR, yR] = self.obrocPunkt2([x1, y1], [i['x'], i['y']], -i['rot'])
                    else:
                        [xR, yR] = self.obrocPunkt2([x1, y1], [i['x'], i['y']], i['rot'])
                    
                    
                    j[4] = j[4] + i['rot']
                    j[1] = xR
                    j[2] = yR
                    
                    if j[0] == '&gt;NAME' and EL_Name[0] == '':
                        j[0] = 'NAME'
                        EL_Name = j
                    elif j[0] == '&gt;VALUE' and EL_Value[0] == '':
                        j[0] = 'VALUE'
                        EL_Value = j
            
            #newPart = [[i['name'], i['package'], i['value'], i['x'], i['y'], i['rot'], side, i['library']], EL_Name, EL_Value]
            #wyn = self.addPart(newPart, koloroweElemnty, adjustParts, groupParts, partMinX, partMinY, partMinZ)
            # <uros@isotel.eu> modified package here and 7 lines below
            newPart = [[i['name'], i['freecad_package'], i['value'], i['x'], i['y'], i['rot'], side, i['library']], EL_Name, EL_Value]
            wyn = self.addPart(newPart, koloroweElemnty, adjustParts, groupParts, partMinX, partMinY, partMinZ)
            #
            if wyn[0] == 'Error':  # lista brakujacych elementow
                partNameTXT = partNameTXT_label = self.generateNewLabel(i['name'])
                if isinstance(partNameTXT, unicode):
                    partNameTXT = unicodedata.normalize('NFKD', partNameTXT).encode('ascii', 'ignore')
                
                #PCB_ER.append([partNameTXT, i['package'], i['value'], i['library']])
                PCB_ER.append([partNameTXT, i['freecad_package'], i['value'], i['library']])
        ####
        return PCB_ER

    def getConstraintAreas(self, layerNumber):
        areas = []
        dane = self.getSection('plain')
        # kola
        for i in self.getCircles(dane, layerNumber):
            areas.append(['circle', i['x'], i['y'], i['r'], i['width']])
        # kwadraty
        for i in self.getRectangle(dane, layerNumber):
            areas.append(['rect', i['x1'], i['y1'], i['x2'], i['y2'], 0, i['rot']])
        # polygon
        for i in self.getPolygons(dane, layerNumber):
            areas.append(['polygon', self.getPolygon(i)])
        #
        return areas

    #def getPolygons(self, layerNumber):
        #if layerNumber == 998:
            #layerNumber = 1
        #else:
            #layerNumber = 16
        ##
        #signal = []
        #wiresDB = []
        ##
        #for i in self.pobierzParametryPCB("signals", "signal"):
            #signalName = i.getAttribute("name")
            
            #for j in i.getElementsByTagName("polygon"):
                #if int(j.getAttribute("layer")) == layerNumber:
                    ##isolate = float(j.getAttribute("isolate"))
                    #isolate = 1.27
                    #width = float(j.getAttribute("width"))
                    ##
                    #polygon = [isolate, width, signalName]
                    #signal.append([])
                    #points = []
                    ##
                    #for k in j.getElementsByTagName("vertex"):
                        #x = float(k.getAttribute("x"))
                        #y = float(k.getAttribute("y"))
                        
                        #points.append([x, y])
                    ##
                    #polygon.append(points)
                    #signal[-1].append(polygon)
            ##
            #for j in i.getElementsByTagName("wire"):
                #if int(j.getAttribute("layer")) == layerNumber:
                    #x1 = float(j.getAttribute("x1"))
                    #y1 = float(j.getAttribute("y1"))
                    #x2 = float(j.getAttribute("x2"))
                    #y2 = float(j.getAttribute("y2"))
                    #width = float(j.getAttribute("width"))
                    
                    #if [x1, y1] != [x2, y2]:
                        #wiresDB.append(['line', signalName, x1, y1, x2, y2, width])
        
        #return [signal, wiresDB]
        
    def getPaths(self, layerNumber):
        signal = []
        wires = []
        num = 1
        #
        dane = self.getSection('signals')
        #
        for i in self.getWires(dane, layerNumber):
            signal.append([])
            #
            if not i['curve']:
                wires.append(['line', i['x1'], i['y1'], i['x2'], i['y2'], i['width']])
            else:
                wires.append(['arc', i['x1'], i['y1'], i['x2'], i['y2'], i['curve'], i['width'], i['cap']])
            #
            signal[-1].append(num)
            num += 1
        #
        wires.append(signal)
        return wires

    def getSettings(self, paramName):
        dane = re.search('<param name="{0}" value="(.+?)"/>'.format(paramName), self.projektBRD).groups(0)[0]
        dane = re.search(r'(.[^a-z]*)(.*)', dane).groups()
        wartosc = float(dane[0])
        
        if dane[1] == 'mil':
            wartosc *= 0.0254

        return wartosc

    def getPads(self, doc, layerNumber, grp, layerName, layerColor, defHeight):
        layerName = "{0}_{1}".format(layerName, layerNumber)
        layerSide = PCBlayers[softLayers["eagle"][layerNumber][1]][0] 
        layerType = PCBlayers[softLayers["eagle"][layerNumber][1]][3]
        ####
        layerS = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", layerName)
        layerNew = layerSilkObject(layerS, layerType)
        layerNew.holes = self.showHoles()
        layerNew.defHeight = defHeight
        ####
        MAX_P = self.getSettings('rlMaxPadTop')
        MIN_P = self.getSettings('rlMinPadTop')
        PERC_P = self.getSettings('rvPadTop')
        
        MAX_V = self.getSettings('rlMaxViaOuter')
        MIN_V = self.getSettings('rlMinViaOuter')
        PERC_V = self.getSettings('rvViaOuter')
        ####
        data = re.findall("<signals>(.+?)</signals>", self.projektBRD, re.MULTILINE|re.DOTALL)[0]
        for i in re.findall('<via x="(.+?)" y="(.+?)" extent=".+?" drill="(.+?)"( diameter="(.+?)"|)( shape="(.+?)"|)/>', data):
            x = float(i[0])
            y = float(i[1])
            drill = float(i[2])
            shape = i[6]
            
            if shape == "":
                shape = "round"
            
            if i[4] != "":
                diameter = float(i[4])
                
                if diameter < (2 * MIN_V + drill):
                    diameter = 2 * MIN_V + drill
                elif diameter > (2 * MAX_V + drill):
                    diameter = 2 * MAX_V + drill
            else:
                diameter = drill * PERC_V
                
                if diameter < MIN_V:
                    diameter = 2 * MIN_V + drill
                elif diameter > MAX_V:
                    diameter = 2 * MAX_V + drill
                else:
                    diameter = 2 * diameter + drill
            ####
            if shape == "round":
                layerNew.createObject()
                layerNew.addCircle(x, y, diameter / 2.)
                layerNew.setFace()
            elif shape == "square":
                a = diameter / 2.
                x1 = x - a
                y1 = y - a
                x2 = x + a
                y2 = y + a
                
                layerNew.createObject()
                layerNew.addRectangle(x1, y1, x2, y2)
                layerNew.setFace()
            elif shape == "octagon":
                layerNew.createObject()
                layerNew.addOctagon(x, y, diameter)
                layerNew.setFace()
        ####
        if layerNumber == 17:
            newLayer = 1
        elif layerNumber == 18:
            newLayer = 16
        ##
        dane = self.getSection('plain')
        #
        for i in self.getCircles(dane, [newLayer, layerNumber]):
            layerNew.createObject()
            layerNew.addCircle(i['x'], i['y'], i['r'] / 2., i['width'])
            layerNew.setFace()
        # kwadraty
        for i in self.getRectangle(dane, [newLayer, layerNumber]):
            dx = i['x1'] - i['x2']
            dy = i['y1'] - i['y2']
            
            layerNew.createObject()
            layerNew.addRectangle(i['x1'], i['y1'], i['x2'], i['y2'])
            layerNew.addRotation(i['x1'] - (dx / 2.), i['y1'] - (dy / 2.), i['rot'])
            layerNew.setFace()
        #####
        self.getLibraries()
        self.getElements()
        elongationOffset = self.getSettings('psElongationOffset')
        elongationLong = self.getSettings('psElongationLong')
        
        for i in self.elements:
            for j in re.findall('<(smd) name=".+?"(.+?)layer="1"(.+?)>', self.libraries[i['library']][i['package']]) + re.findall('<(pad) name=".+?"(.+?)/>', self.libraries[i['library']][i['package']]):
                data = ('').join(j[1:])
                #####
                x = float(re.search('x="(.+?)"', data).groups()[0]) + i['x']
                y = float(re.search('y="(.+?)"', data).groups()[0]) + i['y']
                
                try:
                    ROT_2 = float(re.search('rot="R([0-9,.-]*)"', data).groups()[0])  # kat o jaki zostana obrocone elementy
                except:
                    ROT_2 = 0  # kat o jaki zostana obrocone elementy
                
                if j[0] == "pad":
                    drill = float(re.search('drill="(.+?)"', data).groups()[0])
                    
                    try:
                        shape = re.search('shape="(.+?)"', data).groups()[0]
                    except:
                        shape = "round"
                    
                    if shape == "":
                        shape = "round"

                    try:
                        diameter = float(re.search('diameter="(.+?)"', data).groups()[0])
                        
                        if diameter < (2 * MIN_P + drill):
                            diameter = 2 * MIN_P + drill
                        elif diameter > (2 * MAX_P + drill):
                            diameter = 2 * MAX_P + drill
                    except:
                        diameter = drill * PERC_P
            
                        if diameter < MIN_P:
                            diameter = 2 * MIN_P + drill
                        elif diameter > MAX_P:
                            diameter = 2 * MAX_P + drill
                        else:
                            diameter = 2 * diameter + drill
                    ####
                    if shape == "round":
                        layerNew.createObject()
                        layerNew.addCircle(x, y, diameter / 2.)
                        layerNew.addRotation(i['x'], i['y'], i['rot'])
                        layerNew.setChangeSide(i['x'], i['y'], i['side'])
                        layerNew.setFace()
                    elif shape == "square":
                        a = diameter / 2.
                        x1 = x - a
                        y1 = y - a
                        x2 = x + a
                        y2 = y + a
                        
                        layerNew.createObject()
                        layerNew.addRectangle(x1, y1, x2, y2)
                        layerNew.addRotation(x, y, ROT_2)
                        layerNew.addRotation(i['x'], i['y'], i['rot'])
                        layerNew.setChangeSide(i['x'], i['y'], i['side'])
                        layerNew.setFace()
                    elif shape == "long":
                        e = (elongationLong * diameter) / 200.
                        
                        layerNew.createObject()
                        layerNew.addPadLong(x, y, diameter / 2. + e, diameter / 2., 100)
                        layerNew.addRotation(x, y, ROT_2)
                        layerNew.addRotation(i['x'], i['y'], i['rot'])
                        layerNew.setChangeSide(i['x'], i['y'], i['side'])
                        layerNew.setFace()
                    elif shape == "offset":
                        e = (elongationOffset * diameter) / 100.
                        
                        layerNew.createObject()
                        layerNew.addPadOffset(x, y, diameter / 2., e)
                        layerNew.addRotation(x, y, ROT_2)
                        layerNew.addRotation(i['x'], i['y'], i['rot'])
                        layerNew.setChangeSide(i['x'], i['y'], i['side'])
                        layerNew.setFace()
                    elif shape == "octagon":
                        layerNew.createObject()
                        layerNew.addOctagon(x, y, diameter)
                        layerNew.addRotation(x, y, ROT_2)
                        layerNew.addRotation(i['x'], i['y'], i['rot'])
                        layerNew.setChangeSide(i['x'], i['y'], i['side'])
                        layerNew.setFace()
                elif j[0] == "smd" and layerSide == i['side']:  # smd
                    dx = float(re.search('dx="(.+?)"', data).groups()[0])
                    dy = float(re.search('dy="(.+?)"', data).groups()[0])
                    
                    try:
                        roundness = float(re.search('roundness="(.+?)"', data).groups()[0])
                    except:
                        roundness = 0
                    #
                    if dx == dy and roundness == 100:
                        layerNew.createObject()
                        layerNew.addCircle(x, y, dx / 2.)
                        layerNew.addRotation(i['x'], i['y'], i['rot'])
                        layerNew.setChangeSide(i['x'], i['y'], i['side'])
                        layerNew.setFace()
                    elif roundness:
                        layerNew.createObject()
                        layerNew.addPadLong(x, y, dx / 2., dy / 2., roundness)
                        layerNew.addRotation(x, y, ROT_2)
                        layerNew.addRotation(i['x'], i['y'], i['rot'])
                        layerNew.setChangeSide(i['x'], i['y'], i['side'])
                        layerNew.setFace()
                    else:
                        x1 = x - dx / 2.
                        y1 = y - dy / 2.
                        x2 = x + dx / 2.
                        y2 = y + dy / 2.
                        
                        layerNew.createObject()
                        layerNew.addRectangle(x1, y1, x2, y2)
                        layerNew.addRotation(x, y, ROT_2)
                        layerNew.addRotation(i['x'], i['y'], i['rot'])
                        layerNew.setChangeSide(i['x'], i['y'], i['side'])
                        layerNew.setFace()
        ###
        layerNew.generuj(layerS)
        layerNew.updatePosition_Z(layerS)
        viewProviderLayerSilkObject(layerS.ViewObject)
        layerS.ViewObject.ShapeColor = layerColor
        grp.addObject(layerS)


    def getSilkLayer(self, doc, layerNumber, grp, layerName, layerColor, defHeight):
        layerName = "{0}_{1}".format(layerName, layerNumber)
        layerSide = PCBlayers[softLayers["eagle"][layerNumber][1]][0]
        layerType = PCBlayers[softLayers["eagle"][layerNumber][1]][3]
        
        layerS = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", layerName)
        layerNew = layerSilkObject(layerS, layerType)
        layerNew.defHeight = defHeight
        ##
        self.getLibraries()
        self.getElements()
        
        for i in self.elements:
            if i['side'] == 0:
                if layerNumber in [21, 51]:  # bottom
                    szukanaWarstwa = [layerNumber + 1]
                elif layerNumber in [22, 52]:  # top
                    szukanaWarstwa = [layerNumber - 1]
            else:
                szukanaWarstwa = [layerNumber]
            #
            # linie/luki
            for j in self.getWires(self.libraries[i['library']][i['package']], szukanaWarstwa, [i['x'], i['y']]):
                if not j['curve']:
                    layerNew.createObject()
                    layerNew.addLineWidth(j['x1'], j['y1'], j['x2'], j['y2'], j['width'], j['style'])
                    layerNew.addRotation(i['x'], i['y'], i['rot'])
                    layerNew.setChangeSide(i['x'], i['y'], i['side'])
                    layerNew.setFace()
                else:
                    layerNew.createObject()
                    layerNew.addArcWidth([j['x1'], j['y1']], [j['x2'], j['y2']], j['curve'], j['width'], j['cap'])
                    layerNew.addRotation(i['x'], i['y'], i['rot'])
                    layerNew.setChangeSide(i['x'], i['y'], i['side'])
                    layerNew.setFace()
            # okregi
            for j in self.getCircles(self.libraries[i['library']][i['package']], szukanaWarstwa, [i['x'], i['y']]):
                layerNew.createObject()
                layerNew.addCircle(j['x'], j['y'], j['r'], j['width'])
                layerNew.addRotation(i['x'], i['y'], i['rot'])
                layerNew.setChangeSide(i['x'], i['y'], i['side'])
                layerNew.setFace()
            # kwadraty
            for j in self.getRectangle(self.libraries[i['library']][i['package']], szukanaWarstwa, [i['x'], i['y']]):
                layerNew.createObject()
                layerNew.addRectangle(j['x1'], j['y1'], j['x2'], j['y2'])
                layerNew.addRotation(j['xs'], j['ys'], j['rot'])
                layerNew.addRotation(i['x'], i['y'], i['rot'])
                layerNew.setChangeSide(i['x'], i['y'], i['side'])
                layerNew.setFace()
            # polygon
            for j in self.getPolygons(self.libraries[i['library']][i['package']], szukanaWarstwa):
                layerNew.createObject()
                layerNew.addPolygon(self.getPolygon(j, i['x'], i['y']))
                layerNew.addRotation(i['x'], i['y'], i['rot'])
                layerNew.setChangeSide(i['x'], i['y'], i['side'])
                layerNew.setFace()
        ######
        ######
        dane = self.getSection('plain')
        # linie/luki
        for i in self.getWires(dane, layerNumber):
            if not i['curve']:
                layerNew.createObject()
                layerNew.addLineWidth(i['x1'], i['y1'], i['x2'], i['y2'], i['width'])
                layerNew.setFace()
            else:
                layerNew.createObject()
                layerNew.addArcWidth([i['x1'], i['y1']], [i['x2'], i['y2']], i['curve'], i['width'], i['cap'])
                layerNew.setFace()
        # kola
        for i in self.getCircles(dane, layerNumber):
            layerNew.createObject()
            layerNew.addCircle(i['x'], i['y'], i['r'], i['width'])
            layerNew.setFace()
        # kwadraty
        for i in self.getRectangle(dane, layerNumber):
            layerNew.createObject()
            layerNew.addRectangle(i['x1'], i['y1'], i['x2'], i['y2'])
            layerNew.addRotation(i['xs'], i['ys'], i['rot'])
            layerNew.setFace()
        # polygon
        for i in self.getPolygons(dane, layerNumber):
            layerNew.createObject()
            layerNew.addPolygon(self.getPolygon(i))
            layerNew.setFace()
        #######
        layerNew.generuj(layerS)
        layerNew.updatePosition_Z(layerS)
        viewProviderLayerSilkObject(layerS.ViewObject)
        layerS.ViewObject.ShapeColor = layerColor
        grp.addObject(layerS)

        
    def getAnnotations(self, dane1, mode='anno'):
        adnotacje = []
        #
        for i in dane1:
            if not isinstance(i, str):
                i = ' '.join(i)
            
            x = float(re.search('x="(.+?)"', i).groups()[0])
            y = float(re.search('y="(.+?)"', i).groups()[0])
            size = float(re.search('size="(.+?)"', i).groups()[0])
        
            try:
                mainROT = re.search('rot="(.+?)"', i).groups()[0]
                
                try:
                    rot = float(re.search('R(.*)', mainROT).groups()[0])  # kat o jaki zostana obrocone elementy
                except:
                    rot = 0  # kat o jaki zostana obrocone elementy
                    
                try:
                    float(re.search('MR(.*)', mainROT).groups()[0])  # dolna warstwa
                    mirror = 1
                except:
                    mirror = 0
                    
                try:
                    float(re.search('SR(.*)', i).groups()[0])  # napis bez mirrora
                    spin = True
                except:
                    spin = False
            except:
                rot = 0  # kat o jaki zostana obrocone elementy
                mirror = 0
                spin = False

            if int(re.search('layer="(.+?)"', i).groups()[0]) in [16, 22, 24, 26, 28, 52]:
                side = 'BOTTOM'
            else:
                side = 'TOP'

            try:
                align = float(re.search('align="(.+?)"', i).groups()[0])  # napis bez mirrora
            except:
                align = "bottom-left"
            
            if mode == 'anno':
                try:
                    txt = re.search('>(.*)', i, re.MULTILINE|re.DOTALL).groups()[0]
                except AttributeError:
                    txt = ''
            else:
                txt = re.search('name="(.+?)"', i).groups()[0]
            
            #try:
                #font = dane1[i].getAttribute("font")
            #except:
            font = 'proportional'
                
            try:
                display = re.search('display="(.+?)"', i).groups()[0]
                
                if display == "off":
                    display = False
                else:
                    display = True
            except:
                display = True
            
            adnotacje.append([txt, x, y, size, rot, side, align, spin, mirror, font, display])
        #
        return adnotacje

    def getDimensions(self):
        wymiary = []
        #
        data = self.getSection('plain')
        for i in re.findall('<dimension x1="(.+?)" y1="(.+?)" x2="(.+?)" y2="(.+?)" x3="(.+?)" y3="(.+?)" textsize="(.+?) layer=".+?"/>', data):
            x1 = float(i[0])
            y1 = float(i[1])
            x2 = float(i[2])
            y2 = float(i[3])
            x3 = float(i[4])
            y3 = float(i[5])
        
            wymiary.append([x1, y1, x2, y2, x3, y3])
        return wymiary
