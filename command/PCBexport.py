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
import os
import shutil
import codecs
import Part
from math import sin, cos, degrees
from xml.dom import minidom
from PySide import QtCore, QtGui
import json
import builtins
from collections import OrderedDict
import datetime
#
from PCBconf import supSoftware
from PCBfunctions import mathFunctions
from PCBboard import getBoardOutline, getHoles, getDimensions, getAnnotations, getPCBheight, getPCBsize, getGlue

__currentPath__ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

#***********************************************************************
#*                               GUI
#***********************************************************************
class exportPCB_Gui(QtGui.QWizard):
    def __init__(self, parent=None):
        QtGui.QWizard.__init__(self, parent)

        self.setWindowTitle(u"Export PCB")
        self.setPixmap(QtGui.QWizard.LogoPixmap, QtGui.QPixmap(":/data/img/exportModel.png"))
        self.exportType = eagle()
        ###
        self.addPage(self.formatPliku())
        self.addPage(self.exportUstawienia())
        #
        self.listaFormatow.setCurrentRow(0)
        self.button(QtGui.QWizard.FinishButton).clicked.connect(self.export)

    def export(self):
        if not os.path.exists(os.path.dirname(self.pathToFile.text())):
            FreeCAD.Console.PrintWarning('The specified path does not exist\n')
            return
        ####
        FreeCAD.Console.PrintWarning('Exporting file\n')
        try:
            self.exportType.addHoles = self.addHoles.isChecked()
            self.exportType.addAnnotations = self.addAnnotations.isChecked()
            self.exportType.addDimensions = self.addDimensions.isChecked()
            self.exportType.addGluePaths = self.addGluePaths.isChecked()
            self.exportType.export(str(self.pathToFile.text()))
            
            FreeCAD.Console.PrintWarning('End \n')
        except Exception as e:
            FreeCAD.Console.PrintWarning(u"Error: {0} \n".format(e))
            FreeCAD.Console.PrintWarning('STOP \n')
    
    def zmianaProgramu(self):
        program = str(self.listaFormatow.currentItem().data(QtCore.Qt.UserRole))
        
        self.exportType = eval(supSoftware[program]['exportClass'])
        self.nazwaProgramu.setText(u'<b>Progam:</b> ' + supSoftware[program]['name'])
        self.formatPliku.setText(u'<b>Format:</b> ' + supSoftware[program]['format'])
        self.ikonaProgramu.setPixmap(QtGui.QPixmap(supSoftware[program]['icon']))
        self.pathToFile.setText(QtCore.QDir.homePath() + '/untitled.' + supSoftware[program]['format'].split('.')[1])
        #
        freecadSettings = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB")
        
        self.addAnnotations.setCheckState(QtCore.Qt.Unchecked)
        self.addHoles.setCheckState(QtCore.Qt.Unchecked)
        self.addDimensions.setCheckState(QtCore.Qt.Unchecked)
        
        if 'dim' in supSoftware[self.exportType.programName]['exportLayers']:
            if freecadSettings.GetBool("exportDim_{0}".format(self.exportType.programName), False):
                value = QtCore.Qt.Checked
            else:
                value = QtCore.Qt.Unchecked
            
            self.addDimensions.setCheckState(value)
            self.addDimensions.setDisabled(False)
        else:
            self.addDimensions.setDisabled(True)
            self.addDimensions.setCheckState(QtCore.Qt.Unchecked)

        if 'hol' in supSoftware[self.exportType.programName]['exportLayers']:
            if freecadSettings.GetBool("exportHol_{0}".format(self.exportType.programName), False):
                value = QtCore.Qt.Checked
            else:
                value = QtCore.Qt.Unchecked
            
            self.addHoles.setCheckState(value)
            self.addHoles.setDisabled(False)
        else:
            self.addHoles.setDisabled(True)
            self.addHoles.setCheckState(QtCore.Qt.Unchecked)

        if 'anno' in supSoftware[self.exportType.programName]['exportLayers']:
            if freecadSettings.GetBool("exportAnno_{0}".format(self.exportType.programName), False):
                value = QtCore.Qt.Checked
            else:
                value = QtCore.Qt.Unchecked
            
            self.addAnnotations.setCheckState(value)
            self.addAnnotations.setDisabled(False)
        else:
            self.addAnnotations.setDisabled(True)
            self.addAnnotations.setCheckState(QtCore.Qt.Unchecked)
            
        if 'glue' in supSoftware[self.exportType.programName]['exportLayers']:
            if freecadSettings.GetBool("exportGlue_{0}".format(self.exportType.programName), False):
                value = QtCore.Qt.Checked
            else:
                value = QtCore.Qt.Unchecked
            
            self.addGluePaths.setCheckState(value)
            self.addGluePaths.setDisabled(False)
        else:
            self.addGluePaths.setDisabled(True)
            self.addGluePaths.setCheckState(QtCore.Qt.Unchecked)
        
    def formatPliku(self):
        page = QtGui.QWizardPage()
        page.setSubTitle(u"<span style='font-weight:bold;font-size:13px;'>File format</span>")
        #
        self.nazwaProgramu = QtGui.QLabel()
        self.formatPliku = QtGui.QLabel()

        self.ikonaProgramu = QtGui.QLabel()
        self.ikonaProgramu.setFixedSize(120, 120)
        self.ikonaProgramu.setAlignment(QtCore.Qt.AlignCenter)
        #
        self.listaFormatow = QtGui.QListWidget()
        for i, j in supSoftware.items():
            if j['export']:
                a = QtGui.QListWidgetItem(j['name'])
                a.setData(QtCore.Qt.UserRole, i)
            
                self.listaFormatow.addItem(a)
        QtCore.QObject.connect(self.listaFormatow, QtCore.SIGNAL("currentRowChanged (int)"), self.zmianaProgramu)
        #
        lay = QtGui.QGridLayout(page)
        lay.addWidget(self.listaFormatow, 0, 0, 4, 1)
        lay.addWidget(self.ikonaProgramu, 0, 1, 1, 1, QtCore.Qt.AlignCenter)
        lay.addWidget(self.nazwaProgramu, 1, 1, 1, 1)
        lay.addWidget(self.formatPliku, 2, 1, 1, 1)
        lay.setHorizontalSpacing(20)
        lay.setColumnMinimumWidth(1, 140)
        return page

    def exportUstawienia(self):
        page = QtGui.QWizardPage()
        page.setSubTitle(u"<span style='font-weight:bold;font-size:13px;'>Settings</span>")
        #
        self.pathToFile = QtGui.QLineEdit('')
        #self.pathToFile.setReadOnly(True)
        #
        zmianaSciezki = QtGui.QPushButton('...')
        zmianaSciezki.setToolTip(u'Change path')
        QtCore.QObject.connect(zmianaSciezki, QtCore.SIGNAL("pressed ()"), self.zmianaSciezkiF)
        #
        self.addHoles = QtGui.QCheckBox(u'Add holes')
        self.addDimensions = QtGui.QCheckBox(u'Add dimensions')
        self.addAnnotations = QtGui.QCheckBox(u'Add annotations')
        self.addGluePaths = QtGui.QCheckBox(u'Export glue paths')
        #
        lay = QtGui.QGridLayout(page)
        lay.addWidget(QtGui.QLabel(u'Path: '), 0, 0, 1, 1)
        lay.addWidget(self.pathToFile, 0, 1, 1, 1)
        lay.addWidget(zmianaSciezki, 0, 2, 1, 1)
        lay.addItem(QtGui.QSpacerItem(1, 10), 1, 0, 1, 3)
        lay.addWidget(self.addHoles, 2, 0, 1, 3)
        lay.addWidget(self.addDimensions, 3, 0, 1, 3)
        lay.addWidget(self.addAnnotations, 4, 0, 1, 3)
        lay.addWidget(self.addGluePaths, 5, 0, 1, 3)
        lay.setColumnStretch(1, 6)
        return page
        
    def zmianaSciezkiF(self):
        fileName = QtGui.QFileDialog().getSaveFileName(None, 'Save as', QtCore.QDir.homePath(), supSoftware[self.exportType.programName]['format'])
        if fileName[0]:
            fileName = fileName[0]
            program = str(self.listaFormatow.currentItem().data(QtCore.Qt.UserRole))
                
            if not fileName.endswith('.{0}'.format(supSoftware[program]['format'].split('.')[1])):
                fileName += '.{0}'.format(supSoftware[program]['format'].split('.')[1])
                
            self.pathToFile.setText(fileName)


