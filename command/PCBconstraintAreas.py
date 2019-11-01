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
#
import PCBrc
from PCBconf import PCBconstraintAreas
from PCBboard import getPCBheight
from command.PCBgroups import createGroup_Areas
from PCBobjects import constraintAreaObject, viewProviderConstraintAreaObject

#***********************************************************************
#*                             CONSOLE
#***********************************************************************
def createConstraintArea(obj, typeCA, height=0):
    try:
        pcb = getPCBheight()
        
        if not pcb[0]:
            return
        #
        grp = createGroup_Areas()
        
        if obj.isDerivedFrom("Sketcher::SketchObject"):
            if not obj.Shape.isClosed():
                FreeCAD.Console.PrintWarning("Sketcher is not closed!\n")
                return
            #
            obj.ViewObject.Visibility = False
            
            #layerName = PCBconstraintAreas[typeCA][0]
            layerColor = (PCBconstraintAreas[typeCA][3][0] / 255., PCBconstraintAreas[typeCA][3][1] / 255., PCBconstraintAreas[typeCA][3][2] / 255.)
            layerTransparent = PCBconstraintAreas[typeCA][2][2]
            typeL = PCBconstraintAreas[typeCA][1][0]
            #numLayer = 0
            #
            a = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", typeCA + "_{0}".format(0))
            layerObj = constraintAreaObject(a, typeL)
            a.Base = obj
            if height != 0:
                a.Height = height
            viewProviderConstraintAreaObject(a.ViewObject)
            grp.addObject(a)
            FreeCADGui.activeDocument().getObject(a.Name).ShapeColor = layerColor
            FreeCADGui.activeDocument().getObject(a.Name).Transparency = layerTransparent
            FreeCADGui.activeDocument().getObject(a.Name).DisplayMode = 1
            
            a.purgeTouched()

            pcb[2].addObject(a)
            #FreeCAD.ActiveDocument.recompute()
            return a
    except Exception as e:
        FreeCAD.Console.PrintWarning("{0} \n".format(e))
