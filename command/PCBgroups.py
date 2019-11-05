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


#***********************************************************************
#*                             CONSOLE
#***********************************************************************
def createGroup_Parts():
    return makeUnigueGroup('Parts')

def createGroup_Layers():
    return makeUnigueGroup('Layers')

def createGroup_PCB():
    return makeUnigueGroup('PCB')

def createGroup_Annotations():
    group = makeUnigueGroup('Annotations')
    
    gr = createGroup_Layers()
    gr.addObject(group)
    
    return group
    
def createGroup_Areas():
    group = makeUnigueGroup('Areas')
    
    gr = createGroup_Layers()
    gr.addObject(group)
    
    return group
    
def createGroup_Dimensions(groupName="Measures"):
    group = makeUnigueGroup(groupName)
    
    gr = createGroup_Layers()
    gr.addObject(group)
    
    return group
    
def createGroup_Others():
    group = makeUnigueGroup('Others')
    
    gr = createGroup_Parts()
    gr.addObject(group)
    
    return group

def createGroup_Missing():
    group = makeUnigueGroup('Missing')
    
    gr = createGroup_Parts()
    gr.addObject(group)
    
    return group

def createGroup(groupName=""):
    return makeUnigueGroup(groupName)
    
def createGroup_Glue():
    group= makeUnigueGroup('Glue')
    
    gr = createGroup_Layers()
    gr.addObject(group)
    
    return group

def setProject():
    createGroup_Parts()
    createGroup_Layers()
    createGroup_PCB()
    createGroup_Annotations()
    createGroup_Areas()

def makeUnigueGroup(groupName):
    if not FreeCAD.ActiveDocument:
        return False
    
    try:
        group = FreeCAD.ActiveDocument.getObject(groupName)
        label = group.Label
        return group
    except:
        return FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup", groupName)