#***********************************************************************
#*                             CONSOLE
#***********************************************************************
class exportPCB:
    def __init__(self):
        self.addHoles = False
        self.addAnnotations = False
        self.addDimensions = False
    
    def fileExtension(self, path):
        extension = supSoftware[self.programName]['format'].split('.')[1]
        if not path.endswith(extension):
            path += '.{0}'.format(extension)
        
        return path
        
    def precyzjaLiczb(self, value):
        return "%.2f" % float(value)
    
    def getHoles(self):
        doc = FreeCAD.activeDocument()
        data = []
        
        for j in doc.Objects:
            if hasattr(j, "Proxy") and hasattr(j.Proxy, "Type") and j.Proxy.Type == "PCBboard":
                try:
                    for k in range(len(j.Holes.Geometry)):
                        if j.Holes.Geometry[k].Construction:
                            continue
                        
                        data.append([
                            j.Holes.Geometry[k].Radius,
                            j.Holes.Geometry[k].Center.x, 
                            j.Holes.Geometry[k].Center.y
                        ])
                    break
                except Exception as e:
                    FreeCAD.Console.PrintWarning(str(e) + "\n")
        
        return data


class razen(exportPCB):
    ''' Export PCB to *.rzp - Razen '''
    def __init__(self, parent=None):
        exportPCB.__init__(self)
        
        self.dummyPath = __currentPath__ + "/save/untitled"
        self.programName = 'razen'
    
    def export(self, fileName):
        '''export(filePath): save board to pcb file
            filePath -> strig
            filePath = path/fileName.rzp'''
        fileName = self.fileExtension(fileName)
        
        [path, project] = os.path.split(fileName)
        [projectName, extension] = project.split('.')
        
        self.setProject(os.path.join(path, projectName))
        #
        self.exportBoard(getBoardOutline())
        if self.addHoles:
            self.exportHoles(self.getHoles())
        if self.addAnnotations:
            self.exportAnnotations(getAnnotations())
        #
        with open(os.path.join(os.path.join(path, projectName), "layout.json"), 'w') as outfile:
            json.dump(self.dummyFile, outfile)
    
    def setProject(self, projectPath):
        shutil.copytree(self.dummyPath, projectPath)
        self.dummyFile = json.load(codecs.open(os.path.join(projectPath, "layout.json"), "r"))
    
    def setUnit(self, value):
        return int(value * 10000)
    
    def exportAnnotations(self, annotations):
        for i in annotations:
            x = self.setUnit(i[0])
            y = self.setUnit(i[1]) * (-1)
            size = i[2]
            annotation = i[4]
            align = i[5]
            rot = i[6] * (-1)
            mirror = i[7]
            
            if i[7] == 'Global Y axis':
                mirror = True
            else:
                mirror = False
            
            spin = i[8]
            
            if i[3] == 'TOP':
                layer = 25
            else:
                layer = 26
            
            #
            self.dummyFile["elts"].append({"layer": layer, "angle": rot, "_t": "Text", "pos": [x, y], "value": annotation, "charspace": 200, "width": 0, "mirror": mirror, "font": "vector", "size": size})
    
    def exportHoles(self, holes):
        for i in holes:
            r = self.setUnit(i[0] * 2)
            x = self.setUnit(i[1])
            y = self.setUnit(i[2]) * (-1)
            
            self.dummyFile["elts"].append({"diameter": r, "_t": "Drill", "pos": [x, y]})
    
    def exportBoard(self, board):
        layer = ''
        
        for i in board:
            if i[0] == 'line':
                self.addLine(i[1:], 20, 0)
            elif i[0] == 'arc':
                self.addArc(i[1:], 20, 0)
            elif i[0] == 'circle':
                self.addCircle(i[1:], 20, 0)
        
    def addCircle(self, circle, layer, width):
        r = self.setUnit(circle[0] / 2.0)
        x = self.setUnit(circle[1])
        y = self.setUnit(circle[2]) * (-1)
        
        self.dummyFile["elts"].append({"layer": layer, "name": "#n157", "_t": "Arc", "pos": [x, y], "ofsb": [x + r, 0], "width": width, "ofsa": [x + r, 0]})

    def addLine(self, line, layer, width):
        x1 = self.setUnit(line[0])
        y1 = self.setUnit(line[1]) * (-1)
        x2 = self.setUnit(line[2])
        y2 = self.setUnit(line[3]) * (-1)
        
        self.dummyFile["elts"].append({"layer": layer, "name": "line", "_t": "Segment", "ptb": [x2, y2], "pta": [x1, y1], "width": width})
    
    def addArc(self, arc, layer, width):
        math = mathFunctions()
        
        r = self.setUnit(arc[0])
        xs = arc[1]
        ys = arc[2] * (-1)
        sA = degrees(arc[3]) * (-1)
        eA = degrees(arc[4]) * (-1)
        
        [x1, y1] = math.obrocPunkt2([xs + r, ys], [xs, ys], sA)
        [x2, y2] = math.obrocPunkt2([xs + r, ys], [xs, ys], eA)
        xs = self.setUnit(xs)
        ys = self.setUnit(ys)
        
        self.dummyFile["elts"].append({"layer": layer, "name": "#n157", "_t": "Arc", "pos": [xs, ys], "ofsb": [x1, y1], "width": width, "ofsa": [x2, y2]})


