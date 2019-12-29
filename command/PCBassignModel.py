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

from PySide import QtCore, QtGui
import os
import FreeCAD, FreeCADGui, Part
import glob
import sys
#
from PCBdataBase import dataBase
from PCBconf import defSoftware, partPaths
from PCBfunctions import getFromSettings_databasePath, kolorWarstwy, prepareScriptCopy, importScriptCopy
from PCBcategories import addCategoryGui, removeCategoryGui, updateCategoryGui, setOneCategoryGui, categorySelector
from PCBpartManaging import partExistPath, partsManaging
from PCBobjects import *
__currentPath__ = os.path.dirname(os.path.abspath(__file__))


class addModelDialog(QtGui.QDialog):
    def __init__(self, mod, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowIcon(QtGui.QIcon(":/data/img/uklad.png"))

        if mod == 0:
            self.setWindowTitle(u"Add new model")
        else:
            self.setWindowTitle(u"Edit model")
        
        ########################
        # model type
        ########################
        self.packageName = QtGui.QLineEdit("")
        
        ########################
        # software
        ########################
        self.supSoftware = QtGui.QComboBox()
        for i in defSoftware:
            self.supSoftware.addItem(i)
        freecadSettings = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB")
        self.supSoftware.setCurrentIndex(self.supSoftware.findText(defSoftware[freecadSettings.GetInt("pcbDefaultSoftware", 0)]))
        
        ########################
        # rotation / shift
        ########################
        self.pozX = QtGui.QDoubleSpinBox()
        self.pozX.setRange(-1000, 1000)
        self.pozX.setSuffix(" mm")
        self.pozY = QtGui.QDoubleSpinBox()
        self.pozY.setRange(-1000, 1000)
        self.pozY.setSuffix(" mm")
        self.pozZ = QtGui.QDoubleSpinBox()
        self.pozZ.setRange(-1000, 1000)
        self.pozZ.setSuffix(" mm")
        self.pozRX = QtGui.QDoubleSpinBox()
        self.pozRX.setRange(-1000, 1000)
        self.pozRX.setSuffix(" deg")
        self.pozRY = QtGui.QDoubleSpinBox()
        self.pozRY.setRange(-1000, 1000)
        self.pozRY.setSuffix(" deg")
        self.pozRZ = QtGui.QDoubleSpinBox()
        self.pozRZ.setRange(-1000, 1000)
        self.pozRZ.setSuffix(" deg")
        ukladWspolrzednych = QtGui.QLabel("")
        ukladWspolrzednych.setPixmap(QtGui.QPixmap(":/data/img/uklad.png"))
        
        layWspolrzedne = QtGui.QGridLayout()
        layWspolrzedne.setContentsMargins(0, 10, 0, 20)
        layWspolrzedne.addWidget(ukladWspolrzednych, 0, 0, 6, 1, QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        layWspolrzedne.addWidget(QtGui.QLabel("X"), 0, 1, 1, 1, QtCore.Qt.AlignRight)
        layWspolrzedne.addWidget(self.pozX, 0, 2, 1, 1, QtCore.Qt.AlignTop)
        layWspolrzedne.addWidget(QtGui.QLabel("Y"), 1, 1, 1, 1, QtCore.Qt.AlignRight)
        layWspolrzedne.addWidget(self.pozY, 1, 2, 1, 1, QtCore.Qt.AlignTop)
        layWspolrzedne.addWidget(QtGui.QLabel("Z"), 2, 1, 1, 1, QtCore.Qt.AlignRight)
        layWspolrzedne.addWidget(self.pozZ, 2, 2, 1, 1, QtCore.Qt.AlignTop)
        layWspolrzedne.addWidget(QtGui.QLabel("RX"), 3, 1, 1, 1, QtCore.Qt.AlignRight)
        layWspolrzedne.addWidget(self.pozRX, 3, 2, 1, 1, QtCore.Qt.AlignTop)
        layWspolrzedne.addWidget(QtGui.QLabel("RY"), 4, 1, 1, 1, QtCore.Qt.AlignRight)
        layWspolrzedne.addWidget(self.pozRY, 4, 2, 1, 1, QtCore.Qt.AlignTop)
        layWspolrzedne.addWidget(QtGui.QLabel("RZ"), 5, 1, 1, 1, QtCore.Qt.AlignRight)
        layWspolrzedne.addWidget(self.pozRZ, 5, 2, 1, 1, QtCore.Qt.AlignTop)
        layWspolrzedne.setRowStretch(6, 10)
        layWspolrzedne.setColumnStretch(2, 10)
        
        ########################
        # buttons
        ########################
        buttons = QtGui.QDialogButtonBox()
        buttons.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
        if mod == 0:
            buttons.addButton("Add", QtGui.QDialogButtonBox.AcceptRole)
        else:
            buttons.addButton("Save", QtGui.QDialogButtonBox.AcceptRole)
        self.connect(buttons, QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        self.connect(buttons, QtCore.SIGNAL("rejected()"), self, QtCore.SLOT("reject()"))
        
        ########################
        # layouts
        ########################
        mainLay = QtGui.QGridLayout()
        mainLay.addWidget(QtGui.QLabel(u"Package name"), 0, 0, 1, 1)
        mainLay.addWidget(self.packageName, 0, 1, 1, 1)
        mainLay.addWidget(QtGui.QLabel(u"Software"), 2, 0, 1, 1)
        mainLay.addWidget(self.supSoftware, 2, 1, 1, 1)
        mainLay.addLayout(layWspolrzedne, 3, 0, 1, 2)
        mainLay.addWidget(buttons, 4, 0, 1, 2)
        mainLay.setColumnStretch(1, 10)
        self.setLayout(mainLay)

    #def accept(self):
        #if str(self.packageName.text()).strip() == "":
            #FreeCAD.Console.PrintWarning("Mandatory field is empty!.\n")
            #return False
        #return True


class pathChooser(QtGui.QTreeView):
    def __init__(self, parent=None):
        QtGui.QTreeView.__init__(self, parent)
        self.parent = parent
        #
        model = QtGui.QFileSystemModel()
        model.setFilter(QtCore.QDir.AllEntries | QtCore.QDir.NoDot | QtCore.QDir.NoDotDot | QtCore.QDir.Hidden)
        model.setNameFilters(["*.stp", "*.step", "*.igs", "*.iges"])
        model.setRootPath(QtCore.QDir().homePath())
        
        self.setSortingEnabled(False)
        self.setModel(model)
        self.setAlternatingRowColors(True)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.header().setResizeMode(QtGui.QHeaderView.Stretch)
        self.hideColumn(1)
        self.hideColumn(2)
        self.hideColumn(2)
        self.hideColumn(3)
        self.setStyleSheet('''QTreeView {border:1px solid rgb(199, 199, 199);}''')
    
    def selectionChanged(self, item1, item2):
        item = self.selectedIndexes()
        if len(item):
            self.parent.setNewPath(item[0].model().filePath(item[0]))
        
        return super(pathChooser, self).selectionChanged(item1, item2)


class addNewPath(QtGui.QDialog):
    def __init__(self, lista, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowIcon(QtGui.QIcon(":/data/img/uklad.png"))
        self.setWindowTitle(u"Paths")
        #
        self.pathChooser = pathChooser(self)
        #
        self.path = QtGui.QLineEdit('')
        #
        self.pathsList = QtGui.QListWidget()
        self.pathsList.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked | QtGui.QAbstractItemView.EditKeyPressed)
        #self.pathsList.setStyleSheet('''QListWidget:item:selected:active {background: rgb(215, 243, 255);} ''')
        #
        librariesList = QtGui.QComboBox()
        librariesList.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToMinimumContentsLength)
        
        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("partsPaths", "").strip() != '':
            librariesList.addItems(FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("partsPaths", "").split(','))
        else:
            librariesList.addItem(__currentPath__.replace('command', 'parts'))
            
        librariesList.addItem(u'Whole computer')
        #
        addPathButton = QtGui.QPushButton(u'Add')
        self.connect(addPathButton, QtCore.SIGNAL("clicked()"), self.addNewPath)
        
        removePathButton = QtGui.QPushButton(u'Remove paths')
        self.connect(removePathButton, QtCore.SIGNAL("clicked ()"), self.removePath)
        
        editPathButton = QtGui.QPushButton(u'Edit path')
        self.connect(editPathButton, QtCore.SIGNAL("clicked ()"), self.editPath)
        
        checkPathsButton = QtGui.QPushButton(u'Check paths')
        self.connect(checkPathsButton, QtCore.SIGNAL("clicked ()"), self.checkPaths)
        
        deleteColFileButton = QtGui.QPushButton(u'Delete *.col file')
        deleteColFileButton.setToolTip("For selected models")
        self.connect(deleteColFileButton, QtCore.SIGNAL("clicked ()"), self.deleteColFile)
        
        deleteAllColFilesButton = QtGui.QPushButton(u'Delete all *.col files')
        self.connect(deleteAllColFilesButton, QtCore.SIGNAL("clicked ()"), self.deleteAllColFiles)
        # buttons
        buttons = QtGui.QDialogButtonBox()
        buttons.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
        buttons.addButton("Save", QtGui.QDialogButtonBox.AcceptRole)
        self.connect(buttons, QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        self.connect(buttons, QtCore.SIGNAL("rejected()"), self, QtCore.SLOT("reject()"))
        #####
        layPathWidget = QtGui.QFrame()
        layPathWidget.setObjectName('lay_path_widget')
        layPathWidget.setStyleSheet('''#lay_path_widget {background-color:#fff; border:1px solid rgb(199, 199, 199); padding: 5px;}''')
        layPath = QtGui.QHBoxLayout(layPathWidget)
        layPath.addWidget(self.path)
        layPath.addWidget(addPathButton)
        layPath.setContentsMargins(0, 0, 0, 0)
        #
        layPathsListWidget = QtGui.QFrame()
        layPathsListWidget.setObjectName('lay_path_widget')
        layPathsListWidget.setStyleSheet('''#lay_path_widget {background-color:#fff; border:1px solid rgb(199, 199, 199); padding: 5px;} QListWidget {border:1px solid rgb(223, 223, 223);}''')
        layPathsLis = QtGui.QGridLayout(layPathsListWidget)
        layPathsLis.addWidget(self.pathsList, 0, 0, 8, 1)
        layPathsLis.addWidget(editPathButton, 0, 1, 1, 1)
        layPathsLis.addWidget(removePathButton, 1, 1, 1, 1)
        layPathsLis.addWidget(separator(), 2, 1, 1, 1)
        layPathsLis.addWidget(checkPathsButton, 3, 1, 1, 1)
        layPathsLis.addWidget(separator(), 4, 1, 1, 1)
        layPathsLis.addWidget(deleteColFileButton, 5, 1, 1, 1)
        layPathsLis.addWidget(deleteAllColFilesButton, 6, 1, 1, 1)
        layPathsLis.setContentsMargins(0, 0, 0, 0)
        #
        lay = QtGui.QGridLayout(self)
        lay.addWidget(self.pathChooser, 0, 0, 3, 2)
        lay.addWidget(QtGui.QLabel('Saved paths'), 3, 0, 1, 1)
        lay.addWidget(librariesList, 3, 1, 1, 1)
        lay.addWidget(layPathWidget, 0, 2, 1, 1)
        lay.addWidget(layPathsListWidget, 1, 2, 3, 1)
        lay.addWidget(buttons, 4, 0, 1, 3)
        lay.setRowStretch(2, 10)
        #
        self.loadlist(lista)
        self.connect(self.pathsList, QtCore.SIGNAL("itemChanged (QListWidgetItem*)"), self.checkPath)
        self.connect(librariesList, QtCore.SIGNAL("currentIndexChanged (const QString&)"), self.loadPath)
        librariesList.setCurrentIndex(0)
        self.loadPath(librariesList.currentText())
    
    def loadPath(self, value):
        try:
            if value == "Whole computer":
                self.pathChooser.setRootIndex(self.pathChooser.model().index('/'))
            else:
                self.pathChooser.setRootIndex(self.pathChooser.model().index(value))
        except Exception as e:
            FreeCAD.Console.PrintWarning("{0} \n".format(e))
            
    def setNewPath(self, path):
        self.path.setText(path)
    
    def addNewPath(self):
        if self.path.text().strip() == '':
            return
        #
        [boolValue, path] = partExistPath(self.path.text().strip())
        if boolValue:
            if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("partsPaths", "").strip() != '':
                pathsToModels = partPaths + FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("partsPaths", "").split(',')
            else:
                pathsToModels = partPaths
            
            for i in pathsToModels:
                if i.replace('\\', '/') in path.replace('\\', '/'):
                    self.addItem(path.replace('\\', '/').replace(i.replace('\\', '/'), '')[1:])  # relative path
                    return
            #
            self.addItem(path) # absolute path
        
    def editPath(self):
        if self.pathsList.currentRow() == -1:
            return
            
        self.pathsList.editItem(self.pathsList.currentItem())
        
    def checkPath(self, item):
        [boolValue, path] = partExistPath(item.text())
        
        if boolValue:
            item.setForeground(QtGui.QBrush(QtGui.QColor(72, 144, 0)))
            item.setData(QtCore.Qt.UserRole, path)
            if item.checkState() != QtCore.Qt.Checked:
                item.setCheckState(QtCore.Qt.Unchecked)
        else:
            item.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
            item.setCheckState(QtCore.Qt.Checked)
            item.setData(QtCore.Qt.UserRole, '')
    
    def checkPaths(self):
        for i in range(self.pathsList.count()):
            self.checkPath(self.pathsList.item(i))
            
    def addItem(self, path):
        item = QtGui.QListWidgetItem(path)
        #item.setData(QtCore.Qt.UserRole, absolutePath)
        self.checkPath(item)
        item.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
        self.pathsList.addItem(item)

    def loadlist(self, lista):
        for i in  lista.split(';'):
            if i == '':
                continue
            #
            self.addItem(i)
        
        self.pathsList.setCurrentRow(0)
    
    def deleteColFile(self):
        if self.pathsList.currentRow() == -1:
            return
        
        dial = QtGui.QMessageBox()
        dial.setText(u"Delete *.col file for selected model?")
        dial.setWindowTitle("Caution!")
        dial.setIcon(QtGui.QMessageBox.Question)
        delete_YES = dial.addButton('Yes', QtGui.QMessageBox.YesRole)
        dial.addButton('No', QtGui.QMessageBox.RejectRole)
        dial.exec_()
        
        if dial.clickedButton() == delete_YES:
            [boolValue, path] = partExistPath(self.pathsList.currentItem().text())
            path, extension = os.path.splitext(path)
            
            try:
                os.remove(path + ".col") 
            except:
                pass
    
    def deleteAllColFiles(self):
        dial = QtGui.QMessageBox()
        dial.setText(u"Delete all *.col files?")
        dial.setWindowTitle("Caution!")
        dial.setIcon(QtGui.QMessageBox.Question)
        delete_YES = dial.addButton('Yes', QtGui.QMessageBox.YesRole)
        dial.addButton('No', QtGui.QMessageBox.RejectRole)
        dial.exec_()
        
        if dial.clickedButton() == delete_YES:
            for i in range(self.pathsList.count()):
                [boolValue, path] = partExistPath(self.pathsList.item(i).text())
                path, extension = os.path.splitext(path)
                
                try:
                    os.remove(path + ".col") 
                except:
                    pass

    def removePath(self):
        if self.pathsList.currentRow() == -1:
            return
        
        dial = QtGui.QMessageBox()
        dial.setText(u"Delete all selected paths?")
        dial.setWindowTitle("Caution!")
        dial.setIcon(QtGui.QMessageBox.Question)
        delete_YES = dial.addButton('Yes', QtGui.QMessageBox.YesRole)
        dial.addButton('No', QtGui.QMessageBox.RejectRole)
        dial.exec_()
        
        if dial.clickedButton() == delete_YES:
            for i in range(self.pathsList.count(), 0, -1):
                if self.pathsList.item(i - 1).checkState() == QtCore.Qt.Checked:
                    self.pathsList.takeItem(i - 1)


class modelAdjustTable(QtGui.QTableWidget):
    def __init__(self, parent=None):
        QtGui.QTableWidget.__init__(self, parent)
        
        self.setColumnCount(12)
        self.setHorizontalHeaderLabels([u"", u"Parameter", "Visible", "X", "Y", "Z", "RZ", "Size", "Color", "Align", "Spin", "ID"])
        self.setColumnHidden(11, True)
        self.setSortingEnabled(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().hide()
        self.setGridStyle(QtCore.Qt.PenStyle(QtCore.Qt.NoPen))
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.setStyleSheet('''
                border: 1px solid #808080;
            ''')
        
        self.dataParam = {}

    def getData(self):
        table = {}
        #
        for i in range(0, self.rowCount(), 1):
            key = u"{0}".format(self.item(i, 1).text())
            table[key] = {
                'active': self.cellWidget(i, 0).isChecked(),
                'display': self.cellWidget(i, 2).currentText(),
                'x': self.cellWidget(i, 3).value(),
                'y': self.cellWidget(i, 4).value(),
                'z': self.cellWidget(i, 5).value(),
                'rz': self.cellWidget(i, 6).value(),
                'size': self.cellWidget(i, 7).value(),
                'color': self.cellWidget(i, 8).getColor(),
                'align': u"{0}".format(self.cellWidget(i, 9).currentText()),
                'spin': self.cellWidget(i, 10).currentText(),
                'id': int(self.item(i, 11).text())
            }
        #
        return table

    def updateType(self, key, data):
        if key in self.dataParam.keys():
            row = self.dataParam[key]
            #
            self.cellWidget(row, 0).setChecked(eval(str(data['active'])))
            self.cellWidget(row, 2).setCurrentIndex(self.cellWidget(row, 2).findText(str(data['display'])))
            self.cellWidget(row, 3).setValue(data['x'])
            self.cellWidget(row, 4).setValue(data['y'])
            self.cellWidget(row, 5).setValue(data['z'])
            self.cellWidget(row, 6).setValue(data['rz'])
            self.cellWidget(row, 7).setValue(data['size'])
            self.cellWidget(row, 8).setColor(self.cellWidget(row, 8).PcbColorToRGB(eval(data['color'])))
            self.cellWidget(row, 9).setCurrentIndex(self.cellWidget(row, 9).findText(data['align']))
            self.cellWidget(row, 10).setCurrentIndex(self.cellWidget(row, 2).findText(str(data['spin'])))
            self.item(row, 11).setText(str(data['id']))
        
    def resetTable(self):
        for i in range(0, self.rowCount(), 1):
            self.cellWidget(i, 0).setChecked(False)
            self.cellWidget(i, 2).setCurrentIndex(0)
            self.cellWidget(i, 3).setValue(0.0)
            self.cellWidget(i, 4).setValue(0.0)
            self.cellWidget(i, 5).setValue(0.0)
            self.cellWidget(i, 6).setValue(0.0)
            self.cellWidget(i, 7).setValue(1.27)
            self.cellWidget(i, 8).setColor([255, 255, 255])
            self.cellWidget(i, 9).setCurrentIndex(4)
            self.cellWidget(i, 10).setCurrentIndex(0)
            self.item(i, 11).setText(u"-1")
        
    def addRow(self, rowType):
        self.insertRow(self.rowCount())
        row = self.rowCount() - 1
        self.dataParam[rowType] = row
        
        b = QtGui.QCheckBox("")
        b.setToolTip(u"Active")
        self.setCellWidget(row, 0, b)
        
        a = QtGui.QTableWidgetItem(rowType)
        a.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.setItem(row, 1, a)
        
        c = QtGui.QComboBox()
        c.addItems(["True", "False"])
        self.setCellWidget(row, 2, c)
        
        d = QtGui.QDoubleSpinBox()
        d.setSingleStep(0.1)
        d.setRange(-1000, 1000)
        d.setSuffix("mm")
        self.setCellWidget(row, 3, d)
        
        e = QtGui.QDoubleSpinBox()
        e.setSingleStep(0.1)
        e.setRange(-1000, 1000)
        e.setSuffix("mm")
        self.setCellWidget(row, 4, e)
        
        f = QtGui.QDoubleSpinBox()
        f.setSingleStep(0.1)
        f.setRange(-1000, 1000)
        f.setSuffix("mm")
        self.setCellWidget(row, 5, f)
        
        d2 = QtGui.QDoubleSpinBox()
        d2.setSingleStep(0.1)
        d2.setRange(-1000, 1000)
        d2.setSuffix("deg")
        self.setCellWidget(row, 6, d2)
        
        g = QtGui.QDoubleSpinBox()
        g.setSingleStep(0.1)
        g.setValue(1.27)
        g.setSuffix("mm")
        self.setCellWidget(row, 7, g)
        
        color = kolorWarstwy()
        color.setToolTip(u"Click to change color")
        self.setCellWidget(row, 8, color)
        
        i = QtGui.QComboBox()
        i.addItems(["bottom-left", "bottom-center", "bottom-right", "center-left", "center", "center-right", "top-left", "top-center", "top-right"])
        i.setCurrentIndex(4)
        self.setCellWidget(row, 9, i)
        
        c2 = QtGui.QComboBox()
        c2.addItems(["True", "False"])
        self.setCellWidget(row, 10, c2)
        
        aa = QtGui.QTableWidgetItem('-1')
        self.setItem(row, 11, aa)
        #
        self.setColumnWidth(0, 25)


class modelSettingsTable(QtGui.QTableWidget):
    def __init__(self, parent=None):
        QtGui.QTableWidget.__init__(self, parent)
        
        self.setColumnCount(9)
        self.setHorizontalHeaderLabels([u"ID", u"Package name", u"Software", "X", "Y", "Z", "RX", "RY", "RZ"])
        self.setSortingEnabled(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().hide()
        self.setGridStyle(QtCore.Qt.PenStyle(QtCore.Qt.DashLine))
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)
        self.hideColumn(0)
        self.setStyleSheet('''
                border: 1px solid #808080;
            ''')
            
    def editModel(self):
        row = self.currentRow()
        if row != -1:
            self.editRow(row)
    
    def deleteModel(self):
        if self.currentRow() != -1:
            dial = QtGui.QMessageBox()
            dial.setText(u"Delete selected package?")
            dial.setWindowTitle("Caution!")
            dial.setIcon(QtGui.QMessageBox.Question)
            dial.addButton('No', QtGui.QMessageBox.RejectRole)
            usunT = dial.addButton('Yes', QtGui.QMessageBox.YesRole)
            dial.exec_()
                    
            if dial.clickedButton() == usunT:
                self.deleteRow(self.currentRow())
    
    def addNewModelCell(self, text, num):
        a = QtGui.QTableWidgetItem(str(text))
        a.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        a.setTextAlignment(QtCore.Qt.AlignCenter)
        self.setItem(self.rowCount() - 1, num, a)
    
    def copyModel(self):
        row = self.currentRow()
        if row != -1:
            dial = addModelDialog(0)
            #dial.packageName.setText(self.item(row, 0).text())
            dial.supSoftware.setCurrentIndex(dial.supSoftware.findText(self.item(row, 2).text(), QtCore.Qt.MatchExactly))
            dial.pozX.setValue(float(self.item(row, 3).text()))
            dial.pozY.setValue(float(self.item(row, 4).text()))
            dial.pozZ.setValue(float(self.item(row, 5).text()))
            dial.pozRX.setValue(float(self.item(row, 6).text()))
            dial.pozRY.setValue(float(self.item(row, 7).text()))
            dial.pozRZ.setValue(float(self.item(row, 8).text()))
            
            if dial.exec_():
                item = self.findItems(str(dial.supSoftware.currentText()), QtCore.Qt.MatchExactly)
                #if len(item):
                for i in item:
                    if str(dial.packageName.text()) == str(self.item(self.row(i), 0).text()):
                        FreeCAD.Console.PrintWarning("Part already exist.\n")
                        return False
                #
                data = {}
                data['id'] = -1
                data['name'] = dial.packageName.text().strip()
                data['software'] = dial.supSoftware.currentText()
                data['x'] = dial.pozX.value()
                data['y'] = dial.pozY.value()
                data['z'] = dial.pozZ.value()
                data['rx'] = dial.pozRX.value()
                data['ry'] = dial.pozRY.value()
                data['rz'] = dial.pozRZ.value()
                
                self.addRows([data])

    def addNewModel(self):
        dial = addModelDialog(0)
        if dial.exec_():
            item = self.findItems(str(dial.supSoftware.currentText()), QtCore.Qt.MatchExactly)
            #if len(item):
            for i in item:
                if str(dial.packageName.text()) == str(self.item(self.row(i), 0).text()):
                    FreeCAD.Console.PrintWarning("Part already exist.\n")
                    return False
            #
            data = {}
            data['id'] = -1
            data['name'] = dial.packageName.text().strip()
            data['software'] = dial.supSoftware.currentText()
            data['x'] = dial.pozX.value()
            data['y'] = dial.pozY.value()
            data['z'] = dial.pozZ.value()
            data['rx'] = dial.pozRX.value()
            data['ry'] = dial.pozRY.value()
            data['rz'] = dial.pozRZ.value()
            
            self.addRows([data])
                
    def deleteRow(self, row):
        #self.removeRow(row)
        self.hideRow(int(row))

    def editRow(self, row):
        dial = addModelDialog(1)
        
        dial.packageName.setText(self.item(row, 1).text())
        dial.supSoftware.setCurrentIndex(dial.supSoftware.findText(self.item(row, 2).text(), QtCore.Qt.MatchExactly))
        dial.pozX.setValue(float(self.item(row, 3).text()))
        dial.pozY.setValue(float(self.item(row, 4).text()))
        dial.pozZ.setValue(float(self.item(row, 5).text()))
        dial.pozRX.setValue(float(self.item(row, 6).text()))
        dial.pozRY.setValue(float(self.item(row, 7).text()))
        dial.pozRZ.setValue(float(self.item(row, 8).text()))
        
        if dial.exec_():
            self.item(row, 1).setText(dial.packageName.text().strip())
            self.item(row, 2).setText(dial.supSoftware.currentText())
            self.item(row, 3).setText(str(dial.pozX.value()))
            self.item(row, 4).setText(str(dial.pozY.value()))
            self.item(row, 5).setText(str(dial.pozZ.value()))
            self.item(row, 6).setText(str(dial.pozRX.value()))
            self.item(row, 7).setText(str(dial.pozRY.value()))
            self.item(row, 8).setText(str(dial.pozRZ.value()))
    
    def addRows(self, data):
        ''' '''
        for i in data:
            self.insertRow(self.rowCount())
            
            self.addNewModelCell(i['id'], 0)
            self.addNewModelCell(i['name'], 1)
            self.addNewModelCell(i['software'], 2)
            self.addNewModelCell(i['x'], 3)
            self.addNewModelCell(i['y'], 4)
            self.addNewModelCell(i['z'], 5)
            self.addNewModelCell(i['rx'], 6)
            self.addNewModelCell(i['ry'], 7)
            self.addNewModelCell(i['rz'], 8)
        
    def clear(self):
        for i in range(self.rowCount(), -1, -1):
            self.removeRow(i)
    
    def getData(self):
        result = []
        
        for i in range(self.rowCount()):
            data = {}
            try:
                data['id'] = int(self.item(i, 0).text())
            except:
                data['id'] = -1
            data['name'] = u"{0}".format(self.item(i, 1).text())
            data['software'] = self.item(i, 2).text()
            data['x'] = float(self.item(i, 3).text())
            data['y'] = float(self.item(i, 4).text())
            data['z'] = float(self.item(i, 5).text())
            data['rx'] = float(self.item(i, 6).text())
            data['ry'] = float(self.item(i, 7).text())
            data['rz'] = float(self.item(i, 8).text())
            data['blanked'] = self.isRowHidden(i)
            
            result.append(data)
        
        return  result

    def __str__(self):
        return str(self.getData())


class modelsList(QtGui.QTreeWidget):
    def __init__(self, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        #
        self.sql = None
        #
        self.setColumnCount(2)
        self.setHeaderLabels([u"Name", u"Description"])
        self.setSortingEnabled(True)
        self.checkItems = True
    
    def addNewModel(self, model):
        description = model.description
        description = description.replace("\n", " ")
        description = description[:50]
        
        mainItem = QtGui.QTreeWidgetItem([model.name, description])
        mainItem.setData(0, QtCore.Qt.UserRole, model.id)
        mainItem.setData(0, QtCore.Qt.UserRole + 1, "P")
        if self.checkItems:
            mainItem.setCheckState(0, QtCore.Qt.Unchecked)
        
        return mainItem

    def addNewItem(self, category):
        mainItem = QtGui.QTreeWidgetItem([category[0], category[1]['description']])
        mainItem.setData(0, QtCore.Qt.UserRole, category[1]['id'])
        mainItem.setData(0, QtCore.Qt.UserRole + 1, "C")
        mainItem.setIcon(0, QtGui.QIcon(QtGui.QPixmap(":/data/img/folder_open_22x22.png")))
        
        # models
        for i in self.sql.getAllModelsByCategory(category[1]['id']):
            mainItem.addChild(self.addNewModel(i))
        
        # sub categories
        for i in category[1]['sub'].items():
            mainItem.addChild(self.addNewItem(i))
            
        return mainItem
    
    def reloadList(self):
        ''' reload list of packages from current lib '''
        if not self.sql:
            return False
        
        self.clear()
        
        # models without category
        for i in self.sql.getAllModelsByCategory(0):
            self.addTopLevelItem(self.addNewModel(i))
        
        # main categories
        for i in self.sql.getAllcategoriesWithSubCat(0).items():
            self.addTopLevelItem(self.addNewItem(i))
        
        self.sortItems(0, QtCore.Qt.AscendingOrder)
        #self.resizeColumnToContents(0)


class separator(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QFrame.__init__(self, parent)
        #
        self.setFrameShape(QtGui.QFrame.HLine)
        self.setFrameShadow(QtGui.QFrame.Sunken)
        self.setLineWidth(1)
        

class flatButton(QtGui.QPushButton):
    def __init__(self, icon, tooltip, parent=None):
        QtGui.QPushButton.__init__(self, QtGui.QIcon(icon), "", parent)
        #
        self.setToolTip(tooltip)
        self.setFlat(True)
        self.setStyleSheet("QPushButton:hover:!pressed{border: 1px solid #808080; background-color: #e6e6e6;} ")

class dodajElement(QtGui.QDialog, partsManaging):
    def __init__(self, parent=None):
        partsManaging.__init__(self)
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u"Assign models")
        self.setWindowIcon(QtGui.QIcon(":/data/img/uklad.png"))
        self.modelPreview = None
        
        self.elementID = None
        self.szukaneFrazy = []
        self.szukaneFrazyNr = 0
        self.sql = dataBase()
        self.sql.connect()
        
        ########################
        # models list
        ########################
        self.modelsList = modelsList()
        self.modelsList.sql = self.sql
        self.modelsList.reloadList()
        self.connect(self.modelsList, QtCore.SIGNAL("itemPressed (QTreeWidgetItem *,int)"), self.loadData)
        
        ##
        mainWidgetLeftSide = QtGui.QWidget()
        mainLayLeftSide = QtGui.QGridLayout(mainWidgetLeftSide)
        mainLayLeftSide.addLayout(self.searcherLayout(), 0, 1, 1, 1)
        mainLayLeftSide.addLayout(self.leftMenuLayout(), 1, 0, 1, 1)
        mainLayLeftSide.addWidget(self.modelsList, 1, 1, 1, 1)
        
        # main layout
        self.splitter = QtGui.QSplitter()
        self.splitter.setStyleSheet('QSplitter::handle {background: rgba(31.8, 33.3, 33.7, 0.1); cursor: col-resize;} ')
        self.splitter.setChildrenCollapsible(False)
        self.splitter.addWidget(mainWidgetLeftSide)
        self.splitter.addWidget(self.mainWidgetRightSide())
        
        mainLay = QtGui.QHBoxLayout()
        mainLay.addWidget(self.splitter)
        mainLay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLay)
        #
        self.reloadList()
        
    def readSize(self):
        try:
            data = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("assignWindow", "").strip()
            if data != "":
                data = eval(data)
                
                x = int(data[0])
                y = int(data[1]) + 30
                w = int(data[2])
                h = int(data[3])
                self.splitter.setSizes(data[4])
                self.modelsList.setColumnWidth(0, data[5])
                
                self.setGeometry(x, y, w, h)
        except Exception as e:
            FreeCAD.Console.PrintWarning(u"{0} \n".format(e))
    
    def showEvent (self, event):
        self.readSize()
        self.RightSide_tab.setCurrentIndex(2)
        self.RightSide_tab.setCurrentIndex(0)
        event.accept()
    
    def closeEvent(self, event):
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").SetString("assignWindow", str([self.x(), self.y(), self.width(), self.height(), self.splitter.sizes(), self.modelsList.columnWidth(0)]))
        #
        event.accept()

    def importDatabase(self):
        try:
            dial = importScriptCopy()
            dial.exec_()
        except Exception as e:
            FreeCAD.Console.PrintWarning(u"Error: {0} \n".format(e))
        else:
            self.reloadList()
            FreeCAD.Console.PrintWarning(u"Done!\n")

    def prepareCopy(self):
        try:
            dial = prepareScriptCopy()
            dial.exec_()
        except Exception as e:
            FreeCAD.Console.PrintWarning(u"Error: {0} \n".format(e))

    def clearData(self):
        ''' clean form '''
        tablica = {"id": 0,
                   "name" : "",
                   "description": "",
                   "categoryID" : 0,
                   "datasheet" : "",
                   "path3DModels" : "",
                   "isSocket" : False,
                   "isSocketHeight" : 0.0,
                   "socketID" : 0,
                   "socketIDSocket" : False,
                   "software" : []
                }
        self.showData(tablica)
        
        self.RightSide_tab.setCurrentIndex(0)
        self.pathsList.clear()
        self.modelPreview.Shape = Part.Shape()
        self.modelPreview.ViewObject.DiffuseColor = [(0.800000011920929, 0.800000011920929, 0.800000011920929, 0.0)]
        self.modelAdjust.resetTable()
    
    def readFormData(self):
        try:
            return {"name": str(self.packageName.text()).strip(),
                   "description": str(self.modelDescription.toPlainText()),
                   "categoryID": self.modelCategory.categoryID,
                   "datasheet": str(self.datasheetPath.text()).strip(),
                   "path3DModels": str(self.pathToModel.text()).strip(),
                   "isSocket": self.boxSetAsSocketa.isChecked(),
                   "isSocketHeight": float(self.socketHeight.value()),
                   "socketID": self.socketModelName.itemData(self.socketModelName.currentIndex(), QtCore.Qt.UserRole),
                   "socketIDSocket": self.boxAddSocket.isChecked(),
                   "software": self.modelSettings.getData(),
                   "params": self.modelAdjust.getData()
                   }
        except Exception as e:
            FreeCAD.Console.PrintWarning("{0} \n".format(e))
    
    def addModelAsNew(self):
        ''' add package as new - based on other package '''
        if str(self.packageName.text()).strip() == "" or str(self.pathToModel.text()).strip() == "":
            QtGui.QMessageBox().critical(self, u"Caution!", u"At least one required field is empty.")
            return

        zawiera = self.sql.getModelByName(str(self.packageName.text()).strip())
        if zawiera[0]:
            dial = QtGui.QMessageBox(self)
            dial.setText(u"Rejected. Package already exist.")
            dial.setWindowTitle("Caution!")
            dial.setIcon(QtGui.QMessageBox.Warning)
            dial.addButton('Ok', QtGui.QMessageBox.RejectRole)
            dial.exec_()
        else:
            self.saveNewModel()
        
    def saveNewModel(self):
        ''' add package info to lib '''
        data = self.readFormData()
        
        self.sql.addModel(data)
        self.reloadList()
        self.wyszukajObiekty(data["name"])
        
    def updateModel(self, elemID):
        data = self.readFormData()
        
        self.sql.updateModel(elemID, data)
        self.reloadList()
        self.wyszukajObiekty(data["name"])
    
    def setOneCategoryForModelsF(self):
        ''' '''
        try:
            dial = setOneCategoryGui()
            dial.loadCategories(self.sql.getAllcategoriesWithSubCat(0).items())
            
            if dial.exec_():
                for i in QtGui.QTreeWidgetItemIterator(self.modelsList):
                    if str(i.value().data(0, QtCore.Qt.UserRole + 1)) == 'C':
                        continue
                    if not i.value().checkState(0) == QtCore.Qt.Checked:
                        continue
                    #
                    item = i.value()
                    modelID = str(item.data(0, QtCore.Qt.UserRole))
                    categoryID = dial.parentCategory.categoryID
                    
                    self.sql.setCategoryForModel(modelID, categoryID)
                    item.setCheckState(0, QtCore.Qt.Unchecked)
                
                self.reloadList()
        except Exception as e:
            FreeCAD.Console.PrintWarning("Error1: {0} \n".format(e))
    
    def selectAllModels(self):
        for i in QtGui.QTreeWidgetItemIterator(self.modelsList):
                if str(i.value().data(0, QtCore.Qt.UserRole + 1)) == 'C':
                    continue
                
                i.value().setCheckState(0, QtCore.Qt.Checked)
    
    def deselectAllModels(self):
        for i in QtGui.QTreeWidgetItemIterator(self.modelsList):
                if str(i.value().data(0, QtCore.Qt.UserRole + 1)) == 'C':
                    continue
                
                i.value().setCheckState(0, QtCore.Qt.Unchecked)
    
    def deleteColFilesF(self):
        try:
            delAll = False
            #
            for i in QtGui.QTreeWidgetItemIterator(self.modelsList):
                if str(i.value().data(0, QtCore.Qt.UserRole + 1)) == 'C':
                    continue
                if not i.value().checkState(0) == QtCore.Qt.Checked:
                    continue
                ##########
                item = i.value()
                objectID = str(item.data(0, QtCore.Qt.UserRole))
                ##########
                if not delAll:
                    dial = QtGui.QMessageBox()
                    dial.setText(u"Delete *.col file for package {0}?".format(item.text(0)))
                    dial.setWindowTitle("Caution!")
                    dial.setIcon(QtGui.QMessageBox.Question)
                    delete_YES = dial.addButton('Yes', QtGui.QMessageBox.YesRole)
                    delete_YES_ALL = dial.addButton('Yes for all', QtGui.QMessageBox.YesRole)
                    delete_NO = dial.addButton('No', QtGui.QMessageBox.RejectRole)
                    delete_NO_ALL = dial.addButton('No for all', QtGui.QMessageBox.RejectRole)
                    dial.exec_()
                    
                    if dial.clickedButton() == delete_NO_ALL:
                        break
                    elif dial.clickedButton() == delete_YES_ALL:
                        delAll = True
                    elif dial.clickedButton() == delete_NO:
                        continue
                ##
                dane = self.sql.getModelByID(objectID)
                if dane[0]:
                    modelData = self.sql.convertToTable(dane[1])
                    for p in modelData["path3DModels"].split(';'):
                        if p == '':
                            continue
                        
                        [boolValue, path] = partExistPath(p)
                        path, extension = os.path.splitext(path)
                        
                        try:
                            os.remove(path + ".col") 
                        except:
                            pass
            ##########
        except Exception as e:
            FreeCAD.Console.PrintWarning("Error1: {0} \n".format(e))

    def deleteModel(self):
        ''' delete selected packages from lib '''
        try:
            delAll = False
            #
            for i in QtGui.QTreeWidgetItemIterator(self.modelsList):
                if str(i.value().data(0, QtCore.Qt.UserRole + 1)) == 'C':
                    continue
                if not i.value().checkState(0) == QtCore.Qt.Checked:
                    continue
                ##########
                item = i.value()
                objectID = str(item.data(0, QtCore.Qt.UserRole))
                ##########
                if not delAll:
                    dial = QtGui.QMessageBox()
                    dial.setText(u"Delete selected package {0}?".format(item.text(0)))
                    dial.setWindowTitle("Caution!")
                    dial.setIcon(QtGui.QMessageBox.Question)
                    delete_YES = dial.addButton('Yes', QtGui.QMessageBox.YesRole)
                    delete_YES_ALL = dial.addButton('Yes for all', QtGui.QMessageBox.YesRole)
                    delete_NO = dial.addButton('No', QtGui.QMessageBox.RejectRole)
                    delete_NO_ALL = dial.addButton('No for all', QtGui.QMessageBox.RejectRole)
                    dial.exec_()
                    
                    if dial.clickedButton() == delete_NO_ALL:
                        break
                    elif dial.clickedButton() == delete_YES_ALL:
                        delAll = True
                    elif dial.clickedButton() == delete_NO:
                        continue
                #
                self.sql.deleteModel(objectID)
                item.setCheckState(0, QtCore.Qt.Unchecked)
                item.setHidden(True)
            ##########
        except Exception as e:
            FreeCAD.Console.PrintWarning("Error1: {0} \n".format(e))

    def addNewModel(self):
        ''' add package to lib '''
        #if str(self.packageName.text()).strip() == "" or str(self.pathToModel.text()).strip() == "":
            #QtGui.QMessageBox().critical(self, u"Caution!", u"At least one required field is empty.")
            #return
        
        zawiera = self.sql.getModelByName(str(self.packageName.text()).strip())
        if not self.elementID and zawiera[0]:  # aktualizacja niezaznaczonego obiektu
            dial = QtGui.QMessageBox(self)
            dial.setText(u"Package already exist. Rewrite?")
            dial.setWindowTitle("Caution!")
            dial.setIcon(QtGui.QMessageBox.Question)
            rewN = dial.addButton('No', QtGui.QMessageBox.RejectRole)
            rewT = dial.addButton('Yes', QtGui.QMessageBox.YesRole)
            dial.exec_()
                
            if dial.clickedButton() == rewN:
                return
            else:
                self.updateModel(zawiera[1].id)
                return
        elif self.elementID:  # aktualizacja zaznaczonego obiektu
            dial = QtGui.QMessageBox(self)
            dial.setText(u"Save changes?")
            dial.setWindowTitle("Caution!")
            dial.setIcon(QtGui.QMessageBox.Question)
            rewN = dial.addButton('No', QtGui.QMessageBox.RejectRole)
            dial.addButton('Yes', QtGui.QMessageBox.YesRole)
            dial.exec_()
                
            if dial.clickedButton() == rewN:
                return
            else:
                #zawiera = self.sql.has_value("name", self.nazwaEagle.text())
                if zawiera[0] and zawiera[1].id != self.elementID:
                    dial = QtGui.QMessageBox(self)
                    dial.setText(u"Rejected. Package already exist.")
                    dial.setWindowTitle("Caution!")
                    dial.setIcon(QtGui.QMessageBox.Warning)
                    dial.addButton('Ok', QtGui.QMessageBox.RejectRole)
                    dial.exec_()
                else:
                    if not self.sql.getModelByID(self.elementID)[0]:
                        self.saveNewModel()
                    else:
                        self.updateModel(self.elementID)
                return
        else:  # dodanie nowego obiektu
            self.saveNewModel()
    
    def showData(self, model):
        ''' load package info to form '''
        try:
            self.elementID = model["id"]
            self.packageName.setText(model["name"])
            self.pathToModel.setText(model["path3DModels"])
            self.modelDescription.setPlainText(model["description"])
            self.datasheetPath.setText(model["datasheet"])
            if model["categoryID"] == 0:
                self.modelCategory.setData(model["categoryID"], '')
            else:
                self.modelCategory.setData(model["categoryID"], self.sql.getCategoryByID(model["categoryID"]).name)
            # software
            self.modelSettings.clear()
            self.modelSettings.addRows(model["software"])
            # params
            self.modelAdjust.resetTable()
            if "params" in model.keys():
                for i in model["params"]:
                    self.modelAdjust.updateType(i['name'], i)
            # sockets
            self.reloadSockets()
            self.socketModelName.removeItem(self.socketModelName.findData(self.elementID))
            
            if self.socketModelName.findData(model["socketID"]) != -1:
                self.boxAddSocket.setChecked(model["socketIDSocket"])
                self.socketModelName.setCurrentIndex(self.socketModelName.findData(model["socketID"]))
            else:
                self.boxAddSocket.setChecked(QtCore.Qt.Unchecked)
            #
            self.boxSetAsSocketa.setChecked(model["isSocket"])
            self.socketHeight.setValue(model["isSocketHeight"])
        except Exception as e:
            FreeCAD.Console.PrintWarning(u"showData(): {0} \n".format(e))

    def resetSetAsSocket(self, value):
        if value:
            self.socketHeight.setValue(0)
            self.boxSetAsSocketa.setChecked(False)
            
    def resetSetSocket(self, value):
        if value:
            self.boxAddSocket.setChecked(False)
            try:
                self.socketModelName.setCurrentIndex(-1)
            except Exception as e:
                pass
    
    def addNewPathF(self):
        '''  '''
        dial = addNewPath(self.pathToModel.text())
        if dial.exec_():
            path = []
            for i in range(dial.pathsList.count()):
                path.append(dial.pathsList.item(i).text())
            self.pathToModel.setText(';'.join(path))

    def loadDatasheet(self):
        ''' load datasheet of selected package '''
        url = str(self.datasheetPath.text()).strip()
        if len(url):
            if url.startswith("http://") or url.startswith("https://") or url.startswith("www."):
                QtGui.QDesktopServices().openUrl(QtCore.QUrl(url))
            else:
                QtGui.QDesktopServices().openUrl(QtCore.QUrl("file:///{0}".format(url), QtCore.QUrl.TolerantMode))
    
    def wyszukajObiektyNext(self):
        ''' find next object '''
        try:
            if len(self.szukaneFrazy):
                if self.szukaneFrazyNr <= len(self.szukaneFrazy) - 2:
                    self.szukaneFrazyNr += 1
                else:
                    self.szukaneFrazyNr = 0
                self.modelsList.setCurrentItem(self.szukaneFrazy[self.szukaneFrazyNr])
        except RuntimeError:
            self.szukaneFrazy = []
            self.szukaneFrazyNr = 0
    
    def wyszukajObiektyPrev(self):
        ''' find prev object '''
        try:
            if len(self.szukaneFrazy):
                if self.szukaneFrazyNr >= 1:
                    self.szukaneFrazyNr -= 1
                else:
                    self.szukaneFrazyNr = len(self.szukaneFrazy) - 1
                self.modelsList.setCurrentItem(self.szukaneFrazy[self.szukaneFrazyNr])
        except RuntimeError:
            self.szukaneFrazy = []
            self.szukaneFrazyNr = 0
        
    def wyszukajObiekty(self, fraza):
        ''' find object in current document '''
        fraza = str(fraza).strip()
        if fraza != "":
            self.szukaneFrazy = self.modelsList.findItems(fraza, QtCore.Qt.MatchRecursive | QtCore.Qt.MatchStartsWith)
            if len(self.szukaneFrazy):
                self.searcher.setStyleSheet("border: 1px solid #808080")
                self.modelsList.setCurrentItem(self.szukaneFrazy[0])
                self.szukaneFrazyNr = 0
            else:
                self.searcher.setStyleSheet("border: 2px solid #F00")
        else:
            self.searcher.setStyleSheet("border: 1px solid #808080")

    def editCategoryF(self):
        ID = int(self.modelsList.currentItem().data(0, QtCore.Qt.UserRole))
        categoryData = self.sql.getCategoryByID(ID)
        
        parentCategoryData = self.sql.getCategoryByID(categoryData.parentID)
        #
        dial = updateCategoryGui()
        dial.categoryName.setText(categoryData.name)
        dial.categoryDescription.setText(categoryData.description)
        if not parentCategoryData:
            dial.loadCategories(self.sql.getAllcategoriesWithSubCat(0).items(), 0, '')
        else:
            dial.loadCategories(self.sql.getAllcategoriesWithSubCat(0).items(), parentCategoryData.id, parentCategoryData.name)
        
        if dial.exec_():
            if str(dial.categoryName.text()).strip() == '':
                FreeCAD.Console.PrintWarning("{0} \n".format(u'Mandatory field is empty!'))
                return
            
            name = str(dial.categoryName.text()).strip()
            parentID = dial.parentCategory.categoryID
            if parentID == -1 or parentID == None:
                parentID = 0
            parentID = int(parentID)
            description = str(dial.categoryDescription.toPlainText()).strip()
            
            if self.sql.updateCategory(ID, name, parentID, description):
                #self.modelsList.reloadList(self.sql.getAllcategoriesWithSubCat(0))
                self.reloadList()
    
    def addCategory(self):
        if self.modelsList.currentItem() and self.modelsList.currentItem().data(0, QtCore.Qt.UserRole + 1) == 'C':
            ID = int(self.modelsList.currentItem().data(0, QtCore.Qt.UserRole))
            categoryData = self.sql.getCategoryByID(ID)
            
            defParent = categoryData.name
            parentID = categoryData.id
        else:
            defParent = 'None'
            parentID = 0
        
        dial = addCategoryGui()
        dial.loadCategories(self.sql.getAllcategoriesWithSubCat(0).items(), parentID, defParent)
        
        if dial.exec_():
            if str(dial.categoryName.text()).strip() == '':
                FreeCAD.Console.PrintWarning("{0} \n".format(u'Mandatory field is empty!'))
                return
            
            if self.sql.addCategory(str(dial.categoryName.text()).strip(), dial.parentCategory.categoryID, str(dial.categoryDescription.toPlainText()).strip()):
                #self.modelsList.reloadList()
                self.reloadList()
    
    def deleteCategory(self):
        ID = int(self.modelsList.currentItem().data(0, QtCore.Qt.UserRole))
        
        dial = removeCategoryGui(self.modelsList.currentItem().text(0))
        dial.exec_()
        
        if dial.clickedButton() == dial.delete:
            if self.sql.deleteCategory(ID):
                #self.modelsList.reloadList(self.sql.getAllcategoriesWithSubCat(0))
                self.reloadList()
        
    def loadData(self, item):
        self.RightSide_tab.setCurrentIndex(0)
        
        if str(self.modelsList.currentItem().data(0, QtCore.Qt.UserRole + 1)) == 'C':
            self.clearData()
            self.editCategory.setDisabled(False)
            self.removeCategory.setDisabled(False)
            self.removeModel.setDisabled(True)
            self.deleteColFiles.setDisabled(True)
            self.setOneCategoryForModels.setDisabled(True)
        else:
            self.editCategory.setDisabled(True)
            self.removeCategory.setDisabled(True)
            self.removeModel.setDisabled(False)
            self.deleteColFiles.setDisabled(False)
            self.setOneCategoryForModels.setDisabled(False)
            #
            try:
                dane = self.sql.getModelByID(self.modelsList.currentItem().data(0, QtCore.Qt.UserRole))
                if dane[0]:
                    modelData = self.sql.convertToTable(dane[1])
                    modelData = self.sql.packagesDataToDictionary(modelData)
                    modelData = self.sql.paramsDataToDictionary(modelData)
                    self.showData(modelData)
            except Exception as e:
                FreeCAD.Console.PrintWarning("ERROR (LD): {0}.\n".format(e))

    def reloadCategoryList(self):
        self.modelCategory.setMenuF(self.sql.getAllcategoriesWithSubCat(0).items())

    def reloadList(self):
        ''' reload list of packages from current lib '''
        self.editCategory.setDisabled(True)
        self.removeCategory.setDisabled(True)
        self.removeModel.setDisabled(True)
        self.deleteColFiles.setDisabled(True)
        self.setOneCategoryForModels.setDisabled(True)
        
        try:
            try:
                data = self.modelsList.currentItem().text(0)
            except:
                data = None
            
            self.modelsList.reloadList()
            self.reloadCategoryList()
            #self.clearData()
            
            if data:
                self.wyszukajObiekty(data)
        except Exception as e:
            FreeCAD.Console.PrintWarning(u"Error 6: {0} \n".format(e))
    
    def loadModelPreview(self, data):
        [boolValue, path] = partExistPath(data)
        if boolValue:
            active = None
            if FreeCAD.ActiveDocument:
                active = FreeCAD.ActiveDocument.Name
            FreeCAD.setActiveDocument('modelPreview')
            FreeCAD.ActiveDocument = FreeCAD.getDocument('modelPreview')
            FreeCADGui.ActiveDocument = FreeCADGui.getDocument('modelPreview')
            FreeCADGui.activeDocument().activeView().viewIsometric()
            
            self.modelPreview = self.getPartShape(path, self.modelPreview, True)
            self.modelPreview.ViewObject.DiffuseColor = self.modelPreview.ViewObject.DiffuseColor
            FreeCAD.ActiveDocument.recompute()
            
            #FreeCADGui.SendMsgToActiveView("ViewFit")
            if active:
                FreeCAD.setActiveDocument(active)
                FreeCAD.ActiveDocument=FreeCAD.getDocument(active)
                FreeCADGui.ActiveDocument=FreeCADGui.getDocument(active)
        else:
            self.modelPreview.Shape = Part.Shape()

    def checkSockets(self, tabID):
        if tabID == 1 and self.socketModelName.count() == 0:
            self.boxAddSocket.setDisabled(True)
        if tabID == 2: # preview
            self.pathsList.clear()
            if len(self.pathToModel.text().split(';')):
                self.pathsList.addItems(self.pathToModel.text().split(';'))
                self.connect(self.pathsList, QtCore.SIGNAL("currentIndexChanged (const QString&)"), self.loadModelPreview)
                self.pathsList.setCurrentIndex(-1)
                self.pathsList.setCurrentIndex(0)
            else:
                self.modelPreview.Shape = Part.Shape()
        else:
            self.pathsList.clear()
            self.boxAddSocket.setDisabled(False)
            
    def reloadSockets(self):
        try:
            self.socketModelName.clear()
            
            for i in self.sql.getAllSockets():
                socket = self.sql.convertToTable(i)
                self.socketModelName.addItem(socket['name'])
                self.socketModelName.setItemData(self.socketModelName.count() - 1, socket['id'], QtCore.Qt.UserRole)
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR: {0}.\n".format(e))
        
    ##########################
    ##########################
    ##          GUI
    ##########################
    ##########################
    
    ##########################
    # right menu - model
    ##########################
    
    def mainWidgetRightSide(self):
        ########################
        # package name
        ########################
        self.packageName = QtGui.QLineEdit("")
        
        #########################
        ## path to package
        #########################
        self.pathToModel = QtGui.QLineEdit("")
        self.pathToModel.setReadOnly(True)
        
        pathToModelInfo = flatButton(":/data/img/edit_16x16.png", u"Edit")
        self.connect(pathToModelInfo, QtCore.SIGNAL("clicked ()"), self.addNewPathF)
        
        #########################
        ## datasheet
        #########################
        self.datasheetPath = QtGui.QLineEdit("")
        
        datasheetPathPrz = flatButton(":/data/img/browser_16x16.png", u"Open datasheet")
        self.connect(datasheetPathPrz, QtCore.SIGNAL("clicked ()"), self.loadDatasheet)
        #########################
        ## FCStd file
        #########################
        # self.fcstdFilePath = QtGui.QLineEdit("")
        
        # fcstdFilePathPrz = flatButton(":/data/img/browser_16x16.png", u"Open file")
        # self.connect(fcstdFilePathPrz, QtCore.SIGNAL("clicked ()"), self.loadDatasheet)
        #########################
        ## socket for model
        #########################
        self.socketModelName = QtGui.QComboBox()
        
        self.boxAddSocket = QtGui.QGroupBox()
        self.boxAddSocket.setTitle(u"Add socket")
        self.boxAddSocket.setCheckable(True)
        self.boxAddSocket.setChecked(False)
        boxAddSocketLay = QtGui.QHBoxLayout(self.boxAddSocket)
        boxAddSocketLay.addWidget(QtGui.QLabel(u"Socket"))
        boxAddSocketLay.addWidget(self.socketModelName)
        
        self.connect(self.boxAddSocket, QtCore.SIGNAL("toggled (bool)"), self.resetSetAsSocket)
        #########################
        ## set model as socket
        #########################
        self.socketHeight = QtGui.QDoubleSpinBox()
        self.socketHeight.setSuffix(" mm")
        
        self.boxSetAsSocketa = QtGui.QGroupBox()
        self.boxSetAsSocketa.setTitle(u"Set as socket")
        self.boxSetAsSocketa.setCheckable(True)
        self.boxSetAsSocketa.setChecked(False)
        layBoxPodstawka = QtGui.QHBoxLayout(self.boxSetAsSocketa)
        layBoxPodstawka.addWidget(QtGui.QLabel(u"Height"))
        layBoxPodstawka.addWidget(self.socketHeight)
        
        self.connect(self.boxSetAsSocketa, QtCore.SIGNAL("toggled (bool)"), self.resetSetSocket)
        #########################
        ## model category
        #########################
        self.modelCategory = categorySelector()
        
        #########################
        ## description
        #########################
        self.modelDescription = QtGui.QTextEdit()
        self.modelDescription.setStyleSheet('''
                border: 1px solid #808080;
            ''')
        
        #########################
        ## save / save as / clean button
        #########################
        saveModelSettings = QtGui.QPushButton("Save")
        saveModelSettings.setIcon(QtGui.QIcon(":/data/img/save_22x22.png"))
        self.connect(saveModelSettings, QtCore.SIGNAL("clicked ()"), self.addNewModel)
        
        cleanForm = QtGui.QPushButton("Clean/New")
        cleanForm.setIcon(QtGui.QIcon(":/data/img/clear_16x16.png"))
        self.connect(cleanForm, QtCore.SIGNAL("clicked ()"), self.clearData)
        
        saveAsModelSettings = QtGui.QPushButton("Save As New")
        saveAsModelSettings.setIcon(QtGui.QIcon(":/data/img/save_22x22.png"))
        self.connect(saveAsModelSettings, QtCore.SIGNAL("clicked ()"), self.addModelAsNew)
        
        closeDialog = QtGui.QPushButton("Close")
        self.connect(closeDialog, QtCore.SIGNAL("clicked ()"), self, QtCore.SLOT('close()'))
        
        ########################
        # adjust name/value
        ########################
        self.modelAdjust = modelAdjustTable()
        self.modelAdjust.addRow("Name")
        self.modelAdjust.addRow("Value")
        
        #########################
        ## model settings
        #########################
        self.modelSettings = modelSettingsTable()
        
        modelSettingsAdd = flatButton(":/data/img/add_16x16.png", u"Add")
        self.connect(modelSettingsAdd, QtCore.SIGNAL("clicked ()"), self.modelSettings.addNewModel)
        
        modelSettingsDelete = flatButton(":/data/img/delete_16x16.png", u"Delete")
        self.connect(modelSettingsDelete, QtCore.SIGNAL("clicked ()"), self.modelSettings.deleteModel)
        
        modelSettingsEdit = flatButton(":/data/img/edit_16x16.png", u"Edit")
        self.connect(modelSettingsEdit, QtCore.SIGNAL("clicked ()"), self.modelSettings.editModel)
        
        modelSettingsCopy = flatButton(":/data/img/copy.png", u"Copy")
        self.connect(modelSettingsCopy, QtCore.SIGNAL("clicked ()"), self.modelSettings.copyModel)

        ########################
        # layouts
        ########################
        # right side
        packageFooter = QtGui.QHBoxLayout()
        packageFooter.addWidget(saveModelSettings)
        packageFooter.addWidget(saveAsModelSettings)
        packageFooter.addWidget(cleanForm)
        if os.name == 'posix':
            packageFooter.addWidget(closeDialog)
        
        # rightSide_Main
        rightSide_Main = QtGui.QWidget()
        layRightSide_Main = QtGui.QGridLayout(rightSide_Main)
        layRightSide_Main.addWidget(QtGui.QLabel(u"Model name*"), 0, 0, 1, 1)
        layRightSide_Main.addWidget(self.packageName, 0, 1, 1, 2)
        layRightSide_Main.addWidget(QtGui.QLabel(u"Path to element*"), 2, 0, 1, 1)
        layRightSide_Main.addWidget(self.pathToModel, 2, 1, 1, 1)
        layRightSide_Main.addWidget(pathToModelInfo, 2, 2, 1, 1)
        layRightSide_Main.addWidget(QtGui.QLabel(u"Datasheet"), 3, 0, 1, 1)
        layRightSide_Main.addWidget(self.datasheetPath, 3, 1, 1, 1)
        layRightSide_Main.addWidget(datasheetPathPrz, 3, 2, 1, 1)
        # layRightSide_Main.addWidget(QtGui.QLabel(u"FCStd file"), 4, 0, 1, 1)
        # layRightSide_Main.addWidget(self.fcstdFilePath, 4, 1, 1, 1)
        # layRightSide_Main.addWidget(fcstdFilePathPrz, 4, 2, 1, 1)
        layRightSide_Main.addWidget(QtGui.QLabel(u"Category"), 5, 0, 1, 1)
        layRightSide_Main.addWidget(self.modelCategory, 5, 1, 1, 2)
        layRightSide_Main.addWidget(self.modelSettings, 6, 0, 6, 2)
        layRightSide_Main.addWidget(modelSettingsAdd, 7, 2, 1, 1)
        layRightSide_Main.addWidget(modelSettingsDelete, 8, 2, 1, 1)
        layRightSide_Main.addWidget(modelSettingsEdit, 9, 2, 1, 1)
        layRightSide_Main.addWidget(modelSettingsCopy, 10, 2, 1, 1)
        ##################
        ##################
        active = None
        if FreeCAD.ActiveDocument:
            active = FreeCAD.ActiveDocument.Name
        #
        doc = FreeCAD.newDocument('modelPreview')
        FreeCAD.setActiveDocument('modelPreview')
        FreeCAD.ActiveDocument = FreeCAD.getDocument('modelPreview')
        FreeCADGui.ActiveDocument = FreeCADGui.getDocument('modelPreview')
        
        step_model = doc.addObject("Part::FeaturePython", "preview")
        #step_model = self.getPartShape("D:\Program Files\FreeCAD 0.18\Mod\PCB\parts/batteries\CR2032V.stp", step_model, False)
        self.modelPreview = step_model
        viewProviderPartObject(step_model.ViewObject)
        
        #FreeCADGui.SendMsgToActiveView("ViewFit")
        FreeCADGui.ActiveDocument.ActiveView.setAxisCross(True)
        #
        self.pathsList = QtGui.QComboBox()
        
        rightSide_Trash = QtGui.QWidget()
        layRightSide_Trash = QtGui.QGridLayout(rightSide_Trash)
        
        rightSide_Preview = QtGui.QWidget()
        layRightSide_Preview = QtGui.QGridLayout(rightSide_Preview)
        layRightSide_Preview.addWidget(self.pathsList, 0, 0, 1, 1)
        
        wL = FreeCADGui.getMainWindow().findChild(QtGui.QMdiArea).subWindowList()
        for i in wL:
            if 'modelPreview' in i.windowTitle():
                #widget = i.widget()
                #wL = widget.layout()
                #wI = wL.itemAt(0).widget().currentWidget()
                #i.event = self.ppm
                #FreeCAD.Console.PrintWarning(u"{0}\n".format(wI))
                #i.widget().mouseMoveEvent = self.ppm
                
                layRightSide_Trash.addWidget(i, 0, 0, 1, 1)
                layRightSide_Preview.addWidget(i.widget(), 1, 0, 10, 1)
                break

        layRightSide_Preview.setRowStretch(1, 10);
        #
        if active:
            FreeCAD.setActiveDocument(active)
            FreeCAD.ActiveDocument=FreeCAD.getDocument(active)
            FreeCADGui.ActiveDocument=FreeCADGui.getDocument(active)
        ##################
        ##################
        
        #  rightSide_Other
        rightSide_Other = QtGui.QWidget()
        layRightSide_Other = QtGui.QGridLayout(rightSide_Other)
        layRightSide_Other.addWidget(self.modelAdjust, 0, 0, 1, 2)
        layRightSide_Other.addWidget(self.boxAddSocket, 1, 0, 1, 2)
        layRightSide_Other.addWidget(self.boxSetAsSocketa, 2, 0, 1, 2)
        layRightSide_Other.addWidget(QtGui.QLabel("Description"), 3, 0, 1, 1, QtCore.Qt.AlignTop)
        layRightSide_Other.addWidget(self.modelDescription, 3, 1, 1, 1)
        
        layRightSide_Other.setColumnStretch(1, 10)
        #####
        self.RightSide_tab = QtGui.QTabWidget()
        self.RightSide_tab.addTab(rightSide_Main, u"Main")
        self.RightSide_tab.addTab(rightSide_Other, u"Other")
        self.RightSide_tab.addTab(rightSide_Preview, u"Preview")
        #self.RightSide_tab.addTab(rightSide_Trash, u"Trash")
        #self.RightSide_tab.
        self.connect(self.RightSide_tab, QtCore.SIGNAL("currentChanged (int)"), self.checkSockets)
        
        mainWidgetRightSide = QtGui.QWidget()
        mainLayRightSide = QtGui.QGridLayout(mainWidgetRightSide)
        mainLayRightSide.addWidget(self.RightSide_tab, 0, 0, 1, 1)
        mainLayRightSide.addItem(QtGui.QSpacerItem(1, 15), 1, 0, 1, 3)
        mainLayRightSide.addLayout(packageFooter, 2, 0, 1, 3)
        mainLayRightSide.setRowStretch(0, 20)
        mainLayRightSide.setContentsMargins(10, 10, 10, 10)
        
        return mainWidgetRightSide
    
    ##########################
    # left menu - options
    ##########################
    def leftMenuLayout(self):
        ########################
        # database
        ########################
        modelsListSaveCopy = flatButton(":/data/img/databaseExport.svg", u"Save database copy")
        self.connect(modelsListSaveCopy, QtCore.SIGNAL("clicked ()"), self.prepareCopy)
        
        modelsListImportDatabase = flatButton(":/data/img/databaseImport.svg", u"Import database")
        self.connect(modelsListImportDatabase, QtCore.SIGNAL("clicked ()"), self.importDatabase)
        
        modelsListReload = flatButton(":/data/img/databaseReload.svg", u"Reload database")
        self.connect(modelsListReload, QtCore.SIGNAL("clicked ()"), self.reloadList)
        
        ########################
        # models list
        ########################
        modelsListExpand = flatButton(":/data/img/expand.png", u"Expand all")
        self.connect(modelsListExpand, QtCore.SIGNAL("clicked ()"), self.modelsList.expandAll)
        
        modelsListCollapse = flatButton(":/data/img/collapse.png", u"Collapse all")
        self.connect(modelsListCollapse, QtCore.SIGNAL("clicked ()"), self.modelsList.collapseAll)
        
        modelsListSelectAll = flatButton(":/data/img/checkbox_checked_16x16.png", u"Select all models")
        self.connect(modelsListSelectAll, QtCore.SIGNAL("clicked ()"), self.selectAllModels)
        
        modelsListDeselectAll = flatButton(":/data/img/checkbox_unchecked_16x16.png", u"Deselect all models")
        self.connect(modelsListDeselectAll, QtCore.SIGNAL("clicked ()"), self.deselectAllModels)
        
        self.removeModel = flatButton(":/data/img/databaseDeleteModel.svg", u"Delete all selected models from database")
        self.removeModel.setDisabled(True)
        self.connect(self.removeModel, QtCore.SIGNAL("clicked ()"), self.deleteModel)
        
        self.setOneCategoryForModels = flatButton(":/data/img/boundingBoxAll.svg", u"Set one category for all selected models")
        self.setOneCategoryForModels.setDisabled(True)
        self.connect(self.setOneCategoryForModels, QtCore.SIGNAL("clicked ()"), self.setOneCategoryForModelsF)
        
        self.deleteColFiles = flatButton(":/data/img/deleteColFile.svg", u"Delete *.col files for selected models")
        self.deleteColFiles.setDisabled(True)
        self.connect(self.deleteColFiles, QtCore.SIGNAL("clicked ()"), self.deleteColFilesF)
        
        ########################
        # categories
        ########################
        self.editCategory = QtGui.QPushButton("")
        self.editCategory.setIcon(QtGui.QIcon(":/data/img/edit_16x16.png"))
        self.editCategory.setToolTip(u"Edit category")
        self.editCategory.setFlat(True)
        self.editCategory.setDisabled(True)
        self.editCategory.setStyleSheet("QPushButton:hover:!pressed{border: 1px solid #808080; background-color: #e6e6e6;} ")
        self.connect(self.editCategory, QtCore.SIGNAL("clicked ()"), self.editCategoryF)
        
        addCategoryButton = QtGui.QPushButton("")
        addCategoryButton.setIcon(QtGui.QIcon(":/data/img/add_16x16.png"))
        addCategoryButton.setToolTip(u"Add new category")
        addCategoryButton.setFlat(True)
        addCategoryButton.setStyleSheet("QPushButton:hover:!pressed{border: 1px solid #808080; background-color: #e6e6e6;} ")
        self.connect(addCategoryButton, QtCore.SIGNAL("clicked ()"), self.addCategory)
        
        self.removeCategory = QtGui.QPushButton("")
        self.removeCategory.setIcon(QtGui.QIcon(":/data/img/delete_16x16.png"))
        self.removeCategory.setToolTip(u"Remove category")
        self.removeCategory.setFlat(True)
        self.removeCategory.setDisabled(True)
        self.removeCategory.setStyleSheet("QPushButton:hover:!pressed{border: 1px solid #808080; background-color: #e6e6e6;} ")
        self.connect(self.removeCategory, QtCore.SIGNAL("clicked ()"), self.deleteCategory)
        ########################
        ########################
        mainLayLeftSide = QtGui.QVBoxLayout()
        mainLayLeftSide.addWidget(modelsListExpand)
        mainLayLeftSide.addWidget(modelsListCollapse)
        mainLayLeftSide.addWidget(modelsListSelectAll)
        mainLayLeftSide.addWidget(modelsListDeselectAll)
        mainLayLeftSide.addWidget(separator())
        mainLayLeftSide.addWidget(modelsListReload)
        mainLayLeftSide.addWidget(modelsListSaveCopy)
        mainLayLeftSide.addWidget(modelsListImportDatabase)
        mainLayLeftSide.addWidget(separator())
        mainLayLeftSide.addWidget(self.removeModel)
        mainLayLeftSide.addWidget(self.deleteColFiles)
        mainLayLeftSide.addWidget(self.setOneCategoryForModels)
        mainLayLeftSide.addWidget(separator())
        mainLayLeftSide.addWidget(self.editCategory)
        mainLayLeftSide.addWidget(addCategoryButton)
        mainLayLeftSide.addWidget(self.removeCategory)
        mainLayLeftSide.addStretch(10)
        mainLayLeftSide.setContentsMargins(0, 0, 0, 0)
        
        return mainLayLeftSide
 
    ##########################
    # searcher
    ##########################
    def searcherLayout(self):
        self.searcher = QtGui.QLineEdit()
        self.searcher.setStyleSheet("border: 1px solid #808080")
        self.connect(self.searcher, QtCore.SIGNAL("textChanged (const QString&)"), self.wyszukajObiekty)
       
        searcherNext = flatButton(":/data/img/next_16x16.png", u"Next package")
        self.connect(searcherNext, QtCore.SIGNAL("clicked ()"), self.wyszukajObiektyNext)
        
        searcherPrev = flatButton(":/data/img/previous_16x16.png", u"Previous package")
        self.connect(searcherPrev, QtCore.SIGNAL("clicked ()"), self.wyszukajObiektyPrev)
        
        mainLayLeftSide = QtGui.QHBoxLayout()
        mainLayLeftSide.addWidget(searcherPrev)
        mainLayLeftSide.addWidget(self.searcher)
        mainLayLeftSide.addWidget(searcherNext)
        mainLayLeftSide.setContentsMargins(0, 0, 0, 0)
        return mainLayLeftSide
