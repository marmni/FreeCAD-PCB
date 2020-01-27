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
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui
#
import re
from functools import partial
#
import PCBrc
from PCBobjects import *
from PCBboard import getPCBheight
from PCBpartManaging import partsManaging
from PCBdataBase import dataBase
from command.PCBassignModel import dodajElement
from command.PCBexplode import *
from command.PCBexport import exportPCB_Gui
from command.PCBexportBOM import exportBOM_Gui, createCentroid_Gui
from command.PCBexportHoles import exportHoles_Gui, exportHolesReport_Gui
from command.PCBexportDrillingMap import exportDrillingMap_Gui
from command.PCBgroups import *
from command.PCBupdateParts import updateParts
from command.PCBDownload import downloadModelW
from command.PCBaddModel import addModel
from command.PCBcreateBoard import createPCB
from command.PCBlayers import layersSettings
from command.PCBannotations import createAnnotation_Gui, PCBannotation, viewProviderPCBannotation
from command.PCBexportKerkythea import exportToKerkytheaGui
from command.PCBexportPovRay import exportObjectToPovRayGui
from command.PCBboundingBox import boundingBox, boundingBoxFromSelection
from command.PCBglue import createGlueGui
from command.PCBassembly import createAssemblyGui, updateAssembly, exportAssembly
from command.PCBdrill import createDrillcenter_Gui
from command.PCBcollision import checkCollisionsGui
from command.PCBconstraintAreas import createConstraintArea
from command.PCBsections import createSectionsGui


class pcbToolBarMain(QtGui.QToolBar):
    def __init__(self, text, parent=None):
        QtGui.QToolBar.__init__(self, text, parent)
        self.setVisible(False)
        self.toggleViewAction().setVisible(False)
        
    def show(self):
        self.draftWidget.setVisible(True)
        self.setVisible(True)

    def hide(self):
        self.draftWidget.setVisible(False)
        self.setVisible(True)

    def Activated(self):
        self.setVisible(True)
        self.toggleViewAction().setVisible(True)

    def Deactivated(self):
        self.setVisible(False)
        self.toggleViewAction().setVisible(False)
        
    def createAction(self, text, tooltip, icon):
        action = QtGui.QAction(text, self)
        action.setToolTip(tooltip)
        action.setStatusTip(tooltip)
        action.setIcon(QtGui.QIcon(icon))
        #action.setIcon(QtGui.QIcon(__currentPath__ + "/data/img/" + icon))
        return action
        
    #def getMainWindow(self):
        #toplevel = QtGui.qApp.topLevelWidgets()
        #for i in toplevel:
            #if i.metaObject().className() == "Gui::MainWindow":
                #return i
                
    def addToolBar(self, toolBar):
        self.mainWindow = FreeCADGui.getMainWindow()
        self.mainWindow.addToolBar(QtCore.Qt.TopToolBarArea, toolBar)


