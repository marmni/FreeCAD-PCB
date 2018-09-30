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
# parts height
# collisions
# gerber
# paths from image

__title__="FreeCAD Printed Circuit Board Workbench - Init file"
__author__ = "marmni <marmni@onet.eu>"
__url__ = ["http://www.freecadweb.org"]

# ICONS
# drill-icon.png -> http://www.fatcow.com/free-icons

# Database backup
# Database upload
# http://creativecommons.org/licenses/by/3.0/
# <div>Icon made by <a href="http://www.freepik.com" title="Freepik">Freepik</a> from <a href="http://www.flaticon.com" title="Flaticon">www.flaticon.com</a> is licensed under <a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0">CC BY 3.0</a></div>

class PCB(Workbench):
    MenuText = "Printed Circuit Board"
    ToolTip = "PCB workbench"
    Icon = """
        /* XPM */
        static char * arch_xpm[] = {
        "17 17 45 1",
        " 	c None",
        ".	c #00F000",
        "+	c #00F200",
        "@	c #00E200",
        "#	c #00F100",
        "$	c #00FF00",
        "%	c #00F300",
        "&	c #00FC00",
        "*	c #00F400",
        "=	c #00F700",
        "-	c #00D600",
        ";	c #00CD00",
        ">	c #00D800",
        ",	c #00F800",
        "'	c #00DD00",
        ")	c #00F600",
        "!	c #008F00",
        "~	c #008800",
        "{	c #009800",
        "]	c #009700",
        "^	c #00A600",
        "/	c #007F00",
        "(	c #00E500",
        "_	c #00A700",
        ":	c #00FA00",
        "<	c #008900",
        "[	c #00CA00",
        "}	c #00FD00",
        "|	c #00FB00",
        "1	c #00F900",
        "2	c #009A00",
        "3	c #007A00",
        "4	c #00B200",
        "5	c #00EF00",
        "6	c #00FE00",
        "7	c #00AD00",
        "8	c #007200",
        "9	c #008400",
        "0	c #00C300",
        "a	c #00BE00",
        "b	c #007400",
        "c	c #00DC00",
        "d	c #007000",
        "e	c #008300",
        "f	c #00B600",
        "                 ",
        "                 ",
        "                 ",
        "      .+@        ",
        "     #$$$$%@     ",
        "    %$$$$$$$$&$  ",
        "   *$$=-;>,$$$$$'",
        "  )$$)!~{]^=$$$*/",
        " =$$$(_    %$$:< ",
        "[}$$$|    #1$&2  ",
        " 345$$|61=$$67   ",
        "   890:$$$$$a    ",
        "      b2c$$c     ",
        "        defb     ",
        "                 ",
        "                 ",
        "                 "};"""

    def Initialize(self):
        PCBcheckFreeCADVersion.setDefaultValues()
        
        import PCBtoolBar, PCBrc, PCBcommands
        import SketcherGui
        
        FreeCADGui.addIconPath(":/data/img")
        FreeCADGui.addPreferencePage(":/data/ui/pcbGeneral.ui","PCB")
        FreeCADGui.addPreferencePage(":/data/ui/pcbExport.ui","PCB")
        FreeCADGui.addPreferencePage(":/data/ui/pcbColors.ui","PCB")
        
        self.explodeSettings = PCBcommands.listaExplode
        self.parts_E_Settings = PCBcommands.listaPartsE
        self.partsSettings = PCBcommands.listaParts
        
        self.sketchertools = ["Sketcher_NewSketch", "Sketcher_LeaveSketch", 
                                "Sketcher_ViewSketch", "Sketcher_MapSketch",
                                "Separator", "ScriptCmd_OpenSketcherWorkbench",
                                "Separator", 
                                "Sketcher_CreatePoint", "Sketcher_CreateArc", 
                                "Sketcher_Create3PointArc", "Sketcher_CreateCircle", 
                                "Sketcher_Create3PointCircle", "Sketcher_CreateLine", 
                                "Sketcher_CreatePolyline", "Sketcher_CreateRectangle", 
                                "Sketcher_CreateSlot", "Separator", 
                                "Sketcher_CreateFillet", "Sketcher_Trimming", 
                                "Sketcher_External", "Sketcher_ToggleConstruction"]

        self.appendToolbar("Sketcher", self.sketchertools)
        self.appendMenu("Sketcher", self.sketchertools)
        
    def Activated(self):
        if hasattr(FreeCADGui, "pcbToolBar"):
            FreeCADGui.pcbToolBar.Activated()
        if hasattr(FreeCADGui, "pcbToolBarView"):
            FreeCADGui.pcbToolBarView.Activated()
        if hasattr(FreeCADGui,"sketcherToolBar"):
            FreeCADGui.sketcherToolBar.Activated()
        
    def Deactivated(self):
        if hasattr(FreeCADGui, "pcbToolBar"):
            FreeCADGui.pcbToolBar.Deactivated()
        if hasattr(FreeCADGui, "pcbToolBarView"):
            FreeCADGui.pcbToolBarView.Deactivated()
        if hasattr(FreeCADGui,"sketcherToolBar"):
            FreeCADGui.sketcherToolBar.Deactivated()
    
    def GetClassName(self):
        return "Gui::PythonWorkbench"
        
    def ContextMenu(self, recipient):
        elem = FreeCADGui.Selection.getSelection()
        if(elem) and len(elem) == 1:
            if hasattr(elem[0], "Proxy") and hasattr(elem[0], "Type"):
                if elem[0].Proxy.Type == 'Explode':
                    self.appendContextMenu("Explode", self.explodeSettings)
                elif elem[0].Proxy.Type == 'PCBpart_E':
                    self.appendContextMenu("PCB model", self.parts_E_Settings)
                elif elem[0].Proxy.Type == 'PCBpart':
                    self.appendContextMenu("PCB model", self.partsSettings)


Gui.addWorkbench(PCB())
import PCBcheckFreeCADVersion
result = PCBcheckFreeCADVersion.checkCompatibility()
if result[0]:
    FreeCAD.addImportType("PCB file formats (*.brd *.pcb *.fpc *.rzp *.fcd *.kicad_pcb *.idf *.emn *.bdf *.idb *.HYP)", "PCBbrd")
else:
    FreeCAD.Console.PrintWarning("PCB Workbench: {0}\n".format(result[1]))
    
