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
#defSoftware = ['Eagle', 'KiCad', 'FidoCadJ', 'FreePCB', 'Razen', 'gEDA', 'IDF', 'HyperLynx']  # do not change order!
defSoftware = ['Eagle', 'KiCad', 'FreePCB', 'gEDA', 'IDF', 'HyperLynx', 'LibrePCB']  # do not change order!

#########################
exportData = {
    "eagle" : {
        'name': 'Eagle',
        'exportLayers': ['dim', 'hol', 'anno', 'glue'],
        'exportClass': 'eagle()',
        'description': 'Eagle',
        'format': '*.brd',
        'icon': ':/data/img/eagle.png',
        'export': True,
        'exportComponent': True,
        'formatLIB': '*.lbr',
    },
    "geda" : {
        'name': 'gEDA',
        'exportLayers': ['hol', 'anno'],
        'exportClass': 'geda()',
        'description': 'gEDA',
        'format': '*.pcb',
        'icon': ':/data/img/geda.png',
        'export': True,
        'exportComponent': True,
        'formatLIB': '',
    },
    "idf_v3" : {
        'name': 'IDF v3',
        'exportLayers': ['hol', 'anno'],
        'exportClass': 'idf_v3()',
        'description': 'IDF v3',
        'format': '*.emn',
        'icon': '',
        'export': True,
        'exportComponent': False,
    },
    "freepcb" : {
        'name': 'FreePCB',
        'exportLayers': ['hol', 'anno'],
        'exportClass': 'freePCB()',
        'description': 'FreePCB',
        'format': '*.fpc',
        'icon': ':/data/img/freepcb.png',
        'export': True,
        'exportComponent': False,
    },
    "kicad" : {
        'name': 'KiCad v4',
        'exportLayers': ['dim', 'hol', 'anno', 'glue'],
        'exportClass': 'kicad()',
        'description': 'KiCad',
        'format': '*.kicad_pcb',
        'icon': ':/data/img/kicad.png',
        'export': True,
        'exportComponent': True,
        'formatLIB': '*.kicad_mod',
    },
    "hyp_v2" : {
        'name': 'HyperLynx',
        'exportLayers': [],
        'exportClass': '',
        'description': 'HyperLynx',
        'format': '*.HYP',
        'icon': '',
        'export': False,
        'exportComponent': False,
    },
    "librepcb" : {
        'name': 'LibrePCB',
        'exportLayers': [],
        'exportClass': '',
        'description': 'LibrePCB',
        'format': '*.lpp',
        'icon': '',
        'export': False,
        'exportComponent': False,
    },
}
#########################
#  PCBconstraintAreas = layerName: [layer nape for menu, [layerType], [Type, Surfix, Value, Min, Max], [R, G, B], layer description]
#
#  layerPosition
#   0: Bottom
#   1: Top
#   2: Both
#
PCBconstraintAreas = {
    "vPlaceKeepout": ["Place Keepout", ['vPlaceKeepout', 'bothSide'], ['int', '%', 50, 0, 100], getFromSettings_Color_1('vPlaceKeepoutColor', 255), ''],
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
    "vRouteKeepout": ["Via Keepout", ['vRestrict', 'bothSide'], ['int', '%', 50, 0, 100], getFromSettings_Color_1('vRouteKeepoutColor', 255), "Restricted areas for vias"],
    "routeOutline":["ROUTE_OUTLINE", ["vRouteOutline", 'bothSide'], ['int', '%', 50, 0, 100], getFromSettings_Color_1('vRouteOutlineColor', 255), "ROUTE_OUTLINE"],
    "placeOutline": ["PLACE_OUTLINE", ['vPlaceOutline', 'bothSide'], ['int', '%', 50, 0, 100], getFromSettings_Color_1('vPlaceOutlineColor', 255), "PLACE_OUTLINE"],
    "viaKeepout": ["Via Keepout", ['vRestrict', 'bothSide'], ['int', '%', 50, 0, 100], getFromSettings_Color_1('vRouteKeepoutColor', 255), "Restricted areas for vias"],
    "tPlaceRegion": ["Place Outline Top", ['tPlaceOutline', 'topSide'], ['int', '%', 50, 0, 100], getFromSettings_Color_1('tPlaceOutlineColor', 4278190335), ''],
    "bPlaceRegion": ["Place Outline Bottom", ['bPlaceOutline', 'bottomSide'], ['int', '%', 50, 0, 100], getFromSettings_Color_1('bPlaceOutlineColor', 65535), ''],
    "vPlaceRegion": ["Place Outline", ['vPlaceOutline', 'bothSide'], ['int', '%', 50, 0, 100], getFromSettings_Color_1('bPlaceOutlineColor', 65535), ''],
}

