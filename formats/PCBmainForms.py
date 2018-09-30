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
if FreeCAD.GuiUp:
    import FreeCADGui
    from PySide import QtCore, QtGui
from math import sqrt
import DraftGeomUtils
import Draft
import Part
import os
import builtins
import unicodedata
import time
#
import PCBconf
from PCBpartManaging import partsManaging
from PCBfunctions import kolorWarstwy, mathFunctions, getFromSettings_Color_1
from PCBobjects import layerPolygonObject, viewProviderLayerPolygonObject, layerPathObject, constraintAreaObject, viewProviderConstraintAreaObject
from PCBboard import PCBboardObject, viewProviderPCBboardObject
from command.PCBgroups import *
from command.PCBannotations import createAnnotation
from command.PCBglue import createGlue
from PCBconf import PCBlayers, softLayers
from PCBobjects import *

from formats.eagle import EaglePCB
#from formats.freepcb import FreePCB
#from formats.geda import gEDA_PCB
#from formats.fidocadj import FidoCadJ_PCB
#from formats.razen import Razen_PCB
from formats.kicad_v3 import KiCadv3_PCB
from formats.kicad_v4 import KiCadv4_PCB
#from formats.idf_v2 import IDFv2_PCB
#from formats.idf_v3 import IDFv3_PCB
#from formats.idf_v4 import IDFv4_PCB
#from formats.diptrace import DipTrace_PCB
#from formats.hyp import HYP_PCB





