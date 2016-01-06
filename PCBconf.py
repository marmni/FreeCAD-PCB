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
import os
#
from PCBfunctions import getFromSettings_Color_1, getFromSettings_Color

__currentPath__ = os.path.abspath(os.path.join(os.path.dirname(__file__), ''))


#****************************************************************************
#*                                                                          *
#*                                                                          *
#*                       You can modify variables below                     *
#*                                                                          *
#*                                                                          *
#****************************************************************************
spisKolorowSTP = {
    "red": (1.0, 0.0, 0.0),
    "white": (1.0, 1.0, 1.0),
    "black": (0.0, 0.0, 0.0),
    "yellow": (1.0, 1.0, 0.0),
    "green": (0.0, 1.0, 0.0),
    "blue": (0.0, 0.0, 1.0)
}

#****************************************************************************
#*                                                                          *
#*                                                                          *
#*                    Please do not change anything below!                  *
#*                                                                          *
#*                                                                          *
#****************************************************************************
#  categories fo models for assign window
modelsCategories = {
        1: ['Capacitors', ''],
        2: ['Resistors', ''],
        3: ['Relays', ''],
        4: ['Rectifiers', ''],
        5: ['Heatsinks', ''],
        6: ['Crystals', ''],
        7: ['Diodes', ''],
        8: ['Led', ''],
        9: ['Buzzers', ''],
        10: ['Goldpins', ''],
        11: ['Jumpers', ''],
        12: ['Packages', ''],
        13: ['con-phoenix', ''],
        14: ['Varistors', ''],
        15: ["Connectors", ""],
        16: ["Potentiometers", ""],
        17: ["Batteries", ""],
        18: ["con-harting", ""],
        19: ["Packages-*BGA", ""],
        20: ["Display", ""],
        21: ["Switch-dil", ""],
        22: ["Inductor", ""]
    }
############

#  default pcb color
#       PCB_COLOR = (R/255., G/255., B/255.)
#            (84./255., 170./255., 0./255.) => (0.33, 0.67, 0.0)
#            PCB_COLOR = (0.33, 0.67, 0.0)
PCB_COLOR = getFromSettings_Color('boardColor', 1437204735)


#  partPaths = [path_1, path_2, etc]
#       for example: /home/mariusz/.FreeCAD/Mod/EaglePCB_2_FreeCAD/parts/
#       used in: PCBpartManaging.partExist()
partPaths = [os.path.join(FreeCAD.getHomePath(), "Mod\PCB\parts"), os.path.join(__currentPath__, "parts")]

#  default software list
defSoftware = ['Eagle', 'KiCad', 'FidoCadJ', 'FreePCB', 'Razen', 'gEDA', 'IDF v2', 'IDF v3', 'IDF v4', 'HyperLynx']  # do not change order!