class geda(exportPCB):
    ''' Export PCB to *.pcb - gEDA '''
    def __init__(self, parent=None):
        exportPCB.__init__(self)
        
        self.dummyFile = codecs.open(__currentPath__ + "/save/untitled.pcb", "r").read()
        self.programName = 'geda'
        
        self.minX = 0
        self.maxY = 0
        
    def shiftPCB(self):
        try:
            board = FreeCAD.ActiveDocument.Board
            
            self.minX = float("%.3f" % board.Shape.BoundBox.XMin)
            self.maxY = float("%.3f" % board.Shape.BoundBox.YMax)
        except:
            pass
    
    def setHeader(self):
        [xmin, ymin, width, height] = getPCBsize()
        
        self.dummyFile = self.dummyFile.replace('{pcbX}', '{0}mm'.format(width))
        self.dummyFile = self.dummyFile.replace('{pcbY}', '{0}mm'.format(height))
    
    def export(self, fileName):
        '''export(filePath): save board to pcb file
            filePath -> strig
            filePath = path/fileName.pcb'''
        fileName = self.fileExtension(fileName)
        self.setHeader()
        self.shiftPCB()
        #
        self.exportBoard(getBoardOutline())
        if self.addHoles:
            minDiameter = self.exportHoles(self.getHoles())
            self.dummyFile = self.dummyFile.replace('{minDrillDiameter}', str(minDiameter))
        else:
            self.dummyFile = self.dummyFile.replace('{minDrillDiameter}', '10')
            self.dummyFile = self.dummyFile.replace('{holes}', '')
        
        if self.addAnnotations:
            self.exportAnnotations(getAnnotations())
        else:
            self.dummyFile = self.dummyFile.replace('{text}', '')
        #
        files = codecs.open(fileName, "w", "utf-8")
        files.write(self.dummyFile)
        files.close()
    
    def exportAnnotations(self, annotations):
        layer = ''
        
        for i in annotations:
            x = self.shiftXValue(i[0])
            y = self.shiftYValue(i[1])
            size = i[2] * 100
            txt = i[4]
            rot = degrees(i[6])
            #
            layer += '  Text[{0}mm {1}mm {2} {3} "{4}" "clearline"]\n'.format(x, y, rot, size, txt)
        #
        self.dummyFile = self.dummyFile.replace('{text}', layer)
    
    def exportHoles(self, holes):
        layer = ''
        minDiameter = 0
        
        for i in holes:
            x = self.shiftXValue(i[1])
            y = self.shiftYValue(i[2])
            r = i[0] * 2
            thickness = r + 0.508
            clearance = 0.508
            mask = r + 0.254
            if r > minDiameter:
                minDiameter = r
            
            layer += '  Via[{0}mm {1}mm {3}mm {4}mm {5}mm {2}mm "" "hole"]\n'.format(x, y, r, thickness, clearance, mask)
        #
        self.dummyFile = self.dummyFile.replace('{holes}', layer)
        return minDiameter

    def exportBoard(self, board):
        layer = ''
        
        for i in board:
            if i[0] == 'line':
                layer += self.addLine(i[1:], '10.00mil')
            elif i[0] == 'arc':
                layer += self.addArc(i[1:], '10.00mil')
            elif i[0] == 'circle':
                layer += self.addCircle(i[1:], '10.00mil')
        
        self.dummyFile = self.dummyFile.replace('{outline}', layer)
    
    def addCircle(self, circle, width):
        return self.addArc([circle[0], circle[1], circle[2], 0, 6.28], width)
    
    def addLine(self, line, width):
        x1 = self.shiftXValue(line[0])
        y1 = self.shiftYValue(line[1])
        x2 = self.shiftXValue(line[2])
        y2 = self.shiftYValue(line[3])
        
        return '    Line[{0}mm {1}mm {2}mm {3}mm {4} 20.00mil "clearline"]\n'.format(x1, y1, x2, y2, width)
    
    def addArc(self, arc, width):
        r = arc[0]
        x = self.shiftXValue(arc[1])
        y = self.shiftYValue(arc[2])
        startAngle = float("%.0f" % degrees(arc[3])) - 180
        stopAngle = float("%.0f" % degrees(arc[4])) - startAngle - 180
        
        return '    Arc[{0}mm {1}mm {2}mm {2}mm {3} 20.00mil {4} {5} "clearline"]\n'.format(x, y, r, width, startAngle, stopAngle)
    
    def shiftXValue(self, value):
        return float("%.4f" % (value - self.minX))
    
    def shiftYValue(self, value):
        return float("%.4f" % ((value - self.maxY) * (-1)))


