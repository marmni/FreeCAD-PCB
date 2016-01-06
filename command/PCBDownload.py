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
    from PySide import QtGui
    

class dodatkowaIkonka_klucz(QtGui.QLabel):
    def __init__(self, parent=None):
        QtGui.QLabel.__init__(self, parent)
        #
        self.setPixmap(QtGui.QPixmap(':/data/img/user_profile.png'))
        self.setToolTip('Registration is necessary')


class dodatkowaIkonka_lista(QtGui.QLabel):
     def __init__(self, parent=None):
        QtGui.QLabel.__init__(self, parent)
        #
        self.setPixmap(QtGui.QPixmap(':/data/img/arrow-forward.png'))


class odnosnik(QtGui.QLabel):
     def __init__(self, txt, parent=None):
        QtGui.QLabel.__init__(self, txt, parent)
        #
        self.setOpenExternalLinks(True)


class downloadModelW(QtGui.QWidget):
    def __init__(self, searchPhrase=None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        #
        self.form = self
        self.form.setWindowIcon(QtGui.QIcon(":/data/img/downloadModel.png"))
        #
        if searchPhrase:
            self.form.setWindowTitle('Download model for {0}'.format(searchPhrase))
            url_1 = odnosnik("<a href='http://sourceforge.net/projects/eaglepcb2freecad/files/models/'>FreeCAD-PCB</a>")
            url_2 = odnosnik("<a href='http://www.tracepartsonline.net/(S(q4odzm45rnnypc4513kjgy45))/content.aspx?SKeywords={0}'>trace<b>parts</b></a>".format(searchPhrase))
            url_3 = odnosnik("<a href='http://www.3dcontentcentral.com/Search.aspx?arg={0}'>3D ContentCentral</a>".format(searchPhrase))
        else:
            self.form.setWindowTitle('Download model')
            url_1 = odnosnik("<a href='http://sourceforge.net/projects/eaglepcb2freecad/files/models/'>FreeCAD-PCB</a>")
            url_2 = odnosnik("<a href='http://www.tracepartsonline.net/(S(q4odzm45rnnypc4513kjgy45))/content.aspx'>trace<b>parts</b></a>")
            url_3 = odnosnik("<a href='http://www.3dcontentcentral.com/'>3D ContentCentral</a>")
        #
        lay = QtGui.QGridLayout(self)
        lay.addWidget(dodatkowaIkonka_lista(), 0, 0, 1, 1)
        lay.addWidget(url_1, 0, 1, 1, 1)

        
        lay.addWidget(dodatkowaIkonka_lista(), 1, 0, 1, 1)
        lay.addWidget(url_2, 1, 1, 1, 1)
        lay.addWidget(dodatkowaIkonka_klucz(), 1, 2, 1, 1)
        
        lay.addWidget(dodatkowaIkonka_lista(), 2, 0, 1, 1)
        lay.addWidget(url_3, 2, 1, 1, 1)
        lay.addWidget(dodatkowaIkonka_klucz(), 2, 2, 1, 1)
        
        lay.addItem(QtGui.QSpacerItem(5, 20), 3, 0, 1, 3)
        lay.addWidget(QtGui.QLabel('Printed Circuit Board supported formats: IGS, STEP'), 3, 0, 1, 3)
        lay.setColumnStretch(1, 10)
