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
import os.path
import shutil
import configparser
import json
from PySide import QtCore, QtGui
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import reflection
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
import PCBcheckFreeCADVersion

import FreeCAD

__currentPath__ = os.path.abspath(os.path.join(os.path.dirname(__file__), ''))
Base = declarative_base()

class Categories(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    parentID = Column(Integer)
    description = Column(String)
    
    def __init__(self, name, parentID, description):
        self.name = name
        self.parentID = parentID
        self.description = description
    
    def __repr__(self):
        return "<Categories('%s','%s')>" % (self.name, self.description)
        

class Models(Base):
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    categoryID = Column(Integer)
    datasheet = Column(String)
    path3DModels = Column(String, nullable=False)
    isSocket = Column(Boolean)
    isSocketHeight = Column(Float)
    socketID = Column(Integer)
    socketIDSocket = Column(Boolean)

    def __init__(self, name, path3DModels, description='', categoryID=0, datasheet='', isSocket=False, isSocketHeight=0.0, socketID=0, socketIDSocket=False):
        self.name = name
        self.description = description
        self.categoryID = categoryID
        self.datasheet = datasheet
        self.path3DModels = path3DModels
        self.isSocket = isSocket
        self.isSocketHeight = isSocketHeight
        self.socketID = socketID
        self.socketIDSocket = socketIDSocket
    
    def __repr__(self):
        return "<Models('%s','%s')>" % (self.name, self.description)


class Packages(Base):
    __tablename__ = "packages"
    
    id = Column(Integer, primary_key=True)
    modelID = Column(Integer)
    name = Column(String, nullable=False)
    software = Column(String, nullable=False)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)
    rx = Column(Float)
    ry = Column(Float)
    rz = Column(Float)
    
    def __init__(self, modelID, name, software, x=0.0, y=0.0, z=0.0, rx=0.0, ry=0.0, rz=0.0):
        self.modelID = modelID
        self.name = name
        self.software = software
        self.x = x
        self.y = y
        self.z = z
        self.rx = rx
        self.ry = ry
        self.rz = rz
    
    def __repr__(self):
        return "<Packages('%s')>" % (self.name)


class dataBase_CFG():
    def __init__(self, parent=None):
        self.config = configparser.RawConfigParser()
        self.fileName = None
    
    def read(self, fileName):
        if fileName != "":
            #self.config = configparser.RawConfigParser()
            sciezka = os.path.dirname(fileName)
            if os.access(sciezka, os.R_OK) and os.access(sciezka, os.F_OK):
                self.fileName = fileName
                self.config.read(fileName)
                return True
            FreeCAD.Console.PrintWarning("Access Denied. The file '{0}' may not exist, or there could be permission problem.\n".format(fileName))
    
    def packages(self):
        return self.config.sections()
        
    def getValues(self, sectionName):
        dane = {}
        for i in self.config.items(sectionName):
            dane[i[0]] = i[1]
        return dane
    
    def readCategories(self):
        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("partsCategories", '').strip() != '':
            return {int(i):j for i, j in json.loads(FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("partsCategories", '')).items()}
        else:
            return {}