class kicad(exportPCB):
    ''' Export PCB to *.kicad_pcb - KiCad '''
    def __init__(self, parent=None):
        exportPCB.__init__(self)
        
        self.dummyFile = codecs.open(__currentPath__ + "/save/untitled.kicad_pcb", "r").readlines()
        self.programName = 'kicad'
        
        self.pcbElem = []
        self.minX = 0
        self.minY = 0
    
    def export(self, fileName):
        '''export(filePath): save board to kicad_pcb file
            filePath -> strig
            filePath = path/fileName.kicad_pcb'''
        fileName = self.fileExtension(fileName)
        #
        self.exportBoard(getBoardOutline())
        if self.addHoles:
            self.exportHoles(self.getHoles())
        if self.addAnnotations:
            self.exportAnnotations(getAnnotations())
        if self.addDimensions:
            self.exportDimensions(getDimensions())
        if self.addGluePaths:
            self.exportGlue(getGlue())
        #
        self.przesunPCB()
        files = codecs.open(fileName, "w", "utf-8")
        files.write("".join(self.dummyFile))
        files.close()
    
    def przesunPCB(self):
        for i in self.pcbElem:
            if i[0] == 'gr_arc':
                self.dummyFile.insert(-2, "  (gr_arc (start {0} {1}) (end {2} {3}) (angle {4}) (layer {6}) (width {5}))\n".format(
                    '{0:.10f}'.format(i[1] + abs(self.minX)), '{0:.10f}'.format(i[2] + abs(self.minY)), '{0:.10f}'.format(i[3] + abs(self.minX)), '{0:.10f}'.format(i[4] + abs(self.minY)), i[5], i[6], i[7]))
            elif i[0] == 'gr_line':
                self.dummyFile.insert(-2, "  (gr_line (start {0} {1}) (end {2} {3}) (angle 90) (layer {5}) (width {4}))\n".format(
                    '{0:.10f}'.format(i[1] + abs(self.minX)), '{0:.10f}'.format(i[2] + abs(self.minY)), '{0:.10f}'.format(i[3] + abs(self.minX)), '{0:.10f}'.format(i[4] + abs(self.minY)), i[5], i[6]))
            elif i[0] == 'gr_circle':
                self.dummyFile.insert(-2, "  (gr_circle (center {0} {1}) (end {2} {1}) (layer {4}) (width {3}))\n".format(
                    '{0:.10f}'.format(i[1] + abs(self.minX)), '{0:.10f}'.format(i[2] + abs(self.minY)), '{0:.10f}'.format(i[3] + abs(self.minX)), i[4], i[5]))
            elif i[0] == 'gr_text':
                x = i[1] + abs(self.minX)
                y = i[2] + abs(self.minY)
                
                self.dummyFile.insert(-2, '''
  (gr_text "{4}" (at {0} {1}{5}) (layer {2})
    (effects (font (size {3} {3}) (thickness 0.3)){6})
  )'''.format(x, y, i[3], i[4], i[5], i[6], i[7]))
            
            elif i[0] == 'hole':
                x = i[1] + abs(self.minX)
                y = i[2] * (-1) + abs(self.minY)
                drill = i[3] * 2
                
                self.dummyFile.insert(-2, '''\n
  (module 1pin (layer F.Cu) (tedit 53DA8F8F) (tstamp 53DB092E)
    (at {0} {1})
    (descr "module 1 pin (ou trou mecanique de percage)")
    (tags DEV)
    (path 1pin)
    (fp_text reference "" (at 0 -3.048) (layer F.SilkS)
      (effects (font (size 1.016 1.016) (thickness 0.254)))
    )
    (fp_text value "" (at 0 2.794) (layer F.SilkS) hide
      (effects (font (size 1.016 1.016) (thickness 0.254)))
    )
    (pad 1 thru_hole circle (at 0 0) (size {3} {3}) (drill {2})
      (layers *.Cu *.Mask F.SilkS)
    )
  )
'''.format(x, y, drill, drill + 0.01))

            elif i[0] == 'dim':
                if i[3][1] == i[4][1]:  # yS == yE
                    arrow1a = "{0} {1}".format("{0:.10f}".format(i[3][0] + abs(self.minX)), "{0:.10f}".format(i[5][1] * (-1) + abs(self.minY)))
                    arrow2a = "{0} {1}".format("{0:.10f}".format(i[4][0] + abs(self.minX)), "{0:.10f}".format(i[5][1] * (-1) + abs(self.minY)))
                elif i[3][0] == i[4][0]:  # xS == xE
                    arrow1a = "{0} {1}".format("{0:.10f}".format(i[5][0] + abs(self.minX)), "{0:.10f}".format(i[3][1] * (-1) + abs(self.minY)))
                    arrow2a = "{0} {1}".format("{0:.10f}".format(i[5][0] + abs(self.minX)), "{0:.10f}".format(i[4][1] * (-1) + abs(self.minY)))
                
                self.dummyFile.insert(-2, '''(dimension {0} (width 0.3) (layer Dwgs.User)
                    (gr_text "{1}" (at {2} {3} {4}) (layer Dwgs.User)
                      (effects (font (size 1.5 1.5) (thickness 0.3)))
                    )
                    (feature1 (pts (xy {5} {6}) (xy {9})))
                    (feature2 (pts (xy {7} {8}) (xy {10})))
                    (crossbar (pts (xy {9}) (xy {10})))
                    (arrow1a (pts (xy {9}) (xy {9})))
                    (arrow1b (pts (xy {9}) (xy {9})))
                    (arrow2a (pts (xy {10}) (xy {10})))
                    (arrow2b (pts (xy {10}) (xy {10})))
                  )'''.format(i[1], i[2], "{0:.10f}".format(i[5][0] + abs(self.minX)), "{0:.10f}".format(i[5][1] * (-1) + abs(self.minY)), i[6], "{0:.10f}".format(i[3][0] + abs(self.minX)), "{0:.10f}".format(i[3][1] * (-1) + abs(self.minY)), "{0:.10f}".format(i[4][0] + abs(self.minX)), "{0:.10f}".format(i[4][1] * (-1) + abs(self.minY)), arrow1a, arrow2a))

    def getMinX(self, x):
        if x < self.minX:
            self.minX = x
            
    def getMinY(self, y):
        if y < self.minY:
            self.minY = y
    
    def exportBoard(self, board):
        for i in board:
            if i[0] == 'line':
                self.addLine(i[1:], 'Edge.Cuts', 0.01)
            elif i[0] == 'circle':
                self.addCircle(i[1:], 'Edge.Cuts', 0.01)
            elif i[0] == 'arc':
                self.addArc(i[1:], 'Edge.Cuts', 0.01)
                
    def exportGlue(self, glue):
        for i in glue:
            if 'tGlue' in i[-2]:
                layer = 'F.Adhes'
            else:
                layer = 'B.Adhes'
                
            width = i[-1]
            
            if i[0] == 'line':
                self.addLine(i[1:], layer, width)
            elif i[0] == 'circle':
                self.addCircle(i[1:], layer, width)
            elif i[0] == 'arc':
                self.addArc(i[1:], layer, width)

                
    def addLine(self, line, layer, width):
        x1 = float(line[0])
        y1 = float(line[1]) * (-1)
        x2 = float(line[2])
        y2 = float(line[3]) * (-1)
        
        self.getMinX(x1)
        self.getMinY(y1)
        self.getMinX(x2)
        self.getMinY(y2)
        
        self.pcbElem.append(['gr_line', x1, y1, x2, y2, width, layer])
    
    def addCircle(self, circle, layer, width):
        xs = float(circle[1])
        ys = float(circle[2]) * (-1)
        xe = float(circle[1]) + float(circle[0])
        
        self.getMinX(xs)
        self.getMinY(ys)
        self.getMinX(xe)
        
        self.pcbElem.append(['gr_circle', xs, ys, xe, width, layer])
    
    def addArc(self, arc, layer, width):
        radius = arc[0]
        xs = arc[1]
        ys = arc[2] * (-1)
        sA = arc[3]
        eA = arc[4]
        
        x1 = radius * cos(sA) + xs
        y1 = (radius * sin(sA)) * (-1) + ys
        curve = degrees(sA - eA)
        
        self.getMinX(xs)
        self.getMinY(ys)
        self.getMinX(x1)
        self.getMinY(y1)
        
        self.pcbElem.append(['gr_arc', xs, ys, x1, y1, curve, width, layer])
    
    def exportAnnotations(self, annotations):
        for i in annotations:
            x = i[0]
            y = i[1]
            size = i[2]
            layer = i[3]
            annotation = i[4]
            align = i[5]
            rot = i[6]
            mirror = i[7]
            #spin = i[8]
            #
            y *= -1
        
            self.getMinX(x)
            self.getMinY(y)
            
            if layer == 'TOP':
                layer = 'F.Cu'
            else:
                layer = 'B.Cu'
            
            if rot == 0:
                rot = ''
            else:
                rot = ' {0}'.format(rot)
            
            if align in ["bottom-left", "center-left", "top-left"]:
                align = ' (justify left'
            elif align in ["bottom-right", "center-right", "top-right"]:
                align = ' (justify right'
            else:
                align = ' (justify'
            
            if mirror == 'Local Y axis':
                align = align + ' mirror)'
            else:
                align = align + ')'
            
            if align == ' (justify)':
                align = ''
                
            annotation = annotation.replace('\n', '\\n')
            
            self.pcbElem.append(['gr_text', x, y, layer, size, annotation, rot, align])
    
    def exportHoles(self, holes):
        for i in holes:
            self.getMinX(i[1])
            self.getMinY(i[2])
        
            self.pcbElem.append(['hole', i[1], i[2], i[0]])
    
    def exportDimensions(self, dimensions):
        for i in dimensions:
            Start = i[0]
            End = i[1]
            Dimline = i[2]
            Len = i[3]
            #
            rot = 0
            if Start[0] == End[0]:
                rot = 90

            self.pcbElem.append(['dim', Len.Value, Len, Start, End, Dimline, rot])


