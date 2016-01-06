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

import FreeCADGui
#
from command.PCBexplode import explodeEditWizard
from command.PCBupdateParts import updateParts
from command.PCBassignModel import dodajElement
from command.PCBmoveParts import moveParts
from command.PCBDownload import downloadModelW

################################################
##   change display mode of all element in active document
################################################
#class ScriptCmd_viewShaded:
    #def Activated(self):
        #changeDisplayMode('Shaded')
    
    #def GetResources(self):
        #return {'Pixmap': __currentPath__ + "/data/img/viewShaded.png", 'MenuText': 'Change display mode, Shaded', 'ToolTip': 'Change display mode, Shaded'}

#FreeCADGui.addCommand('ScriptCmd_viewShaded', ScriptCmd_viewShaded())


#class ScriptCmd_viewFlatLines:
    #def Activated(self):
        #changeDisplayMode('Flat Lines')
    
    #def GetResources(self):
        #return {'Pixmap': __currentPath__ + "/data/img/viewFlatLines.png", 'MenuText': 'Change display mode, Flat Lines', 'ToolTip': 'Change display mode, Flat Lines'}

#FreeCADGui.addCommand('ScriptCmd_viewFlatLines', ScriptCmd_viewFlatLines())


#class ScriptCmd_viewWireframe:
    #def Activated(self):
        #changeDisplayMode('Wireframe')
    
    #def GetResources(self):
        #return {'Pixmap': __currentPath__ + "/data/img/viewWireframe.png", 'MenuText': 'Change display mode, Wireframe', 'ToolTip': 'Change display mode, Wireframe'}

#FreeCADGui.addCommand('ScriptCmd_viewWireframe', ScriptCmd_viewWireframe())

################################################
##   odajElement() -> Assign models
################################################
#class ScriptCmd_Assign:
    #def Activated(self):
        #dial = dodajElement()
        #dial.exec_()
    
    #def GetResources(self):
        #return {'Pixmap': __currentPath__ + "/data/img/uklad.png", 'MenuText': 'Assign models', 'ToolTip': 'Assign models'}

#FreeCADGui.addCommand('ScriptCmd_Assign', ScriptCmd_Assign())


################################################
##   convertDB() -> Convert old database (param.py) to new dane.cfg
################################################
#class ScriptCmd_Convert:
    #def Activated(self):
        #dial = convertDB()
        #dial.exec_()
    
    #def GetResources(self):
        #return {'Pixmap': __currentPath__ + "/data/img/convert_16x16.png", 'MenuText': 'Convert DB', 'ToolTip': 'Convert DB'}

#FreeCADGui.addCommand('ScriptCmd_Convert', ScriptCmd_Convert())

###############################################
#   EXPLODE SETTINGS
###############################################


class cmdExplodeEdit:
    def Activated(self):
        panel = explodeEditWizard(FreeCADGui.Selection.getSelection()[0])
        FreeCADGui.Control.showDialog(panel)
    
    def GetResources(self):
        return {'MenuText': 'Edit', 'ToolTip': 'Edit Explode'}

FreeCADGui.addCommand('cmdExplodeEdit', cmdExplodeEdit())
###############################################
#   ASSIGN 3D MODEL
###############################################


class cmdPartAssignModel:
    def Activated(self):
        dial = dodajElement()
        dial.packageName.setText(FreeCADGui.Selection.getSelection()[0].Package)
        dial.exec_()
    
    def GetResources(self):
        return {'MenuText': 'Assign model', 'ToolTip': 'Assign model'}

FreeCADGui.addCommand('cmdPartAssignModel', cmdPartAssignModel())
###############################################
#   UPDATE 3D MODEL
###############################################


class cmdPartUpdateModel:
    def Activated(self):
        panel = updateParts(updateModel=FreeCADGui.Selection.getSelection()[0].Package)
        FreeCADGui.Control.showDialog(panel)
        
    def GetResources(self):
        return {'MenuText': 'Update model', 'ToolTip': 'Update model'}

FreeCADGui.addCommand('cmdPartUpdateModel', cmdPartUpdateModel())
###############################################
#   MOVE 3D MODEL
###############################################


class cmdPartMoveModel:
    def Activated(self):
        panel = moveParts(FreeCADGui.Selection.getSelection()[0].Package)
        FreeCADGui.Control.showDialog(panel)
        
    def GetResources(self):
        return {'MenuText': 'Placement model', 'ToolTip': 'Placement model'}

FreeCADGui.addCommand('cmdPartMoveModel', cmdPartMoveModel())
###############################################
#   FIND MODEL ON-LINE
###############################################


class cmdPartFindModel:
    def Activated(self):
        FreeCADGui.Control.showDialog(downloadModelW(FreeCADGui.Selection.getSelection()[0].Package))
        
    def GetResources(self):
        return {'MenuText': 'Find model on-line', 'ToolTip': 'Find model on-line'}

FreeCADGui.addCommand('cmdPartFindModel', cmdPartFindModel())
################################################
##   odajElement() -> Assign models
################################################
class ScriptCmd_OpenSketcherWorkbench:
    def Activated(self):
        FreeCADGui.activateWorkbench("SketcherWorkbench")
    
    def GetResources(self):
        return {'Pixmap': ":/data/img/Sketcher_Sketch.png", 'MenuText': 'Open Sketcher Workbench', 'ToolTip': 'Open Sketcher Workbench'}

FreeCADGui.addCommand('ScriptCmd_OpenSketcherWorkbench', ScriptCmd_OpenSketcherWorkbench())
#######
listaExplode = ["cmdExplodeEdit"]
listaPartsE = ["cmdPartAssignModel", "cmdPartUpdateModel", 'cmdPartFindModel']
listaParts = ["cmdPartUpdateModel", "cmdPartMoveModel"]
###############################################
###############################################