class pcbToolBarView(pcbToolBarMain):
    def __init__(self, parent=None):
        pcbToolBarMain.__init__(self, 'PCB View', parent)
        self.setObjectName("pcbToolBarView")
        
        # przyciski
        scriptCmd_viewShaded = self.createAction(u"Display mode: Shaded", u"Display mode: Shaded", ":/data/img/displayShaded.png")
        par = partial(self.changeDisplayMode, 'Shaded')
        QtCore.QObject.connect(scriptCmd_viewShaded, QtCore.SIGNAL("triggered()"), par)
        
        scriptCmd_viewFlatLines = self.createAction(u"Display mode: Shaded with Edges", u"Display mode: Shaded with Edges", ":/data/img/displayFlatLines.png")
        par = partial(self.changeDisplayMode, 'Flat Lines')
        QtCore.QObject.connect(scriptCmd_viewFlatLines, QtCore.SIGNAL("triggered()"), par)
        
        scriptCmd_viewWireframe = self.createAction(u"Display mode: Wireframe", u"Display mode: Wireframe", ":/data/img/displayWrireFrame.png")
        par = partial(self.changeDisplayMode, 'Wireframe')
        QtCore.QObject.connect(scriptCmd_viewWireframe, QtCore.SIGNAL("triggered()"), par)
        
        scriptCmd_viewInternalView = self.createAction(u"Display mode: Internal View", u"Display mode: Internal View", ":/data/img/displayInternalView.png")
        par = partial(self.changeDisplayMode, 'Internal View')
        QtCore.QObject.connect(scriptCmd_viewInternalView, QtCore.SIGNAL("triggered()"), par)

        scriptCmd_Layers = self.createAction(u"Layers settings", u"Layers settings", ":/data/img/layers_TI.svg")
        QtCore.QObject.connect(scriptCmd_Layers, QtCore.SIGNAL("triggered()"), self.Flayers)
        # Cut to board outline
        scriptCmd_cutToBoardOutlineON = self.createAction(u"Cut to board outline - ON", u"Cut to board outline ON", ":/data/img/cutToBoard.svg")
        QtCore.QObject.connect(scriptCmd_cutToBoardOutlineON, QtCore.SIGNAL("triggered()"), partial(self.cutToBoardOutline, True))
        
        scriptCmd_cutToBoardOutlineON2 = self.createAction(u"Cut to board outline - ON", u"Cut to board outline ON", ":/data/img/cutToBoard.svg")
        QtCore.QObject.connect(scriptCmd_cutToBoardOutlineON2, QtCore.SIGNAL("triggered()"), partial(self.cutToBoardOutline, True))
        
        scriptCmd_cutToBoardOutlineOFF = self.createAction(u"Cut to board outline - OFF", u"Cut to board outline ON", ":/data/img/cutToBoard.svg")
        QtCore.QObject.connect(scriptCmd_cutToBoardOutlineOFF, QtCore.SIGNAL("triggered()"), partial(self.cutToBoardOutline, False))
        
        groupsMenuCTB = QtGui.QMenu(self)
        groupsMenuCTB.addAction(scriptCmd_cutToBoardOutlineON2)
        groupsMenuCTB.addAction(scriptCmd_cutToBoardOutlineOFF)
        scriptCmd_cutToBoardOutlineON.setMenu(groupsMenuCTB)
        # show signals ON/OFF
        scriptCmd_showSignals = self.createAction(u"Show signals - ON", u"Show signals ON", ":/data/img/showSignalsON.png")
        QtCore.QObject.connect(scriptCmd_showSignals, QtCore.SIGNAL("triggered()"), partial(self.showSignals, True))
        
        scriptCmd_showSignals2 = self.createAction(u"Show signals - ON", u"Show signals ON", ":/data/img/showSignalsON.png")
        QtCore.QObject.connect(scriptCmd_showSignals2, QtCore.SIGNAL("triggered()"), partial(self.showSignals, True))
        
        scriptCmd_showSignalsOFF = self.createAction(u"Show signals - OFF", u"Show signals OFF", ":/data/img/showSignalsOFF.png")
        QtCore.QObject.connect(scriptCmd_showSignalsOFF, QtCore.SIGNAL("triggered()"), partial(self.showSignals, False))
        
        groupsMenuCTB = QtGui.QMenu(self)
        groupsMenuCTB.addAction(scriptCmd_showSignals2)
        groupsMenuCTB.addAction(scriptCmd_showSignalsOFF)
        scriptCmd_showSignals.setMenu(groupsMenuCTB)
        # Cut holes through all layers ON/OFF
        scriptCmd_cutHolesThroughAllLayersON = self.createAction(u"Cut holes through all layers - ON", u"Cut holes through all layers - ON", ":/data/img/layers_TI_Holes.svg")
        QtCore.QObject.connect(scriptCmd_cutHolesThroughAllLayersON, QtCore.SIGNAL("triggered()"), partial(self.cutHolesThroughAllLayers, True))
        
        scriptCmd_cutHolesThroughAllLayersON2 = self.createAction(u"Cut holes through all layers - ON", u"Cut holes through all layers - ON", ":/data/img/layers_TI_Holes.svg")
        QtCore.QObject.connect(scriptCmd_cutHolesThroughAllLayersON2, QtCore.SIGNAL("triggered()"), partial(self.cutHolesThroughAllLayers, True))
        
        scriptCmd_cutHolesThroughAllLayersOFF = self.createAction(u"Cut holes through all layers - OFF", u"Cut holes through all layers - OFF", ":/data/img/layers_TI.svg")
        QtCore.QObject.connect(scriptCmd_cutHolesThroughAllLayersOFF, QtCore.SIGNAL("triggered()"), partial(self.cutHolesThroughAllLayers, False))
        
        groupsMenuCH = QtGui.QMenu(self)
        groupsMenuCH.addAction(scriptCmd_cutHolesThroughAllLayersON2)
        groupsMenuCH.addAction(scriptCmd_cutHolesThroughAllLayersOFF)
        scriptCmd_cutHolesThroughAllLayersON.setMenu(groupsMenuCH)
        # rendering
        scriptCmd_ExportToKerkythea = self.createAction(u"3D rendering: export to Kerkythea", u"3D rendering: export to Kerkythea", ":/data/img/kticon.ico")
        QtCore.QObject.connect(scriptCmd_ExportToKerkythea, QtCore.SIGNAL("triggered()"), self.exportToKerkytheaF)
        
        scriptCmd_ExportObjectToPovRay = self.createAction(u"3D rendering: export object to POV-Ray (*.inc)", u"3D rendering: export object to POV-Ray (*.inc)", ":/data/img/povray.ico")
        QtCore.QObject.connect(scriptCmd_ExportObjectToPovRay, QtCore.SIGNAL("triggered()"), self.exportObjectToPovRayF)
        
        # assembly
        scriptCmd_QuickAssembly = self.createAction(u"Add assembly", u"Add assembly", ":/data/img/asmMain.png")
        QtCore.QObject.connect(scriptCmd_QuickAssembly, QtCore.SIGNAL("triggered()"), self.quickAssembly)
        
        scriptCmd_QuickAssembly2 = self.createAction(u"Update assembly", u"Update assembly", ":/data/img/asmUpdate.png")
        QtCore.QObject.connect(scriptCmd_QuickAssembly2, QtCore.SIGNAL("triggered()"), self.quickAssemblyUpdate)
        
        scriptCmd_exportAssembly = self.createAction(u"Generate one object from the board", u"Generate one object from the board", ":/data/img/asmUpdate.png")
        QtCore.QObject.connect(scriptCmd_exportAssembly, QtCore.SIGNAL("triggered()"), self.exportAssembly)

        scriptCmd_CheckForCollisions = self.createAction(u"Check for collisions", u"Check for collisions", ":/data/img/collisions.png")
        QtCore.QObject.connect(scriptCmd_CheckForCollisions, QtCore.SIGNAL("triggered()"), self.checkForCollisionsF)
        
        # parts groups
        scriptCmd_ungroupParts = self.createAction(u"Ungroup parts", u"Ungroup parts", ":/data/img/ungroup.svg")
        QtCore.QObject.connect(scriptCmd_ungroupParts, QtCore.SIGNAL("triggered()"), self.ungroupParts)
        
        scriptCmd_groupParts = self.createAction(u"Group parts", u"Group parts", ":/data/img/group.svg")
        QtCore.QObject.connect(scriptCmd_groupParts, QtCore.SIGNAL("triggered()"), self.groupParts)
        
        ##########
        self.addAction(scriptCmd_viewShaded)
        self.addAction(scriptCmd_viewFlatLines)
        self.addAction(scriptCmd_viewWireframe)
        self.addAction(scriptCmd_viewInternalView)
        self.addSeparator()
        self.addAction(scriptCmd_Layers)
        self.addSeparator()
        self.addAction(scriptCmd_cutHolesThroughAllLayersON)
        self.addAction(scriptCmd_cutToBoardOutlineON)
        self.addAction(scriptCmd_showSignals)
        self.addAction(scriptCmd_ungroupParts)
        self.addAction(scriptCmd_groupParts)
        self.addSeparator()
        self.addAction(scriptCmd_ExportToKerkythea)
        self.addAction(scriptCmd_ExportObjectToPovRay)
        #self.addSeparator()
        #self.addAction(scriptCmd_QuickAssembly)
        #self.addAction(scriptCmd_QuickAssembly2)
        #self.addAction(scriptCmd_exportAssembly)
        #self.addAction(scriptCmd_CheckForCollisions)
        self.addToolBar(self)
    
    def cutHolesThroughAllLayers(self, value):
        pcb = getPCBheight()
        if pcb[0]:  # board is available
            for i in pcb[2].Group:
                if hasattr(i, "Cut") and not i.Cut == value:
                    i.Cut = value
    
    def showSignals(self, value):
        pcb = getPCBheight()
        if pcb[0]:  # board is available
            colorsList = {}
            
            for i in pcb[2].Group:
                if hasattr(i, "Proxy") and hasattr(i.Proxy, "Type") and isinstance(i.Proxy.Type, list) and "paths" in i.Proxy.Type:
                    if value:
                        colorsList = i.Proxy.colorizePaths(i, colorsList)
                    else:
                        i.Proxy.resetColors(i)
    
    def cutToBoardOutline(self, value):
        pcb = getPCBheight()
        if pcb[0]:  # board is available
            for i in pcb[2].Group:
                if hasattr(i, "CutToBoard") and not i.CutToBoard == value:
                    i.CutToBoard = value
    
    def ungroupParts(self):
        pcb = getPCBheight()
        if pcb[0]:  # board is available
            groupsToDelete = []
            pM = partsManaging()
            
            for i in pcb[2].Group:
                if hasattr(i, "Proxy") and hasattr(i.Proxy, "Type") and i.Proxy.Type in ["PCBpart", "PCBpart_E"]:
                    if not i.getParentGroup().Name in groupsToDelete:
                        groupsToDelete.append(i.getParentGroup().Name)
                    
                    pM.addPartToGroup(False, i)
            
            for i in groupsToDelete:
                if i == "Parts":
                    continue
                
                try:
                    FreeCAD.ActiveDocument.removeObject(i)
                except Exception as e:
                    FreeCAD.Console.PrintWarning("{0} \n".format(e))

    def groupParts(self):
        pcb = getPCBheight()
        if pcb[0]:  # board is available
            pM = partsManaging()
            pM.setDatabase()
            
            for i in pcb[2].Group:
                if hasattr(i, "Proxy") and hasattr(i.Proxy, "Type") and i.Proxy.Type in ["PCBpart", "PCBpart_E"]:
                    pM.addPartToGroup(True, i)
    
    def exportAssembly(self):
        exportAssembly()

    def quickAssembly(self):
        try:
            if FreeCAD.activeDocument():
                FreeCADGui.Control.showDialog(createAssemblyGui())
        except Exception as e:
            FreeCAD.Console.PrintWarning("{0} \n".format(e))
        
    def quickAssemblyUpdate(self):
        try:
            if FreeCAD.activeDocument():
                updateAssembly()
        except Exception as e:
            FreeCAD.Console.PrintWarning("{0} \n".format(e))
    
    def checkForCollisionsF(self):
        try:
            if FreeCAD.activeDocument():
                FreeCADGui.Control.showDialog(checkCollisionsGui())
        except Exception as e:
            FreeCAD.Console.PrintWarning("{0} \n".format(e))
    
    def exportToKerkytheaF(self):
        if FreeCAD.activeDocument():
            FreeCADGui.Control.showDialog(exportToKerkytheaGui())
            
    def exportObjectToPovRayF(self):
        if FreeCAD.activeDocument():
            FreeCADGui.Control.showDialog(exportObjectToPovRayGui())
    
    def Flayers(self):
        pcb = getPCBheight()
        if FreeCAD.activeDocument() and pcb[0]:
            if not FreeCADGui.Control.activeDialog():
                FreeCADGui.Control.showDialog(layersSettings())

    def changeDisplayMode(self, mode):
        hidePCB = False
        if mode == 'Internal View':
            mode = 'Shaded'
            hidePCB = True
        #
        try:
            obj = FreeCAD.ActiveDocument.Objects
        except:
            obj = []
        
        if len(obj):
            for i in obj:
                if mode in i.ViewObject.listDisplayModes():
                    #if hasattr(i, "Proxy") and hasattr(i, "Type") and type(i.Proxy.Type) == list:
                        #if 'tSilk' in i.Proxy.Type or 'bSilk' in i.Proxy.Type or 'tDocu' in i.Proxy.Type or 'bDocu' in i.Proxy.Type:
                            #continue
                    i.ViewObject.DisplayMode = mode
        #
        if hidePCB:
            try:
                FreeCAD.ActiveDocument.Board.ViewObject.DisplayMode = 'Wireframe'
            except Exception as e:
                pass


