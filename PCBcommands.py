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

###############################################
#   EXPLODE SETTINGS
###############################################


class cmdExplodeEdit:
    def Activated(self):
        panel = explodeEditWizard(FreeCADGui.Selection.getSelection()[0])
        FreeCADGui.Control.showDialog(panel)
    
    def GetResources(self):
        return {'MenuText': 'Edit', 'ToolTip': 'Edit Explode', 'Pixmap'  : ":/data/img/explode.png"}

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
        return {'MenuText': 'Assign model', 'ToolTip': 'Assign model', 'Pixmap'  : ':/data/img/uklad.png'}

FreeCADGui.addCommand('cmdPartAssignModel', cmdPartAssignModel())
###############################################
#   UPDATE 3D MODEL
###############################################


class cmdPartUpdateModel:
    def Activated(self):
        panel = updateParts(updateModel=FreeCADGui.Selection.getSelection()[0].Package)
        FreeCADGui.Control.showDialog(panel)
        
    def GetResources(self):
        return {'MenuText': 'Update model', 'ToolTip': 'Update model', 'Pixmap'  : ":/data/img/updateModels.png"}

FreeCADGui.addCommand('cmdPartUpdateModel', cmdPartUpdateModel())
###############################################
#   MOVE 3D MODEL
###############################################


class cmdPartMoveModel:
    def Activated(self):
        panel = moveParts(FreeCADGui.Selection.getSelection()[0].Package)
        FreeCADGui.Control.showDialog(panel)
        
    def GetResources(self):
        return {'MenuText': 'Placement model', 'ToolTip': 'Placement model', 'Pixmap'  : ":/data/img/centroid.svg"}
        
    def IsActive(self):
        return True

FreeCADGui.addCommand('cmdPartMoveModel', cmdPartMoveModel())
###############################################
#   FIND MODEL ON-LINE
###############################################


class cmdPartFindModel:
    def Activated(self):
        FreeCADGui.Control.showDialog(downloadModelW(FreeCADGui.Selection.getSelection()[0].Package))
        
    def GetResources(self):
        return {'MenuText': 'Find model on-line', 'ToolTip': 'Find model on-line', 'Pixmap'  : ":/data/img/downloadModels.png"}

FreeCADGui.addCommand('cmdPartFindModel', cmdPartFindModel())
################################################
##   odajElement() -> Assign models
################################################
class ScriptCmd_OpenSketcherWorkbench:
    def Activated(self):
        FreeCADGui.activateWorkbench("SketcherWorkbench")
    
    def GetResources(self):
        return {'Pixmap': ":/data/img/SketcherWorkbech.svg", 'MenuText': 'Open Sketcher Workbench', 'ToolTip': 'Open Sketcher Workbench'}

FreeCADGui.addCommand('ScriptCmd_OpenSketcherWorkbench', ScriptCmd_OpenSketcherWorkbench())
#######
listaExplode = ["cmdExplodeEdit"]
listaPartsE = ["cmdPartAssignModel", "cmdPartUpdateModel", 'cmdPartFindModel']
listaParts = ["cmdPartUpdateModel", "cmdPartMoveModel"]
###############################################
