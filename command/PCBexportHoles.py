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
    'drl': {'name': 'Excellon (DRL)', 'class': 'drl()', 'extension': 'drl'},
    'txt': {'name': 'Text File (TXT)', 'class': 'txt()', 'extension': 'txt'},
    'csv': {'name': 'Comma Separated Values (CSV)', 'class': 'csv()', 'extension': 'csv'},
    'html': {'name': 'HyperText Markup Language (HTML)', 'class': 'html()', 'extension': 'html'},
}

__saveFormats__ = ['Decimal', 'Suppress leading zeros', 'Suppress trailing zeros', 'Keep zeros']
__zeroPointDrilling__ = ['Absolute', 'Own']

#***********************************************************************
#*                               GUI
#***********************************************************************
class exportHoles_Gui(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        
        self.setWindowTitle(u"Export hole locations")
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
    
        # Format
        formatDecimal = QtGui.QRadioButton(__saveFormats__[0])
        formatDecimal.setChecked(True)
        
        formatSuppressLeadingZeros = QtGui.QRadioButton(__saveFormats__[1])
        formatSuppressTrailingZeros = QtGui.QRadioButton(__saveFormats__[2])
        formatKeepZeros = QtGui.QRadioButton(__saveFormats__[3])
        
        self.buttonGroupFormat = QtGui.QButtonGroup()
        self.buttonGroupFormat.addButton(formatDecimal)
        self.buttonGroupFormat.addButton(formatSuppressLeadingZeros)
        self.buttonGroupFormat.addButton(formatSuppressTrailingZeros)
        self.buttonGroupFormat.addButton(formatKeepZeros)
        
        formatGroupBox = QtGui.QGroupBox(u'Format')
        formatGroupBoxLay = QtGui.QVBoxLayout(formatGroupBox)
        formatGroupBoxLay.addWidget(formatDecimal)
        formatGroupBoxLay.addWidget(formatSuppressLeadingZeros)
        formatGroupBoxLay.addWidget(formatSuppressTrailingZeros)
        formatGroupBoxLay.addWidget(formatKeepZeros)
        formatGroupBoxLay.addStretch(10)
        
        # Zero point drilling
        zeroPointDrillingAbsolute = QtGui.QRadioButton(__zeroPointDrilling__[0])
        zeroPointDrillingAbsolute.setChecked(True)
        
        zeroPointDrillingOwn = QtGui.QRadioButton(__zeroPointDrilling__[1])
        
        self.zeroPointDrillingOwn_X = QtGui.QDoubleSpinBox()
        self.zeroPointDrillingOwn_X.setPrefix('X: ')
        self.zeroPointDrillingOwn_X.setSuffix('mm')
        self.zeroPointDrillingOwn_X.setRange(-1000, 1000)
        
        self.zeroPointDrillingOwn_Y = QtGui.QDoubleSpinBox()
        self.zeroPointDrillingOwn_Y.setPrefix('Y: ')
        self.zeroPointDrillingOwn_Y.setSuffix('mm')
        self.zeroPointDrillingOwn_Y.setRange(-1000, 1000)
        
        self.buttonGroupZeroPointDrilling = QtGui.QButtonGroup()
        self.buttonGroupZeroPointDrilling.addButton(zeroPointDrillingAbsolute)
        self.buttonGroupZeroPointDrilling.addButton(zeroPointDrillingOwn)
        
        zeroPointDrillingGroupBox = QtGui.QGroupBox(u'Zero point drilling')
        zeroPointDrillingGroupBoxLay = QtGui.QGridLayout(zeroPointDrillingGroupBox)
        zeroPointDrillingGroupBoxLay.addWidget(zeroPointDrillingAbsolute, 0, 0, 1, 3)
        zeroPointDrillingGroupBoxLay.addWidget(zeroPointDrillingOwn, 1, 0, 1, 3)
        zeroPointDrillingGroupBoxLay.addItem(QtGui.QSpacerItem(20, 1), 2, 0, 1, 1)
        zeroPointDrillingGroupBoxLay.addWidget(self.zeroPointDrillingOwn_X, 2, 1, 1, 1)
        zeroPointDrillingGroupBoxLay.addWidget(self.zeroPointDrillingOwn_Y, 2, 2, 1, 1)
        zeroPointDrillingGroupBoxLay.setRowStretch(3, 10)
        
        # Options
        self.optionsMirror_X = QtGui.QCheckBox('Mirror X')
        self.optionsMirror_Y = QtGui.QCheckBox('Mirror Y')
        self.optionsMinimalHeader = QtGui.QCheckBox('Minimal header')
        self.optionsGroupHoles = QtGui.QCheckBox('Group holes by diameter')
        
        optionsGroupBox = QtGui.QGroupBox(u'Options')
        optionsGroupBoxLay = QtGui.QVBoxLayout(optionsGroupBox)
        optionsGroupBoxLay.addWidget(self.optionsMirror_X)
        optionsGroupBoxLay.addWidget(self.optionsMirror_Y)
        optionsGroupBoxLay.addWidget(self.optionsMinimalHeader)
        optionsGroupBoxLay.addWidget(self.optionsGroupHoles)
        optionsGroupBoxLay.addStretch(10)
        
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
        icon.setPixmap(QtGui.QPixmap(":/data/img/drill-icon.png"))
        
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
        centerLay_2.addWidget(formatGroupBox, 1, 0, 1, 1)
        centerLay_2.addWidget(zeroPointDrillingGroupBox, 1, 1, 1, 1)
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
        self.connect(self.formatList, QtCore.SIGNAL('currentIndexChanged (int)'), self.changeFileFormat)
        self.formatList.setCurrentIndex(self.formatList.findData('drl'))
        
    def changeFileFormat(self):
        if self.formatList.itemData(self.formatList.currentIndex()) in ['drl']:
            self.optionsGroupHoles.setChecked(False)
            self.optionsGroupHoles.setDisabled(True)
        else:
            self.optionsGroupHoles.setDisabled(False)
        
    def accept(self):
        export = exportHoles()
        export.fileFormat = self.formatList.itemData(self.formatList.currentIndex())
        export.filePath = str(self.pathToFile.text())
        export.fileName = FreeCAD.ActiveDocument.Label

        if self.buttonGroupUnits.checkedId() == -2:
            export.units = 'mm'
        else:
            export.units = 'inch' 
        
        export.saveFormat = self.buttonGroupFormat.checkedId()
        export.zeroPointDrilling = self.buttonGroupZeroPointDrilling.checkedId()
        export.zeroPointDrilling_X = self.zeroPointDrillingOwn_X.value()
        export.zeroPointDrilling_Y = self.zeroPointDrillingOwn_Y.value()
        export.mirror_X = self.optionsMirror_X.isChecked()
        export.mirror_Y = self.optionsMirror_Y.isChecked()
        export.minimalHeader = self.optionsMinimalHeader.isChecked()
        export.groupHoles = self.optionsGroupHoles.isChecked()
        export.export()
        
        #super(exportHoles_Gui, self).accept()
        
    def zmianaSciezkiF(self):
        ''' change output file path '''
        fileName = QtGui.QFileDialog().getExistingDirectory(None, 'Output directory', QtCore.QDir.homePath(), QtGui.QFileDialog.ShowDirsOnly)
        
        if fileName:
            self.pathToFile.setText(fileName)


class exportHolesReport_Gui(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        
        self.setWindowTitle(u"Export hole locations report")
        
        # Output directory
        self.pathToFile = QtGui.QLineEdit('')
        self.pathToFile.setReadOnly(True)
        
        zmianaSciezki = QtGui.QPushButton('...')
        zmianaSciezki.setToolTip(u'Change path')
        QtCore.QObject.connect(zmianaSciezki, QtCore.SIGNAL("pressed ()"), self.zmianaSciezkiF)
        # header
        icon = QtGui.QLabel('')
        icon.setPixmap(QtGui.QPixmap(":/data/img/drill-icon.png"))
        
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
        holes = self.getHoles()
        #
        txt = ''
        txt += 'Drill report for {0}\n'.format(FreeCAD.ActiveDocument.Label)
        txt += 'Created on {0}\n'.format(datetime.datetime.now())
        txt += 'Drill report for plated through holes:\n'
        
        num = 0
        for i in range(len(holes.keys())):
            txt += 'T{0}  {1}mm  {2}"  ({3} holes)\n'.format(i + 1, '%.2f' % holes.keys()[i], '%.3f' % (float(holes.keys()[i]) / 25.4), holes[holes.keys()[i]])
            num += holes[holes.keys()[i]]
        
        txt += '\nTotal plated holes count: {0}\n'.format(num)
        
        self.reportPrev.setPlainText(txt)
    
    def getHoles(self):
        holes = {}
        #
        for i in FreeCAD.ActiveDocument.Board.Holes.Geometry:
            if str(i.__class__) == "<type 'Part.GeomCircle'>" and not i.Construction:
                d = i.Radius * 2.0
                
                if not d in holes.keys():
                    holes[d] = 0
                
                holes[d] += 1
        #
        return holes
    
    def accept(self):
        try:
            export = exportHolesReport()
            export.filePath = str(self.pathToFile.text())
            export.fileName = FreeCAD.ActiveDocument.Label
            export.export()
            
            super(exportHolesReport_Gui, self).accept()
        except Exception, e:
            FreeCAD.Console.PrintWarning("{0} \n".format(e))
        
    def zmianaSciezkiF(self):
        ''' change output file path '''
        fileName = QtGui.QFileDialog().getExistingDirectory(None, 'Output directory', QtCore.QDir.homePath(), QtGui.QFileDialog.ShowDirsOnly)
        
        if fileName:
            self.pathToFile.setText(fileName)


##***********************************************************************
##*                             CONSOLE
##***********************************************************************
class exportHoles:
    def __init__(self):
        self.fileFormat = 'drl'
        self.filePath = str(QtCore.QDir.homePath())  # def. home directory
        self.fileName = 'untitled'  # def. value
        self.units = 'mm'  # mm/inch
        self.saveFormat = -2  # -2:Decimal   -3:Suppress leading zeros  -4:Suppress trailing zeros  -5:Keep zeros
        self.zeroPointDrilling = -2  # -2:Absolute   -3:Own - read from zeroPointDrilling_X/Y
        self.zeroPointDrilling_X = 0
        self.zeroPointDrilling_Y = 0
        self.mirror_X = False  # True/False
        self.mirror_Y = False  # True/False
        self.minimalHeader = False  # True/False
        self.groupHoles = False  # True/False
        
    def setUnit(self, value):
        if self.units == 'mm':
            return value
        else:
            return value

    def prepareX(self, value):
        value = self.setUnit(value)
        
        if self.mirror_X:
            value *= -1
        
        if self.zeroPointDrilling == -3:
            value -= self.zeroPointDrilling_X

        value = self.setSaveFormat(value)
        
        return value
        
    def prepareY(self, value):
        value = self.setUnit(value)
        
        if self.mirror_Y:
            value *= -1
        
        if self.zeroPointDrilling == -3:
            value -= self.zeroPointDrilling_Y

        value = self.setSaveFormat(value)
        
        return value
    
    def setSaveFormat(self, value):
        if value < 0:
            char = '-'
        else:
            char = ''
        
        value = ('%3.3f' % value).replace('-', '').split('.')

        if self.saveFormat == -3:
            return '{0}{1}{2}'.format(char, value[0], value[1])
        elif self.saveFormat == -4:
            return '{0}{1}{2}'.format(char, value[0].rjust(3, '0'), value[1].rstrip('0'))
        elif self.saveFormat == -5:
            return '{0}{1}{2}'.format(char, value[0].rjust(3, '0'), value[1])
        else:  # self.saveFormat == -2
            return float('{0}{1}.{2}'.format(char, value[0], value[1]))

    def export(self):
        try:
            exportClass = eval(exportList[self.fileFormat]['class'])
            exportClass.fileName = self.fileName
            exportClass.filePath = self.filePath
            exportClass.holes = self.getHoles()
            exportClass.groupList = self.groupHoles
            exportClass.minimalHeader = self.minimalHeader
            exportClass.unit = self.units
            exportClass.fromat = __saveFormats__[self.saveFormat * (-1) -2]
            exportClass.zeroPointDrilling = __zeroPointDrilling__[self.zeroPointDrilling * (-1) -2]
            if not self.zeroPointDrilling == -2:
                exportClass.zeroPointDrilling_X = self.zeroPointDrilling_X
                exportClass.zeroPointDrilling_Y = self.zeroPointDrilling_Y
            
            exportClass.export()
        except Exception, e:
            FreeCAD.Console.PrintWarning("{0} \n".format(e))
    
    def getHoles(self):
        holes = {}
        #
        for i in FreeCAD.ActiveDocument.Board.Holes.Geometry:
            if str(i.__class__) == "<type 'Part.GeomCircle'>" and not i.Construction:
                x = self.prepareX(i.Center[0])
                y = self.prepareY(i.Center[1])
                d = self.setUnit(i.Radius) * 2.0
                
                if not d in holes.keys():
                    holes[d] = []
                
                holes[d].append([x, y])
        #
        return holes


class exportHolesReport(exportHoles):
    def __init__(self):
        exportHoles.__init__(self)
        
        self.fileFormat = 'rpt'
        self.filePath = str(QtCore.QDir.homePath())  # def. home directory
        self.fileName = 'untitled'  # def. value
    
    def export(self):
        holes = self.getHoles()
        #
        fileName = os.path.join(self.filePath, self.fileName)
        if not fileName.endswith('rpt'):
            fileName = fileName + '.rpt'
        
        self.files = codecs.open(fileName, "w", "utf-8")
        #
        self.files.write('Drill report for {0}\n'.format(self.fileName))
        self.files.write('Created on {0}\n'.format(datetime.datetime.now()))
        self.files.write('Drill report for plated through holes:\n')
        
        num = 0
        for i in range(len(holes.keys())):
            self.files.write('T{0}  {1}mm  {2}"  ({3} holes)\n'.format(i + 1, '%.2f' % holes.keys()[i], '%.3f' % (float(holes.keys()[i]) / 25.4), len(holes[holes.keys()[i]])))
            num += len(holes[holes.keys()[i]])
        
        self.files.write('\nTotal plated holes count: {0}\n'.format(num))
        #
        self.files.close()

##
class exportFileMain():
    def __init__(self):
        self.exportHeaders = ['Diameter', 'X', 'Y']
        self.fileName = ''
        self.filePath = ''
        self.holes = {}
        self.groupList = False
        self.minimalHeader = False
        self.unit = 'mm'
        self.fromat = -2
        self.zeroPointDrilling = -2
        self.zeroPointDrilling_X = 0
        self.zeroPointDrilling_Y = 0


class drl(exportFileMain):
    ''' Export holes to *.csv '''
    def __init__(self, parent=None):
        exportFileMain.__init__(self)

    def export(self):
        '''export(filePath): save holes to drl file
            filePath -> strig
            filePath = path/fileName.drl'''
        fileName = os.path.join(self.filePath, self.fileName)
        if not fileName.endswith('drl'):
            fileName = fileName + '.drl'
        
        self.files = codecs.open(fileName, "w", "utf-8")
        #######
        #header
        self.files.write('M48\n')  # The beginning of a header 
        
        if not self.minimalHeader:
            self.files.write(';Drill file\n')
            self.files.write(';Project: {0}\n'.format(self.fileName))
            self.files.write(';Date: {0}\n'.format(datetime.datetime.now()))
            self.files.write(';Unit: {0}\n'.format(self.unit))
            self.files.write(';Format: {0}\n'.format(self.fromat))
            self.files.write(';Zero point drilling: {0} ({1} x {2})\n'.format(self.zeroPointDrilling, self.zeroPointDrilling_X, self.zeroPointDrilling_Y))
        
        self.files.write('R,C\n')  # Reset Clocks
        self.files.write('R,H\n')  # Reset Hits
        self.files.write('R,T\n')  # Reset Tool Information
        
        self.files.write('VER,1\n')  # Use Version 1 X and Y axis layout 
        
        if self.unit == 'mm':
            self.files.write('METRIC')  # Measure Everything in Metric 
        else:
            self.files.write('INCH')  # Measure Everything in Inches 
        
        if self.fromat == __saveFormats__[2]:
            self.files.write(',LZ\n')  # leading zeros 
        else:
            self.files.write(',TZ\n')  # trailing zeros
        
        self.files.write('FMAT,2\n')  # 
        # tools
        for i in range(len(self.holes.keys())):
            self.files.write('T{0}C{1}\n'.format(i + 1, self.holes.keys()[i]))
        #
        self.files.write('%\n')
        self.files.write('M47,DRILL\n')  # Message
        self.files.write('G90\n')  # Absolute Mode
        self.files.write('G05\n')  # Drill Mode
        
        if self.unit == 'mm':
            self.files.write('M71\n')  # Metric Measuring Mode 
        else:
            self.files.write('M72\n')  # Inch Measuring Mode 
        # holes
        for i in range(len(self.holes.keys())):
            self.files.write('T{0}\n'.format(i + 1))
            for j in self.holes[self.holes.keys()[i]]:
                self.files.write('X{0}Y{1}\n'.format(j[0], j[1]))
            
        #self.files.write('T0\n')
        # end
        self.files.write('M95\n')  # End of the header 
        #######
        self.files.close()


class txt(exportFileMain):
    ''' Export BOM to *.txt '''
    def __init__(self):
        exportFileMain.__init__(self)

    def addTitle(self, num):
        return self.exportHeaders[num]
        
    def export(self):
        '''export(filePath): save holes to txt file
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
            self.files.write('Unit: {0}\n'.format(self.unit))
            self.files.write('Format: {0}\n'.format(self.fromat))
            self.files.write('Zero point drilling: {0} ({1} x {2})\n'.format(self.zeroPointDrilling, self.zeroPointDrilling_X, self.zeroPointDrilling_Y))
            self.files.write('\n\n')
        #
        self.exportHoles()
        #
        self.files.close()

    def exportHoles(self):
        #  get param.
        kolumny = [0, 0, 0]
        for i in self.holes.keys():
            if len(str(i)) > kolumny[0]:  # diameter
                kolumny[0] = len(str(i))
            
            for j in self.holes[i]:
                if len(str(j[0])) > kolumny[1]:    # x
                    kolumny[1] = len(str(j[0]))
                if len(str(j[1])) > kolumny[2]:    # y
                    kolumny[2] = len(str(j[1]))
        # headers
        self.files.write(self.addTitle(0).ljust(kolumny[0] + 10))
        self.files.write(self.addTitle(1).ljust(kolumny[1] + 10))
        self.files.write(self.addTitle(2).ljust(kolumny[2] + 10))
        self.files.write("\n")
        # write param. to file
        for i in self.holes.keys():  # package
            if self.groupList:
                self.files.write(str(i).ljust(kolumny[0] + 10))
                self.files.write("\n")
            
            for j in self.holes[i]:  # value
                if self.groupList:
                    self.files.write(str(' ').ljust(kolumny[0] + 10))
                else:
                    self.files.write(str(i).ljust(kolumny[0] + 10))
                self.files.write(str(j[0]).ljust(kolumny[1] + 10))
                self.files.write(str(j[1]).ljust(kolumny[2] + 10))
                self.files.write("\n")


class html(exportFileMain):
    ''' Export BOM to *.html '''
    def __init__(self):
        exportFileMain.__init__(self)
        
    def addTitle(self):
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
        <p><h1>Drill file</h1></p>
         """)
        
        if not self.minimalHeader:
            self.files.write('<p><span style="font-weight:bold">Project:</span> {0}</p>'.format(self.fileName))
            self.files.write('<p><span style="font-weight:bold">Date:</span> {0}</p>'.format(datetime.datetime.now()))
            self.files.write('<p><span style="font-weight:bold">Unit:</span> {0}</p>'.format(self.unit))
            self.files.write('<p><span style="font-weight:bold">Format:</span> {0}</p>'.format(self.fromat))
            self.files.write('<p><span style="font-weight:bold">Zero point drilling:</span> {0} ({1} x {2})</p>'.format(self.zeroPointDrilling, self.zeroPointDrilling_X, self.zeroPointDrilling_Y))
        
        self.files.write('''<p><table>''')
        
    def fileFooter(self):
        self.files.write("""
            </table>
        </p>
        <div class='stopka'></div>
    </body>
</html>""")
    
    def export(self):
        '''export(filePath): save holes to html file
            filePath -> strig
            filePath = path/fileName.html'''
        fileName = os.path.join(self.filePath, self.fileName)
        if not fileName.endswith('html'):
            fileName = fileName + '.html'
        
        self.files = codecs.open(fileName, "w", "utf-8")
        self.fileHeader()
        self.addTitle()
        #
        self.exportHoles()
        #
        self.fileFooter()
        self.files.close()
    
    def exportHoles(self):
        for i in self.holes.keys():
            if self.groupList:
                self.files.write("<tr><td>{0}</td><td></td><td></td></tr>\n".format(i))
            for j in self.holes[i]:
                if self.groupList:
                    self.files.write("<tr><td></td><td>{0}</td><td>{1}</td></tr>\n".format(j[0], j[1]))
                else:
                    self.files.write("<tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>\n".format(i, j[0], j[1]))


class csv(exportFileMain):
    ''' Export holes to *.csv '''
    def __init__(self):
        exportFileMain.__init__(self)
        
    def addTitle(self):
        if not self.minimalHeader:
            self.files.write('Drill file\n')
            self.files.write('Project:;{0}\n'.format(self.fileName))
            self.files.write('Date;{0}\n'.format(datetime.datetime.now()))
            self.files.write('Unit;{0}\n'.format(self.unit))
            self.files.write('Format;{0}\n'.format(self.fromat))
            self.files.write('Zero point drilling;{0} ({1} x {2})\n'.format(self.zeroPointDrilling, self.zeroPointDrilling_X, self.zeroPointDrilling_Y))
            self.files.write('\n\n')
        
        self.files.write((';').join(self.exportHeaders) + '\n')
        
    def export(self):
        '''export(filePath): save holes to csv file
            filePath -> strig
            filePath = path/fileName.csv'''
        fileName = os.path.join(self.filePath, self.fileName)
        if not fileName.endswith('csv'):
            fileName = fileName + '.csv'

        self.files = codecs.open(fileName, "w", "utf-8")
        self.addTitle()
        #
        self.exportHoles()
        #
        self.files.close()
        
    def exportHoles(self):
        for i in self.holes.keys():
            if self.groupList:
                self.files.write("{0};;\n".format(i))
            for j in self.holes[i]:
                if self.groupList:
                    self.files.write(";{0};{1}\n".format(j[0], j[1]))
                else:
                    self.files.write("{0};{1};{2}\n".format(i, j[0], j[1]))
