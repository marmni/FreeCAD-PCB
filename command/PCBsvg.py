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


#***********************************************************************
#*                            SVG OBJECTS
#***********************************************************************
class SVG_Object:
    def setColor(self):
        data = '#'
        
        for i in self.color:
            val = str(i)
            if len(val) == 1:
                val = val + '0'
            data = data + val
            
        if data == '#ffffff':
            data = '#000000'
        
        return data


class SVG_Line(SVG_Object):
    def __init__(self):
        self.p1 = [0.0, 0.0, 0.0]
        self.p2 = [0.0, 0.0, 0.0]
        self.color = [0, 0, 0]
        self.width = 0.1
    
    def __str__(self):
        return '''
            <line 
                    style="fill:{color};stroke:{color};stroke-width:{self.width}px;"
                    x1 = "{self.p1[0]}"
                    y1 = "{self.p1[1]}"
                    x2 = "{self.p2[0]}"
                    y2 = "{self.p2[1]}"
            />'''.format(self=self, color=self.setColor())


class SVG_Circle(SVG_Object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.r = 1
        self.color = [0 ,0 ,0]
        self.width = 0.1
    
    def __str__(self):
        return '''
            <circle 
                    style="fill:none;stroke:{color};stroke-width:{self.width}px;"
                    cx = "{self.x}"
                    cy = "{self.y}"
                    r = "{self.r}"
            />'''.format(self=self, color=self.setColor())


class SVG_Text(SVG_Object):
    def __init__(self, txt):
        self.x = 0
        self.y = 0
        self.fontSize = 1
        self.color = [255 ,255 ,0]
        self.txt = txt
        
    def __str__(self):
        return '''
            <text
               x="{self.x}"
               y="{self.y}"
               style="font-size:{self.fontSize}px;font-style:normal;font-weight:normal;line-height:125%;letter-spacing:0px;word-spacing:0px;fill:{color}fill-opacity:1;stroke:none;font-family:Sans">
               <tspan
                 x="{self.x}"
                 y="{self.y}">{self.txt}</tspan></text>'''.format(self=self, color=self.setColor())
