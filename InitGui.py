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
# parts height
# collisions
# gerber
# paths from image

__title__ = "FreeCAD Printed Circuit Board Workbench - Init file"
__author__ = "marmni <marmni@onet.eu>"
__url__ = ["http://www.freecadweb.org"]


class PCB(Workbench):
    MenuText = "Printed Circuit Board"
    ToolTip = "PCB workbench"
    Icon = """
/* XPM */
static char * D:\Program Files\FreeCAD 0_18_4\Mod\PCB\RC_test\svg\modelKopia_xpm[] = {
"32 32 41 1",
" 	c None",
".	c #FFFFFF",
"+	c #7E7E7E",
"@	c #6E6E6E",
"#	c #EBEBEB",
"$	c #1D1D1D",
"%	c #000000",
"&	c #0F0F0F",
"*	c #0C0C0C",
"=	c #DADADA",
"-	c #7B7B7B",
";	c #FDFDFD",
">	c #FBFBFB",
",	c #6C6C6C",
"'	c #6F6F6F",
")	c #161616",
"!	c #F9F9F9",
"~	c #090909",
"{	c #D8D8D8",
"]	c #B4B4B4",
"^	c #575757",
"/	c #171717",
"(	c #FEFEFE",
"_	c #D7D7D7",
":	c #9D9D9D",
"<	c #808080",
"[	c #121212",
"}	c #101010",
"|	c #D3D3D3",
"1	c #EEEEEE",
"2	c #777777",
"3	c #D9D9D9",
"4	c #BABABA",
"5	c #E3E3E3",
"6	c #A1A1A1",
"7	c #D6D6D6",
"8	c #848484",
"9	c #C4C4C4",
"0	c #ABABAB",
"a	c #F2F2F2",
"b	c #FAFAFA",
"                                ",
"      .....................     ",
"      .+@@@@@@@@@@@@@@@@@#.     ",
"      .$%%&*%%%%%%%%%%%%%=.     ",
"      .$%-;>,%%%%%%%%%%%%=.     ",
"  %%%'.$);..!~%%%%%%%%%%%{]%%%  ",
" %%%%^.$/(..!~%%%%%%%%%%%_:%%%% ",
" %%%%^.$%<(>'%%%%%%%%%%%%_:%%%% ",
" %%%%^.$%%[}%%%%%%%%%%%%%_:%%%% ",
" %%%%^.$%%%%%%%%%%%%%%%%%_:%%%% ",
"     |.$%%%%%%%%%%%%%%%%%=1     ",
"      .$%%%%%%%%%%%%%%%%%=.     ",
"      .$%%%%%%%%%%%%%%%%%=.     ",
"  %%%2.$%%%%%%%%%%%%%%%%%34%%%  ",
" %%%%^.$%%%%%%%%%%%%%%%%%_:%%%% ",
" %%%%^.$%%%%%%%%%%%%%%%%%_:%%%% ",
" %%%%^.$%%%%%%%%%%%%%%%%%_:%%%% ",
" %%%%^.$%%%%%%%%%%%%%%%%%_:%%%% ",
"     4.$%%%%%%%%%%%%%%%%%=5     ",
"      .$%%%%%%%%%%%%%%%%%=.     ",
"      .$%%%%%%%%%%%%%%%%%=.     ",
"     6.$%%%%%%%%%%%%%%%%%=7     ",
" %%%%^.$%%%%%%%%%%%%%%%%%_:%%%% ",
" %%%%^.$%%%%%%%%%%%%%%%%%_:%%%% ",
" %%%%^.$%%%%%%%%%%%%%%%%%_:%%%% ",
" %%%%^.$%%%%%%%%%%%%%%%%%_:%%%% ",
"  %%%8.$%%%%%%%%%%%%%%%%%39%%%  ",
"      .$%%%%%%%%%%%%%%%%%=.     ",
"      .$%%%%%%%%%%%%%%%%%=.     ",
"      .066666666666666666a.     ",
"      >bbbbbbbbbbbbbbbbbbb.     ",
"                                "};

"""

    def Initialize(self):
        import PCBcheckFreeCADVersion
        #result = PCBcheckFreeCADVersion.checkCompatibility()
        #if result[0]:
        PCBcheckFreeCADVersion.setDefaultValues()
        #
        import PCBtoolBar
        import PCBrc
        import PCBcommands
        import SketcherGui
        #
        FreeCADGui.addIconPath(":/data/img")
        FreeCADGui.addPreferencePage(":/data/ui/pcbGeneral.ui", "PCB")
        FreeCADGui.addPreferencePage(":/data/ui/pcbExport.ui", "PCB")
        FreeCADGui.addPreferencePage(":/data/ui/pcbColors.ui", "PCB")
        #
        self.explodeSettings = PCBcommands.listaExplode
        self.parts_E_Settings = PCBcommands.listaPartsE
        self.partsSettings = PCBcommands.listaParts
        #
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
        if hasattr(FreeCADGui, "sketcherToolBar"):
            FreeCADGui.sketcherToolBar.Activated()

    def Deactivated(self):
        if hasattr(FreeCADGui, "pcbToolBar"):
            FreeCADGui.pcbToolBar.Deactivated()
        if hasattr(FreeCADGui, "pcbToolBarView"):
            FreeCADGui.pcbToolBarView.Deactivated()
        if hasattr(FreeCADGui, "sketcherToolBar"):
            FreeCADGui.sketcherToolBar.Deactivated()

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def ContextMenu(self, recipient):
        elem = FreeCADGui.Selection.getSelection()
        if(elem) and len(elem) == 1:
            if hasattr(elem[0], "Proxy") and hasattr(elem[0].Proxy, "Type"):
                if elem[0].Proxy.Type == 'Explode':
                    self.appendContextMenu("Explode", self.explodeSettings)
                elif elem[0].Proxy.Type == 'PCBpart_E':
                    self.appendContextMenu("PCB model", self.parts_E_Settings)
                elif elem[0].Proxy.Type == 'PCBpart' and not elem[0].ViewObject.Proxy.__class__.__name__ == "viewProviderPartObjectExternal":
                    self.appendContextMenu("PCB model", self.partsSettings)

Gui.addWorkbench(PCB())
