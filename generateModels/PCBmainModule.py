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
from PySide import QtCore, QtGui
import os


class modelPreviewMain(QtGui.QToolButton):
    def __init__(self, icon, tooltip, parent=None):
        iconDirectory = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..\generateModels\data"), icon)
        #
        QtGui.QToolButton.__init__(self, parent)
        #
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        self.setToolTip(tooltip)
        self.setAutoFillBackground(True)
        self.setIcon(QtGui.QIcon(iconDirectory))  # 100x100px
        self.setText(tooltip)
        self.setStyleSheet("QToolButton {background-color: #b2babb; color: #FFFFFF; font-weight: bold; font-size: 10px;} QToolButton:hover:!pressed{border: 1px solid #808080; background-color: #e6e6e6; color: #000000} ")
        self.setIconSize(QtCore.QSize(120, 120))
        self.setFixedSize(QtCore.QSize(128, 128))


class modelGenerateGUIMain(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        #
        showMainWidget = flatButton(":/data/img/previous_16x16.png", "Back", self)
        self.connect(showMainWidget, QtCore.SIGNAL("clicked ()"), parent.showMainWidget)
        #
        line = QtGui.QFrame()
        line.setFrameShape(QtGui.QFrame.HLine)
        line.setFrameShadow(QtGui.QFrame.Sunken)
        #
        self.mainFormLay = QtGui.QFormLayout()
        #
        self.mainLayout = QtGui.QGridLayout(self)
        self.mainLayout.addWidget(showMainWidget, 0, 0, 1, 1)
        self.mainLayout.addWidget(line, 1, 0, 1, 6)
        # ICON
        self.mainLayout.addItem(QtGui.QSpacerItem(1, 15), 3, 0, 1, 1)
        self.mainLayout.addLayout(self.mainFormLay, 4, 0, 1, 6)
        self.mainLayout.setRowStretch(100, 100)
        self.mainLayout.setColumnStretch(5, 100)
        
    def addMainImageDim(self, icon):
        modelDim = modelPictureDim(icon, self)
        self.mainLayout.addWidget(modelDim, 2, 0, 1, 6, QtCore.Qt.AlignHCenter 	)


class modelPictureDim(QtGui.QLabel):
     def __init__(self, icon, parent=None):
        QtGui.QLabel.__init__(self, "")
        #
        iconDirectory = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..\generateModels\data"), icon)
        #
        img = QtGui.QPixmap(iconDirectory)
        #
        self.setPixmap(img)

class flatButton(QtGui.QPushButton):
    def __init__(self, icon, tooltip, parent=None):
        QtGui.QPushButton.__init__(self, QtGui.QIcon(icon), "", parent)
        #
        self.setToolTip(tooltip)
        self.setFlat(True)
        self.setStyleSheet("QPushButton:hover:!pressed{border: 1px solid #808080;} ")
        self.setIconSize(QtCore.QSize(32, 32))
        self.setFixedSize(QtCore.QSize(32, 32))

# class modelPreviewMain(QtGui.QWidget):
    # def __init__(self, icon, tooltip, parent=None):
        # QtGui.QWidget.__init__(self, parent)
        
        # self.setFixedSize(QtCore.QSize(128, 128))
        # self.setAutoFillBackground(True)
        # self.setStyleSheet("background-color: #434e52; border:0px solid red")
        
        # p = self.palette()
        # p.setColor(self.backgroundRole(), QtGui.QColor(209, 209, 209))
        # self.setPalette(p)
        # #
        # iconDirectory = os.path.join(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..\generateModels\data"), icon)
        # #
        # self.button = QtGui.QPushButton(QtGui.QIcon(iconDirectory), "", self)
        # self.button.setFlat(True)
        # self.button.setIconSize(QtCore.QSize(120, 120))
        # #self.button.setStyleSheet("QPushButton:hover:!pressed{border: 1px solid #808080; background-color: #e6e6e6;} ")
        # #
        # desc = QtGui.QLabel(tooltip)
        # #
        # self.mainLay = QtGui.QGridLayout(self)
        # self.mainLay.addWidget(self.button, 0, 0, 1, 1)
        # self.mainLay.addWidget(desc, 1, 0, 1, 1, QtCore.Qt.AlignHCenter)
        # self.mainLay.setContentsMargins(5, 5, 5, 5)
        # self.mainLay.setSpacing(0)
        
    