#  DATABASES LIST
#  libPath - default position of library for program (if necessary)
#       for example: FidoCadJ -> 'libPath': 'C:\\Users\\mariusz\\Downloads\\Desktop\\fidocadj.jar'
supSoftware = {
    "eagle" : {
        'name': 'Eagle',
        'pathToBase': __currentPath__ + '/data/data.cfg',
        'libPath': '',
        'export': True,
        'exportLayers': ['dim', 'hol', 'anno', 'glue'],
        'exportClass': 'eagle()',
        'description': 'Eagle',
        'format': '*.brd',
        'icon': ':/data/img/eagle.png',
    },
    "kicad" : {
        'name': 'KiCad',
        'pathToBase': __currentPath__ + '/data/kicad.cfg',
        'libPath': '',
        'export': True,
        'exportLayers': ['dim', 'hol', 'anno', 'glue'],
        'exportClass': 'kicad()',
        'description': 'KiCad',
        'format': '*.kicad_pcb',
        'icon': ':/data/img/kicad.png',
    },
    "fidocadj" : {
        'name': 'FidoCadJ',
        'pathToBase': __currentPath__ + '/data/fidocadj.cfg',
        'libPath': FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("librariesPathFidoCADJ","").strip(),
        'export': True,
        'exportLayers': ['hol', 'anno'],
        'exportClass': 'fidocadj()',
        'description': 'FidoCadJ',
        'format': '*.fcd',
        'icon': ':/data/img/fidocadj.png',
    },
    "geda" : {
        'name': 'gEDA',
        'pathToBase': '',
        'libPath': '',
        'export': True,
        'exportLayers': ['hol', 'anno'],
        'exportClass': 'geda()',
        'description': 'gEDA',
        'format': '*.pcb',
        'icon': ':/data/img/geda.png',
    },
    "freepcb" : {
        'name': 'FreePCB',
        'pathToBase': __currentPath__ + '/data/freepcb.cfg',
        'libPath': '',
        'export': False,
        'exportLayers': ['anno'],
        'exportClass': 'exportPCB_FreePCB()',
        'description': 'FreePCB',
        'format': '*.fpc',
        'icon': ':/data/img/freepcb.png',
    },
    "razen" : {
        'name': 'Razen',
        'pathToBase': __currentPath__ + '/data/razen.cfg',
        'libPath': FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("librariesPathRazen","").strip(),
        'export': True,
        'exportLayers': ['hol', 'anno'],
        'exportClass': 'razen()',
        'description': 'Razen',
        'format': '*.rzp',
        'icon': ':/data/img/razen.png',
    },
    "idf_v2" : {
        'name': 'IDF v2',
        'pathToBase': __currentPath__ + '/data/idf.cfg',
        'libPath': '',
        'export': False,
        'exportLayers': ['hol'],
        'exportClass': 'idf_v2()',
        'description': 'IDF v2',
        'format': '*.emn',
        'icon': '',
    },
    "idf_v3" : {
        'name': 'IDF v3',
        'pathToBase': __currentPath__ + '/data/idf.cfg',
        'libPath': '',
        'export': True,
        'exportLayers': ['hol', 'anno'],
        'exportClass': 'idf_v3()',
        'description': 'IDF v3',
        'format': '*.emn',
        'icon': '',
    },
    "idf_v4" : {
        'name': 'IDF v4',
        'pathToBase': __currentPath__ + '/data/idf.cfg',
        'libPath': '',
        'export': False,
        'exportLayers': [],
        'exportClass': '',
        'description': 'IDF v4',
        'format': '*.idf',
        'icon': '',
    },
    "hyp" : {
        'name': 'HyperLynx',
        'pathToBase': __currentPath__ + '/data/idf.cfg',
        'libPath': '',
        'export': False,
        'exportLayers': [],
        'exportClass': '',
        'description': 'HyperLynx',
        'format': '*.HYP',
        'icon': '',
    }
}

##
# pathToDAtabase = moved to PCBfunctions.py getFromSettings_databasePath()


#  PCBconstraintAreas = layerName: [layer nape for menu, [layerType], [Type, Surfix, Value, Min, Max], [R, G, B], layer description]
#
#  layerPosition
#   0: Bottom
#   1: Top
#   2: Both
#
PCBconstraintAreas = {
    "tPlaceKeepout": ['Place Keepout Top', ['tKeepout', 'topSide'], ['int', '%', 50, 0, 100], getFromSettings_Color_1('tPlaceKeepoutColor', 4278190335), "Restricted areas for components, top side"],
    "bPlaceKeepout": ['Place Keepout Bottom', ['bKeepout', 'bottomSide'],['int', '%', 50, 0, 100] , getFromSettings_Color_1('bPlaceKeepoutColor', 65535), "Restricted areas for components, bottom side"],
    "vPlaceOutline": ["Place Outline", ['vPlaceOutline', 'bothSide'], ['int', '%', 50, 0, 100], getFromSettings_Color_1('vPlaceOutlineColor', 255), ''],
    "tPlaceOutline": ["Place Outline Top", ['tPlaceOutline', 'topSide'], ['int', '%', 50, 0, 100], getFromSettings_Color_1('tPlaceOutlineColor', 4278190335), ''],
    "bPlaceOutline": ["Place Outline Bottom", ['bPlaceOutline', 'bottomSide'], ['int', '%', 50, 0, 100], getFromSettings_Color_1('bPlaceOutlineColor', 65535), ''],
    "vRouteOutline": ["Route Outline", ['vRouteOutline', 'bothSide'], ['int', '%', 50, 0, 100], getFromSettings_Color_1('vRouteOutlineColor', 255), ''],
    "tRouteOutline": ["Route Outline Top", ['tRestrict', 'tRouteOutline', 'topSide'], ['int', '%', 50, 0, 100], getFromSettings_Color_1('tRouteOutlineColor', 4278190335), ''],
    "bRouteOutline": ["Route Outline Bottom", ['bRestrict', 'bRouteOutline', 'bottomSide'], ['int', '%', 50, 0, 100], getFromSettings_Color_1('bRouteOutlineColor', 65535), ''],
    "tRouteKeepout": ["Route Keepout Top", ['tRestrict', 'topSide'], ['int', '%', 50, 0, 100], getFromSettings_Color_1('tRouteKeepoutColor', 4278190335), "Restricted areas for copper, top side"],
    "bRouteKeepout": ["Route Keepout Bottom", ['bRestrict', 'bottomSide'], ['int', '%', 50, 0, 100], getFromSettings_Color_1('bRouteKeepoutColor', 65535), "Restricted areas for copper, bottom side"],
    "vRouteKeepout": ["Via Keepout", ['vRestrict', 'bothSide'], ['int', '%', 50, 0, 100], getFromSettings_Color_1('vRouteKeepoutColor', 255), "Restricted areas for vias"]
}

