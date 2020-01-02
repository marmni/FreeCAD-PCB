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
import builtins
import re
from math import radians
#
from PCBconf import PCBlayers, softLayers
from PCBobjects import *
from formats.dialogMAIN_FORM import dialogMAIN_FORM
from command.PCBgroups import *
from PCBfunctions import mathFunctions, setProjectFile, filterHoles


class dialogMAIN(dialogMAIN_FORM):
    def __init__(self, filename=None, parent=None):
        dialogMAIN_FORM.__init__(self, parent)
        self.databaseType = "geda"
        #
        self.projektBRD = builtins.open(filename, "r").read().replace('\n', ' ')
        self.layersNames = self.getLayersNames()
        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetBool("boardImportThickness", True):
            self.gruboscPlytki.setValue(self.getBoardThickness())
        ##
        self.generateLayers() # blocked layers
        self.spisWarstw.sortItems(1)
    
    def getBoardThickness(self):
        pcbThickness = 1.5 # mm
        return pcbThickness
    
    def getLayersNames(self):
        dane = {}
        for i in re.findall("Layer\((.+?) \"(.+?)\" \"(.+?)\"\)", self.projektBRD):
            layerNumber = i[0]
            layerName = i[1]
            layerType = i[2]
            layerColor = None
            
            if layerName == "outline":
                continue
            
            dane[layerNumber] = {"name": layerName, "color": layerColor, "type": layerType, "number": layerNumber}
        
        # extra layers
        dane[0] = {"name": softLayers[self.databaseType]["anno"]["description"], "color": softLayers[self.databaseType]["anno"]["color"], "type": "anno", "number": 0}  # annotations
        dane[100000] = {"name": softLayers[self.databaseType]["padT"]["description"], "color": softLayers[self.databaseType]["padT"]["color"], "type": "pad", "number": 100000}
        dane[100001] = {"name": softLayers[self.databaseType]["padB"]["description"], "color": softLayers[self.databaseType]["padB"]["color"], "type": "pad", "number": 100001}
        #
        return dane


