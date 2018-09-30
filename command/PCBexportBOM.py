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
import codecs
from PySide import QtCore, QtGui
import datetime


exportList = {
    "csv": {'name': 'Comma Separated Values (CSV)', 'extension': 'csv', 'class': 'csv()'},
    "txt": {'name': 'Text File (TXT)', 'extension': 'txt', 'class': 'txt()'},
    "html": {'name': 'HyperText Markup Language (HTML)', 'extension': 'html', 'class': 'html()'},
}

__zeroPoint__ = ['Absolute', 'Own']


#***********************************************************************
#*                               GUI
#***********************************************************************
class createCentroid_Gui(QtGui.QDialog):
    ''' export bill of materials to one of supported formats '''
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        
        self.setWindowTitle(u"Centroid")
        #
        # Output directory
        self.pathToFile = QtGui.QLineEdit('')
        self.pathToFile.setReadOnly(True)
        
        zmianaSciezki = QtGui.QPushButton('...')
        zmianaSciezki.setToolTip(u'Change path')
        QtCore.QObject.connect(zmianaSciezki, QtCore.SIGNAL("pressed ()"), self.zmianaSciezkiF)
        # header
        icon = QtGui.QLabel('')
        icon.setPixmap(QtGui.QPixmap(":/data/img/exportBOM.png"))
        
        headerWidget = QtGui.QWidget()
        headerWidget.setStyleSheet("padding: 10px; border-bottom: 1px solid #dcdcdc; background-color:#FFF;")
        headerLay = QtGui.QGridLayout(headerWidget)
        headerLay.addWidget(icon, 0, 0, 1, 1)
        headerLay.setContentsMargins(0, 0, 0, 0)
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
        # report
        self.reportPrev = QtGui.QTextEdit()
    
        ########
        centerLay = QtGui.QGridLayout()
        centerLay.addWidget(QtGui.QLabel(u'Output directory:'), 0, 0, 1, 1)
        centerLay.addWidget(self.pathToFile, 0, 1, 1, 1)
        centerLay.addWidget(zmianaSciezki, 0, 2, 1, 1)
        centerLay.addWidget(self.reportPrev, 1, 0, 1, 3)
        centerLay.setContentsMargins(10, 20, 10, 20)

        mainLay = QtGui.QVBoxLayout(self)
        mainLay.addWidget(headerWidget)
        mainLay.addLayout(centerLay)
        mainLay.addLayout(packageFooter)
        mainLay.setContentsMargins(0, 0, 0, 0)
        #
        self.showReport()
        
    def showReport(self):
        txt = '''Report Origin = (0.0, 0.0)
Units used = "mm"
"RefDes","Layer","LocationX","LocationY","Rotation"

'''
        doc = FreeCAD.activeDocument()
        if len(doc.Objects):
            for i in doc.Objects:
                if hasattr(i, "Proxy") and hasattr(i.Proxy, "Type") and i.Proxy.Type in ["PCBpart", "PCBpart_E"]:  # objects
                    x = doc.getObject(i.Name).X.Value
                    y = doc.getObject(i.Name).Y.Value
                    side = doc.getObject(i.Name).Side
                    rot = doc.getObject(i.Name).Rot.Value
                    
                    rot = rot % 360
                    
                    txt += '"{0}","{1}","{2}","{3}","{4}"\n'.format(i.PartName.ViewObject.Text, side, x, y, rot)
        
        self.reportPrev.setPlainText(txt)

    def accept(self):
        try:
            export = createCentroid()
            export.filePath = str(self.pathToFile.text())
            export.fileName = FreeCAD.ActiveDocument.Label
            export.export()
            
            super(createCentroid_Gui, self).accept()
        except Exception as e:
            FreeCAD.Console.PrintWarning("{0} \n".format(e))
        
    def zmianaSciezkiF(self):
        ''' change output file path '''
        fileName = QtGui.QFileDialog().getExistingDirectory(None, 'Output directory', QtCore.QDir.homePath(), QtGui.QFileDialog.ShowDirsOnly)
        
        if fileName:
            self.pathToFile.setText(fileName)


