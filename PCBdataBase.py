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
import os.path
import shutil
import copy
try:
    import configparser
except:
    import ConfigParser as configparser
import FreeCAD
from PySide import QtGui
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Float
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import reflection
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref
import PCBcheckFreeCADVersion

__currentPath__ = os.path.abspath(os.path.join(os.path.dirname(__file__), ''))
Base = declarative_base()


class modelsParam(Base):
    __tablename__ = "modelsParam"
    #
    id = Column(Integer, primary_key=True)
    modelID = Column(Integer)
    name = Column(String)
    active = Column(Boolean)
    display = Column(Boolean)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)
    rz = Column(Float)
    size = Column(Float)
    color = Column(String)
    align = Column(String)
    spin = Column(Boolean)

    def __init__(self, modelID, name, color, align, active=True, display=True, x=0.0, y=0.0, z=0.0, rz=0.0, size=1.27, spin=False):
        self.modelID = modelID
        self.name = name
        self.active = active
        self.display = display
        self.x = x
        self.y = y
        self.z = z
        self.rz = rz
        self.size = size
        self.color = color
        self.align = align
        self.spin = spin

    def __repr__(self):
        return "<modelsParam('%s')>" % (name)


class Categories(Base):
    __tablename__ = "categories"
    #
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
    #
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
    #
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
            # self.config = configparser.RawConfigParser()
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
        import json
        #
        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("partsCategories", '').strip() != '':
            return {int(i): j for i, j in json.loads(FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("partsCategories", '')).items()}
        else:
            return {}


