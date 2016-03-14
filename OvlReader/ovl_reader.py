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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from qgsvbsovlimporter import QgsVBSOvlImporter
import os.path


class OvlReader(QObject):
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        QObject.__init__(self)
        # Save reference to the QGIS interface
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'OvlReader_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.toolAction = None

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        ovlAction = self.iface.findAction("mActionImportOVL")
        if ovlAction:
            ovlAction.triggered.connect(self.__importOVL)
        else:
            self.toolAction = QAction(QIcon(":/plugins/OvlReader/icon.png"), self.tr("OVL Import"), self.iface.pluginToolBar())
            self.toolAction.setToolTip(self.tr("OVL Import"))
            self.iface.pluginToolBar().addAction(self.toolAction)
            self.toolAction.triggered.connect(self.__importOVL)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        if hasattr(self, 'toolButton'):
            self.iface.pluginToolBar().removeAction(self.toolAction)

    def __importOVL(self):
        lastProjectDir = QSettings().value("/UI/lastProjectDir", ".")
        filename = QFileDialog.getOpenFileName(self.iface.mainWindow(), self.tr("Select OVL File..."), lastProjectDir, self.tr("OVL Files (*.ovl);;"))
        finfo = QFileInfo(filename)
        if not finfo.exists():
            return

        importer = QgsVBSOvlImporter()
        importer.import_ovl(filename, self.iface)
