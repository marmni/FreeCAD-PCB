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
import FreeCAD
import glob
import sys
#
from PCBdataBase import dataBase
from PCBconf import supSoftware, defSoftware, partPaths
from PCBfunctions import getFromSettings_databasePath, kolorWarstwy, prepareScriptCopy, importScriptCopy, configParserRead, configParserWrite
from PCBcategories import addCategoryGui, removeCategoryGui, updateCategoryGui, setOneCategoryGui
from PCBpartManaging import partExistPath

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
        for i, j in supSoftware.items():
            self.supSoftware.addItem(j['name'], i)
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
        self.parent.setNewPath(item[0].model().filePath(item[0]))
        
        return super(pathChooser, self).selectionChanged(item1, item2)


class addNewPath(QtGui.QDialog):
    def __init__(self, lista, parent=None):
        QtGui.QDialog.__init__(self, parent)
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
        layPathsLis.addWidget(self.pathsList, 0, 0, 5, 1)
        layPathsLis.addWidget(editPathButton, 0, 1, 1, 1)
        layPathsLis.addWidget(removePathButton, 1, 1, 1, 1)
        layPathsLis.addWidget(separator(), 2, 1, 1, 1)
        layPathsLis.addWidget(checkPathsButton, 3, 1, 1, 1)
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
                if i in path:
                    self.addItem(path.replace(os.path.join(i, ''), ''))  # relative path
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
        
        self.setColumnCount(9)
        self.setHorizontalHeaderLabels([u"", u"Parameter", "Visible", "X", "Y", "Z", "Size", "Color", "Align"])
        self.setSortingEnabled(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().hide()
        self.setGridStyle(QtCore.Qt.PenStyle(QtCore.Qt.NoPen))
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtGui.QAbstractItemView.NoSelection)
        self.setStyleSheet('''
                border: 1px solid #808080;
            ''')
        
    def __str__(self):
        table = {}
        for i in range(0, self.rowCount(), 1):
            table[u"{0}".format(self.item(i, 1).text())] = [
                self.cellWidget(i, 0).isChecked(),
                self.cellWidget(i, 2).currentText(),
                self.cellWidget(i, 3).value(),
                self.cellWidget(i, 4).value(),
                self.cellWidget(i, 5).value(),
                self.cellWidget(i, 6).value(),
                self.cellWidget(i, 7).getColor(),
                u"{0}".format(self.cellWidget(i, 8).currentText())
            ]
        
        return str(table)
        
    def updateType(self, key, param):
        for i in range(0, self.rowCount(), 1):
            if self.item(i, 1).text() == key:
                self.cellWidget(i, 0).setChecked(eval(str(param[0])))
                self.cellWidget(i, 2).setCurrentIndex(self.cellWidget(i, 2).findText(param[1]))
                self.cellWidget(i, 3).setValue(param[2])
                self.cellWidget(i, 4).setValue(param[3])
                self.cellWidget(i, 5).setValue(param[4])
                self.cellWidget(i, 6).setValue(param[5])
                self.cellWidget(i, 7).setColor(self.cellWidget(i, 7).PcbColorToRGB(param[6]))
                self.cellWidget(i, 8).setCurrentIndex(self.cellWidget(i, 8).findText(param[7]))
                break
        
    def resetTable(self):
        for i in range(0, self.rowCount(), 1):
            self.cellWidget(i, 0).setChecked(False)
            self.cellWidget(i, 2).setCurrentIndex(0)
            self.cellWidget(i, 3).setValue(0.0)
            self.cellWidget(i, 4).setValue(0.0)
            self.cellWidget(i, 5).setValue(0.0)
            self.cellWidget(i, 6).setValue(1.27)
            self.cellWidget(i, 7).setColor([255, 255, 255])
            self.cellWidget(i, 8).setCurrentIndex(4)
        
    def addRow(self, rowType):
        self.insertRow(self.rowCount())
        row = self.rowCount() - 1
        
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
        
        g = QtGui.QDoubleSpinBox()
        g.setSingleStep(0.1)
        g.setValue(1.27)
        g.setSuffix("mm")
        self.setCellWidget(row, 6, g)
        
        color = kolorWarstwy()
        color.setToolTip(u"Click to change color")
        self.setCellWidget(row, 7, color)
        
        i = QtGui.QComboBox()
        i.addItems(["bottom-left", "bottom-center", "bottom-right", "center-left", "center", "center-right", "top-left", "top-center", "top-right"])
        i.setCurrentIndex(4)
        self.setCellWidget(row, 8, i)
        
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
        mainItem = QtGui.QTreeWidgetItem([model.name, model.description])
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
        
        # models withoud category
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


