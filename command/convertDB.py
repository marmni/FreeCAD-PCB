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

import os
import sys
try:
    from PyQt4 import QtCore, QtGui
except:
    from PySide import QtCore, QtGui
import FreeCAD
#
from dataBase import dataBase


__currentPath__ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class convertDB(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("Convert old database to a new format")
        self.setMinimumWidth(500)
        # stary plik z modelami
        self.oldFilePath = QtGui.QLineEdit(os.path.join(__currentPath__, "param.py"))
        # nowy plik z modelami
        self.newFilePath = QtGui.QLineEdit(os.path.join(__currentPath__, "data/dane.cfg"))
        #
        self.pominDuplikaty = QtGui.QCheckBox(u"Skip duplicates")
        self.pominDuplikaty.setChecked(True)
        self.pominDuplikaty.setDisabled(True)
        #
        self.removeOld = QtGui.QCheckBox(u"Remove old database")
        self.removeOld.setChecked(True)
        # przyciski
        buttons = QtGui.QDialogButtonBox()
        buttons.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
        buttons.addButton("Convert", QtGui.QDialogButtonBox.AcceptRole)
        self.connect(buttons, QtCore.SIGNAL("accepted()"), self.konwertuj)
        self.connect(buttons, QtCore.SIGNAL("rejected()"), self, QtCore.SLOT("reject()"))
        #
        self.mainLayout = QtGui.QGridLayout(self)
        #self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addWidget(QtGui.QLabel(u"Old database"), 0, 0, 1, 1)
        self.mainLayout.addWidget(self.oldFilePath, 0, 1, 1, 1)
        self.mainLayout.addWidget(QtGui.QLabel(u"New database"), 1, 0, 1, 1)
        self.mainLayout.addWidget(self.newFilePath, 1, 1, 1, 1)
        
        self.mainLayout.addWidget(self.pominDuplikaty, 3, 0, 1, 2)
        self.mainLayout.addWidget(self.removeOld, 4, 0, 1, 2)
        self.mainLayout.addWidget(buttons, 5, 1, 1, 1, QtCore.Qt.AlignRight)
        self.mainLayout.setRowStretch(6, 10)
        
    def sprawdzPliki(self, fileName):
        if os.path.exists(fileName) and os.path.isfile(fileName):
            return True
        
        FreeCAD.Console.PrintWarning("Plik '{0}' nie istnieje bądź brak wymagających praw do odczytu/zapisu.\n".format(fileName))
        return False
        
    def konwertuj(self):
        if self.sprawdzPliki(str(self.oldFilePath.text())) and self.sprawdzPliki(str(self.newFilePath.text())):
            # baza danych
            sql = dataBase()
            sql.read(str(self.newFilePath.text()))
            # stara baza danych
            oldPath = os.path.dirname(str(self.oldFilePath.text()))
            oldName = os.path.basename(str(self.oldFilePath.text()))
            
            sys.path.append(oldPath)
            oldModule = __import__(os.path.splitext(oldName)[0])
            #
            for i, j in oldModule.bibliotekaDane.items():
                param = sql.has_value("name", i)
                if not param[0]:
                    sql.addPackage({"name": i,
                                    "path": j[0],
                                    "x": str(j[1]),
                                    "y": str(j[2]),
                                    "z": str(j[3]),
                                    "rx": str(j[4]),
                                    "ry": str(j[5]),
                                    "rz": str(j[6]),
                                    "add_socket": 0,
                                    "add_socket_id": 0,
                                    "socket": str(j[7]),
                                    "socket_height": str(j[8]),
                                    "description": "",
                                    "datasheet": ""})
            try:
                if self.removeOld.isChecked():
                    os.remove(str(self.oldFilePath.text()))
            except OSError:
                pass
            QtGui.QMessageBox().information(self, u"Conversion", u"Conversion finished.")
            self.reject()
