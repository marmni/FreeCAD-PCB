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

# import sqlite3                <--- NOT WORKING, WHY?
import ConfigParser
import random
import os
import FreeCAD
from PySide import QtGui, QtCore
import __builtin__
from xml.dom import minidom
import __builtin__
import re
#
from PCBfunctions import getFromSettings_databasePath
from PCBconf import defSoftware
from PCBcategories import readCategories, addCategory, getCategoryIdByName


class dataBase:
    def __init__(self, parent=None):
        self.config = ConfigParser.RawConfigParser()
        self.fileName = None
    
    def convertDatabaseEntries(self):
        dial = convertSoftwareItems(self)
        if dial.exec_():
            soft = dial.toSoftware.currentText()
            
            for i in range(dial.categoriesTable.rowCount()):
                if dial.categoriesTable.cellWidget(i, 0).isChecked():
                    try:
                        sectionID = dial.categoriesTable.item(i, 1).text()
                        name = dial.categoriesTable.item(i, 3).text()
                        try:
                            x = float(dial.categoriesTable.item(i, 5).text())
                        except ValueError:
                            x = 0.0
                        try:
                            y = float(dial.categoriesTable.item(i, 6).text())
                        except ValueError:
                            y = 0.0
                        try:
                            z = float(dial.categoriesTable.item(i, 7).text())
                        except ValueError:
                            z = 0.0  
                        try:
                            rx = float(dial.categoriesTable.item(i, 8).text())
                        except ValueError:
                            rx = 0.0
                        try:
                            ry = float(dial.categoriesTable.item(i, 9).text())
                        except ValueError:
                            ry = 0.0
                        try:
                            rz = float(dial.categoriesTable.item(i, 10).text())
                        except ValueError:
                            rz = 0.0
                        #
                        softsList = eval(self.getValues(sectionID)['soft'])
                        
                        if not [name, soft, x, y, z, rx, ry, rz] in softsList:
                            connections = [[name, soft, x, y, z, rx, ry, rz]]
                         
                            dane = {'soft': connections + softsList}
                            self.updatePackage(sectionID, dane)
                    except:
                        continue
            #
            return True
        
    def read(self, fileName):
        if fileName != "":
            #self.config = ConfigParser.RawConfigParser()
            sciezka = os.path.dirname(fileName)
            if os.access(sciezka, os.R_OK) and os.access(sciezka, os.F_OK):
                self.fileName = fileName
                self.config.read(fileName)
                return True
            FreeCAD.Console.PrintWarning("Access Denied. The file '{0}' may not exist, or there could be permission problem.\n".format(fileName))
            
    def create(self, fileName):
        plik = __builtin__.open(fileName, "w")
        plik.close()
        self.fileName = fileName
        #self.config = ConfigParser.RawConfigParser()
        self.config.read(fileName)
        
    def write(self):
        if os.access(os.path.dirname(self.fileName), os.W_OK):
            with open(self.fileName, 'wb') as configfile:
                self.config.write(configfile)
            return True
        FreeCAD.Console.PrintWarning("Access Denied. The file '{0}' may not exist, or there could be permission problem.\n".format(self.fileName))

    def has_section(self, name):
        return self.config.has_section(str(name))
        
    def findPackage(self, package, soft):
        for i in self.packages():
            for j in eval(self.getValues(i)["soft"]):
                if soft == '*':
                    if str(package) in j:
                        return [True, i, j, int(self.getValues(i)['category'])]
                else:
                    if str(soft) in j and str(package) in j:
                        return [True, i, j, int(self.getValues(i)['category'])]
        return [False]
        
    def has_value(self, valueName, txt):
        for i in self.packages():
            if self.config.get(i, valueName) == txt:
                return [True, i]
        return [False]
            
    def getValues(self, sectionName):
        dane = {}
        for i in self.config.items(sectionName):
            dane[i[0]] = i[1]
        return dane
        
    def reloadList(self):
        self.read(self.fileName)
            
    def delPackage(self, name):
        self.config.remove_section(name)
        self.write()
    
    def updateValue(self, sectionName, txt, value):
        self.config.set(sectionName, txt, value)
        
    def updatePackage(self, sectionName, dane):
        for i, j in dane.items():
            self.config.set(sectionName, i, j)
        #self.config.set(sectionName, 'name', dane["name"])
        #self.config.set(sectionName, 'path', dane["path"])
        #self.config.set(sectionName, 'x', dane["x"])
        #self.config.set(sectionName, 'y', dane["y"])
        #self.config.set(sectionName, 'z', dane["z"])
        #self.config.set(sectionName, 'rx', dane["rx"])
        #self.config.set(sectionName, 'ry', dane["ry"])
        #self.config.set(sectionName, 'rz', dane["rz"])
        #self.config.set(sectionName, 'add_socket', dane["add_socket"])
        #self.config.set(sectionName, 'add_socket_id', dane["add_socket_id"])
        #self.config.set(sectionName, 'socket', dane["socket"])
        #self.config.set(sectionName, 'socket_height', dane["socket_height"])
        #self.config.set(sectionName, 'description', dane["description"])
        #self.config.set(sectionName, 'datasheet', dane["datasheet"])
        self.write()
        
    def wygenerujID(self, ll, lc):
        ''' generate random section name '''
        numerID = ""
    
        for i in range(ll):
            numerID += random.choice('abcdefghij')
        numerID += "_"
        for i in range(lc):
            numerID += str(random.randrange(0, 99, 1))
        
        if not self.has_section(numerID):
            return numerID
        else:
            return self.wygenerujID(ll, lc)
            
    def addPackage(self, dane):
        sectionName = self.wygenerujID(5, 5)
        
        self.config.add_section(sectionName)
        for i, j in dane.items():
            self.config.set(sectionName, i, j)
        #self.config.set(sectionName, 'name', dane["name"])
        #self.config.set(sectionName, 'path', dane["path"])
        #self.config.set(sectionName, 'x', dane["x"])
        #self.config.set(sectionName, 'y', dane["y"])
        #self.config.set(sectionName, 'z', dane["z"])
        #self.config.set(sectionName, 'rx', dane["rx"])
        #self.config.set(sectionName, 'ry', dane["ry"])
        #self.config.set(sectionName, 'rz', dane["rz"])
        #self.config.set(sectionName, 'add_socket', dane["add_socket"])
        #self.config.set(sectionName, 'add_socket_id', dane["add_socket_id"])
        #self.config.set(sectionName, 'socket', dane["socket"])
        #self.config.set(sectionName, 'socket_height', dane["socket_height"])
        #self.config.set(sectionName, 'description', dane["description"])
        #self.config.set(sectionName, 'datasheet', dane["datasheet"])
        self.write()
            
    def packages(self):
        return self.config.sections()
    
    def makeACopy(self):
        try:
            newFolder = QtGui.QFileDialog.getExistingDirectory(None, 'Save database copy', os.path.expanduser("~"))
            if newFolder:
                try:
                    xml = minidom.Document()
                    root = xml.createElement("pcb")
                    xml.appendChild(root)
                    
                    # categories
                    categories = xml.createElement("categories")
                    root.appendChild(categories)

                    for i,j in readCategories().items():
                        category = xml.createElement("category")
                        category.setAttribute('number', str(i))
                        category.setAttribute('name', str(j[0]))
                        #
                        description = xml.createTextNode(str(j[1]))
                        category.appendChild(description)
                        #
                        categories.appendChild(category)
                    # models
                    models = xml.createElement("models")
                    root.appendChild(models)
                    
                    for i in self.packages():
                        dane = self.getValues(i)
                        
                        model = xml.createElement("model")
                        model.setAttribute('ID', str(i))
                        model.setAttribute('name', str(dane['name']))
                        model.setAttribute('category', str(dane['category']))
                        model.setAttribute('datasheet', str(dane['datasheet']))
                        model.setAttribute('isSocket', str(eval(dane['socket'])[0]))
                        model.setAttribute('height', str(eval(dane['socket'])[1]))
                        model.setAttribute('socket', str(eval(dane['add_socket'])[0]))
                        model.setAttribute('socketID', str(eval(dane['add_socket'])[1]))
                        #
                        description = xml.createElement("description")
                        model.appendChild(description)
                        
                        descriptionTXT = xml.createTextNode(str(dane['description']))
                        description.appendChild(descriptionTXT)
                        #
                        paths = xml.createElement("paths")
                        model.appendChild(paths)
                        
                        for j in dane['path'].split(';'):
                            path = xml.createElement("path")
                            
                            description = xml.createTextNode(str(j))
                            path.appendChild(description)
                            #
                            paths.appendChild(path)
                        #
                        connections = xml.createElement("connections")
                        model.appendChild(connections)
                        
                        for j in eval(dane['soft']):
                            item = xml.createElement("item")
                            item.setAttribute('name', str(j[0]))
                            item.setAttribute('soft', str(j[1]))
                            item.setAttribute('x', str(j[2]))
                            item.setAttribute('y', str(j[3]))
                            item.setAttribute('z', str(j[4]))
                            item.setAttribute('rx', str(j[5]))
                            item.setAttribute('ry', str(j[6]))
                            item.setAttribute('rz', str(j[7]))
                            #
                            connections.appendChild(item)
                        #
                        adjust = xml.createElement("adjust")
                        model.appendChild(adjust)
                        
                        try:
                            for i, j in eval(str(dane["adjust"])).items():
                                item = xml.createElement("item")
                                item.setAttribute('parameter', str(i))
                                
                                item.setAttribute('active', str(j[0]))
                                item.setAttribute('visible', str(j[1]))
                                item.setAttribute('x', str(j[2]))
                                item.setAttribute('y', str(j[3]))
                                item.setAttribute('z', str(j[4]))
                                item.setAttribute('size', str(j[5]))
                                item.setAttribute('align', str(j[7]))
                                #
                                color = xml.createElement("color")
                                color.setAttribute('R', str(j[6][0]))
                                color.setAttribute('G', str(j[6][1]))
                                color.setAttribute('B', str(j[6][2]))
                                ##
                                item.appendChild(color)
                                #
                                adjust.appendChild(item)
                        except:
                            pass
                        #
                        models.appendChild(model)
                    
                    # write to file
                    outputFile = __builtin__.open(os.path.join(newFolder, 'freecad-pcb_copy.fpcb'), 'w')
                    xml.writexml(outputFile)
                    outputFile.close()
                except Exception, e:
                    FreeCAD.Console.PrintWarning(u"{0} \n".format(e))
        except Exception, e:
            FreeCAD.Console.PrintWarning(u"{0} \n".format(e))
    
    def readFromXML(self):
        try:
            dial = readDatabaseFromXML_GUI(self)
            if dial.exec_():
                for i in QtGui.QTreeWidgetItemIterator(dial.modelsTable):
                    if str(i.value().data(0, QtCore.Qt.UserRole)) != 'PM':
                        continue
                
                    mainItem = i.value()
                    # items
                    connections = []
                    checked = 0
                    for j in range(mainItem.childCount()):
                        if mainItem.child(j).checkState(0) == QtCore.Qt.Checked:
                            child = mainItem.child(j).data(0, QtCore.Qt.UserRole + 2)
                            # <item name="1X08" rx="90.0" ry="0.0" rz="0.0" soft="Eagle" x="0.0" y="0.0" z="2.77"/>
                            name = child.getAttribute("name")
                            soft = child.getAttribute("soft")
                            x = float(child.getAttribute("x"))
                            y = float(child.getAttribute("y"))
                            z = float(child.getAttribute("z"))
                            rx = float(child.getAttribute("rx"))
                            ry = float(child.getAttribute("ry"))
                            rz = float(child.getAttribute("rz"))
                            #
                            connections.append([name, soft, x, y, z, rx, ry, rz])
                            checked += 1
                    
                    if checked == 0:
                        continue
                    #
                    if mainItem.data(0, QtCore.Qt.UserRole + 4) == 'new': # new entry
                        topLevelItem = mainItem.parent()
                        modelXML = mainItem.data(0, QtCore.Qt.UserRole + 2)
                        #
                        if topLevelItem.data(0, QtCore.Qt.UserRole) == -1:  # models without category
                            modelCategory = -1
                        elif topLevelItem.data(0, QtCore.Qt.UserRole) == 'New':  # new category
                            rowNum = topLevelItem.data(0, QtCore.Qt.UserRole + 1)
                        
                            categoryName = dial.categoriesTable.item(rowNum, 2).text()
                            categoryDescription = dial.categoriesTable.item(rowNum, 3).text()
                            #
                            modelCategory = getCategoryIdByName(categoryName)
                            if modelCategory == -1:
                                addCategory(categoryName, categoryDescription)
                                modelCategory = getCategoryIdByName(categoryName)
                        elif topLevelItem.data(0, QtCore.Qt.UserRole) == 'Old':  # add models to existing category
                            rowNum = topLevelItem.data(0, QtCore.Qt.UserRole + 1)
                            modelCategory = int(dial.categoriesTable.cellWidget(rowNum, 4).itemData(dial.categoriesTable.cellWidget(rowNum, 4).currentIndex())[0])
                        #
                        modelPaths = []
                        for j in modelXML.getElementsByTagName('paths')[0].getElementsByTagName('path'):
                            try:
                                modelPaths.append(j.firstChild.data)
                            except AttributeError:
                                pass
                        modelPaths = '; '.join(modelPaths)
                        #
                        try:
                            modelDescription = modelXML.getElementsByTagName('description')[0].firstChild.data
                        except AttributeError:
                            modelDescription = ''
                        #
                        #
                        adjust = {}
                        for j in modelXML.getElementsByTagName('adjust')[0].getElementsByTagName('item'):
                            parameter = str(j.getAttribute('parameter')).strip()
                            active = j.getAttribute('active')
                            visible = str(j.getAttribute('visible'))
                            x = float(j.getAttribute('x'))
                            y = float(j.getAttribute('y'))
                            z = float(j.getAttribute('z'))
                            size = float(j.getAttribute('size'))
                            align = str(j.getAttribute('align')).strip()
                            #
                            colors = j.getElementsByTagName('color')[0]
                            color = {float(colors.getAttribute('R')), float(colors.getAttribute('G')), float(colors.getAttribute('B'))}
                            #
                            adjust[parameter] = [active, visible, x, y, z, size, color, align]
                        #
                        self.addPackage({
                            "name": str(modelXML.getAttribute('name').strip()),
                            "path": modelPaths,
                            "add_socket": str([False, False]),
                            "socket": str([eval(modelXML.getAttribute('isSocket')), float(modelXML.getAttribute('height'))]),
                            "description": str(modelDescription),
                            "datasheet": str(modelXML.getAttribute('datasheet').strip()),
                            "soft": str(connections),
                            "category": str(modelCategory),
                            "adjust": str(adjust)
                        })
                    else:
                        sectionID = mainItem.data(0, QtCore.Qt.UserRole + 4)
                        
                        dane = {'soft': connections + eval(self.getValues(sectionID)['soft'])}
                        self.updatePackage(sectionID, dane)
                
                return True
        except Exception ,e:
            FreeCAD.Console.PrintWarning("{0} \n".format(e))
        
        return False


