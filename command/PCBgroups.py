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
    return makeUnigueGroup('Parts', 'partsGroup')

def createGroup_Layers():
    return makeUnigueGroup('Layers', 'layersGroup')

def createGroup_PCB():
    return makeUnigueGroup('PCB', 'pcbGroup')

def createGroup_Annotations():
    a = makeUnigueGroup('Annotations', 'annotationsGroup')
    return a

def createGroup_Areas():
    return makeUnigueGroup('Areas', 'areasGroup')
    
def createGroup_Glue():
    glue = makeUnigueGroup('Glue', 'glueGroup')
    
    gr = createGroup_Layers()
    gr.addObject(glue)
    
    return glue

def setProject():
    createGroup_Parts()
    createGroup_Layers()
    createGroup_PCB()
    createGroup_Annotations()
    createGroup_Areas()


def makeGroup(groupName):
    doc = FreeCAD.ActiveDocument
    
    for i in doc.Objects:
        if hasattr(i, "TypeId") and i.TypeId == 'App::DocumentObjectGroup' and i.Label == groupName:
            return i
    
    obj = doc.addObject("App::DocumentObjectGroup", groupName)
    #normalGroup(obj)
    #ViewProviderUnigueGroup(obj.ViewObject)
    return obj


def makeUnigueGroup(groupName, groupType):
    # group with parts => Type == partsGroup
    # group with layers => Type == layersGroup
    # group with pcb => Type == pcbGroup
    # group with areas => Type == areasGroup
    # group with annotations => Type == annotationsGroup
    # group with glue => Type == glueGroup
    if not FreeCAD.ActiveDocument or not groupType in ['partsGroup', 'layersGroup', 'pcbGroup', 'areasGroup', 'annotationsGroup', 'glueGroup']:
        return False
    
    doc = FreeCAD.ActiveDocument
    
    for i in doc.Objects:
        if hasattr(i, "Proxy") and hasattr(i.Proxy, "Type") and i.Proxy.Type == groupType:
            return i
    
    obj = doc.addObject("App::DocumentObjectGroupPython", groupName)
    unigueGroup(obj, groupType)
    ViewProviderUnigueGroup(obj.ViewObject)
    return obj


#***********************************************************************
#*                             OBJECT
#***********************************************************************
class unigueGroup:
    def __init__(self, obj, typeName):
        self.Type = typeName
        obj.Proxy = self
        self.Object = obj

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def execute(self, obj):
        pass
    
    def onChanged(self, fp, prop):
        if not hasattr(self, "Object"):
            self.Object = fp

    def addObject(self, child):
        if hasattr(self, "Object"):
            g = self.Object.Group
            if not child in g:
                g.append(child)
                self.Object.Group = g
        
    def removeObject(self, child):
        if hasattr(self, "Object"):
            g = self.Object.Group
            if child in g:
                g.remove(child)
                self.Object.Group = g


class normalGroup:
    def __init__(self, obj):
        self.Object = obj

    def execute(self, obj):
        pass
    
    def onChanged(self, fp, prop):
        if not hasattr(self, "Object"):
            self.Object = fp

    def addObject(self, child):
        if hasattr(self, "Object"):
            g = self.Object.Group
            if not child in g:
                g.append(child)
                self.Object.Group = g
        
    def removeObject(self, child):
        if hasattr(self, "Object"):
            g = self.Object.Group
            if child in g:
                g.remove(child)
                self.Object.Group = g


class ViewProviderUnigueGroup:
    def __init__(self, vobj):
        self.Object = vobj.Object

    def attach(self, vobj):
        self.Object = vobj.Object
        return
    
    def claimChildren(self):
        return self.Object.Group

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
