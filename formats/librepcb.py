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
try:
    import builtins
except:
    import __builtin__ as builtins
import re
from math import radians
from PySide import QtCore, QtGui
#
from PCBconf import softLayers
from PCBobjects import *
from formats.dialogMAIN_FORM import dialogMAIN_FORM
from formats.baseModel import baseModel


class dialogMAIN(dialogMAIN_FORM):
    def __init__(self, filename=None, parent=None):
        dialogMAIN_FORM.__init__(self, parent)
        self.databaseType = "librepcb"
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
        # extra layers
        dane["top_cu"] = {"name": softLayers[self.databaseType]["top_cu"]["description"], "color": softLayers[self.databaseType]["top_cu"]["color"]}
        dane["bot_cu"] = {"name": softLayers[self.databaseType]["bot_cu"]["description"], "color": softLayers[self.databaseType]["bot_cu"]["color"]}
        dane["top_pad"] = {"name": softLayers[self.databaseType]["top_pad"]["description"], "color": softLayers[self.databaseType]["top_pad"]["color"]}
        dane["bot_pad"] = {"name": softLayers[self.databaseType]["bot_pad"]["description"], "color": softLayers[self.databaseType]["bot_pad"]["color"]}
        dane["top_documentation"] = {"name": softLayers[self.databaseType]["top_documentation"]["description"], "color": softLayers[self.databaseType]["top_documentation"]["color"]}
        dane["bot_documentation"] = {"name": softLayers[self.databaseType]["bot_documentation"]["description"], "color": softLayers[self.databaseType]["bot_documentation"]["color"]}
        dane["top_placement"] = {"name": softLayers[self.databaseType]["top_placement"]["description"], "color": softLayers[self.databaseType]["top_placement"]["color"]}
        dane["bot_placement"] = {"name": softLayers[self.databaseType]["bot_placement"]["description"], "color": softLayers[self.databaseType]["bot_placement"]["color"]}
        dane["anno"] = {"name": softLayers[self.databaseType]["anno"]["description"], "color": softLayers[self.databaseType]["anno"]["color"]}
        dane["top_glue"] = {"name": softLayers[self.databaseType]["top_glue"]["description"], "color": softLayers[self.databaseType]["top_glue"]["color"]}
        dane["bot_glue"] = {"name": softLayers[self.databaseType]["bot_glue"]["description"], "color": softLayers[self.databaseType]["bot_glue"]["color"]}
        #
        return dane