class gEDA_PCB(mathFunctions):
    '''Board importer for gEDA software'''
    def __init__(self, filename, parent):
        #self.groups = {}  # layers groups
        #
        self.fileName = filename
        self.dialogMAIN = dialogMAIN(self.fileName)
        self.databaseType = "geda"
        self.parent = parent
        self.elements = []
    
    def setProject(self):
        '''Load project from file'''
        #self.projektBRD = builtins.open(self.fileName, "r").read().replace('\r\n', '\n')
        self.projektBRD = setProjectFile(self.fileName)
        
        ##############
        try:
            re.search('PCB\s*\[.+? (.+?) (.+?)\]', self.projektBRD).groups()
            self.globalUnit = True  # mils
        except:
            self.globalUnit = False
        # ##############
        # # layers groups
        # # c: top
        # # s: bottom
        # data = re.search('Groups\("(.*?)"\)', self.projektBRD).groups()[0]
        # self.groups = {
            # 'top': re.search('([0-9,]*?),c', data).groups()[0].split(','),
            # 'bottom': re.search('([0-9,]*?),s', data).groups()[0].split(',')
            # }
        # ##############
        # #self.projektBRD = re.sub(r'(.*)\((.*)\)', r'\1[\2]', self.projektBRD)
        
    def setUnit(self, value):
        '''Get unit from transferred value and convert to millimeters - if necessary
           Possible value units:
            -   millimeters -> 1.0mm
            -   mils        -> 1.0mil
            -   inches      -> 1.0'''
        data = re.search(r'(.[^a-z]*)(.*)', value).groups()
        
        if data[1] == 'mm':
            multiplier = 1.0
        elif data[1] == 'mil':
            multiplier = 0.0254
        else:
            if self.globalUnit:
                multiplier = 0.0254
            else:
                multiplier = 0.0254 / 100.
            
        #return float(data[0]) * multiplier
        return float("%.3f" % (float(data[0]) * multiplier))
        
    def getNormalAnnotations(self):
        adnotacje = []
        #
        data= re.findall(r'Layer\([0-9]*\s+"(.+?)\s+.+?\)\[stop\]\[start\](.+?)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL)
        for i in data:
            for j in re.findall(r'Text\s*\[(.+?) (.+?) ([0-9]+) ([0-9]+) "(.+?)" (.+?)\]', i[1]):
                side = "TOP"
                rot = int(j[2]) * 90
                if "bottom" in i[0].lower():
                    side = "BOTTOM"
                    rot += 180
                
                adnotacje.append({
                    "text": str(j[4]),
                    "x": self.setUnit(j[0]),
                    "y": 0 - self.setUnit(j[1]),
                    "z": 0,
                    "size": (float(j[3]) * 1.016) / 100, # 1.016 == 40mils (default size)
                    "rot": rot,
                    "side": side,
                    "align": "top-left",
                    "spin": True,
                    "font": "Fixed",
                    "display": True,
                    "distance": 1,
                    "tracking": 0,
                    "mode": 'anno'
                })
        #
        return adnotacje

    #def getAnnotations(self, dane1, mode='anno'):
        # annotations = []
        # #
        # for i in re.findall(r'Text\s*\[(.+?) (.+?) ([0-9]+) ([0-9]+) "(.+?)" (.+?)\]', self.projektBRD):
            # x = self.setUnit(i[0])
            # y = 0 - self.setUnit(i[1])
            # #txt = str(i[4])[1:-1]
            # txt = str(i[4])
            # align = 'top-left'
            # size = (float(i[3]) * 40 * 0.0254) / 100
            # spin = False
            # mirror = 0
            # font = 'proportional'
            # side = 'TOP'
            
            # if int(i[2]) == 0:
                # rot = 0
            # elif int(i[2]) == 1:
                # rot = 90
            # elif int(i[2]) == 2:
                # rot = 180
            # else:
                # rot = 270

            # annotations.append([txt, x, y, size, rot, side, align, spin, mirror, font])
        # #
        # return annotations
    
    def getParts(self):
        self.getElements()
        parts = []
        #
        for k in self.elements:
            for i in re.findall(r'Attribute\("(.*?)" "(.*?)"\)', k['dataElement'], re.MULTILINE|re.DOTALL):
                if i[0] == 'FREECAD': # use different 3D model for current package
                    if i[1].strip() == "":
                        FreeCAD.Console.PrintWarning(u"Empty attribute 'FREECAD' found for the element {0}. Default package will be used.\n".format(k["name"]))
                    else:
                        FreeCAD.Console.PrintWarning(u"Package '{1}' will be used for the element {0} (instead of {2}).\n".format(k["name"], i[1].strip(), k['package']))
                        k['package'] = i[1].strip()
                        #if not self.parent.partExist(['', attr.getAttribute('value').strip()], '')[0]:
                        #    FreeCAD.Console.PrintWarning(u"\tIncorrect package '{1}' set for the element {0}.\n".format(i["name"], attr.getAttribute('value').strip()))
                        
                        #if self.parent.partExist(['', attr.getAttribute('value').strip()], '')[0]:
                            # FreeCAD.Console.PrintWarning(u"Package '{1}' will be used for the element {0} (instead of {2}).\n".format(i["name"], attr.getAttribute('value').strip(), i['package']))
                            # package = attr.getAttribute('value').strip()
                        # else:
                            # FreeCAD.Console.PrintWarning(u"Incorrect package '{1}' set for the element {0}. Default package will be used.\n".format(i["name"], attr.getAttribute('value').strip()))
                elif i[0] == 'VALUE':
                    if not i[1].strip() == "":
                        k['value'] = i[1].strip()
                        
                        k['EL_Value'] = {
                            "text": "VALUE",
                            "x": k['txtX'] + k['x'] + 0.5,
                            "y": -k['txtY'] + k['y'] + 0.5,
                            "z": 0,
                            "size": k['txtSize'],
                            "rot": k['rot'],
                            "side": k['side'],
                            "align": "bottom-center",
                            "spin": True,
                            "font": "Fixed",
                            "display": True,
                            "distance": 1,
                            "tracking": 0,
                            "mode": 'param'
                        }
            ####################################
            k['EL_Name'] = {
                "text": "NAME",
                "x": k['txtX'] + k['x'] - 0.5,
                "y": k['txtY'] + k['y'] - 0.5,
                "z": 0,
                "size": k['txtSize'],
                "rot": k['rot'],
                "side": k['side'],
                "align": "top-left",
                "spin": True,
                "font": "Fixed",
                "display": True,
                "distance": 1,
                "tracking": 0,
                "mode": 'param'
            }
            ####################################
            parts.append(k)
        #
        return parts
    
    def getHoles(self, holesObject, types, Hmin, Hmax):
        ''' holes/vias '''
        if types['IH']:  # detecting collisions between holes - intersections
            holesList = []

        # holes
        if types['H']:
            for i in self.getAllVias():
                if not "hole" in i["sflags"]:
                    continue
                
                r = i["drill"] / 2. + 0.001
                
                if filterHoles(r, Hmin, Hmax):
                    if types['IH']:  # detecting collisions between holes - intersections
                        add = True
                        try:
                            for k in holesList:
                                d = sqrt( (i["x"] - k[0]) ** 2 + (i["y"] - k[1]) ** 2)
                                if(d < r + k[2]):
                                    add = False
                                    break
                        except Exception as e:
                            FreeCAD.Console.PrintWarning("1. {0}\n".format(e))
                        
                        if (add):
                            holesList.append([i["x"], i["y"], r])
                            holesObject.addGeometry(Part.Circle(FreeCAD.Vector(i["x"], i["y"], 0.), FreeCAD.Vector(0, 0, 1), r))
                        else:
                            FreeCAD.Console.PrintWarning("Intersection between holes detected. Hole x={:.2f}, y={:.2f} will be omitted.\n".format(i["x"], i["y"]))
                    else:
                        holesObject.addGeometry(Part.Circle(FreeCAD.Vector(i["x"], i["y"], 0.), FreeCAD.Vector(0, 0, 1), r))

        # vias
        if types['V']:
            for i in self.getAllVias():
                if not i["through"] or "hole" in i["sflags"]:
                    continue
                
                r = i["drill"] / 2. + 0.001
                
                if filterHoles(r, Hmin, Hmax):
                    if types['IH']:  # detecting collisions between holes - intersections
                        add = True
                        try:
                            for k in holesList:
                                d = sqrt( (i["x"] - k[0]) ** 2 + (i["y"] - k[1]) ** 2)
                                if(d < r + k[2]):
                                    add = False
                                    break
                        except Exception as e:
                            FreeCAD.Console.PrintWarning("1. {0}\n".format(e))
                        
                        if (add):
                            holesList.append([i["x"], i["y"], r])
                            holesObject.addGeometry(Part.Circle(FreeCAD.Vector(i["x"], i["y"], 0.), FreeCAD.Vector(0, 0, 1), r))
                        else:
                            FreeCAD.Console.PrintWarning("Intersection between holes detected. Hole x={:.2f}, y={:.2f} will be omitted.\n".format(i["x"], i["y"]))
                    else:
                        holesObject.addGeometry(Part.Circle(FreeCAD.Vector(i["x"], i["y"], 0.), FreeCAD.Vector(0, 0, 1), r))
        # pads
        if types['P'] or types['H']:
            self.getElements()
            for j in self.elements:
                X1 = j["x"]
                Y1 = j["y"]
                
                if types['P']:  # pins
                    for i in self.getAllPins(j["dataElement"]):
                        if "hole" in i["sflags"]:
                            continue
                        
                        r = i["drill"] / 2. + 0.001
                        x = i["x"] + X1
                        y = i["y"] + Y1
                        
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
                if types['H']:
                    for i in self.getAllPins(j["dataElement"]):
                        if not "hole" in i["sflags"]:
                            continue
                        
                        r = i["drill"] / 2. + 0.001
                        x = i["x"] + X1
                        y = i["y"] + Y1
                        
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

    def getPCB(self, borderObject):
        # checking if there is a layer "outline" (prio layer as PCB aoutline)
        data = re.findall(r'Layer\([0-9]*\s+"outline"\s+.+?\)\[stop\]\[start\](.+?)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL)
        if len(data) and data[0]!= '(\n)':
            for i in re.findall('Line\s*\[(.+?) (.+?) (.+?) (.+?) (.+?) .+? .+?\]', data[0]):
                x1 = self.setUnit(i[0])
                y1 = 0 - self.setUnit(i[1])
                x2 = self.setUnit(i[2])
                y2 = 0 - self.setUnit(i[3])
                #
                if [x1, y1] != [x2, y2]:
                    borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x2, y2, 0)))
            for i in re.findall('Arc\s*\[(.+?) (.+?) (.+?) (.+?) (.+?) .+? (.+?) (.+?) .+?\]', data[0]):
                if float(i[5]) == 360 and display[1]: # circle
                    xs = self.setUnit(i[0])
                    ys = 0 - self.setUnit(i[1])
                    r = self.setUnit(i[2])
                    #
                    borderObject.addGeometry(Part.Circle(FreeCAD.Vector(xs, ys), FreeCAD.Vector(0, 0, 1), r))
                else:
                    (x1, y1, x2, y2, curve, width) = self.getArcParameters(i)
                    #
                    [x3, y3] = self.arcMidPoint([x1, y1], [x2, y2],curve)
                    arc = Part.ArcOfCircle(FreeCAD.Vector(x1, y1, 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(x2, y2, 0.0))
                    borderObject.addGeometry(arc)
        else:
            pcbSize = re.search('PCB\s*\[.+? (.+?) (.+?)\]', self.projektBRD).groups()
            self.width = self.setUnit(pcbSize[0])
            self.height = self.setUnit(pcbSize[1]) * (-1)
            
            borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(0, 0, 0), FreeCAD.Vector(self.width, 0, 0)))
            borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(self.width, 0, 0), FreeCAD.Vector(self.width, self.height, 0)))
            borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(self.width, self.height, 0), FreeCAD.Vector(0, self.height, 0)))
            borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(0, self.height, 0), FreeCAD.Vector(0, 0, 0)))

    def getPads(self, layerNew, layerNumber, layerSide):
        # via
        for i in self.getAllVias():
            if "hole" in i["sflags"]:
                continue
            
            layerNew.addCircle(i["x"], i["y"], i["thickness"] / 2.)
            layerNew.setFace()
        #
        self.getElements()
        for j in self.elements:
            X1 = j["x"]
            Y1 = j["y"]
            
            # pins
            for i in self.getAllPins(j["dataElement"]):
                if "hole" in i["sflags"]:
                    continue
                
                if "square" in i["sflags"]:
                    a = i["thickness"] / 2.
                    x1 = i["x"] + X1 - a
                    y1 = i["y"] + Y1 - a
                    x2 = i["x"] + X1 + a
                    y2 = i["y"] + Y1 + a
                    
                    layerNew.addRectangle(x1, y1, x2, y2)
                    layerNew.setFace()
                else: # circle
                    r = i["thickness"] / 2.
                    x = i["x"] + X1
                    y = i["y"] + Y1
                    
                    layerNew.addCircle(x, y, r)
                    layerNew.setFace()
            # pads
            if j['side'] == "BOTTOM" and "B" in layerNumber[0] or j['side'] == "TOP" and "T" in layerNumber[0]:
                for i in self.getAllPads(j["dataElement"]):
                    a = i["thickness"] / 2.
                    
                    if i["x1"] != i["x2"]:
                        x1 = X1 + i["x1"] - a
                        y1 = Y1 + i["y1"] - a
                        x2 = X1 + i["x2"] + a
                        y2 = Y1 + i["y2"] + a

                    else:
                        x1 = X1 + i["x1"] + a
                        y1 = Y1 + i["y1"] + a
                        x2 = X1 + i["x2"] - a
                        y2 = Y1 + i["y2"] - a
                    
                    if "square" in i["sflags"]:
                        layerNew.addRectangle(x1, y1, x2, y2)
                        layerNew.setFace()
                    else: # long pad
                        xs = x1 - (x1 - x2) / 2.
                        ys = y1 - (y1 - y2) / 2.
                        dx = abs((x1 - x2) / 2.)
                        dy = abs((y1 - y2) / 2.)
                        
                        layerNew.addPadLong(xs, ys, dx, dy, 100)
                        layerNew.setFace()

    def getElementArcParameters(self, arc):
        return self.getArcParameters([arc[0], arc[1], arc[2], arc[3], arc[6], arc[4], arc[5]])
        
    def getArcParameters(self, arc):
        xs = self.setUnit(arc[0])
        ys = 0 - self.setUnit(arc[1])
        r = self.setUnit(arc[2])
        #height = self.setUnit(arc[3])
        width = self.setUnit(arc[4])
        startAngle = radians(float(arc[5]) + 180)
        stopAngle = startAngle + radians(float(arc[6]))
        
        if startAngle > stopAngle:
            p = stopAngle
            stopAngle = startAngle
            startAngle = p
        
        startAngle = degrees(startAngle)
        stopAngle = degrees(stopAngle)
        
        x1 = xs + r
        y1 = ys
        
        [x1, y1] = self.obrocPunkt2([x1, y1], [xs, ys], startAngle)
        [x2, y2] = self.obrocPunkt2([x1, y1], [xs, ys], stopAngle - startAngle)
        
        return (x1, y1, x2, y2, stopAngle - startAngle, width)

    def getAllPads(self, baseData):
        data = []
        # Pad [rX1 rY1 rX2 rY2 Thickness Clearance Mask "Name" "Number" SFlags]
        for i in re.findall(r'Pad\s*\[([\w.-]+)\s+([\w.-]+)\s+([\w.-]+)\s+([\w.-]+)\s+([\w.-]+)\s+([\w.-]+)\s+([\w.-\\,\\"]+)\s+([\w.-\\,\\"]+)\s+([\w.-\\,\\"]+)\s+([\w.-\\,\\"]+)', baseData):
            data.append({
                "x1": self.setUnit(i[0]),
                "y1": 0 - self.setUnit(i[1]),
                "x2": self.setUnit(i[2]),
                "y2": 0 - self.setUnit(i[3]),
                "thickness": self.setUnit(i[4]),
                "clearance": self.setUnit(i[5]),
                "mask": self.setUnit(i[6]),
                "sflags": i[9]
            })
        
        return data
    
    def getAllPins(self, baseData):
        data = []
        # Pin [rX rY Thickness Clearance Mask Drill "Name" "Number" SFlags]
        for i in re.findall(r'Pin\s*\[([\w.-]+)\s+([\w.-]+)\s+([\w.-]+)\s+([\w.-]+)\s+([\w.-]+)\s+([\w.-]+)\s+([\w.-\\,\\"]+)\s+([\w.-\\,\\"]+)\s+([\w.-\\,\\"]+)', baseData):
            data.append({
                "x": self.setUnit(i[0]),
                "y": 0 - self.setUnit(i[1]),
                "thickness": self.setUnit(i[2]),
                "clearance": self.setUnit(i[3]),
                "mask": self.setUnit(i[4]),
                "drill": self.setUnit(i[5]),
                "sflags": i[8]
            })
        
        return data
    
    def getAllVias(self):
        data = []
        # Via [X Y Thickness Clearance Mask Drill BuriedFrom BuriedTo "Name" SFlags]
        # Via [X Y Thickness Clearance Mask Drill "Name" SFlags]
        for i in re.findall(r'Via\s*\[([\w.]+)\s+([\w.]+)\s+([\w.]+)\s+([\w.]+)\s+([\w.]+)\s+([\w.]+)(\s+[\w.]+|)(\s+[\w.]+|)(\s+[\w."]+|)(\s+[\w."]+|)', self.projektBRD):
            through = True

            if i[6].strip() != "":
                through = False
            
            data.append({
                "x": self.setUnit(i[0]),
                "y": 0 - self.setUnit(i[1]),
                "thickness": self.setUnit(i[2]),
                "clearance": self.setUnit(i[3]),
                "mask": self.setUnit(i[4]),
                "drill": self.setUnit(i[5]),
                "through": through,
                "sflags": i[9]
            })
        
        return data

    def getElements(self):
        # Element [SFlags "Desc" "Name" "Value" MX MY TX TY TDir TScale TSFlags] 
        if len(self.elements) == 0:
            for i in re.findall(r'Element(.+?)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL):
                data = re.search(r'^\["(.*?)"\s+"(.*?)"\s+"(.*?)"\s+"(.*?)"\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+(.+?)\s+"(.*?)"\]', i).groups()
                
                locked = False
                if "lock" in data[0] or "lock" in data[10]:
                    locked = True
                
                side = "TOP"
                if "onsolder" in data[0] or "onsolder" in data[10]:
                    side = "BOTTOM"
                
                self.elements.append({
                    'name': data[2], 
                    'library': "", 
                    'package': data[3], 
                    'value': '', 
                    'x': self.setUnit(data[4]), 
                    'y': 0 - self.setUnit(data[5]), 
                    'locked': locked,
                    'populated': False, 
                    'smashed': False, 
                    'rot': int(data[8]) * 90, 
                    'side': side,
                    'dataElement': i,
                    'txtX': self.setUnit(data[6]), 
                    'txtY': 0 - self.setUnit(data[7]),
                    'txtSize': (float(data[9]) * 1.016) / 100, # 1.016 == 40mils (default size)
                })

    def addStandardShapes(self, dane, layerNew, layerNumber, display=[True, True, True, True], parent=None):
        # linie
        if display[0]:
            if parent == None:
                # Line [X1 Y1 X2 Y2 Thickness Clearance SFlags]
                for i in re.findall('Line\s*\[(.+?) (.+?) (.+?) (.+?) (.+?) .+? .+?\]', dane):
                    x1 = self.setUnit(i[0])
                    y1 = 0 - self.setUnit(i[1])
                    x2 = self.setUnit(i[2])
                    y2 = 0 - self.setUnit(i[3])
                    width = self.setUnit(i[4])
                    #
                    layerNew.addLineWidth(x1, y1, x2, y2, width)
                    layerNew.setFace()
                # Arc [X Y RadiusX RadiusY Thickness Clearance StartAngle DeltaAngle SFlags]
                for i in re.findall('Arc\s*\[(.+?) (.+?) (.+?) (.+?) (.+?) .+? (.+?) (.+?) .+?\]', dane):
                    if float(i[5]) == 360 and display[1]: # circle
                        xs = self.setUnit(i[0])
                        ys = 0 - self.setUnit(i[1])
                        r = self.setUnit(i[2])
                        width = self.setUnit(i[4])
                        #
                        layerNew.addCircle(xs, ys, r, width)
                        layerNew.setFace()
                        if i['width'] > 0:
                            layerNew.circleCutHole(xs, ys, r - width / 2.)
                    else:
                        (x1, y1, x2, y2, curve, width) = self.getArcParameters(i)
                        #
                        layerNew.addArcWidth([x1, y1], [x2, y2], curve, width)
                        layerNew.setFace()
            else:
                # ElementLine [X1 Y1 X2 Y2 Thickness]
                for i in re.findall('ElementLine \s*\[(.+?) (.+?) (.+?) (.+?) (.+?)\]', dane):
                    x1 = self.setUnit(i[0]) + parent['x']
                    y1 = 0 - self.setUnit(i[1]) + parent['y']
                    x2 = self.setUnit(i[2]) + parent['x']
                    y2 = 0 - self.setUnit(i[3]) + parent['y']
                    width = self.setUnit(i[4])
                    #
                    layerNew.addLineWidth(x1, y1, x2, y2, width)
                    layerNew.setFace()
                # ElementArc [X Y Width Height StartAngle DeltaAngle Thickness]
                for i in re.findall('ElementArc\s*\[(.+?) (.+?) (.+?) (.+?) (.+?) (.+?) (.+?)\]', dane):
                    if float(i[5]) == 360 and display[1]: # circle
                        xs = self.setUnit(i[0]) + parent['x']
                        ys = 0 - self.setUnit(i[1]) + parent['y']
                        r = self.setUnit(i[2])
                        width = self.setUnit(i[6])
                        #
                        layerNew.addCircle(xs, ys, r, width)
                        layerNew.setFace()
                        if i['width'] > 0:
                            layerNew.circleCutHole(xs, ys, r - width / 2.)
                    else:
                        (x1, y1, x2, y2, curve, width) = self.getElementArcParameters(i)
                        #
                        layerNew.addArcWidth([x1 + parent['x'], y1 + parent['y']], [x2 + parent['x'], y2 + parent['y']], curve, width)
                        layerNew.setFace()
        ## polygon
        if display[3]:
            if parent == None:
                for i in re.findall('Polygon\s*\(.+?\)\n\t\(\n.(.+?)\n\t\)\n', dane, re.DOTALL|re.MULTILINE):
                    poin = []
            
                    punkty = i.strip().split("]")
                    punkty = punkty[:-1]
                    for j in range(len(punkty)):
                        x1 = self.setUnit(re.search('\[(.+?) (.*)', punkty[j]).groups()[0])
                        y1 = 0 - self.setUnit(re.search('\[(.+?) (.*)', punkty[j]).groups()[1])
                        
                        if j == len(punkty) - 1:
                            x2 = self.setUnit(re.search('\[(.+?) (.*)', punkty[0]).groups()[0])
                            y2 = 0 - self.setUnit(re.search('\[(.+?) (.*)', punkty[0]).groups()[1])
                        else:
                            x2 = self.setUnit(re.search('\[(.+?) (.*)', punkty[j + 1]).groups()[0])
                            y2 = 0 - self.setUnit(re.search('\[(.+?) (.*)', punkty[j + 1]).groups()[1])
                        
                        if not [x1, y1] == [x2, y2]:  # remove points, only lines
                            poin.append(['Line', x1, y1, x2, y2])
                    #
                    layerNew.addPolygon(poin)
                    layerNew.setFace()
            else:
                pass

    def getSilkLayer(self, layerNew, layerNumber, display=[True, True, True, True]):
        try:
            layerNumber = int(layerNumber[0].split("_")[1])
            #
            data = re.findall(r'Layer\(' + str(layerNumber) + '\s+.+?\s+.+?\)\[stop\]\[start\](.+?)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL)[0]
            self.addStandardShapes(data, layerNew, [layerNumber], display)
        except:
            pass
        
    def getSilkLayerModels(self, layerNew, layerNumber):
        try:
            self.getElements()
            layerNumberN = int(layerNumber[0].split("_")[1])
            
            for i in self.elements:
                if i['side'] == "BOTTOM" and "B" in layerNumber[0]:
                    self.addStandardShapes(i['dataElement'], layerNew, [layerNumberN], parent=i)
                elif i['side'] == "TOP" and "T" in layerNumber[0]:
                    self.addStandardShapes(i['dataElement'], layerNew, [layerNumberN], parent=i)
        except:
            pass
    
    def getPaths(self, layerNew, layerNumber, display=[True, True, True, True]):
        pass

    def defineFunction(self, layerNumber):
        if "pad" in layerNumber.lower():  # pady
            return "pads"
        elif "copper" in layerNumber.lower():  # paths
            return "paths"
        elif "anno" in layerNumber.lower():
            return "annotations"
        else:  # 10
            return "silk"

