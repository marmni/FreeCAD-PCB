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
#*                            DXF OBJECTS
#***********************************************************************
class DXF_Circle:
    def __init__(self, layer):
        self.layer = layer
        self.x = 0
        self.y = 0
        self.r = 1
        self.color = 8
        
    def __str__(self):
        return str([
            [0, 'CIRCLE'],  # Entity type
            [8, self.layer],  # Layer name
            [62, self.color],  # Color number
            [10, self.x],  # Center point (in OCS) DXF: X value; APP: 3D point
            [20, self.y],  # DXF: Y values of center point (in OCS)
            [30, 0.0],  # DXF: Z values of center point (in OCS)
            [40, self.r],  # Radius
        ])


class DXF_Arc:
    def __init__(self, layer):
        self.layer = layer
        self.x = 0
        self.y = 0
        self.r = 1
        self.startAngle = 0
        self.stopAngle = 90
        self.color = 8
        
    def __str__(self):
        return str([
            [0, 'ARC'],  # Entity type
            [8, self.layer],  # Layer name
            [62, self.color],  # Color number
            [10, self.x],  # Center point (in OCS) DXF: X value; APP: 3D point
            [20, self.y],  # DXF: Y values of center point (in OCS)
            [30, 0.0],  # DXF: Z values of center point (in OCS)
            [40, self.r],  # Radius
            [50, self.startAngle],  # Start angle
            [51, self.stopAngle],  # End angle
        ])


class DXF_Line:
    def __init__(self, layer):
        self.layer = layer
        self.p1 = [0.0, 0.0, 0.0]
        self.p2 = [0.0, 0.0, 0.0]
        self.color = 8
        
    def __str__(self):
        return str([
            [0, 'POLYLINE'],  # Entity type
            [8, self.layer],  # Layer name
            [62, self.color],  # Color number
            #[70, 0],  # Polyline flag (bit-coded; default = 0):
            [10, 0.0],  # DXF: always 0
            [20, 0.0],  # DXF: always 0
            [30, 0.0],  # DXF: polyline's elevation (in OCS when 2D; WCS when 3D)
            
            [0, 'VERTEX'],  # Entity type
            [8, self.layer],  # Layer name
            [10, self.p1[0]],  # DXF: always 0
            [20, self.p1[1]],  # DXF: always 0
            [30, self.p1[2]],  # DXF: polyline's elevation (in OCS when 2D; WCS when 3D)
            
            [0, 'VERTEX'],  # Entity type
            [8, self.layer],  # Layer name
            [10, self.p2[0]],  # DXF: always 0
            [20, self.p2[1]],  # DXF: always 0
            [30, self.p2[2]],  # DXF: polyline's elevation (in OCS when 2D; WCS when 3D)
            
            [0, 'SEQEND'],  # Entity type
            [8, self.layer],  # Layer name
        ])


class DXF_Text:
    def __init__(self, layer, txt):
        self.layer = layer
        self.p = [0.0, 0.0, 0.0]
        self.color = 2
        self.text = txt
        self.height = 3
    
    def __str__(self):
        return str([
            [0, 'TEXT'],  # Entity type
            [1, self.text],  # string
            [8, self.layer],  # Layer name
            [62, self.color],  # Color number
            [10, self.p[0]],  # DXF: always 0
            [20, self.p[1]],  # DXF: always 0
            [30, self.p[2]],  # DXF: polyline's elevation (in OCS when 2D; WCS when 3D)
            #[72, 2],  # Horizontal text justification type
            [40, self.height],  # Text height
            [0, 'SEQEND'],  # Entity type
            [8, self.layer],  # Layer name
        ])


class DXF_Layer:
    def __init__(self, name):
        self.layerName = name
        
    def __str__(self):
        return str([
            [0, 'TABLE'],  # 
            [2, self.layerName],  # 
            [62, 2],  # 
            [6, 'continuous'],  # 
            [0, 'ENDTAB'],  #
        ])