class dodajElement(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u"Assign models")
        self.setWindowIcon(QtGui.QIcon(":/data/img/uklad.png"))
        
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
        self.splitter.setChildrenCollapsible(False)
        self.splitter.addWidget(mainWidgetLeftSide)
        self.splitter.addWidget(self.mainWidgetRightSide())
        
        mainLay = QtGui.QHBoxLayout()
        mainLay.addWidget(self.splitter)
        mainLay.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLay)
        #
        self.reloadList()
        self.readSize()
        
    def readSize(self):
        data = configParserRead('assignWindow')
        if data:
            try:
                x = int(data['window_x'])
                y = int(data['window_y'])
                w = int(data['window_w'])
                h = int(data['window_h'])
                self.splitter.setSizes(eval(data['window_splitter']))
                self.modelsList.setColumnWidth(0, int(data['window_modellist']))
                
                self.setGeometry(x, y, w, h)
            except Exception as e:
                FreeCAD.Console.PrintWarning(u"{0} \n".format(e))
    
    def closeEvent(self, event):
        data = {}
        data['window_x'] = self.x()
        data['window_y'] = self.y()
        data['window_w'] = self.width()
        data['window_h'] = self.height()
        data['window_splitter'] = self.splitter.sizes()
        data['window_modellist'] = self.modelsList.columnWidth(0)
        
        configParserWrite('assignWindow', data)
        ###########
        event.accept()
    
    def importDatabase(self):
        try:
            dial = importScriptCopy()
            dial.exec_()
        except Exception as e:
            FreeCAD.Console.PrintWarning(u"Error: {0} \n".format(e))

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
    
    def readFormData(self):
        try:
            return {"name" : str(self.packageName.text()).strip(),
                   "description": str(self.modelDescription.toPlainText()),
                   "categoryID" : self.modelCategory.itemData(self.modelCategory.currentIndex(), QtCore.Qt.UserRole),
                   "datasheet" : str(self.datasheetPath.text()).strip(),
                   "path3DModels": str(self.pathToModel.text()).strip(),
                   "isSocket" : self.boxSetAsSocketa.isChecked(),
                   "isSocketHeight" : float(self.socketHeight.value()),
                   "socketID" : self.socketModelName.itemData(self.socketModelName.currentIndex(), QtCore.Qt.UserRole),
                   "socketIDSocket" : self.boxAddSocket.isChecked(),
                   "software" : self.modelSettings.getData()
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
            dial.loadCategories(self.sql.getAllcategories())
            
            if dial.exec_():
                for i in QtGui.QTreeWidgetItemIterator(self.modelsList):
                    if str(i.value().data(0, QtCore.Qt.UserRole + 1)) == 'C':
                        continue
                    if not i.value().checkState(0) == QtCore.Qt.Checked:
                        continue
                    #
                    item = i.value()
                    modelID = str(item.data(0, QtCore.Qt.UserRole))
                    categoryID = dial.parentCategory.itemData(dial.parentCategory.currentIndex())
                    
                    self.sql.setCategoryForModel(modelID, categoryID)
                    item.setCheckState(0, QtCore.Qt.Unchecked)
                
                self.reloadList()
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
            self.modelCategory.setCurrentIndex(self.modelCategory.findData(model["categoryID"]))
            # software
            self.modelSettings.clear()
            self.modelSettings.addRows(model["software"])
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
        
        #try:
            #for i, j in eval(dane["adjust"]).items():
                #self.modelAdjust.updateType(i, j)
        #except:
            #self.modelAdjust.resetTable()
        
        #soft = eval(dane["soft"])
        #for i in soft:
            #try:
                #self.modelSettings.addRow(i)
            #except Exception as e:
                #FreeCAD.Console.PrintWarning("{0} \n".format(e))
        
    def resetSetAsSocket(self, value):
        if value:
            self.socketHeight.setValue(0)
            self.boxSetAsSocketa.setChecked(False)
            
    def resetSetSocket(self, value):
        if value:
            self.boxAddSocket.setChecked(False)
            self.socketModelName.setCurrentInedx(-1)
    
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
        
        dial = updateCategoryGui()
        dial.categoryName.setText(categoryData.name)
        dial.categoryDescription.setText(categoryData.description)
        dial.loadCategories(self.sql.getAllcategories(), categoryData.parentID)
        
        if dial.exec_():
            if str(dial.categoryName.text()).strip() == '':
                FreeCAD.Console.PrintWarning("{0} \n".format(u'Mandatory field is empty!'))
                return
            
            name = str(dial.categoryName.text()).strip()
            parentID = dial.parentCategory.itemData(dial.parentCategory.currentIndex())
            if parentID == -1 or parentID == None:
                parentID = 0
            parentID = int(parentID)
            description = str(dial.categoryDescription.toPlainText()).strip()
            
            if self.sql.updateCategory(ID, name, parentID, description):
                #self.modelsList.reloadList(self.sql.getAllcategoriesWithSubCat(0))
                self.reloadList()
    
    def addCategory(self):
        dial = addCategoryGui()
        dial.loadCategories(self.sql.getAllcategories())
        
        if dial.exec_():
            if str(dial.categoryName.text()).strip() == '':
                FreeCAD.Console.PrintWarning("{0} \n".format(u'Mandatory field is empty!'))
                return
            
            if self.sql.addCategory(str(dial.categoryName.text()).strip(), dial.parentCategory.itemData(dial.parentCategory.currentIndex()), str(dial.categoryDescription.toPlainText()).strip()):
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
            self.setOneCategoryForModels.setDisabled(True)
        else:
            self.editCategory.setDisabled(True)
            self.removeCategory.setDisabled(True)
            self.removeModel.setDisabled(False)
            self.setOneCategoryForModels.setDisabled(False)
            #
            try:
                dane = self.sql.getModelByID(self.modelsList.currentItem().data(0, QtCore.Qt.UserRole))
                if dane[0]:
                    modelData = self.sql.convertToTable(dane[1])
                    modelData = self.sql.packagesDataToDictionary(modelData)
                    self.showData(modelData)
            except Exception as e:
                FreeCAD.Console.PrintWarning("ERROR: {0}.\n".format(e))

    def reloadCategoryList(self):
        currentIndex = self.modelCategory.currentIndex()
        self.modelCategory.clear()
        #
        for i in self.sql.getAllcategories():
            self.modelCategory.addItem("{0}".format(i.name))
            self.modelCategory.setItemData(self.modelCategory.count() - 1, i.id, QtCore.Qt.UserRole)
        
        self.modelCategory.insertItem(-1, 'None', 0)
        if currentIndex and currentIndex >= 1:
            self.modelCategory.setCurrentIndex(currentIndex)
        else:
            self.modelCategory.setCurrentIndex(0)
            
    def reloadList(self):
        ''' reload list of packages from current lib '''
        self.editCategory.setDisabled(True)
        self.removeCategory.setDisabled(True)
        self.removeModel.setDisabled(True)
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
    
    def checkSockets(self, tabID):
        if tabID == 1 and self.socketModelName.count() == 0:
            self.boxAddSocket.setDisabled(True)
        else:
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
        
        pathToModelInfo = QtGui.QPushButton("")
        pathToModelInfo.setToolTip(u"Edit")
        #pathToModelInfo.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        pathToModelInfo.setIcon(QtGui.QIcon(":/data/img/edit_16x16.png"))
        pathToModelInfo.setFlat(True)
        pathToModelInfo.setStyleSheet('''
                QPushButton
                {
                    border: 0px;
                    margin-top: 2px;
                    width: 15px;
                    height: 15px;
                }
            ''')
        self.connect(pathToModelInfo, QtCore.SIGNAL("clicked ()"), self.addNewPathF)
        
        #########################
        ## datasheet
        #########################
        self.datasheetPath = QtGui.QLineEdit("")
        
        datasheetPathPrz = QtGui.QPushButton("")
        datasheetPathPrz.setToolTip(u"Open datasheet")
        #datasheetPathPrz.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        datasheetPathPrz.setIcon(QtGui.QIcon(":/data/img/browser_16x16.png"))
        datasheetPathPrz.setFlat(True)
        datasheetPathPrz.setStyleSheet('''
                QPushButton
                {
                    border: 0px;
                    margin-top: 2px;
                    width: 15px;
                    height: 15px;
                }
            ''')
        self.connect(datasheetPathPrz, QtCore.SIGNAL("clicked ()"), self.loadDatasheet)
        
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
        self.modelCategory = QtGui.QComboBox()
        
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
        
        modelSettingsAdd = QtGui.QPushButton("")
        modelSettingsAdd.setToolTip(u"Add")
        #modelSettingsAdd.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        modelSettingsAdd.setIcon(QtGui.QIcon(":/data/img/add_16x16.png"))
        modelSettingsAdd.setFlat(True)
        modelSettingsAdd.setStyleSheet('''
                QPushButton
                {
                    border: 0px;
                    margin-top: 2px;
                    width: 16px;
                    height: 16px;
                }
            ''')
        self.connect(modelSettingsAdd, QtCore.SIGNAL("clicked ()"), self.modelSettings.addNewModel)
        
        modelSettingsDelete = QtGui.QPushButton("")
        modelSettingsDelete.setToolTip(u"Delete")
        #modelSettingsDelete.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        modelSettingsDelete.setIcon(QtGui.QIcon(":/data/img/delete_16x16.png"))
        modelSettingsDelete.setFlat(True)
        modelSettingsDelete.setStyleSheet('''
                QPushButton
                {
                    border: 0px;
                    margin-top: 2px;
                    width: 16px;
                    height: 16px;
                }
            ''')
        self.connect(modelSettingsDelete, QtCore.SIGNAL("clicked ()"), self.modelSettings.deleteModel)
        
        modelSettingsEdit = QtGui.QPushButton("")
        modelSettingsEdit.setToolTip(u"Edit")
        #modelSettingsEdit.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        modelSettingsEdit.setIcon(QtGui.QIcon(":/data/img/edit_16x16.png"))
        modelSettingsEdit.setFlat(True)
        modelSettingsEdit.setStyleSheet('''
                QPushButton
                {
                    border: 0px;
                    margin-top: 2px;
                    width: 16px;
                    height: 16px;
                }
            ''')
        self.connect(modelSettingsEdit, QtCore.SIGNAL("clicked ()"), self.modelSettings.editModel)
        
        modelSettingsCopy = QtGui.QPushButton("")
        modelSettingsCopy.setToolTip(u"Copy")
        #modelSettingsCopy.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        modelSettingsCopy.setIcon(QtGui.QIcon(":/data/img/copy.png"))
        modelSettingsCopy.setFlat(True)
        modelSettingsCopy.setStyleSheet('''
                QPushButton
                {
                    border: 0px;
                    margin-top: 2px;
                    width: 16px;
                    height: 16px;
                }
            ''')
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
        layRightSide_Main.addWidget(QtGui.QLabel(u"Category"), 4, 0, 1, 1)
        layRightSide_Main.addWidget(self.modelCategory, 4, 1, 1, 2)
        layRightSide_Main.addWidget(self.modelSettings, 5, 0, 6, 2)
        layRightSide_Main.addWidget(modelSettingsAdd, 6, 2, 1, 1)
        layRightSide_Main.addWidget(modelSettingsDelete, 7, 2, 1, 1)
        layRightSide_Main.addWidget(modelSettingsEdit, 8, 2, 1, 1)
        layRightSide_Main.addWidget(modelSettingsCopy, 9, 2, 1, 1)
        
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
        modelsListSaveCopy = QtGui.QPushButton("")
        #modelsListSaveCopy.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        modelsListSaveCopy.setIcon(QtGui.QIcon(":/data/img/databaseExport.png"))
        modelsListSaveCopy.setToolTip(u"Save database copy")
        modelsListSaveCopy.setFlat(True)
        self.connect(modelsListSaveCopy, QtCore.SIGNAL("clicked ()"), self.prepareCopy)
        
        modelsListImportDatabase = QtGui.QPushButton("")
        #modelsListImportDatabase.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        modelsListImportDatabase.setIcon(QtGui.QIcon(":/data/img/databaseUpload.png"))
        modelsListImportDatabase.setToolTip(u"Import database")
        modelsListImportDatabase.setFlat(True)
        self.connect(modelsListImportDatabase, QtCore.SIGNAL("clicked ()"), self.importDatabase)
        
        ########################
        # models list
        ########################
        modelsListExpand = QtGui.QPushButton("")
        modelsListExpand.setIcon(QtGui.QIcon(":/data/img/expand.png"))
        modelsListExpand.setToolTip(u"Expand all")
        modelsListExpand.setFlat(True)
        self.connect(modelsListExpand, QtCore.SIGNAL("clicked ()"), self.modelsList.expandAll)
        
        modelsListCollapse = QtGui.QPushButton("")
        modelsListCollapse.setIcon(QtGui.QIcon(":/data/img/collapse.png"))
        modelsListCollapse.setToolTip(u"Collapse all")
        modelsListCollapse.setFlat(True)
        self.connect(modelsListCollapse, QtCore.SIGNAL("clicked ()"), self.modelsList.collapseAll)
        
        modelsListReload = QtGui.QPushButton("")
        modelsListReload.setIcon(QtGui.QIcon(":/data/img/databaseReload.png"))
        modelsListReload.setToolTip(u"Reload database")
        modelsListReload.setFlat(True)
        self.connect(modelsListReload, QtCore.SIGNAL("clicked ()"), self.reloadList)
        
        self.removeModel = QtGui.QPushButton("")
        self.removeModel.setIcon(QtGui.QIcon(":/data/img/databaseDelete.png"))
        self.removeModel.setToolTip(u"Delete all selected models from database")
        self.removeModel.setFlat(True)
        self.removeModel.setDisabled(True)
        self.connect(self.removeModel, QtCore.SIGNAL("clicked ()"), self.deleteModel)
        
        self.setOneCategoryForModels = QtGui.QPushButton("")
        self.setOneCategoryForModels.setIcon(QtGui.QIcon(":/data/img/Draft_SelectGroup.png"))
        self.setOneCategoryForModels.setToolTip(u"Set one category for all selected models")
        self.setOneCategoryForModels.setFlat(True)
        self.setOneCategoryForModels.setDisabled(True)
        self.connect(self.setOneCategoryForModels, QtCore.SIGNAL("clicked ()"), self.setOneCategoryForModelsF)
        
        ########################
        # categories
        ########################
        self.editCategory = QtGui.QPushButton("")
        self.editCategory.setIcon(QtGui.QIcon(":/data/img/edit_16x16.png"))
        self.editCategory.setToolTip(u"Edit category")
        self.editCategory.setFlat(True)
        self.editCategory.setDisabled(True)
        self.connect(self.editCategory, QtCore.SIGNAL("clicked ()"), self.editCategoryF)
        
        addCategoryButton = QtGui.QPushButton("")
        addCategoryButton.setIcon(QtGui.QIcon(":/data/img/add_16x16.png"))
        addCategoryButton.setToolTip(u"Add new category")
        addCategoryButton.setFlat(True)
        self.connect(addCategoryButton, QtCore.SIGNAL("clicked ()"), self.addCategory)
        
        self.removeCategory = QtGui.QPushButton("")
        self.removeCategory.setIcon(QtGui.QIcon(":/data/img/delete_16x16.png"))
        self.removeCategory.setToolTip(u"Remove category")
        self.removeCategory.setFlat(True)
        self.removeCategory.setDisabled(True)
        self.connect(self.removeCategory, QtCore.SIGNAL("clicked ()"), self.deleteCategory)
        ########################
        ########################
        mainLayLeftSide = QtGui.QVBoxLayout()
        mainLayLeftSide.addWidget(modelsListExpand)
        mainLayLeftSide.addWidget(modelsListCollapse)
        mainLayLeftSide.addWidget(separator())
        mainLayLeftSide.addWidget(modelsListReload)
        mainLayLeftSide.addWidget(modelsListSaveCopy)
        mainLayLeftSide.addWidget(modelsListImportDatabase)
        mainLayLeftSide.addWidget(separator())
        mainLayLeftSide.addWidget(self.removeModel)
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
       
        searcherNext = QtGui.QPushButton("")
        #searcherNext.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        searcherNext.setIcon(QtGui.QIcon(":/data/img/next_16x16.png"))
        searcherNext.setToolTip(u"Next package")
        searcherNext.setFlat(True)
        self.connect(searcherNext, QtCore.SIGNAL("clicked ()"), self.wyszukajObiektyNext)
        
        searcherPrev = QtGui.QPushButton("")
        #searcherPrev.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        searcherPrev.setIcon(QtGui.QIcon(":/data/img/previous_16x16.png"))
        searcherPrev.setToolTip(u"Previous package")
        searcherPrev.setFlat(True)
        self.connect(searcherPrev, QtCore.SIGNAL("clicked ()"), self.wyszukajObiektyPrev)
        
        mainLayLeftSide = QtGui.QHBoxLayout()
        mainLayLeftSide.addWidget(searcherPrev)
        mainLayLeftSide.addWidget(self.searcher)
        mainLayLeftSide.addWidget(searcherNext)
        mainLayLeftSide.setContentsMargins(0, 0, 0, 0)
        return mainLayLeftSide

    
    
    
    ##def __init__(self, parent=None):
        ##QtGui.QDialog.__init__(self, parent)
        ##self.setWindowTitle(u"Assign models")
        ##self.setWindowIcon(QtGui.QIcon(":/data/img/uklad.png"))
        
        ##self.elementID = None
        ##self.szukaneFrazy = []
        ##self.szukaneFrazyNr = 0
        ##self.sql = dataBase()
        
        #########################
        ## searcher
        #########################
        #searcher = QtGui.QLineEdit()
        #self.connect(searcher, QtCore.SIGNAL("textChanged (const QString&)"), self.wyszukajObiekty)
       
        #searcherNext = QtGui.QPushButton("")
        ##searcherNext.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        #searcherNext.setIcon(QtGui.QIcon(":/data/img/next_16x16.png"))
        #searcherNext.setToolTip(u"Next package")
        #searcherNext.setFlat(True)
        #self.connect(searcherNext, QtCore.SIGNAL("clicked ()"), self.wyszukajObiektyNext)
        
        #searcherPrev = QtGui.QPushButton("")
        ##searcherPrev.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        #searcherPrev.setIcon(QtGui.QIcon(":/data/img/previous_16x16.png"))
        #searcherPrev.setToolTip(u"Previous package")
        #searcherPrev.setFlat(True)
        #self.connect(searcherPrev, QtCore.SIGNAL("clicked ()"), self.wyszukajObiektyPrev)
        
        #########################
        ## categories
        #########################
        #self.editCategory = QtGui.QPushButton("")
        #self.editCategory.setIcon(QtGui.QIcon(":/data/img/edit_16x16.png"))
        #self.editCategory.setToolTip(u"Edit category")
        #self.editCategory.setFlat(True)
        #self.editCategory.setDisabled(True)
        #self.connect(self.editCategory, QtCore.SIGNAL("clicked ()"), self.editCategoryF)
        
        #self.addCategory = QtGui.QPushButton("")
        #self.addCategory.setIcon(QtGui.QIcon(":/data/img/add_16x16.png"))
        #self.addCategory.setToolTip(u"Add new category")
        #self.addCategory.setFlat(True)
        #self.connect(self.addCategory, QtCore.SIGNAL("clicked ()"), self.addCategoryF)
        
        #self.removeCategory = QtGui.QPushButton("")
        #self.removeCategory.setIcon(QtGui.QIcon(":/data/img/delete_16x16.png"))
        #self.removeCategory.setToolTip(u"Remove category")
        #self.removeCategory.setFlat(True)
        #self.removeCategory.setDisabled(True)
        #self.connect(self.removeCategory, QtCore.SIGNAL("clicked ()"), self.removeCategoryF)
        #########################
        ## models list
        #########################
        ##self.modelsList = modelsList()
        ##self.modelsList.sql = self.sql
        ##self.connect(self.modelsList, QtCore.SIGNAL("itemPressed (QTreeWidgetItem *,int)"), self.loadData)

        #modelsListExpand = QtGui.QPushButton("")
        ##modelsListExpand.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        #modelsListExpand.setIcon(QtGui.QIcon(":/data/img/expand.png"))
        #modelsListExpand.setToolTip(u"Expand all")
        #modelsListExpand.setFlat(True)
        #self.connect(modelsListExpand, QtCore.SIGNAL("clicked ()"), self.modelsList.expandAll)
        
        #modelsListCollapse = QtGui.QPushButton("")
        ##modelsListCollapse.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        #modelsListCollapse.setIcon(QtGui.QIcon(":/data/img/collapse.png"))
        #modelsListCollapse.setToolTip(u"Collapse all")
        #modelsListCollapse.setFlat(True)
        #self.connect(modelsListCollapse, QtCore.SIGNAL("clicked ()"), self.modelsList.collapseAll)
        
        #modelsListDelete = QtGui.QPushButton("")
        ##modelsListDelete.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        #modelsListDelete.setIcon(QtGui.QIcon(":/data/img/databaseDelete.png"))
        #modelsListDelete.setToolTip(u"Delete model from database")
        #modelsListDelete.setFlat(True)
        #self.connect(modelsListDelete, QtCore.SIGNAL("clicked ()"), self.deletePackage)
        
        #modelsListReload = QtGui.QPushButton("")
        ##modelsListReload.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        #modelsListReload.setIcon(QtGui.QIcon(":/data/img/databaseReload.png"))
        #modelsListReload.setToolTip(u"Reload database")
        #modelsListReload.setFlat(True)
        #self.connect(modelsListReload, QtCore.SIGNAL("clicked ()"), self.reloadList)
        
        #modelsListSaveCopy = QtGui.QPushButton("")
        ##modelsListSaveCopy.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        #modelsListSaveCopy.setIcon(QtGui.QIcon(":/data/img/databaseExport.png"))
        #modelsListSaveCopy.setToolTip(u"Save database copy")
        #modelsListSaveCopy.setFlat(True)
        #self.connect(modelsListSaveCopy, QtCore.SIGNAL("clicked ()"), self.sql.makeACopy)
        
        #modelsListImportDatabase = QtGui.QPushButton("")
        ##modelsListImportDatabase.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        #modelsListImportDatabase.setIcon(QtGui.QIcon(":/data/img/databaseUpload.png"))
        #modelsListImportDatabase.setToolTip(u"Import database")
        #modelsListImportDatabase.setFlat(True)
        #self.connect(modelsListImportDatabase, QtCore.SIGNAL("clicked ()"), self.importDatabase)
        
        #modelsListConvertDatabaseEntries = QtGui.QPushButton("")
        ##modelsListConvertDatabaseEntries.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        #modelsListConvertDatabaseEntries.setIcon(QtGui.QIcon(":/data/img/databaseConvert.png"))
        #modelsListConvertDatabaseEntries.setToolTip(u"Convert items")
        #modelsListConvertDatabaseEntries.setFlat(True)
        #self.connect(modelsListConvertDatabaseEntries, QtCore.SIGNAL("clicked ()"), self.convertDatabaseEntries)
        #########################
        ## package name
        #########################
        #self.packageName = QtGui.QLineEdit("")
        
        ##########################
        ### path to package
        ##########################
        #self.pathToModel = QtGui.QLineEdit("")
        #self.pathToModel.setReadOnly(True)
        
        #pathToModelInfo = QtGui.QPushButton("")
        #pathToModelInfo.setToolTip(u"Edit")
        ##pathToModelInfo.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        #pathToModelInfo.setIcon(QtGui.QIcon(":/data/img/edit_16x16.png"))
        #pathToModelInfo.setFlat(True)
        #pathToModelInfo.setStyleSheet('''
                #QPushButton
                #{
                    #border: 0px;
                    #margin-top: 2px;
                    #width: 15px;
                    #height: 15px;
                #}
            #''')
        #self.connect(pathToModelInfo, QtCore.SIGNAL("clicked ()"), self.addNewPathF)
        
        ##########################
        ### datasheet
        ##########################
        #self.datasheetPath = QtGui.QLineEdit("")
        
        #datasheetPathPrz = QtGui.QPushButton("")
        #datasheetPathPrz.setToolTip(u"Open datasheet")
        ##datasheetPathPrz.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        #datasheetPathPrz.setIcon(QtGui.QIcon(":/data/img/browser_16x16.png"))
        #datasheetPathPrz.setFlat(True)
        #datasheetPathPrz.setStyleSheet('''
                #QPushButton
                #{
                    #border: 0px;
                    #margin-top: 2px;
                    #width: 15px;
                    #height: 15px;
                #}
            #''')
        #self.connect(datasheetPathPrz, QtCore.SIGNAL("clicked ()"), self.loadDatasheet)
        
        ##########################
        ### socket for model
        ##########################
        #self.socketModelName = QtGui.QComboBox()
        
        #self.boxAddSocket = QtGui.QGroupBox()
        #self.boxAddSocket.setTitle(u"Add socket")
        #self.boxAddSocket.setCheckable(True)
        #self.boxAddSocket.setChecked(False)
        #boxAddSocketLay = QtGui.QHBoxLayout(self.boxAddSocket)
        #boxAddSocketLay.addWidget(QtGui.QLabel(u"Socket"))
        #boxAddSocketLay.addWidget(self.socketModelName)
        
        #self.connect(self.boxAddSocket, QtCore.SIGNAL("toggled (bool)"), self.resetSetAsSocket)
        ##########################
        ### set model as socket
        ##########################
        #self.socketHeight = QtGui.QDoubleSpinBox()
        #self.socketHeight.setSuffix(" mm")
        
        #self.boxSetAsSocketa = QtGui.QGroupBox()
        #self.boxSetAsSocketa.setTitle(u"Set as socket")
        #self.boxSetAsSocketa.setCheckable(True)
        #self.boxSetAsSocketa.setChecked(False)
        #layBoxPodstawka = QtGui.QHBoxLayout(self.boxSetAsSocketa)
        #layBoxPodstawka.addWidget(QtGui.QLabel(u"Height"))
        #layBoxPodstawka.addWidget(self.socketHeight)
        
        #self.connect(self.boxSetAsSocketa, QtCore.SIGNAL("toggled (bool)"), self.resetSetSocket)
        ##########################
        ### model category
        ##########################
        #self.modelCategory = QtGui.QComboBox()
        
        ##########################
        ### description
        ##########################
        #self.modelDescription = QtGui.QTextEdit()
        #self.modelDescription.setStyleSheet('''
                #border: 1px solid #808080;
            #''')
        
        ##########################
        ### save / save as / clean button
        ##########################
        #saveModelSettings = QtGui.QPushButton("Save")
        #saveModelSettings.setIcon(QtGui.QIcon(":/data/img/save_22x22.png"))
        #self.connect(saveModelSettings, QtCore.SIGNAL("clicked ()"), self.addNewPackage)
        
        #cleanForm = QtGui.QPushButton("Clean/New")
        #cleanForm.setIcon(QtGui.QIcon(":/data/img/clear_16x16.png"))
        #self.connect(cleanForm, QtCore.SIGNAL("clicked ()"), self.clearData)
        
        #saveAsModelSettings = QtGui.QPushButton("Save As New")
        #saveAsModelSettings.setIcon(QtGui.QIcon(":/data/img/save_22x22.png"))
        #self.connect(saveAsModelSettings, QtCore.SIGNAL("clicked ()"), self.addPackageAsNew)
        
        #closeDialog = QtGui.QPushButton("Close")
        #self.connect(closeDialog, QtCore.SIGNAL("clicked ()"), self, QtCore.SLOT('close()'))
        
        #########################
        ## adjust name/value
        #########################
        #self.modelAdjust = modelAdjustTable()
        #self.modelAdjust.addRow("Name")
        #self.modelAdjust.addRow("Value")
        
        ##########################
        ### model settings
        ##########################
        #self.modelSettings = modelSettingsTable()
        
        #modelSettingsAdd = QtGui.QPushButton("")
        #modelSettingsAdd.setToolTip(u"Add")
        ##modelSettingsAdd.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        #modelSettingsAdd.setIcon(QtGui.QIcon(":/data/img/add_16x16.png"))
        #modelSettingsAdd.setFlat(True)
        #modelSettingsAdd.setStyleSheet('''
                #QPushButton
                #{
                    #border: 0px;
                    #margin-top: 2px;
                    #width: 16px;
                    #height: 16px;
                #}
            #''')
        #self.connect(modelSettingsAdd, QtCore.SIGNAL("clicked ()"), self.modelSettings.addNewModel)
        
        #modelSettingsDelete = QtGui.QPushButton("")
        #modelSettingsDelete.setToolTip(u"Delete")
        ##modelSettingsDelete.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        #modelSettingsDelete.setIcon(QtGui.QIcon(":/data/img/delete_16x16.png"))
        #modelSettingsDelete.setFlat(True)
        #modelSettingsDelete.setStyleSheet('''
                #QPushButton
                #{
                    #border: 0px;
                    #margin-top: 2px;
                    #width: 16px;
                    #height: 16px;
                #}
            #''')
        #self.connect(modelSettingsDelete, QtCore.SIGNAL("clicked ()"), self.modelSettings.deleteModel)
        
        #modelSettingsEdit = QtGui.QPushButton("")
        #modelSettingsEdit.setToolTip(u"Edit")
        ##modelSettingsEdit.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        #modelSettingsEdit.setIcon(QtGui.QIcon(":/data/img/edit_16x16.png"))
        #modelSettingsEdit.setFlat(True)
        #modelSettingsEdit.setStyleSheet('''
                #QPushButton
                #{
                    #border: 0px;
                    #margin-top: 2px;
                    #width: 16px;
                    #height: 16px;
                #}
            #''')
        #self.connect(modelSettingsEdit, QtCore.SIGNAL("clicked ()"), self.modelSettings.editModel)
        
        #modelSettingsCopy = QtGui.QPushButton("")
        #modelSettingsCopy.setToolTip(u"Copy")
        ##modelSettingsCopy.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        #modelSettingsCopy.setIcon(QtGui.QIcon(":/data/img/copy.png"))
        #modelSettingsCopy.setFlat(True)
        #modelSettingsCopy.setStyleSheet('''
                #QPushButton
                #{
                    #border: 0px;
                    #margin-top: 2px;
                    #width: 16px;
                    #height: 16px;
                #}
            #''')
        #self.connect(modelSettingsCopy, QtCore.SIGNAL("clicked ()"), self.modelSettings.copyModel)

        #########################
        ## layouts
        #########################
        ## right side
        #packageFooter = QtGui.QHBoxLayout()
        #packageFooter.addWidget(saveModelSettings)
        #packageFooter.addWidget(saveAsModelSettings)
        #packageFooter.addWidget(cleanForm)
        #if os.name == 'posix':
            #packageFooter.addWidget(closeDialog)
        
        ## rightSide_Main
        #rightSide_Main = QtGui.QWidget()
        #layRightSide_Main = QtGui.QGridLayout(rightSide_Main)
        #layRightSide_Main.addWidget(QtGui.QLabel(u"Package type"), 0, 0, 1, 1)
        #layRightSide_Main.addWidget(self.packageName, 0, 1, 1, 2)
        #layRightSide_Main.addWidget(QtGui.QLabel(u"Path to element"), 2, 0, 1, 1)
        #layRightSide_Main.addWidget(self.pathToModel, 2, 1, 1, 1)
        #layRightSide_Main.addWidget(pathToModelInfo, 2, 2, 1, 1)
        #layRightSide_Main.addWidget(QtGui.QLabel(u"Datasheet"), 3, 0, 1, 1)
        #layRightSide_Main.addWidget(self.datasheetPath, 3, 1, 1, 1)
        #layRightSide_Main.addWidget(datasheetPathPrz, 3, 2, 1, 1)
        #layRightSide_Main.addWidget(QtGui.QLabel(u"Category"), 4, 0, 1, 1)
        #layRightSide_Main.addWidget(self.modelCategory, 4, 1, 1, 2)
        #layRightSide_Main.addWidget(self.modelSettings, 5, 0, 6, 2)
        #layRightSide_Main.addWidget(modelSettingsAdd, 6, 2, 1, 1)
        #layRightSide_Main.addWidget(modelSettingsDelete, 7, 2, 1, 1)
        #layRightSide_Main.addWidget(modelSettingsEdit, 8, 2, 1, 1)
        #layRightSide_Main.addWidget(modelSettingsCopy, 9, 2, 1, 1)
        
        ##  rightSide_Other
        #rightSide_Other = QtGui.QWidget()
        #layRightSide_Other = QtGui.QGridLayout(rightSide_Other)
        #layRightSide_Other.addWidget(self.modelAdjust, 0, 0, 1, 2)
        #layRightSide_Other.addWidget(self.boxAddSocket, 1, 0, 1, 2)
        #layRightSide_Other.addWidget(self.boxSetAsSocketa, 2, 0, 1, 2)
        #layRightSide_Other.addWidget(QtGui.QLabel("Description"), 3, 0, 1, 1, QtCore.Qt.AlignTop)
        #layRightSide_Other.addWidget(self.modelDescription, 3, 1, 1, 1)
        
        #layRightSide_Other.setColumnStretch(1, 10)
        ######
        #self.RightSide_tab = QtGui.QTabWidget()
        #self.RightSide_tab.addTab(rightSide_Main, u"Main")
        #self.RightSide_tab.addTab(rightSide_Other, u"Other")
        
        #mainWidgetRightSide = QtGui.QWidget()
        #mainLayRightSide = QtGui.QGridLayout(mainWidgetRightSide)
        #mainLayRightSide.addWidget(self.RightSide_tab, 0, 0, 1, 1)
        #mainLayRightSide.addItem(QtGui.QSpacerItem(1, 15), 1, 0, 1, 3)
        #mainLayRightSide.addLayout(packageFooter, 2, 0, 1, 3)
        #mainLayRightSide.setRowStretch(0, 20)
        #mainLayRightSide.setContentsMargins(0, 0, 0, 0)
        
        ## left layout
        #leftSideLeftToolbar = QtGui.QVBoxLayout()
        #leftSideLeftToolbar.addWidget(modelsListCollapse)
        #leftSideLeftToolbar.addWidget(modelsListExpand)
        #leftSideLeftToolbar.addWidget(separator())
        #leftSideLeftToolbar.addWidget(modelsListReload)
        #leftSideLeftToolbar.addWidget(modelsListImportDatabase)
        #leftSideLeftToolbar.addWidget(modelsListSaveCopy)
        #leftSideLeftToolbar.addWidget(modelsListConvertDatabaseEntries)
        #leftSideLeftToolbar.addWidget(separator())
        #leftSideLeftToolbar.addWidget(modelsListDelete)
        #leftSideLeftToolbar.addWidget(separator())
        #leftSideLeftToolbar.addWidget(self.addCategory)
        #leftSideLeftToolbar.addWidget(self.editCategory)
        #leftSideLeftToolbar.addWidget(self.removeCategory)
        #leftSideLeftToolbar.addStretch(10)
        
        #mainWidgetLeftSide = QtGui.QWidget()
        #mainLayLeftSide = QtGui.QGridLayout(mainWidgetLeftSide)
        #mainLayLeftSide.setContentsMargins(0, 0, 10, 0)
        #mainLayLeftSide.addLayout(leftSideLeftToolbar, 1, 0, 1, 1)
        #mainLayLeftSide.addWidget(searcherPrev, 0, 1, 1, 1)
        #mainLayLeftSide.addWidget(searcher, 0, 2, 1, 1)
        #mainLayLeftSide.addWidget(searcherNext, 0, 3, 1, 1)
        #mainLayLeftSide.addWidget(self.modelsList, 1, 1, 1, 4)
        #mainLayLeftSide.setRowStretch(1, 10)
        #mainLayLeftSide.setColumnStretch(2, 10)
        
        ## main layout
        #splitter = QtGui.QSplitter()
        #splitter.setChildrenCollapsible(False)
        #splitter.addWidget(mainWidgetLeftSide)
        #splitter.addWidget(mainWidgetRightSide)
        
        #mainLay = QtGui.QHBoxLayout()
        #mainLay.addWidget(splitter)
        #self.setLayout(mainLay)
        ###
        ##self.reloadList()
    
    #def editCategoryF(self):
        #try:
            #ID = int(self.modelsList.currentItem().data(0, QtCore.Qt.UserRole))
            #dial = updateCategoryGui(ID)
            
            #if dial.exec_():
                #if str(dial.categoryName.text()).strip() == '':
                    #FreeCAD.Console.PrintWarning("{0} \n".format(u'Mandatory field is empty!'))
                    #return
            
                #dial.updateCategory()
                ##
                #categoryData = readCategories()[ID]
                #self.modelsList.currentItem().setText(0, categoryData[0])
                #self.modelsList.currentItem().setText(1, categoryData[1])
                #self.reloadCategoryList()
        #except Exception as e:
            #pass
    
    #def addCategoryF(self):
        #try:
            #dial = addCategoryGui()
            
            #if dial.exec_():
                #if str(dial.categoryName.text()).strip() == '':
                    #FreeCAD.Console.PrintWarning("{0} \n".format(u'Mandatory field is empty!'))
                    #return
                
                #dial.addCategory()
                #self.reloadList()
        #except Exception as e:
            #pass
        
    #def removeCategoryF(self):
        #try:
            #ID = int(self.modelsList.currentItem().data(0, QtCore.Qt.UserRole))
            #removeCategoryGui(ID)
            #self.reloadList()
        #except Exception as e:
            #FreeCAD.Console.PrintWarning("{0} \n".format(e))
    
    #def deletePackage(self):
        #''' delete selected packages from lib '''
        #try:
            #delAll = False
            ##
            #for i in QtGui.QTreeWidgetItemIterator(self.modelsList):
                #if str(i.value().data(0, QtCore.Qt.UserRole + 1)) == 'C':
                    #continue
                #if not i.value().checkState(0) == QtCore.Qt.Checked:
                    #continue
                ###########
                #item = i.value()
                #objectID = str(item.data(0, QtCore.Qt.UserRole))
                ###########
                #if not delAll:
                    #dial = QtGui.QMessageBox()
                    #dial.setText(u"Delete selected package {0}?".format(item.text(0)))
                    #dial.setWindowTitle("Caution!")
                    #dial.setIcon(QtGui.QMessageBox.Question)
                    #delete_YES = dial.addButton('Yes', QtGui.QMessageBox.YesRole)
                    #delete_YES_ALL = dial.addButton('Yes for all', QtGui.QMessageBox.YesRole)
                    #delete_NO = dial.addButton('No', QtGui.QMessageBox.RejectRole)
                    #delete_NO_ALL = dial.addButton('No for all', QtGui.QMessageBox.RejectRole)
                    #dial.exec_()
                    
                    #if dial.clickedButton() == delete_NO_ALL:
                        #break
                    #elif dial.clickedButton() == delete_YES_ALL:
                        #delAll = True
                    #elif dial.clickedButton() == delete_NO:
                        #continue
                ##
                #self.sql.delPackage(objectID)
                #item.setCheckState(0, QtCore.Qt.Unchecked)
                #item.setHidden(True)
            ###########
        #except Exception as e:
            #FreeCAD.Console.PrintWarning("{0} \n".format(e))
    
    #def resetSetAsSocket(self, value):
        #if value:
            #self.socketHeight.setValue(0)
            #self.boxSetAsSocketa.setChecked(False)
            
    #def resetSetSocket(self, value):
        #if value:
            #self.boxAddSocket.setChecked(False)
            #self.socketModelName.setCurrentInedx(-1)

    #def importDatabase(self):
        #if self.sql.readFromXML():
            #self.reloadList()
    
    #def convertDatabaseEntries(self):
        #if self.sql.convertDatabaseEntries():
            #self.reloadList()

    #def addNewPathF(self):
        #'''  '''
        #dial = addNewPath(self.pathToModel.text())
        #if dial.exec_():
            #path = []
            #for i in range(dial.pathsList.count()):
                #path.append(dial.pathsList.item(i).text())
            #self.pathToModel.setText(';'.join(path))

    #def loadDatasheet(self):
        #''' load datasheet of selected package '''
        #url = str(self.datasheetPath.text()).strip()
        #if len(url):
            #if url.startswith("http://") or url.startswith("https://") or url.startswith("www."):
                #QtGui.QDesktopServices().openUrl(QtCore.QUrl(url))
            #else:
                #QtGui.QDesktopServices().openUrl(QtCore.QUrl("file:///{0}".format(url), QtCore.QUrl.TolerantMode))
    
    #def clearData(self):
        #''' clean form '''
        #tablica = {"id": None,
                   #"description": "",
                   #"add_socket": '[False, None]',
                   #"name": '',
                   #"datasheet": "",
                   #"path": '',
                   #"soft": '[]',
                   #"socket": '[False, 0.0]',
                   #'category': '-1'}
        #self.showData(tablica)
        
    #def readFormData(self):
        #return {"name": str(self.packageName.text()).strip(),
                #"path": str(self.pathToModel.text()).strip(),
                #"add_socket": str([self.boxAddSocket.isChecked(), self.socketModelName.itemData(self.socketModelName.currentIndex(), QtCore.Qt.UserRole)]),
                #"socket": str([self.boxSetAsSocketa.isChecked(), self.socketHeight.value()]),
                #"description": str(self.modelDescription.toPlainText()),
                #"datasheet": str(self.datasheetPath.text()).strip(),
                #"soft": str(self.modelSettings),
                #"category": self.modelCategory.itemData(self.modelCategory.currentIndex(), QtCore.Qt.UserRole),
                #"adjust": str(self.modelAdjust)
               #}

    #def updatePackage(self, elemID):
        #self.sql.updatePackage(elemID, self.readFormData())
        ##self.reloadList()
        
    #def addPackageAsNew(self):
        #''' add package as new - based on other package '''
        #if str(self.packageName.text()).strip() == "" or str(self.pathToModel.text()).strip() == "":
            #QtGui.QMessageBox().critical(self, u"Caution!", u"At least one required field is empty.")
            #return

        #zawiera = self.sql.has_value("name", self.packageName.text())
        #if zawiera[0]:
            #dial = QtGui.QMessageBox(self)
            #dial.setText(u"Rejected. Package already exist.")
            #dial.setWindowTitle("Caution!")
            #dial.setIcon(QtGui.QMessageBox.Warning)
            #dial.addButton('Ok', QtGui.QMessageBox.RejectRole)
            #dial.exec_()
        #else:
            #self.addElement()
    
    #def addNewPackage(self):
        #''' add package to lib '''
        #if str(self.packageName.text()).strip() == "" or str(self.pathToModel.text()).strip() == "":
            #QtGui.QMessageBox().critical(self, u"Caution!", u"At least one required field is empty.")
            #return

        #zawiera = self.sql.has_value("name", self.packageName.text())
        #if not self.elementID and zawiera[0]:  # aktualizacja niezaznaczonego obiektu
            #dial = QtGui.QMessageBox(self)
            #dial.setText(u"Package already exist. Rewrite?")
            #dial.setWindowTitle("Caution!")
            #dial.setIcon(QtGui.QMessageBox.Question)
            #rewN = dial.addButton('No', QtGui.QMessageBox.RejectRole)
            #rewT = dial.addButton('Yes', QtGui.QMessageBox.YesRole)
            #dial.exec_()
                
            #if dial.clickedButton() == rewN:
                #return
            #else:
                #self.updatePackage(zawiera[1])
                #return
        #elif self.elementID:  # aktualizacja zaznaczonego obiektu
            #dial = QtGui.QMessageBox(self)
            #dial.setText(u"Save changes?")
            #dial.setWindowTitle("Caution!")
            #dial.setIcon(QtGui.QMessageBox.Question)
            #rewN = dial.addButton('No', QtGui.QMessageBox.RejectRole)
            #dial.addButton('Yes', QtGui.QMessageBox.YesRole)
            #dial.exec_()
                
            #if dial.clickedButton() == rewN:
                #return
            #else:
                ##zawiera = self.sql.has_value("name", self.nazwaEagle.text())
                #if zawiera[0] and zawiera[1] != self.elementID:
                    #dial = QtGui.QMessageBox(self)
                    #dial.setText(u"Rejected. Package already exist.")
                    #dial.setWindowTitle("Caution!")
                    #dial.setIcon(QtGui.QMessageBox.Warning)
                    #dial.addButton('Ok', QtGui.QMessageBox.RejectRole)
                    #dial.exec_()
                #else:
                    #if not self.sql.has_section(self.elementID):
                        #self.addElement()
                    #else:
                        #self.updatePackage(self.elementID)
                #return
        #else:  # dodanie nowego obiektu
            #self.addElement()
    
    #def addElement(self):
        #''' add package info to lib '''
        #self.sql.addPackage(self.readFormData())
        #self.reloadList()
        
    #def convertDatabase(self):
        #sciezka = os.path.dirname(getFromSettings_databasePath())
        #if os.access(sciezka, os.R_OK) and os.access(sciezka, os.F_OK):
            #if not os.path.isfile(getFromSettings_databasePath()):
                #self.sql.create(getFromSettings_databasePath())
                ## convert old database to new format
                #exportData = {}
                #try:
                    #FreeCAD.Console.PrintWarning("Convert old database to new format\n")
                    #for i in supSoftware.keys():
                        #data = dataBase()
                        #data.read(supSoftware[i]['pathToBase'])
                        
                        #for j in data.packages():
                            #package = data.getValues(j)
                            
                            #if not package['path'] in exportData.keys():
                                #exportData[package['path']] = {}
                                #exportData[package['path']]['name'] = u"{0}".format(package["name"])
                                #exportData[package['path']]['description'] = u"{0}".format(package["description"])
                                #exportData[package['path']]['datasheet'] = u"{0}".format(package["datasheet"])
                                #exportData[package['path']]['add_socket'] = str([False, None])
                                #exportData[package['path']]['socket'] = str([bool(int(package["socket"])), float(package["socket_height"])])
                                
                                #exportData[package['path']]['soft'] = []
                                #exportData[package['path']]['soft'].append([u'{0}'.format(package["name"]), supSoftware[i]['name'], float(package["x"]), float(package["y"]), float(package["z"]), float(package["rx"]), float(package["ry"]), float(package["rz"])])
                            #else:
                                #exportData[package['path']]['soft'].append([u'{0}'.format(package["name"]), supSoftware[i]['name'], float(package["x"]), float(package["y"]), float(package["z"]), float(package["rx"]), float(package["ry"]), float(package["rz"])])
                                
                                #if package["description"].strip() != '' and exportData[package['path']]['description'] == '':
                                    #exportData[package['path']]['description'] = u"{0}".format(package["description"])
                                #if package["datasheet"].strip() != '' and exportData[package['path']]['datasheet'] == '':
                                    #exportData[package['path']]['datasheet'] = u"{0}".format(package["datasheet"])
                    
                    #for i, j in exportData.items():
                        ##FreeCAD.Console.PrintWarning("{0} - {1} \n\n".format(i, j))
                        #j["path"] = i
                        #j['soft'] = str(j['soft'])
                        #self.sql.addPackage(j)
                #except Exception as e:
                    #FreeCAD.Console.PrintWarning(u"Error 5: {0} \n".format(e))
            ##
            #FreeCAD.Console.PrintWarning("Read database\n")
            #self.sql.read(getFromSettings_databasePath())
        #else:
            #FreeCAD.Console.PrintWarning("No access\n")
            
    #def reloadCategoryList(self):
        #self.modelCategory.clear()
        ##
        #self.modelCategory.addItem("None")
        #self.modelCategory.setItemData(self.modelCategory.count() - 1, -1, QtCore.Qt.UserRole)
        #for i, j in readCategories().items():
            #self.modelCategory.addItem("{0}".format(j[0]))
            #self.modelCategory.setItemData(self.modelCategory.count() - 1, i, QtCore.Qt.UserRole)
            
    #def reloadSockets(self):
        #try:
            #self.modelsList.reloadSockets()
            #self.socketModelName.clear()
            
            #for i in self.modelsList.Sockets:
                #self.socketModelName.addItem(i[0])
                #self.socketModelName.setItemData(self.socketModelName.count() - 1, i[1], QtCore.Qt.UserRole)
        #except:
            #pass

    #def reloadList(self):
        #''' reload list of packages from current lib '''
        #self.editCategory.setDisabled(True)
        #self.removeCategory.setDisabled(True)
        
        #try:
            #self.convertDatabase()
            #self.modelsList.reloadList()
            #self.reloadSockets()
            #self.reloadCategoryList()
            ###
            #self.clearData()
        #except Exception as e:
            #FreeCAD.Console.PrintWarning(u"Error 6: {0} \n".format(e))
    
    #def loadData(self, item):
        #self.RightSide_tab.setCurrentIndex(0)
        
        #if str(self.modelsList.currentItem().data(0, QtCore.Qt.UserRole + 1)) == 'C':
            #self.clearData()
            #self.editCategory.setDisabled(False)
            #self.removeCategory.setDisabled(False)
        #else:
            #self.editCategory.setDisabled(True)
            #self.removeCategory.setDisabled(True)
            ##
            #elemID = str(self.modelsList.currentItem().data(0, QtCore.Qt.UserRole))

            #dane = self.sql.getValues(elemID)
            #dane["id"] = elemID
            
            #self.showData(dane)
        
    #def showData(self, dane):
        #''' load package info to form '''
        #self.modelSettings.clear()
        ##
        #self.elementID = dane["id"]
        
        #self.packageName.setText(dane["name"])
        #self.pathToModel.setText(dane["path"])
        #self.modelDescription.setPlainText(dane["description"])
        #self.datasheetPath.setText(dane["datasheet"])
        
        #try:
            #self.modelCategory.setCurrentIndex(self.modelCategory.findData(dane["category"]))
        #except:
            #self.modelCategory.setCurrentIndex(self.modelCategory.findData(-1))
        
        #self.reloadSockets()
        #self.socketModelName.removeItem(self.socketModelName.findData(self.elementID))
        #add_socket = eval(dane["add_socket"])
        #if self.socketModelName.findData(add_socket[1]) != -1:
            #self.boxAddSocket.setChecked(add_socket[0])
            #self.socketModelName.setCurrentIndex(self.socketModelName.findData(add_socket[1]))
        #else:
            #self.boxAddSocket.setChecked(QtCore.Qt.Unchecked)
        
        #socket = eval(dane["socket"])
        #self.boxSetAsSocketa.setChecked(int(socket[0]))
        #self.socketHeight.setValue(socket[1])
        
        #try:
            #for i, j in eval(dane["adjust"]).items():
                #self.modelAdjust.updateType(i, j)
        #except:
            #self.modelAdjust.resetTable()
        
        #soft = eval(dane["soft"])
        #for i in soft:
            #try:
                #self.modelSettings.addRow(i)
            #except Exception as e:
                #FreeCAD.Console.PrintWarning("{0} \n".format(e))

    #def wyszukajObiektyNext(self):
        #''' find next object '''
        #try:
            #if len(self.szukaneFrazy):
                #if self.szukaneFrazyNr <= len(self.szukaneFrazy) - 2:
                    #self.szukaneFrazyNr += 1
                #else:
                    #self.szukaneFrazyNr = 0
                #self.modelsList.setCurrentItem(self.szukaneFrazy[self.szukaneFrazyNr])
        #except RuntimeError:
            #self.szukaneFrazy = []
            #self.szukaneFrazyNr = 0
    
    #def wyszukajObiektyPrev(self):
        #''' find prev object '''
        #try:
            #if len(self.szukaneFrazy):
                #if self.szukaneFrazyNr >= 1:
                    #self.szukaneFrazyNr -= 1
                #else:
                    #self.szukaneFrazyNr = len(self.szukaneFrazy) - 1
                #self.modelsList.setCurrentItem(self.szukaneFrazy[self.szukaneFrazyNr])
        #except RuntimeError:
            #self.szukaneFrazy = []
            #self.szukaneFrazyNr = 0
        
    #def wyszukajObiekty(self, fraza):
        #''' find object in current document '''
        #fraza = str(fraza).strip()
        #if fraza != "":
            #self.szukaneFrazy = self.modelsList.findItems(fraza, QtCore.Qt.MatchRecursive | QtCore.Qt.MatchStartsWith)
            #if len(self.szukaneFrazy):
                #self.modelsList.setCurrentItem(self.szukaneFrazy[0])
                #self.szukaneFrazyNr = 0