layersList = {
    "anno": {"side": -1, "mirrorLayer": None, "color": getFromSettings_Color_1('AnnotationsColor', 4294967295), "description": "Annotations", "value": None},
    "pathT": {"side": 1, "mirrorLayer": 16, "color": getFromSettings_Color_1('PathColor', 7012607), "description": "Tracks, top side", "value": ['double', u'μm', 34.6, 0, 350]},
    "pathB": {"side": 0, "mirrorLayer": 1, "color": getFromSettings_Color_1('PathColor', 7012607), "description": "Tracks, bottom side", "value": ['double', u'μm', 34.6, 0, 350]}, 
    "padT": {"name": "tPad", "side": 1, "mirrorLayer": None, "color": getFromSettings_Color_1('PadColor', 3094557695), "description": "Pads, top side", "value": ['double', u'μm', 35, 0, 350]}, 
    "padB": {"name": "bPad", "side": 0, "mirrorLayer": None, "color": getFromSettings_Color_1('PadColor', 3094557695), "description": "Pads, bottom side", "value": ['double', u'μm', 35, 0, 350]}, 
    "silkT": {"side": 1, "mirrorLayer": 22, "color": getFromSettings_Color_1('SilkColor', 4294967295), "description": "Silk screen, top side", "value": ['double', u'μm', 34.8, 0, 350]},
    "silkB": {"side": 0, "mirrorLayer": 21, "color": getFromSettings_Color_1('SilkColor', 4294967295), "description": "Silk screen, bottom side", "value": ['double', u'μm', 34.8, 0, 350]},
    "glueT": {"side": 1, "mirrorLayer": None, "color": getFromSettings_Color_1('GlueColor', 4290230271), "description": "Glue, top side", "value": None},
    "glueB": {"side": 0, "mirrorLayer": None, "color": getFromSettings_Color_1('GlueColor', 4290230271), "description": "Glue, bottom side", "value": None},
    "measure": {"side": -1, "mirrorLayer": None, "color": getFromSettings_Color_1('MeasuresColor', 1879048447), "description": "Measures", "value": None},
    "placeT": {"side": 1, "mirrorLayer": 22, "color": getFromSettings_Color_1('SilkColor', 4294967295), "description": "Placement, top side", "value": ['double', u'μm', 34.8, 0, 350]},
    "placeB": {"side": 0, "mirrorLayer": 21, "color": getFromSettings_Color_1('SilkColor', 4294967295), "description": "Placement, bottom side", "value": ['double', u'μm', 34.8, 0, 350]},
}

def replaceMirrorLayer(data, value):
    data["mirrorLayer"] = value
    return data

