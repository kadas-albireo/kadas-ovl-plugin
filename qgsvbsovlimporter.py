###########################################################################
#  qgsvbsovlimporter.cpp                                                  #
#  -------------------                                                    #
#  begin                : Oct 07, 2015                                    #
#  copyright            : (C) 2015 by Sandro Mani / Sourcepole AG         #
#  email                : smani@sourcepole.ch                             #
###########################################################################

###########################################################################
#                                                                         #
#   This program is free software; you can redistribute it and/or modify  #
#   it under the terms of the GNU General Public License as published by  #
#   the Free Software Foundation; either version 2 of the License, or     #
#   (at your option) any later version.                                   #
#                                                                         #
###########################################################################

from copexreader import OverlayConverter

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.gui import *
from qgis.core import *
from PyQt4.QtXml import *
import zipfile


class QgsVBSOvlImporter(QObject):

    MapPixels, ScreenPixels, Meters = range(1, 4)
    NoDelimiter, OutArrowDelimiter, InArrowDelimiter, MeasureDelimiter, EmptyCircleDelimiter, FilledCircleDelimiter = range(1, 7)

    def __init__(self):
        QObject.__init__(self)

    def import_ovl(self, filename, iface):
        self.iface = iface
        if not filename:
            lastProjectDir = QSettings().value("/UI/lastProjectDir", ".")
            filename = QFileDialog.getOpenFileName(self.iface.mainWindow(), self.tr("Select OVL File"), lastProjectDir, self.tr("OVL Files (*.ovl);;"))
            finfo(filename)
            if not finfo.exists():
                return

                QSettings().setValue("/UI/lastProjectDir", finfo.absolutePath())

        # TODO: quazip gibt es in Python nicht, umweg muss gesucht werden
        zf = zipfile.ZipFile(filename)
        file_list = zf.namelist()
        # geogrid(filename, "geogrid50.xml")
        if 'geogrid50.xml' not in file_list:
            MessageBox.warning(self.iface.mainWindow(), self.tr("Error"), self.tr("Cannot open file for reading: %1").arg(QFileInfo(filename).fileName()))
            return

        geogrid = zf.read('geogrid50.xml')
        doc = QDomDocument()
        doc.setContent(geogrid)
        objectList = doc.firstChildElement("geogridOvl").firstChildElement("objectList")
        object = objectList.firstChildElement("object")
        count = 0
        while not object.isNull():
            clsid = object.attribute("clsid")
            if clsid == "{352CC905-847C-403A-8EE1-C991C86CCE58}":  # Overlay
                pass  # TODO ??
            elif clsid == "{F848EC6F-7105-4C54-9CC1-520E6D38549A}":  # Group
                pass  # TODO ??
            elif clsid == "{E2CCBD8B-E6DC-4B30-894F-D082A434922B}":  # Rectangle
                self.parseRectangleTriangleCircle(object)
                count += 1
            elif clsid == "{FD1F97C1-54FF-4FB2-A7DC-7B27C4ED0BE2}":  # Triangle
                self.parseRectangleTriangleCircle(object)
                count += 1
            elif clsid == "{4B866664-04FF-41A9-B741-15E705BA6DAD}":  # Circle
                self.parseRectangleTriangleCircle(object)
                count += 1
            elif clsid == "{48A64475-69D0-41DC-AF3C-A910B2C0603F}":  # Line
                self.parseLine(object)
                count += 1
            elif clsid == "{1130C93F-EE80-4F0A-A42E-5234CCA0364F}":  # Text
                self.parseText(object)
                count += 1
            elif clsid == "{A56DD602-D748-4231-A9CB-439F3390257F}":  # Bitmap
                pass
            elif clsid == "{E821201B-F7F4-4FA9-80C9-AAD95C285849}":  # Polygon
                self.parsePolygon(object)
                count += 1
            elif clsid == "{6074C216-B8DF-4207-883F-862EFE9346BC}":  # GeoBitmap
                pass
            elif clsid == "{E8032F4A-A3B2-446A-B71F-6B3D43DDF5E5}":
                self.parseCopex(object, clsid)
            elif clsid == "{AE42E103-74BD-44E2-A15A-BD4F40362167}":
                self.parseCopex(object, clsid)
            elif clsid == "{C1FD308D-CE83-4294-855C-2613F97CC7B4}":
                self.parseCopex(object, clsid)
            elif clsid == "{D2B5BBF4-E847-4726-B60A-F3DCB1500F5B}":
                self.parseCopex(object, clsid)
            elif clsid == "{C9184146-7335-4D0B-B7F8-8E6294267E4D}":
                self.parseCopex(object, clsid)
            else:
                QgsDebugMsg("Unhandled clsid %1".arg(clsid))

            object = object.nextSiblingElement("object")
        self.iface.mapCanvas().clearCache(self.iface.redliningLayer().id())
        self.iface.mapCanvas().refresh()
        QMessageBox.information(self.iface.mainWindow(), self.tr("OVL Import"), self.tr("%1 features were imported.").arg(count))

    def parseGraphic(self, attribute, points):
        coord = attribute.firstChildElement("coordList").firstChildElement("coord")
        while not coord.isNull():
            x = float(coord.attribute("x"))
            y = float(coord.attribute("y"))
            points.append(QgsPointV2(x, y))
            coord = coord.nextSiblingElement("coord")

    def parseGraphicTooltip(self, attribute, tooltip):
        enabled = attribute.firstChildElement("enable").text() == "True"
        tooltip = attribute.firstChildElement("text").text() if enabled else ""

    def parseGraphicLineAttributes(self, attribute, outline, lineSize, lineStyle):
        color = attribute.firstChildElement("color")
        colorAlpha = attribute.firstChildElement("colorAlpha")
        outline = QColor(
            int(color.attribute("red")),
            int(color.attribute("green")),
            int(color.attribute("blue")),
            int(colorAlpha.text()))
        lineSize = int(attribute.firstChildElement("size").text())
        lineStyle = self.ConvertLineStyle(int(attribute.firstChildElement("lineStyle").text()))

    def parseGraphicFillAttributes(self, attribute, fill, fillStyle):
        color = attribute.firstChildElement("color")
        colorAlpha = attribute.firstChildElement("colorAlpha")
        fill = QColor(
            int(color.attribute("red")),
            int(color.attribute("green")),
            int(color.attribute("blue")),
            int(colorAlpha.text()))
        fillStyle = self.convertFillStyle(int(attribute.firstChildElement("fillStyle").text()))

    def parseGraphicDimmAttributes(self, attribute, dimm, factor):
        color = attribute.firstChildElement("color")
        dimm = QColor(
            int(color.attribute("red")),
            int(color.attribute("green")),
            int(color.attribute("blue")))
        factor = float(attribute.firstChildElement("factor").text())

    def parseGraphicSinglePointAttributes(self, attribute, width, height, rotation):
        height = float(attribute.firstChildElement("height").text())
        width = float(attribute.firstChildElement("width").text())
        rotation = float(attribute.firstChildElement("rotation").text())

    def parseGraphicWHUSetable(self, attribute, whu):
        whu = int(attribute.firstChildElement("unit").text())

    def parseGraphicDelimiter(self, attribute, startDelimiter, endDelimiter):
        startDelimiter = int(attribute.firstChildElement("startDelimiter").text())
        endDelimiter = int(attribute.firstChildElement("endDelimiter").text())

    def parseGraphicRoundable(self, attribute, roundable):
        roundable = attribute.firstChildElement("roundable").text() == "True"

    def parseGraphicCloseable(self, attribute, roundable):
        roundable = attribute.firstChildElement("closeable").text() == "True"

    def parseGraphicTextAttributes(self, attribute, text, textColor, font):
        color = attribute.firstChildElement("color")
        colorAlpha = attribute.firstChildElement("colorAlpha")
        textColor = QColor(
            int(color.attribute("red")),
            int(color.attribute("green")),
            int(color.attribute("blue")),
            int(colorAlpha.text()))
        text = attribute.firstChildElement("text").text()
        font.setFamily(attribute.firstChildElement("fontFamily").text())
        font.setItalic(int(attribute.firstChildElement("italic").text()))
        font.setBold(int(attribute.firstChildElement("bold").text()))

    def applyDimm(self, factor, dimmColor, outline=0, fill=0):
        if outline:
            outline.setRed(outline.red() * (1. - factor) + dimmColor.red() * factor)
            outline.setGreen(outline.green() * (1. - factor) + dimmColor.green() * factor)
            outline.setBlue(outline.blue() * (1. - factor) + dimmColor.blue() * factor)
        if fill:
            fill.setRed(fill.red() * (1. - factor) + dimmColor.red() * factor)
            fill.setGreen(fill.green() * (1. - factor) + dimmColor.green() * factor)
            fill.setBlue(fill.blue() * (1. - factor) + dimmColor.blue() * factor)

    def parseRectangleTriangleCircle(self, object):
        point = QgsPointV2()
        width = 0.0
        height = 0.0
        rotation = 0.0
        dimmFactor = 0.0
        lineSize = 1
        lineStyle = Qt.SolidLine
        fillStyle = Qt.SolidPattern
        outline = QColor()
        fill = QColor()
        dimmColor = QColor()
        tooltip = ""

        attribute = object.firstChildElement("attributeList").firstChildElement("attribute")
        while not attribute.isNull():
            iidName = attribute.attribute("iidName")
            if iidName == "IID_IGraphic":
                points = []
                self.parseGraphic(attribute, points)
                if not points.isEmpty():
                    point = points.first()
                elif iidName == "IID_IGraphicTooltip":
                    self.parseGraphicTooltip(attribute, tooltip)
                elif (iidName == "IID_IGraphicLineAttributes"):
                    self.parseGraphicLineAttributes(attribute, outline, lineSize, lineStyle)
                elif iidName == "IID_IGraphicFillAttributes":
                    self.parseGraphicFillAttributes(attribute, fill, fillStyle)
                elif iidName == "IID_IGraphicDimmAttributes":
                    self.parseGraphicDimmAttributes(attribute, dimmColor, dimmFactor)
                elif iidName == "IID_IGraphicSinglePointAttributes":
                    self.parseGraphicSinglePointAttributes(attribute, width, height, rotation)
                elif iidName == "IID_IGraphicWHUSetable":
                    self.parseGraphicWHUSetable(attribute, whu)

                attribute = attribute.nextSiblingElement("attribute")

            self.applyDimm(dimmFactor, dimmColor, outline, fill)

            clsid = object.attribute("clsid")
            if whu == Meters:
                da = QgsDistanceArea()
                da.convertMeasurement(width, QGis.Meters, QGis.Degrees, False)
                da.convertMeasurement(height, QGis.Meters, QGis.Degrees, False)
                if clsid == "{E2CCBD8B-E6DC-4B30-894F-D082A434922B}":  # Rectangle
                    ring = QgsLineStringV2()
                    ring.setPoints([
                        QgsPointV2(point.x() - .5 * width, point.y() - .5 * height),
                        QgsPointV2(point.x() + .5 * width, point.y() - .5 * height),
                        QgsPointV2(point.x() + .5 * width, point.y() + .5 * height),
                        QgsPointV2(point.x() - .5 * width, point.y() + .5 * height),
                        QgsPointV2(point.x() - .5 * width, point.y() - .5 * height)])
                elif clsid == "{FD1F97C1-54FF-4FB2-A7DC-7B27C4ED0BE2}":  # Triangle
                    ring = QgsLineStringV2()
                    ring.setPoints([
                        QgsPointV2(point.x() - .5 * width, point.y() - .5 * height),
                        QgsPointV2(point.x() + .5 * width, point.y() - .5 * height),
                        QgsPointV2(point.x() + .5 * width, point.y() + .5 * height),
                        QgsPointV2(point.x() - .5 * width, point.y() + .5 * height),
                        QgsPointV2(point.x() - .5 * width, point.y() - .5 * height)])
                elif clsid == "{4B866664-04FF-41A9-B741-15E705BA6DAD}":  # Circle
                    ring = QgsCircularStringV2
                    ring.setPoints([
                        QgsPointV2(point.x() + .5 * width, point.y()),
                        QgsPointV2(point.x(), point.y()),
                        QgsPointV2(point.x() + .5 * width, point.y())])
                poly = QgsCurvePolygonV2()
                poly.setExteriorRing(ring)
                self.iface.redliningLayer().addShape(QgsGeometry(poly), outline, fill, lineSize, lineStyle, fillStyle, "", tooltip)
            else:
                width = (width * 25.4) / self.iface.mapCanvas().mapSettings().outputDpi()
                height = (height * 25.4) / self.iface.mapCanvas().mapSettings().outputDpi()
                shape = ""
                if clsid == "{E2CCBD8B-E6DC-4B30-894F-D082A434922B}":  # Rectangle
                    shape = "rectangle"
                elif clsid == "{FD1F97C1-54FF-4FB2-A7DC-7B27C4ED0BE2}":  # Triangle
                    shape = "triangle"
                elif clsid == "{4B866664-04FF-41A9-B741-15E705BA6DAD}":  # Circle
                    shape = "circle"

                flags = "symbol=%1,w=%2,h=%3,r=%4".arg(shape).arg(width).arg(height).arg(rotation)
                self.iface.redliningLayer().addShape(QgsGeometry(point.clone()), outline, fill, lineSize, lineStyle, fillStyle, flags, tooltip)

    def parseLine(self, object):
        points = []
        lineSize = 1
        lineStyle = Qt.SolidLine
        outline = QColor()
        dimmColor = QColor()
        startDelimiter = QgsVBSOvlImporter.NoDelimiter
        endDelimiter = QgsVBSOvlImporter.NoDelimiter
        tooltip = ""
        dimmFactor = 0.
        roundable = False
        closeable = False

        attribute = object.firstChildElement("attributeList").firstChildElement("attribute")
        while not attribute.isNull():
            iidName = attribute.attribute("iidName")
            if iidName == "IID_IGraphic":
                self.parseGraphic(attribute, points)
            elif iidName == "IID_IGraphicDelimiter":
                self.parseGraphicDelimiter(attribute, startDelimiter, endDelimiter)
            elif iidName == "IID_IGraphicTooltip":
                self.parseGraphicTooltip(attribute, tooltip)
            elif iidName == "IID_IGraphicLineAttributes":
                self.parseGraphicLineAttributes(attribute, outline, lineSize, lineStyle)
            elif iidName == "IID_IGraphicDimmAttributes":
                self.parseGraphicDimmAttributes(attribute, dimmColor, dimmFactor)
            elif iidName == "IID_IGraphicRoundable":
                self.parseGraphicRoundable(attribute, roundable)
            elif iidName == "IID_IGraphicCloseable":
                self.parseGraphicCloseable(attribute, closeable)

            attribute = attribute.nextSiblingElement("attribute")

        self.applyDimm(dimmFactor, dimmColor, outline)

        line = QgsLineStringV2()
        line.setPoints(points)
        if closeable:
            line.addVertex(points.front())

        # TODO: roundable, startDelimiter, endDelimiter
        self.iface.redliningLayer().addShape(QgsGeometry(line), outline, Qt.black, lineSize, lineStyle, Qt.SolidPattern, "", tooltip)

    def parsePolygon(self, object):
        points = []
        lineSize = 1
        lineStyle = Qt.SolidLine
        fillStyle = Qt.SolidPattern
        outline = QColor()
        fill = QColor()
        dimmColor = QColor()
        tooltip = ""
        dimmFactor = 0.0
        roundable = False

        attribute = object.firstChildElement("attributeList").firstChildElement("attribute")
        while not attribute.isNull():
            iidName = attribute.attribute("iidName")
            if iidName == "IID_IGraphic":
                self.parseGraphic(attribute, points)
            elif iidName == "IID_IGraphicTooltip":
                self.parseGraphicTooltip(attribute, tooltip)
            elif iidName == "IID_IGraphicLineAttributes":
                self.parseGraphicLineAttributes(attribute, outline, lineSize, lineStyle)
            elif iidName == "IID_IGraphicFillAttributes":
                self.parseGraphicFillAttributes(attribute, fill, fillStyle)
            elif iidName == "IID_IGraphicDimmAttributes":
                self.parseGraphicDimmAttributes(attribute, dimmColor, dimmFactor)
            elif iidName == "IID_IGraphicRoundable":
                self.parseGraphicRoundable(attribute, roundable)

            attribute = attribute.nextSiblingElement("attribute")

        self.applyDimm(dimmFactor, dimmColor, outline, fill)

        # TODO: roundable
        poly = QgsPolygonV2()
        ring = QgsLineStringV2()
        ring.setPoints(points)
        ring.addVertex(points.first())
        poly.setExteriorRing(ring)

        self.iface.redliningLayer().addShape(QgsGeometry(poly), outline, fill, lineSize, lineStyle, fillStyle, "", tooltip)

    def parseText(self, object):
        text, tooltip = ""
        font = QFont()
        color = QColor()
        dimmColor = QColor()
        width = 0.0
        height = 0.0
        rotation = 0.0
        dimmFactor = 0.0

        attribute = object.firstChildElement("attributeList").firstChildElement("attribute")
        while not attribute.isNull():
            iidName = attribute.attribute("iidName")
            if iidName == "IID_IGraphic":
                points = []
                self.parseGraphic(attribute, points)
                if not points.isEmpty():
                    point = points.first()
                elif iidName == "IID_IGraphicTooltip":
                    self.parseGraphicTooltip(attribute, tooltip)
    # These are in the spec but make little sense
    # else if(iidName == "IID_IGraphicLineAttributes")
    #   self.parseGraphicLineAttributes(attribute, outline, lineSize, lineStyle);
    # else if(iidName == "IID_IGraphicFillAttributes")
    #   self.parseGraphicFillAttributes(attribute, fill, fillStyle);
                elif iidName == "IID_IGraphicDimmAttributes":
                    self.parseGraphicDimmAttributes(attribute, dimmColor, dimmFactor)
                elif iidName == "IID_IGraphicSinglePointAttributes":
                    self.parseGraphicSinglePointAttributes(attribute, width, height, rotation)
                elif iidName == "IID_IGraphicWHUSetable":
                    self.parseGraphicWHUSetable(attribute, whu)
                elif iidName == "IID_IGraphicTextAttributes":
                    self.parseGraphicTextAttributes(attribute, text, color, font)

                attribute = attribute.nextSiblingElement("attribute")

            self.applyDimm(dimmFactor, dimmColor, color)

            self.iface.redliningLayer().addText(text, point, color, font, tooltip, rotation)

    def parseCopex(self, object, clsid):
        byte_data_value = object.attribute("ByteArray")
        OverlayConverter.read_copex(clsid, byte_data_value)

    def ConvertLineStyle(self, lineStyle):
        if lineStyle == 0:
            return Qt.NoPen
        elif lineStyle == 1:
            return Qt.SolidLine
        elif lineStyle == 2:
            return Qt.DashLine
        elif lineStyle == 3:
            return Qt.DashDotLine
        elif lineStyle == 4:
            return Qt.DotLine
        else:
            return Qt.SolidLine

    def convertFillStyle(fillStyle):
        if fillStyle == 0:
            return Qt.NoBrush
        elif fillStyle == 1:
            return Qt.SolidPattern
        elif fillStyle == 2:
            return Qt.HorPattern
        elif fillStyle == 3:
            return Qt.VerPattern
        elif fillStyle == 4:
            return Qt.BDiagPattern
        elif fillStyle == 5:
            return Qt.DiagCrossPattern
        elif fillStyle == 6:
            return Qt.FDiagPattern
        elif fillStyle == 7:
            return Qt.CrossPattern
        else:
            return Qt.SolidPattern
