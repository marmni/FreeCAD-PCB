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
from PySide import QtGui

__scriptVersion__ = 5.0
__pythonVersion__ = 3.6
__requiredFreeCADVersion__ = (0.18, 0.20)  # (min, max)


def currentFreeCADVersion():
    data = FreeCAD.Version()
    # data[1] may contain '18' or '18.4'. In case of '18.4', just keep the '18' part
    return float(data[0] + '.' + (data[1][:data[1].index('.')] if '.' in data[1] else data[1]))


# def checkCompatibility():
    # ''' InitGui -> Initialize() '''
    # currentFCVersion = currentFreeCADVersion()
    # #
    # if currentFCVersion >= __requiredFreeCADVersion__[0] and currentFCVersion <= __requiredFreeCADVersion__[1]:
        # # if float("{0}.{1}".format(sys.version_info[0], sys.version_info[1])) < __pythonVersion__:
            # # FreeCAD.Console.PrintWarning("PCB Workbench: Error. Minimum required Python version: {0}.\n".format(__pythonVersion__))
            # # return [False]
        # # else:
        # return [True]
    # elif currentFCVersion <= __requiredFreeCADVersion__[0]:
        # FreeCAD.Console.PrintError("PCB Workbench: Error\n\tYour version of FreeCAD is too old. Supported versions => {0}.\n".format(__requiredFreeCADVersion__[0]))
        # return [False]
    # else:
        # FreeCAD.Console.PrintWarning("PCB Workbench: Warning\n\tIncompatible FreeCAD version. Supported versions: {0}-{1}.\n".format(__requiredFreeCADVersion__[0], __requiredFreeCADVersion__[1]))
        # return [True]


def setDefaultValues():
    ''' InitGui -> Initialize() '''
    data = {
        "scriptVersion": ['f', __scriptVersion__]
    }

    for i, j in data.items():
        if j[0] == 'f' and FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetFloat(i, 0.0) == 0.0:
            FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").SetFloat(i, float(j[1]))