softLayers = {
    "eagle": {
        0: layersList["anno"],
        1: replaceMirrorLayer(layersList["pathT"], 16),
        16: replaceMirrorLayer(layersList["pathB"], 1),
        17: replaceMirrorLayer(layersList["padT"], 18),
        18: replaceMirrorLayer(layersList["padB"], 17),
        21: replaceMirrorLayer(layersList["placeT"], 22),
        22: replaceMirrorLayer(layersList["placeB"], 21),
        35: replaceMirrorLayer(layersList["glueT"], 36),
        36: replaceMirrorLayer(layersList["glueB"], 35),
        39: {"side": 1, "mirrorLayer": None, "color": getFromSettings_Color_1('tPlaceKeepoutColor', 4278190335), "ltype": 'tPlaceKeepout', "description": "Place Keepout, top side", "value": ['int', '%', 50, 0, 100]},
        40: {"side": 0, "mirrorLayer": None, "color": getFromSettings_Color_1('bPlaceKeepoutColor', 65535), "ltype": 'bPlaceKeepout', "description": "Place Keepout, bottom side", "value": ['int', '%', 50, 0, 100]},
        41: {"side": 1, "mirrorLayer": None, "color": getFromSettings_Color_1('tRouteKeepoutColor', 4278190335), "ltype": 'tRouteKeepout', "description": "Route Keepout, top side", "value": ['int', '%', 50, 0, 100]},
        42: {"side": 0, "mirrorLayer": None, "color": getFromSettings_Color_1('bRouteKeepoutColor', 65535), "ltype": 'bRouteKeepout', "description": "Route Keepout, bottom side", "value": ['int', '%', 50, 0, 100]},
        43: {"side": -1, "mirrorLayer": None, "color": getFromSettings_Color_1('vRouteKeepoutColor', 255), "ltype": 'vRouteKeepout', "description": "Via Keepout", "value": ['int', '%', 50, 0, 100]},
        47: layersList["measure"],
        51: replaceMirrorLayer(layersList["silkT"], 52),
        52: replaceMirrorLayer(layersList["silkB"], 51),
    },
    "librepcb": {
        "top_cu": replaceMirrorLayer(layersList["pathT"], "bot_cu"),
        "bot_cu": replaceMirrorLayer(layersList["pathB"], "top_cu"),
        "top_pad": replaceMirrorLayer(layersList["padT"], "bot_pad"),
        "bot_pad": replaceMirrorLayer(layersList["padB"], "top_pad"),
        "top_documentation": replaceMirrorLayer(layersList["silkT"], "bot_documentation"),
        "bot_documentation": replaceMirrorLayer(layersList["silkB"], "top_documentation"),
        "top_placement":  replaceMirrorLayer(layersList["placeT"], "bot_placement"),
        "bot_placement": replaceMirrorLayer(layersList["placeB"], "top_placement"),
        "anno": layersList["anno"],
        "top_glue": replaceMirrorLayer(layersList["glueT"], "bot_glue"),
        "bot_glue": replaceMirrorLayer(layersList["glueB"], "top_glue"),
    },
    "freepcb": {
        7: replaceMirrorLayer(layersList["silkT"], 8),
        8: replaceMirrorLayer(layersList["silkB"], 7),
        12: replaceMirrorLayer(layersList["pathT"], 32),
        13: replaceMirrorLayer(layersList["pathB"], 12),
        97: layersList["anno"],
        98: replaceMirrorLayer(layersList["padT"], 99),
        99: replaceMirrorLayer(layersList["padB"], 98),
    },
    "idf": {
        "ANNOTATIONS": layersList["anno"],
        "ROUTE_OUTLINE": {"side": -1, "mirrorLayer": None, "color": getFromSettings_Color_1('vRouteOutlineColor', 255), "ltype": 'vRouteOutline', "description": "ROUTE_OUTLINE", "value": ['int', '%', 50, 0, 100]},
        "PLACE_OUTLINE": {"side": -1, "mirrorLayer": None, "color": getFromSettings_Color_1('vPlaceOutlineColor', 255), "ltype": 'vPlaceOutline', "description": "PLACE_OUTLINE", "value": ['int', '%', 50, 0, 100]},
        "T_ROUTE_KEEPOUT": {"side": 1, "mirrorLayer": None, "color": getFromSettings_Color_1('tRouteKeepoutColor', 4278190335), "ltype": 'tRouteKeepout', "description": "T_ROUTE_KEEPOUT", "value": ['int', '%', 50, 0, 100]},
        "B_ROUTE_KEEPOUT": {"side": 0, "mirrorLayer": None, "color": getFromSettings_Color_1('tRouteKeepoutColor', 4278190335), "ltype": 'tRouteKeepout', "description": "B_ROUTE_KEEPOUT", "value": ['int', '%', 50, 0, 100]},
        "V_ROUTE_KEEPOUT": {"side": -1, "mirrorLayer": None, "color": getFromSettings_Color_1('tRouteKeepoutColor', 4278190335), "ltype": 'tRouteKeepout', "description": "V_ROUTE_KEEPOUT", "value": ['int', '%', 50, 0, 100]},
        "VIA_KEEPOUT": {"side": -1, "mirrorLayer": None, "color": getFromSettings_Color_1('vRouteKeepoutColor', 255), "ltype": 'vRouteKeepout', "description": "VIA_KEEPOUT", "value": ['int', '%', 50, 0, 100]},
        "T_PLACE_KEEPOUT": {"side": 1, "mirrorLayer": None, "color": getFromSettings_Color_1('tPlaceKeepoutColor', 4278190335), "ltype": 'tPlaceKeepout', "description": "T_PLACE_KEEPOUT", "value": ['int', '%', 50, 0, 100]},
        "B_PLACE_KEEPOUT": {"side": 0, "mirrorLayer": None, "color": getFromSettings_Color_1('bPlaceKeepoutColor', 65535), "ltype": 'bPlaceKeepout', "description": "B_PLACE_KEEPOUT", "value": ['int', '%', 50, 0, 100]},
        "V_PLACE_KEEPOUT": {"side": -1, "mirrorLayer": None, "color": getFromSettings_Color_1('vPlaceKeepoutColor', 65535), "ltype": 'vPlaceKeepout', "description": "V_PLACE_KEEPOUT", "value": ['int', '%', 50, 0, 100]},
        "T_PLACE_REGION": {"side": 1, "mirrorLayer": None, "color": getFromSettings_Color_1('tPlaceRegionColor', 4278190335), "ltype": 'tPlaceRegion', "description": "T_PLACE_REGION", "value": ['int', '%', 50, 0, 100]},
        "B_PLACE_REGION": {"side": 0, "mirrorLayer": None, "color": getFromSettings_Color_1('tPlaceRegionColor', 4278190335), "ltype": 'bPlaceRegion', "description": "B_PLACE_REGION", "value": ['int', '%', 50, 0, 100]},
        "V_PLACE_REGION": {"side": -1, "mirrorLayer": None, "color": getFromSettings_Color_1('tPlaceRegionColor', 4278190335), "ltype": 'vPlaceRegion', "description": "V_PLACE_REGION", "value": ['int', '%', 50, 0, 100]},
    },
    "geda": {
        "anno": layersList["anno"],
        "copperT": replaceMirrorLayer(layersList["pathT"], "copperB"),
        "copperB": replaceMirrorLayer(layersList["pathB"], "copperT"),
        "padT": replaceMirrorLayer(layersList["padT"], "padB"),
        "padB": replaceMirrorLayer(layersList["padB"], "padT"),
        "silkT": replaceMirrorLayer(layersList["silkT"], "silkB"),
        "silkB": replaceMirrorLayer(layersList["silkB"], "silkT"),
    },
    "kicad": {
        15: replaceMirrorLayer(layersList["pathT"], 0),
        0: replaceMirrorLayer(layersList["pathB"], 15),
        33: replaceMirrorLayer(layersList["glueT"], 32),
        32: replaceMirrorLayer(layersList["glueB"], 33),
        107: replaceMirrorLayer(layersList["padT"], 108),
        108: replaceMirrorLayer(layersList["padB"], 107),
        21: replaceMirrorLayer(layersList["silkT"], 20),
        20: replaceMirrorLayer(layersList["silkB"], 21),
        106: layersList["measure"],
        900: {"side": 1, "mirrorLayer": None, "color": getFromSettings_Color_1('tPlaceKeepoutColor', 4278190335), "ltype": 'tPlaceKeepout', "description": "Place Keepout, top side", "value": ['int', '%', 50, 0, 100]},
        901: {"side": 0, "mirrorLayer": None, "color": getFromSettings_Color_1('bPlaceKeepoutColor', 65535), "ltype": 'bPlaceKeepout', "description": "Place Keepout, bottom side", "value": ['int', '%', 50, 0, 100]},
        902: {"side": 1, "mirrorLayer": None, "color": getFromSettings_Color_1('tRouteKeepoutColor', 4278190335), "ltype": 'tRouteKeepout', "description": "Route Keepout, top side", "value": ['int', '%', 50, 0, 100]},
        903: {"side": 0, "mirrorLayer": None, "color": getFromSettings_Color_1('bRouteKeepoutColor', 65535), "ltype": 'bRouteKeepout', "description": "Route Keepout, bottom side", "value": ['int', '%', 50, 0, 100]},
        904: {"side": -1, "mirrorLayer": None, "color": getFromSettings_Color_1('vRouteKeepoutColor', 255), "ltype": 'vRouteKeepout', "description": "Via Keepout", "value": ['int', '%', 50, 0, 100]},
        905: layersList["anno"],
    },
    "kicad_v4": {
        0: replaceMirrorLayer(layersList["pathT"], 31),
        31: replaceMirrorLayer(layersList["pathB"], 0),
        33: replaceMirrorLayer(layersList["glueT"], 32),
        32: replaceMirrorLayer(layersList["glueB"], 33),
        107: replaceMirrorLayer(layersList["padT"], 108),
        108: replaceMirrorLayer(layersList["padB"], 107),
        37: replaceMirrorLayer(layersList["silkT"], 36),
        36: replaceMirrorLayer(layersList["silkB"], 37),
        106: layersList["measure"],
        900: {"side": 1, "mirrorLayer": None, "color": getFromSettings_Color_1('tPlaceKeepoutColor', 4278190335), "ltype": 'tPlaceKeepout', "description": "Place Keepout, top side", "value": ['int', '%', 50, 0, 100]},
        901: {"side": 0, "mirrorLayer": None, "color": getFromSettings_Color_1('bPlaceKeepoutColor', 65535), "ltype": 'bPlaceKeepout', "description": "Place Keepout, bottom side", "value": ['int', '%', 50, 0, 100]},
        902: {"side": 1, "mirrorLayer": None, "color": getFromSettings_Color_1('tRouteKeepoutColor', 4278190335), "ltype": 'tRouteKeepout', "description": "Route Keepout, top side", "value": ['int', '%', 50, 0, 100]},
        903: {"side": 0, "mirrorLayer": None, "color": getFromSettings_Color_1('bRouteKeepoutColor', 65535), "ltype": 'bRouteKeepout', "description": "Route Keepout, bottom side", "value": ['int', '%', 50, 0, 100]},
        904: {"side": -1, "mirrorLayer": None, "color": getFromSettings_Color_1('vRouteKeepoutColor', 255), "ltype": 'vRouteKeepout', "description": "Via Keepout", "value": ['int', '%', 50, 0, 100]},
        905: layersList["anno"],
    },
    "hyp": {
        1: replaceMirrorLayer(layersList["pathT"], 16),
        16: replaceMirrorLayer(layersList["pathB"], 1),
        17: replaceMirrorLayer(layersList["padT"], 18),
        18: replaceMirrorLayer(layersList["padB"], 17),
    },
}