class fidocadj(exportPCB):
    ''' Export PCB to *.fcd - FidoCadJ '''
    def __init__(self, parent=None):
        exportPCB.__init__(self)
        
        self.dummyFile = codecs.open(__currentPath__ + "/save/untitled.fcd", "r").readlines()
        self.pcbElem = []
        self.programName = 'fidocadj'
        
        self.mnoznik = 0.127
        self.minX = 0
        self.maxY = 0

    def export(self, fileName):
        '''export(filePath): save board to fcd file
            filePath -> strig
            filePath = path/fileName.fcd'''
        fileName = self.fileExtension(fileName)
        #
        self.shiftPCB()
        self.files = codecs.open(fileName, "w", "utf-8")
        self.files.write("".join(self.dummyFile))
        #
        self.exportBoard(getBoardOutline())
        if self.addHoles:
            self.exportHoles(self.getHoles())
        if self.addAnnotations:
            self.exportAnnotations(getAnnotations())
        #
        self.files.close()
        
    def exportBoard(self, board):
        for i in board:
            if i[0] == 'line':
                self.addLine(i[1:], 0)
            elif i[0] == 'circle':
                self.addCircle(i[1:], 0)
            elif i[0] == 'arc':
                pass
    
    def exportAnnotations(self, annotations):
        for i in annotations:
            x = self.shiftXValue(i[0])
            y = self.shiftYValue(i[1])
            size = i[2]
            layer = i[3]
            annotation = i[4]
            #align = i[5]
            rot = i[6]
            mirror = i[7]
            #spin = i[8]
            #
            if mirror == 'Global Y axis':
                mirror = 4
            else:
                mirror = 0
            
            if layer == 'TOP':
                layer = 2
            else:
                layer = 1
                
            annotation = annotation.replace('\n', ' ')
            size = int(size / self.mnoznik)
            rot = int(rot)
            #
            self.files.write('TY {0} {1} {2} {3} {4} {5} {6} {7} {8}\n'.format(x, y, size, size, rot, mirror, layer, '*', annotation))

    def exportHoles(self, holes):
        for i in holes:
            self.addCircle(i, 0)
    
    def shiftPCB(self):
        try:
            board = FreeCAD.ActiveDocument.Board
            
            if board.Shape.BoundBox.XMin < 0:
                self.minX = float("%.3f" % board.Shape.BoundBox.XMin)
            if board.Shape.BoundBox.YMax > 0:
                self.maxY = float("%.3f" % board.Shape.BoundBox.YMax)
        except:
            pass

    def shiftXValue(self, value):
        return int((float(value) - self.minX) / self.mnoznik)
    
    def shiftYValue(self, value):
        return int((float(value) - self.maxY) / self.mnoznik) * (-1)
    
    def addLine(self, line, layer):
        x1 = self.shiftXValue(line[0])
        y1 = self.shiftYValue(line[1])
        x2 = self.shiftXValue(line[2])
        y2 = self.shiftYValue(line[3])
        
        self.files.write('LI {0} {1} {2} {3} {4}\n'.format(x1, y1, x2, y2, layer))
        
    def addCircle(self, circle, layer):
        x1 = self.shiftXValue(float(circle[1]) - float(circle[0]))
        y1 = self.shiftYValue(float(circle[2]) - float(circle[0]))
        x2 = self.shiftXValue(float(circle[1]) + float(circle[0]))
        y2 = self.shiftYValue(float(circle[2]) + float(circle[0]))
        
        self.files.write('EV {0} {1} {2} {3} {4}\n'.format(x1, y1, x2, y2, layer))