###########
class pcbToolBar(pcbToolBarMain):
    def __init__(self, parent=None):
        pcbToolBarMain.__init__(self, 'PCB Settings', parent)
        self.setObjectName("pcbToolBar")
        
        self.szukaneFrazy = []
        self.szukaneFrazyNr = 0

        ####### przyciski
        scriptCmd_CreatePCB = self.createAction(u"Create PCB", u"Create PCB", ":/data/img/board.png")
        QtCore.QObject.connect(scriptCmd_CreatePCB, QtCore.SIGNAL("triggered()"), self.createPCB_F)
        
        scriptCmd_CreateGluePath = self.createAction(u"Create glue path", u"Create glue path", ":/data/img/gluePath.png")
        QtCore.QObject.connect(scriptCmd_CreateGluePath, QtCore.SIGNAL("triggered()"), self.createGluePath)
 
        scriptCmd_Assign = self.createAction(u"Assign models", u"Assign models", ":/data/img/assignModels.png")
        QtCore.QObject.connect(scriptCmd_Assign, QtCore.SIGNAL("triggered()"), self.assignModels)
        
        scriptCmd_AddModel = self.createAction(u"Add model", u"Add model", ":/data/img/addNewModel.png")
        QtCore.QObject.connect(scriptCmd_AddModel, QtCore.SIGNAL("triggered()"), self.addModel)
        
        scriptCmd_UpdateModels = self.createAction(u"Update models", u"Update models", ":/data/img/updateModels.png")
        QtCore.QObject.connect(scriptCmd_UpdateModels, QtCore.SIGNAL("triggered()"), self.updateModels)
        
        scriptCmd_DownloadModels = self.createAction(u"Download models", u"Download models", ":/data/img/downloadModels.png")
        QtCore.QObject.connect(scriptCmd_DownloadModels, QtCore.SIGNAL("triggered()"), self.downloadModels)
        #
        scriptCmd_Explode = self.createAction(u"Explode", u"Explode", ":/data/img/explode.png")
        QtCore.QObject.connect(scriptCmd_Explode, QtCore.SIGNAL("triggered()"), self.explodeModels)
        scriptCmd_Explode1 = self.createAction(u"Explode", u"Explode", ":/data/img/explode.png")
        QtCore.QObject.connect(scriptCmd_Explode1, QtCore.SIGNAL("triggered()"), self.explodeModels)
        scriptCmd_FastExplode = self.createAction(u"Fast explode", u"Fast explode", ":/data/img/explode.png")
        QtCore.QObject.connect(scriptCmd_FastExplode, QtCore.SIGNAL("triggered()"), self.fastExplodeModels)
        
        groupsMenu = QtGui.QMenu(self)
        groupsMenu.addAction(scriptCmd_Explode1)
        groupsMenu.addAction(scriptCmd_FastExplode)
        scriptCmd_Explode.setMenu(groupsMenu)
        # Bounding Box
        scriptCmd_BoundingBox_M = self.createAction(u"Bounding box", u"Bounding box", ":/data/img/boundingBoxAll.svg")
        QtCore.QObject.connect(scriptCmd_BoundingBox_M, QtCore.SIGNAL("triggered()"), self.showPCBBoundingBox)
        scriptCmd_BoundingBox = self.createAction(u"Bounding box", u"Bounding box", ":/data/img/boundingBoxAll.svg")
        QtCore.QObject.connect(scriptCmd_BoundingBox, QtCore.SIGNAL("triggered()"), self.showPCBBoundingBox)
        scriptCmd_BoundingBoxSel = self.createAction(u"Bounding box from selection", u"Bounding box from selection", ":/data/img/boundingBoxSelected.svg")
        QtCore.QObject.connect(scriptCmd_BoundingBoxSel, QtCore.SIGNAL("triggered()"), self.showPCBBoundingBoxSel)
        
        boundingBoxMenu = QtGui.QMenu(self)
        boundingBoxMenu.addAction(scriptCmd_BoundingBox)
        boundingBoxMenu.addAction(scriptCmd_BoundingBoxSel)
        scriptCmd_BoundingBox_M.setMenu(boundingBoxMenu)
        # sections
        scriptCmd_crossSections_M = self.createAction(u"Cross sections", u"Create sections from selected models and export them as library", ":/data/img/Part_CrossSections.svg")
        QtCore.QObject.connect(scriptCmd_crossSections_M, QtCore.SIGNAL("triggered()"), self.createSectionsSelParts)
        # scriptCmd_crossSections = self.createAction(u"Cross sections", u"Create sections from selected models and export them as library", ":/data/img/Part_CrossSections.svg")
        # QtCore.QObject.connect(scriptCmd_crossSections, QtCore.SIGNAL("triggered()"), self.createSectionsSelParts)
        # scriptCmd_crossSectionsPCB = self.createAction(u"Cross sections from whole PCB", u"Create sections from PCB board (with components) and export them as library", ":/data/img/Part_CrossSections.svg")
        # QtCore.QObject.connect(scriptCmd_crossSectionsPCB, QtCore.SIGNAL("triggered()"), self.showPCBBoundingBoxSel)
        
        # crossSectionsMenu = QtGui.QMenu(self)
        # crossSectionsMenu.addAction(scriptCmd_crossSections)
        # crossSectionsMenu.addAction(scriptCmd_crossSectionsPCB)
        # scriptCmd_crossSections_M.setMenu(crossSectionsMenu)
        # groups
        scriptCmd_addAllGroup = self.createAction(u"Create new project", u"Create new project", ":/data/img/folder_open_22x22.png")
        QtCore.QObject.connect(scriptCmd_addAllGroup, QtCore.SIGNAL("triggered()"), self.addAllGroups)
        scriptCmd_addLayerGroup = self.createAction(u"Add layers group", u"Add layers group", ":/data/img/folder_open_22x22.png")
        QtCore.QObject.connect(scriptCmd_addLayerGroup, QtCore.SIGNAL("triggered()"), self.addLayerGroup)
        scriptCmd_addPartsGroup = self.createAction(u"Add parts group", u"Add parts group", ":/data/img/folder_open_22x22.png")
        QtCore.QObject.connect(scriptCmd_addPartsGroup, QtCore.SIGNAL("triggered()"), self.addPartsGroup)
        scriptCmd_addPCBGroup = self.createAction(u"Add PCB group", u"Add PCB group", ":/data/img/folder_open_22x22.png")
        QtCore.QObject.connect(scriptCmd_addPCBGroup, QtCore.SIGNAL("triggered()"), self.addPCBGroup)
        scriptCmd_addAreasGroup = self.createAction(u"Add areas group", u"Add areas group", ":/data/img/folder_open_22x22.png")
        QtCore.QObject.connect(scriptCmd_addAreasGroup, QtCore.SIGNAL("triggered()"), self.addAreasGroup)
        scriptCmd_addAnnotationsGroup = self.createAction(u"Add annotations group", u"Add annotations group", ":/data/img/folder_open_22x22.png")
        QtCore.QObject.connect(scriptCmd_addAnnotationsGroup, QtCore.SIGNAL("triggered()"), self.addAnnotationsGroup)
        scriptCmd_addGlueGroup = self.createAction(u"Add glue group", u"Add annotations group", ":/data/img/folder_open_22x22.png")
        QtCore.QObject.connect(scriptCmd_addGlueGroup, QtCore.SIGNAL("triggered()"), self.addGlueGroup)
        
        groupsMenu = QtGui.QMenu(self)
        groupsMenu.addAction(scriptCmd_addPCBGroup)
        groupsMenu.addAction(scriptCmd_addPartsGroup)
        groupsMenu.addAction(scriptCmd_addLayerGroup)
        groupsMenu.addAction(scriptCmd_addAreasGroup)
        groupsMenu.addAction(scriptCmd_addAnnotationsGroup)
        groupsMenu.addAction(scriptCmd_addGlueGroup)
        scriptCmd_addAllGroup.setMenu(groupsMenu)
        ##### constraints areas
        self.scriptCmd_constraintsAreas = self.createAction(u"Create constraint area", u"Create constraint area", ":/data/img/constraintsArea.png")
        QtCore.QObject.connect(self.scriptCmd_constraintsAreas, QtCore.SIGNAL("triggered()"), self.defConstraintAreaF)
        
        constraintsAreasMenu = QtGui.QMenu(self)
        self.scriptCmd_constraintsAreas.setMenu(constraintsAreasMenu)
        self.scriptCmd_constraintsAreas.setDisabled(True)
        # Route Outline
        constraintsAreaRouteOutlineTop = self.createAction(u"Top", u"Route Outline Top", ":/data/img/constraintsArea.png")
        par = partial(self.constraintAreaF, "tRouteOutline")
        QtCore.QObject.connect(constraintsAreaRouteOutlineTop, QtCore.SIGNAL("triggered()"), par)
        constraintsAreaRouteOutlineBottom = self.createAction(u"Bottom", u"Route Outline Bottom", ":/data/img/constraintsArea.png")
        par = partial(self.constraintAreaF, "bRouteOutline")
        QtCore.QObject.connect(constraintsAreaRouteOutlineBottom, QtCore.SIGNAL("triggered()"), par)
        constraintsAreaRouteOutlineBoth = self.createAction(u"Both", u"Route Outline Both", ":/data/img/constraintsArea.png")
        par = partial(self.constraintAreaF, "vRouteOutline")
        QtCore.QObject.connect(constraintsAreaRouteOutlineBoth, QtCore.SIGNAL("triggered()"), par)
        
        constraintsAreaRouteOutlineMenu = QtGui.QMenu("Route Outline", constraintsAreasMenu)
        constraintsAreaRouteOutlineMenu.addAction(constraintsAreaRouteOutlineTop)
        constraintsAreaRouteOutlineMenu.addAction(constraintsAreaRouteOutlineBottom)
        constraintsAreaRouteOutlineMenu.addAction(constraintsAreaRouteOutlineBoth)
        constraintsAreasMenu.addMenu(constraintsAreaRouteOutlineMenu)
        # Place Outline
        constraintsAreaPlaceOutlineTop = self.createAction(u"Top", u"Place Outline Top", ":/data/img/constraintsArea.png")
        par = partial(self.constraintAreaF, "tPlaceOutline")
        QtCore.QObject.connect(constraintsAreaPlaceOutlineTop, QtCore.SIGNAL("triggered()"), par)
        constraintsAreaPlaceOutlineBottom = self.createAction(u"Bottom", u"Place Outline Bottom", ":/data/img/constraintsArea.png")
        par = partial(self.constraintAreaF, "bPlaceOutline")
        QtCore.QObject.connect(constraintsAreaPlaceOutlineBottom, QtCore.SIGNAL("triggered()"), par)
        constraintsAreaPlaceOutlineBoth = self.createAction(u"Both", u"Place Outline Both", ":/data/img/constraintsArea.png")
        par = partial(self.constraintAreaF, "vPlaceOutline")
        QtCore.QObject.connect(constraintsAreaPlaceOutlineBoth, QtCore.SIGNAL("triggered()"), par)

        constraintsAreaPlaceOutlineMenu = QtGui.QMenu("Place Outline", constraintsAreasMenu)
        constraintsAreaPlaceOutlineMenu.addAction(constraintsAreaPlaceOutlineTop)
        constraintsAreaPlaceOutlineMenu.addAction(constraintsAreaPlaceOutlineBottom)
        constraintsAreaPlaceOutlineMenu.addAction(constraintsAreaPlaceOutlineBoth)
        constraintsAreasMenu.addMenu(constraintsAreaPlaceOutlineMenu)
        # Place Keepout
        constraintsAreaPlaceKeepoutTop = self.createAction(u"Top", u"Place Keepout Top", ":/data/img/constraintsArea.png")
        par = partial(self.constraintAreaF, "tPlaceKeepout")
        QtCore.QObject.connect(constraintsAreaPlaceKeepoutTop, QtCore.SIGNAL("triggered()"), par)
        constraintsAreaPlaceKeepoutBottom = self.createAction(u"Bottom", u"Place Keepout Bottom", ":/data/img/constraintsArea.png")
        par = partial(self.constraintAreaF, "bPlaceKeepout")
        QtCore.QObject.connect(constraintsAreaPlaceKeepoutBottom, QtCore.SIGNAL("triggered()"), par)

        constraintsAreaPlaceKeepoutMenu = QtGui.QMenu("Place Keepout", constraintsAreasMenu)
        constraintsAreaPlaceKeepoutMenu.addAction(constraintsAreaPlaceKeepoutTop)
        constraintsAreaPlaceKeepoutMenu.addAction(constraintsAreaPlaceKeepoutBottom)
        constraintsAreasMenu.addMenu(constraintsAreaPlaceKeepoutMenu)
        # Route Keepout
        constraintsAreaRouteKeepoutTop = self.createAction(u"Top", u"Route Keepout Top", ":/data/img/constraintsArea.png")
        par = partial(self.constraintAreaF, "tRouteKeepout")
        QtCore.QObject.connect(constraintsAreaRouteKeepoutTop, QtCore.SIGNAL("triggered()"), par)
        constraintsAreaRouteKeepoutBottom = self.createAction(u"Bottom", u"Route Keepout Bottom", ":/data/img/constraintsArea.png")
        par = partial(self.constraintAreaF, "bRouteKeepout")
        QtCore.QObject.connect(constraintsAreaRouteKeepoutBottom, QtCore.SIGNAL("triggered()"), par)
        constraintsAreaRouteKeepoutBoth = self.createAction(u"Both", u"Route Keepout Both", ":/data/img/constraintsArea.png")
        par = partial(self.constraintAreaF, "vRouteKeepout")
        QtCore.QObject.connect(constraintsAreaRouteKeepoutBoth, QtCore.SIGNAL("triggered()"), par)

        constraintsAreaRouteKeepoutMenu = QtGui.QMenu("Route Keepout", constraintsAreasMenu)
        constraintsAreaRouteKeepoutMenu.addAction(constraintsAreaRouteKeepoutTop)
        constraintsAreaRouteKeepoutMenu.addAction(constraintsAreaRouteKeepoutBottom)
        constraintsAreaRouteKeepoutMenu.addAction(constraintsAreaRouteKeepoutBoth)
        constraintsAreasMenu.addMenu(constraintsAreaRouteKeepoutMenu)
        ##########
        scriptCmd_Export = self.createAction(u"Export board", u"Export board", ":/data/img/exportPCB.png")
        QtCore.QObject.connect(scriptCmd_Export, QtCore.SIGNAL("triggered()"), self.exportPCB)
        ##
        scriptCmd_ExportBOM = self.createAction(u"Export BOM", u"Export BOM", ":/data/img/exportBOM.png")
        QtCore.QObject.connect(scriptCmd_ExportBOM, QtCore.SIGNAL("triggered()"), self.exportBOM)
        
        scriptCmd_ExportBOM_2 = self.createAction(u"Export BOM", u"Export BOM", ":/data/img/exportBOM.png")
        QtCore.QObject.connect(scriptCmd_ExportBOM_2, QtCore.SIGNAL("triggered()"), self.exportBOM)
        
        scriptCmd_centroid = self.createAction(u"Centroid", u"Centroid", ":/data/img/centroid.svg")
        QtCore.QObject.connect(scriptCmd_centroid, QtCore.SIGNAL("triggered()"), self.exportCentroid)
        
        groupsMenu = QtGui.QMenu(self)
        groupsMenu.addAction(scriptCmd_ExportBOM_2)
        groupsMenu.addAction(scriptCmd_centroid)
        scriptCmd_ExportBOM.setMenu(groupsMenu)
        
        # export drills
        scriptCmd_ExportHoleLocations = self.createAction(u"Export hole locations", u"Export hole locations", ":/data/img/drilling.svg")
        QtCore.QObject.connect(scriptCmd_ExportHoleLocations, QtCore.SIGNAL("triggered()"), self.exportHoleLocations)
        
        scriptCmd_ExportHoleLocations_2 = self.createAction(u"Export hole locations", u"Export hole locations", ":/data/img/centroid.svg")
        QtCore.QObject.connect(scriptCmd_ExportHoleLocations_2, QtCore.SIGNAL("triggered()"), self.exportHoleLocations)
        
        scriptCmd_ExportHoleLocationsReport = self.createAction(u"Export hole locations report", u"Export hole locations report", ":/data/img/drilling.svg")
        QtCore.QObject.connect(scriptCmd_ExportHoleLocationsReport, QtCore.SIGNAL("triggered()"), self.exportHoleLocationsReport)
        
        scriptCmd_ExportDrillingMap = self.createAction(u"Create drilling map", u"Create drilling map", ":/data/img/drilling.svg")
        QtCore.QObject.connect(scriptCmd_ExportDrillingMap, QtCore.SIGNAL("triggered()"), self.exportDrillingMap)
        
        scriptCmd_CreateCenteDrill = self.createAction(u"Create drill center", u"Create drill center", ":/data/img/drilling.svg")
        QtCore.QObject.connect(scriptCmd_CreateCenteDrill, QtCore.SIGNAL("triggered()"), self.createCenteDrill)
        
        groupsMenu = QtGui.QMenu(self)
        groupsMenu.addAction(scriptCmd_ExportHoleLocations_2)
        groupsMenu.addAction(scriptCmd_ExportHoleLocationsReport)
        groupsMenu.addAction(scriptCmd_ExportDrillingMap)
        #groupsMenu.addSeparator()
        #groupsMenu.addAction(scriptCmd_CreateCenteDrill)
        scriptCmd_ExportHoleLocations.setMenu(groupsMenu)
        ##########
        self.wyszukajElementy = QtGui.QLineEdit('')
        self.wyszukajElementy.setFixedWidth(120)
        QtCore.QObject.connect(self.wyszukajElementy, QtCore.SIGNAL("textChanged (const QString&)"), self.wyszukajObiekty)

        scriptCmd_PreviousPackage = self.createAction(u"Previous package", u"Previous package", ":/data/img/previous_16x16.png")
        QtCore.QObject.connect(scriptCmd_PreviousPackage, QtCore.SIGNAL("triggered()"), self.wyszukajObiektyPrev)
        
        scriptCmd_NextPackage = self.createAction(u"Next package", u"Next package", ":/data/img/next_16x16.png")
        QtCore.QObject.connect(scriptCmd_NextPackage, QtCore.SIGNAL("triggered()"), self.wyszukajObiektyNext)
        ##########
        scriptCmd_addAnnotation = self.createAction(u"Add annotation", u"Add annotation",  ":/data/img/addAnnotation.svg")
        QtCore.QObject.connect(scriptCmd_addAnnotation, QtCore.SIGNAL("triggered()"), self.addAnnotation)

        scriptCmd_storeNameValueAsParam = self.createAction(u"Store Name/Value as param", u"Store Name/Value as param",  ":/data/img/modelAddAnnotation.svg")
        QtCore.QObject.connect(scriptCmd_storeNameValueAsParam, QtCore.SIGNAL("triggered()"), self.storeNameValueAsParam)
        ##########
        self.addAction(scriptCmd_Export)
        self.addAction(scriptCmd_ExportBOM)
        self.addAction(scriptCmd_ExportHoleLocations)
        #self.addAction(scriptCmd_ImportSTP)
        self.addSeparator()
        self.addAction(scriptCmd_addAllGroup)
        self.addAction(scriptCmd_CreatePCB)
        self.addAction(scriptCmd_CreateGluePath)
        self.addAction(scriptCmd_addAnnotation)
        self.addAction(scriptCmd_storeNameValueAsParam)
        self.addSeparator()
        self.addAction(scriptCmd_Assign)
        self.addAction(scriptCmd_AddModel)
        self.addAction(scriptCmd_UpdateModels)
        self.addAction(scriptCmd_DownloadModels)
        self.addSeparator()
        self.addAction(scriptCmd_Explode)
        self.addAction(self.scriptCmd_constraintsAreas)
        self.addAction(scriptCmd_BoundingBox_M)
        self.addAction(scriptCmd_crossSections_M)
        #self.addAction(scriptCmd_Convert)
        self.addSeparator()
        self.addAction(scriptCmd_PreviousPackage)
        self.addWidget(self.wyszukajElementy)
        self.addAction(scriptCmd_NextPackage)
        #
        self.addToolBar(self)
    
    def storeNameValueAsParam(self):
        sel = FreeCADGui.Selection.getSelection()
        if not FreeCAD.activeDocument():
            return
        elif len(sel) > 1:
            FreeCAD.Console.PrintWarning("Select only one part.\n")
            return
        elif not len(sel):
            FreeCAD.Console.PrintWarning("No part selected.\n")
            return
        elif hasattr(sel[0], "Proxy") and hasattr(sel[0].Proxy, "Type") and not sel[0].Proxy.Type in ["PCBpart"]:
            FreeCAD.Console.PrintWarning("Wrong part type selected.\n")
            return
        
        pcb = getPCBheight()
        if not pcb[0]:
            FreeCAD.Console.PrintWarning("PCB not found.\n")
            return
        #
        sql = dataBase()
        sql.connect()
        
        model = sel[0]
        #
        packageData = sql.findPackage(model.Package, '*')
        if packageData:
            modelData = sql.getModelByID(packageData.modelID)
            if modelData[0]:
                
                [mX, mY, mROT, mSIDE] = [model.X.Value, model.Y.Value, model.Rot.Value, model.Side]
                model.X.Value = 0
                model.Y.Value = 0
                model.Rot.Value = 0
                model.Side = "TOP"
                ###############################
                modelData = modelData[1]
                # NAME
                if model.PartName:
                    #
                    nameParam = model.PartName
                    
                    table = {
                        'active': True,
                        'display': str(nameParam.ViewObject.Visibility),
                        'x': model.X.Value - nameParam.X.Value,
                        'y': nameParam.Y.Value - model.Y.Value,
                        'z': nameParam.Z.Value - model.Socket.Value - pcb[1],
                        'rz': nameParam.Rot.Value + ( model.Rot.Value * -1),
                        'size': nameParam.Size,
                        'color': nameParam.ViewObject.ShapeColor,
                        'align': nameParam.Justification,
                        'spin': str(nameParam.Spin)
                    }
                    #
                    paramData = sql.getParamsByModelID(modelData.id, 'Name')
                    if isinstance(paramData, list):  # new param
                        sql.addNewParam(modelData.id, 'Name', table)
                    else:
                        sql.updateParam(paramData[0].id, table)
                # VALUE
                if model.PartValue:
                    #
                    nameParam = model.PartValue
                    
                    table = {
                        'active': True,
                        'display': str(nameParam.ViewObject.Visibility),
                        'x': model.X.Value - nameParam.X.Value,
                        'y': nameParam.Y.Value - model.Y.Value,
                        'z': nameParam.Z.Value - model.Socket.Value - pcb[1],
                        'rz': nameParam.Rot.Value + ( model.Rot.Value * -1),
                        'size': nameParam.Size,
                        'color': nameParam.ViewObject.ShapeColor,
                        'align': nameParam.Justification,
                        'spin': str(nameParam.Spin)
                    }
                    #
                    paramData = sql.getParamsByModelID(modelData.id, 'Value')
                    if isinstance(paramData, list):  # new param
                        sql.addNewParam(modelData.id, 'Value', table)
                    else:
                        sql.updateParam(paramData[0].id, table)
                ###############################
                model.X.Value = mX
                model.Y.Value = mY
                model.Rot.Value = mROT
                model.Side = mSIDE
            
    def addAnnotation(self):
        if FreeCAD.activeDocument() and getPCBheight()[0]:
            if not FreeCADGui.Control.activeDialog():
                FreeCADGui.Control.showDialog(createAnnotation_Gui())

    def exportHoleLocations(self):
        if FreeCAD.activeDocument() and getPCBheight()[0]:
            exportHoles_Gui().exec_()
    
    def exportHoleLocationsReport(self):
        if FreeCAD.activeDocument() and getPCBheight()[0]:
            exportHolesReport_Gui().exec_()
            
    def createCenteDrill(self):
        if FreeCAD.activeDocument() and getPCBheight()[0]:
            try:
                form = createDrillcenter_Gui()
                FreeCADGui.Control.showDialog(form)
            except Exception as e:
                FreeCAD.Console.PrintWarning("{0} \n".format(e))
    
    def exportDrillingMap(self):
        if FreeCAD.activeDocument() and getPCBheight()[0]:
            exportDrillingMap_Gui().exec_()

    def exportBOM(self):
        ''' load export bom to file '''
        if FreeCAD.activeDocument() and getPCBheight()[0]:
            exportBOM_Gui().exec_()
            
    def exportCentroid(self):
        ''' also known as Insertion or pick-and-place or XY data '''
        if FreeCAD.activeDocument() and getPCBheight()[0]:
            createCentroid_Gui().exec_()
    
    def exportPCB(self):
        ''' export project to one supported file format '''
        if FreeCAD.activeDocument() and getPCBheight()[0]:
            exportPCB_Gui().exec_()
    
    def defConstraintAreaF(self):
        ''' create constraint are dialog '''
        dial = QtGui.QDialog()
        dial.setWindowTitle("Create constraint area")
        # areas list
        lista = QtGui.QListWidget()
        for i, j in PCBconstraintAreas.items():
            a = QtGui.QListWidgetItem(j[0])
            a.setData(QtCore.Qt.UserRole, i)
            
            lista.addItem(a)
        lista.sortItems()
        ##########
        # przyciski
        buttons = QtGui.QDialogButtonBox()
        buttons.setOrientation(QtCore.Qt.Vertical)
        buttons.addButton("Cancel", QtGui.QDialogButtonBox.RejectRole)
        buttons.addButton("Create", QtGui.QDialogButtonBox.AcceptRole)
        dial.connect(buttons, QtCore.SIGNAL("accepted()"), dial, QtCore.SLOT("accept()"))
        dial.connect(buttons, QtCore.SIGNAL("rejected()"), dial, QtCore.SLOT("reject()"))
        ####
        lay = QtGui.QGridLayout()
        lay.addWidget(lista, 0, 0, 1, 1)
        lay.addWidget(buttons, 0, 1, 1, 1)
        dial.setLayout(lay)
        
        if dial.exec_():
            self.constraintAreaF(str(lista.currentItem().data(QtCore.Qt.UserRole)))

    def constraintAreaF(self, typeCA):
        ''' create constraint area '''
        zaznaczoneObiekty = FreeCADGui.Selection.getSelection()

        if len(zaznaczoneObiekty) and getPCBheight()[0]:
            #grp = createGroup_Areas()
            for i in zaznaczoneObiekty:
                try:
                    createConstraintArea(i, typeCA)
                except Exception as e:
                    continue
                    #FreeCAD.Console.PrintWarning("Error: {0}\n".format(e))
        elif not pcb[0]:
            FreeCAD.Console.PrintWarning("No PCB found\n")
    
    def createSectionsSelParts(self):
        if FreeCAD.activeDocument():
            if len(FreeCADGui.Selection.getSelection()):
                if not FreeCADGui.Control.activeDialog():
                    FreeCADGui.Control.showDialog(createSectionsGui())
            else:
                FreeCAD.Console.PrintWarning("Select minimum one object\n")
        
    def createGluePath(self):
        if FreeCAD.activeDocument() and getPCBheight()[0]:
            if not FreeCADGui.Control.activeDialog():
                FreeCADGui.Control.showDialog(createGlueGui())
            
    def createPCB_F(self):
        if FreeCAD.activeDocument():
            if getPCBheight()[0]:
                FreeCAD.Console.PrintWarning("One board per project.\n")
                return
            #
            form = createPCB()
            if len(FreeCADGui.Selection.getSelection()):
                if FreeCADGui.Selection.getSelection()[0].isDerivedFrom("Sketcher::SketchObject"):
                    form.pcbBorder.setText(FreeCADGui.Selection.getSelection()[0].Name)
                    if len(FreeCADGui.Selection.getSelection()) > 1 and FreeCADGui.Selection.getSelection()[1].isDerivedFrom("Sketcher::SketchObject"):
                        form.pcbHoles.setText(FreeCADGui.Selection.getSelection()[1].Name)
            if not FreeCADGui.Control.activeDialog():
                FreeCADGui.Control.showDialog(form)

    def addAllGroups(self):
        ''' add to current document all groups '''
        setProject()
    
    def addAreasGroup(self):
        createGroup_Areas()
        
    def addAnnotationsGroup(self):
        createGroup_Annotations()
        
    def addPCBGroup(self):
        createGroup_PCB()

    def addLayerGroup(self):
        createGroup_Layers()
        
    def addPartsGroup(self):
        createGroup_Parts()
        
    def addGlueGroup(self):
        createGroup_Glue()
        
    def fastExplodeModels(self):
        if FreeCAD.activeDocument():
            doc = FreeCAD.activeDocument()
            pcb = getPCBheight()
            
            if pcb[0]:  # board is available
                a = doc.addObject("App::FeaturePython", 'Explode')
                obj = explodeObject(a)
                viewProviderExplodeObject(a.ViewObject)
                #
                for i in pcb[2].Group:
                    if hasattr(i, "Proxy") and hasattr(i.Proxy, "Type") and i.Proxy.Type in ["PCBpart"]:
                        if i.Side == "TOP":
                            obj.spisObiektowGora[i.Name] = [doc.getObject(i.Name).Placement.Base.z, 3]
                        else:
                            obj.spisObiektowDol[i.Name] = [doc.getObject(i.Name).Placement.Base.z, 3]
                #
                obj.setParam(a, 'Inverse', False)
                obj.setParam(a, 'Active', True)
                obj.setParam(a, 'TopStepSize', 10)
                obj.setParam(a, 'BottomStepSize', 10)
                obj.generuj(a)

    def explodeModels(self):
        doc = FreeCAD.activeDocument()
        if doc and len(doc.Objects):
            panel = explodeWizard()
            if not FreeCADGui.Control.activeDialog():
                FreeCADGui.Control.showDialog(panel)
            
    def wyszukajObiektyNext(self):
        ''' find next object '''
        try:
            if len(self.szukaneFrazy):
                if self.szukaneFrazyNr < len(self.szukaneFrazy) - 1:
                    self.szukaneFrazyNr += 1
                else:
                    self.szukaneFrazyNr = 0
                
                FreeCADGui.Selection.clearSelection()
                FreeCADGui.Selection.addSelection(self.szukaneFrazy[self.szukaneFrazyNr])
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
                
                FreeCADGui.Selection.clearSelection()
                FreeCADGui.Selection.addSelection(self.szukaneFrazy[self.szukaneFrazyNr])
        except RuntimeError:
            self.szukaneFrazy = []
            self.szukaneFrazyNr = 0
        
    def wyszukajObiekty(self, fraza):
        ''' find object in current document '''
        try:
            FreeCADGui.Selection.clearSelection()
            self.szukaneFrazy = []
            self.szukaneFrazyNr = 0
            
            fraza = str(fraza).strip()
            if fraza != "":
                pcb = getPCBheight()
                if pcb[0]:
                    for i in pcb[2].Group:
                        if i.Proxy.Type in ['PCBpart', "PCBpart_E"]:
                            if re.match('^{0}.*'.format(re.escape(fraza).lower()), i.Label.lower()):
                                self.szukaneFrazy.append(i)

            if len(self.szukaneFrazy):
                FreeCADGui.Selection.addSelection(self.szukaneFrazy[self.szukaneFrazyNr])
        except Exception as e:
            FreeCAD.Console.PrintWarning(u"{0}\n".format(e))

    #def convertDB(self):
        #''' convert old database format ot new one '''
        #dial = convertDB()
        #dial.exec_()
    
    def addModel(self):
        ''' add model from library to project '''
        if FreeCAD.activeDocument() and getPCBheight()[0]:
            if not FreeCADGui.Control.activeDialog():
                FreeCADGui.Control.showDialog(addModel())

    def assignModels(self):
        ''' assign 3d models to packages '''
        try:
            dodajElement().exec_()
        except Exception as e:
            FreeCAD.Console.PrintWarning("Error: {0}\n".format(e))

    def updateModels(self):
        ''' update 3d models of packages '''
        if FreeCAD.activeDocument():
            if not FreeCADGui.Control.activeDialog():
                FreeCADGui.Control.showDialog(updateParts())
    
    def downloadModels(self):
        if not FreeCADGui.Control.activeDialog():
            FreeCADGui.Control.showDialog(downloadModelW())
        
    def showPCBBoundingBox(self):
        boundingBox()

    def showPCBBoundingBoxSel(self):
        boundingBoxFromSelection(FreeCADGui.Selection.getSelection())