class exportBOM_Gui(QtGui.QDialog):
    ''' export bill of materials to one of supported formats '''
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        
        self.setWindowTitle(u"Export BOM")
        #
        # Output file format
        self.formatList = QtGui.QComboBox()
        for i, j in exportList.items():
            self.formatList.addItem(j['name'], i)
        
        self.formatList.setCurrentIndex(self.formatList.findData('csv'))
        # Output directory
        self.pathToFile = QtGui.QLineEdit('')
        self.pathToFile.setReadOnly(True)
        
        zmianaSciezki = QtGui.QPushButton('...')
        zmianaSciezki.setToolTip(u'Change path')
        QtCore.QObject.connect(zmianaSciezki, QtCore.SIGNAL("pressed ()"), self.zmianaSciezkiF)
        # Units
        unitsMM = QtGui.QRadioButton(u'Millimeters')
        unitsMM.setChecked(True)
        
        unitsINCH = QtGui.QRadioButton(u'Inches')
        unitsINCH.setDisabled(True)
        
        self.buttonGroupUnits = QtGui.QButtonGroup()
        self.buttonGroupUnits.addButton(unitsMM)
        self.buttonGroupUnits.addButton(unitsINCH)
        
        unitsGroupBox = QtGui.QGroupBox(u'Units')
        unitsGroupBoxLay = QtGui.QVBoxLayout(unitsGroupBox)
        unitsGroupBoxLay.addWidget(unitsMM)
        unitsGroupBoxLay.addWidget(unitsINCH)
        unitsGroupBoxLay.addStretch(10)
        # Options
        self.opetionFullList = QtGui.QCheckBox('Full list')
        self.optionsMinimalHeader = QtGui.QCheckBox('Minimal header')
        
        optionsGroupBox = QtGui.QGroupBox(u'Options')
        optionsGroupBoxLay = QtGui.QVBoxLayout(optionsGroupBox)
        optionsGroupBoxLay.addWidget(self.opetionFullList)
        optionsGroupBoxLay.addWidget(self.optionsMinimalHeader)
        optionsGroupBoxLay.addStretch(10)
        # Zero point drilling
        zeroPointAbsolute = QtGui.QRadioButton(__zeroPoint__[0])
        zeroPointAbsolute.setChecked(True)
        
        zeroPointOwn = QtGui.QRadioButton(__zeroPoint__[1])
        
        self.zeroPointOwn_X = QtGui.QDoubleSpinBox()
        self.zeroPointOwn_X.setPrefix('X: ')
        self.zeroPointOwn_X.setSuffix('mm')
        self.zeroPointOwn_X.setRange(-1000, 1000)
        
        self.zeroPointOwn_Y = QtGui.QDoubleSpinBox()
        self.zeroPointOwn_Y.setPrefix('Y: ')
        self.zeroPointOwn_Y.setSuffix('mm')
        self.zeroPointOwn_Y.setRange(-1000, 1000)
        
        self.buttonGroupzeroPoint = QtGui.QButtonGroup()
        self.buttonGroupzeroPoint.addButton(zeroPointAbsolute)
        self.buttonGroupzeroPoint.addButton(zeroPointOwn)
        
        zeroPointGroupBox = QtGui.QGroupBox(u'Zero point')
        zeroPointGroupBoxLay = QtGui.QGridLayout(zeroPointGroupBox)
        zeroPointGroupBoxLay.addWidget(zeroPointAbsolute, 0, 0, 1, 3)
        zeroPointGroupBoxLay.addWidget(zeroPointOwn, 1, 0, 1, 3)
        zeroPointGroupBoxLay.addItem(QtGui.QSpacerItem(20, 1), 2, 0, 1, 1)
        zeroPointGroupBoxLay.addWidget(self.zeroPointOwn_X, 2, 1, 1, 1)
        zeroPointGroupBoxLay.addWidget(self.zeroPointOwn_Y, 2, 2, 1, 1)
        zeroPointGroupBoxLay.setRowStretch(3, 10)
        
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
        icon.setPixmap(QtGui.QPixmap(":/data/img/exportBOM.png"))
        
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
        centerLay.setContentsMargins(10, 20, 10, 0)
        
        centerLay_2 = QtGui.QGridLayout()
        centerLay_2.addWidget(unitsGroupBox, 0, 0, 1, 1)
        centerLay_2.addWidget(optionsGroupBox, 0, 1, 1, 1)
        centerLay_2.addWidget(zeroPointGroupBox, 1, 0, 1, 2)
        centerLay_2.setHorizontalSpacing(20)
        centerLay_2.setColumnStretch(10, 10)
        centerLay_2.setContentsMargins(10, 0, 10, 20)
        
        mainLay = QtGui.QVBoxLayout(self)
        mainLay.addWidget(headerWidget)
        mainLay.addLayout(centerLay)
        mainLay.addLayout(centerLay_2)
        mainLay.addStretch(10)
        mainLay.addLayout(packageFooter)
        mainLay.setContentsMargins(0, 0, 0, 0)
        #
    
    def accept(self):
        try:
            export = exportBOM()
            export.fileFormat = self.formatList.itemData(self.formatList.currentIndex())
            export.filePath = str(self.pathToFile.text())
            export.fileName = FreeCAD.ActiveDocument.Label
            export.zeroPoint = self.buttonGroupzeroPoint.checkedId()
            export.zeroPoint_X = self.zeroPointOwn_X.value()
            export.zeroPoint_Y = self.zeroPointOwn_Y.value()
            export.minimalHeader = self.optionsMinimalHeader.isChecked()
            export.fullList = self.opetionFullList.isChecked()
            
            if self.buttonGroupUnits.checkedId() == -2:
                export.units = 'mm'
            else:
                export.units = 'inch' 

            export.export()
        except Exception as e:
            FreeCAD.Console.PrintWarning("{0} \n".format(e))
        
        #super(exportBOM_Gui, self).accept()
        
    def zmianaSciezkiF(self):
        ''' change output file path '''
        fileName = QtGui.QFileDialog().getExistingDirectory(None, 'Output directory', QtCore.QDir.homePath(), QtGui.QFileDialog.ShowDirsOnly)
        
        if fileName:
            self.pathToFile.setText(fileName)


