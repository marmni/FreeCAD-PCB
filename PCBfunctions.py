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
import random
import builtins
from PySide import QtCore, QtGui
import os
import time
from shutil import copy2, make_archive, rmtree
import configparser
import glob
import zipfile
import tempfile
#import sys
from math import sqrt, atan2, sin, cos, radians, pi, hypot, atan, degrees
from PCBdataBase import dataBase

__currentPath__ = os.path.abspath(os.path.join(os.path.dirname(__file__), ''))

########################################################################
## configparser
########################################################################

def configParserRead(sectionName):
    try:
        config = configparser.RawConfigParser()
        config.read(os.path.join(__currentPath__, 'PCBsettings.cfg'))
        
        if sectionName in config.sections():
            dane = {}
            for i in config.items(sectionName):
                dane[i[0]] = i[1]
            return dane
        else:
            return False
    except Exception as e:
        FreeCAD.Console.PrintWarning(u"Error: {0} \n".format(e))

def configParserWrite(sectionName, data):
    try:
        config = configparser.RawConfigParser()
        config.read(os.path.join(__currentPath__, 'PCBsettings.cfg'))
        
        if not sectionName in config.sections():
            config.add_section(sectionName)
        
        for i, j in data.items():
            config.set(sectionName, i, j)
            
        with open(os.path.join(__currentPath__, 'PCBsettings.cfg'), 'w') as configfile:
            config.write(configfile)
        
    except Exception as e:
        FreeCAD.Console.PrintWarning(u"Error: {0} \n".format(e))

########################################################################
########################################################################
########################################################################

#def printError(self, data, info=''):
    #Fexc_type, exc_value, exc_tb = sys.exc_info()
            
            
            #FreeCAD.Console.PrintWarning(exc_type)
            #FreeCAD.Console.PrintWarning('\n')
            #FreeCAD.Console.PrintWarning(exc_value)
            #FreeCAD.Console.PrintWarning('\n')
            #FreeCAD.Console.PrintWarning(exc_tb)
            #FreeCAD.Console.PrintWarning('\n')
            
            #import traceback
            #filename, line_num, func_name, text = traceback.extract_tb(exc_tb)[-1]
            
            #FreeCAD.Console.PrintWarning(filename)
            #FreeCAD.Console.PrintWarning('\n')
            #FreeCAD.Console.PrintWarning(line_num)
            #FreeCAD.Console.PrintWarning('\n')
            #FreeCAD.Console.PrintWarning(func_name)
            #FreeCAD.Console.PrintWarning('\n')
            #FreeCAD.Console.PrintWarning(text)
            #FreeCAD.Console.PrintWarning('\n')

def filterHoles(r, Hmin, Hmax):
    if Hmin == 0 and Hmax == 0:
        return True
    elif Hmin != 0 and Hmax == 0 and Hmin <= r * 2:
        return True
    elif Hmax != 0 and Hmin == 0 and r * 2 <= Hmax:
        return True
    elif Hmin <= r * 2 <= Hmax:
        return True
    else:
        return False

########################################################################
#
########################################################################

def sketcherGetArcAngle(arcData):
    x1 = arcData.StartPoint.x
    y1 = arcData.StartPoint.y
    x2 = arcData.EndPoint.x
    y2 = arcData.EndPoint.y
    
    x = arcData.Center.x
    y = arcData.Center.y
    
    axisZ = arcData.Axis.z
    angleXU = arcData.AngleXU
    curve = degrees(arcData.FirstParameter) - degrees(arcData.LastParameter)
    
    if axisZ > 0:
        curve *= -1
    
    if curve < 0:
        #if angleXU < 0:
        start = degrees(atan2(y2 - y, x2 - x))
    else:
        if angleXU < 0:
            start =  360 + degrees(atan2(y1 - y, x1 - x))
        else:
            start =  degrees(atan2(y1 - y, x1 - x))

    stop = abs(curve) + start 
    
    return [round(curve, 4), round(start, 4), round(stop, 4)]

def sketcherRemoveOpenShapes(dataIN):
    outline = {}
    
    for i in dataIN.keys():
        if dataIN[i][0][-1] == 'Circle':
            outline[i] = dataIN[i]
        if [dataIN[i][0][0], dataIN[i][0][1]] != [dataIN[i][len(dataIN[i])-1][0] , dataIN[i][len(dataIN[i])-1][1]] and dataIN[i][0][-1] != 'Circle':
            FreeCAD.Console.PrintWarning("Open shape omitted.\n")
            continue
        else:
            outline[i] = dataIN[i]
    
    return outline

def sketcherGetGeometryShapes(sketcherIN):
    if not sketcherIN.isDerivedFrom("Sketcher::SketchObject"):
        FreeCAD.Console.PrintWarning("Error: Object is not a sketcher.\n")
        return [False]
    elif not len(sketcherIN.Geometry):
        FreeCAD.Console.PrintWarning("Error: No geometry.\n")
        return [False]
    elif not FreeCAD.activeDocument():
        FreeCAD.Console.PrintWarning("Error: FreeCAD is not activated.\n")
        return [False]
    #
    outList = {}
    try:
        num_1 = 0
        num_2 = 1
        data = sketcherIN.Geometry
        first = False
        
        while len(data):
            for i in range(0, len(data)):
                if data[i].Construction:
                    data.pop(i)
                    break
                ####
                if type(data[i]).__name__ == 'ArcOfCircle':
                    [angle, startAngle, stopAngle] = sketcherGetArcAngle(data[i])
                    
                    x3 = float("%.4f" % ( data[i].StartPoint.x))
                    y3 = float("%.4f" % ( data[i].StartPoint.y))
                    x4 = float("%.4f" % ( data[i].EndPoint.x))
                    y4 = float("%.4f" % ( data[i].EndPoint.y))
                    
                    if not first:
                        num_1 = 0
                        if not num_2 in outList.keys():
                            outList[num_2] = {}
                        outList[num_2][num_1] = [x3, y3, 'Line']
                        num_1 += 1
                        outList[num_2][num_1] = [x4, y4, angle, data[i], 'Arc']
                        data.pop(i)
                        first = True
                        
                        x2 = x4
                        y2 = y4
                        
                        break
                    #
                    if [x3, y3] == [x2, y2]:
                        num_1 += 1
                        outList[num_2][num_1] = [x4, y4, angle, data[i], 'Arc']
                        x2 = x4
                        y2 = y4
                        data.pop(i)
                        break
                    elif [x4, y4] == [x2, y2]:
                        num_1 += 1
                        outList[num_2][num_1] = [x3, y3, angle, data[i], 'rev', 'Arc']
                        x2 = x3
                        y2 = y3
                        data.pop(i)
                        break
                elif type(data[i]).__name__ == 'LineSegment':
                    x3 = float("%.4f" % ( data[i].StartPoint.x))
                    y3 = float("%.4f" % ( data[i].StartPoint.y))
                    x4 = float("%.4f" % ( data[i].EndPoint.x))
                    y4 = float("%.4f" % ( data[i].EndPoint.y))
                    
                    if not first:
                        num_1 = 0
                        if not num_2 in outList.keys():
                            outList[num_2] = {}
                        outList[num_2][num_1] = [x3, y3, 'Line']
                        num_1 += 1
                        outList[num_2][num_1] = [x4, y4, 'Line']
                        data.pop(i)
                        first = True
                        
                        x2 = x4
                        y2 = y4
                        
                        break
                    #
                    if [x3, y3] == [x2, y2]:
                        num_1 += 1
                        outList[num_2][num_1] = [x4, y4, 'Line']
                        x2 = x4
                        y2 = y4
                        data.pop(i)
                        break
                    elif [x4, y4] == [x2, y2]:
                        num_1 += 1
                        outList[num_2][num_1] = [x3, y3, 'Line']
                        x2 = x3
                        y2 = y3
                        data.pop(i)
                        break
                ######
                if i == len(data) - 1:
                    if type(data[0]).__name__ == 'Circle':
                        xs = float("%.4f" % (data[0].Center.x))
                        ys = float("%.4f" % (data[0].Center.y))
                        r = float("%.4f" % (data[0].Radius))
                        
                        num_2 += 1
                        outList[num_2] = {}
                        outList[num_2][0] = [xs, ys, r, 'Circle']
                        data.pop(i)
                    #########
                    first = False
                    num_2 += 1
                    break
    except Exception as e:
        FreeCAD.Console.PrintWarning('1. ' + str(e) + "\n")
    #
    return [True, outList]