class idf_v2(exportPCB):
    ''' Export PCB to *.emn - IDF v2 '''
    def __init__(self, parent=None):
        exportPCB.__init__(self)
        
        self.programName = 'idf_v2'
    
    def writeHeader(self):
        self.files.write('''.HEADER
board_file 2.0 "FreeCAD-PCB" {0} 1
'{1}' MM
.END_HEADER\n'''.format(datetime.datetime.now().strftime('%Y/%m/%d.%H:%M:%S'), FreeCAD.ActiveDocument.Label))
    
    def export(self, fileName):
        '''export(filePath): save board to emn file
            filePath -> strig
            filePath = path/fileName.emn'''
        fileName = self.fileExtension(fileName)
        #
        self.files = codecs.open(fileName, "w", "utf-8")
        
        self.writeHeader()
        toHoles = self.exportBoardOutline()
        if self.addHoles:
            self.exportHoles(self.getHoles() + toHoles)

    def exportHoles(self, holes):
        self.files.write('.DRILLED_HOLES\n')
        #
        for i in holes:
            x = i[1]
            y = i[2]
            r = i[0] * 2
            
            self.files.write('{0} {1} {2} PTH BOARD\n'.format(r, x, y))
        #
        self.files.write('.END_DRILLED_HOLES\n')
    
    def exportBoardOutline(self):
        self.files.write('.BOARD_OUTLINE\n')
        self.files.write('{0}\n'.format(getPCBheight()[1]))
        #
        doc = FreeCAD.activeDocument()
        data = []
        toHoles = []
        
        for j in doc.Objects:
            if hasattr(j, "Proxy") and hasattr(j.Proxy, "Type") and j.Proxy.Type == "PCBboard":
                try:
                    pcbData = j.Border
                    pcbData.Geometry.sort()
                    # wires
                    wires = pcbData.Shape.Wires
                    wires = sortByArea(wires)
                    wires = [j for i,j in wires]
                    
                    num = 0
                    prev = [0, 0]
                    for i in range(len(wires)):
                        for j in range(len(wires[i].Edges)):
                            if wires[i].Edges[ j].Curve.__class__.__name__ == 'GeomLineSegment':
                                v = wires[i].Edges[j].Vertexes
                                if prev == [v[0].Point.x, v[0].Point.y]:
                                    x1 = v[1].Point.x
                                    y1 = v[1].Point.y
                                else:
                                    x1 = v[0].Point.x
                                    y1 = v[0].Point.y
                                prev = [x1, y1]
                                
                                # write to file
                                self.files.write("{0} {1} {2} {3}\n".format(num, x1, y1, 0.0))

                                if  j == len(wires[i].Edges) - 1:
                                    v = wires[i].Edges[0].Vertexes
                                    
                                    if prev == [v[0].Point.x, v[0].Point.y]:
                                        x1 = v[1].Point.x
                                        y1 = v[1].Point.y
                                    else:
                                        x1 = v[0].Point.x
                                        y1 = v[0].Point.y
                                    prev = [0, 0]
                                    
                                    self.files.write("{0} {1} {2} {3}\n".format(num, x1, y1, 0.0))
                            elif wires[i].Edges[j].Curve.__class__.__name__ == 'GeomArcOfCircle':
                                pass
                            elif wires[i].Edges[j].Curve.__class__.__name__ == 'GeomCircle':
                                # circles are not supported by IDFv2
                                cx = wires[i].Edges[j].Curve.Center.x
                                cy = wires[i].Edges[j].Curve.Center.y
                                r = wires[i].Edges[j].Curve.Radius
                                
                                toHoles.append([r, cx, cy])
                        #
                        num += 1
                    break
                except Exception as e:
                    FreeCAD.Console.PrintWarning('1. ' + str(e) + "\n")
        #
        self.files.write('.END_BOARD_OUTLINE\n')
        return toHoles