#***********************************************************************
#*                             CONSOLE
#***********************************************************************
class createCentroid(QtGui.QDialog):
    def __init__(self):
        self.fileFormat = 'txt'
        self.filePath = str(QtCore.QDir.homePath())  # def. home directory
        self.fileName = 'untitled'  # def. value

    def export(self):
        fileName = os.path.join(self.filePath, self.fileName + "_centroid")
        if not fileName.endswith('txt'):
            fileName = fileName + '.txt'
        
        self.files = codecs.open(fileName, "w", "utf-8")
        #
        self.files.write('Report Origin = (0.0, 0.0)\n')
        self.files.write('Units used = "mm"\n')
        self.files.write('"RefDes","Layer","LocationX","LocationY","Rotation"\n')
        self.files.write('\n')
        
        doc = FreeCAD.activeDocument()
        if len(doc.Objects):
            for i in doc.Objects:
                if hasattr(i, "Proxy") and hasattr(i.Proxy, "Type") and i.Proxy.Type in ["PCBpart", "PCBpart_E"]:  # objects
                    x = doc.getObject(i.Name).X.Value
                    y = doc.getObject(i.Name).Y.Value
                    side = doc.getObject(i.Name).Side
                    rot = doc.getObject(i.Name).Rot.Value
                    
                    rot = rot % 360
                    
                    self.files.write('"{0}","{1}","{2}","{3}","{4}"\n'.format(i.PartName.ViewObject.Text, side, x, y, rot))
        #
        self.files.close()