def sketcherGetGeometry(sketcherIN):
    if not sketcherIN.isDerivedFrom("Sketcher::SketchObject"):
        FreeCAD.Console.PrintWarning("Error: Object is not a sketcher.\n")
        return [False]
    elif not len(sketcherIN.Geometry):
        FreeCAD.Console.PrintWarning("Error: No geometry.\n")
        return [False]
    elif not FreeCAD.activeDocument():
        FreeCAD.Console.PrintWarning("Error: FreeCAD is not activated.\n")
        return [False]
    #
    outline = []
    try:
        for k in range(len(sketcherIN.Geometry)):
            if sketcherIN.Geometry[k].Construction:
                continue
            
            if type(sketcherIN.Geometry[k]).__name__ == 'LineSegment':
                outline.append({
                    'type': 'line',
                    'x1': sketcherIN.Geometry[k].StartPoint.x,
                    'y1': sketcherIN.Geometry[k].StartPoint.y,
                    'x2': sketcherIN.Geometry[k].EndPoint.x,
                    'y2': sketcherIN.Geometry[k].EndPoint.y
                })
            elif type(sketcherIN.Geometry[k]).__name__ == 'Circle':
                outline.append({
                    'type': 'circle',
                    'x': sketcherIN.Geometry[k].Center.x,
                    'y': sketcherIN.Geometry[k].Center.y,
                    'r': sketcherIN.Geometry[k].Radius,
                })
            elif type(sketcherIN.Geometry[k]).__name__ == 'ArcOfCircle':
                [angle, startAngle, stopAngle] = sketcherGetArcAngle(sketcherIN.Geometry[k])
                
                outline.append({
                    'type': 'arc',
                    'x': sketcherIN.Geometry[k].Center.x,
                    'y': sketcherIN.Geometry[k].Center.y,
                    'r': sketcherIN.Geometry[k].Radius,
                    'angle': angle,
                    'x1': sketcherIN.Geometry[k].StartPoint.x,
                    'y1': sketcherIN.Geometry[k].StartPoint.y,
                    'x2': sketcherIN.Geometry[k].EndPoint.x,
                    'y2': sketcherIN.Geometry[k].EndPoint.y,
                    'startAngle': startAngle, 
                    'stopAngle': stopAngle
                })
        
    except Exception as e:
        FreeCAD.Console.PrintWarning('1. ' + str(e) + "\n")
    #
    return [True, outline]

# def sortPointsCounterClockwise(data):
    # result = []
    # for i in data.keys():
        # if data[i][0][-1] == 'Circle':
            # result.append[data[i][0]]
            # continue
        # if [data[i][0][0], data[i][0][1]] != [data[i][len(data[i])-1][0] , data[i][len(data[i])-1][1]] and data[i][0][-1] != 'Circle':
            # #FreeCAD.Console.PrintWarning("Open shape omitted.\n")
            # continue
        # #
        # xValue = [data[i][k][0] for k in data[i].keys()]
        # xMin = min(xValue)
        # xMax = max(xValue)
        # xCenter = (xMin + xMax) / 2.

        # yValue = [data[i][k][1] for k in data[i].keys()]
        # yMin = min(yValue)
        # yMax = max(yValue)
        # yCenter = (yMin + yMax) / 2.
        
        # out = {}
        # for j in data[i].keys():
            # x = data[i][j][0]
            # y = data[i][j][1]
            
            # # angle = atan(x - xCenter)
            # # if x - xCenter < 0 and y - yCenter > 0:
                # # angle *= -1
                # # angle += 3.14
            # # elif x - xCenter < 0 and y - yCenter < 0:
                # # angle -= 3.14
            # # elif x - xCenter > 0 and y - yCenter < 0:
                # # angle *= -1
            
            # angle = atan2((y - yCenter)*-1, x - xCenter)*-1
            # if x - xCenter < 0:
                # angle -= 2*pi
            # out[angle] =  data[i][j]
        # #
        # tmp = []
        # for p in builtins.sorted(out.keys()):  
            # tmp.append(out[p])
        # result.append(tmp)
    # #
    # return result

########################################################################
#
########################################################################

def setProjectFile(filename, char=['(', ')']):
    projektBRD = builtins.open(filename, "r").read()[1:]
    wynik = ''
    licznik = 0
    txt = ''
    start = 0
    #
    txt_1 = 0

    for i in projektBRD:
        if i in ['"', "'"] and txt_1 == 0:
            txt_1 = 1
        elif i in ['"', "'"] and txt_1 == 1:
            txt_1 = 0
        
        if txt_1 == 0:
            if i == char[0]:
                licznik += 1
                start = 1
            elif i == char[1]:
                licznik -= 1
        
        txt += i
        
        if licznik == 0 and start == 1:
            wynik += '[start]' + txt.strip() + '[stop]'
            txt = ''
            start = 0
    
    return wynik


def wygenerujID(ll, lc):
    ''' generate random section name '''
    numerID = ""

    for i in range(ll):
        numerID += random.choice('abcdefghij')
    numerID += "_"
    for i in range(lc):
        numerID += str(random.randrange(0, 99, 1))
    
    return numerID

