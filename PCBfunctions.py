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
import random
from PySide import QtCore, QtGui
import os
from math import sqrt, atan2, sin, cos, radians, pi, hypot, atan


__currentPath__ = os.path.abspath(os.path.join(os.path.dirname(__file__), ''))


def wygenerujID(ll, lc):
    ''' generate random section name '''
    numerID = ""

    for i in range(ll):
        numerID += random.choice('abcdefghij')
    numerID += "_"
    for i in range(lc):
        numerID += str(random.randrange(0, 99, 1))
    
    return numerID

class kolorWarstwy(QtGui.QPushButton):
    def __init__(self, parent=None):
        QtGui.QPushButton.__init__(self, parent)
        self.setStyleSheet('''
            QPushButton
            {
                border: 1px solid #000;
                background-color: rgb(255, 0, 0);
                margin: 1px;
            }
        ''')
        self.setFlat(True)
        #self.setFixedSize(20, 20)
        self.kolor = [0., 0., 0.]
        #
        self.connect(self, QtCore.SIGNAL("released ()"), self.pickColor)
        
    def PcbColorToRGB(self, baseColor):
        returnColor = []
        
        returnColor.append(baseColor[0] * 255)
        returnColor.append(baseColor[1] * 255)
        returnColor.append(baseColor[2] * 255)
        
        return returnColor
        
    def setColor(self, nowyKolorRGB):
        self.kolor = nowyKolorRGB
        self.setStyleSheet('''
            QPushButton
            {
                border: 1px solid #000;
                background-color: rgb(%i, %i, %i);
                margin: 1px;
            }
        ''' % (nowyKolorRGB[0],
               nowyKolorRGB[1],
               nowyKolorRGB[2]))
    
    def pickColor(self):
        pick = QtGui.QColorDialog(QtGui.QColor(self.kolor[0], self.kolor[1], self.kolor[2]))
        if pick.exec_():
            [R, G, B, A] = pick.selectedColor().getRgb()
            
            self.setColor([R, G, B])

    def getColor(self):
        R = float(self.kolor[0] / 255.)
        G = float(self.kolor[1] / 255.)
        B = float(self.kolor[2] / 255.)
        return (R, G, B)


def getFromSettings_Color_0(val, defVal):
    return FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetUnsigned(val, defVal)

def getFromSettings_Color_1(val, defVal):
    color = getFromSettings_Color_0(val, defVal)
    
    r = float((color>>24)&0xFF)
    g = float((color>>16)&0xFF)
    b = float((color>>8)&0xFF)
    
    return [r, g, b]

def getFromSettings_Color(val, defVal):
    color = getFromSettings_Color_0(val, defVal)
    
    r = float((color>>24)&0xFF)/255.0
    g = float((color>>16)&0xFF)/255.0
    b = float((color>>8)&0xFF)/255.0
    
    return (r, g, b)

def getFromSettings_databasePath():
    if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("databasePath", "").strip() != '':
        return FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/PCB").GetString("databasePath", "")
    else:
        return __currentPath__ + '/data/database.cfg'




########################################################################
####
####
####            MATH FUNCTIONS
####
####
########################################################################