class exportBOM:
    def __init__(self):
        self.fileFormat = 'csv'
        self.filePath = str(QtCore.QDir.homePath())  # def. home directory
        self.fileName = 'untitled'  # def. value
        self.units = 'mm'  # mm/inch
        self.fullList = False  # True/False
        self.zeroPoint = -2  # -2:Absolute   -3:Own - read from zeroPoint_X/Y
        self.zeroPoint_X = 0
        self.zeroPoint_Y = 0
        self.minimalHeader = False  # True/False
    
    def setUnit(self, value):
        if self.units == 'mm':
            return value
        else:
            return value
    
    def prepareX(self, value):
        value = self.setUnit(value)

        if self.zeroPoint == -3:
            value -= self.zeroPoint_X

        return value
        
    def prepareY(self, value):
        value = self.setUnit(value)

        if self.zeroPoint == -3:
            value -= self.zeroPoint_Y

        return value
    
    def export(self):
        try:
            exportClass = eval(exportList[self.fileFormat]['class'])
            exportClass.fileName = self.fileName
            exportClass.filePath = self.filePath
            exportClass.parts = self.getParts()
            exportClass.fullList = self.fullList
            exportClass.unit = self.units
            exportClass.minimalHeader = self.minimalHeader
            exportClass.zeroPoint = __zeroPoint__[self.zeroPoint * (-1) -2]
            if not self.zeroPoint == -2:
                exportClass.zeroPoint_X = self.zeroPoint_X
                exportClass.zeroPoint_Y = self.zeroPoint_Y
            exportClass.export()
        except Exception as e:
            FreeCAD.Console.PrintWarning("{0} \n".format(e))
    
    def getParts(self):
        ''' get param from all packages from current document '''
        parts = {}
        
        doc = FreeCAD.activeDocument()
        if len(doc.Objects):
            for i in doc.Objects:
                if hasattr(i, "Proxy") and hasattr(i.Proxy, "Type") and i.Proxy.Type in ["PCBpart", "PCBpart_E"]:  # objects
                #if hasattr(elem, "Proxy") and hasattr(elem.Proxy, "Type") and elem.Proxy.Type == 'partsGroup':  # objects
                    #for i in elem.OutList:
                        #if hasattr(i, "Proxy") and hasattr(i.Proxy, "Type") and i.Proxy.Type in ["PCBpart", "PCBpart_E"]:
                    if not i.Package in parts.keys():
                        parts[i.Package] = {}
                    if not '_'.join(i.PartValue.ViewObject.Text) in parts[i.Package].keys():
                        parts[i.Package]['_'.join(i.PartValue.ViewObject.Text)] = {}
                        
                    x = self.prepareX(doc.getObject(i.Name).X.Value)
                    y = self.prepareY(doc.getObject(i.Name).Y.Value)
                    
                    parts[i.Package]['_'.join(i.PartValue.ViewObject.Text)]['_'.join(i.PartName.ViewObject.Text)] = {'side': i.Side, 'x': x, 'y': y, 'z': doc.getObject(i.Name).Placement.Base.z, 'rot': doc.getObject(i.Name).Rot.Value}
        return parts


##
class exportFileMain():
    def __init__(self):
        self.exportHeaders = ['ID', 'Package', 'Value', 'Quantity', 'X', 'Y', 'Rotation', 'Side']
        self.fileName = ''
        self.filePath = ''
        self.parts = {}
        self.fullList = False
        self.minimalHeader = False
        self.unit = 'mm'
        self.zeroPoint = -2
        self.zeroPoint_X = 0
        self.zeroPoint_Y = 0