class dataBase:
    def __init__(self):
        self.session = None
    
    def checkVersion(self):
        if not PCBcheckFreeCADVersion.checkdataBaseVersion():
            return False
        else:
            return True
    
    def cfg2db(self):
        ''' convert from cfg to db format - local '''
        try:
            dataBaseCFG = dataBase_CFG()  # old cfg file
            dataBaseCFG.read(getFromSettings_databasePath().replace(".db", ".cfg"))
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR cfg2db 1: {0}.\n".format(self.errorsDescription(e)))
            return False
        else:
            FreeCAD.Console.PrintWarning("Reading old database\n")
        
        # converting categories
        categoriesList = dataBaseCFG.readCategories()
        for i, j in categoriesList.items():
            name = self.clearString(j[0])
            description = self.clearString(j[1])
            
            self.addCategory(name, 0, description)
        
        # converting models
        seketsList = []
        packagesList = dataBaseCFG.packages()
        
        for i in packagesList:
            data = dataBaseCFG.getValues(i)
            
            result = {}
            result["name"] = self.clearString(data["name"])
            result["datasheet"] = self.clearString(data["datasheet"])
            result["description"] = self.clearString(data["description"])
            result["path3DModels"] = self.clearString(data["path"])
            result["isSocket"] = eval(self.clearString(data["socket"]))[0]
            result["isSocketHeight"] = float(eval(self.clearString(data["socket"]))[1])
            result["socketIDSocket"] = eval(self.clearString(data["add_socket"]))[0]
            
            categoryID = int(data["category"])
            if categoryID in categoriesList.keys():
                if categoryID in [-1, 0]:
                    result["categoryID"] = 0
                else:
                    category = self.getCategoryByName(categoriesList[categoryID][0])
                    if category[0]:
                        result["categoryID"] = category[1].id
                    else:
                        result["categoryID"] = 0
            else:
                result["categoryID"] = 0
            
            if result["socketIDSocket"]:
                result["socketID"] = 0
                seketsList.append([result["name"], dataBaseCFG.getValues(result["socketIDSocket"])["name"]])
            else:
                result["socketID"] = 0
            
            # packages
            result["software"] = []
            for p in eval(data["soft"]):
                packageData = {}
                packageData['name'] = self.clearString(p[0])
                packageData['software'] = self.clearString(p[1])
                packageData['x'] = float(p[2])
                packageData['y'] = float(p[3])
                packageData['z'] = float(p[4])
                packageData['rx'] = float(p[5])
                packageData['ry'] = float(p[6])
                packageData['rz'] = float(p[7])
                packageData['blanked'] = False
                packageData['id'] = -1
                
                result["software"].append(packageData)
            
            self.addModel(result)
            
        for i in seketsList:
            socket = self.getModelByName(i[1])
            if socket[0]:
                self.session.query(Models).filter(Models.name == i[0]).update({"socketID" : socket[1].id})
        
        self.session.commit()
        FreeCAD.Console.PrintWarning("DONE!.\n")
        
        # database file update - position/name
        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("databasePath", "").strip() != '':
            database = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("databasePath", "").strip()
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").SetString('databasePath', database.replace('cfg', 'db'))
            
        try:
            data = getFromSettings_databasePath()
            shutil.move(data.replace(".db", ".cfg"), data.replace(".db", ".cfg") + "_old")
        except Exception as e:
            pass
        
        ## deleting old categories
        #if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("partsCategories", '').strip() != '':
            #FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").SetString('partsCategories', json.dumps(""))
        
        FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").SetFloat("Version", __dataBaseVersion__)
        return True
        
    def connect(self, newPath=False):
        ''' '''
        try:
            if newPath:
                engine = create_engine('sqlite:///{0}'.format(newPath))
            else:
                from PCBfunctions import getFromSettings_databasePath
                
                engine = create_engine('sqlite:///{0}'.format(getFromSettings_databasePath()))  # relative path
            Base.metadata.create_all(engine)
            Session = sessionmaker(bind=engine)
            self.session = Session()
            
            if not newPath and not self.checkVersion():
                self.cfg2db()
            
            FreeCAD.Console.PrintWarning("Read database\n")
        except Exception as e:
            return False
        return True
    
    def clearString(self, value, errors="replace"):
        ''' @Jeremy Banks http://stackoverflow.com/questions/6514274/how-do-you-escape-strings-for-sqlite-table-column-names-in-python '''
        encodable = value.encode("utf-8", errors).decode("utf-8")
        nul_index = encodable.find("\x00")

        if nul_index >= 0:
            error = UnicodeEncodeError("NUL-terminated utf-8", encodable,
                                       nul_index, nul_index + 1, "NUL not allowed")
            error_handler = codecs.lookup_error(errors)
            replacement, _ = error_handler(error)
            encodable = encodable.replace("\x00", replacement)

        #return "\"" + encodable.replace("\"", "\"\"") + "\""
        return encodable.strip()
    
    def errorsDescription(self, error):
        if "IntegrityError" in str(error):
            return 'UNIQUE constraint failed.'
        elif "OperationalError" in str(error):
            return 'Database is locked.'
        elif "MandatoryError" in str(error):
            return "One of the mandatory fields is empty!"
        elif "ConvertError()" in str(error):
            return "Problems with converting database"
        else:
            return error.message
    
    def convertToTable(self, data):
        result = {}
        
        for i, j in data.__dict__.items():
            if not i.startswith("_sa_"):
                result[i] = j
        return result
        
    def findPackage(self, name, software, returnAll=False):
        try:
            name = self.clearString(name).strip()
            software = self.clearString(software).strip()
            
            if software == "*":
                query = self.session.query(Packages).filter(Packages.name == name)
            else:
                query = self.session.query(Packages).filter(Packages.name == name and Packages.software == software)
                
            if query.count() == 0:
                return False
            
            if returnAll:
                return query
            else:
                return query[0]
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR: {0} (findPackage).\n".format(self.errorsDescription(e)))
            return False
            
    def packagesDataToDictionary(self, modelData):
        modelData['software'] = []
        
        for i in self.getPackagesByModelID(modelData['id']):
            modelData['software'].append(self.convertToTable(i))
        
        return modelData
    
    def getPackageByID(self, param):
        if param <= 0:
            return False
        
        query = self.session.query(Packages).filter(Packages.id == int(param))
        
        if query.count() == 0:
            FreeCAD.Console.PrintWarning("ERROR: {0} (get package).\n".format(self.errorsDescription(e)))
            return False
            
        return query[0]
        
    def getPackagesByModelID(self, param):
        try:
            query = self.session.query(Packages).filter(Packages.modelID == int(param))
            
            if query.count() == 0:
                return []
            
            return query
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR: {0} (get package).\n".format(self.errorsDescription(e)))
            return []

    def addPackage(self, data, modelID=0, modelName=0):
        try:
            if modelID != 0:
                modelID = int(modelID)
            elif modelName != 0:
                modelID = self.getModelByName(self.clearString(modelName))[1].id
            else:
                return [False]
            
            name = self.clearString(data['name'])
            software = self.clearString(data['software'])
            x = float(data['x'])
            y = float(data['y'])
            z = float(data['z'])
            rx = float(data['rx'])
            ry = float(data['ry'])
            rz = float(data['rz'])
            
            package = Packages(modelID, name, software, x, y, z, rx, ry, rz)
            self.session.add(package)
            self.session.commit()
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR: {0} (add package).\n".format(e))
            return [False]
        
    def updatePackage(self, packageID, data):
        try:
            packageID = int(packageID)
            name = self.clearString(data["name"])
            software = self.clearString(data["software"])
            
            if name == '' or software == '' or packageID <= 0:
                raise MandatoryError()
            
            self.session.query(Packages).filter(Packages.id == packageID).update({
                    "name": name,
                    "software": software,
                    "x": float(data["x"]),
                    "y": float(data["y"]),
                    "z": float(data["z"]),
                    "rx": float(data["rx"]),
                    "ry": float(data["ry"]),
                    "rz": float(data["rz"])
             })
             
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            FreeCAD.Console.PrintWarning("ERROR: {0} (update package).\n".format(self.errorsDescription(e)))
            return False
        
    def deletePackage(self, packageID):
        try:
            self.session.query(Packages).filter(Packages.id == int(packageID)).delete()
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            FreeCAD.Console.PrintWarning("ERROR: {0} (delete package).\n".format(self.errorsDescription(e)))
            return False
        else:
            return True
            
    def getAllSockets(self):
        try:
            query = self.session.query(Models).filter(Models.isSocket == 1)
            if query.count() == 0:
                return []
            
            return query
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR: {0} (get all sockets).\n".format(self.errorsDescription(e)))
            return []
    
    def getAllModels(self):
        return self.session.query(Models)

    def getAllModelsByCategory(self, categoryID):
        return self.session.query(Models).filter(Models.categoryID == categoryID)
    
    def getModelByID(self, param):
        try:
            query = self.session.query(Models).filter(Models.id == int(param))
            if query.count() == 0:
                return [False]
            
            return [True, query[0]]
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR: {0} (get model).\n".format(self.errorsDescription(e)))
            return [False]

    def getModelByName(self, param):
        try:
            query = self.session.query(Models).filter(Models.name == self.clearString(param))
            if query.count() == 0:
                return [False]
            
            return [True, query[0]]
            
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR: {0} (get model).\n".format(self.errorsDescription(e)))
            return [False]
    
    def deleteModel(self, modelID):
        try:
            modelID = int(modelID)
            
            self.session.query(Models).filter(Models.socketID == modelID).update({"socketID" : 0, "socketIDSocket" : False})
            self.session.query(Packages).filter(Packages.modelID == modelID).delete()
            self.session.query(Models).filter(Models.id == modelID).delete()
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            FreeCAD.Console.PrintWarning("ERROR: {0} (delete model).\n".format(self.errorsDescription(e)))
            return False
        else:
            FreeCAD.Console.PrintWarning("Model was deleted.\n")
            return True
    
    def addModel(self, data):
        try:
            name = self.clearString(data["name"])
            description = self.clearString(data["description"])
            categoryID = int(data["categoryID"])
            datasheet = self.clearString(data["datasheet"])
            path3DModels = self.clearString(data["path3DModels"])
            isSocket = data["isSocket"]
            isSocketHeight = float(data["isSocketHeight"])

            try:
                socketID = int(data["socketID"])
            except:
                socketID = 0
                
            socketIDSocket = data["socketIDSocket"]
            
            if name == '' or path3DModels == '':
                raise MandatoryError()

            model = Models(name, path3DModels, description, categoryID, datasheet, isSocket, isSocketHeight, socketID, socketIDSocket)
            self.session.add(model)
            self.session.commit()
            
            for i in data["software"]:
                if i['blanked']:
                    continue
                else: # add new package
                    self.addPackage(i, modelName=name)
                
                #if i['blanked']:
                    #if int(i['id']) == -1:
                        #continue
                    #else:  # del package
                        #continue
                        ## self.deletePackage(int(i['id']))
                #else:
                    #if int(i['id']) != -1:  # update package
                        #self.updatePackage(int(i['id']), i)
                    #else:  # add package
                        #self.addPackage(i, modelName=name)
            
        except Exception as e:
            self.session.rollback()
            FreeCAD.Console.PrintWarning("ERROR: {0} (add new model).\n".format(self.errorsDescription(e)))
            return False
        else:
            FreeCAD.Console.PrintWarning("Model {0} was added.\n".format(name))
            return True
    
    def setCategoryForModel(self, modelID, categoryID):
        try:
            modelID = int(modelID)
            
            if modelID <= 0:
                raise MandatoryError()
                
            self.session.query(Models).filter(Models.id == modelID).update({
                    "categoryID" : int(categoryID)
            })
            self.session.commit()
            
        except Exception as e:
            self.session.rollback()
            FreeCAD.Console.PrintWarning("ERROR: {0} (update model).\n".format(self.errorsDescription(e)))
            return False
        else:
            return True
    
    def updateModel(self, modelID, data):
        try:
            name = self.clearString(data["name"])
            path3DModels = self.clearString(data["path3DModels"])
            modelID = int(modelID)

            try:
                socketID = int(data["socketID"])
            except:
                socketID = 0
            
            if name == '' or path3DModels == '' or modelID <= 0:
                raise MandatoryError()
            
            self.session.query(Models).filter(Models.id == modelID).update({
                    "name": name,
                    "description" : self.clearString(data["description"]),
                    "categoryID" : int(data["categoryID"]),
                    "datasheet": self.clearString(data["datasheet"]),
                    "path3DModels" : path3DModels,
                    "isSocket" : data["isSocket"],
                    "isSocketHeight" : float(data["isSocketHeight"]),
                    "socketID" : socketID,
                    "socketIDSocket" : data["socketIDSocket"]
            })
            
            self.session.commit()
            
            for i in data["software"]:
                if i['blanked']:
                    if int(i['id']) == -1:
                        continue
                    else:  # del package
                        self.deletePackage(int(i['id']))
                else:
                    if int(i['id']) != -1:  # update package
                        self.updatePackage(int(i['id']), i)
                    else:  # add package
                        self.addPackage(i, modelID=modelID)
            
        except Exception as e:
            self.session.rollback()
            FreeCAD.Console.PrintWarning("ERROR: {0} (update model).\n".format(self.errorsDescription(e)))
            return False
        else:
            FreeCAD.Console.PrintWarning("Model {0} was updated.\n".format(name))
            return True
    
    def getCategoryByName(self, param):
        try:
            query = self.session.query(Categories).filter(Categories.name == self.clearString(param))
            if query.count() == 0:
                return [False]
            
            return [True, query[0]]
            
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR: {0} (get category).\n".format(self.errorsDescription(e)))
            return [False]
    
    def getCategoryByID(self, catID=0):
        if catID <= 0:
            return False
        
        query = self.session.query(Categories).filter(Categories.id == int(catID))
        
        if query.count() == 0:
            FreeCAD.Console.PrintWarning("ERROR: Category does not exist.\n")
            return False
        
        return query[0]
        
    def getAllcategoriesWithSubCat(self, catID=0):
        categories = {}
    
        for i in self.session.query(Categories).filter(Categories.parentID == catID):
            categories[i.name] = {}
            categories[i.name]['id'] = i.id
            categories[i.name]['description'] = i.description
            
            categories[i.name]['sub'] = self.getAllcategoriesWithSubCat(i.id)
            
        return categories
                
    def getAllcategories(self):
        return self.session.query(Categories)
    
    def deleteCategory(self, categoryID):
        ''' '''
        try:
            categoryID = int(categoryID)
            
            categoryData = self.getCategoryByID(categoryID)
            parentID = categoryData.parentID
            
            self.session.query(Categories).filter(Categories.parentID == categoryID).update({"parentID" : parentID})
            self.session.query(Models).filter(Models.categoryID == categoryID).update({"categoryID" : parentID})
            
            self.session.query(Categories).filter(Categories.id == categoryID).delete()
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            FreeCAD.Console.PrintWarning("ERROR: {0} (delete category).\n".format(self.errorsDescription(e)))
            return False
        else:
            FreeCAD.Console.PrintWarning("Category {0} was deleted.\n".format(categoryData.name))
            return True
        
    def updateCategory(self, categoryID, name, parentID, description):
        ''' '''
        try:
            categoryID = int(categoryID)
            name = self.clearString(name)
            if parentID == -1 or parentID == None:
                parentID = 0
            parentID = int(parentID)
            description = self.clearString(description)
            
            if name == '' or categoryID <= 0:
                raise MandatoryError()
            
            self.session.query(Categories).filter(Categories.id == categoryID).update({"name": name, "parentID" : parentID, "description" : description})
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            FreeCAD.Console.PrintWarning("ERROR: {0} (update category).\n".format(self.errorsDescription(e)))
            return False
        else:
            FreeCAD.Console.PrintWarning("Category {0} was updated.\n".format(name))
            return True
        
    def addCategory(self, name, parentID, description):
        ''' '''
        try:
            name = self.clearString(name)
            if parentID == -1 or parentID == None:
                parentID = 0
            parentID = int(parentID)
            description = self.clearString(description)
            
            if name == '':
                raise MandatoryError()
            
            categories = Categories(name, parentID, description)
            self.session.add(categories)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            FreeCAD.Console.PrintWarning("ERROR: {0} (add new category).\n".format(self.errorsDescription(e)))
            return False
        else:
            FreeCAD.Console.PrintWarning("Category {0} was added.\n".format(name))
            return True