class mainPCB(partsManaging):
    def __init__(self, wersjaFormatu, filename, parent=None):
        #reload(PCBconf)
        partsManaging.__init__(self, wersjaFormatu)
        self.projektBRD = None
        self.projektBRDName = None
        self.wersjaFormatu = None
        
        if wersjaFormatu == "eagle":
            self.wersjaFormatu = EaglePCB(filename, self)
        #elif wersjaFormatu == "freepcb":
            #self.wersjaFormatu = FreePCB()
        #elif wersjaFormatu == "geda":
            #self.wersjaFormatu = gEDA_PCB(filename)
        #elif wersjaFormatu == "fidocadj":
            #self.wersjaFormatu = FidoCadJ_PCB(filename)
        #elif wersjaFormatu == "razen":
            #self.wersjaFormatu = Razen_PCB()
        elif wersjaFormatu == "kicad_v3":
            self.wersjaFormatu = KiCadv3_PCB(filename, self)
        elif wersjaFormatu == "kicad_v4":
            self.wersjaFormatu = KiCadv4_PCB(filename, self)
        #elif wersjaFormatu == "idf_v2":
            #self.wersjaFormatu = IDFv2_PCB(filename)
        #elif wersjaFormatu == "idf_v3":
            #self.wersjaFormatu = IDFv3_PCB(filename)
        #elif wersjaFormatu == "idf_v4":
            #self.wersjaFormatu = IDFv4_PCB(filename)
        #elif wersjaFormatu == "diptrace":
            #self.wersjaFormatu = DipTrace_PCB(filename)
        #elif wersjaFormatu == "hyp_v2":
            #self.wersjaFormatu = HYP_PCB(filename)

        self.setDatabase()
        
    def setProject(self, filename):
        self.projektBRDName = filename
        self.wersjaFormatu.setProject()
        
    def printInfo(self, data, dataFormat='msg'):
        if self.wersjaFormatu.dialogMAIN.debugImport.isChecked():
            time.sleep(0.05)
            
            if dataFormat == 'error':
                FreeCAD.Console.PrintError(str(data))
            else:
                FreeCAD.Console.PrintMessage(str(data))
            
            #QtGui.qApp.processEvents()
            QtGui.QApplication.processEvents()
    
    def generate(self, doc, groupBRD):
        self.printInfo('\nInitializing')
        # BOARD
        self.generatePCB(doc, groupBRD, self.wersjaFormatu.dialogMAIN.gruboscPlytki.value())
        # HOLES
        self.generateHoles(doc, self.wersjaFormatu.dialogMAIN.holesMin.value(), self.wersjaFormatu.dialogMAIN.holesMax.value())
        # PARTS
        if self.wersjaFormatu.dialogMAIN.plytkaPCB_elementy.isChecked():
            self.importParts(self.wersjaFormatu.dialogMAIN.plytkaPCB_elementyKolory.isChecked(), self.wersjaFormatu.dialogMAIN.adjustParts.isChecked(), self.wersjaFormatu.dialogMAIN.plytkaPCB_grupujElementy.isChecked(), self.wersjaFormatu.dialogMAIN.partMinX.value(), self.wersjaFormatu.dialogMAIN.partMinY.value(), self.wersjaFormatu.dialogMAIN.partMinZ.value())
        # LAYERS
        grp = createGroup_Layers()
        grp_2 = createGroup_Areas()
        for i in range(self.wersjaFormatu.dialogMAIN.spisWarstw.rowCount()):
            if self.wersjaFormatu.dialogMAIN.spisWarstw.cellWidget(i, 0).isChecked():
                layerNumber = int(self.wersjaFormatu.dialogMAIN.spisWarstw.item(i, 1).text())
                layerName = str(self.wersjaFormatu.dialogMAIN.spisWarstw.item(i, 5).text())
                
                try:
                    layerSide = self.wersjaFormatu.dialogMAIN.spisWarstw.cellWidget(i, 3).itemData(self.wersjaFormatu.dialogMAIN.spisWarstw.cellWidget(i, 3).currentIndex())
                except:  
                    layerSide = None
                
                try:
                    layerColor = self.wersjaFormatu.dialogMAIN.spisWarstw.cellWidget(i, 2).getColor()
                except:
                    layerColor = None
                try:
                    layerTransp = self.wersjaFormatu.dialogMAIN.spisWarstw.cellWidget(i, 4).value()
                except:
                    layerTransp = None
                #
                layerFunction = self.wersjaFormatu.defineFunction(layerNumber)
                
                self.printInfo("\nImporting layer '{0}': ".format(layerName))
                try:
                    if layerFunction in ["silk", "pads", "paths"]:
                        self.generateSilkLayer(doc, layerNumber, grp, layerName, layerColor, layerTransp, layerSide, layerFunction)
                    elif layerFunction == "measures":
                        self.generateDimensions(doc, grp, layerName, layerColor, self.wersjaFormatu.dialogMAIN.gruboscPlytki.value())
                    elif layerFunction == "glue":
                        self.generateGlue(doc, grp, layerName, layerColor, layerNumber, layerSide)
                    elif layerFunction == "constraint":
                        self.generateConstraintAreas(doc, layerNumber, grp, layerName, layerColor, layerTransp)
                except Exception as e:
                    self.printInfo('{0}'.format(e), 'error')
                else:
                    self.printInfo('done')
                    
    
    def importParts(self, koloroweElemnty, adjustParts, groupParts, partMinX, partMinY, partMinZ):
        self.printInfo('\nImporting parts: ')
        errors = []
        
        for i in self.wersjaFormatu.getParts():
            self.printInfo('\n    {0} ({1}): '.format(i[0][0], i[0][1]))
            
            result = self.addPart(i, koloroweElemnty, adjustParts, groupParts, partMinX, partMinY, partMinZ)
        
            if self.wersjaFormatu.dialogMAIN.plytkaPCB_plikER.isChecked() and result[0] == 'Error':
                partNameTXT = partNameTXT_label = self.generateNewLabel(i[0][0])
                if isinstance(partNameTXT, str):
                    partNameTXT = unicodedata.normalize('NFKD', partNameTXT).encode('ascii', 'ignore')
                
                #errors.append([partNameTXT, i['package'], i['value'], i['library']])
                errors.append([partNameTXT, i[0][1], i[1], i[6]])
                self.printInfo('error', 'error')
            else:
                self.printInfo('done')
        
        if self.wersjaFormatu.dialogMAIN.plytkaPCB_plikER.isChecked() and len(errors):
            self.generateErrorReport(errors, self.projektBRDName)
    
    def generateGlue(self, doc, grp, layerName, layerColor, layerNumber, layerSide):
        for i, j in self.wersjaFormatu.getGlue([layerNumber, layerName]).items():
            ser = doc.addObject('Sketcher::SketchObject', "Sketch_{0}".format(layerName))
            ser.ViewObject.Visibility = False
            for k in j:
                if k[0] == 'line':
                    ser.addGeometry(Part.LineSegment(FreeCAD.Vector(k[1], k[2], 0), FreeCAD.Vector(k[3], k[4], 0)))
                elif k[0] == 'circle':
                    ser.addGeometry(Part.Circle(FreeCAD.Vector(k[1], k[2]), FreeCAD.Vector(0, 0, 1), k[3]))
                elif k[0] == 'arc':
                    x1 = k[1]
                    y1 = k[2]
                    x2 = k[3]
                    y2 = k[4]
                    [x3, y3] = self.arcMidPoint([x2, y2], [x1, y1], k[5])
                    
                    arc = Part.Arc(FreeCAD.Vector(x1, y1, 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(x2, y2, 0.0))
                    ser.addGeometry(self.Draft2Sketch(arc, ser))
            #
            glue = createGlue()
            glue.base = ser
            glue.width = i
            glue.side = layerSide
            glue.color = layerColor
            glue.generate()
        
    def generateDimensions(self, doc, layerGRP, layerName, layerColor, gruboscPlytki):
        layerName = "{0}".format(layerName)
        grp = doc.addObject("App::DocumentObjectGroup", layerName)
        
        for i in self.wersjaFormatu.getDimensions():
            x1 = i[0]
            y1 = i[1]
            x2 = i[2]
            y2 = i[3]
            x3 = i[4]
            y3 = i[5]
            dtype = i[6]
            
            if dtype in ["angle"]:
                continue
            
            dim = Draft.makeDimension(FreeCAD.Vector(x1, y1, gruboscPlytki), FreeCAD.Vector(x2, y2, gruboscPlytki), FreeCAD.Vector(x3, y3, gruboscPlytki))
            dim.ViewObject.LineColor = layerColor
            dim.ViewObject.LineWidth = 1.00
            dim.ViewObject.ExtLines = 0.00
            dim.ViewObject.FontSize = 2.00
            dim.ViewObject.ArrowSize = '0.5 mm'
            dim.ViewObject.ArrowType = "Arrow"
            grp.addObject(dim)
        
        layerGRP.addObject(grp)
    
    def generateSilkLayer(self, doc, layerNumber, grp, layerNameO, layerColor, defHeight, layerSide, layerVariant):
        layerName = "{0}_{1}".format(layerNameO, layerNumber)
        #layerSide = softLayers[self.wersjaFormatu.databaseType][layerNumber]['side']
        layerType = [layerName]
        #
        layerS = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", layerName)
        layerNew = layerSilkObject(layerS, layerType)
        layerNew.holes = self.showHoles()
        layerNew.side = layerSide
        layerNew.defHeight = defHeight
        #
        if layerVariant == "paths":
            self.wersjaFormatu.getSilkLayer(layerNew, [layerNumber, layerNameO], [True, True, True, False])
            self.wersjaFormatu.getPaths(layerNew, [layerNumber, layerNameO], [True, True, True, False])
        else:
            self.wersjaFormatu.getSilkLayer(layerNew, [layerNumber, layerNameO])
            self.wersjaFormatu.getSilkLayerModels(layerNew, [layerNumber, layerNameO])
                
            if layerVariant == "pads":
                self.wersjaFormatu.getPads(layerNew, [layerNumber, layerNameO], layerSide)
        #
        layerNew.generuj(layerS)
        layerNew.updatePosition_Z(layerS)
        viewProviderLayerSilkObject(layerS.ViewObject)
        layerS.ViewObject.ShapeColor = layerColor
        grp.addObject(layerS)
        #
        #
        doc.recompute()
        #FreeCADGui.activeDocument().getObject(layerS.Name).DisplayMode = 1

    def generatePCB(self, doc, groupBRD, gruboscPlytki):
        self.printInfo('\nGenerate board: ')
        
        try:
            doc.addObject('Sketcher::SketchObject', 'PCB_Border')
            doc.PCB_Border.Placement = FreeCAD.Placement(FreeCAD.Vector(0.0, 0.0, 0.0), FreeCAD.Rotation(0.0, 0.0, 0.0, 1.0))
            #
            self.wersjaFormatu.getPCB(doc.PCB_Border)
            #
            PCBboard = doc.addObject("Part::FeaturePython", "Board")
            PCBboardObject(PCBboard)
            PCBboard.Thickness = gruboscPlytki
            PCBboard.Border = doc.PCB_Border
            viewProviderPCBboardObject(PCBboard.ViewObject)
            groupBRD.addObject(doc.Board)
            FreeCADGui.activeDocument().getObject(PCBboard.Name).ShapeColor = PCBconf.PCB_COLOR
            FreeCADGui.activeDocument().PCB_Border.Visibility = False
            self.updateView()
        except Exception as e:
            self.printInfo(u'{0}'.format(e), 'error')
        else:
            self.printInfo('done')
        
    def generateHoles(self, doc, Hmin, Hmax):
        self.printInfo('\nGenerate holes: ')
        
        try:
            doc.addObject('Sketcher::SketchObject', 'PCB_Holes')
            doc.PCB_Holes.Placement = FreeCAD.Placement(FreeCAD.Vector(0.0, 0.0, 0.0), FreeCAD.Rotation(0.0, 0.0, 0.0, 1.0))
            FreeCADGui.activeDocument().PCB_Holes.Visibility = False
            #
            types = {'H':self.wersjaFormatu.dialogMAIN.plytkaPCB_otworyH.isChecked(), 'V':self.wersjaFormatu.dialogMAIN.plytkaPCB_otworyV.isChecked(), 'P':self.wersjaFormatu.dialogMAIN.plytkaPCB_otworyP.isChecked()}
            self.wersjaFormatu.getHoles(doc.PCB_Holes, types, Hmin, Hmax)
            #
            doc.Board.Holes = doc.PCB_Holes
            doc.recompute()
        except Exception as e:
            self.printInfo(u'{0}'.format(e), 'error')
        else:
            self.printInfo('done')
    
    def Draft2Sketch(self, elem, sketch):
        return (DraftGeomUtils.geom(elem.toShape().Edges[0], sketch.Placement))
    
    def generateConstraintAreas(self, doc, layerNumber, grp, layerName, layerColor, layerTransparent):
        typeL = PCBconf.softLayers[self.databaseType][layerNumber]['ltype']
        mainGroup = doc.addObject("App::DocumentObjectGroup", layerName)
        grp.addObject(mainGroup)
        
        for i in self.wersjaFormatu.getConstraintAreas(layerNumber):
            ser = doc.addObject('Sketcher::SketchObject', "Sketch_{0}".format(layerName))
            ser.ViewObject.Visibility = False
            #
            if i[0] == 'rect':
                try:
                    height = i[5]
                except:
                    height = 0
                
                x1 = i[1]
                y1 = i[2]
                
                x2 = i[3]
                y2 = i[2]
                
                x3 = i[3]
                y3 = i[4]
                
                x4 = i[1]
                y4 = i[4]
                
                try:
                    if i[6] != 0:
                        xs = (i[1] + i[3]) / 2.
                        ys = (i[2] + i[4]) / 2.
                
                        mat = mathFunctions()
                        (x1, y1) = mat.obrocPunkt2([x1, y1], [xs, ys], i[6])
                        (x2, y2) = mat.obrocPunkt2([x2, y2], [xs, ys], i[6])
                        (x3, y3) = mat.obrocPunkt2([x3, y3], [xs, ys], i[6])
                        (x4, y4) = mat.obrocPunkt2([x4, y4], [xs, ys], i[6])
                except:
                    pass
                
                ser.addGeometry(Part.LineSegment(FreeCAD.Vector(x1, y1, 0), FreeCAD.Vector(x2, y2, 0)))
                ser.addGeometry(Part.LineSegment(FreeCAD.Vector(x2, y2, 0), FreeCAD.Vector(x3, y3, 0)))
                ser.addGeometry(Part.LineSegment(FreeCAD.Vector(x3, y3, 0), FreeCAD.Vector(x4, y4, 0)))
                ser.addGeometry(Part.LineSegment(FreeCAD.Vector(x4, y4, 0), FreeCAD.Vector(x1, y1, 0)))
            elif i[0] == 'circle':
                try:
                    height = i[5]
                except:
                    height = 0
                
                if i[4] == 0:
                    ser.addGeometry(Part.Circle(FreeCAD.Vector(i[1], i[2]), FreeCAD.Vector(0, 0, 1), i[3]))
                else:
                    ser.addGeometry(Part.Circle(FreeCAD.Vector(i[1], i[2]), FreeCAD.Vector(0, 0, 1), i[3] + i[4] / 2))
                    ser.addGeometry(Part.Circle(FreeCAD.Vector(i[1], i[2]), FreeCAD.Vector(0, 0, 1), i[3] - i[4] / 2))
            elif i[0] == 'polygon':
                try:
                    height = i[2]
                except:
                    height = 0
                
                for j in i[1]:
                    if j[0] == 'Line':
                        ser.addGeometry(Part.LineSegment(FreeCAD.Vector(j[1], j[2], 0), FreeCAD.Vector(j[3], j[4], 0)))
                    elif j[0] == 'Arc':
                        x1 = j[1]
                        y1 = j[2]
                        x2 = j[3]
                        y2 = j[4]
                        [x3, y3] = self.arcMidPoint([x2, y2], [x1, y1], j[5])
                        
                        arc = Part.Arc(FreeCAD.Vector(x1, y1, 0.0), FreeCAD.Vector(x3, y3, 0.0), FreeCAD.Vector(x2, y2, 0.0))
                        ser.addGeometry(self.Draft2Sketch(arc, ser))
            #
            a = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", layerName + "_{0}".format(0))
            layerObj = constraintAreaObject(a, typeL)
            a.Base = ser
            if height != 0:
                a.Height = height
            viewProviderConstraintAreaObject(a.ViewObject)
            mainGroup.addObject(a)
            FreeCADGui.activeDocument().getObject(a.Name).ShapeColor = layerColor
            FreeCADGui.activeDocument().getObject(a.Name).Transparency = layerTransparent
            FreeCADGui.activeDocument().getObject(a.Name).DisplayMode = 1
            self.updateView()
    
    def generatePolygons(self, data, doc, group, layerName, layerColor, layerNumber):
        for i in data[0]:
            for j in i: # polygons
                layerS = FreeCAD.ActiveDocument.addObject("Part::FeaturePython", "{0}_{1}".format(layerName, layerNumber))
                layerNew = layerPolygonObject(layerS, PCBconf.PCBlayers[PCBconf.softLayers[self.databaseType][layerNumber][1]][3])
                layerNew.points = j[3]
                layerNew.name = j[2]
                layerNew.isolate = j[1]
                layerNew.paths = data[1]
                layerNew.generuj(layerS)
                layerNew.updatePosition_Z(layerS)
                viewProviderLayerPolygonObject(layerS.ViewObject)
                layerS.ViewObject.ShapeColor = layerColor
                group.addObject(layerS)
    
    def generateOctagon(self, x, y, height, width=0):
        if width == 0:
            width = height
        
        w_pP = width / 2.
        w_zP = width / (2 + (sqrt(2)))
        w_aP = width * (sqrt(2) - 1)
        
        h_pP = height / 2.
        h_zP = height / (2 + (sqrt(2)))
        h_aP = height * (sqrt(2) - 1)
        
        return [[x - w_pP + w_zP, y - h_pP, 0, x - w_pP + w_zP + w_aP, y - h_pP, 0],
                [x - w_pP + w_zP + w_aP, y - h_pP, 0, x + w_pP, y -h_pP + h_zP, 0],
                [x + w_pP, y - h_pP + h_zP, 0, x + w_pP, y - h_pP + h_zP + h_aP, 0],
                [x + w_pP, y - h_pP + h_zP + h_aP, 0, x + w_pP - w_zP, y + h_pP, 0],
                [x + w_pP - w_zP, y + h_pP, 0, x + w_pP - w_zP - w_aP, y + h_pP, 0],
                [x + w_pP - w_zP - w_aP, y + h_pP, 0, x - w_pP, y + h_pP - h_zP, 0],
                [x - w_pP, y + h_pP - h_zP, 0, x - w_pP, y + h_pP - h_zP - h_aP, 0],
                [x - w_pP, y + h_pP - h_zP - h_aP, 0, x - w_pP + w_zP, y - h_pP, 0]]

    #def generateOctagon(self, x, y, diameter):
        #pP = diameter / 2.
        #zP = diameter / (2 + (sqrt(2)))
        #aP = diameter * (sqrt(2) - 1)
        
        #return [[x - pP + zP, y - pP, 0, x - pP + zP + aP, y - pP, 0],
                #[x - pP + zP + aP, y - pP, 0, x + pP, y - pP + zP, 0],
                #[x + pP, y - pP + zP, 0, x + pP, y - pP + zP + aP, 0],
                #[x + pP, y - pP + zP + aP, 0, x + pP - zP, y + pP, 0],
                #[x + pP - zP, y + pP, 0, x + pP - zP - aP, y + pP, 0],
                #[x + pP - zP - aP, y + pP, 0, x - pP, y + pP - zP, 0],
                #[x - pP, y + pP - zP, 0, x - pP, y + pP - zP - aP, 0],
                #[x - pP, y + pP - zP - aP, 0, x - pP + zP, y - pP, 0]]
    
    def showHoles(self):
        if not self.wersjaFormatu.dialogMAIN.plytkaPCB_otworyH.isChecked() and not self.wersjaFormatu.dialogMAIN.plytkaPCB_otworyV.isChecked() and not self.wersjaFormatu.dialogMAIN.plytkaPCB_otworyP.isChecked():
            return False
        else:
            return True

    def generateErrorReport(self, PCB_ER, filename):
        ############### ZAPIS DO PLIKU - LISTA BRAKUJACYCH ELEMENTOW
        if PCB_ER and len(PCB_ER):
            if os.path.exists(filename) and os.path.isfile(filename):
                (path, docname) = os.path.splitext(os.path.basename(filename))
                plik = builtins.open(u"{0}.err".format(filename), "w")
                a = []
                a = [i for i in PCB_ER if str(i) not in a and not a.append(str(i))]
                PCB_ER = list(a)
                
                FreeCAD.Console.PrintWarning("**************************\n")
                for i in PCB_ER:
                    line = u"Object not found: {0} {2} [Package: {1}, Library: {3}]\n".format(i[0], i[1], i[2], i[3])
                    plik.writelines(line)
                    FreeCAD.Console.PrintWarning(line)
                FreeCAD.Console.PrintWarning("**************************\n")
                plik.close()
            else:
                FreeCAD.Console.PrintWarning("Access Denied. The Specified Path does not exist, or there could be permission problem.")
        else:
            try:
                os.remove("{0}.err".format(filename))
            except:
                pass
        ##############
        
    def addAnnotations(self, annotations, doc, color):
        for i in annotations:
            annotation = createAnnotation()
            annotation.X = float(i[1])
            annotation.Y = float(i[2])
            annotation.Side = str(i[5])
            annotation.Rot = float(i[4])
            annotation.Text = i[0]
            annotation.Align = str(i[6])
            annotation.Size = float(i[3])
            annotation.Spin = i[7]
            annotation.Mirror = i[8]
            annotation.Color = color
            #annotation.fontName = str(i[9])
            annotation.generate()
            annotation.addToAnnotations()
        