kicadColorsDefinition = {
    0: [0, 0, 0],
    1: [0, 0, 0],
    2: [0, 0, 0],
    3: [0, 0, 0],
    4: [0, 0, 0],
    5: [0, 0, 0],
    6: [0, 0, 0],
    7: [0, 0, 0],
    8: [0, 0, 0],
    9: [0, 0, 0],
    10: [0, 0, 0],
    11: [0, 0, 0],
    12: [0, 0, 0],
    13: [0, 0, 0],
    14: [0, 0, 0],
    15: [0, 0, 0],
    16: [0, 0, 0],
    17: [0, 0, 0],
    18: [0, 0, 0],
    19: [0, 0, 0],
    20: [0, 0, 0],
    21: [0, 0, 0],
    22: [0, 0, 0],
    23: [0, 0, 0],
    24: [0, 0, 0],
    25: [0, 0, 0],
    26: [0, 0, 0],
    27: [0, 0, 0],
    28: [0, 0, 0],
    29: [0, 0, 0],
    30: [0, 0, 0]
}

eagleColorsDefinition = {
    0: [0, 0, 0],
    1: [50, 50, 200],
    2: [50, 200, 50],
    3: [50, 200, 200],
    4: [200, 50, 50],
    5: [200, 50, 200],
    6: [200, 200, 50],
    7: [200, 200, 200],
    8: [100, 100, 100],
    9: [0, 0, 255],
    10: [0, 255, 0],
    11: [0, 255, 255],
    12: [255, 0, 0],
    13: [255, 0, 255],
    14: [255, 255, 0],
    15: [255, 255, 255],
    16: [204, 102, 0],
    17: [204, 153, 0],
    18: [51, 102, 0],
    19: [102, 102, 51],
    20: [102, 153, 102],
    21: [51, 102, 102],
    22: [0, 153, 102],
    23: [0, 102, 153],
    24: [255, 153, 0],
    25: [255, 204, 51],
    26: [105, 153, 0],
    27: [153, 153, 102],
    28: [153, 204, 153],
    29: [102, 153, 153],
    30: [51, 204, 153],
    31: [0, 153, 204],
    32: [153, 102, 153],
    33: [204, 153, 153],
    34: [204, 102, 102],
    35: [102, 0, 51],
    36: [102, 51, 102],
    37: [153, 102, 102],
    38: [51, 102, 153],
    39: [51, 153, 153],
    40: [204, 153, 204],
    41: [255, 204, 204],
    42: [255, 153, 153],
    43: [153, 0, 51],
    44: [153, 102, 153],
    45: [204, 153, 153],
    46: [102, 153, 204],
    47: [102, 204, 204],
    48: [251, 175, 93],
    49: [175, 209, 52],
    50: [106, 106, 106],
    51: [126, 126, 126],
    52: [126, 126, 126],
    53: [150, 150, 150],
    54: [150, 150, 150],
    55: [150, 150, 150],
    56: [253, 198, 137],
    57: [217, 255, 61],
    58: [227, 227, 227],
    59: [214, 37, 37],
    60: [57, 212, 55],
    61: [230, 230, 0],
    62: [44, 123, 206],
    63: [149, 38, 222]
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