class mathFunctions(object):
    def sinus(self, angle):
        return float("%4.10f" % sin(radians(angle)))
        
    def cosinus(self, angle):
        return float("%4.10f" % cos(radians(angle)))
    
    def arcCenter(self, x1, y1, x2, y2, x3, y3):
        Xs = 0.5 * (x2 * x2 * y3 + y2 * y2 * y3 - x1 * x1 * y3 + x1 * x1 * y2 - y1 * y1 * y3 + y1 * y1 * y2 + y1 * x3 * x3 + y1 * y3 * y3 - y1 * x2 * x2 - y1 * y2 * y2 - y2 * x3 * x3 - y2 * y3 * y3) / (y1 * x3 - y1 * x2 - y2 * x3 - y3 * x1 + y3 * x2 + y2 * x1)
        Ys = 0.5 * (-x1 * x3 * x3 - x1 * y3 * y3 + x1 * x2 * x2 + x1 * y2 * y2 + x2 * x3 * x3 + x2 * y3 * y3 - x2 * x2 * x3 - y2 * y2 * x3 + x1 * x1 * x3 - x1 * x1 * x2 + y1 * y1 * x3 - y1 * y1 * x2) / (y1 * x3 - y1 * x2 - y2 * x3 - y3 * x1 + y3 * x2 + y2 * x1)
        
        return [Xs, Ys]
    
    def shiftPointOnLine(self, x1, y1, x2, y2, distance):
        if x2 - x1 == 0:  # vertical line
            
            
            x_T1 = x1
            y_T1 = y1 - distance
        else:
            a = (y2 - y1) / (x2 - x1)
            
            if a == 0:  # horizontal line
                x_T1 = x1 - distance
                y_T1 = y1
            else:
                alfa = atan(a)
                #alfa = tan(a)

                x_T1 = x1 - distance * cos(alfa)
                y_T1 = y1 - distance * sin(alfa)

        return [x_T1, y_T1]
        
    def obrocPunkt2(self, punkt, srodek, angle):
        sinKAT = self.sinus(angle)
        cosKAT = self.cosinus(angle)
        
        x1R = ((punkt[0] - srodek[0]) * cosKAT) - sinKAT * (punkt[1] - srodek[1]) + srodek[0]
        y1R = ((punkt[0] - srodek[0]) * sinKAT) + cosKAT * (punkt[1] - srodek[1]) + srodek[1]
        return [x1R, y1R]


    def obrocPunkt(self, punkt, srodek, angle):
        sinKAT = self.sinus(angle)
        cosKAT = self.cosinus(angle)
        
        x1R = (punkt[0] * cosKAT) - (punkt[1] * sinKAT) + srodek[0]
        y1R = (punkt[0] * sinKAT) + (punkt[1] * cosKAT) + srodek[1]
        return [x1R, y1R]
        

    def odbijWspolrzedne(self, punkt, srodek):
        ''' mirror '''
        return srodek + (srodek - punkt)
        
    def arc3point(self, stopAngle, startAngle, radius, cx, cy):
        d = stopAngle - startAngle
        offset = 0
        if d < 0.0:
            offset = 3.14
        x3 = cos(((startAngle + stopAngle) / 2.) + offset) * radius + cx
        y3 = -sin(((startAngle + stopAngle) / 2.) + offset) * radius + cy
        
        return [x3, y3]
        
    def arcRadius(self, x1, y1, x2, y2, angle):
        #dx = abs(x2 - x1)
        #dy = abs(y2 - y1)
        #d = sqrt(dx ** 2 + dy ** 2)  # distance between p1 and p2

        # point M - center point between p1 and p2
        Mx = (x1 + x2) / 2.
        My = (y1 + y2) / 2.
        
        # p1_M - distance between point p1 and M
        p1_M = sqrt((x1 - Mx) ** 2 + (y1 - My) ** 2)
        radius = float("%4.9f" % abs(p1_M / sin(radians(angle / 2.))))  # radius of searching circle - line C_p1
        
        return radius
    
    def arcAngles(self, x1, y1, x2, y2, Cx, Cy, angle):
        if angle > 0:
            startAngle = atan2(y1 - Cy, x1 - Cx)
            if startAngle < 0.:
                startAngle = 6.28 + startAngle
                    
            stopAngle = startAngle + radians(angle)  # STOP ANGLE
        else:
            startAngle = atan2(y2 - Cy, x2 - Cx)
            if startAngle < 0.:
                startAngle = 6.28 + startAngle

            stopAngle = startAngle + radians(abs(angle))  # STOP ANGLE
        #
        startAngle = float("%4.2f" % startAngle) - pi/2
        stopAngle = float("%4.2f" % stopAngle) - pi/2
        
        return [startAngle, stopAngle]
        
    #***************************************************************************
    #*   (c) Milos Koutny (milos.koutny@gmail.com) 2012                        *
    #*   Idf.py                                                                *
    #***************************************************************************
    def arcMidPoint(self, prev_vertex, vertex, angle):
        [x1, y1] = prev_vertex
        [x2, y2] = vertex
        
        angle = radians(angle / 2)
        basic_angle = atan2(y2 - y1, x2 - x1) - pi / 2
        shift = (1 - cos(angle)) * hypot(y2 - y1, x2 - x1) / 2 / sin(angle)
        midpoint = [(x2 + x1) / 2 + shift * cos(basic_angle), (y2 + y1) / 2 + shift * sin(basic_angle)]
        
        return midpoint
        
    def arcGetAngle(self, center, p1, p2):
        angle_1 = atan2((p1[1] - center[1]) * -1, (p1[0] - center[0])) * 180 / pi
        angle_2 = atan2((p2[1] - center[1]) * -1, (p2[0] - center[0])) * 180 / pi

        return angle_1 - angle_2
        
    def toQuaternion(self, heading, attitude, bank):  # rotation heading=arround Y, attitude =arround Z,  bank attitude =arround X
        ''' #***************************************************************************
            #*              (c) Milos Koutny (milos.koutny@gmail.com) 2010             *
            #***************************************************************************
            toQuaternion(heading, attitude,bank)->FreeCAD.Base.Rotation(Quternion)'''
        c1 = cos(heading / 2)
        s1 = sin(heading / 2)
        c2 = cos(attitude / 2)
        s2 = sin(attitude / 2)
        c3 = cos(bank / 2)
        s3 = sin(bank / 2)
        c1c2 = c1 * c2
        s1s2 = s1 * s2
        w = c1c2 * c3 - s1s2 * s3
        x = c1c2 * s3 + s1s2 * c3
        y = s1 * c2 * c3 + c1 * s2 * s3
        z = c1 * s2 * c3 - s1 * c2 * s3
        return FreeCAD.Base.Rotation(x, y, z, w)
        #return FreeCAD.Rotation(FreeCAD.Vector(x, y, z), w)
