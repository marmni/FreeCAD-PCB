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

import FreeCAD
import Part
import unicodedata
if FreeCAD.GuiUp:
    #import FreeCADGui
    from PySide import QtCore, QtGui
#
from PCBconf import *
from PCBobjects import partObject, viewProviderPartObject, partObject_E, viewProviderPartObject_E
from PCBpartManaging import partsManaging
from PCBboard import getPCBheight
from command.PCBannotations import createAnnotation


class updateObjectTable(QtGui.QListWidget):
    def __init__(self, parent=None):
        QtGui.QListWidget.__init__(self, parent)
        
        self.setFrameShape(QtGui.QFrame.NoFrame)
    
    def DeSelectAllObj(self, value):
        for i in range(self.count()):
            self.item(i).setCheckState(value)


class updateWizardWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
        freecadSettings = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB")
        #
        self.listaBibliotek = QtGui.QComboBox()
        
        libraryFrame = QtGui.QGroupBox(u'Library:')
        libraryFrameLay = QtGui.QHBoxLayout(libraryFrame)
        libraryFrameLay.addWidget(self.listaBibliotek)
        #
        self.listaElementow = updateObjectTable()

        przSelectAllT = QtGui.QPushButton('')
        #przSelectAllT.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        przSelectAllT.setFlat(True)
        przSelectAllT.setIcon(QtGui.QIcon(":/data/img/checkbox_checked_16x16.png"))
        przSelectAllT.setToolTip('Select all')
        self.connect(przSelectAllT, QtCore.SIGNAL('pressed ()'), self.selectAllObj)
        
        przSelectAllTF = QtGui.QPushButton('')
        #przSelectAllTF.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        przSelectAllTF.setFlat(True)
        przSelectAllTF.setIcon(QtGui.QIcon(":/data/img/checkbox_unchecked_16x16.png"))
        przSelectAllTF.setToolTip('Deselect all')
        self.connect(przSelectAllTF, QtCore.SIGNAL('pressed ()'), self.unselectAllObj)
        
        self.adjustParts = QtGui.QCheckBox(u'Adjust part name/value')
        self.adjustParts.setChecked(freecadSettings.GetBool("adjustNameValue", False))
        
        self.groupParts = QtGui.QCheckBox(u'Group parts')
        self.groupParts.setChecked(freecadSettings.GetBool("groupParts", False))
        
        self.plytkaPCB_elementyKolory = QtGui.QCheckBox(u"Colorize elements")
        self.plytkaPCB_elementyKolory.setChecked(freecadSettings.GetBool("partsColorize", True))
        
        packagesFrame = QtGui.QGroupBox(u'Packages:')
        packagesFrameLay = QtGui.QGridLayout(packagesFrame)
        packagesFrameLay.addWidget(przSelectAllT, 0, 0, 1, 1)
        packagesFrameLay.addWidget(przSelectAllTF, 1, 0, 1, 1)
        packagesFrameLay.addWidget(self.listaElementow, 0, 1, 3, 1)
        #
        lay = QtGui.QVBoxLayout()
        lay.addWidget(libraryFrame)
        lay.addWidget(packagesFrame)
        lay.addWidget(self.adjustParts)
        lay.addWidget(self.groupParts)
        lay.addWidget(self.plytkaPCB_elementyKolory)
        lay.setStretch(1, 10)
        self.setLayout(lay)
        #
        self.readLibs()

    def selectAllObj(self):
        ''' select all object on list '''
        self.listaElementow.DeSelectAllObj(QtCore.Qt.Checked)
    
    def unselectAllObj(self):
        ''' deselect all object on list '''
        self.listaElementow.DeSelectAllObj(QtCore.Qt.Unchecked)
    
    def readLibs(self):
        ''' read all available libs from conf file '''
        for i in defSoftware:
            self.listaBibliotek.addItem(i)
            self.listaBibliotek.setItemData(self.listaBibliotek.count() - 1, i.lower(), QtCore.Qt.UserRole)
        
        freecadSettings = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB")
        self.listaBibliotek.setCurrentIndex(self.listaBibliotek.findText(defSoftware[freecadSettings.GetInt("pcbDefaultSoftware", 0)]))