class html(exportFileMain):
    ''' Export BOM to *.html '''
    def __init__(self):
        exportFileMain.__init__(self)

    def addTitle(self):
        if not self.fullList:
            self.files.write('<tr><th>' + ('</th><th>').join(self.exportHeaders[:4]) + '</th></tr>\n')
        else:
            self.files.write('<tr><th>' + ('</th><th>').join(self.exportHeaders) + '</th></tr>\n')
    
    def fileHeader(self):
        self.files.write("""<html>
    <head>
        <style tyle="text/css">
            body {cursor: default !important;}
            table {margin: 0 auto;}
            table td, table th {padding:5px 10px;}
            table tr:nth-child(odd) {background:#E6E6DC;}
            table tr:nth-child(1) {background:#00628B !important; font-weight: bold.}
            table tr:hover {background:#81A594;}
            .stopka {font-weight:bold; font-size: 12px; background: #fff; padding: 5px;}
        </style>
    </head>
    <body>
        <p><h1>Bill of materials</h1></p>
        """)
        
        if not self.minimalHeader:
            self.files.write('<p><span style="font-weight:bold">Project:</span> {0}</p>'.format(self.fileName))
            self.files.write('<p><span style="font-weight:bold">Date:</span> {0}</p>'.format(datetime.datetime.now()))
            if self.fullList:
                self.files.write('<p><span style="font-weight:bold">Unit:</span> {0}</p>'.format(self.unit))
                self.files.write('<p><span style="font-weight:bold">Zero point drilling:</span> {0} ({1} x {2})</p>'.format(self.zeroPoint, self.zeroPoint_X, self.zeroPoint_Y))
        
        self.files.write('''<p><table>''')
        
    def fileFooter(self):
        self.files.write("""
            </table>
        </p>
        <div class='stopka'></div>
    </body>
</html>""".format())
    
    def export(self):
        '''export(filePath): save BOM to html file
            filePath -> strig
            filePath = path/fileName.html'''
        fileName = os.path.join(self.filePath, self.fileName)
        if not fileName.endswith('html'):
            fileName = fileName + '.html'
        
        self.files = codecs.open(fileName, "w", "utf-8")
        #
        self.fileHeader()
        self.addTitle()
        #
        self.exportParts()
        #
        self.fileFooter()
        self.files.close()
    
    def exportParts(self):
        for i in self.parts.keys():
            for j in self.parts[i].keys():  # value
                if not self.fullList:
                    #files.write("<tr><td>{0}</td><td>{1}</td><td>{2}</td><td style='text-align:center;'>{3}</td></tr>\n".format(i, j, ', '.join(elem[i][j].keys()), len(elem[i][j].keys())))
                    self.files.write("<tr style='text-align:center;'><td style='text-align:left;'>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>\n".format(', '.join(self.parts[i][j].keys()), i, j, len(self.parts[i][j].keys())))
                else:
                    for k in self.parts[i][j].keys():
                        self.files.write("<tr style='text-align:center;'><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td><td>{7}</td></tr>\n".format(k, i, j, len(self.parts[i][j].keys()), self.parts[i][j][k]['x'], self.parts[i][j][k]['y'], self.parts[i][j][k]['rot'], self.parts[i][j][k]['side']))


class txt(exportFileMain):
    ''' Export BOM to *.txt '''
    def __init__(self):
        exportFileMain.__init__(self)
    
    def addTitle(self, num):
        if not self.fullList:
            return self.exportHeaders[num]
        else:
            return self.exportHeaders[num]
    
    def export(self):
        '''export(filePath): save BOM to txt file
            filePath -> strig
            filePath = path/fileName.txt'''
        fileName = os.path.join(self.filePath, self.fileName)
        if not fileName.endswith('txt'):
            fileName = fileName + '.txt'
        
        self.files = codecs.open(fileName, "w", "utf-8")
        #
        if not self.minimalHeader:
            self.files.write('Drill file\n')
            self.files.write('Project: {0}\n'.format(self.fileName))
            self.files.write('Date: {0}\n'.format(datetime.datetime.now()))
            if self.fullList:
                self.files.write('Unit: {0}\n'.format(self.unit))
                self.files.write('Zero point drilling: {0} ({1} x {2})\n'.format(self.zeroPoint, self.zeroPoint_X, self.zeroPoint_Y))
            self.files.write('\n\n')
        
        self.exportParts()
        #
        self.files.close()

    def exportParts(self):
        #  get param.
        try:
            kolumny = [0, 0, 0, 0, 0, 0, 0, 0]
            for i in self.parts.keys():
                if len(i) > kolumny[0]:  # package
                    kolumny[0] = len(i)
                for j in self.parts[i].keys():
                    if len(j) > kolumny[1]:    # value
                        kolumny[1] = len(j)
                    
                    if not self.fullList:
                        if len(', '.join(self.parts[i][j].keys())) > kolumny[2]:    # part name
                            kolumny[2] = len(', '.join(self.parts[i][j].keys()))
                    else:
                        for k in self.parts[i][j].keys():
                            if len(k) > kolumny[2]:    # part name
                                kolumny[2] = len(k)
                            if len(str(self.parts[i][j][k]['x'])) > kolumny[4]:
                                kolumny[4] = len(str(self.parts[i][j][k]['x']))
                            if len(str(self.parts[i][j][k]['y'])) > kolumny[5]:
                                kolumny[5] = len(str(self.parts[i][j][k]['y']))
                            if len(str(self.parts[i][j][k]['rot'])) > kolumny[6]:
                                kolumny[6] = len(str(self.parts[i][j][k]['rot']))
                            if len(str(self.parts[i][j][k]['side'])) > kolumny[7]:
                                kolumny[7] = len(str(self.parts[i][j][k]['side']))
            # headers
            self.files.write(self.addTitle(0).ljust(kolumny[2] + 10))
            self.files.write(self.addTitle(1).ljust(kolumny[0] + 10))
            self.files.write(self.addTitle(2).ljust(kolumny[1] + 10))
            if self.fullList:
                self.files.write(self.addTitle(4).ljust(kolumny[4] + 10))
                self.files.write(self.addTitle(5).ljust(kolumny[5] + 10))
                self.files.write(self.addTitle(6).ljust(kolumny[6] + 10))
                self.files.write(self.addTitle(7).ljust(kolumny[7] + 10))
            self.files.write(self.addTitle(3))
            self.files.write("\n")
            # write param. to file
            for i in self.parts.keys():  # package
                for j in self.parts[i].keys():  # value
                    if not self.fullList:
                        self.files.write(', '.join(self.parts[i][j].keys()).ljust(kolumny[2] + 10))
                        self.files.write(str(i).ljust(kolumny[0] + 10))
                        self.files.write(str(j).ljust(kolumny[1] + 10))
                        self.files.write(str(len(self.parts[i][j].keys())))
                        self.files.write("\n")
                    else:
                        for k in self.parts[i][j].keys():
                            self.files.write(str(k).ljust(kolumny[2] + 10))
                            self.files.write(str(i).ljust(kolumny[0] + 10))
                            self.files.write(str(j).ljust(kolumny[1] + 10))
                            self.files.write(str(self.parts[i][j][k]['x']).ljust(kolumny[4] + 10))
                            self.files.write(str(self.parts[i][j][k]['y']).ljust(kolumny[5] + 10))
                            self.files.write(str(self.parts[i][j][k]['rot']).ljust(kolumny[6] + 10))
                            self.files.write(str(self.parts[i][j][k]['side']).ljust(kolumny[7] + 10))
                            self.files.write(str(len(self.parts[i][j].keys())))
                            self.files.write("\n")
        except Exception as e:
            FreeCAD.Console.PrintWarning("{0} \n".format(e))