class dataBase:
    def __init__(self):
        self.session = None
        self.lastInsertedID = None
        self.lastInsertedModelID = None

    def cfg2db(self, databasePath):
        ''' convert from cfg to db format - local '''
        try:
            dataBaseCFG = dataBase_CFG()  # old cfg file
            dataBaseCFG.read(databasePath)
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR cfg2db 1: {0}.\n".format(self.errorsDescription(e)))
            return False
        else:
            FreeCAD.Console.PrintWarning("Reading old database\n")
        try:
            # converting categories
            categoriesList = dataBaseCFG.readCategories()
            if len(categoriesList.keys()):
                for i, j in categoriesList.items():
                    name = self.clearString(j[0])
                    description = self.clearString(j[1])
                    self.addCategory(name, 0, description)
            # converting models
            seketsList = []
            packagesList = dataBaseCFG.packages()
            #
            for i in packagesList:
                data = dataBaseCFG.getValues(i)
                #
                result = {}
                result["name"] = self.clearString(data["name"])
                result["datasheet"] = self.clearString(data["datasheet"])
                result["description"] = self.clearString(data["description"])
                result["path3DModels"] = self.clearString(data["path"])
                result["isSocket"] = eval(self.clearString(data["socket"]))[0]
                result["isSocketHeight"] = float(eval(self.clearString(data["socket"]))[1])
                result["socketIDSocket"] = eval(self.clearString(data["add_socket"]))[0]
                #
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
                #
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
                    #
                    result["software"].append(packageData)
                #
                self.addModel(result)
            #
            for i in seketsList:
                socket = self.getModelByName(i[1])
                if socket[0]:
                    self.session.query(Models).filter(Models.name == i[0]).update({"socketID": socket[1].id})
            #
            self.session.commit()
            FreeCAD.Console.PrintWarning("DONE!.\n")
            #
            # database file update - position/name
            if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("databasePath", "").strip() != '':
                database = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("databasePath", "").strip()
                FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").SetString('databasePath', database.replace('.cfg', '.db'))
            try:
                shutil.move(databasePath.replace(".db", ".cfg"), databasePath.replace(".db", ".cfg") + "_old")
            except Exception as e:
                pass
            #
            # deleting old categories
            # if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("partsCategories", '').strip() != '':
                # FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").SetString('partsCategories', json.dumps(""))
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").SetFloat("Version", PCBcheckFreeCADVersion.__dataBaseVersion__)
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").SetFloat("Version", PCBcheckFreeCADVersion.__dataBaseVersion__)
            return True
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR 3: {0}.\n".format(e))

    def checkVersion(self):
        if not PCBcheckFreeCADVersion.checkdataBaseVersion():
            return False
        else:
            return True

    def connect(self, newPath=False):
        ''' '''
        try:
            from PCBfunctions import getFromSettings_databasePath
            databasePath = getFromSettings_databasePath()
            #
            if newPath:
                engine = create_engine('sqlite:///{0}'.format(newPath))
            else:
                engine = create_engine('sqlite:///{0}'.format(getFromSettings_databasePath().replace('cfg', 'db')))  # relative path
            #
            Base.metadata.create_all(engine)
            Session = sessionmaker(bind=engine)
            self.session = Session()
            self.connection = engine.connect()
            #
            if databasePath.endswith(".cfg"):
                dial = QtGui.QMessageBox()
                dial.setText(u"Old database format detected - upgrading database format is required. This may take several seconds.")
                dial.setWindowTitle("Caution!")
                dial.setIcon(QtGui.QMessageBox.Question)
                rewT = dial.addButton('Ok', QtGui.QMessageBox.YesRole)
                dial.exec_()
                #
                self.cfg2db(databasePath)
            #
            self.packagesChangeSoftware("IDF v3", "IDF")
            #
            FreeCAD.Console.PrintWarning("Read database\n")
        except Exception as e:
            return False
        return True

    def packagesChangeSoftware(self, dataFrom, dataTo):
        try:
            dataFrom = self.clearString(dataFrom)
            dataTo = self.clearString(dataTo)
            #
            query = self.session.query(Packages).filter(Packages.software == dataFrom)
            if query.count():
                data = []
                for i in query:
                    data.append(self.convertToTable(i))
                #
                for i in data:
                    i["software"] = dataTo
                    self.updatePackage(i["id"], i)
        except Exception as e:
            print(e)

    def clearString(self, value, errors="replace"):
        ''' @Jeremy Banks http://stackoverflow.com/questions/6514274/how-do-you-escape-strings-for-sqlite-table-column-names-in-python '''
        encodable = value.encode("utf-8", errors).decode("utf-8")
        nul_index = encodable.find("\x00")
        #
        if nul_index >= 0:
            error = UnicodeEncodeError("NUL-terminated utf-8", encodable,
                                       nul_index, nul_index + 1, "NUL not allowed")
            error_handler = codecs.lookup_error(errors)
            replacement, _ = error_handler(error)
            encodable = encodable.replace("\x00", replacement)

        # return "\"" + encodable.replace("\"", "\"\"") + "\""
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
            if hasattr(error, 'message'):
                return error.message
            else:
                return error

    def convertToTable(self, data):
        result = {}
        #
        for i, j in data.__dict__.items():
            if not i.startswith("_sa_"):
                result[i] = j
        return result

    def findPackage(self, name, software, returnAll=False):
        try:
            name = self.clearString(name).strip()
            software = self.clearString(software).strip()
            #
            if software == "*":
                query = self.session.query(Packages).filter(Packages.name == name)
            else:
                query = self.session.query(Packages).filter(Packages.software == software, Packages.name == name)
            #
            if query.count() == 0:
                return False
            #
            if returnAll:
                return query
            else:
                return query[0]
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR (FP): {0} (findPackage).\n".format(self.errorsDescription(e)))
            return False

    def packagesDataToDictionary(self, modelData):
        modelData['software'] = []
        #
        for i in self.getPackagesByModelID(modelData['id']):
            modelData['software'].append(self.convertToTable(i))
        #
        return modelData

    def getPackageByID(self, param):
        if param <= 0:
            return False
        #
        query = self.session.query(Packages).filter(Packages.id == int(param))
        #
        if query.count() == 0:
            FreeCAD.Console.PrintWarning("ERROR (GPB_ID): {0} (get package).\n".format(self.errorsDescription(e)))
            return False
        #
        return query[0]

    def getPackagesBySoftware(self, param):
        try:
            query = self.session.query(Packages).filter(Packages.software == str(param))
            #
            if query.count() == 0:
                return []
            #
            return query
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR (GPBM_ID): {0} (get package).\n".format(self.errorsDescription(e)))
            return []

    def getPackagesByModelID(self, param):
        try:
            query = self.session.query(Packages).filter(Packages.modelID == int(param))
            #
            if query.count() == 0:
                return []
            #
            return query
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR (GPBM_ID): {0} (get package).\n".format(self.errorsDescription(e)))
            return []

    def addPackage(self, data, modelID=0, modelName=0):
        try:
            if modelID != 0:
                modelID = int(modelID)
            elif modelName != 0:
                modelID = self.getModelByName(self.clearString(modelName))[1].id
            else:
                return [False]
            #
            name = self.clearString(data['name'])
            software = self.clearString(data['software'])
            x = float(data['x'])
            y = float(data['y'])
            z = float(data['z'])
            rx = float(data['rx'])
            ry = float(data['ry'])
            rz = float(data['rz'])
            #
            package = Packages(modelID, name, software, x, y, z, rx, ry, rz)
            self.session.add(package)
            self.session.commit()
            self.lastInsertedID = package.id
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR (AP): {0} (add package).\n".format(e))
            return [False]

    def updatePackage(self, packageID, data):
        try:
            packageID = int(packageID)
            name = self.clearString(data["name"])
            software = self.clearString(data["software"])
            #
            if name == '' or software == '' or packageID <= 0:
                raise MandatoryError()
            #
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
            #
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            FreeCAD.Console.PrintWarning("ERROR (UP): {0} (update package).\n".format(self.errorsDescription(e)))
            return False

    def deletePackage(self, packageID):
        try:
            self.session.query(Packages).filter(Packages.id == int(packageID)).delete()
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            FreeCAD.Console.PrintWarning("ERROR (DP): {0} (delete package).\n".format(self.errorsDescription(e)))
            return False
        else:
            return True

    def getAllSockets(self):
        try:
            query = self.session.query(Models).filter(Models.isSocket == 1)
            if query.count() == 0:
                return []
            #
            return query
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR (GAS): {0} (get all sockets).\n".format(self.errorsDescription(e)))
            return []

    def packagesConvertFromTo(self, fromParam, toParam, defSoftware):
        fromParam = self.clearString(fromParam)
        toParam = self.clearString(toParam)
        #
        if fromParam == "" or toParam == "":
            FreeCAD.Console.PrintWarning("One or more mandatory fields are empty!\n")
            return
        elif fromParam == toParam:
            FreeCAD.Console.PrintWarning("Error: both values are equal!\n")
            return
        elif not fromParam in defSoftware or not toParam in defSoftware:
            FreeCAD.Console.PrintWarning("Error: One or more mandatory fields are incorrect!\n")
            return
        #
        data = []
        for i in self.getPackagesBySoftware(fromParam):
            packageData = self.convertToTable(i)
            #
            query = self.session.query(Packages).filter(Packages.software == toParam, Packages.name == packageData["name"], Packages.modelID == packageData["modelID"])
            if query.count() == 0:
                data.append(packageData)
        #
        for i in data:
            i["software"] = toParam
            self.addPackage(i, i["modelID"])
        #
        FreeCAD.Console.PrintWarning("Done!\n")

    def getAllModels(self):
        return self.session.query(Models)

    def getAllModelsByCategory(self, categoryID):
        return self.session.query(Models).filter(Models.categoryID == categoryID)

    def getModelByID(self, param):
        try:
            query = self.session.query(Models).filter(Models.id == int(param))
            if query.count() == 0:
                return [False]
            #
            return [True, query[0]]
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR (GMBID): {0} (get model).\n".format(self.errorsDescription(e)))
            return [False]

    def getModelByName(self, param):
        try:
            query = self.session.query(Models).filter(Models.name == self.clearString(param))
            if query.count() == 0:
                return [False]
            #
            return [True, query[0]]
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR (GMBN): {0} (get model).\n".format(self.errorsDescription(e)))
            return [False]

    def deleteModel(self, modelID):
        try:
            modelID = int(modelID)
            #
            self.session.query(Models).filter(Models.socketID == modelID).update({"socketID": 0, "socketIDSocket": False})
            self.session.query(Packages).filter(Packages.modelID == modelID).delete()
            self.session.query(Models).filter(Models.id == modelID).delete()
            self.session.query(modelsParam).filter(modelsParam.modelID == modelID).delete()
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            FreeCAD.Console.PrintWarning("ERROR (DM): {0} (delete model).\n".format(self.errorsDescription(e)))
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
            #
            try:
                socketID = int(data["socketID"])
            except:
                socketID = 0
            #
            socketIDSocket = data["socketIDSocket"]
            #
            if name == '' or path3DModels == '':
                raise MandatoryError()
            #
            model = Models(name, path3DModels, description, categoryID, datasheet, isSocket, isSocketHeight, socketID, socketIDSocket)
            self.session.add(model)
            self.session.commit()
            self.lastInsertedID = model.id
            self.lastInsertedModelID = model.id
            #
            for i in data["software"]:
                if i['blanked']:
                    continue
                else:  # add new package
                    self.addPackage(i, modelID=self.lastInsertedModelID)
            #
            for i in data["params"].keys():
                if data["params"][i]["active"]:
                    self.addNewParam(model.id, i, data["params"][i])
        except Exception as e:
            self.session.rollback()
            FreeCAD.Console.PrintWarning("ERROR (AM): {0} (add new model).\n".format(self.errorsDescription(e)))
            return False
        else:
            FreeCAD.Console.PrintWarning("Model {0} was added.\n".format(name))
            return True

    def paramsDataToDictionary(self, modelData):
        modelData["params"] = []
        #
        for i in self.getParamsByModelID(modelData['id']):
            modelData["params"].append(self.convertToTable(i))
        #
        return modelData

    def getParamsByModelID(self, param, name='*'):
        try:
            if name == "*":
                query = self.session.query(modelsParam).filter(modelsParam.modelID == int(param))
            else:
                query = self.session.query(modelsParam).filter(modelsParam.modelID == int(param), modelsParam.name == name)
            #
            if query.count() == 0:
                return []
            #
            return query
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR (GPBM_ID): {0} (get package).\n".format(self.errorsDescription(e)))
            return []

    def addNewParam(self, modelID, name, data):
        try:
            modelID = int(modelID)
            name = self.clearString(name)
            color = self.clearString(str(data['color']))
            align = self.clearString(data['align'])
            active = bool(data['active'])
            display = bool(eval(data['display']))
            x = float(data['x'])
            y = float(data['y'])
            z = float(data['z'])
            rz = float(data['rz'])
            size = float(data['size'])
            spin = bool(eval(data['spin']))
            #
            param = modelsParam(modelID, name, color, align, active, display, x, y, z, rz, size, spin)
            self.session.add(param)
            self.session.commit()
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR (A_PARAM): {0} (add param).\n".format(e))
            return [False]

    def updateParam(self, paramID, data):
        try:
            paramID = int(paramID)
            if paramID <= 0:
                raise MandatoryError()
            #
            self.session.query(modelsParam).filter(modelsParam.id == paramID).update({
                    "active": bool(data['active']),
                    "display": bool(eval(data['display'])),
                    "x": float(data["x"]),
                    "y": float(data["y"]),
                    "z": float(data["z"]),
                    "rz": float(data["rz"]),
                    "size": float(data["size"]),
                    "color": self.clearString(str(data['color'])),
                    "align": self.clearString(data['align']),
                    "spin": bool(eval(data['spin'])),
            })
            #
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            FreeCAD.Console.PrintWarning("ERROR (U_PARAM): {0} (update param).\n".format(self.errorsDescription(e)))
            return False

    def setCategoryForModel(self, modelID, categoryID):
        try:
            modelID = int(modelID)
            #
            if modelID <= 0:
                raise MandatoryError()
            #
            self.session.query(Models).filter(Models.id == modelID).update({
                    "categoryID": int(categoryID)
            })
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            FreeCAD.Console.PrintWarning("ERROR (SCFM): {0} (update model).\n".format(self.errorsDescription(e)))
            return False
        else:
            return True

    def updateModelSockedID(self, modelID, socketID):
        try:
            if modelID <= 0 or socketID <= 0:
                raise MandatoryError()
            #
            self.session.query(Models).filter(Models.id == modelID).update({
                    "socketID": socketID
            })
            #
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            FreeCAD.Console.PrintWarning("ERROR (UMS): {0} (update model).\n".format(self.errorsDescription(e)))
            return False

    def updateModel(self, modelID, data):
        try:
            name = self.clearString(data["name"])
            path3DModels = self.clearString(data["path3DModels"])
            modelID = int(modelID)
            #
            try:
                socketID = int(data["socketID"])
            except:
                socketID = 0
            #
            if name == '' or path3DModels == '' or modelID <= 0:
                raise MandatoryError()
            #
            self.session.query(Models).filter(Models.id == modelID).update({
                    "name": name,
                    "description": self.clearString(data["description"]),
                    "categoryID": int(data["categoryID"]),
                    "datasheet": self.clearString(data["datasheet"]),
                    "path3DModels": path3DModels,
                    "isSocket": data["isSocket"],
                    "isSocketHeight": float(data["isSocketHeight"]),
                    "socketID": socketID,
                    "socketIDSocket": data["socketIDSocket"]
            })
            #
            self.session.commit()
            #
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
            #
            for i in data["params"].keys():
                if data["params"][i]["id"] == -1 and data["params"][i]["active"]:  # add new param
                    self.addNewParam(modelID, i, data["params"][i])
                elif not data["params"][i]["id"] == -1:  # update param
                    self.updateParam(data["params"][i]["id"], data["params"][i])
        except Exception as e:
            self.session.rollback()
            FreeCAD.Console.PrintWarning("ERROR (UP): {0} (update model).\n".format(self.errorsDescription(e)))
            return False
        else:
            FreeCAD.Console.PrintWarning("Model {0} was updated.\n".format(name))
            return True

    def getCategoryByName(self, param):
        try:
            query = self.session.query(Categories).filter(Categories.name == self.clearString(param))
            if query.count() == 0:
                return [False]
            #
            return [True, query[0]]
        #
        except Exception as e:
            FreeCAD.Console.PrintWarning("ERROR (GCBN): {0} (get category).\n".format(self.errorsDescription(e)))
            return [False]

    def getCategoryByID(self, catID=0):
        if catID <= 0:
            return False
        #
        query = self.session.query(Categories).filter(Categories.id == int(catID))
        #
        if query.count() == 0:
            FreeCAD.Console.PrintWarning("ERROR (GCBID): Category does not exist.\n")
            return False
        #
        return query[0]

    def getAllcategoriesWithSubCat(self, catID=0):
        categories = {}
        #
        for i in self.session.query(Categories).filter(Categories.parentID == catID):
            categories[i.name] = {}
            categories[i.name]['id'] = i.id
            categories[i.name]['description'] = i.description
            #
            categories[i.name]['sub'] = self.getAllcategoriesWithSubCat(i.id)
        #
        return categories

    def getAllcategories(self):
        return self.session.query(Categories)

    def deleteCategory(self, categoryID):
        ''' '''
        try:
            categoryID = int(categoryID)
            #
            categoryData = self.getCategoryByID(categoryID)
            parentID = categoryData.parentID
            #
            self.session.query(Categories).filter(Categories.parentID == categoryID).update({"parentID": parentID})
            self.session.query(Models).filter(Models.categoryID == categoryID).update({"categoryID": parentID})
            #
            self.session.query(Categories).filter(Categories.id == categoryID).delete()
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            FreeCAD.Console.PrintWarning("ERROR (DC): {0} (delete category).\n".format(self.errorsDescription(e)))
            return False
        else:
            FreeCAD.Console.PrintWarning("Category {0} was deleted.\n".format(categoryData.name))
            return True

    def updateCategory(self, categoryID, name, parentID, description):
        ''' '''
        try:
            categoryID = int(categoryID)
            name = self.clearString(name)
            if parentID == -1 or parentID is None:
                parentID = 0
            parentID = int(parentID)
            description = self.clearString(description)
            #
            if name == '' or categoryID <= 0:
                raise MandatoryError()
            #
            self.session.query(Categories).filter(Categories.id == categoryID).update({"name": name, "parentID": parentID, "description": description})
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            FreeCAD.Console.PrintWarning("ERROR (UC): {0} (update category).\n".format(self.errorsDescription(e)))
            return False
        else:
            FreeCAD.Console.PrintWarning("Category {0} was updated.\n".format(name))
            return True

    def addCategory(self, name, parentID, description):
        ''' '''
        try:
            name = self.clearString(name)
            if parentID == -1 or parentID is None:
                parentID = 0
            parentID = int(parentID)
            description = self.clearString(description)
            #
            if name == '':
                raise MandatoryError()
            #
            categories = Categories(name, parentID, description)
            self.session.add(categories)
            self.session.commit()
            self.lastInsertedID = categories.id
        except Exception as e:
            self.session.rollback()
            FreeCAD.Console.PrintWarning("ERROR (AC): {0} (add new category).\n".format(self.errorsDescription(e)))
            return False
        else:
            FreeCAD.Console.PrintWarning("Category {0} was added.\n".format(name))
            return True
