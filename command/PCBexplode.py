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
    import FreeCADGui
    from PySide import QtCore, QtGui
from functools import partial


class ser:
    def __init__(self):
        self.dostepneWarstwy = QtGui.QComboBox()
        self.dostepneWarstwy.addItems(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
        self.dostepneWarstwy.setCurrentIndex(1)
        self.dostepneWarstwy.setMaximumWidth(60)


class explodeObjectTable(QtGui.QTreeWidget):
    def __init__(self, parent=None):
        QtGui.QTreeWidget.__init__(self, parent)
        
        self.setColumnCount(2)
        self.setItemsExpandable(True)
        self.setSortingEnabled(False)
        self.setHeaderLabels(['Object', 'Layer'])
        self.setFrameShape(QtGui.QFrame.NoFrame)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.setStyleSheet('''
            QTreeWidget QHeaderView
            {
                border:0px;
            }
            QTreeWidget
            {
                border: 1px solid #9EB6CE;
                border-top:0px;
            }
            QTreeWidget QHeaderView::section
            {
                color:#4C4161;
                font-size:12px;
                border:1px solid #9EB6CE;
                border-left:0px;
                padding:5px;
            }
        ''')

    def showHideAllObj(self, value):
        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            if not root.child(i).checkState(0) == 2:
                root.child(i).setCheckState(0, QtCore.Qt.Unchecked)
                root.child(i).setHidden(value)

    def DeSelectAllObj(self, value):
        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            if not root.child(i).isHidden():
                root.child(i).setCheckState(0, value)

    def schowajItem(self, name, value):
        value = [False, None, True][value]
        root = self.invisibleRootItem()

        for i in range(root.childCount()):
            item = root.child(i)
            if item.data(0, QtCore.Qt.UserRole) == name:
                item.setCheckState(0, QtCore.Qt.Unchecked)
                item.setHidden(value)
                return
        return


class explodeWizardWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        #
        self.TopStepSize = QtGui.QSpinBox()
        self.TopStepSize.setRange(5, 100)
        self.TopStepSize.setValue(10)
        self.TopStepSize.setSingleStep(5)
        
        self.BottomStepSize = QtGui.QSpinBox()
        self.BottomStepSize.setRange(5, 100)
        self.BottomStepSize.setValue(10)
        self.BottomStepSize.setSingleStep(5)
        #
        self.tableTop = explodeObjectTable()
        self.tableBottom = explodeObjectTable()
        
        # partial dont work
        self.connect(self.tableTop, QtCore.SIGNAL('itemClicked(QTreeWidgetItem*, int)'), self.klikGora)
        self.connect(self.tableBottom, QtCore.SIGNAL('itemClicked(QTreeWidgetItem*, int)'), self.klikDol)
        #
        self.setActive = QtGui.QCheckBox('Active')
        self.setActive.setChecked(False)
        
        self.inversObj = QtGui.QCheckBox('Inverse')
        self.inversObj.setChecked(False)
        #
        przSelectAllT = QtGui.QPushButton('')
        przSelectAllT.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        przSelectAllT.setFlat(True)
        przSelectAllT.setIcon(QtGui.QIcon(":/data/img/checkbox_checked_16x16.png"))
        przSelectAllT.setToolTip('Select all')
        par = partial(self.selectAllObj, self.tableTop, self.tableBottom)
        self.connect(przSelectAllT, QtCore.SIGNAL('pressed ()'), par)
        
        przSelectAllTF = QtGui.QPushButton('')
        przSelectAllTF.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        przSelectAllTF.setFlat(True)
        przSelectAllTF.setIcon(QtGui.QIcon(":/data/img/checkbox_unchecked_16x16.PNG"))
        przSelectAllTF.setToolTip('Deselect all')
        par = partial(self.deselectAllObj, self.tableTop, self.tableBottom)
        self.connect(przSelectAllTF, QtCore.SIGNAL('pressed ()'), par)
        
        przSelectAllT1 = QtGui.QPushButton('')
        przSelectAllT1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        przSelectAllT1.setFlat(True)
        przSelectAllT1.setIcon(QtGui.QIcon(":/data/img/checkbox_checked_16x16.png"))
        przSelectAllT1.setToolTip('Select all')
        par = partial(self.selectAllObj, self.tableBottom, self.tableTop)
        self.connect(przSelectAllT1, QtCore.SIGNAL('pressed ()'), par)
        
        przSelectAllTF1 = QtGui.QPushButton('')
        przSelectAllTF1.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        przSelectAllTF1.setFlat(True)
        przSelectAllTF1.setIcon(QtGui.QIcon(":/data/img/checkbox_unchecked_16x16.PNG"))
        przSelectAllTF1.setToolTip('Deselect all')
        par = partial(self.deselectAllObj, self.tableBottom, self.tableTop)
        self.connect(przSelectAllTF1, QtCore.SIGNAL('pressed ()'), par)
        #
        lay = QtGui.QGridLayout()
        lay.addWidget(QtGui.QLabel('Top Step Size'), 0, 0, 1, 2)
        lay.addWidget(self.TopStepSize, 0, 2, 1, 1)
        
        lay.addWidget(przSelectAllT, 1, 0, 1, 1)
        lay.addWidget(przSelectAllTF, 2, 0, 1, 1)
        lay.addWidget(self.tableTop, 1, 1, 3, 2)
        
        lay.addWidget(QtGui.QLabel('Bottom Step Size'), 4, 0, 1, 2)
        lay.addWidget(self.BottomStepSize, 4, 2, 1, 1)
        
        lay.addWidget(przSelectAllT1, 5, 0, 1, 1)
        lay.addWidget(przSelectAllTF1, 6, 0, 1, 1)
        lay.addWidget(self.tableBottom, 5, 1, 3, 2)
        
        lay.addWidget(self.setActive, 8, 0, 1, 3)
        lay.addWidget(self.inversObj, 9, 0, 1, 3)
        
        lay.setColumnStretch(1, 10)
        lay.setColumnStretch(2, 5)
        
        self.setLayout(lay)
        
    def selectAllObj(self, tabela_1, tabela_2):
        tabela_1.DeSelectAllObj(QtCore.Qt.Checked)
        tabela_2.showHideAllObj(True)

    def deselectAllObj(self, tabela_1, tabela_2):
        tabela_1.DeSelectAllObj(QtCore.Qt.Unchecked)
        tabela_2.showHideAllObj(False)
        
    def deselectAll(self, table_1, table_2):
        pass
    
    def klikGora(self):
        self.odznaczDrug(self.tableBottom, self.tableTop)
        
    def klikDol(self):
        self.odznaczDrug(self.tableTop, self.tableBottom)
        
    def odznaczDrug(self, table, tableMain):
        #FreeCAD.Console.PrintWarning("{0} 1\n".format(tableMain.currentItem()))
        #FreeCAD.Console.PrintWarning("{0} 2\n".format(tableMain.currentItem().data(0, QtCore.Qt.UserRole)))
        #FreeCAD.Console.PrintWarning("{0} 3\n".format(tableMain.currentItem().checkState(0)))
        
        item = tableMain.currentItem()
        name = item.data(0, QtCore.Qt.UserRole)
        value = item.checkState(0)
        table.schowajItem(name, value)


class explodeEditWizard:
    def __init__(self, obj):
        self.mainObject = obj
        
        self.form = explodeWizardWidget()
        self.form.setWindowTitle('Explode settings - editing `{0}`'.format(self.mainObject.Label))
        self.form.setWindowIcon(QtGui.QIcon(":/data/img/explode.png"))

    def reject(self):
        return True
        
    def accept(self):
        doc = FreeCAD.activeDocument()
        
        self.mainObject.Proxy.spisObiektowGora = {}
        self.mainObject.Proxy.spisObiektowDol = {}
        # top
        root = self.form.tableTop.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if item.checkState(0) == 2:
                name = str(item.data(0, QtCore.Qt.UserRole))
                layer = int(self.form.tableTop.itemWidget(item, 1).currentText())
                 
                elem = doc.getObject(name)
                self.mainObject.Proxy.spisObiektowGora[name] = [elem.Placement.Base.z, layer]
        # bottom
        root = self.form.tableBottom.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if item.checkState(0) == 2:
                name = str(item.data(0, QtCore.Qt.UserRole))
                layer = int(self.form.tableBottom.itemWidget(item, 1).currentText())
                 
                elem = doc.getObject(name)
                self.mainObject.Proxy.spisObiektowDol[name] = [elem.Placement.Base.z, layer]
        #
        self.mainObject.Inverse = self.form.inversObj.isChecked()
        self.mainObject.Active = self.form.setActive.isChecked()
        self.mainObject.TopStepSize = self.form.TopStepSize.value()
        self.mainObject.BottomStepSize = self.form.BottomStepSize.value()
        self.mainObject.Proxy.generuj(self.mainObject)
        return True
        
    def clicked(self, index):
        pass
        
    def open(self):
        self.mainObject.Active = False
        self.mainObject.Proxy.generuj(self.mainObject)
        #
        self.form.inversObj.setChecked(self.mainObject.Inverse)
        self.form.setActive.setChecked(self.mainObject.Active)
        self.form.TopStepSize.setValue(self.mainObject.TopStepSize)
        self.form.BottomStepSize.setValue(self.mainObject.BottomStepSize)
        #
        obj = FreeCAD.ActiveDocument.Objects
        nr = 1
        for i in obj:
            if hasattr(i, "Placement"):
                #top
                a = QtGui.QTreeWidgetItem()
                a.setText(0, i.Label)
                a.setData(0, QtCore.Qt.UserRole, i.Name)
                a.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable | Qt.ItemIsSelectable)
                
                dostepneWarstwy = QtGui.QComboBox()
                dostepneWarstwy.addItems(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
                dostepneWarstwy.setMaximumWidth(60)
                
                if i.Name in self.mainObject.Proxy.spisObiektowGora.keys():
                    a.setCheckState(0, QtCore.Qt.Checked)
                    dostepneWarstwy.setCurrentIndex(dostepneWarstwy.findText(str(self.mainObject.Proxy.spisObiektowGora[i.Name][1])))
                else:
                    a.setCheckState(0, QtCore.Qt.Unchecked)
                    dostepneWarstwy.setCurrentIndex(1)
                    
                globals()["zm_g_%s" % nr] = dostepneWarstwy  # workaround bug from pyside
                
                self.form.tableTop.addTopLevelItem(a)
                self.form.tableTop.setItemWidget(a, 1, globals()["zm_g_%s" % nr])
                if i.Name in self.mainObject.Proxy.spisObiektowDol.keys(): a.setHidden(True)
                
                # bottom
                a = QtGui.QTreeWidgetItem()
                a.setText(0, i.Label)
                a.setData(0, QtCore.Qt.UserRole, i.Name)
                a.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
                    
                dostepneWarstwy = QtGui.QComboBox()
                dostepneWarstwy.addItems(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
                dostepneWarstwy.setMaximumWidth(60)

                if i.Name in self.mainObject.Proxy.spisObiektowDol.keys():
                    a.setCheckState(0, QtCore.Qt.Checked)
                    dostepneWarstwy.setCurrentIndex(dostepneWarstwy.findText(str(self.mainObject.Proxy.spisObiektowDol[i.Name][1])))
                else:
                    a.setCheckState(0, QtCore.Qt.Unchecked)
                    dostepneWarstwy.setCurrentIndex(1)
                
                globals()["zm_d_%s" % nr] = dostepneWarstwy  # workaround bug from pyside
                    
                self.form.tableBottom.addTopLevelItem(a)
                self.form.tableBottom.setItemWidget(a, 1, globals()["zm_d_%s" % nr])
                if i.Name in self.mainObject.Proxy.spisObiektowGora.keys(): a.setHidden(True)
                
                ####
                nr += 1
                
        self.form.tableTop.resizeColumnToContents(1)
        self.form.tableBottom.resizeColumnToContents(1)
        
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


class explodeWizard:
    def __init__(self):
        self.form = explodeWizardWidget()
        self.form.setWindowTitle('Explode settings')
        self.form.setWindowIcon(QtGui.QIcon(":/data/img/explode.png"))

    def reject(self):
        return True
        
    def accept(self):
        doc = FreeCAD.activeDocument()
        a = doc.addObject("App::FeaturePython", 'Explode')
        obj = explodeObject(a)

        # top
        root = self.form.tableTop.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if item.checkState(0) == 2:
                name = str(item.data(0, QtCore.Qt.UserRole))
                layer = int(self.form.tableTop.itemWidget(item, 1).currentText())
                 
                elem = doc.getObject(name)
                obj.spisObiektowGora[name] = [elem.Placement.Base.z, layer]
        # bottom
        root = self.form.tableBottom.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            if item.checkState(0) == 2:
                name = str(item.data(0, QtCore.Qt.UserRole))
                layer = int(self.form.tableBottom.itemWidget(item, 1).currentText())
                 
                elem = doc.getObject(name)
                obj.spisObiektowDol[name] = [elem.Placement.Base.z, layer]
        #
        obj.setParam(a, 'Inverse', self.form.inversObj.isChecked())
        obj.setParam(a, 'Active', self.form.setActive.isChecked())
        obj.setParam(a, 'TopStepSize', self.form.TopStepSize.value())
        obj.setParam(a, 'BottomStepSize', self.form.BottomStepSize.value())
        obj.generuj(a)
        viewProviderExplodeObject(a.ViewObject)
        return True

    def clicked(self, index):
        pass

    def open(self):
        obj = FreeCAD.ActiveDocument.Objects
        
        nr = 0
        for i in obj:
            if hasattr(i, "Placement"):
                #top
                a = QtGui.QTreeWidgetItem()
                a.setText(0, i.Label)
                a.setCheckState(0, QtCore.Qt.Unchecked)
                a.setData(0, QtCore.Qt.UserRole, i.Name)
                try:
                    a.setIcon(0, i.ViewObject.Icon)
                except AttributeError:
                    pass
                a.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
                
                dostepneWarstwy = QtGui.QComboBox()
                dostepneWarstwy.addItems(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
                dostepneWarstwy.setCurrentIndex(1)
                dostepneWarstwy.setMaximumWidth(60)
                globals()["zm_g_%s" % nr] = dostepneWarstwy  # workaround bug from pyside

                self.form.tableTop.addTopLevelItem(a)
                self.form.tableTop.setItemWidget(a, 1, globals()["zm_g_%s" % nr])
                
                # bottom
                a = QtGui.QTreeWidgetItem()
                a.setText(0, i.Label)
                a.setCheckState(0, QtCore.Qt.Unchecked)
                a.setData(0, QtCore.Qt.UserRole, i.Name)
                try:
                    a.setIcon(0, i.ViewObject.Icon)
                except AttributeError:
                    pass
                a.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
                
                dostepneWarstwy = QtGui.QComboBox()
                dostepneWarstwy.addItems(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10'])
                dostepneWarstwy.setCurrentIndex(1)
                dostepneWarstwy.setMaximumWidth(60)
                globals()["zm_d_%s" % nr] = dostepneWarstwy  # workaround bug from pyside
                
                self.form.tableBottom.addTopLevelItem(a)
                self.form.tableBottom.setItemWidget(a, 1, globals()["zm_d_%s" % nr])
                
                ##
                nr += 1
            
        self.form.tableTop.resizeColumnToContents(1)
        self.form.tableBottom.resizeColumnToContents(1)
                
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


###########
###########
class explodeObject:
    def __init__(self, obj):
        self.Type = 'Explode'
        
        self.spisObiektowGora = {}
        self.spisObiektowDol = {}
        obj.addProperty("App::PropertyBool", "Active", "Base", "Active/deacvtive explode").Active = False
        obj.addProperty("App::PropertyBool", "Inverse", "Base", "Inverse").Inverse = False
        obj.addProperty("App::PropertyFloat", "TopStepSize", "Base", "Top explode step").TopStepSize = 10.
        obj.addProperty("App::PropertyFloat", "BottomStepSize", "Base", "Bottom explode step").BottomStepSize = 10.
        
        obj.Proxy = self
        
    def wylaczPozostale(self):
        pass
        
    def onChanged(self, fp, prop):
        if hasattr(fp, "Placement"):
            fp.setEditorMode("Placement", 2)
        
        if prop == 'Active' or prop == 'TopStepSize' or prop == 'BottomStepSize' or prop == 'Inverse':
            self.generuj(fp)
        #if prop == 'Active':
            #self.wylaczPozostale()
            
    def setParam(self, obj, param, value):
        if param == 'Active':
            obj.Active = value
        elif param == 'Inverse':
            obj.Inverse = value
        elif param == 'BottomStepSize':
            obj.BottomStepSize = value
        elif param == 'TopStepSize':
            obj.TopStepSize = value

    def generuj(self, fp):
        for i, j in self.spisObiektowGora.items():
            try:
                elem = fp.Document.getObject(i)
                pos = elem.Placement.Base

                if fp.Active:
                    if not fp.Inverse:
                        pos.z = j[0] + j[1] * fp.TopStepSize
                    else:
                        pos.z = j[0] - j[1] * fp.BottomStepSize
                else:
                    pos.z = j[0]
            except:
                continue
        
        for i, j in self.spisObiektowDol.items():
            try:
                elem = fp.Document.getObject(i)
                pos = elem.Placement.Base

                if fp.Active:
                    if not fp.Inverse:
                        pos.z = j[0] - j[1] * fp.BottomStepSize
                    else:
                        pos.z = j[0] + j[1] * fp.TopStepSize
                else:
                    pos.z = j[0]
            except:
                continue

    def execute(self, fp):
        pass
        
    def __getstate__(self):
        return (self.spisObiektowGora, self.spisObiektowDol, self.Type)
        
    def __setstate__(self, state):
        self.spisObiektowGora = state[0]
        self.spisObiektowDol = state[1]
        self.Type = state[2]
        return None


class viewProviderExplodeObject:
    def __init__(self, obj):
        ''' Set this object to the proxy object of the actual view provider '''
        obj.Proxy = self

    # Copy from ArchAxis.py -> Arch module
    # Author: Yorik van Havre <yorik@uncreated.net>
    #def attach(self, vobj):  # <<<<<<<<<--------------- cos jest nie tak z tym fragmentem!!!!!!!!!!!!!!!!!!!!!!!!
        #self.bubbles = None
        #self.bubbletexts = []
        #sep = coin.SoSeparator()
        #self.mat = coin.SoMaterial()
        #self.linestyle = coin.SoDrawStyle()
        #self.linecoords = coin.SoCoordinate3()
        #self.lineset = coin.SoType.fromName("SoBrepEdgeSet").createInstance()
        #self.bubbleset = coin.SoSeparator()
        #sep.addChild(self.mat)
        #sep.addChild(self.linestyle)
        #sep.addChild(self.linecoords)
        #sep.addChild(self.lineset)
        #sep.addChild(self.bubbleset)
        #vobj.addDisplayMode(sep,"Default")
        #self.onChanged(vobj,"BubbleSize")
    
    def setEdit(self, vobj, mode=0):
        panel = explodeEditWizard(vobj)
        FreeCADGui.Control.showDialog(panel)
        return True
    
    def unsetEdit(self,vobj,mode):
        FreeCADGui.Control.closeDialog()
        return

    def doubleClicked(self,vobj):
        self.setEdit(vobj.Object)
        
    def getDisplayModes(self, vobj):
        return ["Default"]

    def getDefaultDisplayMode(self):
        return "Default"
    ##############################################

    def onChanged(self, vp, prop):
        ''' Print the name of the property that has changed '''
        vp.setEditorMode("DisplayMode", 2)
        vp.setEditorMode("Visibility", 2)
        if hasattr(vp, "AngularDeflection"):
            vp.setEditorMode("AngularDeflection", 2)

    def getIcon(self):
        ''' Return the icon in XMP format which will appear in the tree view. This method is optional
        and if not defined a default icon is shown.
        '''
        #***************************************************************
        #   Author:     Gentleface custom icons design agency (http://www.gentleface.com/)
        #   License:    Creative Commons Attribution-Noncommercial 3.0
        #   Iconset:    Mono Icon Set
        #***************************************************************
        return ":/data/img/explode_TI.svg"
        
    def __getstate__(self):
        ''' When saving the document this object gets stored using Python's cPickle module.
        Since we have some un-pickable here -- the Coin stuff -- we must define this method
        to return a tuple of all pickable objects or None.
        '''
        return None

    def __setstate__(self, state):
        ''' When restoring the pickled object from document we have the chance to set some
        internals here. Since no data were pickled nothing needs to be done here.
        '''
        return None
