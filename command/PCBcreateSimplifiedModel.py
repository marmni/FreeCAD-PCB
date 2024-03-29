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
import FreeCAD, FreeCADGui
import Part

from PCBboard import getPCBheight
from command.PCBboundingBox import createBoxForModel

#***********************************************************************
#*                            
#***********************************************************************
def createSimplifiedModel():
    if not FreeCAD.activeDocument():
        FreeCAD.Console.PrintWarning("File does not exist or is empty\n")
        return
    #
    pcb = getPCBheight()
    if not pcb[0]:
        FreeCAD.Console.PrintWarning("No PCB found\n")
        return
    #
    dataComp = [pcb[2].Shape]
    
    for i in pcb[2].Group:
        obj = createBoxForModel(i)
        if hasattr(obj, "Shape"):
            dataComp.append(obj.Shape)
            FreeCAD.ActiveDocument.removeObject(obj.Name)
    #
    elem = Part.makeCompound(dataComp)
    Part.show(elem)
    FreeCAD.ActiveDocument.recompute()

