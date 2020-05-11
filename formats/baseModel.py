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
import Part
try:
    import builtins
except:
    import __builtin__ as builtins
from math import sqrt
#
from PCBfunctions import mathFunctions


class baseModel(mathFunctions):
    def filterHoles(self, r, Hmin, Hmax):
        if Hmin == 0 and Hmax == 0:
            return True
        elif Hmin != 0 and Hmax == 0 and Hmin <= r * 2:
            return True
        elif Hmax != 0 and Hmin == 0 and r * 2 <= Hmax:
            return True
        elif Hmin <= r * 2 <= Hmax:
            return True
        else:
            return False
    
    def addHoleToObject(self, holesObject, Hmin, Hmax, iH, x, y, r, holesList):
        try:
            if self.filterHoles(r, Hmin, Hmax):
                if iH:  # detecting collisions between holes - intersections
                    if self.detectIntersectingHoles(holesList, x, y, r):
                        holesList.append([x, y, r])
                        holesObject.addGeometry(Part.Circle(FreeCAD.Vector(x, y, 0.), FreeCAD.Vector(0, 0, 1), r))
                else:
                    holesObject.addGeometry(Part.Circle(FreeCAD.Vector(x, y, 0.), FreeCAD.Vector(0, 0, 1), r))
        except Exception as e:
            print("Error in addHoleToObject(): " + e)
        
        return holesList
    
    def detectIntersectingHoles(self, holesList, x, y, r):
        add = True
        #
        try:
            for k in holesList:
                d = sqrt( (x - k[0]) ** 2 + (y - k[1]) ** 2)
                if(d < r + k[2]):
                    add = False
                    break
        except Exception as e:
            FreeCAD.Console.PrintWarning("1. {0}\n".format(e))
        #
        if add:
            return True
        else:
            FreeCAD.Console.PrintWarning("Intersection between holes detected. Hole x={:.2f}, y={:.2f} will be omitted.\n".format(x, y))
            return False
    
    def filterTentedVias(self, tentedViasLimit, tentedVias, drill, alwaysstop):
        if tentedVias:
            if tentedViasLimit > 0 and drill > tentedViasLimit:
                return True
            elif tentedViasLimit > 0 and drill <= tentedViasLimit and alwaysstop:
                return True
        else:
            if tentedViasLimit > 0 and drill <= tentedViasLimit and not alwaysstop:
                return True
        
        return False
    
    def setProjectFile(self, filename, char=['(', ')'], loadFromFile=True):
        if loadFromFile:
            projektBRD = builtins.open(filename, "r").read()[1:]
        else:
            projektBRD = filename
        #
        wynik = ''
        licznik = 0
        txt = ''
        start = 0
        #
        txt_1 = 0

        for i in projektBRD:
            if i in ['"', "'"] and txt_1 == 0:
                txt_1 = 1
            elif i in ['"', "'"] and txt_1 == 1:
                txt_1 = 0
            #
            if txt_1 == 0:
                if i == char[0]:
                    licznik += 1
                    start = 1
                elif i == char[1]:
                    licznik -= 1
            #
            txt += i
            #
            if licznik == 0 and start == 1:
                wynik += '[start]' + txt.strip() + '[stop]'
                txt = ''
                start = 0
        #
        return wynik