class readDatabaseFromXML_GUI(QtGui.QDialog):
    def __init__(self, sql, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle(u'Import database')
        self.sql = sql
        
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
        self.tabs.setTabEnabled(1, False)
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
            self.modelsTable.clear()
            self.showInfo.setText('')
            categories = self.modelsLoadCategories()
            self.loadModels(categories)
    
    def loadModels(self, categories):
        databaseFile = __builtin__.open(getFromSettings_databasePath(), 'r').read()
        
        for i in self.newDtabase.getElementsByTagName('models')[0].getElementsByTagName('model'):
            modelName = i.getAttribute("name")
            modelID = i.getAttribute("ID")
            #
            try:
                modelDescription = i.getElementsByTagName('description')[0].firstChild.data
            except AttributeError:
                modelDescription = ''
            #
            modelPaths = []
            for j in i.getElementsByTagName('paths')[0].getElementsByTagName('path'):
                try:
                    modelPaths.append(j.firstChild.data)
                except AttributeError:
                    pass
            
            # main model
            mainModel = QtGui.QTreeWidgetItem([modelName, modelDescription, '\n'.join(modelPaths)])
            mainModel.setData(0, QtCore.Qt.UserRole, 'PM')
            mainModel.setData(0, QtCore.Qt.UserRole + 1, modelID)
            mainModel.setData(0, QtCore.Qt.UserRole + 2, i)  # xml representation
            
            if len(modelPaths) == 0 or modelName == '':  # Corrupt entry - this is no error
                self.modelsListsetRowColor(mainModel, [255, 166 , 166])
                mainModel.setData(0, QtCore.Qt.UserRole + 3, "<span style='font-weight:bold; color: #F00;'>Info: Corrupt entry!</span>")  # info
            
            # child model
            errors = 0
            errorsID = -1
            modelSoftware = i.getElementsByTagName('connections')[0].getElementsByTagName('item')
            
            for j in modelSoftware:
                softwareModel = j.getAttribute("name")
                softwareName = j.getAttribute("soft")
                position = "X:{0} ;Y:{1} ;Z:{2} ;RX:{3} ;RY:{4} ;RZ:{5}".format(j.getAttribute("x"), j.getAttribute("y"), j.getAttribute("z"), 
                    j.getAttribute("rx"), j.getAttribute("ry"), j.getAttribute("rz"))
                #
                childModel = QtGui.QTreeWidgetItem([softwareName, softwareModel, position])
                childModel.setData(0, QtCore.Qt.UserRole, 'M')  # correct model definition
                childModel.setData(0, QtCore.Qt.UserRole + 2, j)  # xml representatio
                
                if re.search(r"\[u'%s', u'%s'" % (softwareModel, softwareName), databaseFile):
                    errors += 1
                    childModel.setData(0, QtCore.Qt.UserRole, 'ER')
                    
                    if errorsID == -1:
                        errorsID = self.sql.findPackage(softwareName, softwareModel)[1]
                    
                    self.modelsListsetRowColor(childModel, [255, 166 , 166])
                    childModel.setData(0, QtCore.Qt.UserRole + 3, "<span style='font-weight:bold; color: #F00;'>Error: Model is already defined in database.</span>")  # info
                else:
                    childModel.setCheckState(0, QtCore.Qt.Unchecked)
                
                if len(modelSoftware) > errors > 0:
                    mainModel.setData(0, QtCore.Qt.UserRole + 4, errorsID)
                elif errors == 0:
                    mainModel.setData(0, QtCore.Qt.UserRole + 4, 'new')
                
                mainModel.addChild(childModel)
            #######
            if errors == len(modelSoftware):
                categories[-2].addChild(mainModel)
            else:
                try:
                    categories[int(i.getAttribute("category"))].addChild(mainModel)
                except:  # 
                    categories[-1].addChild(mainModel)  # models without category
            
            
            ##
            #modelSoftware = {}
            #error = False
            
            #for j in i.getElementsByTagName('connections')[0].getElementsByTagName('item'):
                #softwareName = j.getAttribute("soft")
                #softwareModel = j.getAttribute("name")
                ##
                #if not softwareName in modelSoftware.keys():
                    #modelSoftware[softwareName] = []
                ##
                #if re.search(r"\[u'%s', u'%s'" % (softwareModel, softwareName), databaseFile):
                    #error = True
                ##
                #modelSoftware[softwareName].append(softwareModel)
                
            #modelSoftwareTXT = ''
            #for j, k in modelSoftware.items():
                #modelSoftwareTXT += '{0}: {1}\n'.format(j,'; '.join(k))
            #############
            #############
            #item = QtGui.QTreeWidgetItem([modelName, modelDescription, '\n'.join(modelPaths), modelSoftwareTXT.strip()])
            ##item.setCheckState(0, QtCore.Qt.Unchecked)
            ##item.setTextAlignment(0, QtCore.Qt.AlignTop)
            #item.setData(0, QtCore.Qt.UserRole, 'M')
            #item.setData(0, QtCore.Qt.UserRole + 1, modelID)
            #item.setData(0, QtCore.Qt.UserRole + 2, i)  # xml representation
            
            #if error:  # omitted models
                #self.modelsListsetRowColor(item, [255, 166 , 166])
                #item.setData(0, QtCore.Qt.UserRole + 3, "<span style='font-weight:bold; color: #F00;'>Error: Model is already defined in database.</span>")  # info
                
                #categories[-2].addChild(item)
            #else:
                #item.setCheckState(0, QtCore.Qt.Unchecked)
                
                #if len(modelPaths) == 0 or modelName == '' or modelSoftwareTXT.strip() == '':  # Corrupt entry - this is no error
                    #self.modelsListsetRowColor(item, [255, 166 , 166])
                    #item.setData(0, QtCore.Qt.UserRole + 3, "<span style='font-weight:bold; color: #F00;'>Info: Corrupt entry!</span>")  # info
                #elif re.search(r'name\s+=\s+%s' % modelName, databaseFile):  # object with same name already exist in database - this is no error
                    #self.modelsListsetRowColor(item, [255, 255 , 204])
                    #item.setData(0, QtCore.Qt.UserRole + 3, "<span style='font-weight:bold; color: #000;'>Info: Object with same name already exist in database!</span>")  # info
                #else:
                    #self.modelsListsetRowColor(item, [193, 255, 193])
                    ##item.setData(0, QtCore.Qt.UserRole + 3, "<span style='font-weight:bold; color: #F00;'></span>")  # info
            
                #try:
                    #categories[int(i.getAttribute("category"))].addChild(item)
                #except:  # 
                    #categories[-1].addChild(item)  # models without category
    
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
        for i in range(self.categoriesTable.rowCount()):
            if self.categoriesTable.cellWidget(i, 0).isChecked():
                oldCategoryID = int(self.categoriesTable.item(i, 1).text())
                
                if self.categoriesTable.cellWidget(i, 4).currentIndex() == 0:
                    mainItem = QtGui.QTreeWidgetItem(['{0} (New category)'.format(self.categoriesTable.item(i, 2).text())])
                    mainItem.setData(0, QtCore.Qt.UserRole, 'New')
                    mainItem.setData(0, QtCore.Qt.UserRole + 3, "<span style='font-weight:bold;'>New category '{0}' will be added.</span>".format(self.categoriesTable.item(i, 2).text()))  # info
                else:
                    categoryData = self.categoriesTable.cellWidget(i, 4).itemData(self.categoriesTable.cellWidget(i, 4).currentIndex())
                    
                    mainItem = QtGui.QTreeWidgetItem(['{1} (New category {0})'.format(categoryData[1], self.categoriesTable.item(i, 2).text())])
                    mainItem.setData(0, QtCore.Qt.UserRole, 'Old')
                    mainItem.setData(0, QtCore.Qt.UserRole + 3, "<span style='font-weight:bold;'>All entries from old category '{1}' will be shifted to the new '{0}'.</span>".format(categoryData[1], self.categoriesTable.item(i, 2).text()))  # info
                
                mainItem.setData(0, QtCore.Qt.UserRole + 1, i)  # category row number
                self.modelsTable.addTopLevelItem(mainItem)
                self.modelsTable.setFirstItemColumnSpanned(mainItem, True)
                
                categories[oldCategoryID] = mainItem
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
    
    def loadCategories(self):
        for i in range(self.categoriesTable.rowCount(), 0, -1):
            self.categoriesTable.removeRow(i - 1)
        ##
        self.tabs.setTabEnabled(1, True)
        
        for i in self.newDtabase.getElementsByTagName('categories')[0].getElementsByTagName('category'):
            rowNumber = self.categoriesTable.rowCount()
            self.categoriesTable.insertRow(rowNumber)
            ######
            widgetActive = QtGui.QCheckBox('')
            widgetActive.setStyleSheet('margin-left:18px;')
            self.categoriesTable.setCellWidget(rowNumber, 0, widgetActive)
            #
            itemID = QtGui.QTableWidgetItem(i.getAttribute("number"))
            self.categoriesTable.setItem(rowNumber, 1, itemID)
            #
            itemName = QtGui.QTableWidgetItem(i.getAttribute("name"))
            self.categoriesTable.setItem(rowNumber, 2, itemName)
            #
            try:
                cDescription = i.firstChild.data
            except:
                cDescription = ''
            
            itemDescription = QtGui.QTableWidgetItem(cDescription)
            self.categoriesTable.setItem(rowNumber, 3, itemDescription)
            # new category
            widgetAction = QtGui.QComboBox()
            widgetAction.addItem('New category', [-1, ''])  # new category
            #
            nr = 1
            for j, k in readCategories().items():
                widgetAction.addItem('Move all objects to existing category: {0}'.format(k[0]), [j, k[0]])
                if k[0] == i.getAttribute("name"):
                    widgetAction.setCurrentIndex(nr)
                nr += 1
            self.categoriesTable.setCellWidget(rowNumber, 4, widgetAction)
            
    def selectAllCategories(self):
        if self.categoriesTable.rowCount() > 0:
            for i in range(self.categoriesTable.rowCount()):
                self.categoriesTable.cellWidget(i, 0).setCheckState(QtCore.Qt.Checked)
            
    def unselectAllCategories(self):
        if self.categoriesTable.rowCount() > 0:
            for i in range(self.categoriesTable.rowCount()):
                self.categoriesTable.cellWidget(i, 0).setCheckState(QtCore.Qt.Unchecked)
            
    def chooseFile(self):
        newDatabase = QtGui.QFileDialog.getOpenFileName(None, u'Choose file to import', os.path.expanduser("~"), '*.fpcb')
        if newDatabase[0].strip() != '':
            self.filePath.setText(newDatabase[0])
            self.newDtabase = minidom.parse(newDatabase[0])
            #
            self.loadCategories()
    
    def selectAllModels(self):
        for i in QtGui.QTreeWidgetItemIterator(self.modelsTable):
            if i.value().data(0, QtCore.Qt.UserRole) == 'M':
                i.value().setCheckState(0, QtCore.Qt.Checked)
    
    def unselectAllModels(self):
        for i in QtGui.QTreeWidgetItemIterator(self.modelsTable):
            if i.value().data(0, QtCore.Qt.UserRole) == 'M':
                i.value().setCheckState(0, QtCore.Qt.Unchecked)


########################################################################
########################################################################
class convertSoftwareItems(QtGui.QDialog):
    def __init__(self, sql, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.sql = sql
        
        self.setWindowTitle(u'Convert items')
        #
        ########################
        ###### entries
        ########################
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
        self.categoriesTable.setStyleSheet('''QTableWidget{background-color:#fff; border:1px solid rgb(199, 199, 199);}''')
        self.categoriesTable.setColumnCount(11)
        self.categoriesTable.setGridStyle(QtCore.Qt.DashDotLine)
        self.categoriesTable.setHorizontalHeaderLabels([' Active ', 'ID', ' Package type ', ' Package name ', 'Category', ' X ', ' Y ', ' Z ', ' RX ', ' RY ', ' RZ '])
        self.categoriesTable.verticalHeader().hide()
        self.categoriesTable.horizontalHeader().setResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.categoriesTable.horizontalHeader().setStretchLastSection(True)
        self.categoriesTable.hideColumn(1)
        
        # software
        self.fromSoftware = QtGui.QComboBox()
        self.toSoftware = QtGui.QComboBox()
        
        searchItemsButton = QtGui.QPushButton('Find entries')
        self.connect(searchItemsButton, QtCore.SIGNAL("clicked()"), self.findEntries)
        
        softwareFrame = QtGui.QFrame()
        softwareFrame.setObjectName('lay_path_widget')
        softwareFrame.setStyleSheet('''#lay_path_widget {background-color:#fff; border:1px solid rgb(199, 199, 199); padding: 5px;}''')
        softwareLayout = QtGui.QHBoxLayout(softwareFrame)
        softwareLayout.addStretch(10)
        softwareLayout.addWidget(QtGui.QLabel(u'From:\t'))
        softwareLayout.addWidget(self.fromSoftware)
        softwareLayout.addSpacing(20)
        softwareLayout.addWidget(QtGui.QLabel(u'To:\t'))
        softwareLayout.addWidget(self.toSoftware)
        softwareLayout.addSpacing(40)
        softwareLayout.addWidget(searchItemsButton)
        softwareLayout.addStretch(10)
        softwareLayout.setContentsMargins(0, 0, 0, 0)
        
        # buttons
        buttons = QtGui.QDialogButtonBox()
        buttons.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
        buttons.addButton("Convert", QtGui.QDialogButtonBox.AcceptRole)
        self.connect(buttons, QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        self.connect(buttons, QtCore.SIGNAL("rejected()"), self, QtCore.SLOT("reject()"))
        
        buttonsFrame = QtGui.QFrame()
        buttonsFrame.setObjectName('lay_path_widget')
        buttonsFrame.setStyleSheet('''#lay_path_widget {background-color:#fff; border:1px solid rgb(199, 199, 199); padding: 5px;}''')
        buttonsLayout = QtGui.QHBoxLayout(buttonsFrame)
        buttonsLayout.addWidget(buttons)
        buttonsLayout.setContentsMargins(0, 0, 0, 0)
        
        # main layout
        layTableButtons = QtGui.QHBoxLayout()
        layTableButtons.addWidget(selectAll)
        layTableButtons.addWidget(unselectAll)
        layTableButtons.addStretch(10)
        
        lay = QtGui.QGridLayout(self)
        lay.addWidget(softwareFrame, 0, 0, 1, 1)
        lay.addLayout(layTableButtons, 1, 0, 1, 1)
        lay.addWidget(self.categoriesTable, 2, 0, 1, 1)
        lay.addWidget(buttonsFrame, 3, 0, 1, 1)
        lay.setRowStretch(2, 10)
        lay.setContentsMargins(5, 5, 5, 5)
        #
        self.connect(self.fromSoftware, QtCore.SIGNAL("currentIndexChanged (int)"), self.softwareToLoadCategories)
        self.loadCategories()
    
    def findEntries(self):
        for i in range(self.categoriesTable.rowCount(), 0, -1):
            self.categoriesTable.removeRow(i - 1)
        ##
        self.sql.reloadList()
        
        for i in self.sql.packages():
            dane = self.sql.getValues(i)
            
            software = eval(dane["soft"])
            for j in software:
                if j[1] == self.fromSoftware.currentText():
                    rowNumber = self.categoriesTable.rowCount()
                    self.categoriesTable.insertRow(rowNumber)
                    #
                    widgetActive = QtGui.QCheckBox('')
                    widgetActive.setStyleSheet('margin-left:18px;')
                    self.categoriesTable.setCellWidget(rowNumber, 0, widgetActive)
                    #
                    item0 = QtGui.QTableWidgetItem(i)
                    self.categoriesTable.setItem(rowNumber, 1, item0)
                    #
                    item1 = QtGui.QTableWidgetItem(dane["name"])
                    item1.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    self.categoriesTable.setItem(rowNumber, 2, item1)
                    #
                    item2 = QtGui.QTableWidgetItem(j[0])
                    self.categoriesTable.setItem(rowNumber, 3, item2)
                    #
                    itemCat = QtGui.QTableWidgetItem(readCategories()[int(dane['category'])][0])
                    itemCat.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    self.categoriesTable.setItem(rowNumber, 4, itemCat)
                    #
                    item3 = QtGui.QTableWidgetItem(str(j[2]))
                    item3.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.categoriesTable.setItem(rowNumber, 5, item3)
                    #
                    item4 = QtGui.QTableWidgetItem(str(j[3]))
                    item4.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.categoriesTable.setItem(rowNumber, 6, item4)
                    #
                    item5 = QtGui.QTableWidgetItem(str(j[4]))
                    item5.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.categoriesTable.setItem(rowNumber, 7, item5)
                    #
                    item6 = QtGui.QTableWidgetItem(str(j[5]))
                    item6.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.categoriesTable.setItem(rowNumber, 8, item6)
                    #
                    item7 = QtGui.QTableWidgetItem(str(j[6]))
                    item7.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.categoriesTable.setItem(rowNumber, 9, item7)
                    #
                    item8 = QtGui.QTableWidgetItem(str(j[7]))
                    item8.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.categoriesTable.setItem(rowNumber, 10, item8)
        
    def loadCategories(self):
        self.fromSoftware.clear()
        self.fromSoftware.addItems(defSoftware)
        self.fromSoftware.setCurrentIndex(0)
        #
        self.softwareToLoadCategories()
    
    def softwareToLoadCategories(self):
        self.toSoftware.clear()
        #
        for i in defSoftware:
            if i != self.fromSoftware.currentText():
                self.toSoftware.addItem(i)
        self.toSoftware.setCurrentIndex(0)
    
    def selectAllCategories(self):
        if self.categoriesTable.rowCount() > 0:
            for i in range(self.categoriesTable.rowCount()):
                self.categoriesTable.cellWidget(i, 0).setCheckState(QtCore.Qt.Checked)
            
    def unselectAllCategories(self):
        if self.categoriesTable.rowCount() > 0:
            for i in range(self.categoriesTable.rowCount()):
                self.categoriesTable.cellWidget(i, 0).setCheckState(QtCore.Qt.Unchecked)
