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
        static char *_0afc0d065b4666bf20085779c40b807[] = {
/* columns rows colors chars-per-pixel */
"53 53 125 2 ",
"   c None",
".  c #0C0C0C",
"X  c #111111",
"o  c gray7",
"O  c #131313",
"+  c #161616",
"@  c gray9",
"#  c #181818",
"$  c #191919",
"%  c gray10",
"&  c #1B1B1B",
"*  c gray11",
"=  c #1D1D1D",
"-  c #1E1E1E",
";  c gray12",
":  c #202020",
">  c gray13",
",  c #222222",
"<  c #232323",
"1  c gray14",
"2  c #252525",
"3  c gray15",
"4  c #272727",
"5  c #282828",
"6  c gray16",
"7  c #2A2A2A",
"8  c gray17",
"9  c #2C2C2C",
"0  c #2D2D2D",
"q  c gray18",
"w  c #2F2F2F",
"e  c gray19",
"r  c #313131",
"t  c #323232",
"y  c gray20",
"u  c #343434",
"i  c #353535",
"p  c gray21",
"a  c #373737",
"s  c gray22",
"d  c #393939",
"f  c #3A3A3A",
"g  c gray23",
"h  c #3C3C3C",
"j  c gray24",
"k  c #3E3E3E",
"l  c #3F3F3F",
"z  c gray25",
"x  c #414141",
"c  c gray26",
"v  c #434343",
"b  c #444444",
"n  c gray27",
"m  c #464646",
"M  c gray28",
"N  c #484848",
"B  c #494949",
"V  c gray29",
"C  c #4B4B4B",
"Z  c #4C4C4C",
"A  c gray30",
"S  c #4E4E4E",
"D  c gray31",
"F  c #505050",
"G  c #515151",
"H  c gray32",
"J  c #535353",
"K  c gray33",
"L  c #555555",
"P  c #565656",
"I  c gray34",
"U  c #585858",
"Y  c gray35",
"T  c #5A5A5A",
"R  c #5B5B5B",
"E  c gray36",
"W  c #5D5D5D",
"Q  c gray37",
"!  c #5F5F5F",
"~  c #606060",
"^  c gray38",
"/  c #626262",
"(  c gray39",
")  c #646464",
"_  c #656565",
"`  c gray40",
"'  c #676767",
"]  c #686868",
"[  c DimGray",
"{  c #6A6A6A",
"}  c gray42",
"|  c #6C6C6C",
" . c #6D6D6D",
".. c gray43",
"X. c #6F6F6F",
"o. c gray44",
"O. c #717171",
"+. c #727272",
"@. c gray45",
"#. c #747474",
"$. c gray46",
"%. c #777777",
"&. c gray47",
"*. c #797979",
"=. c gray48",
"-. c #7B7B7B",
";. c #7C7C7C",
":. c gray49",
">. c #7E7E7E",
",. c gray50",
"<. c #808080",
"1. c gray51",
"2. c gray52",
"3. c gray53",
"4. c #898989",
"5. c gray55",
"6. c #8D8D8D",
"7. c #8E8E8E",
"8. c gray57",
"9. c #929292",
"0. c #939393",
"q. c gray58",
"w. c gray59",
"e. c #989898",
"r. c gray60",
/* pixels */
"                                                                                                          ",
"                                                                                                          ",
"                                                                                                          ",
"                                                                                                          ",
"                                                              : *                                         ",
"                                                          2 A :.%.f #                                     ",
"                                                      3 I ,.<.<.<.<.| q                                   ",
"                                                  6 / <.<.<.<.<.<.<.<.<.R ,                               ",
"                                            & q { <.<.<.<.<.<.<.<.<.<.<.<.>.V &                           ",
"                                        & i O.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.%.f +                       ",
"                                    ; h %.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.| 6                     ",
"                                > b -.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.E :                 ",
"                            2 A >.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.:.V &             ",
"                        2 I ,.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.%.p $         ",
"                    8 ( <.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.[ %       ",
"              & q { <.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.:.G u H @     ",
"          * i O.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.*.C d ` <.<.>     ",
"      = k &.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.@.c x O.<.<.<.<.9     ",
"    * s _ <.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.} j M &.<.<.<.<.<.<.f     ",
"    g ,.L p ` <.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<./ h V -.<.<.<.<.<.<.<.<.Y     ",
"    W <.<.>.G f V M c n K X.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.,.I f U ,.<.<.<.<.<.<.<.<.<.<.#.@   ",
"  & =.<.<.<.<.] S *.<.*.| S s } <.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.<.;.S g / <.<.<.<.<.<.<.<.<.<.<.:.S r +   ",
"  4 <.<.<.<.<.Q / <.<.<.<.<.>.a &.<.<.<.<.<.<.<.<.<.<.<.<.<.<.*.C h } <.<.<.<.<.<.<.<.<.<.<.*.B y s D     ",
"  6 <.<.<.<.<.K } <.<.<.<.<.<.E ! <.<.<.<.<.<.<.<.<.<.<.<.#.M l +.<.<.<.<.<.<.<.<.<.<.<.+.k p e 4.G r     ",
"  ; y ] <.<.<.z y j h k l l K i =.<.<.<.<.<.<.<.<.<.<.[ h N *.<.<.<.<.<.<.<.<.<.<.<. .h d ! ` S o.^ :     ",
"  * _ b p $.<.-.M c %.<.<.,.m 8 R <.<.<.<.<.<.<.<.! f G :.<.<.<.<.<.<.<.<.<.<.<.^ a G #.p ` ` S o.! *     ",
"  O W ` ~ f n :.<.%.b N -.<.A +.Q i ( <.<.<.,.Y f Y ,.<.<.<.<.<.<.<.<.<.<.,.U y ' e.r.r.v ` ` S o.T X     ",
"    b ` ` ` I t Y <.<.X.h G z >.<.,.F g } Z g _ <.<.<.<.<.<.<.<.<.<.<.=.C y F t w.r.r.r.v ` ) q X.U       ",
"    7 ` ` ` ` ` Z y } <.<.' r <.<.<.<.-.q ..<.<.<.<.<.<.<.<.<.<.<.$.x 8 I ` ` h q.r.r.r.c a #   o.U       ",
"    : ` ` ` ` ` ` ) k g &.<.<.<.<.<.<.<.z <.<.<.<.<.<.<.<.<.<...z B 6.c ~ ` ` j 9.r.r.r.d       o.L       ",
"      1 U ` ` ` ` ` ` Q s N >.<.<.<.<.<.z <.<.<.<.<.<.<.<.` d H 0.r.r.T T ` ` k 8.r.r.r.l       o.J       ",
"      6 Y 5 W ` ` ` ` ` ` J t ~ <.<.<.<.z <.<.<.<.<.,.U t c n +.r.r.r.! I ` A ; 7.r.r.r.g       o.F       ",
"      8 r.3 @ e / ` ` ` ` ` ` B y X.<.<.z <.<.<.;.D t Z ` ` G { r.r.r.( f -   = 6.r.r.e.4       o.S       ",
"      8 r.6     % g _ ` ` ` ` ` / j l *.z <.&.N t ;.a ~ ` ` H ] r.r.r.(         ] r.r.H         o.C       ",
"      8 r.5         # m ` ` ` ` ` ` R y 3 h d E l %.) K ` ` K _ r.r.r.{         < H r.6         o.B       ",
"      8 r.4             - H ` ` ` ` ` ` 7 ^ ` ` D ../ P ` Y > ! r.r.r.^           w r.7         o.M       ",
"      8 r.4                 > Y ` ` ` ` y ` ` ` D ..! m 4 O   ^ r.r.r.s           q r.7         o.n       ",
"      , *.-                   + q ~ ` ` u ` ` ` D  .Y .       k r.r.O.>           0 r.7         o.v       ",
"        o                         + y ( i ) ) k O ..R         ; x q.g             8 r.7         o.x       ",
"                                      # & 0 %     ..Y           & 7.h             7 r.7         F 5       ",
"                                                  ..P           = 5.h             6 r.8         +         ",
"                                                  ..K             4.h             4 r.4                   ",
"                                                  ..H             3.h             = `                     ",
"                                                  ..D             2.h               .                     ",
"                                                  ..A             1.h                                     ",
"                                                  ..V             ,.d                                     ",
"                                                  ..N             U 2                                     ",
"                                                  ..m             #                                       ",
"                                                  ..v                                                     ",
"                                                  } h                                                     ",
"                                                  7 :                                                     ",
"                                                                                                          ",
"                                                                                                          "
};
"""

    def Initialize(self):
        import PCBcheckFreeCADVersion
        result = PCBcheckFreeCADVersion.checkCompatibility()
        if result[0]:
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
            if hasattr(elem[0], "Proxy") and hasattr(elem[0].Proxy, "Type"):
                if elem[0].Proxy.Type == 'Explode':
                    self.appendContextMenu("Explode", self.explodeSettings)
                elif elem[0].Proxy.Type == 'PCBpart_E':
                    self.appendContextMenu("PCB model", self.parts_E_Settings)
                elif elem[0].Proxy.Type == 'PCBpart':
                    self.appendContextMenu("PCB model", self.partsSettings)


Gui.addWorkbench(PCB())