class kolorWarstwy(QtGui.QPushButton):
    def __init__(self, parent=None):
        QtGui.QPushButton.__init__(self, parent)
        self.setStyleSheet('''
            QPushButton
            {
                border: 1px solid #000;
                background-color: rgb(255, 0, 0);
                margin: 1px;
            }
        ''')
        self.setFlat(True)
        #self.setFixedSize(20, 20)
        self.kolor = [0., 0., 0.]
        #
        self.connect(self, QtCore.SIGNAL("released ()"), self.pickColor)
        
    def PcbColorToRGB(self, baseColor):
        returnColor = []
        
        returnColor.append(baseColor[0] * 255)
        returnColor.append(baseColor[1] * 255)
        returnColor.append(baseColor[2] * 255)
        
        return returnColor
        
    def setColor(self, nowyKolorRGB):
        self.kolor = nowyKolorRGB
        self.setStyleSheet('''
            QPushButton
            {
                border: 1px solid #000;
                background-color: rgb(%i, %i, %i);
                margin: 1px;
            }
        ''' % (nowyKolorRGB[0],
               nowyKolorRGB[1],
               nowyKolorRGB[2]))
    
    def pickColor(self):
        pick = QtGui.QColorDialog(QtGui.QColor(self.kolor[0], self.kolor[1], self.kolor[2]))
        if pick.exec_():
            [R, G, B, A] = pick.selectedColor().getRgb()
            
            self.setColor([R, G, B])

    def getColor(self):
        R = float(self.kolor[0] / 255.)
        G = float(self.kolor[1] / 255.)
        B = float(self.kolor[2] / 255.)
        return (R, G, B)


def getFromSettings_Color_0(val, defVal):
    return FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetUnsigned(val, defVal)

def getFromSettings_Color_1(val, defVal):
    color = getFromSettings_Color_0(val, defVal)
    
    r = float((color>>24)&0xFF)
    g = float((color>>16)&0xFF)
    b = float((color>>8)&0xFF)
    
    return [r, g, b]

def getFromSettings_Color(val, defVal):
    color = getFromSettings_Color_0(val, defVal)
    
    r = float((color>>24)&0xFF)/255.0
    g = float((color>>16)&0xFF)/255.0
    b = float((color>>8)&0xFF)/255.0
    
    return (r, g, b)

def getFromSettings_databasePath():
    if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("databasePath", "").strip() != '':
        database =FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("databasePath", "")
    else:
        database = __currentPath__ + '/data/database.cfg'
    
    return database.replace('cfg', 'db')
    

