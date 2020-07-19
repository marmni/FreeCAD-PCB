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
import re
from xml.dom import minidom
#
from PCBconf import softLayers, eagleColorsDefinition
from PCBobjects import *
from formats.dialogMAIN_FORM import dialogMAIN_FORM
from formats.baseModel import baseModel


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
        
        self.tentedViasLimit.setValue(getSettings(self.projektBRD, "mlViaStopLimit", True))
        ##
        self.generateLayers([20, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 44, 45, 46, 91, 92, 93, 94, 95, 96, 97, 98, 99, 116]) # blocked layers
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
            
            if int(i.getAttribute("color")) in eagleColorsDefinition:
                layerColor = eagleColorsDefinition[int(i.getAttribute("color"))]
            else:
                layerColor = None
            
            dane[layerNumber] = {"name": layerName, "color": layerColor}
        
        # annotations
        dane[0] = {"name": softLayers[self.databaseType][0]["description"], "color": softLayers[self.databaseType][0]["color"]}
        #
        return dane


class EaglePCB(baseModel):
    def __init__(self, filename, parent):
        self.fileName = filename
        self.dialogMAIN = dialogMAIN(self.fileName)
        self.databaseType = "eagle"
        self.parent = parent
        #
        self.libraries = {}
        self.elements = []
    
    def setProject(self):
        self.projektBRD = minidom.parse(self.fileName)
    
    def getPCB(self, borderObject):
        dane = self.getSection('plain')
        
        for i in self.getWires(dane, 20):
            if not i['curve']:
                borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(i['x1'], i['y1'], 0), FreeCAD.Vector(i['x2'], i['y2'], 0)))
            else:
                [x3, y3] = self.arcMidPoint([i['x1'], i['y1']], [i['x2'], i['y2']], i['curve'])
                arc = Part.ArcOfCircle(FreeCAD.Vector(i['x1'], i['y1'], 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(i['x2'], i['y2'], 0.0))
                borderObject.addGeometry(arc)
        ######
        for i in self.getCircles(dane, 20):
            borderObject.addGeometry(Part.Circle(FreeCAD.Vector(i['x'], i['y']), FreeCAD.Vector(0, 0, 1), i['r']))
        ######
        self.getLibraries()
        self.getElements()
        
        for i in self.elements:
            ROT = i['rot']
            ########
            #linie/luki
            for j in self.getWires(self.libraries[i['library']][i['package']], 20, [i['x'], i['y']]):
                [x1, y1] = self.obrocPunkt2([j['x1'], j['y1']], [i['x'], i['y']], ROT)
                [x2, y2] = self.obrocPunkt2([j['x2'], j['y2']], [i['x'], i['y']], ROT)
                if i['side'] == 0:
                    x1 = self.odbijWspolrzedne(x1, i['x'])
                    x2 = self.odbijWspolrzedne(x2, i['x'])
                
                if not j['curve']:
                    borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x2, y2, 0)))
                else:
                    curve = j['curve']
                    if i['side'] == 0:
                        curve *= -1
                    
                    [x3, y3] = self.arcMidPoint([x1, y1], [x2, y2], j['curve'])
                    #arc = Part.Arc(FreeCAD.Vector(x1, y1, 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(x2, y2, 0.0))
                    arc = Part.ArcOfCircle(FreeCAD.Vector(x1, y1, 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(x2, y2, 0.0))
                    borderObject.addGeometry(arc)
            #okregi
            for j in self.getCircles(self.libraries[i['library']][i['package']], 20, [i['x'], i['y']]):
                [x, y] = self.obrocPunkt2([j['x'], j['y']], [i['x'], i['y']], ROT)
                if i['side'] == 0:
                    x = self.odbijWspolrzedne(x, i['x'])
                
                borderObject.addGeometry(Part.Circle(FreeCAD.Vector(x, y), FreeCAD.Vector(0, 0, 1), j['r']))

    def getLibraries(self):
        if len(self.libraries) == 0:
            for i in self.projektBRD.getElementsByTagName("library"):
                if not i.getAttribute('name') in self.libraries:
                    self.libraries[i.getAttribute('name')] = {}
                
                for j in i.getElementsByTagName("package"):
                    if not j.getAttribute('name') in self.libraries[i.getAttribute('name')]:
                        self.libraries[i.getAttribute('name')][j.getAttribute('name')] = j

    def translateBoolValue(self, value):
        value = value.strip()
        
        if value in ['no', '']:
            value = False
        elif value in ['yes']:
            value = True
        
        return value

    def getElements(self):
        if len(self.elements) == 0:
            for i in self.projektBRD.getElementsByTagName("element"):
                rot = 0
                side = 1
                name = i.getAttribute('name').strip()
                package = i.getAttribute('package').strip()
                #
                if 'R' in i.getAttribute('rot'):
                    rot = int(re.sub("[^0-9]", "", i.getAttribute('rot')))
                if 'M' in i.getAttribute('rot'):
                    side = 0
                #
                self.elements.append({
                    'name': name, 
                    'library': i.getAttribute('library'), 
                    'package': package, 
                    'value': i.getAttribute('value'), 
                    'x': float(i.getAttribute('x')), 
                    'y': float(i.getAttribute('y')), 
                    'locked': self.translateBoolValue(i.getAttribute('locked')),
                    'populated': self.translateBoolValue(i.getAttribute('populate')), 
                    'smashed': self.translateBoolValue(i.getAttribute('smashed')), 
                    'rot': rot, 
                    'side': side,
                    'dataElement': i
                })
                
    def getSection(self, sectionName):
        if sectionName.strip() == "":
            FreeCAD.Console.PrintWarning("Incorrect parameter (Section)!\n")
            return ''
        
        try:
            return self.projektBRD.getElementsByTagName(sectionName)[0]
        except:
            return ''
    
    def getPolygons(self, section, layer):
        if not isinstance(layer, list):
            layer = [layer]
            
        data = []
        for lay in layer:
            pol = []
            for i in section.getElementsByTagName("polygon"):
                if int(i.getAttribute('layer')) == lay:
                    for j in i.getElementsByTagName("vertex"):
                        x = float(j.getAttribute('x'))
                        y = float(j.getAttribute('y'))
                        curve = j.getAttribute('curve')
                        
                        pol.append([x, y, curve, i])
                    data.append(pol)
        return data
    
    def getRectangle(self, section, layer, m=[0,0]):
        if not isinstance(layer, list):
            layer = [layer]
            
        data = []
        for lay in layer:
            for i in section.getElementsByTagName("rectangle"):
                if int(i.getAttribute('layer')) == lay:
                    x1 = float(i.getAttribute('x1'))
                    y1 = float(i.getAttribute('y1'))
                    x2 = float(i.getAttribute('x2'))
                    y2 = float(i.getAttribute('y2'))
                    
                    if [x1, y1] == [x2, y2]:
                        continue
                    if m[0] != 0:
                        x1 += m[0]
                        x2 += m[0]
                    if m[1] != 0:
                        y1 += m[1]
                        y2 += m[1]
                    
                    if i.getAttribute('rot') == "":
                        rot = 0.
                    else:
                        rot = float(re.search('R([0-9,.-]*)', i.getAttribute('rot')).groups()[0])
                        
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
                        'data': i
                    })
        
        return data
    
    def getCircles(self, section, layer, m=[0,0]):
        if not isinstance(layer, list):
            layer = [layer]
        
        data = []
        for lay in layer:
            for i in section.getElementsByTagName("circle"):
                if int(i.getAttribute('layer')) == lay:
                    x = float(i.getAttribute('x'))
                    y = float(i.getAttribute('y'))
                    r = float(i.getAttribute('radius'))
                    w = float(i.getAttribute('width'))
                    
                    #if w == 0:
                        #w = 0.01
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
                        'data': i
                    })
        
        return data
            
    def getWires(self, section, layer, m=[0,0]):
        if not isinstance(layer, list):
            layer = [layer]
        
        data = []
        for lay in layer:
            for i in section.getElementsByTagName("wire"):
                if int(i.getAttribute('layer')) == lay:
                    #for i in re.findall('<wire\s+x1="(.+?)"\s+y1="(.+?)"\s+x2="(.+?)"\s+y2="(.+?)"\s+width="(.+?)"\s+layer="%s"(\s+style="(.+?)"|)(\s+curve="(.+?)"|)(\s+cap="(.+?)"|)/>' % str(lay), section):
                    x1 = float(i.getAttribute('x1'))
                    y1 = float(i.getAttribute('y1'))
                    x2 = float(i.getAttribute('x2'))
                    y2 = float(i.getAttribute('y2'))
                    width = float(i.getAttribute('width'))
                    style = i.getAttribute('style')
                    
                    if [x1, y1] == [x2, y2]:
                        continue
                    if m[0] != 0:
                        x1 += m[0]
                        x2 += m[0]
                    if m[1] != 0:
                        y1 += m[1]
                        y2 += m[1]
                    
                    if i.getAttribute('curve') == '':
                        curve = 0
                    else:
                        curve = float(i.getAttribute('curve'))
                    
                    if i.getAttribute('cap') == '':
                        cap = 'round'
                    else:
                        cap = i.getAttribute('cap')
                        
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
                        'data': i
                    })
            
        return data
    
    ##############################
    # MAIN FUNCTIONS
    ##############################
    
    def defineFunction(self, layerNumber):
        if layerNumber in [17, 18]:  # pady
            return "pads"
        elif layerNumber in [1, 16]:  # paths
            return "paths"
        elif layerNumber == 47:  # MEASURES
            return "measures"
        elif layerNumber in [35, 36]:  # glue
            return "glue"
        elif layerNumber in [39, 40, 41, 42, 43]:  # ConstraintAreas
            return "constraint"
        elif layerNumber == 0:
            return "annotations"
        else:
            return "silk"

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
                
                
                if polygonL[k][2] == "":
                    poin.append(['Line', x1, y1, x2, y2])
                else:
                    curve = float(polygonL[k][2])
                    poin.append(['Arc3P', x2, y2, x1, y1, curve])
        return poin

    ##############################
    # LAYERS
    ##############################

    def getHoles(self, holesObject, types, Hmin, Hmax):
        ''' holes/vias '''
        holesList = []
        
        # holes
        if types['H']:
            for i in self.projektBRD.getElementsByTagName("plain")[0].getElementsByTagName("hole"):
                x = float(i.getAttribute('x'))
                y = float(i.getAttribute('y'))
                r = float(i.getAttribute('drill')) / 2. + 0.001
                
                holesList = self.addHoleToObject(holesObject, Hmin, Hmax, types['IH'], x, y, r, holesList)
        # vias
        if types['V']:
            for i in self.projektBRD.getElementsByTagName("signals")[0].getElementsByTagName("via"):
                x = float(i.getAttribute('x'))
                y = float(i.getAttribute('y'))
                r = float(i.getAttribute('drill')) / 2. + 0.001
                
                holesList = self.addHoleToObject(holesObject, Hmin, Hmax, types['IH'], x, y, r, holesList)
        ## pady
        self.getLibraries()
        self.getElements()
        
        for i in self.elements:
            if types['H']:  # holes
                for j in self.libraries[i['library']][i['package']].getElementsByTagName("hole"):
                    xs = float(j.getAttribute('x'))
                    ys = float(j.getAttribute('y'))
                    r = float(j.getAttribute('drill')) / 2. + 0.001
                    
                    [xR, yR] = self.obrocPunkt([xs, ys], [i['x'], i['y']], i['rot'])
                    if i['side'] == 0:  # odbicie wspolrzednych
                        xR = self.odbijWspolrzedne(xR, i['x'])
                    
                    holesList = self.addHoleToObject(holesObject, Hmin, Hmax, types['IH'], xR, yR, r, holesList)
            if types['P']:  # pads
                for j in self.libraries[i['library']][i['package']].getElementsByTagName("pad"):
                    xs = float(j.getAttribute('x'))
                    ys = float(j.getAttribute('y'))
                    r = float(j.getAttribute('drill')) / 2. + 0.001
                    
                    [xR, yR] = self.obrocPunkt([xs, ys], [i['x'], i['y']], i['rot'])
                    if i['side'] == 0:  # odbicie wspolrzednych
                        xR = self.odbijWspolrzedne(xR, i['x'])
                    
                    holesList = self.addHoleToObject(holesObject, Hmin, Hmax, types['IH'], xR, yR, r, holesList)

    def getParts(self):
        self.getLibraries()
        self.getElements()
        parts = []
        #
        for k in self.elements:
            i = dict(k)
            #
            if i['side'] == 1:
                i['side'] = "TOP"
            else:
                i['side'] = "BOTTOM"
            #
            if not i['smashed']:
                for j in self.getAnnotations(self.libraries[i['library']][i['package']].getElementsByTagName("text")):
                    x1 = i['x'] + j["x"]
                    y1 = i['y'] + j["y"]
                    
                    if i['side'] == "BOTTOM":
                        x1 = self.odbijWspolrzedne(x1, i['x'])
                        j["side"] = "BOTTOM"
                        #j["mirror"] = True
                        
                        [xR, yR] = self.obrocPunkt2([x1, y1], [i['x'], i['y']], -i['rot'])
                    else:
                        [xR, yR] = self.obrocPunkt2([x1, y1], [i['x'], i['y']], i['rot'])
                    #
                    j["rot"] = j["rot"] + i['rot']
                    j["x"] = xR
                    j["y"] = yR
                    #
                    j["mode"] = 'param'
                    
                    if j["text"] in ['&gt;NAME', ">NAME"]:
                        j["text"] = 'NAME'
                        i['EL_Name'] = j
                    elif j["text"] in ['&gt;VALUE', ">VALUE"]:
                        j["text"] = 'VALUE'
                        i["EL_Value"] = j
            #
            for attr in i['dataElement'].getElementsByTagName('attribute'):
                # <uros@isotel.eu> fix to get a FREECAD attribute out, it's overall all ugly since original
                # code is using regex to parse xml instead of dom parser - all regex should be replaced with the DOM
                if attr.getAttribute('name') == 'FREECAD': # use different 3D model for current package
                    if attr.getAttribute('value').strip() == "":
                        FreeCAD.Console.PrintWarning(u"Empty attribute 'FREECAD' found for the element {0}. Default package will be used.\n".format(i["name"]))
                    else:
                        FreeCAD.Console.PrintWarning(u"Package '{1}' will be used for the element {0} (instead of {2}).\n".format(i["name"], attr.getAttribute('value').strip(), i['package']))
                        i['package'] = attr.getAttribute('value').strip()
                        #if not self.parent.partExist(['', attr.getAttribute('value').strip()], '')[0]:
                        #    FreeCAD.Console.PrintWarning(u"\tIncorrect package '{1}' set for the element {0}.\n".format(i["name"], attr.getAttribute('value').strip()))
                        
                        #if self.parent.partExist(['', attr.getAttribute('value').strip()], '')[0]:
                            # FreeCAD.Console.PrintWarning(u"Package '{1}' will be used for the element {0} (instead of {2}).\n".format(i["name"], attr.getAttribute('value').strip(), i['package']))
                            # package = attr.getAttribute('value').strip()
                        # else:
                            # FreeCAD.Console.PrintWarning(u"Incorrect package '{1}' set for the element {0}. Default package will be used.\n".format(i["name"], attr.getAttribute('value').strip()))
                elif attr.getAttribute('name') in ['NAME', 'VALUE'] and i['smashed']:
                    data = self.getAnnotations([attr], mode='param')[0]
                    
                    if data["text"] == "NAME":
                        i['EL_Name'] = data
                        #i['EL_Name']['rot'] = i['EL_Name']['rot'] - i['rot']
                    elif attr.getAttribute('name') == "VALUE":
                        i['EL_Value'] = data
                        #i['EL_Value']['rot'] = i['EL_Value']['rot'] - i['rot']
            #########################
            if 'EL_Name' not in i:
                x1 = i['x'] - 0.5
                y1 = i['y'] - 0.5
                side = "TOP"
                
                if i['side'] == "BOTTOM":
                    x1 = self.odbijWspolrzedne(x1, i['x'])
                    side = "BOTTOM"
                    #j["mirror"] = True
                    
                    [xR, yR] = self.obrocPunkt2([x1, y1], [i['x'], i['y']], -i['rot'])
                else:
                    [xR, yR] = self.obrocPunkt2([x1, y1], [i['x'], i['y']], i['rot'])
                #
                i['EL_Name'] = {
                    "text": "NAME",
                    "x": xR,
                    "y": yR,
                    "z": 0,
                    "size": 1.27,
                    'rot': i['rot'], 
                    'side': side, 
                    'align': 'center', 
                    'spin': True, 
                    'font': 'Proportional', 
                    'display': True, 
                    'distance': 50, 
                    'tracking': 0, 
                    'mode': 'param'
                }
            #
            if 'EL_Value' not in i:
                x1 = i['x'] + 0.5
                y1 = i['y'] + 0.5
                side = "TOP"
                
                if i['side'] == "BOTTOM":
                    x1 = self.odbijWspolrzedne(x1, i['x'])
                    side = "BOTTOM"
                    #j["mirror"] = True
                    
                    [xR, yR] = self.obrocPunkt2([x1, y1], [i['x'], i['y']], -i['rot'])
                else:
                    [xR, yR] = self.obrocPunkt2([x1, y1], [i['x'], i['y']], i['rot'])
                #
                i['EL_Value'] = {
                    "text": "VALUE",
                    "x": xR,
                    "y": yR,
                    "z": 0,
                    "size": 1.27,
                    'rot': i['rot'], 
                    'side': side, 
                    'align': 'center', 
                    'spin': True, 
                    'font': 'Proportional', 
                    'display': True, 
                    'distance': 50, 
                    'tracking': 0, 
                    'mode': 'param'
                }
            #####################
            # RESULT - EXAMPLE
            #####################
            # i = {
                # 'name': 'E$2', 
                # 'library': 'eagle-ltspice', 
                # 'package': 'R0806', 
                # 'value': '', 
                # 'x': 19.0, 
                # 'y': 5.5, 
                # 'locked': '', 
                # 'populated': '', 
                # 'smashed': 'yes',
                # 'rot': 90, 
                # 'side': 'TOP', 
                # 'dataElement': <DOM Element: element at 0x1bc2634cf20>, 
                # 'EL_Name': {
                    # 'text': 'NAME', 
                    # 'x': 16.73,
                    # 'y': 6.23, 
                    # 'z': 0, 
                    # 'size': 1.27, 
                    # 'rot': 135, 
                    # 'side': 'TOP', 
                    # 'align': 'center', 
                    # 'spin': True, 
                    # 'font': 'Proportional', 
                    # 'display': True, 
                    # 'distance': 50, 
                    # 'tracking': 0, 
                    # 'mode': 'param'
                # }, 
                # 'EL_Value': {
                    # 'text': 'VALUE', 
                    # 'x': 21.54, 
                    # 'y': 4.23,
                    # 'z': 0, 
                    # 'size': 1.27, 
                    # 'rot': 90, 
                    # 'side': 'TOP', 
                    # 'align': 'bottom-left', 
                    # 'spin': True, 
                    # 'font': 'Proportional', 
                    # 'display': True, 
                    # 'distance': 50, 
                    # 'tracking': 0, 
                    # 'mode': 'param'}
            # }
            ##########################################
            ##########################################
            parts.append(i)
        #
        return parts

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
        
    def getPolygonsFromCopperLayer(self, layerNew, layerNumber, display=[True, True, True, False]):
        self.addStandardShapes(self.projektBRD.getElementsByTagName("signals")[0], layerNew, [layerNumber[0]], display, getSignals=True)
        
    def getPaths(self, layerNew, layerNumber, display=[True, True, True, False]):
        self.addStandardShapes(self.projektBRD.getElementsByTagName("signals")[0], layerNew, [layerNumber[0]], display, getSignals=True)

    def getSettings(self, paramName):
        for i in self.projektBRD.getElementsByTagName("param"):
            if i.getAttribute('name') == paramName:
                dane = re.search(r'(.[^a-z]*)(.*)', i.getAttribute('value')).groups()
                wartosc = float(dane[0])
                
                if dane[1] == 'mil':
                    wartosc *= 0.0254

                return wartosc
    
    def getConstraintAreas(self, layerNumber):
        areas = []
        # kola
        for i in self.getCircles(self.projektBRD.getElementsByTagName("plain")[0], layerNumber):
            areas.append(['circle', i['x'], i['y'], i['r'], i['width']])
        # kwadraty
        for i in self.getRectangle(self.projektBRD.getElementsByTagName("plain")[0], layerNumber):
            areas.append(['rect', i['x1'], i['y1'], i['x2'], i['y2'], 0, i['rot']])
        # polygon
        for i in self.getPolygons(self.projektBRD.getElementsByTagName("plain")[0], layerNumber):
            areas.append(['polygon', self.getPolygon(i)])
        #
        return areas
    
    def getGlue(self, layerNumber):
        glue = {}
        # line/arc
        for i in self.getWires(self.projektBRD.getElementsByTagName("plain")[0], [layerNumber[0]]):
            if not i['width'] in glue.keys():
                glue[i['width']] = []
            
            if not i['curve']:
                glue[i['width']].append(['line', i['x1'], i['y1'], i['x2'], i['y2']])
            else:
                glue[i['width']].append(['arc', i['x2'], i['y2'], i['x1'], i['y1'], i['curve'], i['cap']])
        # circle
        for i in self.getCircles(self.projektBRD.getElementsByTagName("plain")[0], layerNumber[0]):
            if not i['width'] in glue.keys():
                glue[i['width']] = []
            
            glue[i['width']].append(['circle', i['x'], i['y'], i['r']])
        ## rectangle
        #for i in self.getRectangle(self.projektBRD.getElementsByTagName("plain")[0], [layerNumber[0]]):
            #if not 1 in glue.keys():
                #glue[1] = []
            
            #glue[i['width']].append(['line', i['x1'], i['y1'], i['x2'], i['y1']])
            #glue[i['width']].append(['line', i['x2'], i['y1'], i['x2'], i['y2']])
            #glue[i['width']].append(['line', i['x2'], i['y2'], i['x1'], i['y2']])
            #glue[i['width']].append(['line', i['x1'], i['y2'], i['x1'], i['y1']])
            
            #glue[i['width']].append(['line', i['x1'], i['y1'], i['x2'], i['y2']])
            #glue[i['width']].append(['line', i['x1'], i['y2'], i['x2'], i['y1']])
            
        #
        return glue
    
    def addStandardShapes(self, dane, layerNew, layerNumber, display=[True, True, True, True], parent=None, getSignals=False):
        if parent:
            X = parent['x']
            Y = parent['y']
        else:
            X = 0
            Y = 0
        
        # linie/luki
        if display[0]:
            for i in self.getWires(dane, layerNumber, [X, Y]):
                if not i['curve']:  # LINE
                    layerNew.addLineWidth(i['x1'], i['y1'], i['x2'], i['y2'], i['width'])
                    if parent:
                        layerNew.addRotation(parent['x'], parent['y'], parent['rot'])
                        layerNew.setChangeSide(parent['x'], parent['y'], parent['side'])
                    if getSignals:
                        layerNew.setFace(signalName=i['data'].parentNode.getAttribute('name'))
                    else:
                        layerNew.setFace()
                else:  # ARC
                    if layerNew.addArcWidth([i['x1'], i['y1']], [i['x2'], i['y2']], i['curve'], i['width'], i['cap']):
                        if parent:
                            layerNew.addRotation(parent['x'], parent['y'], parent['rot'])
                            layerNew.setChangeSide(parent['x'], parent['y'], parent['side'])
                        if getSignals:
                            layerNew.setFace(signalName=i['data'].parentNode.getAttribute('name'))
                        else:
                            layerNew.setFace()
        # okregi
        if display[1]:
            for i in self.getCircles(dane, layerNumber, [X, Y]):
                layerNew.addCircle(i['x'], i['y'], i['r'], i['width'])
                if parent:
                    layerNew.addRotation(parent['x'], parent['y'], parent['rot'])
                    layerNew.setChangeSide(parent['x'], parent['y'], parent['side'])
                layerNew.setFace()
                if i['width'] > 0:
                    layerNew.circleCutHole(i['x'], i['y'], i['r'] - i['width'] / 2.)
        # kwadraty
        if display[2]:
            for i in self.getRectangle(dane, layerNumber, [X, Y]):
                dx = i['x1'] - i['x2']
                dy = i['y1'] - i['y2']
                
                layerNew.addRectangle(i['x1'], i['y1'], i['x2'], i['y2'])
                layerNew.addRotation(i['x1'] - (dx / 2.), i['y1'] - (dy / 2.), i['rot'])
                if parent:
                    layerNew.addRotation(parent['x'], parent['y'], parent['rot'])
                    layerNew.setChangeSide(parent['x'], parent['y'], parent['side'])
                layerNew.setFace()
        ## polygon
        if display[3]:
            for i in self.getPolygons(dane, layerNumber):
                #if getSignals:
                    #signalName = i[0][-1].parentNode.getAttribute('name')
                    # pol = self.getPolygon(i)
                    # polygonN = layerNew.addPolygon(pol, True)
                    
                    # if polygonN:
                
                        # else:
                            # isolate = self.getSettings('mdWireWire')
                        
                        # polygonN = layerNew.createFace(polygonN)
                        # #polygonN = layerNew.cutOffPaths(polygonN, signalName, isolate)
                        # layerNew.addNewObject(polygonN, signalName)
                        # #Part.show(polygonN)
                # else:
                if parent:
                    layerNew.addPolygon(self.getPolygon(i, parent['x'], parent['y']))
                    layerNew.addRotation(parent['x'], parent['y'], parent['rot'])
                    layerNew.setChangeSide(parent['x'], parent['y'], parent['side'])
                else:
                    layerNew.addPolygon(self.getPolygon(i))
                
                if getSignals:
                    isolate = self.getSettings('mdWireWire')
                    
                    if i[0][-1].getAttribute('isolate'):
                        #if float(i[0][-1].getAttribute('isolate')) > isolate:
                        isolate = float(i[0][-1].getAttribute('isolate'))
                    layerNew.setFace(signalName=[i[0][-1].parentNode.getAttribute('name'), isolate])
                else:
                    layerNew.setFace()
    
    def getDimensions(self):
        wymiary = []
        #
        for i in self.projektBRD.getElementsByTagName("plain")[0].getElementsByTagName("dimension"):
            x1 = float(i.getAttribute('x1'))
            y1 = float(i.getAttribute('y1'))
            x2 = float(i.getAttribute('x2'))
            y2 = float(i.getAttribute('y2'))
            x3 = float(i.getAttribute('x3'))
            y3 = float(i.getAttribute('y3'))
            dtype = i.getAttribute('dtype')
            
            wymiary.append([x1, y1, x2, y2, x3, y3, dtype])
        
        return wymiary
    
    def getPads(self, layerNew, layerNumber, layerSide, tentedViasLimit, tentedVias):
        MAX_P = self.getSettings('rlMaxPadTop')
        MIN_P = self.getSettings('rlMinPadTop')
        PERC_P = self.getSettings('rvPadTop')
        
        MAX_V = self.getSettings('rlMaxViaOuter')
        MIN_V = self.getSettings('rlMinViaOuter')
        PERC_V = self.getSettings('rvViaOuter')
        #####
        for i in self.projektBRD.getElementsByTagName("via"):
            x = float(i.getAttribute('x'))
            y = float(i.getAttribute('y'))
            drill = float(i.getAttribute('drill'))
            
            shape = "round"
            if i.getAttribute('shape'):
                shape = i.getAttribute('shape')
            
            alwaysstop = False
            if i.getAttribute('alwaysstop'):
                alwaysstop = True
            #
            if i.getAttribute('diameter') != "":
                diameter = float(i.getAttribute('diameter'))
                
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
            ##### ##### ##### 
            ##### tented dVias
            if self.filterTentedVias(tentedViasLimit, tentedVias, drill, alwaysstop):
                continue
            ##### ##### ##### 
            if shape == "round":
                layerNew.addCircle(x, y, diameter / 2.)
                layerNew.setFace()
            elif shape == "square":
                a = diameter / 2.
                x1 = x - a
                y1 = y - a
                x2 = x + a
                y2 = y + a
                
                layerNew.addRectangle(x1, y1, x2, y2)
                layerNew.setFace()
            elif shape == "octagon":
                layerNew.addOctagon(x, y, diameter)
                layerNew.setFace()
        #####
        if not tentedVias:
            self.getLibraries()
            self.getElements()
            elongationOffset = self.getSettings('psElongationOffset')
            elongationLong = self.getSettings('psElongationLong')
            #layerSide = softLayers[self.databaseType][layerNumber]["side"]
            
            for i in self.elements:
                for j in self.libraries[i['library']][i['package']].getElementsByTagName("smd") + self.libraries[i['library']][i['package']].getElementsByTagName("pad"):
                    x = float(j.getAttribute('x')) + i['x']
                    y = float(j.getAttribute('y')) + i['y']
                    ROT_2 = 0  # kat o jaki zostana obrocone elementy
                    
                    if j.getAttribute('rot'):
                        ROT_2 = int(re.sub("[^0-9]", "", j.getAttribute('rot')))  # kat o jaki zostana obrocone elementy
                    #####
                    if j.tagName == "pad":
                        drill = float(j.getAttribute('drill'))
                        
                        if j.getAttribute('shape'):
                            shape = j.getAttribute('shape')
                        else:
                            shape = "round"
                        
                        if shape == "":
                            shape = "round"
                        
                        if j.getAttribute('diameter'):
                            diameter = float(j.getAttribute('diameter'))
                            
                            if diameter < (2 * MIN_P + drill):
                                diameter = 2 * MIN_P + drill
                            elif diameter > (2 * MAX_P + drill):
                                diameter = 2 * MAX_P + drill
                        else:
                            diameter = drill * PERC_P
                
                            if diameter < MIN_P:
                                diameter = 2 * MIN_P + drill
                            elif diameter > MAX_P:
                                diameter = 2 * MAX_P + drill
                            else:
                                diameter = 2 * diameter + drill
                        ####
                        if shape == "round":  # +
                            layerNew.addCircle(x, y, diameter / 2.)
                            layerNew.addRotation(i['x'], i['y'], i['rot'])
                            layerNew.setChangeSide(i['x'], i['y'], i['side'])
                            layerNew.setFace()
                        elif shape == "square":  # +
                            a = diameter / 2.
                            x1 = x - a
                            y1 = y - a
                            x2 = x + a
                            y2 = y + a
                            
                            layerNew.addRectangle(x1, y1, x2, y2)
                            layerNew.addRotation(x, y, ROT_2)
                            layerNew.addRotation(i['x'], i['y'], i['rot'])
                            layerNew.setChangeSide(i['x'], i['y'], i['side'])
                            layerNew.setFace()
                        elif shape == "long":  # +
                            e = (elongationLong * diameter) / 200.
                            
                            layerNew.addPadLong(x, y, diameter / 2. + e, diameter / 2., 100)
                            layerNew.addRotation(x, y, ROT_2)
                            layerNew.addRotation(i['x'], i['y'], i['rot'])
                            layerNew.setChangeSide(i['x'], i['y'], i['side'])
                            layerNew.setFace()
                        elif shape == "offset":  # +
                            e = (elongationOffset * diameter) / 100.
                            
                            layerNew.addPadOffset(x, y, diameter / 2., e)
                            layerNew.addRotation(x, y, ROT_2)
                            layerNew.addRotation(i['x'], i['y'], i['rot'])
                            layerNew.setChangeSide(i['x'], i['y'], i['side'])
                            layerNew.setFace()
                        elif shape == "octagon":  # +
                            layerNew.addOctagon(x, y, diameter)
                            layerNew.addRotation(x, y, ROT_2)
                            layerNew.addRotation(i['x'], i['y'], i['rot'])
                            layerNew.setChangeSide(i['x'], i['y'], i['side'])
                            layerNew.setFace()
                    elif j.tagName == "smd":
                        padSide = softLayers[self.databaseType][int(j.getAttribute('layer'))]["side"]
                        
                        if i['side'] == 0:
                            padSide = softLayers[self.databaseType][softLayers[self.databaseType][int(j.getAttribute('layer'))]["mirrorLayer"]]["side"]
                        
                        if layerSide == padSide:  # smd
                            dx = float(j.getAttribute('dx'))
                            dy = float(j.getAttribute('dy'))
                            
                            if j.getAttribute('roundness'):
                                roundness = float(j.getAttribute('roundness'))
                            else:
                                roundness = 0
                            ######
                            if dx == dy and roundness == 100:  # +
                                layerNew.addCircle(x, y, dx / 2.)
                                layerNew.addRotation(i['x'], i['y'], i['rot'])
                                layerNew.setChangeSide(i['x'], i['y'], i['side'])
                                layerNew.setFace()
                            elif roundness:  # +
                                layerNew.addPadLong(x, y, dx / 2., dy / 2., roundness)
                                layerNew.addRotation(x, y, ROT_2)
                                layerNew.addRotation(i['x'], i['y'], i['rot'])
                                layerNew.setChangeSide(i['x'], i['y'], i['side'])
                                layerNew.setFace()
                            else:  # +
                                x1 = x - dx / 2.
                                y1 = y - dy / 2.
                                x2 = x + dx / 2.
                                y2 = y + dy / 2.
                                
                                layerNew.addRectangle(x1, y1, x2, y2)
                                layerNew.addRotation(x, y, ROT_2)
                                layerNew.addRotation(i['x'], i['y'], i['rot'])
                                layerNew.setChangeSide(i['x'], i['y'], i['side'])
                                layerNew.setFace()

    def getSilkLayer(self, layerNew, layerNumber, display=[True, True, True, True]):
        self.addStandardShapes(self.projektBRD.getElementsByTagName("plain")[0], layerNew, [layerNumber[0]], display)
        
    def getSilkLayerModels(self, layerNew, layerNumber):
        self.getLibraries()
        self.getElements()
        for i in self.elements:
            if i['side'] == 0:  # bottom side - get mirror
                try:
                    if softLayers[self.databaseType][layerNumber[0]]["mirrorLayer"]:
                        szukanaWarstwa = softLayers[self.databaseType][layerNumber[0]]["mirrorLayer"]
                except:
                    szukanaWarstwa = layerNumber[0]
            else:
                szukanaWarstwa = layerNumber[0]
            ####
            self.addStandardShapes(self.libraries[i['library']][i['package']], layerNew, [szukanaWarstwa], parent=i)
    
    def getNormalAnnotations(self):
        try:
            data = self.projektBRD.getElementsByTagName("plain")[0]
            return self.getAnnotations(data.getElementsByTagName("text"), mode='anno')
        except Exception as e:
            FreeCAD.Console.PrintWarning("4. {0}\n".format(e))
    
    def getAnnotations(self, dane1, mode='anno'):
        adnotacje = []
        #
        for i in dane1:
            # def. values
            rot = 0
            side = "TOP"
            spin = False
            distance = 50
            align = "bottom-left"
            font = 'Proportional'
            #
            x = float(i.getAttribute('x'))
            #
            y = float(i.getAttribute('y'))
            #
            size = float(i.getAttribute('size'))
            #
            if i.getAttribute('rot'):
                if 'S' in i.getAttribute('rot'):
                    spin = True
                if 'M' in i.getAttribute('rot'):
                    side = 'BOTTOM'
                if 'R' in i.getAttribute('rot'):
                    rot = int(re.sub("[^0-9]", "", i.getAttribute('rot')))
            #
            if i.getAttribute('align'):
                align = i.getAttribute('align')
            #
            if mode == 'anno':
                txt = i.firstChild.nodeValue
                #
                if txt.startswith(">") or txt.startswith("&gt;"):
                    for j in self.getSection("attributes").getElementsByTagName("attribute"):
                        if txt.replace(">", "") == j.getAttribute('name') or txt.replace("&gt;", "") == j.getAttribute('name'):
                            txt = j.getAttribute("value")
                            break
            else:
                txt = i.getAttribute('name')
            #
            if i.getAttribute('distance'):
                distance = int(i.getAttribute('distance'))
            #
            if i.getAttribute('font'):
                font = i.getAttribute('font').capitalize()
            #
            if i.getAttribute('display'):
                if i.getAttribute('display') == "off":
                    display = False
                else:
                    display = True
            else:
                display = True
            #
            adnotacje.append({
                "text": txt,
                "x": x,
                "y": y,
                "z": 0,
                "size": size,
                "rot": rot,
                "side": side,
                "align": align,
                "spin": spin,
                "font": font,
                "display": display,
                "distance": distance,
                "tracking": 0,
                "mode": mode
            })

        return adnotacje