PCBlayers = {
    "tPolygon" : [1, getFromSettings_Color_1('PathColor', 7012607), None, ['tPolygon'], "Polygons, top side"],
    "bPolygon" : [0, getFromSettings_Color_1('PathColor', 7012607), None, ['bPolygon'], "Polygons, bottom side"],
    "tPath" : [1, getFromSettings_Color_1('PathColor', 7012607), ['double', u'μm', 34.6, 0, 350], ['tPath'], "Tracks, top side"],
    "bPath" : [0, getFromSettings_Color_1('PathColor', 7012607), ['double', u'μm', 34.6, 0, 350], ['bPath'], "Tracks, bottom side"],
    "tPad" : [1, getFromSettings_Color_1('PadColor', 3094557695), ['double', u'μm', 35, 0, 350], ['tPad'], "Pads, top side"],
    "bPad" : [0, getFromSettings_Color_1('PadColor', 3094557695), ['double', u'μm', 35, 0, 350], ['bPad'], "Pads, bottom side"],
    "tSilk" : [1, getFromSettings_Color_1('SilkColor', 4294967295), ['double', u'μm', 34.8, 0, 350], ['tSilk'], "Silk screen, top side"],
    "bSilk" : [0, getFromSettings_Color_1('SilkColor', 4294967295), ['double', u'μm', 34.8, 0, 350], ['bSilk'], "Silk screen, bottom side"],
    "tDocu" : [1, getFromSettings_Color_1('SilkColor', 4294967295), ['double', u'μm', 34.8, 0, 350], ['tDocu'], "Detailed top screen print"],
    "bDocu" : [0, getFromSettings_Color_1('SilkColor', 4294967295), ['double', u'μm', 34.8, 0, 350], ['bDocu'], "Detailed bottom screen print"],
    "Measures" : [1, getFromSettings_Color_1('MeasuresColor', 1879048447), None, ['Measures'], "Measures"],
    "centerDrill" : [0, getFromSettings_Color_1('CenterDrillColor', 4294967295), None, ['PCBcenterDrill'], "Center drill"],
    #"tcenterDrill" : [1, getFromSettings_Color_1('CenterDrillColor', 4294967295), None, ['tcenterDrill'], "Center drill, top side"],
    #"bcenterDrill" : [0, getFromSettings_Color_1('CenterDrillColor', 4294967295), None, ['bcenterDrill'], "Center drill, bottom side"],
    "Annotations" : [2, getFromSettings_Color_1('AnnotationsColor', 255), [], ['PCBannotation'], "Annotations"],
    "tGlue" : [1, getFromSettings_Color_1('GlueColor', 4290230271), None, ['tGlue'], "Glue, top side"],
    "bGlue" : [0, getFromSettings_Color_1('GlueColor', 4290230271), None, ['bGlue'], "Glue, bottom side"],
}

