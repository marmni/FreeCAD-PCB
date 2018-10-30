# -*- coding: utf8 -*-
#****************************************************************************
#*                                                                          *
#*   Printed Circuit Board Workbench for FreeCAD             PCB            *
#*   Flexible Printed Circuit Board Workbench for FreeCAD    FPCB           *
#*   Copyright (c) 2013, 2014                                               *
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
#import os
import PCBrc
#import glob
import FreeCAD
from PCBdataBase import dataBase
from PCBconf import *
import types

#__currentPath__ = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class dodajElement(QtGui.QDialog):
    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.setWindowTitle("Assign models")
        self.setWindowIcon(QtGui.QIcon(":/data/img/uklad.png"))
        #
        self.elementID = None
        self.szukaneFrazy = []
        self.szukaneFrazyNr = 0
        #
        self.sql = dataBase()
        
        # lista elementow
        wyszukiwarka = QtGui.QLineEdit()
        self.connect(wyszukiwarka, QtCore.SIGNAL("textChanged (const QString&)"), self.wyszukajObiekty)
        self.listaElementow = QtGui.QTreeWidget()
        self.listaElementow.setColumnCount(2)
        self.listaElementow.setHeaderLabels([u"Name", u"Description"])
        self.listaElementow.setSortingEnabled(True)
        self.connect(self.listaElementow, QtCore.SIGNAL("itemPressed (QTreeWidgetItem *,int)"), self.zaladujDane)
        
        przyciskNext = QtGui.QPushButton("")
        przyciskNext.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        przyciskNext.setIcon(QtGui.QIcon(":/data/img/next_16x16.png"))
        przyciskNext.setToolTip(u"Next package")
        przyciskNext.setFlat(True)
        self.connect(przyciskNext, QtCore.SIGNAL("clicked ()"), self.wyszukajObiektyNext)
        przyciskPrev = QtGui.QPushButton("")
        przyciskPrev.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        przyciskPrev.setIcon(QtGui.QIcon(":/data/img/previous_16x16.png"))
        przyciskPrev.setToolTip(u"Previous package")
        przyciskPrev.setFlat(True)
        self.connect(przyciskPrev, QtCore.SIGNAL("clicked ()"), self.wyszukajObiektyPrev)
        przyciskUsunelement = QtGui.QPushButton("")
        przyciskUsunelement.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        przyciskUsunelement.setIcon(QtGui.QIcon(":/data/img/delete_16x16.png"))
        przyciskUsunelement.setToolTip(u"Delete")
        przyciskUsunelement.setFlat(True)
        self.connect(przyciskUsunelement, QtCore.SIGNAL("clicked ()"), self.delObject)
        przyciskReload = QtGui.QPushButton("")
        przyciskReload.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        przyciskReload.setIcon(QtGui.QIcon(":/data/img/reload_16x16.png"))
        przyciskReload.setToolTip(u"Reload")
        przyciskReload.setFlat(True)
        self.connect(przyciskReload, QtCore.SIGNAL("clicked ()"), self.reloadList)
        
        layLista = QtGui.QHBoxLayout()
        layLista.setContentsMargins(0, 0, 0, 0)
        layLista.addWidget(przyciskReload)
        layLista.addStretch(10)
        layLista.addWidget(przyciskUsunelement)
        
        self.listaBibliotek = QtGui.QComboBox()
        self.connect(self.listaBibliotek, QtCore.SIGNAL("currentIndexChanged (int)"), self.reloadList)
        
        listaElementowLay = QtGui.QGridLayout()
        listaElementowLay.setContentsMargins(0, 0, 10, 0)
        listaElementowLay.addWidget(self.listaBibliotek, 0, 0, 1, 3)
        listaElementowLay.addWidget(wyszukiwarka, 1, 0, 1, 1)
        listaElementowLay.addWidget(przyciskPrev, 1, 1, 1, 1)
        listaElementowLay.addWidget(przyciskNext, 1, 2, 1, 1)
        listaElementowLay.addWidget(self.listaElementow, 2, 0, 1, 3)
        listaElementowLay.addLayout(layLista, 3, 0, 1, 3)
        listaElementowLay.setRowStretch(2, 10)
        listaElementowLay.setColumnStretch(0, 10)
        # nazwa elementu eagle
        self.nazwaEagle = QtGui.QLineEdit("")
        # sciezka do elementu
        self.sciezkaDoElementu = QtGui.QLineEdit("")
        
        sciezkaDoElementuPrz = QtGui.QPushButton("")
        sciezkaDoElementuPrz.setToolTip(u"Info")
        sciezkaDoElementuPrz.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        sciezkaDoElementuPrz.setIcon(QtGui.QIcon(":/data/img/info_16x16.png"))
        sciezkaDoElementuPrz.setFlat(True)
        sciezkaDoElementuPrz.setStyleSheet('''
                QPushButton
                {
                    border: 0px;
                    margin-top: 2px;
                    width: 15px;
                    height: 15px;
                }
            ''')
        self.connect(sciezkaDoElementuPrz, QtCore.SIGNAL("clicked ()"), self.loadPathInfo)
        # opis elementu
        self.opisElementu = QtGui.QTextEdit()
        # datasheet
        self.datasheetPath = QtGui.QLineEdit("")
        
        datasheetPrz = QtGui.QPushButton("")
        datasheetPrz.setToolTip(u"Open datasheet")
        datasheetPrz.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        datasheetPrz.setIcon(QtGui.QIcon(":/data/img/browser_16x16.png"))
        datasheetPrz.setFlat(True)
        datasheetPrz.setStyleSheet('''
                QPushButton
                {
                    border: 0px;
                    margin-top: 2px;
                    width: 15px;
                    height: 15px;
                }
            ''')
        self.connect(datasheetPrz, QtCore.SIGNAL("clicked ()"), self.loadDatasheet)
        # PODSTAWKA DLA ELEMENTU
        self.nazwaPodstawki = QtGui.QComboBox()
        
        self.boxZastosujPodstawke = QtGui.QGroupBox()
        self.boxZastosujPodstawke.setTitle(u"Add socket")
        self.boxZastosujPodstawke.setCheckable(True)
        self.boxZastosujPodstawke.setChecked(False)
        layBoxZastosujPodstawke = QtGui.QHBoxLayout(self.boxZastosujPodstawke)
        layBoxZastosujPodstawke.addWidget(QtGui.QLabel(u"Socket"))
        layBoxZastosujPodstawke.addWidget(self.nazwaPodstawki)
        # ELEMENT JEST PODSTAWKA
        self.podstawkaWysokosc = QtGui.QDoubleSpinBox()
        self.podstawkaWysokosc.setSuffix(" mm")
        
        self.boxPodstawka = QtGui.QGroupBox()
        self.boxPodstawka.setTitle(u"Set as socket")
        self.boxPodstawka.setCheckable(True)
        self.boxPodstawka.setChecked(False)
        layBoxPodstawka = QtGui.QHBoxLayout(self.boxPodstawka)
        layBoxPodstawka.addWidget(QtGui.QLabel(u"Height"))
        layBoxPodstawka.addWidget(self.podstawkaWysokosc)
        # pasek z przyciskami 1
        przycsikZapisz = QtGui.QPushButton("Save")
        przycsikZapisz.setIcon(QtGui.QIcon(":/data/img/save_22x22.png"))
        self.connect(przycsikZapisz, QtCore.SIGNAL("clicked ()"), self.addPackage)
        przycsikWyczysc = QtGui.QPushButton("Clean/New")
        przycsikWyczysc.setIcon(QtGui.QIcon(":/data/img/clear_16x16.png"))
        self.connect(przycsikWyczysc, QtCore.SIGNAL("clicked ()"), self.wyczyscDane)
        przycsikZapiszAs = QtGui.QPushButton("Save As New")
        przycsikZapiszAs.setIcon(QtGui.QIcon(":/data/img/save_22x22.png"))
        self.connect(przycsikZapiszAs, QtCore.SIGNAL("clicked ()"), self.addPackageAsNew)
        
        self.layPrzyciski_1 = QtGui.QHBoxLayout()
        self.layPrzyciski_1.setContentsMargins(0, 0, 0, 0)
        self.layPrzyciski_1.addStretch(10)
        self.layPrzyciski_1.addWidget(przycsikZapisz)
        self.layPrzyciski_1.addWidget(przycsikZapiszAs)
        self.layPrzyciski_1.addWidget(przycsikWyczysc)
        # WSPORZEDNE + OBROTY
        self.pozX = QtGui.QDoubleSpinBox()
        self.pozX.setRange(-1000, 1000)
        self.pozX.setSuffix(" mm")
        self.pozY = QtGui.QDoubleSpinBox()
        self.pozY.setRange(-1000, 1000)
        self.pozY.setSuffix(" mm")
        self.pozZ = QtGui.QDoubleSpinBox()
        self.pozZ.setRange(-1000, 1000)
        self.pozZ.setSuffix(" mm")
        self.pozRX = QtGui.QDoubleSpinBox()
        self.pozRX.setRange(-1000, 1000)
        self.pozRX.setSuffix(" deg")
        self.pozRY = QtGui.QDoubleSpinBox()
        self.pozRY.setRange(-1000, 1000)
        self.pozRY.setSuffix(" deg")
        self.pozRZ = QtGui.QDoubleSpinBox()
        self.pozRZ.setRange(-1000, 1000)
        self.pozRZ.setSuffix(" deg")
        ukladWspolrzednych = QtGui.QLabel("")
        ukladWspolrzednych.setPixmap(QtGui.QPixmap(":/data/img/uklad.png"))
        
        layWspolrzedne = QtGui.QGridLayout()
        layWspolrzedne.setContentsMargins(10, 10, 10, 10)
        layWspolrzedne.addWidget(ukladWspolrzednych, 0, 0, 6, 1, QtCore.Qt.AlignTop | QtCore.Qt.AlignCenter)
        layWspolrzedne.addWidget(QtGui.QLabel("X"), 0, 1, 1, 1, QtCore.Qt.AlignRight)
        layWspolrzedne.addWidget(self.pozX, 0, 2, 1, 1, QtCore.Qt.AlignTop)
        layWspolrzedne.addWidget(QtGui.QLabel("Y"), 1, 1, 1, 1, QtCore.Qt.AlignRight)
        layWspolrzedne.addWidget(self.pozY, 1, 2, 1, 1, QtCore.Qt.AlignTop)
        layWspolrzedne.addWidget(QtGui.QLabel("Z"), 2, 1, 1, 1, QtCore.Qt.AlignRight)
        layWspolrzedne.addWidget(self.pozZ, 2, 2, 1, 1, QtCore.Qt.AlignTop)
        layWspolrzedne.addWidget(QtGui.QLabel("RX"), 3, 1, 1, 1, QtCore.Qt.AlignRight)
        layWspolrzedne.addWidget(self.pozRX, 3, 2, 1, 1, QtCore.Qt.AlignTop)
        layWspolrzedne.addWidget(QtGui.QLabel("RY"), 4, 1, 1, 1, QtCore.Qt.AlignRight)
        layWspolrzedne.addWidget(self.pozRY, 4, 2, 1, 1, QtCore.Qt.AlignTop)
        layWspolrzedne.addWidget(QtGui.QLabel("RZ"), 5, 1, 1, 1, QtCore.Qt.AlignRight)
        layWspolrzedne.addWidget(self.pozRZ, 5, 2, 1, 1, QtCore.Qt.AlignTop)
        layWspolrzedne.setRowStretch(6, 10)
        layWspolrzedne.setColumnStretch(2, 10)
        #layWspolrzedne.setColumnStretch(4, 10)
        # dolny pasek
        widgetName = QtGui.QLabel("EaglePCB_2_FreeCAD")
        
        buttonInfo = QtGui.QPushButton("i")
        
        layInfo = QtGui.QGridLayout()
        layInfo.addWidget(widgetName, 0, 0, 1, 1, QtCore.Qt.AlignLeft)
        #layInfo.addWidget(buttonInfo, 0, 1, 1, 1, QtCore.Qt.AlignRight)
        widgetInfo = QtGui.QWidget()
        widgetInfo.setLayout(layInfo)
        widgetInfo.setObjectName("widgetInfo")
        widgetInfo.setStyleSheet('''
                #widgetInfo
                {
                    background: #84978F;
                    border: 1px solid #527578;
                }
                QLabel
                {
                    color: #000;
                    font-weight:bold;
                }
                QPushButton
                {
                    border: 1px solid #527578;
                    width: 15px;
                    height: 15px;
                    font-weight:bold;
                }
            ''')
        ####
        self.mainLayout = QtGui.QGridLayout()
        #self.mainLayout.setContentsMargins(0, 0, 0, 0)
        #self.mainLayout.addWidget(self.listaBibliotek, 0, 0, 1, 1, QtCore.Qt.AlignTop)
        self.mainLayout.addLayout(listaElementowLay, 1, 0, 9, 1, QtCore.Qt.AlignTop)
        self.mainLayout.addItem(QtGui.QSpacerItem(10, 20), 1, 1, 1, 1, QtCore.Qt.AlignTop)
        self.mainLayout.addWidget(QtGui.QLabel(u"Package type"), 2, 1, 1, 1)
        self.mainLayout.addWidget(self.nazwaEagle, 2, 2, 1, 2, QtCore.Qt.AlignTop)
        self.mainLayout.addWidget(QtGui.QLabel(u"Path to element"), 3, 1, 1, 1)
        self.mainLayout.addWidget(self.sciezkaDoElementu, 3, 2, 1, 1, QtCore.Qt.AlignTop)
        self.mainLayout.addWidget(sciezkaDoElementuPrz, 3, 3, 1, 1)
        self.mainLayout.addWidget(QtGui.QLabel(u"Datasheet"), 4, 1, 1, 1)
        self.mainLayout.addWidget(self.datasheetPath, 4, 2, 1, 1, QtCore.Qt.AlignTop)
        self.mainLayout.addWidget(datasheetPrz, 4, 3, 1, 1)
        self.mainLayout.addLayout(layWspolrzedne, 5, 1, 1, 3, QtCore.Qt.AlignTop)
        self.mainLayout.addWidget(self.boxZastosujPodstawke, 6, 1, 1, 3, QtCore.Qt.AlignTop)
        self.mainLayout.addWidget(self.boxPodstawka, 7, 1, 1, 3, QtCore.Qt.AlignTop)
        self.mainLayout.addWidget(QtGui.QLabel("Description"), 8, 1, 1, 3, QtCore.Qt.AlignTop)
        self.mainLayout.addWidget(self.opisElementu, 9, 1, 1, 3)
        self.mainLayout.addLayout(self.layPrzyciski_1, 10, 1, 1, 3)
        #self.mainLayout.addItem(QtGui.QSpacerItem(11, 20), 10, 1, 1, 3, QtCore.Qt.AlignTop)
        #self.mainLayout.addWidget(widgetInfo, 12, 0, 1, 4, QtCore.Qt.AlignTop)
        self.mainLayout.setRowStretch(9, 10)
        #
        self.setLayout(self.mainLayout)
        #
        self.readLibs()
        self.reloadList()
        
    def readLibs(self):
        ''' read libs from conf file '''
        #pliki = glob.glob(__currentPath__ + '/data/*.cfg')
        #for i in pliki:
            #docname = os.path.splitext(os.path.basename(i))[0]
            #self.listaBibliotek.addItem(docname)
            #self.listaBibliotek.setItemData(self.listaBibliotek.count() - 1, i, QtCore.Qt.UserRole)
        #self.listaBibliotek.setCurrentIndex(0)
        for i, j in supSoftware.items():
            if j['pathToBase'].strip() != "":
                if j['name'].strip() != "":
                    dbName = j['name'].strip()
                else:
                    dbName = i.strip()
                
                self.listaBibliotek.addItem(dbName)
                self.listaBibliotek.setItemData(self.listaBibliotek.count() - 1, j['pathToBase'].strip(), QtCore.Qt.UserRole)
        self.listaBibliotek.setCurrentIndex(0)

    def loadPathInfo(self):
        '''  '''
        dial = QtGui.QMessageBox(self)
        dial.setText(u"U can use absolute or relative paths (for relative define paths in file conf.py).")
        dial.setWindowTitle("Info")
        dial.setIcon(QtGui.QMessageBox.Information)
        dial.addButton('Ok', QtGui.QMessageBox.RejectRole)
        dial.exec_()
        
    def loadDatasheet(self):
        ''' load datasheet of selected package '''
        url = str(self.datasheetPath.text()).strip()
        if len(url):
            if url.startswith("http://") or url.startswith("https://") or url.startswith("www."):
                QtGui.QDesktopServices().openUrl(QtCore.QUrl(url))
            else:
                QtGui.QDesktopServices().openUrl(QtCore.QUrl("file:///{0}".format(url), QtCore.QUrl.TolerantMode))
    
    def wyczyscDane(self):
        ''' clean form '''
        tablica = {"id": None,
                   "name": "",
                   "path": "",
                   "x": 0.,
                   "y": 0.,
                   "z": 0.,
                   "rx": 0.,
                   "ry": 0.,
                   "rz": 0.,
                   "add_socket": 0,
                   "add_socket_id": 0,
                   "socket": 0,
                   "socket_height": 0.,
                   "description": "",
                   "datasheet": ""}
        self.pokazDane(tablica)
        
    def pokazDane(self, dane):
        ''' load package info to form '''
        self.elementID = dane["id"]
        
        self.nazwaEagle.setText(dane["name"])
        self.sciezkaDoElementu.setText(dane["path"])
        self.pozX.setValue(float(dane["x"]))
        self.pozY.setValue(float(dane["y"]))
        self.pozZ.setValue(float(dane["z"]))
        self.pozRX.setValue(float(dane["rx"]))
        self.pozRY.setValue(float(dane["ry"]))
        self.pozRZ.setValue(float(dane["rz"]))
        self.podstawkaWysokosc.setValue(float(dane["socket_height"]))
        self.boxPodstawka.setChecked(int(dane["socket"]))
        self.boxZastosujPodstawke.setChecked(int(dane["add_socket"]))
        self.opisElementu.setPlainText(dane["description"])
        self.datasheetPath.setText(dane["datasheet"])
        #self.nazwaPodstawki.setCurrentIndex(self.nazwaPodstawki.findData(dane["addSocketID"]))
        
    def zaladujDane(self, item):
        aktualnyElement = self.listaElementow.currentItem()
        elemID = str(aktualnyElement.data(0, QtCore.Qt.UserRole))
        
        dane = self.sql.getValues(elemID)
        dane["id"] = elemID

        self.pokazDane(dane)
    
    def updatePackage(self, elemID):
        ''' update package param '''
        dane = {"name": str(self.nazwaEagle.text()).strip(),
                "path": str(self.sciezkaDoElementu.text()).strip(),
                "x": str(self.pozX.value()),
                "y": str(self.pozY.value()),
                "z": str(self.pozZ.value()),
                "rx": str(self.pozRX.value()),
                "ry": str(self.pozRY.value()),
                "rz": str(self.pozRZ.value()),
                "add_socket": str(int(self.boxZastosujPodstawke.isChecked())),
                "add_socket_id": str(self.nazwaPodstawki.itemData(self.nazwaPodstawki.currentIndex(), QtCore.Qt.UserRole)),
                "socket": str(int(self.boxPodstawka.isChecked())),
                "socket_height": str(self.podstawkaWysokosc.value()),
                "description": str(self.opisElementu.toPlainText()),
                "datasheet": str(self.datasheetPath.text()).strip()
                }
        
        self.sql.updatePackage(elemID, dane)
        self.reloadList()
        
    def wyszukajObiektyNext(self):
        ''' find next object '''
        try:
            if len(self.szukaneFrazy):
                if self.szukaneFrazyNr <= len(self.szukaneFrazy) - 2:
                    self.szukaneFrazyNr += 1
                else:
                    self.szukaneFrazyNr = 0
                self.listaElementow.setCurrentItem(self.szukaneFrazy[self.szukaneFrazyNr])
        except RuntimeError:
            self.szukaneFrazy = []
            self.szukaneFrazyNr = 0
    
    def wyszukajObiektyPrev(self):
        ''' find prev object '''
        try:
            if len(self.szukaneFrazy):
                if self.szukaneFrazyNr >= 1:
                    self.szukaneFrazyNr -= 1
                else:
                    self.szukaneFrazyNr = len(self.szukaneFrazy) - 1
                self.listaElementow.setCurrentItem(self.szukaneFrazy[self.szukaneFrazyNr])
        except RuntimeError:
            self.szukaneFrazy = []
            self.szukaneFrazyNr = 0
        
    def wyszukajObiekty(self, fraza):
        ''' find object in current document '''
        fraza = str(fraza).strip()
        if fraza != "":
            self.szukaneFrazy = self.listaElementow.findItems(fraza, QtCore.Qt.MatchRecursive | QtCore.Qt.MatchStartsWith)
            if len(self.szukaneFrazy):
                self.listaElementow.setCurrentItem(self.szukaneFrazy[0])
                self.szukaneFrazyNr = 0
                
    def addElement(self):
        ''' add package info to lib '''
        dane = {"name": str(self.nazwaEagle.text()).strip(),
                "path": str(self.sciezkaDoElementu.text()).strip(),
                "x": str(self.pozX.value()),
                "y": str(self.pozY.value()),
                "z": str(self.pozZ.value()),
                "rx": str(self.pozRX.value()),
                "ry": str(self.pozRY.value()),
                "rz": str(self.pozRZ.value()),
                "add_socket": str(int(self.boxZastosujPodstawke.isChecked())),
                "add_socket_id": str(self.nazwaPodstawki.itemData(self.nazwaPodstawki.currentIndex(), QtCore.Qt.UserRole)),
                "socket": str(int(self.boxPodstawka.isChecked())),
                "socket_height": str(self.podstawkaWysokosc.value()),
                "description": str(self.opisElementu.toPlainText()),
                "datasheet": str(self.datasheetPath.text()).strip()}
        self.sql.addPackage(dane)
        self.reloadList()
        
    def addPackageAsNew(self):
        ''' add package as new - based on other package '''
        if str(self.nazwaEagle.text()).strip() == "" or str(self.sciezkaDoElementu.text()).strip() == "":
            QtGui.QMessageBox().critical(self, u"Caution!", u"At least one required field is empty.")
            return

        zawiera = self.sql.has_value("name", self.nazwaEagle.text())
        if zawiera[0]:
            dial = QtGui.QMessageBox(self)
            dial.setText(u"Rejected. Package already exist.")
            dial.setWindowTitle("Caution!")
            dial.setIcon(QtGui.QMessageBox.Warning)
            dial.addButton('Ok', QtGui.QMessageBox.RejectRole)
            dial.exec_()
        else:
            self.addElement()

    def addPackage(self):
        ''' add package to lib '''
        if str(self.nazwaEagle.text()).strip() == "" or str(self.sciezkaDoElementu.text()).strip() == "":
            QtGui.QMessageBox().critical(self, u"Caution!", u"At least one required field is empty.")
            return

        zawiera = self.sql.has_value("name", self.nazwaEagle.text())
        if not self.elementID and zawiera[0]:  # aktualizacja niezaznaczonego obiektu
            dial = QtGui.QMessageBox(self)
            dial.setText(u"Package already exist. Rewrite?")
            dial.setWindowTitle("Caution!")
            dial.setIcon(QtGui.QMessageBox.Question)
            rewN = dial.addButton('No', QtGui.QMessageBox.RejectRole)
            rewT = dial.addButton('Yes', QtGui.QMessageBox.YesRole)
            dial.exec_()
                
            if dial.clickedButton() == rewN:
                return
            else:
                self.updatePackage(zawiera[1])
                return
        elif self.elementID:  # aktualizacja zaznaczonego obiektu
            dial = QtGui.QMessageBox(self)
            dial.setText(u"Save changes?")
            dial.setWindowTitle("Caution!")
            dial.setIcon(QtGui.QMessageBox.Question)
            rewN = dial.addButton('No', QtGui.QMessageBox.RejectRole)
            rewT = dial.addButton('Yes', QtGui.QMessageBox.YesRole)
            dial.exec_()
                
            if dial.clickedButton() == rewN:
                return
            else:
                #zawiera = self.sql.has_value("name", self.nazwaEagle.text())
                if zawiera[0] and zawiera[1] != self.elementID:
                    dial = QtGui.QMessageBox(self)
                    dial.setText(u"Rejected. Package already exist.")
                    dial.setWindowTitle("Caution!")
                    dial.setIcon(QtGui.QMessageBox.Warning)
                    dial.addButton('Ok', QtGui.QMessageBox.RejectRole)
                    dial.exec_()
                else:
                    if not self.sql.has_section(self.elementID):
                        self.addElement()
                    else:
                        self.updatePackage(self.elementID)
                return
        else:  # dodanie nowego obiektu
            self.addElement()

    def delObject(self):
        ''' delete package from lib '''
        try:
            aktualnyElement = self.listaElementow.currentItem()
            objectID = str(aktualnyElement.data(0, QtCore.Qt.UserRole))
            
            dial = QtGui.QMessageBox(self)
            dial.setText(u"Delete selected package?")
            dial.setWindowTitle("Caution!")
            dial.setIcon(QtGui.QMessageBox.Question)
            usunN = dial.addButton('No', QtGui.QMessageBox.RejectRole)
            usunT = dial.addButton('Yes', QtGui.QMessageBox.YesRole)
            dial.exec_()
                    
            if dial.clickedButton() == usunT:
                self.sql.delPackage(objectID)
                self.reloadList()
                self.wyczyscDane()
        except AttributeError:
            pass

    def reloadList(self, num=0):
        ''' reload list of packages from current lib '''
        try:
            if not isinstance(self.listaBibliotek.itemData(self.listaBibliotek.currentIndex()), types.NoneType):
                self.sql.read(str(self.listaBibliotek.itemData(self.listaBibliotek.currentIndex())))
                ##
                self.listaElementow.clear()
                self.nazwaPodstawki.clear()
                #
                self.sql.reloadList()
                spisElementow = self.sql.packages()
                #
                for i in spisElementow:
                    dane = self.sql.getValues(i)
                    
                    mainItem = QtGui.QTreeWidgetItem([dane["name"], dane["description"]])
                    mainItem.setData(0, QtCore.Qt.UserRole, i)
                    mainItem.setData(0, QtCore.Qt.UserRole + 1, "P")
                    
                    self.listaElementow.addTopLevelItem(mainItem)
                    
                    if int(dane["socket"]) == 1:
                        self.nazwaPodstawki.addItem("{0}".format(dane["name"]))
                        self.nazwaPodstawki.setItemData(self.nazwaPodstawki.count() - 1, i, QtCore.Qt.UserRole)
                
                self.listaElementow.sortItems(0, QtCore.Qt.AscendingOrder)
        except Exception, e:
            pass
        
    def closeEvent(self, event):
        self.sql.write()
