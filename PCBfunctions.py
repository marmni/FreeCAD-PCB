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
from PySide import QtCore, QtGui
import os
import time
from shutil import copy2, make_archive, rmtree
import configparser
import glob
import zipfile
import tempfile
#import sys
from math import sqrt, atan2, sin, cos, radians, pi, hypot, atan
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
            
        with open(os.path.join(__currentPath__, 'PCBsettings.cfg'), 'wb') as configfile:
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
        filePathLayout.addWidget(filePathButton)
        filePathLayout.setContentsMargins(0, 0, 0, 0)
        
        # tabs
        self.tabs = QtGui.QTabWidget()
        self.tabs.setTabPosition(QtGui.QTabWidget.West)
        self.tabs.setObjectName('tabs_widget')
        self.tabs.addTab(self.tabCategories(), u'Categories')
        self.tabs.addTab(self.tabModels(), u'Models')
        self.tabs.addTab(self.tabSettings(), u'FreeCAD settings')
        self.tabs.setTabEnabled(0, False)
        self.tabs.setTabEnabled(1, False)
        self.tabs.setTabEnabled(2, False)
        self.connect(self.tabs, QtCore.SIGNAL("currentChanged (int)"), self.activeModelsTab)
        
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
    
    def activeModelsTab(self, num):
        if num == 1:
            self.loadModels()

    def modelsListsetRowColor(self, item, color):
        item.setBackground(0, QtGui.QBrush(QtGui.QColor(color[0], color[1], color[2])))
        item.setBackground(1, QtGui.QBrush(QtGui.QColor(color[0], color[1], color[2])))
        item.setBackground(2, QtGui.QBrush(QtGui.QColor(color[0], color[1], color[2])))
        item.setBackground(3, QtGui.QBrush(QtGui.QColor(color[0], color[1], color[2])))
        #item.setBackground(4, QtGui.QBrush(QtGui.QColor(color[0], color[1], color[2])))
    
    def modelsLoadCategories(self):
        ''' main items '''
        categories = {}
        # Without category
        mainItem = QtGui.QTreeWidgetItem([u'Models without category'])
        mainItem.setData(0, QtCore.Qt.UserRole, -1)
        mainItem.setData(0, QtCore.Qt.UserRole + 1, '')
        self.modelsTable.addTopLevelItem(mainItem)
        self.modelsTable.setFirstItemColumnSpanned(mainItem, True)
        categories[-1] = mainItem
        # omitted models
        mainItem = QtGui.QTreeWidgetItem([u'Omitted models'])
        mainItem.setData(0, QtCore.Qt.UserRole, -2)
        mainItem.setData(0, QtCore.Qt.UserRole + 1, -2)
        self.modelsTable.addTopLevelItem(mainItem)
        self.modelsTable.setFirstItemColumnSpanned(mainItem, True)
        categories[-2] = mainItem
        #
        try:
            for i in range(self.categoriesTable.rowCount()):
                if self.categoriesTable.cellWidget(i, 0).isChecked():
                    oldCategoryID = int(self.categoriesTable.item(i, 1).text())
                    if self.categoriesTable.cellWidget(i, 4).currentIndex() == 0:
                        mainItem = QtGui.QTreeWidgetItem(['{0} (New category)'.format(self.categoriesTable.item(i, 2).text())])
                        mainItem.setData(0, QtCore.Qt.UserRole, 'New')
                        mainItem.setData(0, QtCore.Qt.UserRole + 3, "<span style='font-weight:bold;'>New category '{0}' will be added.</span>".format(self.categoriesTable.item(i, 2).text()))  # info
                    else:
                        categoryData = self.categoriesTable.cellWidget(i, 4).itemData(self.categoriesTable.cellWidget(i, 4).currentIndex())
                        
                        mainItem = QtGui.QTreeWidgetItem(['{1} (Existing category {0})'.format(categoryData[1], self.categoriesTable.item(i, 2).text())])
                        mainItem.setData(0, QtCore.Qt.UserRole, 'Old')
                        mainItem.setData(0, QtCore.Qt.UserRole + 3, "<span style='font-weight:bold;'>All entries from category '{1}' will be shifted to the existing '{0}'.</span>".format(categoryData[1], self.categoriesTable.item(i, 2).text()))  # info
                    
                    mainItem.setData(0, QtCore.Qt.UserRole + 1, i)  # category row number
                    self.modelsTable.addTopLevelItem(mainItem)
                    self.modelsTable.setFirstItemColumnSpanned(mainItem, True)
                    
                    categories[oldCategoryID] = mainItem
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR: {0}.\n".format(e))
        #
        return categories
    
    def tabCategories(self):
        tab = QtGui.QWidget()
        
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
        
        # table
        self.categoriesTable = QtGui.QTableWidget()
        self.categoriesTable.setStyleSheet('''border:0px solid red;''')
        self.categoriesTable.setColumnCount(5)
        self.categoriesTable.setGridStyle(QtCore.Qt.DashDotLine)
        self.categoriesTable.setHorizontalHeaderLabels([' Active ', 'ID', 'Name', 'Description', 'Action'])
        self.categoriesTable.verticalHeader().hide()
        self.categoriesTable.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.categoriesTable.horizontalHeader().setStretchLastSection(True)
        self.categoriesTable.hideColumn(1)
        
        # main lay
        layTableButtons = QtGui.QHBoxLayout()
        layTableButtons.addWidget(selectAll)
        layTableButtons.addWidget(unselectAll)
        layTableButtons.addStretch(10)
        
        lay = QtGui.QGridLayout(tab)
        lay.addLayout(layTableButtons, 0, 0, 1, 1)
        lay.addWidget(self.categoriesTable, 1, 0, 1, 1)
        lay.setRowStretch(1, 10)
        lay.setColumnStretch(0, 10)
        lay.setContentsMargins(5, 5, 5, 5)
        
        return tab
    
    def showInfoF(self, item, num):
        self.showInfo.setText(item.data(0, QtCore.Qt.UserRole + 3))
        
    def tabSettings(self):
        tab = QtGui.QWidget()
        
        return tab
        
    def tabModels(self):
        tab = QtGui.QWidget()
        
        # table
        self.modelsTable = QtGui.QTreeWidget()
        #self.modelsTable.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.modelsTable.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.modelsTable.setHeaderLabels([u'Name', u'Description', u'Paths', u'Softwares'])
        self.modelsTable.setStyleSheet('''
            QTreeWidget {border:0px solid #FFF;}
        ''')
        self.connect(self.modelsTable, QtCore.SIGNAL("itemPressed (QTreeWidgetItem*,int)"), self.showInfoF)
        # buttons
        selectAll = QtGui.QPushButton()
        selectAll.setFlat(True)
        selectAll.setToolTip('Select all')
        selectAll.setIcon(QtGui.QIcon(":/data/img/checkbox_checked_16x16.png"))
        selectAll.setStyleSheet('''border:1px solid rgb(237, 237, 237);''')
        self.connect(selectAll, QtCore.SIGNAL("clicked()"), self.selectAllModels)
        
        unselectAll = QtGui.QPushButton()
        unselectAll.setFlat(True)
        unselectAll.setToolTip('Deselect all')
        unselectAll.setIcon(QtGui.QIcon(":/data/img/checkbox_unchecked_16x16.PNG"))
        unselectAll.setStyleSheet('''border:1px solid rgb(237, 237, 237);''')
        self.connect(unselectAll, QtCore.SIGNAL("clicked()"), self.unselectAllModels)
        
        collapseAll = QtGui.QPushButton()
        collapseAll.setFlat(True)
        collapseAll.setToolTip('Collapse all')
        collapseAll.setIcon(QtGui.QIcon(":/data/img/collapse.png"))
        collapseAll.setStyleSheet('''border:1px solid rgb(237, 237, 237);''')
        self.connect(collapseAll, QtCore.SIGNAL("clicked()"), self.modelsTable.collapseAll)
        
        expandAll = QtGui.QPushButton()
        expandAll.setFlat(True)
        expandAll.setToolTip('Expand all')
        expandAll.setIcon(QtGui.QIcon(":/data/img/expand.png"))
        expandAll.setStyleSheet('''border:1px solid rgb(237, 237, 237);''')
        self.connect(expandAll, QtCore.SIGNAL("clicked()"), self.modelsTable.expandAll)
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
        lay.addWidget(self.modelsTable, 1, 0, 1, 1)
        lay.addWidget(self.showInfo, 2, 0, 1, 1)
        lay.setRowStretch(1, 10)
        lay.setColumnStretch(0, 10)
        lay.setContentsMargins(5, 5, 5, 5)
        
        return tab
    
    def selectAllCategories(self):
        if self.categoriesTable.rowCount() > 0:
            for i in range(self.categoriesTable.rowCount()):
                self.categoriesTable.cellWidget(i, 0).setCheckState(QtCore.Qt.Checked)
            
    def unselectAllCategories(self):
        if self.categoriesTable.rowCount() > 0:
            for i in range(self.categoriesTable.rowCount()):
                self.categoriesTable.cellWidget(i, 0).setCheckState(QtCore.Qt.Unchecked)
    
    def importDataBase(self):
        if self.importSettings['database']:
            #FreeCAD.Console.PrintWarning("\ntempfile: {0}\n".format(self.tmpDir))
            #
            try:
                self.importDatabase = dataBase()
                self.importDatabase.connect(os.path.join(self.tmpDir, "database.db"))
                
                self.originalDatabase = dataBase()
                self.originalDatabase.connect()
                #
                self.tabs.setTabEnabled(0, True)
                self.tabs.setTabEnabled(1, True)
                self.loadCategories()
            except Exception as e:
                FreeCAD.Console.PrintWarning("\nERROR: {0}.\n".format(e))
    
    def loadModels(self):
        self.modelsTable.clear()
        self.showInfo.setText('')
        categories = self.modelsLoadCategories()
        #
        try:
            for i in self.importDatabase.getAllModels():
                data = self.importDatabase.convertToTable(i)
                #
                modelName = data['name']
                modelID = data['id']
                modelDescription = data['description']
                modelPaths = data['path3DModels'].split(';')
                
                # models
                mainModel = QtGui.QTreeWidgetItem([modelName, modelDescription, '\n'.join(modelPaths)])
                mainModel.setData(0, QtCore.Qt.UserRole, 'PM')
                mainModel.setData(0, QtCore.Qt.UserRole + 1, modelID)
                mainModel.setData(0, QtCore.Qt.UserRole + 2, data)  # str representation
                
                if len(modelPaths) == 0 or modelName == '':  # Corrupt entry - this is no error
                    self.modelsListsetRowColor(mainModel, [255, 166 , 166])
                    mainModel.setData(0, QtCore.Qt.UserRole + 3, "<span style='font-weight:bold; color: #F00;'>Info: Corrupt entry!</span>")  # info
               
                # packages
                errors = 0
                errorsID = -1
                modelSoftware = self.importDatabase.getPackagesByModelID(modelID)
                
                for j in modelSoftware:
                    packageData = self.importDatabase.convertToTable(j)
                    #
                    softwareModel = packageData['name']
                    softwareName = packageData['software']
                    position = "X:{0} ;Y:{1} ;Z:{2} ;RX:{3} ;RY:{4} ;RZ:{5}".format(packageData['x'], packageData['y'], packageData['z'], packageData['rx'], packageData['ry'], packageData['rz'])
                    #
                    childModel = QtGui.QTreeWidgetItem([softwareName, softwareModel, position])
                    childModel.setData(0, QtCore.Qt.UserRole, 'M')  # correct model definition
                    childModel.setData(0, QtCore.Qt.UserRole + 2, j)  # str representation
                    
                    if self.originalDatabase.findPackage(softwareModel, softwareName):
                        packageDataOriginal = self.importDatabase.convertToTable(self.originalDatabase.findPackage(softwareModel, softwareName))
                        
                        errors += 1
                        childModel.setData(0, QtCore.Qt.UserRole, 'ER')
                        
                        if errorsID == -1:
                            errorsID = packageDataOriginal['id']
                        
                        self.modelsListsetRowColor(childModel, [255, 166 , 166])
                        childModel.setData(0, QtCore.Qt.UserRole + 3, "<span style='font-weight:bold; color: #F00;'>Error: Model is already defined in database.</span>")  # info
                    else:
                        childModel.setCheckState(0, QtCore.Qt.Unchecked)
                    
                    if modelSoftware.count() > errors > 0:
                        mainModel.setData(0, QtCore.Qt.UserRole + 4, errorsID)
                    elif errors == 0:
                        mainModel.setData(0, QtCore.Qt.UserRole + 4, 'new')
                    
                    mainModel.addChild(childModel)
                #######
                if errors == modelSoftware.count():
                    categories[-2].addChild(mainModel)
                else:
                    try:
                        categories[data['categoryID']].addChild(mainModel)
                    except:  # 
                        categories[-1].addChild(mainModel)  # models without category
        except Exception as e:
            pass
            
    def clearCategories(self):
        for i in range(self.categoriesTable.rowCount(), 0, -1):
            self.categoriesTable.removeRow(i - 1)
    
    def loadCategories(self):
        for i in self.importDatabase.getAllcategories():
            categoryInfo = self.importDatabase.convertToTable(i)
            #FreeCAD.Console.PrintWarning("\ncategoryInfo: {0}.\n".format(categoryInfo))
            
            rowNumber = self.categoriesTable.rowCount()
            self.categoriesTable.insertRow(rowNumber)
            #######
            widgetActive = QtGui.QCheckBox('')
            widgetActive.setStyleSheet('margin-left:18px;')
            self.categoriesTable.setCellWidget(rowNumber, 0, widgetActive)
            #
            itemID = QtGui.QTableWidgetItem(str(categoryInfo['id']))
            self.categoriesTable.setItem(rowNumber, 1, itemID)
            #
            itemName = QtGui.QTableWidgetItem(categoryInfo['name'])
            self.categoriesTable.setItem(rowNumber, 2, itemName)
            
            itemDescription = QtGui.QTableWidgetItem(categoryInfo['description'])
            self.categoriesTable.setItem(rowNumber, 3, itemDescription)
            # new category
            widgetAction = QtGui.QComboBox()
            widgetAction.addItem('New category', [-1, ''])  # new category
            
            nr = 1
            for j in self.originalDatabase.getAllcategories():
                data = self.originalDatabase.convertToTable(j)
                
                widgetAction.addItem('Move all objects to existing category: {0}'.format(data['name']), [data['id'], data['name']])
                if data['name'] == categoryInfo['name']:
                    widgetAction.setCurrentIndex(nr)
                nr += 1
            self.categoriesTable.setCellWidget(rowNumber, 4, widgetAction)

    def importFreeCADSettings(self):
        self.tabs.setTabEnabled(2, True)
      
    def chooseFile(self):
        self.clearCategories()
        self.tabs.setTabEnabled(0, False)
        self.tabs.setTabEnabled(1, False)
        self.tabs.setTabEnabled(2, False)
        
        newDatabase = QtGui.QFileDialog.getOpenFileName(None, u'Choose file to import', os.path.expanduser("~"), '*.zip')
        if newDatabase[0].strip() != '' and self.checkFile(newDatabase[0].strip()):
            self.filePath.setText(newDatabase[0])
            #
            self.importDataBase()
            self.importFreeCADSettings()
    
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
        
    def selectAllModels(self):
        for i in QtGui.QTreeWidgetItemIterator(self.modelsTable):
            if i.value().data(0, QtCore.Qt.UserRole) == 'M':
                i.value().setCheckState(0, QtCore.Qt.Checked)
    
    def unselectAllModels(self):
        for i in QtGui.QTreeWidgetItemIterator(self.modelsTable):
            if i.value().data(0, QtCore.Qt.UserRole) == 'M':
                i.value().setCheckState(0, QtCore.Qt.Unchecked)


class prepareScriptCopy(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u"Save database copy")
        self.setWindowIcon(QtGui.QIcon(":/data/img/databaseExport.png"))
        #
        self.optionSaveDatabase = QtGui.QCheckBox("Database")
        self.optionSaveModels = QtGui.QCheckBox("Models")
        self.optionSaveFreecadSettings = QtGui.QCheckBox("FreeCAD settings")
        
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
        QtGui.qApp.processEvents()
    
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
