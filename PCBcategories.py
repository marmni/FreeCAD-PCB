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
from functools import partial

__freecadSettings__ = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB")

#***********************************************************************
#*                             GUI
#***********************************************************************

class submenuCategorySelector(QtGui.QMenu):
    def __init__(self, title, categoryID, parent, button):
        QtGui.QMenu.__init__(self, parent)
        #
        self.setTitle(title)
        self.button = button
        self.categoryID = categoryID
    
    def mousePressEvent(self, event):
        try:
            self.button.showMenuF(self.title(), self.categoryID)
        except Exception as e:
            pass
        
        return QtGui.QMenu.mousePressEvent(self, event)


class categorySelector(QtGui.QPushButton):
    def __init__(self, parent=None):
        QtGui.QPushButton.__init__(self, parent)
        #
        self.reset()
    
    def setData(self, categoryID, text):
        if categoryID == 0:
            self.reset()
        else:
            self.categoryID = categoryID
            self.setText(text)
    
    def reset(self):
        self.setText("None")
        self.categoryID = 0
    
    def addNewSubmenu(self, category, parent):
        if len(category[1]['sub'].items()):
            menu = submenuCategorySelector(category[0], category[1]['id'], parent, self)
            parent.addMenu(menu)
            #
            action = menu.addAction(category[0])
            action.triggered.connect(partial(self.showMenuF, category[0], category[1]['id']))
            menu.addSeparator()
            #
            for i in sorted(category[1]['sub'].items()):
                self.addNewSubmenu(i, menu)
        else:
            action = parent.addAction(category[0])
            action.triggered.connect(partial(self.showMenuF, category[0], category[1]['id']))
        
    def setMenuF(self, data):
        #
        mainMenu = QtGui.QMenu(self)
        action = mainMenu.addAction("None")
        action.triggered.connect(partial(self.showMenuF, "None", 0))
        
        mainMenu.addSeparator()
        #
        for i in sorted(data):
            self.addNewSubmenu(i, mainMenu)
        #
        self.setMenu(mainMenu)
        
    def showMenuF(self, value, categoryID):
        self.setText(value)
        self.categoryID = categoryID
        #self.menu().setVisible(False)


class setOneCategoryGui(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u'Set one category for all selected models')
        #
        self.parentCategory = categorySelector()
        # buttons
        buttons = QtGui.QDialogButtonBox()
        buttons.setOrientation(QtCore.Qt.Horizontal)
        buttons.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
        buttons.addButton("Set", QtGui.QDialogButtonBox.AcceptRole)
        self.connect(buttons, QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        self.connect(buttons, QtCore.SIGNAL("rejected()"), self, QtCore.SLOT("reject()"))
        #
        lay = QtGui.QGridLayout(self)
        lay.addWidget(QtGui.QLabel(u'New category'), 0, 0, 1, 1)
        lay.addWidget(self.parentCategory, 0, 1, 1, 1)
        lay.setSpacing(10)
        lay.addWidget(buttons, 1, 0, 1, 2, QtCore.Qt.AlignRight)
        lay.setRowStretch(0, 10)
        lay.setColumnStretch(1, 10)
    
    def loadCategories(self, categories):
        self.parentCategory.setMenuF(categories)


class addCategoryGui(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u'Add new category')
        #
        self.categoryName = QtGui.QLineEdit('')
        self.categoryName.setStyleSheet('background-color:#FFF;')
        
        self.parentCategory = categorySelector()
        
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
        lay.addWidget(QtGui.QLabel(u'Name*'), 0, 0, 1, 1)
        lay.addWidget(self.categoryName, 0, 1, 1, 1)
        lay.addWidget(QtGui.QLabel(u'Parent category'), 1, 0, 1, 1)
        lay.addWidget(self.parentCategory, 1, 1, 1, 1)
        lay.addWidget(QtGui.QLabel(u'Desctiption'), 2, 0, 1, 1, QtCore.Qt.AlignTop)
        lay.addWidget(self.categoryDescription, 2, 1, 1, 1)
        lay.addWidget(buttons, 0, 2, 2, 1, QtCore.Qt.AlignCenter)
        lay.setRowStretch(2, 10)
    
    def loadCategories(self, categories, parentID, parentName):
        self.parentCategory.setMenuF(categories)
        
        if parentID >= 1:
            self.parentCategory.setData(parentID, parentName)
        else:
            self.parentCategory.setData(0, '')

class removeCategoryGui(QtGui.QMessageBox):
    def __init__(self, categoryName, parent=None):
        QtGui.QMessageBox.__init__(self, parent)
        
        self.setText(u"Delete selected category '{0}'?".format(categoryName))
        self.setWindowTitle("Caution!")
        self.setIcon(QtGui.QMessageBox.Question)
        self.delete = self.addButton('Yes', QtGui.QMessageBox.AcceptRole)
        self.addButton('No', QtGui.QMessageBox.RejectRole)


class updateCategoryGui(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u'Update category')
        #
        self.categoryName = QtGui.QLineEdit('')
        self.categoryName.setStyleSheet('background-color:#FFF;')
        #self.categoryName.setText()
        
        self.parentCategory = categorySelector()
        
        self.categoryDescription = QtGui.QTextEdit('')
        #self.categoryDescription.setText()
        # buttons
        buttons = QtGui.QDialogButtonBox()
        buttons.setOrientation(QtCore.Qt.Vertical)
        buttons.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
        buttons.addButton("Update", QtGui.QDialogButtonBox.AcceptRole)
        self.connect(buttons, QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        self.connect(buttons, QtCore.SIGNAL("rejected()"), self, QtCore.SLOT("reject()"))
        #
        lay = QtGui.QGridLayout(self)
        lay.addWidget(QtGui.QLabel(u'Name*'), 0, 0, 1, 1)
        lay.addWidget(self.categoryName, 0, 1, 1, 1)
        lay.addWidget(QtGui.QLabel(u'Parent category'), 1, 0, 1, 1)
        lay.addWidget(self.parentCategory, 1, 1, 1, 1)
        lay.addWidget(QtGui.QLabel(u'Desctiption'), 2, 0, 1, 1, QtCore.Qt.AlignTop)
        lay.addWidget(self.categoryDescription, 2, 1, 1, 1)
        lay.addWidget(buttons, 0, 2, 2, 1, QtCore.Qt.AlignCenter)
        lay.setRowStretch(2, 10)
    
    def loadCategories(self, categories, parentID, parentName):
        self.parentCategory.setMenuF(categories)
        
        if parentID >= 1:
            self.parentCategory.setData(parentID, parentName)
        else:
            self.parentCategory.setData(0, '')

#***********************************************************************
#*                             CONSOLE
#***********************************************************************