class idf_v3(exportPCB):
    ''' Export PCB to *.emn - IDF v3 '''
    def __init__(self, parent=None):
        exportPCB.__init__(self)
        
        self.programName = 'idf_v3'
    
    def writeHeader(self):
        self.files.write('''.HEADER
BOARD_FILE 3.0 "FreeCAD-PCB" {0} 1
'{1}' MM
.END_HEADER\n'''.format(datetime.datetime.now().strftime('%Y/%m/%d.%H:%M:%S'), FreeCAD.ActiveDocument.Label))
    
    def export(self, fileName):
        '''export(filePath): save board to emn file
            filePath -> strig
            filePath = path/fileName.emn'''
        fileName = self.fileExtension(fileName)
        #
        self.files = codecs.open(fileName, "w", "utf-8")
        
        self.writeHeader()
        self.exportBoardOutline()
        if self.addHoles:
            self.exportHoles(self.getHoles())
        if self.addAnnotations:
            self.exportAnnotations(getAnnotations())
        #
    
    def exportAnnotations(self, annotations):
        self.files.write('.NOTES\n')
        #
        for i in annotations:
            x = i[0]
            y = i[1]
            size = i[2]
            txt = i[4]
            
            self.files.write('{0} {1} {2} 2500.0 "{3}"\n'.format(x, y, size, txt))
        #
        self.files.write('.END_NOTES\n')
    
    def exportHoles(self, holes):
        self.files.write('.DRILLED_HOLES\n')
        #
        for i in holes:
            x = i[1]
            y = i[2]
            r = i[0] * 2
            
            self.files.write('{0} {1} {2} PTH BOARD VIA ECAD\n'.format(r, x, y))
        #
        self.files.write('.END_DRILLED_HOLES\n')
    
    def exportBoardOutline(self):
        self.files.write('.BOARD_OUTLINE ECAD\n')
        self.files.write('{0}\n'.format(getPCBheight()[1]))
        #
        doc = FreeCAD.activeDocument()
        data = []
        
        for j in doc.Objects:
            if hasattr(j, "Proxy") and hasattr(j.Proxy, "Type") and j.Proxy.Type == "PCBboard":
                try:
                    pcbData = j.Border
                    pcbData.Geometry.sort()
                    # wires
                    data = pcbData.Shape.Wires
                    data = sortByArea(data)
                    data = [j for i,j in data]
                    #
                    wires = []
                    for i in data:
                        for j in i:
                            wires.append(j)
                    
                    #FreeCAD.Console.PrintWarning("prev: {0}\n".format(wires))
                    #FreeCAD.Console.PrintWarning("\n")
                    #
                    num = 0
                    for i in range(len(wires)):
                        start = False
                        prev = [0, 0]
                        arcAngle_1 = 0.0
                        arcAngle_2 = 0.0
                        #
                        for j in range(len(wires[i].Edges)):
                            if wires[i].Edges[j].Curve.__class__.__name__ == 'GeomLineSegment':
                                v = wires[i].Edges[j].Vertexes
                                
                                if not start:
                                    px = v[1].Point.x
                                    py = v[1].Point.y
                                    
                                    self.files.write("{0} {1} {2} {3}\n".format(num, v[0].Point.x, v[0].Point.y, arcAngle_1))
                                    self.files.write("{0} {1} {2} {3}\n".format(num, px, py, arcAngle_1))
                                    
                                    start = [v[0].Point.x, v[0].Point.y]
                                else:
                                    if prev == [v[0].Point.x, v[0].Point.y]:
                                        px = v[1].Point.x
                                        py = v[1].Point.y
                                    else:
                                        px = v[0].Point.x
                                        py = v[0].Point.y
                                
                                    self.files.write("{0} {1} {2} {3}\n".format(num, px, py, arcAngle_1))
                                
                                #FreeCAD.Console.PrintWarning("linia\n")
                                #FreeCAD.Console.PrintWarning("{0} x {1}   /   {2} x {3}\n".format(v[0].Point.x, v[0].Point.y, v[1].Point.x, v[1].Point.y))
                                #FreeCAD.Console.PrintWarning("prev: {0} x {1}\n".format(px, py))
                                #FreeCAD.Console.PrintWarning("prev: {0}\n".format(prev))
                                #FreeCAD.Console.PrintWarning("\n")
                                prev = [px, py]
                                arcAngle_1 = 0.0
                            elif wires[i].Edges[j].Curve.__class__.__name__ == 'GeomCircle':
                                cx = wires[i].Edges[j].Curve.Center.x
                                cy = wires[i].Edges[j].Curve.Center.y
                                r = wires[i].Edges[j].Curve.Radius
                                
                                if len(wires[i].Edges[j].Vertexes) == 1:  # circle
                                    x1 = cx + r
                                    y1 = cy
                                    
                                    # write to file
                                    self.files.write("{0} {1} {2} {3}\n".format(num, cx, cy, 0.0))
                                    self.files.write("{0} {1} {2} {3}\n".format(num, x1, y1, 360.0))
                                elif len(wires[i].Edges[j].Vertexes) == 2: # arc
                                    p1_x = wires[i].Edges[j].Vertexes[0].Point.x
                                    p1_y = wires[i].Edges[j].Vertexes[0].Point.y
                                    p2_x = wires[i].Edges[j].Vertexes[1].Point.x
                                    p2_y = wires[i].Edges[j].Vertexes[1].Point.y
                                    #
                                    getAngle = mathFunctions()
                                    angle = abs(getAngle.arcGetAngle([cx, cy], [p1_x, p1_y], [p2_x, p2_y]))
                                    if angle > 180:
                                        angle = 360 - angle
                                    #
                                    if not start:
                                        px = p2_x
                                        py = p2_y
                                        
                                        arcAngle_1 = 0.0
                                        arcAngle_2 = angle
                                        
                                        start = [p1_x, p1_y]
                                        self.files.write("{0} {1} {2} 0.0\n".format(num, p1_x, p1_y))
                                    else:
                                        if prev == [p1_x, p1_y]:
                                            arcAngle_1 = 0.0
                                            arcAngle_2 = angle
                                            
                                            px = p2_x
                                            py = p2_y
                                        else:
                                            arcAngle_1 = 0.0
                                            arcAngle_2 = angle
                                            
                                            px = p1_x
                                            py = p1_y
                                    #
                                    if wires[i].Edges[j].Orientation != 'Forward':
                                        arcAngle_1 *= -1
                                        arcAngle_2 *= -1
                                    #
                                    prev = [px, py]
                                    self.files.write("{0} {1} {2} {3}\n".format(num, px, py, arcAngle_2))
                                    #
                                    #FreeCAD.Console.PrintWarning("arc\n")
                                    #FreeCAD.Console.PrintWarning("{0} x {1}   /   {2} x {3}\n".format(p1_x, p1_y, p2_x, p2_y))
                                    #FreeCAD.Console.PrintWarning("prev: {0} x {1}\n".format(px, py))
                                    #FreeCAD.Console.PrintWarning("prev: {0}\n".format(prev))
                                    #FreeCAD.Console.PrintWarning("\n")
                            #if j == len(wires[i].Edges) - 1 and start:
                                ##self.files.write("{0} {1} {2} 0.0\n".format(num,start[0], start[1]))
                                #start = False
                        #
                        num += 1
                    break
                except Exception as e:
                    FreeCAD.Console.PrintWarning('1. ' + str(e) + "\n")
        #
        self.files.write('.END_BOARD_OUTLINE\n')


