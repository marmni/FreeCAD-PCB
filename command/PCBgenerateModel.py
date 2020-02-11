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
import FreeCAD, FreeCADGui
if FreeCAD.GuiUp:
    from PySide import QtGui, QtCore
import glob
import os
import sys
import importlib
from functools import partial


class generateModelGui(QtGui.QStackedWidget):
    def __init__(self, parent=None):
        QtGui.QStackedWidget.__init__(self, parent)
        
        self.form = self
        self.form.setWindowTitle(u"Generate model")
        self.form.setWindowIcon(QtGui.QIcon(":/data/img/generateModel.svg"))
        self.moduleName = None
        #
        self.filesDirecory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..\generateModels")
        sys.path.append(self.filesDirecory)
        #
        self.addWidget(self.firstPage())
    
    def accept(self):
        if self.currentIndex() > 0:
            try:
                if self.currentWidget().errors:
                    print("Fix all errors!")
                    return False
                #
                fcstdFile = importlib.import_module(self.moduleName).__fcstdFile__
                doc = FreeCAD.open(os.path.join(self.filesDirecory, "data/" + fcstdFile))
                
                FreeCAD.ActiveDocument = FreeCAD.getDocument(doc.Label)
                FreeCAD.ActiveDocument = FreeCAD.getDocument(doc.Label)
                FreeCADGui.ActiveDocument = FreeCADGui.getDocument(doc.Label)
                FreeCADGui.activeDocument().activeView().viewIsometric()
                
                importlib.import_module(self.moduleName).modelGenerate(doc, self.currentWidget())
            except Exception as e:
                print(e)
        #
        return True
    
    def showMainWidget(self):
        # self.form.setWindowTitle(u"Generate model")
        self.setCurrentIndex(0)
        
    def firstPage(self):
        mainWidget = QtGui.QWidget()
        mainLay = QtGui.QGridLayout(mainWidget)
        row = 0
        col = 0
        num = 0
        #
        for i in glob.glob(os.path.join(self.filesDirecory, "PCBcreate*.py")):
            try:
                moduleName = os.path.splitext(os.path.basename(i))[0]
                i = importlib.import_module(moduleName)
                #
                newButton = i.modelPreview(self)
                self.connect(newButton, QtCore.SIGNAL("clicked ()"), partial(self.getGeneratorUI, moduleName))
                
                mainLay.addWidget(newButton, row, col, 1, 1)
                #
                num += 1
                if num % 2 == 0:
                    row += 1
                
                if col == 1:
                    col = 0
                else:
                    col += 1
            except Exception as e:
                print(e)
        #
        return mainWidget
    
    def getGeneratorUI(self, moduleName):
        if self.count() > 1:
            self.removeWidget(self.widget(1))
            self.moduleName = None
        #
        # self.form.setWindowTitle(u"Generate model: " + importlib.import_module(moduleName).__desc__)
        modelGenerate = importlib.import_module(moduleName).modelGenerateGUI(self)
        self.moduleName = moduleName
        self.addWidget(modelGenerate)
        self.setCurrentIndex(1)