class modelTypes(QtGui.QDialog):
    def __init__(self, paths, parent=None):
        QtGui.QDialog.__init__(self, parent)

        self.setWindowTitle(u'Choose board')
        #
        self.modelsList = QtGui.QListWidget()
        self.pathsData = {}
        for i in paths:
            data = i.split("/")
            self.pathsData[data[-2]] = i
            
            self.modelsList.addItem(data[-2])
        #
        self.modelsList.setCurrentRow(0)
        #
        buttons = QtGui.QDialogButtonBox()
        buttons.setOrientation(QtCore.Qt.Vertical)
        buttons.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
        buttons.addButton("Choose", QtGui.QDialogButtonBox.AcceptRole)
        self.connect(buttons, QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        self.connect(buttons, QtCore.SIGNAL("rejected()"), self, QtCore.SLOT("reject()"))
        #
        lay = QtGui.QGridLayout(self)
        lay.addWidget(QtGui.QLabel(u"Choose which PCB board you want to import"), 0, 0, 1, 1)
        lay.addWidget(self.modelsList, 2, 0, 1, 1)
        lay.addWidget(buttons, 2, 1, 1, 1)


class LibrePCB(baseModel):
    def __init__(self, filename, parent):
        #
        boardData = builtins.open(os.path.join(os.path.dirname(filename), "boards/boards.lp")).read()
        self.projectPath = os.path.dirname(filename)
        #
        boards = re.findall(r'\(board "(.+?)"\)', boardData)
        if len(boards) == 1:
            boardData = boards[0]
        else:
            dial = modelTypes(boards)
            
            if dial.exec_():
                boardData = dial.pathsData[dial.modelsList.currentItem().text()]
            else:
                FreeCAD.Console.PrintWarning("Default board will be loaded\n")
                boardData = boards[0]
        
        self.fileName = os.path.join(os.path.dirname(filename), boardData)
        #
        self.dialogMAIN = dialogMAIN(self.fileName)
        self.databaseType = "librepcb"
        self.parent = parent
        self.netsegments = {}
        self.libraries = {}
        self.elements = {}
    
    def setProject(self):
        '''Load project from file'''
        self.projektBRD = self.setProjectFile(self.fileName)
        self.getNetsegments()

    def getNormalAnnotations(self):
        return self.getAnnotations(self.projektBRD, mode='anno')
        
    def getAnnotations(self, dane1, mode='anno'):
        adnotacje = []
        #
        for i in re.findall(r'\[start\]\(stroke_text(.+?)\[stop\]', dane1, re.MULTILINE|re.DOTALL):
            [x, y] = re.search(r'\(position\s+(.+?)\s+(.+?)\)', i).groups()
            rot = float(re.search(r'\(rotation\s+(.+?)\)', i).groups()[0])
            text = re.search(r'\(value\s+"(.+?)"\)', i).groups()[0].replace('\\n', '\n')
            size = float(re.search(r'\(height\s+(.+?)\)', i).groups()[0])
            #
            align = re.search(r'\(align\s+(.+?)\)', i).groups()[0].strip().split(" ")
            if align[0] == align[1]:
                align = align[0]
            else:
                align = align[1] + "-" + align[0]
            #
            spin = re.search(r'\(auto_rotate\s+(.+?)\)', i).groups()[0]
            if spin == "false":
                spin = True
            else:
                spin = False
            #
            if re.search(r'\(mirror\s+(.+?)\)', i).groups()[0] == "false":
                side = "TOP"
            else:
                side = "BOTTOM"
            #
            distance = re.search(r'\(line_spacing\s+(.+?)\)', i).groups()[0].strip()
            if distance == "auto":
                distance = 1
            else:
                distance = int(float(distance) * 100 - 100)
            #
            tracking = re.search(r'\(letter_spacing\s+(.+?)\)', i).groups()[0].strip()
            if tracking == "auto":
                tracking= 0
            else:
                tracking = size * float(tracking)
            #
            adnotacje.append({
                "text": text,
                "x": float(x),
                "y": float(y),
                "z": 0,
                "size": size,
                "rot": rot,
                "side": side,
                "align": align,
                "spin": spin,
                "font": "Fixed",
                "display": True,
                "distance": distance,
                "tracking": tracking,
                "mode": mode
            })
        #
        return adnotacje

    def getParts(self):
        self.getElements()
        parts = []
        #
        try:
            for k in self.elements.keys():
                elem = self.elements[k]
                elemData = self.setProjectFile(elem["data"], loadFromFile=False)
                ####################################
                if elem["freecadPackage"]:
                    FreeCAD.Console.PrintWarning(u"Package '{1}' will be used for the element {0} (instead of {2}).\n".format(elem["name"], elem["freecadPackage"], elem["package"]))
                    elem["package"] = elem["freecadPackage"]
                ####################################
                for j in self.getAnnotations(elemData, 'param'):
                    if "{{NAME}}" in j["text"]:
                        j["text"] = 'NAME'
                        elem['EL_Name'] = j
                    elif "{{VALUE}}" in j["text"]:
                        j["text"] = 'VALUE'
                        elem["EL_Value"] = j
                #
                parts.append(elem)
        except Exception as e:
            print(e)
        #
        return parts
        
    def getHoles(self, holesObject, types, Hmin, Hmax):
        if types['IH']:  # detecting collisions between holes - intersections
            holesList = []
        #
        # holes
        if types['H']:
            for i in re.findall(r'\(hole\s+.+?\s+\(diameter\s+(.+?)\)\s+\(position\s+(.+?)\s+(.+?)\)\)', self.projektBRD):
                x = float(i[1])
                y = float(i[2])
                r = float(i[0]) / 2. + 0.001
                
                if self.filterHoles(r, Hmin, Hmax):
                    if types['IH']:  # detecting collisions between holes - intersections
                        if self.detectIntersectingHoles(holesList, x, y, r):
                            holesList.append([x, y, r])
                            holesObject.addGeometry(Part.Circle(FreeCAD.Vector(x, y, 0.), FreeCAD.Vector(0, 0, 1), r))
                    else:
                        holesObject.addGeometry(Part.Circle(FreeCAD.Vector(x, y, 0.), FreeCAD.Vector(0, 0, 1), r))
        # vias
        if types['V']:
            self.getNetsegments()
            
            for i in self.netsegments.keys():
                for j in self.netsegments[i]["via"].keys():
                    x = self.netsegments[i]["via"][j]['x']
                    y = self.netsegments[i]["via"][j]['y']
                    r = self.netsegments[i]["via"][j]['drill'] / 2. + 0.001
                    
                    if self.filterHoles(r, Hmin, Hmax):
                        if types['IH']:  # detecting collisions between holes - intersections
                            if self.detectIntersectingHoles(holesList, x, y, r):
                                holesList.append([x, y, r])
                                holesObject.addGeometry(Part.Circle(FreeCAD.Vector(x, y, 0.), FreeCAD.Vector(0, 0, 1), r))
                        else:
                            holesObject.addGeometry(Part.Circle(FreeCAD.Vector(x, y, 0.), FreeCAD.Vector(0, 0, 1), r))
        ## pady
        self.getElements()

        try:
            for i in self.elements.keys():
                X = self.elements[i]["x"]
                Y = self.elements[i]["y"]
                ROT = self.elements[i]["rot"]
                #
                packageID = self.elements[i]["packageID"]
                footprintID = self.elements[i]["footprintID"]
                
                if packageID in self.libraries.keys() and footprintID in self.libraries[packageID]['footprints'].keys():
                    footprint = self.libraries[packageID]['footprints'][footprintID]
                    if types['P']:  # pads
                        for j in re.findall(r'\(pad\s+.+?\(side\s+tht\).+?\(position\s+(.+?)\s+(.+?)\).+?\(drill\s+(.+?)\)', footprint, re.MULTILINE|re.DOTALL):
                            [xs, ys, drill]= j
                           
                            xs = float(xs)
                            ys = float(ys)
                            drill = float(drill) / 2. + 0.001
                            
                            [xR, yR] = self.obrocPunkt([xs, ys], [X, Y], ROT)
                            
                            if self.elements[i]['side'] == "BOTTOM":  # odbicie wspolrzednych
                                xR = self.odbijWspolrzedne(xR, X)
                            
                            if self.filterHoles(drill, Hmin, Hmax):
                                if types['IH']:  # detecting collisions between holes - intersections
                                    if self.detectIntersectingHoles(holesList, xR, yR, drill):
                                        holesList.append([xR, yR, drill])
                                        holesObject.addGeometry(Part.Circle(FreeCAD.Vector(xR, yR, 0.), FreeCAD.Vector(0, 0, 1), drill))
                                else:
                                    holesObject.addGeometry(Part.Circle(FreeCAD.Vector(xR, yR, 0.), FreeCAD.Vector(0, 0, 1), drill))
                    if types['H']:  # holes
                        for j in re.findall(r'\(hole\s+.+?\s+\(diameter\s+(.+?)\)\s+\(position\s+(.+?)\s+(.+?)\)\)', footprint):
                            x = float(j[1])
                            y = float(j[2])
                            r = float(j[0]) / 2. + 0.001
                            
                            [x, y] = self.obrocPunkt([x, y], [X, Y], ROT)
                            
                            if self.elements[i]['side'] == "BOTTOM":  # odbicie wspolrzednych
                                x = self.odbijWspolrzedne(x, X)
                            
                            if self.filterHoles(r, Hmin, Hmax):
                                if types['IH']:  # detecting collisions between holes - intersections
                                    if self.detectIntersectingHoles(holesList, x, y, r):
                                        holesList.append([x, y, r])
                                        holesObject.addGeometry(Part.Circle(FreeCAD.Vector(x, y, 0.), FreeCAD.Vector(0, 0, 1), r))
                                else:
                                    holesObject.addGeometry(Part.Circle(FreeCAD.Vector(x, y, 0.), FreeCAD.Vector(0, 0, 1), r))
        except Exception as e:
            print(e)
        
    def getPCB(self, borderObject):
        for i in re.findall(r'\[start\]\(polygon.[\s+a-zA-Z0-9\-]*\(layer\s+brd_outlines\)\n(.+?)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL):
            data = re.findall(r'\(vertex\s+\(position\s+(.+?)\s+(.+?)\)\s+\(angle\s+(.+?)\)\)', i)
            if data[0] == data[1]:
                data.pop(0)
            if data[0] == data[-1]:
                data.pop(-1)
            
            for j in range(0, len(data)):
                x1 = float(data[j][0])
                y1 = float(data[j][1])
                angle = float(data[j][2])
                
                if j == len(data) - 1:
                    x2 = float(data[0][0])
                    y2 = float(data[0][1])
                else:
                    x2 = float(data[j + 1][0])
                    y2 = float(data[j + 1][1])
        
                if not float(angle) == 0.0:
                    [x3, y3] = self.arcMidPoint([x1, y1], [x2, y2], angle)
                    arc = Part.ArcOfCircle(FreeCAD.Vector(x1, y1, 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(x2, y2, 0.0))
                    borderObject.addGeometry(arc)
                else:
                    if [x1, y1] != [x2, y2]:
                         borderObject.addGeometry(Part.LineSegment(FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x2, y2, 0)))

    def getPads(self, layerNew, layerNumber, layerSide, tentedViasLimit, tentedVias):
        self.getNetsegments()
        self.getElements()
        
        # via
        for i in self.netsegments.keys():
            for j in self.netsegments[i]["via"].keys():
                x = self.netsegments[i]["via"][j]['x']
                y = self.netsegments[i]["via"][j]['y']
                diameter = self.netsegments[i]["via"][j]['size']
                shape = self.netsegments[i]["via"][j]['shape']
                
                ##### ##### ##### 
                ##### tented dVias
                if self.filterTentedVias(tentedViasLimit, tentedVias, diameter, False):
                    continue
                ##### ##### ##### 
                if shape == "octagon":
                    layerNew.addOctagon(x, y, diameter)
                    layerNew.setFace()
                elif shape == "square":
                    a = diameter / 2.
                    x1 = x - a
                    y1 = y - a
                    x2 = x + a
                    y2 = y + a
                    
                    layerNew.addRectangle(x1, y1, x2, y2)
                    layerNew.setFace()
                else: # round
                    layerNew.addCircle(x, y, diameter / 2.)
                    layerNew.setFace()
        
        if not tentedVias:
            # pads
            for i in self.elements.keys():
                X = self.elements[i]["x"]
                Y = self.elements[i]["y"]
                ROT = self.elements[i]["rot"]
                
                side = 1
                if self.elements[i]['side'] == "BOTTOM":
                    side = 0
                #
                packageID = self.elements[i]["packageID"]
                footprintID = self.elements[i]["footprintID"]
                
                if packageID in self.libraries.keys() and footprintID in self.libraries[packageID]['footprints'].keys():
                    footprint = self.libraries[packageID]['footprints'][footprintID]
                    #
                    for j in re.findall(r'\(pad\s+.+?\(side\s+(.+?)\).+?\(shape\s+(.+?)\).+?\(position\s+(.+?)\s+(.+?)\)\s+\(rotation\s+(.+?)\)\s+\(size\s+(.+?)\s+(.+?)\)', footprint, re.MULTILINE|re.DOTALL):
                        [padType, shape, xs, ys, rot, sW, sH]= j
                        
                        if not padType.strip() == "tht": # SMD PADS
                            if layerSide == 1:
                                if side == 0 and padType == "top":
                                    continue
                                elif side == 1 and padType == "bottom":
                                    continue
                            elif layerSide == 0:
                                if side == 1 and padType == "top":
                                    continue
                                elif side == 0 and padType == "bottom":
                                    continue
                        #
                        shape = shape.strip()
                        x = float(xs) + X
                        y = float(ys) + Y
                        rot = float(rot)
                        sW = float(sW)
                        sH = float(sH)
                        #
                        if shape == "round":
                            if sW == sH: # circle
                                layerNew.addCircle(x, y, sW / 2.)
                                layerNew.addRotation(X, Y, ROT)
                                layerNew.setChangeSide(X, Y, side)
                                layerNew.setFace()
                            else: # long
                                layerNew.addPadLong(x, y, sW / 2., sH / 2., 100)
                                layerNew.addRotation(x, y, rot)
                                layerNew.addRotation(X, Y, ROT)
                                layerNew.setChangeSide(X, Y, side)
                                layerNew.setFace()
                        elif shape == "rect":
                            x1 = x - sW / 2.
                            y1 = y - sH / 2.
                            x2 = x + sW / 2.
                            y2 = y + sH / 2.
                            
                            layerNew.addRectangle(x1, y1, x2, y2)
                            layerNew.addRotation(x, y, rot)
                            layerNew.addRotation(X, Y, ROT)
                            layerNew.setChangeSide(X, Y, side)
                            layerNew.setFace()

    def getNetsegments(self):
        if len(self.netsegments) == 0:
            for i in re.findall(r'\[start\]\(netsegment(.+?)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL):
                signal = re.search(r'\(net\s+(.+?)\)', i).groups()[0]
                
                if not signal in self.netsegments.keys():
                    self.netsegments[signal] = {}
                # via
                if not "via" in self.netsegments[signal].keys():
                    self.netsegments[signal]["via"] = {}
                
                for j in re.findall(r'\(via\s+(.+?)\(position\s+(.+?)\s+(.+?)\)\s+\(size\s+(.+?)\)\s+\(drill\s+(.+?)\)\s+\(shape\s+(.+?)\)', i, re.MULTILINE|re.DOTALL):
                    self.netsegments[signal]["via"][j[0].strip()] = {
                        "x": float(j[1]),
                        "y": float(j[2]),
                        "size": float(j[3]),
                        "drill": float(j[4]),
                        "shape": j[5].strip()
                    }
                # junction
                if not "junction" in self.netsegments[signal].keys():
                    self.netsegments[signal]["junction"] = {}
                    
                for j in re.findall(r'\(junction\s+(.+?)\s+\(position\s+(.+?)\s+(.+?)\)\)', i):
                    self.netsegments[signal]["junction"][j[0].strip()] = {
                        "x": float(j[1]),
                        "y": float(j[2]),
                    }
                # trace
                if not "trace" in self.netsegments[signal].keys():
                    self.netsegments[signal]["trace"] = {}
                
                for j in re.findall(r'\(trace\s+(.+?)\s+\(layer\s+(.+?)\)\s+\(width\s+(.+?)\).+?\(from\s+\(([junction|via|device]*)\s+(.+?)\)\)\n.+?\(to\s+\(([junction|via|device]*)\s+(.+?)\)\)', i, re.MULTILINE|re.DOTALL):
                    self.netsegments[signal]["trace"][j[0].strip()] = {
                        "layer": j[1].strip(),
                        "width": float(j[2]),
                        "fromType": j[3].strip(),
                        "from": j[4].strip(),
                        "toType": j[5].strip(),
                        "to": j[6].strip(),
                    }

    def getElements(self):
        try:
            if len(self.elements) == 0:
                packages = {}
                circuitFile = None
                
                for i in re.findall(r'\[start\]\(device\s+(.+?)\n(.+?)\)\[stop\]', self.projektBRD, re.MULTILINE|re.DOTALL):
                    device = i[0].strip()
                    
                    if not device in self.elements.keys():
                        self.elements[device] = {}
                    
                    [x, y] = re.search(r'\(position\s+(.+?)\s+(.+?)\)', i[1]).groups()
                    rot = re.search(r'\(rotation\s+(.+?)\)', i[1]).groups()[0]
                    
                    if re.search(r'\(mirror\s+(.+?)\)', i[1]).groups()[0] == "false":
                        side = "TOP"
                    else:
                        side = "BOTTOM"
                    # package
                    libDevice = re.search(r'\(lib_device\s+(.+?)\)', i[1]).groups()[0].strip()
                    if libDevice in packages.keys():
                        packageID = packages[libDevice]
                    else:
                        fileName = os.path.join(self.projectPath, "library/dev/" + libDevice + "/device.lp")
                        plibDevFile = builtins.open(fileName, "r").read()
                        #package = re.search(r'\(name\s+"(.+?)"\)', plibDevFile).groups()[0]
                        packageID = re.search(r'\(package\s+(.+?)\)', plibDevFile).groups()[0]
                        packages[libDevice] = packageID
                    
                    self.getLibraries(packages[libDevice])
                    package = self.libraries[packageID]["name"]
                    # footprint ID
                    footprintID = re.search(r'\(lib_footprint\s+(.+?)\)', i[1]).groups()[0]
                    # name/value
                    if not circuitFile:
                        fileName = os.path.join(self.projectPath, "circuit/circuit.lp")
                        circuitFile = self.setProjectFile(''.join(builtins.open(fileName, "r").readlines()[1:-2]), loadFromFile=False)
                    
                    component = re.search(r'\[start\]\(component\s+%s(.+?)\[stop\]' % device, circuitFile, re.MULTILINE|re.DOTALL).groups()[0]
                    [name, value]= re.search(r'\(name\s+"(.+?)"\)\s+\(value\s+"(.+?)"\)', component).groups()
                    if value.startswith("{{"):
                        value = " "
                    
                    freecadPackage = None
                    try:
                        freecadPackage = re.sub('[^a-zA-Z0-9 _\+\.\-]+', '', re.search(r'\(attribute\s+"FREECAD".+?\(value\s+"(.+?)"\)\)', component).groups()[0])
                    except:
                        pass
                    #
                    self.elements[device] = {
                        "x": float(x),
                        "y": float(y),
                        "rot": float(rot),
                        "side": side,
                        "package": package,
                        "packageID": packageID,
                        "footprintID": footprintID,
                        "name": name,
                        "value": value,
                        'locked': False,
                        'populated': False, 
                        'smashed': True,
                        'freecadPackage': freecadPackage,
                        "data": i[1]
                    }
        except Exception as e:
            print(e)
    
    def getLibraries(self, value):
        if not value in self.libraries.keys():
            self.libraries[value] = {}
            #
            fileName = os.path.join(self.projectPath, "library/pkg/" + value + "/package.lp")
            libraryFile = builtins.open(fileName, "r").read()
            #
            self.libraries[value]["name"] = re.sub('[^a-zA-Z0-9 _\+\.\-]+', '', re.search(r'\(name\s+"(.+?)"\)', libraryFile).groups()[0])
            # footprints
            self.libraries[value]["footprints"] = {}
            
            footprints = re.findall(r'(?<=footprint).*?(?=footprint|\Z)', libraryFile, re.MULTILINE|re.DOTALL)
            for i in footprints:
                footprintName = re.search(r'(.+?)\n', i).groups()[0].strip()
                self.libraries[value]["footprints"][footprintName] = i
    
    def getGlue(self, layerNumber):
        glue = {}
        #
        for i in re.findall(r'\[start\]\(polygon[\s+a-zA-Z0-9\-]*\(layer\s+%s\)(.+?)\[stop\]' % layerNumber[0], self.projektBRD, re.MULTILINE|re.DOTALL):
            skipLast = False
            [width, fill] = re.search(r'\(width\s+(.+?)\)\s+\(fill\s+(.+?)\)\s+\(', i).groups()
            
            width = float(width)
            if width == 0:
                width = 0.1
            
            if not width in glue.keys():
                glue[width] = []
            #
            data = re.findall(r'\(vertex\s+\(position\s+(.+?)\s+(.+?)\)\s+\(angle\s+(.+?)\)\)', i)
            if data[0] == data[1]:
                data.pop(0)
            
            if data[0] == data[-1]:
                data.pop(-1)
            else:
                skipLast = True
            
            for j in range(0, len(data)):
                if j == len(data) - 1 and skipLast:
                    break
                #
                x1 = float(data[j][0])
                y1 = float(data[j][1])
                angle = float(data[j][2])
                
                if j == len(data) - 1:
                    x2 = float(data[0][0])
                    y2 = float(data[0][1])
                else:
                    x2 = float(data[j + 1][0])
                    y2 = float(data[j + 1][1])
                #
                if not angle == 0.0:
                    glue[width].append(['arc', x2, y2, x1, y1, angle])
                else:
                    glue[width].append(['line', x1, y1, x2, y2])
        #
        return glue
    
    def getSilkLayer(self, layerNew, layerNumber, display=[True, True, True, True]):
        self.addStandardShapes(self.projektBRD, layerNew, layerNumber[0], [True, True, True, True])
        
    def getSilkLayerModels(self, layerNew, layerNumber):
        self.getElements()
        #
        for i in self.elements.keys():
            if self.elements[i]['side'] == "BOTTOM":  # bottom side - get mirror
                try:
                    szukanaWarstwa = softLayers[self.databaseType][layerNumber[0]]["mirrorLayer"]
                except:
                    continue
            else:
                szukanaWarstwa = layerNumber[0]
            
            #
            packageID = self.elements[i]["packageID"]
            footprintID = self.elements[i]["footprintID"]
            #
            if packageID in self.libraries.keys() and footprintID in self.libraries[packageID]['footprints'].keys():
                footprint = self.setProjectFile(self.libraries[packageID]['footprints'][footprintID], loadFromFile=False)
                #
                self.addStandardShapes(footprint, layerNew, szukanaWarstwa, parent=self.elements[i])
    
    def addStandardShapes(self, dane, layerNew, layerNumber, display=[True, True, True, True], parent=None, getSignals=False):
        if parent:
            X = parent['x']
            Y = parent['y']
            SIDE = 1
            if parent["side"] == "BOTTOM":
                SIDE = 0
        else:
            X = 0
            Y = 0
        
        # circle
        if display[1]:
            for i in re.findall(r'\[start\]\(circle[\s+a-zA-Z0-9\-]*\(layer\s+%s\)(.+?)\[stop\]' % layerNumber, dane, re.MULTILINE|re.DOTALL):
                [width, fill, r, x, y] = re.search(r'\(width\s+(.+?)\)\s+\(fill\s+(.+?)\)\s+.+?\s+\(diameter\s+(.+?)\)\s+\(position\s+(.+?)\s+(.+?)\)', i).groups()
                width = float(width)
                x = float(x) + X
                y = float(y) + Y
                r = float(r) / 2.
                
                layerNew.addCircle(x, y, r, width)
                if parent:
                    layerNew.addRotation(X, Y, parent['rot'])
                    layerNew.setChangeSide(X, Y, SIDE)
                layerNew.setFace()
                if fill == "false":
                    if width == 0.0:
                        width = 0.1
                    layerNew.circleCutHole(x, y, r - width / 2.)
        # polygon
        if display[3]:
            for i in re.findall(r'\[start\]\(polygon[\s+a-zA-Z0-9\-]*\(layer\s+%s\)(.+?)\[stop\]' % layerNumber, dane, re.MULTILINE|re.DOTALL):
                polygonData = []
                skipLast = False
                [width, fill] = re.search(r'\(width\s+(.+?)\)\s+\(fill\s+(.+?)\)\s+\(', i).groups()
                
                width = float(width)
                if width == 0:
                    width = 0.1
                #
                data = re.findall(r'\(vertex\s+\(position\s+(.+?)\s+(.+?)\)\s+\(angle\s+(.+?)\)\)', i)
                if data[0] == data[1]:
                    data.pop(0)
                
                if data[0] == data[-1]:
                    data.pop(-1)
                else:
                    fill = "false"
                    skipLast = True
                
                for j in range(0, len(data)):
                    if j == len(data) - 1 and skipLast:
                        break
                    #
                    x1 = float(data[j][0]) + X
                    y1 = float(data[j][1]) + Y
                    angle = float(data[j][2])
                    
                    if j == len(data) - 1:
                        x2 = float(data[0][0]) + X
                        y2 = float(data[0][1]) + Y
                    else:
                        x2 = float(data[j + 1][0]) + X
                        y2 = float(data[j + 1][1]) + Y
            
                    if fill == "true":
                        if not angle == 0.0:
                            polygonData.append(['Arc3P', x2, y2, x1, y1, angle])
                        else:
                            polygonData.append(['Line', x1, y1, x2, y2])
                    else:
                        if not angle == 0.0:
                            layerNew.addArcWidth([x1, y1], [x2, y2], angle, width)
                            if parent:
                                layerNew.addRotation(X, Y, parent['rot'])
                                layerNew.setChangeSide(X, Y, SIDE)
                            layerNew.setFace()
                        else:
                            if [x1, y1] != [x2, y2]:
                                layerNew.addLineWidth(x1, y1, x2, y2, width)
                                if parent:
                                    layerNew.addRotation(X, Y, parent['rot'])
                                    layerNew.setChangeSide(X, Y, SIDE)
                                layerNew.setFace()
                #
                if fill == "true":
                    layerNew.addPolygon(polygonData)
                    if parent:
                        layerNew.addRotation(X, Y, parent['rot'])
                        layerNew.setChangeSide(X, Y, SIDE)
                    layerNew.setFace()
    
    def getPaths(self, layerNew, layerNumber, display=[True, True, True, True]):
        self.getNetsegments()
        self.getElements()
        
        for i in self.netsegments.keys():
            for j in self.netsegments[i]["trace"].keys():
                wire = self.netsegments[i]["trace"][j]
                #
                if not wire["layer"] == layerNumber[0]:
                    continue
                # from
                if wire["fromType"] == "junction":
                    x1 = self.netsegments[i]["junction"][wire["from"]]["x"]
                    y1 = self.netsegments[i]["junction"][wire["from"]]["y"]
                elif wire["fromType"] == "via":
                    x1 = self.netsegments[i]["via"][wire["from"]]["x"]
                    y1 = self.netsegments[i]["via"][wire["from"]]["y"]
                elif wire["fromType"] == "device":
                    [deviceIdF, devicePadId] = re.search(r'^(.+?)\)\s+\(pad\s+(.*)', wire["from"]).groups()
                    
                    if deviceIdF in self.elements.keys():
                        packageID = self.elements[deviceIdF]["packageID"]
                        footprintID = self.elements[deviceIdF]["footprintID"]
                        X = self.elements[deviceIdF]["x"]
                        Y = self.elements[deviceIdF]["y"]
                        ROT = self.elements[deviceIdF]["rot"]
                        
                        if packageID in self.libraries.keys() and footprintID in self.libraries[packageID]['footprints'].keys():
                            footprint = self.libraries[packageID]['footprints'][footprintID]
                            
                            [x1, y1] = re.search(r'\(pad\s+%s.+?\(position\s+(.+?)\s+(.+?)\)' % devicePadId, footprint, re.MULTILINE|re.DOTALL).groups()
                            x1 = float(x1)
                            y1 = float(y1)
                            
                            [x1, y1] = self.obrocPunkt([x1, y1], [X, Y], ROT)
                            
                            if self.elements[deviceIdF]['side'] == "BOTTOM":
                                x1 = self.odbijWspolrzedne(x1, X)
                    else:
                        continue
                else:
                    continue
                # to
                if wire["toType"] == "junction":
                    x2 = self.netsegments[i]["junction"][wire["to"]]["x"]
                    y2 = self.netsegments[i]["junction"][wire["to"]]["y"]
                elif wire["toType"] == "via":
                    x2 = self.netsegments[i]["via"][wire["to"]]["x"]
                    y2 = self.netsegments[i]["via"][wire["to"]]["y"]
                elif wire["toType"] == "device":
                    [deviceIdF, devicePadId] = re.search(r'^(.+?)\)\s+\(pad\s+(.*)', wire["to"]).groups()
                    
                    if deviceIdF in self.elements.keys():
                        packageID = self.elements[deviceIdF]["packageID"]
                        footprintID = self.elements[deviceIdF]["footprintID"]
                        X = self.elements[deviceIdF]["x"]
                        Y = self.elements[deviceIdF]["y"]
                        ROT = self.elements[deviceIdF]["rot"]
                        
                        if packageID in self.libraries.keys() and footprintID in self.libraries[packageID]['footprints'].keys():
                            footprint = self.libraries[packageID]['footprints'][footprintID]
                            
                            [x2, y2] = re.search(r'\(pad\s+%s.+?\(position\s+(.+?)\s+(.+?)\)' % devicePadId, footprint, re.MULTILINE|re.DOTALL).groups()
                            x2 = float(x2)
                            y2 = float(y2)
                            
                            [x2, y2] = self.obrocPunkt([x2, y2], [X, Y], ROT)
                            
                            if self.elements[deviceIdF]['side'] == "BOTTOM":
                                x2 = self.odbijWspolrzedne(x2, X)
                    else:
                        continue
                else:
                    continue
                #
                if [x1, y1] != [x2, y2]:
                    layerNew.addLineWidth(x1, y1, x2, y2, wire["width"])
                    layerNew.setFace(signalName=i[0:5])
            

    def defineFunction(self, layerNumber):
        if "_cu" in layerNumber.lower():
            return "paths"
        elif "_pad" in layerNumber.lower():
            return "pads"
        elif "anno" in layerNumber.lower():
            return "annotations"
        elif "glue" in layerNumber.lower():
            return "glue"
        else:
            return "silk"
