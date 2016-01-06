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
if FreeCAD.GuiUp:
    from PySide import QtGui, QtCore
import json
try:
    from PCBconf import modelsCategories
except:
    modelsCategories = {}

__freecadSettings__ = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB")

#***********************************************************************
#*                             GUI
#***********************************************************************
class addCategoryGui(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u'Add new category')
        #
        self.categoryName = QtGui.QLineEdit('')
        self.categoryName.setStyleSheet('background-color:#FFF;')
        
        self.categoryDescription = QtGui.QTextEdit('')
        # buttons
        buttons = QtGui.QDialogButtonBox()
        buttons.setOrientation(QtCore.Qt.Vertical)
        buttons.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
        buttons.addButton("Add", QtGui.QDialogButtonBox.AcceptRole)
        self.connect(buttons, QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        self.connect(buttons, QtCore.SIGNAL("rejected()"), self, QtCore.SLOT("reject()"))
        #
        lay = QtGui.QGridLayout(self)
        lay.addWidget(QtGui.QLabel(u'Name'), 0, 0, 1, 1)
        lay.addWidget(self.categoryName, 0, 1, 1, 1)
        lay.addWidget(QtGui.QLabel(u'Desctiption'), 1, 0, 1, 1, QtCore.Qt.AlignTop)
        lay.addWidget(self.categoryDescription, 1, 1, 1, 1)
        lay.addWidget(buttons, 0, 2, 2, 1, QtCore.Qt.AlignCenter)
        lay.setRowStretch(1, 10)
        
    def addCategory(self):
        addCategory(self.categoryName.text(), self.categoryDescription.toPlainText())


class removeCategoryGui:
    def __init__(self, categoryID):
        categoryData = readCategories()[categoryID]
        #
        dial = QtGui.QMessageBox()
        dial.setText(u"Delete selected category '{0}'?".format(categoryData[0]))
        dial.setWindowTitle("Caution!")
        dial.setIcon(QtGui.QMessageBox.Question)
        delete = dial.addButton('Yes', QtGui.QMessageBox.AcceptRole)
        dial.addButton('No', QtGui.QMessageBox.RejectRole)
        dial.exec_()
        
        if dial.clickedButton() == delete:
            removeCategory(categoryID)


class updateCategoryGui(QtGui.QDialog):
    def __init__(self, categoryID, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u'Update category')
        
        self.categoryID = categoryID
        categoryData = readCategories()[self.categoryID]
        #
        self.categoryName = QtGui.QLineEdit('')
        self.categoryName.setStyleSheet('background-color:#FFF;')
        self.categoryName.setText(categoryData[0])
        
        self.categoryDescription = QtGui.QTextEdit('')
        self.categoryDescription.setText(categoryData[1])
        # buttons
        buttons = QtGui.QDialogButtonBox()
        buttons.setOrientation(QtCore.Qt.Vertical)
        buttons.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
        buttons.addButton("Update", QtGui.QDialogButtonBox.AcceptRole)
        self.connect(buttons, QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        self.connect(buttons, QtCore.SIGNAL("rejected()"), self, QtCore.SLOT("reject()"))
        #
        lay = QtGui.QGridLayout(self)
        lay.addWidget(QtGui.QLabel(u'Name'), 0, 0, 1, 1)
        lay.addWidget(self.categoryName, 0, 1, 1, 1)
        lay.addWidget(QtGui.QLabel(u'Desctiption'), 1, 0, 1, 1, QtCore.Qt.AlignTop)
        lay.addWidget(self.categoryDescription, 1, 1, 1, 1)
        lay.addWidget(buttons, 0, 2, 2, 1, QtCore.Qt.AlignCenter)
        lay.setRowStretch(1, 10)
        
    def updateCategory(self):
        updateCategory(self.categoryID, [self.categoryName.text(), self.categoryDescription.toPlainText()])

#***********************************************************************
#*                             CONSOLE
#***********************************************************************
def readCategories():
    if __freecadSettings__.GetString("partsCategories", '') == '':
        freecadAddParam()
    #
    return {int(i):j for i, j in json.loads(__freecadSettings__.GetString("partsCategories", '')).items()}
    
def writeCategories(data):
    __freecadSettings__.SetString('partsCategories', json.dumps(data))

def freecadAddParam():
    writeCategories(modelsCategories)
    
def removeCategory(ID):
    categories = readCategories()
    try:
        if int(ID) in categories.keys():
            del categories[ID]
            writeCategories(categories)
    except:
        pass
        
def getCategoryIdByName(categoryName):
    modelCategory = -1
    for j,k in readCategories().items():
        if k[0] == categoryName:
            modelCategory = int(j)
            break
            
    return modelCategory
    
def updateCategory(ID, data):
    '''
        data = [Name, Description]
    '''
    categories = readCategories()
    try:
        categories[ID] = data
        writeCategories(categories)
    except:
        pass

def addCategory(name, description):
    try:
        updateCategory(newID(), [name, description])
    except:
        pass
        
    return 

def newID():
    return max(readCategories().keys()) + 1

def readFromXML(data):
    pass