class eagle(exportPCB):
    ''' Export PCB to *.brd - Eagle '''
    def __init__(self, parent=None):
        exportPCB.__init__(self)
        
        self.dummyFile = minidom.parse(__currentPath__ + "/save/untitled.brd")
        self.projektPlain = self.dummyFile.getElementsByTagName('plain')[0]
        self.programName = 'eagle'
    
    def export(self, fileName):
        '''export(filePath): save board to brd file
            filePath -> strig
            filePath = path/fileName.brd'''
        fileName = self.fileExtension(fileName)
        #
        self.exportBoard(getBoardOutline())
        if self.addHoles:
            self.exportHoles(self.getHoles())
        if self.addAnnotations:
            self.exportAnnotations(getAnnotations())
        if self.addDimensions:
            self.exportDimensions(getDimensions())
        if self.addGluePaths:
            self.exportGlue(getGlue())
        #
        with codecs.open(fileName, "w", "utf-8") as out:
            self.dummyFile.writexml(out)
    
    def addLine(self, line, layer, width):
        # <wire x1="22.86" y1="21.59" x2="54.61" y2="21.59" width="0" layer="20"/>
        x = self.dummyFile.createElement("wire")

        x.setAttribute('x1', self.precyzjaLiczb(line[0]))
        x.setAttribute('y1', self.precyzjaLiczb(line[1]))
        x.setAttribute('x2', self.precyzjaLiczb(line[2]))
        x.setAttribute('y2', self.precyzjaLiczb(line[3]))
        x.setAttribute('width', str(width))
        x.setAttribute('layer', str(layer))
        
        self.projektPlain.appendChild(x)
        
    def addCircle(self, circle, layer, width):
        # <circle x="16.51" y="26.67" radius="5.6796125" width="0" layer="20"/>
        x = self.dummyFile.createElement("circle")
        
        x.setAttribute('x', self.precyzjaLiczb(circle[1]))
        x.setAttribute('y', self.precyzjaLiczb(circle[2]))
        x.setAttribute('radius', str(circle[0]))
        x.setAttribute('width', str(width))
        x.setAttribute('layer', str(layer))
        self.projektPlain.appendChild(x)
        #FreeCAD.Console.PrintWarning(self.dummyFile.toxml())
    
    def addArc(self, arc, layer, width):
        # <wire x1="80.01" y1="7.62" x2="86.36" y2="13.97" width="0.4064" layer="20" curve="90"/>
        radius = arc[0]
        xs = arc[1]
        ys = arc[2]
        sA = arc[3]
        eA = arc[4]
        
        x1 = radius * cos(sA) + xs
        y1 = radius * sin(sA) + ys
        x2 = radius * cos(eA) + xs
        y2 = radius * sin(eA) + ys
        curve = degrees(sA - eA) * (-1)
        
        x = self.dummyFile.createElement("wire")
        
        x.setAttribute('x1', self.precyzjaLiczb(x1))
        x.setAttribute('y1', self.precyzjaLiczb(y1))
        x.setAttribute('x2', self.precyzjaLiczb(x2))
        x.setAttribute('y2', self.precyzjaLiczb(y2))
        x.setAttribute('curve', self.precyzjaLiczb(curve))
        x.setAttribute('width', str(width))
        x.setAttribute('layer', str(layer))
        self.projektPlain.appendChild(x)
        
    def exportGlue(self, glue):
        for i in glue:
            if 'tGlue' in i[-2]:
                layer = 35
            else:
                layer = 36
                
            width = i[-1]
            
            if i[0] == 'line':
                self.addLine(i[1:], layer, width)
            elif i[0] == 'circle':
                self.addCircle(i[1:], layer, width)
            elif i[0] == 'arc':
                self.addArc(i[1:], layer, width)

    def exportBoard(self, board):
        for i in board:
            if i[0] == 'line':
                self.addLine(i[1:], 20, 0.01)
            elif i[0] == 'circle':
                self.addCircle(i[1:], 20, 0.01)
            elif i[0] == 'arc':
                self.addArc(i[1:], 20, 0.01)
        
    def exportHoles(self, holes):
        for i in holes:
            # <hole x="36.83" y="41.91" drill="3.2"/>
            hole = self.dummyFile.createElement("hole")
            
            hole.setAttribute('x', self.precyzjaLiczb(i[1]))
            hole.setAttribute('y', self.precyzjaLiczb(i[2]))
            hole.setAttribute('drill', str(i[0] * 2))
            self.projektPlain.appendChild(hole)
        
    def exportAnnotations(self, annotations):
        for i in annotations:
            x = i[0]
            y = i[1]
            size = i[2]
            layer = i[3]
            annotation = i[4]
            align = i[5]
            rot = i[6]
            mirror = i[7]
            spin = i[8]
            
            # <text x="4.26" y="27.11" size="1.778" layer="25">test</text>
            if layer == 'TOP':
                layer = '25'
            else:
                layer = '26'
            
            annotation = self.dummyFile.createTextNode(annotation)
            
            if mirror == 'Global Y axis':
                mirror = 'M'
            else:
                mirror = ''
            if spin:
                spin = 'S'
            else:
                spin = ''
            rot = "{2}{1}R{0}".format(rot, mirror, spin)
            
            txt = self.dummyFile.createElement("text")
            
            txt.setAttribute('x', self.precyzjaLiczb(x))
            txt.setAttribute('y', self.precyzjaLiczb(y))
            txt.setAttribute('size', self.precyzjaLiczb(size))
            txt.setAttribute('layer', layer)
            if align != "bottom-left":
                txt.setAttribute('align', align)
            if rot != "R0.0":
                txt.setAttribute('rot', rot)
            txt.appendChild(annotation)
            self.projektPlain.appendChild(txt)
        
    def exportDimensions(self, dimensions):
        for i in dimensions:
            Start = i[0]
            End = i[1]
            Dimline = i[2]
            
            measure = self.dummyFile.createElement("dimension")
            
            measure.setAttribute('x1', self.precyzjaLiczb(Start[0]))
            measure.setAttribute('y1', self.precyzjaLiczb(Start[1]))
            measure.setAttribute('x2', self.precyzjaLiczb(End[0]))
            measure.setAttribute('y2', self.precyzjaLiczb(End[1]))
            measure.setAttribute('x3', self.precyzjaLiczb(Dimline[0]))
            measure.setAttribute('y3', self.precyzjaLiczb(Dimline[1]))
            measure.setAttribute('textsize', '1.778')
            measure.setAttribute('layer', '47')
            
            if Start[0] == End[0]:
                measure.setAttribute('dtype', 'vertical')
            elif Start[1] == End[1]:
                measure.setAttribute('dtype', 'horizontal')
            
            self.projektPlain.appendChild(measure)


def sortByArea(wires):
    wynik = {}
    
    for i in wires:
        area = Part.Wire(i.Edges)
        area = Part.Face(area)
        area = area.Area

        if not area in wynik:
            wynik[area] = []

        wynik[area].append(i)
    #
    wynik = OrderedDict(sorted(wynik.items(), key=lambda t: t[0]))
    wynik = wynik.items()
    wynik.reverse()

    return wynik
