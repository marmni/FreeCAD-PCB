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

from PySide import QtCore, QtGui
import codecs
import random
import FreeCAD
import os
from math import degrees
#
from PCBboard import getPCBsize, getHoles, getPCBheight
from command.PCBdxf import *
from command.PCBsvg import *
from command.PCBdrillingMapSymbols import drillingSymbols
from PCBfunctions import sketcherGetGeometry


exportList = {
    'dxf': {'name': 'Data exchange format (DXF)', 'class': 'dxf()', 'extension': 'dxf'},
    'svg': {'name': 'Scalable Vector Graphics (SVG)', 'class': 'svg()', 'extension': 'svg'},
}

def getBoardOutline():
    pcb = getPCBheight()
    if pcb[0]:  # board is available
        board = sketcherGetGeometry(pcb[2].Border)
        if board[0]:
            return board[1]
    
    return []


#***********************************************************************
#*                               GUI
#***********************************************************************
class exportDrillingMap_Gui(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        
        self.setWindowTitle(u"Create drilling map")
        self.setWindowIcon(QtGui.QIcon(":/data/img/drilling.svg"))
        #
        # Output file format
        self.formatList = QtGui.QComboBox()
        for i, j in exportList.items():
            self.formatList.addItem(j['name'], i)

        # Output directory
        self.pathToFile = QtGui.QLineEdit('')
        self.pathToFile.setReadOnly(True)
        
        zmianaSciezki = QtGui.QPushButton('...')
        zmianaSciezki.setToolTip(u'Change path')
        QtCore.QObject.connect(zmianaSciezki, QtCore.SIGNAL("pressed ()"), self.zmianaSciezkiF)
        # buttons
        saveButton = QtGui.QPushButton(u"Export")
        self.connect(saveButton, QtCore.SIGNAL("clicked ()"), self, QtCore.SLOT("accept()"))

        closeButton = QtGui.QPushButton(u"Close")
        self.connect(closeButton, QtCore.SIGNAL("clicked ()"), self, QtCore.SLOT('close()'))
        
        packageFooter = QtGui.QHBoxLayout()
        packageFooter.addStretch(10)
        packageFooter.addWidget(saveButton)
        packageFooter.addWidget(closeButton)
        packageFooter.setContentsMargins(10, 0, 10, 10)
        # header
        icon = QtGui.QLabel('')
        icon.setPixmap(QtGui.QPixmap(":/data/img/drilling1.svg"))
        
        headerWidget = QtGui.QWidget()
        headerWidget.setStyleSheet("padding: 10px; border-bottom: 1px solid #dcdcdc; background-color:#FFF;")
        headerLay = QtGui.QGridLayout(headerWidget)
        headerLay.addWidget(icon, 0, 0, 1, 1)
        headerLay.setContentsMargins(0, 0, 0, 0)
        ########
        centerLay = QtGui.QGridLayout()
        centerLay.addWidget(QtGui.QLabel(u'Output file format:'), 0, 0, 1, 1)
        centerLay.addWidget(self.formatList, 0, 1, 1, 2)
        centerLay.addWidget(QtGui.QLabel(u'Output directory:'), 1, 0, 1, 1)
        centerLay.addWidget(self.pathToFile, 1, 1, 1, 1)
        centerLay.addWidget(zmianaSciezki, 1, 2, 1, 1)
        centerLay.setContentsMargins(10, 20, 10, 20)

        mainLay = QtGui.QVBoxLayout(self)
        mainLay.addWidget(headerWidget)
        mainLay.addLayout(centerLay)
        mainLay.addStretch(10)
        mainLay.addLayout(packageFooter)
        mainLay.setContentsMargins(0, 0, 0, 0)
        #
        self.formatList.setCurrentIndex(self.formatList.findData('dxf'))
    
    def accept(self):
        export = exportDrillingMap()
        export.fileFormat = self.formatList.itemData(self.formatList.currentIndex())
        export.filePath = str(self.pathToFile.text())
        export.fileName = FreeCAD.ActiveDocument.Label
        export.export()
        #super(exportDrillingMap_Gui, self).accept()
        self.close()
        
    def zmianaSciezkiF(self):
        ''' change output file path '''
        fileName = QtGui.QFileDialog().getExistingDirectory(None, 'Output directory', QtCore.QDir.homePath(), QtGui.QFileDialog.ShowDirsOnly)
        
        if fileName:
            self.pathToFile.setText(fileName)


##***********************************************************************
##*                             CONSOLE
##***********************************************************************
class exportDrillingMap:
    def __init__(self):
        self.fileFormat = 'dxf'
        self.filePath = str(QtCore.QDir.homePath())  # def. home directory
        self.fileName = 'untitled'  # def. value
    
    def export(self):
        try:
            exportClass = eval(exportList[self.fileFormat]['class'])
            exportClass.fileName = self.fileName
            exportClass.filePath = self.filePath
            exportClass.holes = getHoles()
            exportClass.outline = getBoardOutline()
            [exportClass.pcbMin_X, exportClass.pcbMin_Y, exportClass.pcbXLength, exportClass.pcbYLength] = getPCBsize()
            exportClass.export()
        except Exception as e:
            FreeCAD.Console.PrintWarning("{0} \n".format(e))
        else:
            FreeCAD.Console.PrintWarning("File has been successfully exported\n")
            


##***********************************************************************
##*                             FORMATS
##***********************************************************************
def randomValue(maximum):
    return random.randint(0, maximum)

class drillMap:
    def __init__(self):
        self.fileName = ''
        self.filePath = ''
        self.holes = {}
        self.outline = []
        self.pcbMin_X = 0
        self.pcbMin_Y = 0
        self.pcbXLength = 1
        self.pcbYLength = 1
        self.blockedChars = []
    
    def randomChar(self):
        if len(self.blockedChars) == len(drillingSymbols):
            self.blockedChars = []
        
        charNum = randomValue(len(drillingSymbols) - 1)
        if charNum in self.blockedChars:
            while charNum in self.blockedChars:
                charNum = randomValue(len(drillingSymbols) - 1)

        self.blockedChars.append(charNum)
        return drillingSymbols[charNum]


class svg(drillMap):
    def __init__(self):
        drillMap.__init__(self)
    
    def writeHeader(self, files):
        files.write('''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg
    xmlns="http://www.w3.org/2000/svg"
    version="1.1"
    width="{0}"
    height="{1}"
>'''.format(self.pcbXLength+2, self.pcbYLength+2))
    
    def writeFooter(self, files):
        files.write('''
</svg>''')

    def writeHoles(self, files):
        # table parameters
        lineHeight = 1
        lineNumber = 2
        
        # row line
        line = SVG_Line()
        line.p1 = [self.pcbMin_X, self.pcbMin_Y - 0.4, 0]
        line.p2 = [self.pcbMin_X + 13, self.pcbMin_Y - 0.4, 0]
        line.color = [0, 0, 0]
        self.addCode(files, line)
        #
        txt = SVG_Text('SYM')
        txt.x = self.pcbMin_X + 0.6
        txt.y = self.pcbMin_Y - 0.6
        txt.fontSize = 0.5
        self.addCode(files, txt)
        
        txt = SVG_Text('SIZE')
        txt.x = self.pcbMin_X + 2.1
        txt.y = self.pcbMin_Y - 0.6
        txt.fontSize = 0.5
        self.addCode(files, txt)
        
        txt = SVG_Text('QTY')
        txt.x = self.pcbMin_X + 4.3
        txt.y = self.pcbMin_Y - 0.6
        txt.fontSize = 0.5
        self.addCode(files, txt)
        
        txt = SVG_Text('PLATED')
        txt.x = self.pcbMin_X + 6.5
        txt.y = self.pcbMin_Y - 0.6
        txt.fontSize = 0.5
        self.addCode(files, txt)
        
        txt = SVG_Text('RANGE')
        txt.x = self.pcbMin_X + 9.7
        txt.y = self.pcbMin_Y - 0.6
        txt.fontSize = 0.5
        self.addCode(files, txt)
        # row line
        line = SVG_Line()
        line.p1 = [self.pcbMin_X, self.pcbMin_Y - 0.3 - 1 * lineHeight, 0]
        line.p2 = [self.pcbMin_X + 13, self.pcbMin_Y - 0.3 - 1 * lineHeight, 0]
        line.color = [0, 0, 0]
        self.addCode(files, line)
        #
        #line = 1.5
        nr = 1
        data = ''
        
        for i in range(len(self.holes.keys())):
            key = list(self.holes)
            
            char = self.randomChar()
            layer = 'T{0}'.format(i + 1)
            color_R = hex(randomValue(254)).split('x')[1]
            color_G = hex(randomValue(254)).split('x')[1]
            color_B = hex(randomValue(254)).split('x')[1]
            
            self.addCode(files, '\n\t<g id="{0}" inkscape:groupmode="layer" inkscape:label="{0}">'.format(layer))
            header = False
            for j in self.holes[key[i]]:
                self.addCode(files, '\n\t\t<g>')
                for k in char:
                    x = self.correctX(j[0])
                    y = self.correctY(j[1])
                    r = key[i]
                    
                    if k[0] == 'l':
                        p1 = eval(k[1])
                        p2 = eval(k[2])
                        
                        line = SVG_Line()
                        line.p1 = [p1[0], p1[1], 0]
                        line.p2 = [p2[0], p2[1], 0]
                        line.color = [color_R, color_G, color_B]
                        self.addCode(files, line)
                        # annotation under board
                        if not header:
                            x = self.pcbMin_X + 1.2
                            y = self.pcbMin_Y + 0.2 - lineNumber * lineHeight
                            r = 0.3
                            
                            p1 = eval(k[1])
                            p2 = eval(k[2])
                            
                            line = SVG_Line()
                            line.p1 = [p1[0], p1[1], 0]
                            line.p2 = [p2[0], p2[1], 0]
                            line.color = [color_R, color_G, color_B]
                            self.addCode(files, line)
                    elif k[0] == 'c':
                        sx = eval(k[1])
                        sy = eval(k[2])
                        nr = eval(k[3])
                        
                        line = SVG_Circle()
                        line.x = sx
                        line.y = sy
                        line.r = nr
                        line.color = [color_R, color_G, color_B]
                        self.addCode(files, line)
                        # annotation under board
                        if not header:
                            x = self.pcbMin_X + 1.2
                            y = self.pcbMin_Y + 0.2 - lineNumber * lineHeight
                            r = 0.3
                            
                            sx = eval(k[1])
                            sy = eval(k[2])
                            nr = eval(k[3])
                            
                            line = SVG_Circle()
                            line.x = sx
                            line.y = sy
                            line.r = nr
                            line.color = [color_R, color_G, color_B]
                            self.addCode(files, line)
                header = True
                self.addCode(files, '\n\t\t</g>')
            self.addCode(files, '\n\t</g>')
            # add annotation under board
            #txt = SVG_Text(str('%.2f' % (key[i] * 2)))
            txt = SVG_Text(str(key[i] * 2))
            txt.x = self.pcbMin_X + 2.1
            txt.y = self.pcbMin_Y + 0.4 - lineNumber * lineHeight
            txt.fontSize = 0.5
            self.addCode(files, txt)
            
            txt = SVG_Text(str(len(self.holes[key[i]])))
            txt.x = self.pcbMin_X + 4.3
            txt.y = self.pcbMin_Y + 0.4 - lineNumber * lineHeight
            txt.fontSize = 0.5
            self.addCode(files, txt)
            # row line
            line = SVG_Line()
            line.p1 = [self.pcbMin_X, self.pcbMin_Y - 0.3 - lineNumber * lineHeight, 0]
            line.p2 = [self.pcbMin_X + 13, self.pcbMin_Y - 0.3 - lineNumber * lineHeight, 0]
            self.addCode(files, line)
            # columns lines
            line = SVG_Line()
            line.p1 = [self.pcbMin_X, self.pcbMin_Y - 0.4, 0]
            line.p2 = [self.pcbMin_X, self.pcbMin_Y - 0.3 - lineNumber * lineHeight, 0]
            self.addCode(files, line)
            
            line = SVG_Line()
            line.p1 = [self.pcbMin_X + 13, self.pcbMin_Y - 0.4, 0]
            line.p2 = [self.pcbMin_X + 13, self.pcbMin_Y - 0.3 - lineNumber * lineHeight, 0]
            self.addCode(files, line)
            #
            lineNumber += 1
            #txt = SVG_Text('T{0} {1}mm x {2}'.format(i + 1, self.holes.keys()[i], len(self.holes[self.holes.keys()[i]])))
            #txt.x = 2
            #txt.y = self.pcbYLength + nr * line + 0.4
            #txt.fontSize = 1
            #txt.color = [255, 255, 0]
            #data = data + str(txt)
            ##
            #nr += 1
        #
        #self.addCode(files, '\n\t<g id="{0}" inkscape:groupmode="layer" inkscape:label="{0}">'.format('Info'))
        #self.addCode(files, data)
        #self.addCode(files, '\n\t</g>')
    
    def correctY(self, value):
        return value * -1 + self.pcbMin_Y + self.pcbYLength + 1
    
    def correctX(self, value):
        return value - self.pcbMin_X + 1
    
    def writeBoardOutline(self, files):
        layerColor = [0, 0 ,0]
        
        self.addCode(files, '\n\t<g id="{0}" inkscape:groupmode="layer" inkscape:label="{0}">'.format('Border outline'))
        for i in self.outline:
            if i['type'] == 'line':
                line = SVG_Line()
                line.p1 = [self.correctX(i['x1']), self.correctY(i['y1']), 0]
                line.p2 = [self.correctX(i['x2']), self.correctY(i['y2']), 0]
                line.color = layerColor
                
                self.addCode(files, line)
            elif i['type'] == 'circle':
                circle = SVG_Circle()
                circle.r = i['r']
                circle.x = self.correctX(i['x'])
                circle.y = self.correctY(i['y'])
                circle.color = layerColor
                
                self.addCode(files, circle)
            elif i['type'] == 'arc':
                arc = SVG_Arc()
                arc.p1 = [self.correctX(i['x1']), self.correctY(i['y1']), 0]
                arc.p2 = [self.correctX(i['x2']), self.correctY(i['y2']), 0]
                arc.color = layerColor
                arc.r = i['r']
                
                if i['angle'] > 0:
                    arc.direction = 0
                
                if i['angle'] > 180:
                    arc.side = 1
                
                self.addCode(files, arc)
        #
        self.addCode(files, '\n\t</g>')
    
    def addCode(self, files, data):
        files.write('{0}'.format(data))
        
    def export(self):
        fileName = os.path.join(self.filePath, self.fileName)
        if not fileName.endswith('svg'):
            fileName = fileName + '.svg'
        
        files = codecs.open(fileName, "w", "utf-8")
        #########
        self.writeHeader(files)
        self.writeBoardOutline(files)
        self.writeHoles(files)
        self.writeFooter(files)
        #########
        files.close()


class dxf(drillMap):
    def __init__(self):
        drillMap.__init__(self)
    
    def writeHeader(self, files):
        self.addCode(files, [[999, 'FreeCAD-PCB']])
        self.startSection(files, 'HEADER')  # start header section
        self.addCode(files, [[9, '$ACADVER'], [1, 'AC1012']])  # The AutoCAD drawing database version number: AC1012 = R13
        self.addCode(files, [[9, '$INSBASE'], [10, 0.0], [20, 0.0], [30, 0.0]])  # Insertion base set by BASE command (in WCS)
        self.addCode(files, [[9, '$INSUNITS'], [70, 4]])  # Default drawing units for AutoCAD DesignCenter blocks: 4 = Millimeters;
        self.addCode(files, [[9, '$ATTMODE'], [70, 2]])  # Attribute visibility: 2 = All
        self.endSection(files)  # end section
    
    def writeFooter(self, files):
        self.addCode(files, [[0, 'EOF']])  # file end
    
    def addCode(self, files, data):
        for i in data:
            files.write('{0:>3}\n{1}\n'.format(i[0], i[1]))
    
    def startSection(self, files, name):
        self.addCode(files, [[0, 'SECTION'], [2, name]])  # start header section
        
    def endSection(self, files):
        self.addCode(files, [[0, 'ENDSEC']])  # end section
        
    def writeBoardOutline(self, files):
        layerName = 'Border outline'
        layerColor = 7
        
        for i in self.outline:
            if i['type'] == 'line':
                line = DXF_Line(layerName)
                line.p1 = [i['x1'], i['y1'], 0]
                line.p2 = [i['x2'], i['y2'], 0]
                line.color = layerColor
                
                self.addCode(files, eval(str(line)))
            elif i['type'] == 'circle':
                circle = DXF_Circle(layerName)
                circle.r = i['r']
                circle.x = i['x']
                circle.y = i['y']
                circle.color = layerColor
                
                self.addCode(files, eval(str(circle)))
            elif i['type'] == 'arc':
                arc = DXF_Arc(layerName)
                arc.r = i['r']
                arc.x = i['x']
                arc.y = i['y']
                arc.startAngle = i['startAngle']
                arc.stopAngle = i['stopAngle']
                arc.color = layerColor
                
                self.addCode(files, eval(str(arc)))
    
    def writeHoles(self, files):
        # table parameters
        lineHeight = 1
        lineNumber = 2
        # row line
        line = DXF_Line(1)
        line.p1 = [self.pcbMin_X, self.pcbMin_Y - 0.3, 0]
        line.p2 = [self.pcbMin_X + 19, self.pcbMin_Y - 0.3, 0]
        line.color = 2
        line.layer = "Info"
        self.addCode(files, eval(str(line)))
        header =  '{0}{1}{2}{3}{4}'.format('SYM'.center(5, ' '), 'SIZE'.center(8, ' '), 'QTY'.center(7, ' '), ' PLATED ', 'RANGE'.center(9, ' '))
        txt = DXF_Text("Info", header)
        txt.p = [self.pcbMin_X, self.pcbMin_Y - 1, 0.0]
        txt.height = 0.5
        self.addCode(files, eval(str(txt)))
        # row line
        line = DXF_Line(1)
        line.p1 = [self.pcbMin_X, self.pcbMin_Y - 0.3 - 1 * lineHeight, 0]
        line.p2 = [self.pcbMin_X + 19, self.pcbMin_Y - 0.3 - 1 * lineHeight, 0]
        line.color = 2
        line.layer = "Info"
        self.addCode(files, eval(str(line)))
        #
        num = 1
        for i in range(len(self.holes.keys())):
            key = list(self.holes)
            
            color = randomValue(254)
            char = self.randomChar()
            #layer = 'T{0}_{1}mm'.format(i + 1, self.holes.keys()[i])
            layer = 'T{0}'.format(i + 1)
            #
            header = False
            
            for j in self.holes[key[i]]:
                for k in char:
                    x = j[0]
                    y = j[1]
                    r = key[i]
                    
                    if k[0] == 'l':
                        p1 = eval(k[1])
                        p2 = eval(k[2])
                        
                        line = DXF_Line(1)
                        line.p1 = [p1[0], p1[1], 0]
                        line.p2 = [p2[0], p2[1], 0]
                        
                        line.color = color
                        line.layer = layer
                        self.addCode(files, eval(str(line)))
                        # annotation under board
                        if not header:
                            x = self.pcbMin_X + 1.2
                            y = self.pcbMin_Y + 0.2 - lineNumber * lineHeight
                            r = 0.4
                            
                            p1 = eval(k[1])
                            p2 = eval(k[2])
                            
                            line = DXF_Line(1)
                            line.p1 = [p1[0], p1[1], 0]
                            line.p2 = [p2[0], p2[1], 0]
                            
                            line.color = color
                            line.layer = "Info"
                            self.addCode(files, eval(str(line)))
                    elif k[0] == 'c':
                        sx = eval(k[1])
                        sy = eval(k[2])
                        nr = eval(k[3])
                        
                        line = DXF_Circle(1)
                        line.x = sx
                        line.y = sy
                        line.r = nr
                        
                        line.color = color
                        line.layer = layer
                        self.addCode(files, eval(str(line)))
                        # annotation under board
                        if not header:
                            x = self.pcbMin_X + 1.2
                            y = self.pcbMin_Y + 0.2 - lineNumber * lineHeight
                            r = 0.4
                            
                            sx = eval(k[1])
                            sy = eval(k[2])
                            nr = eval(k[3])
                            
                            line = DXF_Circle(1)
                            line.x = sx
                            line.y = sy
                            line.r = nr
                            
                            line.color = color
                            line.layer = "Info"
                            self.addCode(files, eval(str(line)))
            
            header = True
            # add annotation under board
            txt = DXF_Text("Info", str(key[i] * 2))
            txt.p = [self.pcbMin_X + 3.5, self.pcbMin_Y - lineNumber * lineHeight, 0.0]
            txt.height = 0.5
            self.addCode(files, eval(str(txt)))
            
            txt = DXF_Text("Info", str(len(self.holes[key[i]])))
            txt.p = [self.pcbMin_X + 7.3, self.pcbMin_Y - lineNumber * lineHeight, 0.0]
            txt.height = 0.5
            self.addCode(files, eval(str(txt)))
            # row line
            line = DXF_Line(1)
            line.p1 = [self.pcbMin_X, self.pcbMin_Y - 0.3 - lineNumber * lineHeight, 0]
            line.p2 = [self.pcbMin_X + 19, self.pcbMin_Y - 0.3 - lineNumber * lineHeight, 0]
            line.color = 2
            line.layer = "Info"
            self.addCode(files, eval(str(line)))
            # columns lines
            line = DXF_Line(1)
            line.p1 = [self.pcbMin_X, self.pcbMin_Y - 0.3, 0]
            line.p2 = [self.pcbMin_X, self.pcbMin_Y - 0.3 - lineNumber * lineHeight, 0]
            line.color = 2
            line.layer = "Info"
            self.addCode(files, eval(str(line)))
            
            line = DXF_Line(1)
            line.p1 = [self.pcbMin_X + 19, self.pcbMin_Y - 0.3, 0]
            line.p2 = [self.pcbMin_X + 19, self.pcbMin_Y - 0.3 - lineNumber * lineHeight, 0]
            line.color = 2
            line.layer = "Info"
            self.addCode(files, eval(str(line)))
            #
            lineNumber += 1
            num += 1
            
    def export(self):
        fileName = os.path.join(self.filePath, self.fileName)
        if not fileName.endswith('dxf'):
            fileName = fileName + '.dxf'
        
        files = codecs.open(fileName, "w", "utf-8")
        #########
        self.writeHeader(files)
        #
        self.startSection(files, 'ENTITIES')  # start entities section
        self.writeBoardOutline(files)
        self.writeHoles(files)
        self.endSection(files)  # end section
        #
        self.writeFooter(files)
        #########
        files.close()