softLayers = {
    "eagle": {
        0: ["Annotations", "Annotations"],
        1: ["tPath", "tPath"],
        16 : ["bPath", "bPath"],
        17 : ["tPad", "tPad"],
        18 : ["bPad", "bPad"],
        21 : ["tPlace", "tSilk"],
        22 : ["bPlace", "bSilk"],
        35 : ["tGlue", "tGlue"],
        36 : ["bGlue", "bGlue"],
        39 : ["tKeepout", "tPlaceKeepout"],
        40 : ["bKeepout", "bPlaceKeepout"],
        41 : ["tRestrict", "tRouteKeepout"],
        42 : ["bRestrict", "bRouteKeepout"],
        43 : ["vRestrict", "vRouteKeepout"],
        47 : ["Measures", "Measures"],
        51 : ["tDocu", "tDocu"],
        52 : ["bDocu", "bDocu"],
        #116 : ["tcenterDrill", "tcenterDrill"],
        #117 : ["bcenterDrill", "bcenterDrill"],
        #998: ["tPolygon", "tPolygon"],
        #999: ["bPolygon", "bPolygon"],
    },
    "kicad": {
        0: ["bPath", "bPath"],
        1: ["Annotations", "Annotations"],
        15: ["tPath", "tPath"],
        16 : ["bGlue", "bGlue"],
        17 : ["tGlue", "tGlue"],
        18: ["bPad", "bPad"],
        19: ["tPad", "tPad"],
        20: ["bSilk", "bSilk"],
        21: ["tSilk", "tSilk"],
        106: ["Measures", "Measures"],
        900: ["tKeepout", "tPlaceKeepout"],
        901: ["bKeepout", "bPlaceKeepout"],
        902: ["tRouteKeepout", "tRouteKeepout"],
        903: ["bRouteKeepout", "bRouteKeepout"],
        904: ["ViaKeepout", "vRouteKeepout"],
    },
    "kicad_v4": {
        0: ["tPath", "tPath"],
        31: ["bPath", "bPath"],
        32 : ["bGlue", "bGlue"],
        33 : ["tGlue", "tGlue"],
        36: ["bSilk", "bSilk"],
        37: ["tSilk", "tSilk"],
        105: ["Annotations", "Annotations"],
        106: ["Measures", "Measures"],
        107: ["bPad", "bPad"],
        108: ["tPad", "tPad"],
        900: ["tKeepout", "tPlaceKeepout"],
        901: ["bKeepout", "bPlaceKeepout"],
        902: ["tRouteKeepout", "tRouteKeepout"],
        903: ["bRouteKeepout", "bRouteKeepout"],
        904: ["ViaKeepout", "vRouteKeepout"],
    },
    "freepcb": {
        0: ["Annotations", "Annotations"],
        12: ["tPath", "tPath"],
        13: ["bPath", "bPath"],
        17: ["tPad", "tPad"],
        18: ["bPad", "bPad"],
        21: ["tSilk", "tSilk"],
        22: ["bSilk", "bSilk"],
    },
    "idf_v2": {
        37: ["PlaceOutline", "vPlaceOutline"],
        38: ["RouteOutline", "vRouteOutline"],
        39: ["tPlaceKeepout", "tPlaceKeepout"],
        40: ["bPlaceKeepout", "bPlaceKeepout"],
        41: ["tRouteKeepout", "tRouteKeepout"],
        42: ["bRouteKeepout", "bRouteKeepout"],
        43: ["ViaKeepout", "vRouteKeepout"],
    },
    "idf_v3": {
        0: ["Annotations", "Annotations"],
        35: ["tPlaceOutline", "tPlaceOutline"],
        36: ["bPlaceOutline", "bPlaceOutline"],
        37: ["tRouteOutline", "tRouteOutline"],
        38: ["bRouteOutline", "bRouteOutline"],
        39: ["tPlaceKeepout", "tPlaceKeepout"],
        40: ["bPlaceKeepout", "bPlaceKeepout"],
        41: ["tRouteKeepout", "tRouteKeepout"],
        42: ["bRouteKeepout", "bRouteKeepout"],
        43: ["ViaKeepout", "vRouteKeepout"],
    },
    "idf_v4": {
    },
    "geda": {
        0: ["Annotations", "Annotations"],
        1: ["tPath", "tPath"],
        2: ["bPath", "bPath"],
        10: ["Silk", "tSilk"],
        17: ["tPad", "tPad"],
        18: ["bPad", "bPad"],
    },
    "fidocadj": {
        0: ["Annotations", "Annotations"],
        1: ["bPath", "bPath"],
        2: ["tPath", "tPath"],
        3: ["tSilk", "tSilk"],
        4: ["bSilk", "bSilk"],
        17: ["tPad", "tPad"],
        18: ["bPad", "bPad"],
    },
    "razen": {
        0: ["Annotations", "Annotations"],
        1: ["tPath", "tPath"],
        16: ["bPath", "bPath"],
        17: ["tPad", "tPad"],
        18: ["bPad", "bPad"],
        21: ["OutlineTop", "tSilk"],
        22: ["OutlineBottom", "bSilk"],
    },
    "hyp": {
        1: ["tPath", "tPath"],
        16 : ["bPath", "bPath"],
        17: ["tPad", "tPad"],
        18: ["bPad", "bPad"],
    },
    
}


# IGES format standard color codes
#   0 - No color assigned
#   1 - Black
#   2 - Red
#   3 - Green
#   4 - Blue
#   5 - Yellow
#   6 - Magenta
#   7 - Cyan
#   8 - White
spisKolorow = {
    0: (0.8, 0.8, 0.8),
    1: (0.0, 0.0, 0.0),
    2: (1.0, 0.0, 0.0),
    3: (0.0, 1.0, 0.0),
    4: (0.0, 0.0, 1.0),
    5: (1.0, 1.0, 0.0),
    6: (1.0, 0.0, 0.56),
    7: (0.0, 1.0, 1.0),
    8: (1.0, 1.0, 1.0)
}