#####################################
#####################################
#####################################


class SelObserver:
    def addSelection(self, doc, obj, sub, pnt):
        self.zaznaczSketcher()
        
    def removeSelection(self, doc, obj, sub):
        self.zaznaczSketcher()
        
    def setSelection(self, doc):
        self.zaznaczSketcher()

    def clearSelection(self, doc):
        self.zaznaczSketcher()
        
    def zaznaczSketcher(self):
        pcb = getPCBheight()
        zaznaczoneObiekty = FreeCADGui.Selection.getSelection()
        
        if len(zaznaczoneObiekty):
            for i in zaznaczoneObiekty:
                try:
                    if i.isDerivedFrom("Sketcher::SketchObject") and i.Shape.isClosed() and pcb[0]:
                        FreeCADGui.pcbToolBar.scriptCmd_constraintsAreas.setDisabled(False)
                        break
                except:
                    pass
                FreeCADGui.pcbToolBar.scriptCmd_constraintsAreas.setDisabled(True)
        else:
            FreeCADGui.pcbToolBar.scriptCmd_constraintsAreas.setDisabled(True)
        

FreeCADGui.Selection.addObserver(SelObserver())

#####################################
#####################################
#####################################

if not hasattr(FreeCADGui, "pcbToolBar"):
    FreeCADGui.pcbToolBar = pcbToolBar()
if not hasattr(FreeCADGui, "pcbToolBarView"):
    FreeCADGui.pcbToolBarView = pcbToolBarView()
