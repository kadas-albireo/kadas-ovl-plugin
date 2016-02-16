# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OvlReader
                                 A QGIS plugin
 This plugin reads ovl data
                             -------------------
        begin                : 2016-02-16
        copyright            : (C) 2016 by Cédric Christen
        email                : cch@sourcepole.ch
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load OvlReader class from file OvlReader.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .ovl_reader import OvlReader
    return OvlReader(iface)
