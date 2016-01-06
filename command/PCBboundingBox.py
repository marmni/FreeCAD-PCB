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
import Part
import FreeCADGui


def createBox(parts):
    if len(parts):
        elem = Part.makeCompound(parts)
        BoundBox = FreeCAD.ActiveDocument.addObject("Part::Box", "PCB_Bounding_Box_1")
        BoundBox.Label = "PCB Bounding Box 1"
        BoundBox.Length = elem.BoundBox.XLength
        BoundBox.Width = elem.BoundBox.YLength
        BoundBox.Height = elem.BoundBox.ZLength
        BoundBox.Placement.Base.x = elem.BoundBox.XMin
        BoundBox.Placement.Base.y = elem.BoundBox.YMin
        BoundBox.Placement.Base.z = elem.BoundBox.ZMin
        FreeCADGui.activeDocument().getObject(BoundBox.Name).ShapeColor = (1.0, 0.0, 0.0, 0.0)
        FreeCADGui.activeDocument().getObject(BoundBox.Name).Transparency = 80
        FreeCADGui.activeDocument().getObject(BoundBox.Name).BoundingBox = True
        FreeCADGui.activeDocument().getObject(BoundBox.Name).LineWidth = 10.00
        FreeCADGui.activeDocument().getObject(BoundBox.Name).DisplayMode = "Shaded"
        FreeCAD.ActiveDocument.recompute()
        
        return BoundBox

def boundingBox():
    return createBox([i.Shape for i in FreeCAD.activeDocument().Objects if i.ViewObject.Visibility and hasattr(i, "Shape")])
    
def boundingBoxFromSelection(parts):
    return createBox([i.Shape for i in parts if i.ViewObject.Visibility])
