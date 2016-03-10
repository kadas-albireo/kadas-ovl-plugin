# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OvlReaderDialog
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

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ovl_reader_dialog_base import Ui_OvlReaderDialogBase
from qgsvbsovlimporter import QgsVBSOvlImporter


class OvlReaderDialog(QDialog, Ui_OvlReaderDialogBase):
    def __init__(self, parent=None):
        """Constructor."""
        QDialog.__init__(self, parent)
        self.setupUi(self)
        self.filepathLE.setText("/home/cch/Documents/python/vbs_ovl/test/Lagedarstellung_Reglement.ovl")

    @pyqtSignature("")
    def on_filesearchPB_clicked(self):
        self.filepathLE.setText(QFileDialog.getOpenFileName())

    @pyqtSignature("")
    def on_buttonBox_accepted(self):
        importer = QgsVBSOvlImporter()
        importer.import_ovl(unicode(self.filepathLE.text()), self.iface)
        self.close()
