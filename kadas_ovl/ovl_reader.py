# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OvlReader
                                 A QGIS plugin
 This plugin reads ovl data
                              -------------------
        begin                : 2016-02-16
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Cédric Christen
        email                : cch@sourcepole.ch
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os

from qgis.PyQt.QtCore import *
from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *

from kadas.kadasgui import *

from . import resources
from .qgsovlimporter import QgsOvlImporter


class OvlReader(QObject):

    def __init__(self, iface):
        QObject.__init__(self)
        # Save reference to the QGIS interface
        self.iface = KadasPluginInterface.cast(iface)
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale', "en")[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'OvlReader_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        self.toolAction = None

    def initGui(self):
        self.ovlAction = QAction(self.tr("Import OVL"))
        self.ovlAction.setIcon(QIcon(":/kadas/plugins/ovl/ovl_import.png"))
        self.ovlAction.triggered.connect(self.__importOVL)
        self.iface.addAction(self.ovlAction, self.iface.NO_MENU, self.iface.MSS_TAB)

        self.ovlShortcut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_M, Qt.CTRL + Qt.Key_O), self.iface.mainWindow())
        self.ovlShortcut.activated.connect(self.__importOVL)


    def unload(self):
        self.iface.removeAction(self.ovlAction, self.iface.NO_MENU, self.iface.MSS_TAB)

    def __importOVL(self):
        lastProjectDir = QSettings().value("/UI/lastProjectDir", ".")
        filename = QFileDialog.getOpenFileName(self.iface.mainWindow(), self.tr("Select OVL File..."), lastProjectDir, self.tr("OVL Files (*.ovl);;"))[0]
        finfo = QFileInfo(filename)
        if finfo.exists():
            QgsOvlImporter().import_ovl(filename, self.iface)
