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

# ['l', '[, ]', '[, ]']
# ['c', 'x', 'y', 'r']

drillingSymbols = [
    [['l', "[x-r, y]", "[x+r, y]"]],  # -
    [['c', 'x', 'y', 'r']],  # 0
    [['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"]],  # x
    [['l', "[x-r, y]", "[x+r, y]"], ['l', "[x, y+r]", "[x, y-r]"]],  # +
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y+r]", "[x+r, y-r]"], ['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r, y-r]", "[x-r, y+r]"]],  # square
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y+r]", "[x+r, y-r]"], ['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r, y-r]", "[x-r, y+r]"], ['c', 'x', 'y', 'r']],  # 0 in square
    [['c', 'x', 'y', 'r'], ['c', 'x', 'y', 'r/2.0']],  # 0 in 0
    [['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['c', 'x', 'y', 'r']],  # x in 0
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y+r]", "[x+r, y-r]"], ['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r, y-r]", "[x-r, y+r]"], ['l', "x-r,y+r", "x+r,y-r"], ['l', "x-r,y-r", "x+r,y+r"]],  # x in square
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y+r]", "[x+r, y-r]"], ['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r, y-r]", "[x-r, y+r]"], ['l', "x-r,y+r", "x+r,y-r"], ['l', "x-r,y-r", "x+r,y+r"], ['c', 'x', 'y', 'r']],  # x in 0 in square
    [['l', "[x-r, y]", "[x+r, y]"], ['l', "[x, y+r]", "[x, y-r]"], ['c', 'x', 'y', 'r']],  # + in 0
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y+r]", "[x+r, y-r]"], ['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r, y-r]", "[x-r, y+r]"], ['l', "[x-r, y]", "[x+r, y]"], ['l', "[x, y+r]", "[x, y-r]"]],  # + in square
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y+r]", "[x+r, y-r]"], ['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r, y-r]", "[x-r, y+r]"], ['l', "[x-r, y]", "[x+r, y]"], ['l', "[x, y+r]", "[x, y-r]"], ['c', 'x', 'y', 'r']],  # + in 0 in square
    [['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['l', "[x,y-r]", "[x,y+r]"]],  # *
    [['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['l', "[x,y-r]", "[x,y+r]"], ['c', 'x', 'y', 'r']],  # * in 0
    [['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['l', "[x,y-r]", "[x,y+r]"], ['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y+r]", "[x+r, y-r]"], ['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r, y-r]", "[x-r, y+r]"]],  # * in 0 in square
    [['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['l', "[x-r,y]", "[x+r,y]"]],  # *(v2)
    [['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['l', "[x-r,y]", "[x+r,y]"], ['c', 'x', 'y', 'r']],  # *(v2) in 0
    [['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['l', "[x-r,y]", "[x+r,y]"], ['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y+r]", "[x+r, y-r]"], ['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r, y-r]", "[x-r, y+r]"]],  # *(v2) in 0 in square
    [['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['l', "[x-r,y]", "[x+r,y]"], ['l', "[x,y-r]", "[x,y+r]"]],  # *(v3)
    [['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['l', "[x-r,y]", "[x+r,y]"], ['l', "[x,y-r]", "[x,y+r]"], ['c', 'x', 'y', 'r']],  # *(v3) in 0
    [['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['l', "[x-r,y]", "[x+r,y]"], ['l', "[x,y-r]", "[x,y+r]"], ['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y+r]", "[x+r, y-r]"], ['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r, y-r]", "[x-r, y+r]"]],  # *(v3) in 0 in square
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y+r]", "[x+r, y-r]"], ['c', 'x', 'y', 'r']],  # 0 in not full square
    [['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r, y-r]", "[x-r, y+r]"], ['c', 'x', 'y', 'r']],  # 0 in not full square
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y+r]", "[x+r, y-r]"], ['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"]],  # x in not full square
    [['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r, y-r]", "[x-r, y+r]"], ['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"]],  # x in not full square
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y+r]", "[x+r, y-r]"], ['l', "[x-r, y]", "[x+r, y]"], ['l', "[x, y+r]", "[x, y-r]"]],  # + in not full square
    [['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r, y-r]", "[x-r, y+r]"], ['l', "[x-r, y]", "[x+r, y]"], ['l', "[x, y+r]", "[x, y-r]"]],  # + in not full square
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y+r]", "[x+r, y-r]"], ['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['l', "[x,y-r]", "[x,y+r]"]],  # * in not full square
    [['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r, y-r]", "[x-r, y+r]"], ['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['l', "[x,y-r]", "[x,y+r]"]],  # * in not full square
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y+r]", "[x+r, y-r]"], ['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['l', "[x-r,y]", "[x+r,y]"]],  # *(v2) in not full square
    [['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r, y-r]", "[x-r, y+r]"], ['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['l', "[x-r,y]", "[x+r,y]"]],  # *(v2) in not full square
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y+r]", "[x+r, y-r]"], ['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['l', "[x-r,y]", "[x+r,y]"], ['l', "[x,y-r]", "[x,y+r]"]],  # *(v3) in not full square
    [['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r, y-r]", "[x-r, y+r]"], ['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['l', "[x-r,y]", "[x+r,y]"], ['l', "[x,y-r]", "[x,y+r]"]],  # *(v3) in not full square
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y-r]", "[x-r, y-r]"], ['c', 'x', 'y', 'r']],  # 0 in not full square
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y-r]", "[x-r, y-r]"], ['c', 'x', 'y', 'r']],  # 0 in not full square
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"]],  # x in not full square
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"]],  # x in not full square
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r, y]", "[x+r, y]"], ['l', "[x, y+r]", "[x, y-r]"]],  # + in not full square
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r, y]", "[x+r, y]"], ['l', "[x, y+r]", "[x, y-r]"]],  # + in not full square
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['l', "[x,y-r]", "[x,y+r]"]],  # * in not full square
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['l', "[x,y-r]", "[x,y+r]"]],  # * in not full square
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['l', "[x-r,y]", "[x+r,y]"]],  # *(v2) in not full square
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['l', "[x-r,y]", "[x+r,y]"]],  # *(v2) in not full square
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['l', "[x-r,y]", "[x+r,y]"], ['l', "[x,y-r]", "[x,y+r]"]],  # *(v3) in not full square
    [['l', "[x-r, y+r]", "[x+r, y+r]"], ['l', "[x+r, y-r]", "[x-r, y-r]"], ['l', "[x-r,y+r]", "[x+r,y-r]"], ['l', "[x-r,y-r]", "[x+r,y+r]"], ['l', "[x-r,y]", "[x+r,y]"], ['l', "[x,y-r]", "[x,y+r]"]],  # *(v3) in not full square
]