class importScriptCopy(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u'Import database')
        
        self.archiveFile = None
        self.tmpDir = None
        self.importSettings = {'parts': False, 'settings': False, 'database': False}
        self.sql = None
        
        # file
        self.filePath = QtGui.QLineEdit('')
        self.filePath.setReadOnly(True)
        
        filePathButton = QtGui.QPushButton('...')
        self.connect(filePathButton, QtCore.SIGNAL("clicked()"), self.chooseFile)
        
        filePathFrame = QtGui.QFrame()
        filePathFrame.setObjectName('lay_path_widget')
        filePathFrame.setStyleSheet('''#lay_path_widget {background-color:#fff; border:1px solid rgb(199, 199, 199); padding: 5px;}''')
        filePathLayout = QtGui.QHBoxLayout(filePathFrame)
        filePathLayout.addWidget(QtGui.QLabel(u'File:\t'))
        filePathLayout.addWidget(self.filePath)
        #filePathLayout.addWidget(self.loadingWidget)
        filePathLayout.addWidget(filePathButton)
        filePathLayout.setContentsMargins(0, 0, 0, 0)
        
        # tabs
        self.tabs = QtGui.QTabWidget()
        self.tabs.setTabPosition(QtGui.QTabWidget.West)
        self.tabs.setObjectName('tabs_widget')
        self.tabs.addTab(self.tabCategories(), u'Models')
        self.tabs.addTab(self.tabSettings(), u'FreeCAD settings')
        self.tabs.setTabEnabled(0, False)
        self.tabs.setTabEnabled(1, False)
        
        # buttons
        buttons = QtGui.QDialogButtonBox()
        buttons.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
        buttons.addButton("Import", QtGui.QDialogButtonBox.AcceptRole)
        self.connect(buttons, QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        self.connect(buttons, QtCore.SIGNAL("rejected()"), self, QtCore.SLOT("reject()"))
        
        buttonsFrame = QtGui.QFrame()
        buttonsFrame.setObjectName('lay_path_widget')
        buttonsFrame.setStyleSheet('''#lay_path_widget {background-color:#fff; border:1px solid rgb(199, 199, 199); padding: 5px;}''')
        buttonsLayout = QtGui.QHBoxLayout(buttonsFrame)
        buttonsLayout.addWidget(buttons)
        buttonsLayout.setContentsMargins(0, 0, 0, 0)
        
        # main layout
        lay = QtGui.QGridLayout(self)
        lay.addWidget(filePathFrame, 0, 0, 1, 1)
        lay.addWidget(self.tabs, 1, 0, 1, 1)
        lay.addWidget(buttonsFrame, 2, 0, 1, 1)
        lay.setRowStretch(1, 10)
        lay.setContentsMargins(5, 5, 5, 5)
        
        #loadingGif = QtGui.QMovie('C:/Users/marmn/Desktop/FreeCAD_0.18.14495_Conda_Py3QT5-WinVS2016_x64/Mod/PCB/data/loading.gif')
        self.loadingWidget = QtGui.QLabel('', self)
        self.loadingWidget.setPixmap(QtGui.QPixmap('C:/Users/marmn/Desktop/FreeCAD_0.18.14495_Conda_Py3QT5-WinVS2016_x64/Mod/PCB/data/loading.png'))
        self.loadingWidget.setMinimumSize(400, 400)
        #self.loadingWidget.setMovie(loadingGif)
        #loadingGif.start()
        self.loadingWidget.hide()
    
    def showLoading(self):
        time.sleep(0.05)
        QtGui.QApplication.processEvents()
        #
        x = self.width() / 2. - 50
        y = self.height() / 2. - 200
        self.loadingWidget.move(x, y)
        self.loadingWidget.show()
        #
        time.sleep(0.05)
        QtGui.QApplication.processEvents()
        
    def hideLoading(self):
        time.sleep(0.05)
        QtGui.QApplication.processEvents()
        #
        self.loadingWidget.hide()
        #
        time.sleep(0.05)
        QtGui.QApplication.processEvents()
    
    def importChilds(self, parentItem, parentID, socketsID, topItem=False):
        if topItem:
            childsList = parentItem.topLevelItemCount()
        else:
            childsList = parentItem.childCount()
        
        for i in range(0, childsList):
            if topItem:
                itemMain = self.categoriesTable.topLevelItem(i)
            else:
                itemMain = parentItem.child(i)
            
            if itemMain.checkState(0) and itemMain.data(0, QtCore.Qt.UserRole) in ['IC', 'C']:  # categories
                categoryName = itemMain.text(0)
                categoryType = itemMain.data(0, QtCore.Qt.UserRole)
                categoryDescription = itemMain.text(1)
                
                if categoryType == 'IC':  # ID of existing category
                    categoryID = itemMain.data(0, QtCore.Qt.UserRole + 1)
                else:  # add new category
                    self.originalDatabase.addCategory(categoryName, parentID, categoryDescription)
                    categoryID = self.originalDatabase.lastInsertedID
                
                socketsID = self.importChilds(itemMain, categoryID, socketsID)
            elif itemMain.checkState(0) and itemMain.data(0, QtCore.Qt.UserRole) in ['IM', 'M']:  # models
                modelType = itemMain.data(0, QtCore.Qt.UserRole)
                
                # get packages
                importNumber = 0
                paramModelSoftware = []
                for j in range(0, itemMain.childCount()):
                    itemPackage = itemMain.child(j)
                    if itemPackage.checkState(0) and itemPackage.data(0, QtCore.Qt.UserRole) == 'P':  # new package
                        dataPackage = self.importDatabase.getPackageByID(itemPackage.data(0, QtCore.Qt.UserRole + 1))
                        if dataPackage:
                            paramPackage = {
                                'name' : dataPackage.name,
                                'software' : dataPackage.software,
                                'x' : dataPackage.x,
                                'y' : dataPackage.y,
                                'z' :  dataPackage.z,
                                'rx' : dataPackage.rx,
                                'ry' : dataPackage.ry,
                                'rz' : dataPackage.rz,
                                'blanked': False
                            }
                            paramModelSoftware.append(paramPackage)
                            importNumber += 1
                
                if modelType == 'IM':  # ID of existing model - add only new package
                    modelID = itemMain.data(0, QtCore.Qt.UserRole + 1)
                    
                    for j in paramModelSoftware:
                        self.originalDatabase.addPackage(j, modelID=modelID)
                    
                else:  # add new model
                    data = self.importDatabase.getModelByID(itemMain.data(0, QtCore.Qt.UserRole + 1))[1]
                    paramModel = {
                        'name' : data.name,
                        'description' : data.description,
                        'categoryID' : parentID,
                        'datasheet' : data.datasheet,
                        'path3DModels' : data.path3DModels,
                        'isSocket' : data.isSocket,
                        'isSocketHeight' : data.isSocketHeight,
                        'socketID' : data.socketID,
                        'socketIDSocket' : data.socketIDSocket,
                        'software' : paramModelSoftware
                    }
                    
                    if importNumber:  # protection against importing model without packages
                        self.originalDatabase.addModel(paramModel)
                        ####
                        if data.isSocket:
                            if not itemMain.data(0, QtCore.Qt.UserRole + 1) in socketsID.keys():
                                socketsID[itemMain.data(0, QtCore.Qt.UserRole + 1)] = [[]]
                            else:
                                socketsID[itemMain.data(0, QtCore.Qt.UserRole + 1)].append(self.originalDatabase.lastInsertedModelID)
                        ####
                        if data.socketIDSocket:
                            if not data.socketID in socketsID.keys():
                                socketsID[data.socketID] = [[]]
                            
                            socketsID[data.socketID][0].append(self.originalDatabase.lastInsertedModelID)
                        ####
        return socketsID
        
    def accept(self):
        self.showLoading()
        categoriesID = {}  # OLD_ID : [[], NEW_ID]
        socketsID = {}
        
        socketsID = self.importChilds(self.categoriesTable, 0, socketsID, True)  # main categories/models
        ### update sockets
        #FreeCAD.Console.PrintWarning(u"{0} \n".format(socketsID))
        for i in socketsID.keys():
            newID = socketsID[i][1]
            
            for j in socketsID[i][0]:
                self.originalDatabase.updateModelSockedID(j, newID)
        #
        self.hideLoading()
        self.done(1)
        return True
    
    #def modelsListsetRowColor(self, item, color):
        #item.setBackground(0, QtGui.QBrush(QtGui.QColor(color[0], color[1], color[2])))
        #item.setBackground(1, QtGui.QBrush(QtGui.QColor(color[0], color[1], color[2])))
        #item.setBackground(2, QtGui.QBrush(QtGui.QColor(color[0], color[1], color[2])))
        #item.setBackground(3, QtGui.QBrush(QtGui.QColor(color[0], color[1], color[2])))
        ##item.setBackground(4, QtGui.QBrush(QtGui.QColor(color[0], color[1], color[2])))

    def itemParentSetCheckState(self, item):
        if item.parent() and item.checkState(0):
            item.parent().setCheckState(0, item.checkState(0))
            self.itemParentSetCheckState(item.parent())
    
    def itemChildSetCheckState(self, item):
        for i in range(0, item.childCount()):
            if not item.child(i).data(0, QtCore.Qt.UserRole).startswith('E'):
                item.child(i).setCheckState(0, item.checkState(0))
                self.itemChildSetCheckState(item.child(i))
                
    def changeChildsState(self, item, num):
        if item.parent() and item.checkState(0):
            self.itemParentSetCheckState(item)
        self.itemChildSetCheckState(item)
    
    def selectAllCategories(self):
        for i in QtGui.QTreeWidgetItemIterator(self.categoriesTable):
            if not i.value().data(0, QtCore.Qt.UserRole).startswith('E'):
                i.value().setCheckState(0, QtCore.Qt.Checked)
    
    def unselectAllCategories(self):
        for i in QtGui.QTreeWidgetItemIterator(self.categoriesTable):
            if not i.value().data(0, QtCore.Qt.UserRole).startswith('E'):
                i.value().setCheckState(0, QtCore.Qt.Unchecked)
    
    def tabCategories(self):
        tab = QtGui.QWidget()
        
        # table
        self.categoriesTable = QtGui.QTreeWidget()
        #self.categoriesTable.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.categoriesTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.categoriesTable.setHeaderLabels([u'Name', u'Description', u'Paths', u'Softwares'])
        self.categoriesTable.setStyleSheet('''
            QTreeWidget {border:0px solid #FFF;}
        ''')
        self.connect(self.categoriesTable, QtCore.SIGNAL("itemPressed (QTreeWidgetItem*,int)"), self.showInfoF)
        self.connect(self.categoriesTable, QtCore.SIGNAL("itemClicked (QTreeWidgetItem*,int)"), self.changeChildsState)
        # buttons
        selectAll = QtGui.QPushButton()
        selectAll.setFlat(True)
        selectAll.setToolTip('Select all')
        selectAll.setIcon(QtGui.QIcon(":/data/img/checkbox_checked_16x16.png"))
        selectAll.setStyleSheet('''border:1px solid rgb(237, 237, 237);''')
        self.connect(selectAll, QtCore.SIGNAL("clicked()"), self.selectAllCategories)
        
        unselectAll = QtGui.QPushButton()
        unselectAll.setFlat(True)
        unselectAll.setToolTip('Deselect all')
        unselectAll.setIcon(QtGui.QIcon(":/data/img/checkbox_unchecked_16x16.PNG"))
        unselectAll.setStyleSheet('''border:1px solid rgb(237, 237, 237);''')
        self.connect(unselectAll, QtCore.SIGNAL("clicked()"), self.unselectAllCategories)
        
        collapseAll = QtGui.QPushButton()
        collapseAll.setFlat(True)
        collapseAll.setToolTip('Collapse all')
        collapseAll.setIcon(QtGui.QIcon(":/data/img/collapse.png"))
        collapseAll.setStyleSheet('''border:1px solid rgb(237, 237, 237);''')
        self.connect(collapseAll, QtCore.SIGNAL("clicked()"), self.categoriesTable.collapseAll)
        
        expandAll = QtGui.QPushButton()
        expandAll.setFlat(True)
        expandAll.setToolTip('Expand all')
        expandAll.setIcon(QtGui.QIcon(":/data/img/expand.png"))
        expandAll.setStyleSheet('''border:1px solid rgb(237, 237, 237);''')
        self.connect(expandAll, QtCore.SIGNAL("clicked()"), self.categoriesTable.expandAll)
        # info
        self.showInfo = QtGui.QLabel('')
        self.showInfo.setStyleSheet('border:1px solid rgb(237, 237, 237); padding:5px 2px;')
        
        # main lay
        layTableButtons = QtGui.QHBoxLayout()
        layTableButtons.addWidget(selectAll)
        layTableButtons.addWidget(unselectAll)
        layTableButtons.addWidget(collapseAll)
        layTableButtons.addWidget(expandAll)
        layTableButtons.addStretch(10)
        
        lay = QtGui.QGridLayout(tab)
        lay.addLayout(layTableButtons, 0, 0, 1, 1)
        lay.addWidget(self.categoriesTable, 1, 0, 1, 1)
        lay.addWidget(self.showInfo, 2, 0, 1, 1)
        lay.setRowStretch(1, 10)
        lay.setColumnStretch(0, 10)
        lay.setContentsMargins(5, 5, 5, 5)
        
        return tab

    def showInfoF(self, item, num):
        self.showInfo.setText(item.data(0, QtCore.Qt.UserRole + 3))
        
    def tabSettings(self):
        tab = QtGui.QWidget()
        return tab
 
    def importDataBase(self):
        if self.importSettings['database']:
            #FreeCAD.Console.PrintWarning("\ntempfile: {0}\n".format(self.tmpDir))
            #
            try:
                self.importDatabase = dataBase()
                self.importDatabase.connect(os.path.join(self.tmpDir, "database.db"))  # imported database - tmp directory
                
                self.originalDatabase = dataBase()
                self.originalDatabase.connect()
                #
                self.tabs.setTabEnabled(0, True)
                self.tabs.setTabEnabled(1, False)
                self.loadCategoryData(self.importDatabase.getAllcategoriesWithSubCat(), self.categoriesTable, True)
                self.loadModelsData(self.categoriesTable, 0, True)  # models without category
            except Exception as e:
                FreeCAD.Console.PrintWarning("\nERROR: {0}.\n".format(e))

    def loadPackagesData(self, parentObject, modelID):
        newP = 0
        
        for i in self.importDatabase.getPackagesByModelID(modelID):
            position = "X:{0} ;Y:{1} ;Z:{2} ;RX:{3} ;RY:{4} ;RZ:{5}".format(i.x, i.y, i.z, i.rx, i.ry, i.rz)
            #
            item = QtGui.QTreeWidgetItem([i.name, i.software, position])
            item.setData(0, QtCore.Qt.UserRole + 1, i.id)
            
            if self.originalDatabase.findPackage(i.name, i.software):
                item.setData(0, QtCore.Qt.UserRole, 'ER')
                item.setData(0, QtCore.Qt.UserRole + 3, "<span style='font-weight:bold; color: #F00;'>Package already exist.")  # info
                item.setDisabled(True)
            else: # new package
                item.setCheckState(0, QtCore.Qt.Unchecked)
                item.setData(0, QtCore.Qt.UserRole, 'P')
                item.setData(0, QtCore.Qt.UserRole + 3, "<span style='font-weight:bold;'>New package.</span>")  # info
                
                newP += 1
            ########
            parentObject.addChild(item)
        ########
        ########
        if newP and parentObject.data(0, QtCore.Qt.UserRole) == 'EM':
            parentObject.setData(0, QtCore.Qt.UserRole, 'IM')
            parentObject.setData(0, QtCore.Qt.UserRole + 3, "<span style='font-weight:bold;'>New packages are available.")  # info
            parentObject.setDisabled(False)
            parentObject.setCheckState(0, QtCore.Qt.Unchecked)
            
    def loadModelsData(self, parentObject, categoryID, topItem=False):
        for i in self.importDatabase.getAllModelsByCategory(categoryID):
            modelPaths = i.path3DModels.split(';')
            
            item = QtGui.QTreeWidgetItem([i.name, i.description, '\n'.join(modelPaths)])
            item.setData(0, QtCore.Qt.UserRole + 1, i.id)
            
            data = self.originalDatabase.getModelByName(i.name)
            if data[0]:
                item.setData(0, QtCore.Qt.UserRole, 'EM')
                item.setData(0, QtCore.Qt.UserRole + 1, data[1].id)  # existing model ID
                item.setData(0, QtCore.Qt.UserRole + 3, "<span style='font-weight:bold; color: #F00;'>Model already exist.")  # info
                item.setDisabled(True)
            else:
                item.setData(0, QtCore.Qt.UserRole, 'M')
                item.setCheckState(0, QtCore.Qt.Unchecked)
                item.setData(0, QtCore.Qt.UserRole + 3, "<span style='font-weight:bold;'>New model.")  # info
            
            #load packages
            self.loadPackagesData(item, i.id)
            ########
            if topItem:
                parentObject.addTopLevelItem(item)
            else:
                parentObject.addChild(item)
    
    def loadCategoryData(self, categories, parentObject, topItem=False):
        for i in categories.keys():
            mainItem = QtGui.QTreeWidgetItem(['{0}'.format(i), categories[i]['description']])
            mainItem.setData(0, QtCore.Qt.UserRole + 1, categories[i]['id'])
            mainItem.setCheckState(0, QtCore.Qt.Unchecked)
            
            data = self.originalDatabase.getCategoryByName(i)
            if data[0]:
                mainItem.setData(0, QtCore.Qt.UserRole, 'IC')
                mainItem.setData(0, QtCore.Qt.UserRole + 1, data[1].id)  # existing category ID
                mainItem.setData(0, QtCore.Qt.UserRole + 3, "<span style='font-weight:bold; color: #F00;'>Category already exist.")  # info
            else:
                mainItem.setData(0, QtCore.Qt.UserRole, 'C')
                mainItem.setData(0, QtCore.Qt.UserRole + 3, "<span style='font-weight:bold;'>New category.</span>")  # info
                
            # import models
            self.loadModelsData(mainItem, categories[i]['id'])
            # import sub categories
            self.loadCategoryData(categories[i]['sub'], mainItem)
            
            ##########
            if topItem:
                #widgetAction = QtGui.QComboBox()
                #widgetAction.addItem('New category', [-1, ''])  # new category
                parentObject.addTopLevelItem(mainItem)
                #parentObject.setItemWidget(mainItem, 1, widgetAction)
            else:
                parentObject.addChild(mainItem)

        #try:
            #for i in range(self.categoriesTable.rowCount()):
                #if self.categoriesTable.cellWidget(i, 0).isChecked():
                    #oldCategoryID = int(self.categoriesTable.item(i, 1).text())
                    #if self.categoriesTable.cellWidget(i, 4).currentIndex() == 0:
                        #mainItem = QtGui.QTreeWidgetItem(['{0} (New category)'.format(self.categoriesTable.item(i, 2).text())])
                        #mainItem.setData(0, QtCore.Qt.UserRole, 'New')
                        #mainItem.setData(0, QtCore.Qt.UserRole + 3, "<span style='font-weight:bold;'>New category '{0}' will be added.</span>".format(self.categoriesTable.item(i, 2).text()))  # info
                    #else:
                        #categoryData = self.categoriesTable.cellWidget(i, 4).itemData(self.categoriesTable.cellWidget(i, 4).currentIndex())
                        
                        #mainItem = QtGui.QTreeWidgetItem(['{1} (Existing category {0})'.format(categoryData[1], self.categoriesTable.item(i, 2).text())])
                        #mainItem.setData(0, QtCore.Qt.UserRole, 'Old')
                        #mainItem.setData(0, QtCore.Qt.UserRole + 3, "<span style='font-weight:bold;'>All entries from category '{1}' will be shifted to the existing '{0}'.</span>".format(categoryData[1], self.categoriesTable.item(i, 2).text()))  # info
                    
                    #mainItem.setData(0, QtCore.Qt.UserRole + 1, i)  # category row number
                    #self.modelsTable.addTopLevelItem(mainItem)
                    #self.modelsTable.setFirstItemColumnSpanned(mainItem, True)
                    
                    #categories[oldCategoryID] = mainItem
        #except Exception as e:
            #FreeCAD.Console.PrintWarning("ERROR: {0}.\n".format(e))
        
        
        
        #for i in self.importDatabase.getAllcategories():
            #categoryInfo = self.importDatabase.convertToTable(i)
            ##FreeCAD.Console.PrintWarning("\ncategoryInfo: {0}.\n".format(categoryInfo))
            
            #rowNumber = self.categoriesTable.rowCount()
            #self.categoriesTable.insertRow(rowNumber)
            ########
            #widgetActive = QtGui.QCheckBox('')
            #widgetActive.setStyleSheet('margin-left:18px;')
            #self.categoriesTable.setCellWidget(rowNumber, 0, widgetActive)
            ##
            #itemID = QtGui.QTableWidgetItem(str(categoryInfo['id']))
            #self.categoriesTable.setItem(rowNumber, 1, itemID)
            ##
            #itemName = QtGui.QTableWidgetItem(categoryInfo['name'])
            #self.categoriesTable.setItem(rowNumber, 2, itemName)
            
            #itemDescription = QtGui.QTableWidgetItem(categoryInfo['description'])
            #self.categoriesTable.setItem(rowNumber, 3, itemDescription)
            ## new category
            #widgetAction = QtGui.QComboBox()
            #widgetAction.addItem('New category', [-1, ''])  # new category
            
            #nr = 1
            #for j in self.originalDatabase.getAllcategories():
                #data = self.originalDatabase.convertToTable(j)
                
                #widgetAction.addItem('Move all objects to existing category: {0}'.format(data['name']), [data['id'], data['name']])
                #if data['name'] == categoryInfo['name']:
                    #widgetAction.setCurrentIndex(nr)
                #nr += 1
            #self.categoriesTable.setCellWidget(rowNumber, 4, widgetAction)

    def chooseFile(self):
        self.categoriesTable.clear()
        self.showInfo.setText('')
        self.tabs.setTabEnabled(0, False)
        self.tabs.setTabEnabled(1, False)
        #
        newDatabase = QtGui.QFileDialog.getOpenFileName(None, u'Choose file to import', os.path.expanduser("~"), '*.zip')
        if newDatabase[0].strip() != '' and self.checkFile(newDatabase[0].strip()):
            self.filePath.setText(newDatabase[0])
            #
            self.showLoading()
            self.importDataBase()
            self.hideLoading()
            
    def checkFile(self, fileName):
        try:
            if 'dataFreeCAD_pcb' in zipfile.ZipFile(fileName).namelist():
                self.tmpDir = tempfile.mkdtemp("_test")  # create tmp directory
                self.archiveFile = zipfile.ZipFile(fileName)
                self.archiveFile.extractall(self.tmpDir)

                self.importSettings = eval(self.archiveFile.read('dataFreeCAD_pcb'))
                #
                return True
            else:
                FreeCAD.Console.PrintWarning("\nIncorrect file format!\n")
                return False
        except Exception as e:
            FreeCAD.Console.PrintWarning("\nERROR: {0} (checkFile).\n".format(e))
            return False


class prepareScriptCopy(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u"Save database copy")
        self.setWindowIcon(QtGui.QIcon(":/data/img/databaseExport.png"))
        #
        self.optionSaveDatabase = QtGui.QCheckBox("Database")
        self.optionSaveModels = QtGui.QCheckBox("Models")
        self.optionSaveModels.setDisabled(True)
        self.optionSaveFreecadSettings = QtGui.QCheckBox("FreeCAD settings")
        self.optionSaveFreecadSettings.setDisabled(True)
        
        self.path = QtGui.QLineEdit(os.path.expanduser("~"))
        self.path.setReadOnly(True)
        
        pathChange = QtGui.QPushButton("...")
        self.connect(pathChange, QtCore.SIGNAL("clicked ()"), self.changePath)
        
        self.logs = QtGui.QTextEdit('')
        self.logs.setReadOnly(True)
        
        buttons = QtGui.QDialogButtonBox()
        buttons.setOrientation(QtCore.Qt.Horizontal)
        buttons.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
        buttons.addButton("Save", QtGui.QDialogButtonBox.AcceptRole)
        self.connect(buttons, QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        self.connect(buttons, QtCore.SIGNAL("rejected()"), self, QtCore.SLOT("reject()"))
        #
        layPath = QtGui.QHBoxLayout()
        layPath.addWidget(QtGui.QLabel(u"Path"))
        layPath.addWidget(self.path)
        layPath.addWidget(pathChange)
        
        lay = QtGui.QGridLayout(self)
        lay.addWidget(self.optionSaveDatabase, 1, 0, 1, 1)
        lay.addWidget(self.optionSaveModels, 2, 0, 1, 1)
        lay.addWidget(self.optionSaveFreecadSettings, 3, 0, 1, 1)
        #lay.addWidget(scriptLogo, 0, 1, 5, 1)
        lay.addWidget(self.logs, 0, 2, 6, 1)
        lay.addItem(QtGui.QSpacerItem(10, 10), 6, 0, 1, 3)
        lay.addLayout(layPath, 7, 0, 1, 3)
        lay.addItem(QtGui.QSpacerItem(10, 20), 8, 0, 1, 3)
        lay.addWidget(buttons, 9, 0, 1, 3)
        lay.setRowStretch(5, 10)
    
    def copyModels(self, path, oldPath, newPath):
        for i in glob.glob(os.path.join(path, '*')):
            if os.path.isdir(i):  # folders
                self.copyModels(i, oldPath, newPath)
            else:  # files
                currentPart = i.replace(os.path.join(oldPath, ''), '')
                [path, fileName] = os.path.split(currentPart)
                
                if not os.path.exists(os.path.join(newPath, path)):
                    os.makedirs(os.path.join(newPath, path))
                    
                if not fileName.endswith('fcstd1') and not os.path.exists(os.path.join(newPath, currentPart)):
                    copy2(os.path.join(oldPath, currentPart), os.path.join(newPath, currentPart))
    
    def changePath(self):
        newFolder = QtGui.QFileDialog.getExistingDirectory(None, 'Change path', self.path.text())
        if newFolder:
            self.path.setText(newFolder)
    
    def printInfo(self, data):
        time.sleep(0.05)
        self.logs.insertHtml(data)
        QtGui.QApplication.processEvents()
    
    def accept(self):
        path = self.path.text().strip()
        
        if not os.access(path, os.W_OK):
            self.logs.append("Error: Access denied!")
            return False
        
        mainPath = os.path.join(path, ".freecad_pcb_" + time.strftime('%y%m%d'))
        
        try:
            rmtree(mainPath)  # del tmp directory
        except:
            pass

        try:
            self.logs.clear()
            self.printInfo("<span style='color:rgb(0, 0, 0);'>Initializing</span>")
            
            os.makedirs(mainPath)  # create tmp directory
            ##
            self.printInfo("<br><span style='color:rgb(0, 0, 0);'>Copy database:&nbsp;</span>")
            if self.optionSaveDatabase.isChecked():
                copy2(getFromSettings_databasePath(), mainPath)
                
                self.printInfo("<span style='color:rgb(0, 255, 0);'>done</span>")
            else:
                self.printInfo("skipped")
            ##
            if self.optionSaveModels.isChecked():
                self.printInfo("<br><span style='color:rgb(0, 0, 0);'>Copy models:</span>")
                
                modelsDir = os.path.join(mainPath, "models")
                os.makedirs(modelsDir)
                
                if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("partsPaths", "").strip() != '':
                    librariesList = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("partsPaths", "").split(',')
                else:
                    librariesList = [os.path.join(FreeCAD.getHomePath(), "Mod\PCB\parts"), os.path.join(__currentPath__, "parts")]
                
                for i in librariesList:
                    self.printInfo("<br><span style='color:rgb(0, 0, 0);'>&nbsp;&nbsp;&nbsp;&nbsp;{0}:&nbsp;</span>".format(i))
                    
                    newPath = os.path.join(modelsDir, os.path.basename(i))
                    os.makedirs(newPath)
                    self.copyModels(i, i, newPath)
                    
                    self.printInfo("<span style='color:rgb(0, 255, 0);'>done</span>".format(i))
            else:
                self.printInfo("<br><span style='color:rgb(0, 0, 0);'>Copy models: skipped</span>")
            ##
            self.printInfo("<br><span style='color:rgb(0, 0, 0);'>Copy FreeCAD settings:&nbsp;</span>")
            if self.optionSaveFreecadSettings.isChecked():
                data = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB")
                data.Export(os.path.join(mainPath, 'freecad_pcb_settings.fcparam'))
                
                self.printInfo("<span style='color:rgb(0, 255, 0);'>done</span>")
            else:
                self.printInfo("skipped")
            ########
            plik = open(os.path.join(mainPath, 'dataFreeCAD_pcb'), 'w')
            plik.write(str({'database': self.optionSaveDatabase.isChecked(), 'parts': self.optionSaveModels.isChecked(), 'settings': self.optionSaveFreecadSettings.isChecked()}))
            plik.close()
            ########
            self.printInfo("<br><span style='color:rgb(0, 0, 0);'>Preparing zip file:&nbsp;</span>")
            
            make_archive(mainPath.replace('.freecad_pcb', 'freecad_pcb'), 'zip', mainPath)
            self.printInfo("<span style='color:rgb(0, 255, 0);'>done</span>")
            
            self.printInfo("<br><span style='color:rgb(0, 0, 0);'>Removing tmp files:&nbsp;</span>")
            rmtree(mainPath)  # del tmp directory
            self.printInfo("<span style='color:rgb(0, 255, 0);'>done</span>")
        except Exception as e:
            self.printInfo("<br><span style='color:rgb(255, 0, 0);'>Error: {0}!</span>".format(e))
            return False
        
        self.printInfo("<br><span style='color:rgb(0, 255, 0);'>Done!</span>")
        return True


########################################################################
####
####
####            MATH FUNCTIONS
####
####
########################################################################

class mathFunctions(object):
    def createPointsOnArc(self, point, center, angle, start=False, stop=False):
        arcData = []
        #
        x = point[0]
        y = point[1]
        xs = center[0]
        ys = center[1]
        #
        liczba = abs(angle)
        if liczba > 360:
            liczba = liczba % 360
        liczba = int(liczba / 90)
        if liczba == 0:
            liczba = 1
        liczba *= 7
        #
        if start:
            arcData.append([x, y]) # + first point -> start point
        
        rangeL = int(abs(angle) / liczba) - 1
        if stop:
            rangeL = int(abs(angle) / liczba) # + last point -> end point => start_point +/- angle
        
        for p in range(0, rangeL):
            if angle > 0:
                [x, y] = self.obrocPunkt2([x, y], [xs, ys], liczba)
            else:
                [x, y] = self.obrocPunkt2([x, y], [xs, ys], liczba*-1)
            #
            arcData.append([x, y])
        #
        # d_1 = sqrt( (x1 - arcData[0][0]) ** 2 + (y1 - arcData[0][1]) ** 2)
        # d_2 = sqrt( (x1 - arcData[-1][0]) ** 2 + (y1 - arcData[-1][1]) ** 2)
        # if d_1 < d_2:
            # arcData.reverse()
        #
        return arcData
        
    
    def sinus(self, angle):
        return float("%4.10f" % sin(radians(angle)))
        
    def cosinus(self, angle):
        return float("%4.10f" % cos(radians(angle)))
    
    def arcCenter(self, x1, y1, x2, y2, x3, y3):
        Xs = 0.5 * (x2 * x2 * y3 + y2 * y2 * y3 - x1 * x1 * y3 + x1 * x1 * y2 - y1 * y1 * y3 + y1 * y1 * y2 + y1 * x3 * x3 + y1 * y3 * y3 - y1 * x2 * x2 - y1 * y2 * y2 - y2 * x3 * x3 - y2 * y3 * y3) / (y1 * x3 - y1 * x2 - y2 * x3 - y3 * x1 + y3 * x2 + y2 * x1)
        Ys = 0.5 * (-x1 * x3 * x3 - x1 * y3 * y3 + x1 * x2 * x2 + x1 * y2 * y2 + x2 * x3 * x3 + x2 * y3 * y3 - x2 * x2 * x3 - y2 * y2 * x3 + x1 * x1 * x3 - x1 * x1 * x2 + y1 * y1 * x3 - y1 * y1 * x2) / (y1 * x3 - y1 * x2 - y2 * x3 - y3 * x1 + y3 * x2 + y2 * x1)
        
        return [Xs, Ys]
    
    def shiftPointOnLine(self, x1, y1, x2, y2, distance):
        if x2 - x1 == 0:  # vertical line
            
            
            x_T1 = x1
            y_T1 = y1 - distance
        else:
            a = (y2 - y1) / (x2 - x1)
            
            if a == 0:  # horizontal line
                x_T1 = x1 - distance
                y_T1 = y1
            else:
                alfa = atan(a)
                #alfa = tan(a)

                x_T1 = x1 - distance * cos(alfa)
                y_T1 = y1 - distance * sin(alfa)

        return [x_T1, y_T1]
    
    def rotateObject(self, angle, center):
        cK = self.cosinus(angle)
        sK = self.sinus(angle)
        
        x = center.x
        y = center.y
        z = center.z
        
        matrix = FreeCAD.Matrix( cK + x ** 2 * (1 - cK),  x * y * (1 - cK) - z * sK,   x * z * (1 - cK + y * sK),   0,
                          y * x * (1 - cK) + z * sK, cK + y ** 2 * (1 - cK),  y * z * (1 - cK) - x * sK,   0,
                          z * x * (1 - cK) - y * sK, z * y * (1 - cK) + x * sK, cK + z ** 2 * (1 - cK),  0)

        return matrix
        
        
    def obrocPunkt2(self, punkt, srodek, angle):
        sinKAT = self.sinus(angle)
        cosKAT = self.cosinus(angle)
        
        x1R = ((punkt[0] - srodek[0]) * cosKAT) - sinKAT * (punkt[1] - srodek[1]) + srodek[0]
        y1R = ((punkt[0] - srodek[0]) * sinKAT) + cosKAT * (punkt[1] - srodek[1]) + srodek[1]
        return [x1R, y1R]


    def obrocPunkt(self, punkt, srodek, angle):
        sinKAT = self.sinus(angle)
        cosKAT = self.cosinus(angle)
        
        x1R = (punkt[0] * cosKAT) - (punkt[1] * sinKAT) + srodek[0]
        y1R = (punkt[0] * sinKAT) + (punkt[1] * cosKAT) + srodek[1]
        return [x1R, y1R]
        
    def odbijWspolrzedne(self, punkt, srodek):
        ''' mirror '''
        return srodek + (srodek - punkt)
    
    def arc3point(self, stopAngle, startAngle, radius, cx, cy):
        d = stopAngle - startAngle
        offset = 0
        if d < 0.0:
            offset = 3.14
        x3 = cos(((startAngle + stopAngle) / 2.) + offset) * radius + cx
        y3 = -sin(((startAngle + stopAngle) / 2.) + offset) * radius + cy
        
        return [x3, y3]
        
    def arcRadius(self, x1, y1, x2, y2, angle):
        #dx = abs(x2 - x1)
        #dy = abs(y2 - y1)
        #d = sqrt(dx ** 2 + dy ** 2)  # distance between p1 and p2

        # point M - center point between p1 and p2
        Mx = (x1 + x2) / 2.
        My = (y1 + y2) / 2.
        
        # p1_M - distance between point p1 and M
        p1_M = sqrt((x1 - Mx) ** 2 + (y1 - My) ** 2)
        radius = float("%4.9f" % abs(p1_M / sin(radians(angle / 2.))))  # radius of searching circle - line C_p1
        
        return radius
    
    def arcAngles(self, x1, y1, x2, y2, Cx, Cy, angle):
        if angle > 0:
            startAngle = atan2(y1 - Cy, x1 - Cx)
            if startAngle < 0.:
                startAngle = 6.28 + startAngle
                    
            stopAngle = startAngle + radians(angle)  # STOP ANGLE
        else:
            startAngle = atan2(y2 - Cy, x2 - Cx)
            if startAngle < 0.:
                startAngle = 6.28 + startAngle

            stopAngle = startAngle + radians(abs(angle))  # STOP ANGLE
        #
        startAngle = float("%4.2f" % startAngle) - pi/2
        stopAngle = float("%4.2f" % stopAngle) - pi/2
        
        return [startAngle, stopAngle]
        
    #***************************************************************************
    #*   (c) Milos Koutny (milos.koutny@gmail.com) 2012                        *
    #*   Idf.py                                                                *
    #***************************************************************************
    def arcMidPoint(self, prev_vertex, vertex, angle):
        [x1, y1] = prev_vertex
        [x2, y2] = vertex
        
        angle = radians(angle / 2)
        basic_angle = atan2(y2 - y1, x2 - x1) - pi / 2
        shift = (1 - cos(angle)) * hypot(y2 - y1, x2 - x1) / 2 / sin(angle)
        midpoint = [(x2 + x1) / 2 + shift * cos(basic_angle), (y2 + y1) / 2 + shift * sin(basic_angle)]
        
        return midpoint
        
    def arcGetAngle(self, center, p1, p2):
        angle_1 = atan2((p1[1] - center[1]) * -1, (p1[0] - center[0])) * 180 / pi
        angle_2 = atan2((p2[1] - center[1]) * -1, (p2[0] - center[0])) * 180 / pi

        return angle_1 - angle_2
        
    def toQuaternion(self, heading, attitude, bank):  # rotation heading=arround Y, attitude =arround Z,  bank attitude =arround X
        ''' #***************************************************************************
            #*              (c) Milos Koutny (milos.koutny@gmail.com) 2010             *
            #***************************************************************************
            toQuaternion(heading, attitude,bank)->FreeCAD.Base.Rotation(Quternion)'''
        c1 = cos(heading / 2)
        s1 = sin(heading / 2)
        c2 = cos(attitude / 2)
        s2 = sin(attitude / 2)
        c3 = cos(bank / 2)
        s3 = sin(bank / 2)
        c1c2 = c1 * c2
        s1s2 = s1 * s2
        w = c1c2 * c3 - s1s2 * s3
        x = c1c2 * s3 + s1s2 * c3
        y = s1 * c2 * c3 + c1 * s2 * s3
        z = c1 * s2 * c3 - s1 * c2 * s3
        return FreeCAD.Base.Rotation(x, y, z, w)
        #return FreeCAD.Rotation(FreeCAD.Vector(x, y, z), w)