#class dataBase:
    #def __init__(self, parent=None):
        #self.config = configparser.RawConfigParser()
        #self.fileName = None
    
    #def convertDatabaseEntries(self):
        #dial = convertSoftwareItems(self)
        #if dial.exec_():
            #soft = dial.toSoftware.currentText()
            
            #for i in range(dial.categoriesTable.rowCount()):
                #if dial.categoriesTable.cellWidget(i, 0).isChecked():
                    #try:
                        #sectionID = dial.categoriesTable.item(i, 1).text()
                        #name = dial.categoriesTable.item(i, 3).text()
                        #try:
                            #x = float(dial.categoriesTable.item(i, 5).text())
                        #except ValueError:
                            #x = 0.0
                        #try:
                            #y = float(dial.categoriesTable.item(i, 6).text())
                        #except ValueError:
                            #y = 0.0
                        #try:
                            #z = float(dial.categoriesTable.item(i, 7).text())
                        #except ValueError:
                            #z = 0.0  
                        #try:
                            #rx = float(dial.categoriesTable.item(i, 8).text())
                        #except ValueError:
                            #rx = 0.0
                        #try:
                            #ry = float(dial.categoriesTable.item(i, 9).text())
                        #except ValueError:
                            #ry = 0.0
                        #try:
                            #rz = float(dial.categoriesTable.item(i, 10).text())
                        #except ValueError:
                            #rz = 0.0
                        ##
                        #softsList = eval(self.getValues(sectionID)['soft'])
                        
                        #if not [name, soft, x, y, z, rx, ry, rz] in softsList:
                            #connections = [[name, soft, x, y, z, rx, ry, rz]]
                         
                            #dane = {'soft': connections + softsList}
                            #self.updatePackage(sectionID, dane)
                    #except:
                        #continue
            ##
            #return True
        
    #def read(self, fileName):
        #if fileName != "":
            ##self.config = configparser.RawConfigParser()
            #sciezka = os.path.dirname(fileName)
            #if os.access(sciezka, os.R_OK) and os.access(sciezka, os.F_OK):
                #self.fileName = fileName
                #self.config.read(fileName)
                #return True
            #FreeCAD.Console.PrintWarning("Access Denied. The file '{0}' may not exist, or there could be permission problem.\n".format(fileName))
            
    #def create(self, fileName):
        #plik = builtins.open(fileName, "w")
        #plik.close()
        #self.fileName = fileName
        ##self.config = configparser.RawConfigParser()
        #self.config.read(fileName)
        
    #def write(self):
        #if os.access(os.path.dirname(self.fileName), os.W_OK):
            #with open(self.fileName, 'wb') as configfile:
                #self.config.write(configfile)
            #return True
        #FreeCAD.Console.PrintWarning("Access Denied. The file '{0}' may not exist, or there could be permission problem.\n".format(self.fileName))

    #def has_section(self, name):
        #return self.config.has_section(str(name))
        
    #def findPackage(self, package, soft):
        #for i in self.packages():
            #for j in eval(self.getValues(i)["soft"]):
                #if soft == '*':
                    #if package.lower()+"'" in str(j).lower():
                        #return [True, i, j, int(self.getValues(i)['category'])]
                #else:
                    #if str(soft) in j and package.lower()+"'" in str(j).lower():
                        #return [True, i, j, int(self.getValues(i)['category'])]
        #return [False]
        
    #def has_value(self, valueName, txt):
        #for i in self.packages():
            #if self.config.get(i, valueName) == txt:
                #return [True, i]
        #return [False]
            
    #def getValues(self, sectionName):
        #dane = {}
        #for i in self.config.items(sectionName):
            #dane[i[0]] = i[1]
        #return dane
        
    #def reloadList(self):
        #self.read(self.fileName)
            
    #def delPackage(self, name):
        #self.config.remove_section(name)
        #self.write()
    
    #def updateValue(self, sectionName, txt, value):
        #self.config.set(sectionName, txt, value)
        
    #def updatePackage(self, sectionName, dane):
        #for i, j in dane.items():
            #self.config.set(sectionName, i, j)
        ##self.config.set(sectionName, 'name', dane["name"])
        ##self.config.set(sectionName, 'path', dane["path"])
        ##self.config.set(sectionName, 'x', dane["x"])
        ##self.config.set(sectionName, 'y', dane["y"])
        ##self.config.set(sectionName, 'z', dane["z"])
        ##self.config.set(sectionName, 'rx', dane["rx"])
        ##self.config.set(sectionName, 'ry', dane["ry"])
        ##self.config.set(sectionName, 'rz', dane["rz"])
        ##self.config.set(sectionName, 'add_socket', dane["add_socket"])
        ##self.config.set(sectionName, 'add_socket_id', dane["add_socket_id"])
        ##self.config.set(sectionName, 'socket', dane["socket"])
        ##self.config.set(sectionName, 'socket_height', dane["socket_height"])
        ##self.config.set(sectionName, 'description', dane["description"])
        ##self.config.set(sectionName, 'datasheet', dane["datasheet"])
        #self.write()
        
    #def wygenerujID(self, ll, lc):
        #''' generate random section name '''
        #numerID = ""
    
        #for i in range(ll):
            #numerID += random.choice('abcdefghij')
        #numerID += "_"
        #for i in range(lc):
            #numerID += str(random.randrange(0, 99, 1))
        
        #if not self.has_section(numerID):
            #return numerID
        #else:
            #return self.wygenerujID(ll, lc)
            
    #def addPackage(self, dane):
        #sectionName = self.wygenerujID(5, 5)
        
        #self.config.add_section(sectionName)
        #for i, j in dane.items():
            #self.config.set(sectionName, i, j)
        ##self.config.set(sectionName, 'name', dane["name"])
        ##self.config.set(sectionName, 'path', dane["path"])
        ##self.config.set(sectionName, 'x', dane["x"])
        ##self.config.set(sectionName, 'y', dane["y"])
        ##self.config.set(sectionName, 'z', dane["z"])
        ##self.config.set(sectionName, 'rx', dane["rx"])
        ##self.config.set(sectionName, 'ry', dane["ry"])
        ##self.config.set(sectionName, 'rz', dane["rz"])
        ##self.config.set(sectionName, 'add_socket', dane["add_socket"])
        ##self.config.set(sectionName, 'add_socket_id', dane["add_socket_id"])
        ##self.config.set(sectionName, 'socket', dane["socket"])
        ##self.config.set(sectionName, 'socket_height', dane["socket_height"])
        ##self.config.set(sectionName, 'description', dane["description"])
        ##self.config.set(sectionName, 'datasheet', dane["datasheet"])
        #self.write()
            
    #def packages(self):
        #return self.config.sections()
    
    #def makeACopy(self):
        #try:
            #newFolder = QtGui.QFileDialog.getExistingDirectory(None, 'Save database copy', os.path.expanduser("~"))
            #if newFolder:
                #try:
                    #xml = minidom.Document()
                    #root = xml.createElement("pcb")
                    #xml.appendChild(root)
                    
                    ## categories
                    #categories = xml.createElement("categories")
                    #root.appendChild(categories)

                    #for i,j in readCategories().items():
                        #category = xml.createElement("category")
                        #category.setAttribute('number', str(i))
                        #category.setAttribute('name', str(j[0]))
                        ##
                        #description = xml.createTextNode(str(j[1]))
                        #category.appendChild(description)
                        ##
                        #categories.appendChild(category)
                    ## models
                    #models = xml.createElement("models")
                    #root.appendChild(models)
                    
                    #for i in self.packages():
                        #dane = self.getValues(i)
                        
                        #model = xml.createElement("model")
                        #model.setAttribute('ID', str(i))
                        #model.setAttribute('name', str(dane['name']))
                        #model.setAttribute('category', str(dane['category']))
                        #model.setAttribute('datasheet', str(dane['datasheet']))
                        #model.setAttribute('isSocket', str(eval(dane['socket'])[0]))
                        #model.setAttribute('height', str(eval(dane['socket'])[1]))
                        #model.setAttribute('socket', str(eval(dane['add_socket'])[0]))
                        #model.setAttribute('socketID', str(eval(dane['add_socket'])[1]))
                        ##
                        #description = xml.createElement("description")
                        #model.appendChild(description)
                        
                        #descriptionTXT = xml.createTextNode(str(dane['description']))
                        #description.appendChild(descriptionTXT)
                        ##
                        #paths = xml.createElement("paths")
                        #model.appendChild(paths)
                        
                        #for j in dane['path'].split(';'):
                            #path = xml.createElement("path")
                            
                            #description = xml.createTextNode(str(j))
                            #path.appendChild(description)
                            ##
                            #paths.appendChild(path)
                        ##
                        #connections = xml.createElement("connections")
                        #model.appendChild(connections)
                        
                        #for j in eval(dane['soft']):
                            #item = xml.createElement("item")
                            #item.setAttribute('name', str(j[0]))
                            #item.setAttribute('soft', str(j[1]))
                            #item.setAttribute('x', str(j[2]))
                            #item.setAttribute('y', str(j[3]))
                            #item.setAttribute('z', str(j[4]))
                            #item.setAttribute('rx', str(j[5]))
                            #item.setAttribute('ry', str(j[6]))
                            #item.setAttribute('rz', str(j[7]))
                            ##
                            #connections.appendChild(item)
                        ##
                        #adjust = xml.createElement("adjust")
                        #model.appendChild(adjust)
                        
                        #try:
                            #for i, j in eval(str(dane["adjust"])).items():
                                #item = xml.createElement("item")
                                #item.setAttribute('parameter', str(i))
                                
                                #item.setAttribute('active', str(j[0]))
                                #item.setAttribute('visible', str(j[1]))
                                #item.setAttribute('x', str(j[2]))
                                #item.setAttribute('y', str(j[3]))
                                #item.setAttribute('z', str(j[4]))
                                #item.setAttribute('size', str(j[5]))
                                #item.setAttribute('align', str(j[7]))
                                ##
                                #color = xml.createElement("color")
                                #color.setAttribute('R', str(j[6][0]))
                                #color.setAttribute('G', str(j[6][1]))
                                #color.setAttribute('B', str(j[6][2]))
                                ###
                                #item.appendChild(color)
                                ##
                                #adjust.appendChild(item)
                        #except:
                            #pass
                        ##
                        #models.appendChild(model)
                    
                    ## write to file
                    #outputFile = builtins.open(os.path.join(newFolder, 'freecad-pcb_copy.fpcb'), 'w')
                    #xml.writexml(outputFile)
                    #outputFile.close()
                #except Exception as e:
                    #FreeCAD.Console.PrintWarning(u"{0} \n".format(e))
        #except Exception as e:
            #FreeCAD.Console.PrintWarning(u"{0} \n".format(e))
    
    #def readFromXML(self):
        #try:
            #dial = readDatabaseFromXML_GUI(self)
            #if dial.exec_():
                #for i in QtGui.QTreeWidgetItemIterator(dial.modelsTable):
                    #if str(i.value().data(0, QtCore.Qt.UserRole)) != 'PM':
                        #continue
                
                    #mainItem = i.value()
                    ## items
                    #connections = []
                    #checked = 0
                    #for j in range(mainItem.childCount()):
                        #if mainItem.child(j).checkState(0) == QtCore.Qt.Checked:
                            #child = mainItem.child(j).data(0, QtCore.Qt.UserRole + 2)
                            ## <item name="1X08" rx="90.0" ry="0.0" rz="0.0" soft="Eagle" x="0.0" y="0.0" z="2.77"/>
                            #name = child.getAttribute("name")
                            #soft = child.getAttribute("soft")
                            #x = float(child.getAttribute("x"))
                            #y = float(child.getAttribute("y"))
                            #z = float(child.getAttribute("z"))
                            #rx = float(child.getAttribute("rx"))
                            #ry = float(child.getAttribute("ry"))
                            #rz = float(child.getAttribute("rz"))
                            ##
                            #connections.append([name, soft, x, y, z, rx, ry, rz])
                            #checked += 1
                    
                    #if checked == 0:
                        #continue
                    ##
                    #if mainItem.data(0, QtCore.Qt.UserRole + 4) == 'new': # new entry
                        #topLevelItem = mainItem.parent()
                        #modelXML = mainItem.data(0, QtCore.Qt.UserRole + 2)
                        ##
                        #if topLevelItem.data(0, QtCore.Qt.UserRole) == -1:  # models without category
                            #modelCategory = -1
                        #elif topLevelItem.data(0, QtCore.Qt.UserRole) == 'New':  # new category
                            #rowNum = topLevelItem.data(0, QtCore.Qt.UserRole + 1)
                        
                            #categoryName = dial.categoriesTable.item(rowNum, 2).text()
                            #categoryDescription = dial.categoriesTable.item(rowNum, 3).text()
                            ##
                            #modelCategory = getCategoryIdByName(categoryName)
                            #if modelCategory == -1:
                                #addCategory(categoryName, categoryDescription)
                                #modelCategory = getCategoryIdByName(categoryName)
                        #elif topLevelItem.data(0, QtCore.Qt.UserRole) == 'Old':  # add models to existing category
                            #rowNum = topLevelItem.data(0, QtCore.Qt.UserRole + 1)
                            #modelCategory = int(dial.categoriesTable.cellWidget(rowNum, 4).itemData(dial.categoriesTable.cellWidget(rowNum, 4).currentIndex())[0])
                        ##
                        #modelPaths = []
                        #for j in modelXML.getElementsByTagName('paths')[0].getElementsByTagName('path'):
                            #try:
                                #modelPaths.append(j.firstChild.data)
                            #except AttributeError:
                                #pass
                        #modelPaths = '; '.join(modelPaths)
                        ##
                        #try:
                            #modelDescription = modelXML.getElementsByTagName('description')[0].firstChild.data
                        #except AttributeError:
                            #modelDescription = ''
                        ##
                        ##
                        #adjust = {}
                        #for j in modelXML.getElementsByTagName('adjust')[0].getElementsByTagName('item'):
                            #parameter = str(j.getAttribute('parameter')).strip()
                            #active = j.getAttribute('active')
                            #visible = str(j.getAttribute('visible'))
                            #x = float(j.getAttribute('x'))
                            #y = float(j.getAttribute('y'))
                            #z = float(j.getAttribute('z'))
                            #size = float(j.getAttribute('size'))
                            #align = str(j.getAttribute('align')).strip()
                            ##
                            #colors = j.getElementsByTagName('color')[0]
                            #color = {float(colors.getAttribute('R')), float(colors.getAttribute('G')), float(colors.getAttribute('B'))}
                            ##
                            #adjust[parameter] = [active, visible, x, y, z, size, color, align]
                        ##
                        #self.addPackage({
                            #"name": str(modelXML.getAttribute('name').strip()),
                            #"path": modelPaths,
                            #"add_socket": str([False, False]),
                            #"socket": str([eval(modelXML.getAttribute('isSocket')), float(modelXML.getAttribute('height'))]),
                            #"description": str(modelDescription),
                            #"datasheet": str(modelXML.getAttribute('datasheet').strip()),
                            #"soft": str(connections),
                            #"category": str(modelCategory),
                            #"adjust": str(adjust)
                        #})
                    #else:
                        #sectionID = mainItem.data(0, QtCore.Qt.UserRole + 4)
                        
                        #dane = {'soft': connections + eval(self.getValues(sectionID)['soft'])}
                        #self.updatePackage(sectionID, dane)
                
                #return True
        #except Exception as e:
            #FreeCAD.Console.PrintWarning("{0} \n".format(e))
        
        #return False