class updateParts(partsManaging):
    ''' update 3d models of packages '''
    def __init__(self, parent=None, updateModel=None):
        partsManaging.__init__(self)
        self.form = updateWizardWidget()
        self.form.setWindowTitle('Update model')
        self.form.setWindowIcon(QtGui.QIcon(":/data/img/assignModels.png"))
        self.updateModel = updateModel
        
        self.setDatabase()
        self.listOfModels = {}
    
    def open(self):
        ''' load all packages types to list '''
        pcb = getPCBheight()
        if pcb[0]:  # board is available
            for j in pcb[2].Group:
                if hasattr(j, "Proxy") and hasattr(j.Proxy, "Type") and j.Proxy.Type in ["PCBpart", "PCBpart_E"]:
                    if not j.Package in self.listOfModels.keys():
                        self.listOfModels[j.Package] = []
                        ####
                        a = QtGui.QListWidgetItem(j.Package)
                        #a.setData(QtCore.Qt.UserRole, j.Package)
                        a.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
                        
                        try:
                            a.setIcon(j.ViewObject.Icon)
                        except AttributeError:
                            pass
                        
                        if self.updateModel:
                            if self.updateModel == j.Package:
                                a.setCheckState(QtCore.Qt.Checked)
                            else:
                                a.setCheckState(QtCore.Qt.Unchecked)
                        else:
                            a.setCheckState(QtCore.Qt.Checked)
                        
                        self.form.listaElementow.addItem(a)
                    ####
                    self.listOfModels[j.Package].append(j)

    def reject(self):
        return True
    
    def needsFullSpace(self):
        return True

    def isAllowedAlterSelection(self):
        return False

    def isAllowedAlterView(self):
        return True

    def isAllowedAlterDocument(self):
        return False

    def helpRequested(self):
        pass

    def accept(self):
        ''' update 3d models '''
        if FreeCAD.activeDocument():
            self.databaseType = self.form.listaBibliotek.itemData(self.form.listaBibliotek.currentIndex(), QtCore.Qt.UserRole)
            koloroweElemnty = self.form.plytkaPCB_elementyKolory.isChecked()
            adjustParts = self.form.adjustParts.isChecked()
            groupParts = self.form.groupParts.isChecked()
            pcb = getPCBheight()
            ####
            for j in range(self.form.listaElementow.count()):
                if self.form.listaElementow.item(j).checkState() == 2:
                    package = self.form.listaElementow.item(j).text()
                    
                    fileData = self.partExist({'package': package,'pathAttribute': "","partNameTXT": "", 'value': ""})
                    ####
                    for i in self.listOfModels[package]:
                        if i.Proxy.Type == "PCBpart" and fileData[0]:
                            if fileData[2]['modelID'] > 0:
                                modelData = self.__SQL__.getModelByID(fileData[2]['modelID'])
                                
                                if modelData[0]:
                                    modelData = self.__SQL__.convertToTable(modelData[1])
                                else:
                                    modelData = {'sockedID': 0, 'socketIDSocket': False}
                            else:
                                modelData = {'add_socket':'[False,None]'}
                            
                            filePath = fileData[1]
                            correctingValue_X = fileData[2]['x']  # pos_X
                            correctingValue_Y = fileData[2]['y']  # pos_Y
                            correctingValue_Z = fileData[2]['z']  # pos_Z
                            correctingValue_RX = fileData[2]['rx']  # pos_RX
                            correctingValue_RY = fileData[2]['ry']  # pos_RY
                            correctingValue_RZ = fileData[2]['rz']  # pos_RZ
                            
                            #### NEW MODEL SHAPE
                            i = self.getPartShape(filePath, i, koloroweElemnty)
                            ################################################################
                            # PUTTING OBJECT IN CORRECT POSITION/ORIENTATION
                            ################################################################
                            self.partPlacement(i, correctingValue_X, correctingValue_Y, correctingValue_Z, correctingValue_RX, correctingValue_RY, correctingValue_RZ, i.X.Value, i.Y.Value)
                            if i.Side == "BOTTOM":
                                i.Proxy.changeSide(i)
                            i.Proxy.oldROT = 0
                            i.Rot = i.Rot.Value # rot around Z
                            i.Proxy.updatePosition_Z(i, pcb[1], True)
                            self.addPartToGroup(groupParts, i)
                        elif i.Proxy.Type == "PCBpart_E" and fileData[0]:
                            newPart = self.partStandardDictionary()
                            newPart['name'] = i.Label
                            newPart['library'] = i.Package
                            newPart['package'] = package
                            newPart['value'] = i.Rot.Value
                            newPart['x'] = i.X.Value
                            newPart['y'] = i.Y.Value
                            newPart['rot'] = i.Rot.Value
                            newPart['side'] = i.Side
                            
                            newPart['EL_Name']["x"] = i.X.Value
                            newPart['EL_Name']["y"] = i.Y.Value
                            newPart['EL_Name']["rot"] = i.Rot.Value
                            newPart['EL_Name']["side"] = i.Side
                            
                            newPart['EL_Value']["x"] = i.X.Value
                            newPart['EL_Value']["y"] = i.Y.Value
                            newPart['EL_Value']["rot"] = i.Rot.Value
                            newPart['EL_Value']["side"] = i.Side
                            
                            result = self.addPart(newPart, koloroweElemnty, adjustParts, groupParts)
                            if result[0] == 'OK':
                                try:
                                    FreeCAD.activeDocument().removeObject(i.Name)
                                except:
                                    pass
                        else:
                            self.addPartToGroup(groupParts, i)
        # packages = []
        # for i in range(self.form.listaElementow.count()):
            # if self.form.listaElementow.item(i).checkState() == 2:
                # packages.append(str(self.form.listaElementow.item(i).data(QtCore.Qt.UserRole)))
        # #################################################################
        # if FreeCAD.activeDocument():
            # doc = FreeCAD.activeDocument()
            # if len(doc.Objects):
                # self.databaseType = self.form.listaBibliotek.itemData(self.form.listaBibliotek.currentIndex(), QtCore.Qt.UserRole)
                # for j in doc.Objects:
                    # if hasattr(j, "Proxy") and hasattr(j.Proxy, "Type") and j.Proxy.Type in ["PCBpart", "PCBpart_E"] and not j.KeepPosition  and j.Package in packages:
                        # koloroweElemnty = self.form.plytkaPCB_elementyKolory.isChecked()
                        # adjustParts = self.form.adjustParts.isChecked()
                        # groupParts = self.form.groupParts.isChecked()
                        
                        # name = j.Label
                        # package = j.Package
                        # try:
                            # value = j.PartValue.ViewObject.Text
                        # except:
                            # value = ""
                        # x = j.X.Value - j.Proxy.offsetX
                        # y = j.Y.Value - j.Proxy.offsetY
                        # rot = j.Rot.Value
                        # side = j.Side
                        # library = j.Package
                        
                        # ##################################################################
                        # ## part name object
                        # ## [txt, x, y, size, rot, side, align, spin, mirror, font]
                        # ##################################################################
                        # if j.PartName:
                            # PartName_text = j.PartName.ViewObject.Text
                            # PartName_x = j.PartName.X
                            # PartName_y = j.PartName.Y
                            # PartName_size = j.PartName.ViewObject.Size
                            # PartName_rot = j.PartName.Rot
                            # PartName_side = j.PartName.Side
                            # PartName_align = j.PartName.ViewObject.Align
                            # PartName_mirror = j.PartName.ViewObject.Mirror
                            # PartName_spin = j.PartName.ViewObject.Spin
                            # PartName_Visibility = j.PartName.ViewObject.Visibility
                            # PartName_Color = j.PartName.ViewObject.Color
                        # else:
                            # PartName_text = name
                            # PartName_x = x
                            # PartName_y = y
                            # PartName_size = 1.27
                            # PartName_rot = rot
                            # PartName_side = side
                            # PartName_align = "bottom-left"
                            # PartName_mirror = 'None'
                            # PartName_spin = False
                            # PartName_Visibility = True
                            # PartName_Color = (1., 1., 1.)
                            
                        # EL_Name = [PartName_text, PartName_x, PartName_y, PartName_size, PartName_rot, PartName_side, PartName_align, PartName_spin, PartName_mirror, '', PartName_Visibility]
                        # ##################################################################
                        # ## part value
                        # ## [txt, x, y, size, rot, side, align, spin, mirror, font]
                        # ##################################################################
                        # if j.PartValue:
                            # PartValue_text = j.PartValue.ViewObject.Text
                            # PartValue_x = j.PartValue.X
                            # PartValue_y = j.PartValue.Y
                            # PartValue_size = j.PartValue.ViewObject.Size
                            # PartValue_rot = j.PartValue.Rot
                            # PartValue_side = j.PartValue.Side
                            # PartValue_align = j.PartValue.ViewObject.Align
                            # PartValue_mirror = j.PartValue.ViewObject.Mirror
                            # PartValue_spin = j.PartValue.ViewObject.Spin
                            # PartValue_Visibility = j.PartValue.ViewObject.Visibility
                            # PartValue_Color = j.PartValue.ViewObject.Color
                        # else:
                            # PartValue_text = name
                            # PartValue_x = x
                            # PartValue_y = y
                            # PartValue_size = 1.27
                            # PartValue_rot = rot
                            # PartValue_side = side
                            # PartValue_align = "bottom-left"
                            # PartValue_mirror = 'None'
                            # PartValue_spin = False
                            # PartValue_Visibility = True
                            # PartValue_Color = (1., 1., 1.)
                            
                        # EL_Value = [PartValue_text, PartValue_x, PartValue_y, PartValue_size, PartValue_rot, PartValue_side, PartValue_align, PartValue_spin, PartValue_mirror, '', PartValue_Visibility]
                        # ##################################################################
                        # ## 
                        # ##################################################################
                        # newPart = [[name, library, value, x, y, rot, side, package], EL_Name, EL_Value]
                        # result = self.addPart(newPart, koloroweElemnty, adjustParts, groupParts)
                        
                        # # if result[0] == 'OK':
                            # # oldValueLabel = j.PartValue.Label
                            # # oldNameLabel = j.PartName.Label
                            # # # del old object
                            # # doc.removeObject(j.PartValue.Name)
                            # # doc.removeObject(j.PartName.Name)
                            # # doc.removeObject(j.Name)
                            # # # rename new object name
                            # # result[1].Label = name
                            # # result[1].PartValue.Label = oldValueLabel
                            # # result[1].PartName.Label = oldNameLabel
                            # # # set text color
                            # # result[1].PartName.ViewObject.Color = PartName_Color
                            # # result[1].PartValue.ViewObject.Color = PartValue_Color
                        # # else:
                            # # doc.removeObject(result[1].PartValue.Name)
                            # # doc.removeObject(result[1].PartName.Name)
                            # # doc.removeObject(result[1].Name)
        return True