class csv(exportFileMain):
    ''' Export BOM to *.csv '''
    def __init__(self):
        exportFileMain.__init__(self)
        
    def addTitle(self):
        if not self.minimalHeader:
            self.files.write('Drill file\n')
            self.files.write('Project:;{0}\n'.format(self.fileName))
            self.files.write('Date;{0}\n'.format(datetime.datetime.now()))
            if self.fullList:
                self.files.write('Unit;{0}\n'.format(self.unit))
                self.files.write('Zero point drilling;{0} ({1} x {2})\n'.format(self.zeroPoint, self.zeroPoint_X, self.zeroPoint_Y))
            self.files.write('\n\n')
        
        if not self.fullList:
            self.files.write((';').join(self.exportHeaders[:4]) + '\n')
        else:
            self.files.write((';').join(self.exportHeaders) + '\n')
    
    def export(self):
        '''export(filePath): save BOM to csv file
            filePath -> strig
            filePath = path/fileName.csv'''
        fileName = os.path.join(self.filePath, self.fileName)
        if not fileName.endswith('csv'):
            fileName = fileName + '.csv'
        
        self.files = codecs.open(fileName, "w", "utf-8")
        #
        self.addTitle()
        self.exportParts()
        #
        self.files.close()
    
    def exportParts(self):
        for i in self.parts.keys():  # package
            for j in self.parts[i].keys():  # value
                if not self.fullList:
                    self.files.write("{0};{1};{2};{3}\n".format(', '.join(self.parts[i][j].keys()), i, j, len(self.parts[i][j].keys())))
                else:
                    for k in self.parts[i][j].keys():
                        self.files.write("{0};{1};{2};{3};{4};{5};{6};{7}\n".format(k, i, j, len(self.parts[i][j].keys()), self.parts[i][j][k]['x'], self.parts[i][j][k]['y'], self.parts[i][j][k]['rot'], self.parts[i][j][k]['side']))
