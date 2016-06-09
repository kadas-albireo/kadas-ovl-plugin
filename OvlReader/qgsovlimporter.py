###########################################################################
#  qgsovlimporter.cpp                                                     #
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
from qgis.milx import *
import zipfile


class QgsOvlImporter(QObject):

    MapPixels, ScreenPixels, Meters = range(1, 4)
    NoDelimiter, OutArrowDelimiter, InArrowDelimiter, MeasureDelimiter, EmptyCircleDelimiter, FilledCircleDelimiter = range(1, 7)

    def __init__(self):
        QObject.__init__(self)

    def import_ovl(self, filename, iface):
        self.iface = iface
        self.milx_layer = QgsMilXLayer(iface)
        if not filename:
            lastDir = QSettings().value("/UI/lastImportExportDir", ".")
            filename = QFileDialog.getOpenFileName(self.iface.mainWindow(), self.tr("Select OVL File"), lastDir, self.tr("OVL Files (*.ovl);;"))
            finfo(filename)
            if not finfo.exists():
                return

                QSettings().setValue("/UI/lastImportExportDir", finfo.absolutePath())

        file_list = []
        try:
            zf = zipfile.ZipFile(filename)
            file_list = zf.namelist()
        except:
            pass
        # geogrid(filename, "geogrid50.xml")
        if 'geogrid50.xml' not in file_list:
            QMessageBox.warning(self.iface.mainWindow(), self.tr("Error"), self.tr("The file does not appear to be a valid OVL v5.0 file:  {fn}").format(fn=QFileInfo(filename).fileName()))
            return

        geogrid = zf.read('geogrid50.xml')
        doc = QDomDocument()
        doc.setContent(geogrid)
        objectList = doc.firstChildElement("geogridOvl").firstChildElement("objectList")
        object = objectList.firstChildElement("object")
        count = 0
        mappingErrors = []
        mssErrors = []

        # First pass: count
        totCount = 0
        while not object.isNull():
            totCount += 1
            object = object.nextSiblingElement("object")

        progdialog = QProgressDialog(self.tr("Importing OVL..."), self.tr("Cancel"), 0, totCount, iface.mainWindow())
        progdialog.setWindowTitle(self.tr("OVL Import"))
        progdialog.show()
        progdialog.rejected.connect(progdialog.cancel)
        progdialog.setCancelButton(None)
        counter = 0
        object = objectList.firstChildElement("object")
        while not object.isNull():
            counter += 1
            progdialog.setValue(counter)
            clsid = object.attribute("clsid")
            uid = object.attribute("uid")
            clsname = object.attribute("clsName")
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
            elif clsid == "{06D46883-9097-4F0A-AE96-95E0BB375DE1}":
                result = self.parseCopexLine(object)
                if result[0]:
                    count += 1
                elif result[1]:
                    mssErrors.append("%s: %s" % (result[1], result[2]))
                else:
                    mappingErrors.append("uid: %s, clsid: %s" % (uid, clsid))
            elif clsid == "{A5EC4300-889F-4511-92B6-B34C26299F5E}":
                result = self.parseCopexSign(object)
                if result[0]:
                    count += 1
                elif result[1]:
                    mssErrors.append("%s: %s" % (result[1], result[2]))
                else:
                    mappingErrors.append("uid: %s, clsName: %s" % (uid, clsname))
            else:
                mappingErrors.append("uid: %s, clsName: %s" % (uid, clsname))

            object = object.nextSiblingElement("object")
        if self.milx_layer.items():
            QgsMapLayerRegistry.instance().addMapLayer(self.milx_layer)
        self.iface.mapCanvas().clearCache(self.iface.redliningLayer().id())
        self.iface.mapCanvas().refresh()
        dialog = QDialog()
        dialog.setWindowTitle(self.tr("Import completed"))
        dialog.setLayout(QVBoxLayout())
        dialog.layout().addWidget(QLabel(self.tr("{cnt} features were imported").format(cnt=count)))
        if mappingErrors:
            dialog.layout().addWidget(QLabel(self.tr("The following objects could not be converted:")))
            edit = QPlainTextEdit("\n".join(mappingErrors))
            edit.setReadOnly(True)
            dialog.layout().addWidget(edit)
        if mssErrors:
            dialog.layout().addWidget(QLabel(self.tr("The following MSS symbols did not pass validation:")))
            edit = QPlainTextEdit("\n".join(mssErrors))
            edit.setReadOnly(True)
            dialog.layout().addWidget(edit)
        dialog.layout().addWidget(QLabel(self.tr("Please note that even for successfully converted objects, the representation may differ compared to the PCMAP Swissline Software. It is therefore recommended to check the imported data.")))
        bbox = QDialogButtonBox(QDialogButtonBox.Close)
        bbox.accepted.connect(dialog.accept)
        bbox.rejected.connect(dialog.reject)
        dialog.layout().addWidget(bbox)
        dialog.exec_()

    def parseGraphic(self, attribute, points, crs="EPSG:4326"):
        coord = attribute.firstChildElement("coordList").firstChildElement("coord")
        transform = None
        if crs != "EPSG:4326":
            transform = QgsCoordinateTransformCache.instance().transform("EPSG:4326", crs)
        while not coord.isNull():
            x = float(coord.attribute("x"))
            y = float(coord.attribute("y"))
            if transform:
                p = transform.transform(x, y)
                points.append(QgsPointV2(p.x(), p.y()))
            else:
                points.append(QgsPointV2(x, y))
            coord = coord.nextSiblingElement("coord")
        return attribute, points

    def parseGraphicTooltip(self, attribute, tooltip):
        enabled = attribute.firstChildElement("enable").text() == "True"
        tooltip = attribute.firstChildElement("text").text() if enabled else ""
        return attribute, tooltip

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
        return attribute, outline, lineSize, lineStyle

    def parseGraphicFillAttributes(self, attribute, fill, fillStyle):
        color = attribute.firstChildElement("color")
        colorAlpha = attribute.firstChildElement("colorAlpha")
        fill = QColor(
            int(color.attribute("red")),
            int(color.attribute("green")),
            int(color.attribute("blue")),
            int(colorAlpha.text()))
        fillStyle = self.convertFillStyle(int(attribute.firstChildElement("fillStyle").text()))
        return attribute, fill, fillStyle

    def parseGraphicDimmAttributes(self, attribute, dimm, factor):
        color = attribute.firstChildElement("color")
        dimm = QColor(
            int(color.attribute("red")),
            int(color.attribute("green")),
            int(color.attribute("blue")))
        factor = float(attribute.firstChildElement("factor").text())
        return attribute, dimm, factor

    def parseGraphicSinglePointAttributes(self, attribute, width, height, rotation):
        height = float(attribute.firstChildElement("height").text())
        width = float(attribute.firstChildElement("width").text())
        rotation = -(float(attribute.firstChildElement("rotation").text()))
        return attribute, width, height, rotation

    def parseGraphicWHUSetable(self, attribute, whu):
        whu = int(attribute.firstChildElement("unit").text())
        return attribute, whu

    def parseGraphicDelimiter(self, attribute, startDelimiter, endDelimiter):
        startDelimiter = int(attribute.firstChildElement("startDelimiter").text())
        endDelimiter = int(attribute.firstChildElement("endDelimiter").text())
        return attribute, startDelimiter, endDelimiter

    def parseGraphicRoundable(self, attribute, roundable):
        roundable = attribute.firstChildElement("roundable").text() == "True"
        return attribute, roundable

    def parseGraphicCloseable(self, attribute, roundable):
        roundable = attribute.firstChildElement("closeable").text() == "True"
        return attribute, roundable

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
        font.setItalic(bool(attribute.firstChildElement("italic").text()))
        font.setBold(bool(attribute.firstChildElement("bold").text()))
        return attribute, text, textColor, font

    def applyDimm(self, factor, dimmColor, outline=0, fill=0):
        if outline:
            outline.setRed(outline.red() * (1. - factor) + dimmColor.red() * factor)
            outline.setGreen(outline.green() * (1. - factor) + dimmColor.green() * factor)
            outline.setBlue(outline.blue() * (1. - factor) + dimmColor.blue() * factor)
        if fill:
            fill.setRed(fill.red() * (1. - factor) + dimmColor.red() * factor)
            fill.setGreen(fill.green() * (1. - factor) + dimmColor.green() * factor)
            fill.setBlue(fill.blue() * (1. - factor) + dimmColor.blue() * factor)
        return factor, dimmColor, outline, fill

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
        whu = 0

        attribute = object.firstChildElement("attributeList").firstChildElement("attribute")
        while not attribute.isNull():
            iidName = attribute.attribute("iidName")
            if iidName == "IID_IGraphic":
                points = []
                self.parseGraphic(attribute, points, "EPSG:3857")
                if points:
                    point = points[0]
            elif iidName == "IID_IGraphicTooltip":
                attribute, tooltip = self.parseGraphicTooltip(attribute, tooltip)
            elif (iidName == "IID_IGraphicLineAttributes"):
                attribute, outline, lineSize, lineStyle = self.parseGraphicLineAttributes(attribute, outline, lineSize, lineStyle)
            elif iidName == "IID_IGraphicFillAttributes":
                attribute, fill, fillStyle = self.parseGraphicFillAttributes(attribute, fill, fillStyle)
            elif iidName == "IID_IGraphicDimmAttributes":
                attribute, dimmColor, dimmFactor = self.parseGraphicDimmAttributes(attribute, dimmColor, dimmFactor)
            elif iidName == "IID_IGraphicSinglePointAttributes":
                attribute, width, height, rotation = self.parseGraphicSinglePointAttributes(attribute, width, height, rotation)
            elif iidName == "IID_IGraphicWHUSetable":
                attribute, whu = self.parseGraphicWHUSetable(attribute, whu)

            attribute = attribute.nextSiblingElement("attribute")

        dimmFactor, dimmColor, outline, fill = self.applyDimm(dimmFactor, dimmColor, outline, fill)

        clsid = object.attribute("clsid")
        if whu == self.Meters:
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
                rotation += 90
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
                rotation += 90
                shape = "triangle"
            elif clsid == "{4B866664-04FF-41A9-B741-15E705BA6DAD}":  # Circle
                shape = "circle"

            flags = "symbol={shp},w={wdth},h={hght},r={rot}".format(shp=shape, wdth=width, hght=height, rot=rotation)
            self.iface.redliningLayer().addShape(QgsGeometry(point.clone()), outline, fill, lineSize, lineStyle, fillStyle, flags, tooltip)

    def parseLine(self, object):
        points = []
        lineSize = 1
        lineStyle = Qt.SolidLine
        outline = QColor()
        dimmColor = QColor()
        startDelimiter = self.NoDelimiter
        endDelimiter = self.NoDelimiter
        tooltip = ""
        dimmFactor = 0.
        roundable = False
        closeable = False

        attribute = object.firstChildElement("attributeList").firstChildElement("attribute")
        while not attribute.isNull():
            iidName = attribute.attribute("iidName")
            if iidName == "IID_IGraphic":
                attribute, points = self.parseGraphic(attribute, points, "EPSG:3857")
            elif iidName == "IID_IGraphicDelimiter":
                attribute, startDelimiter, endDelimiter = self.parseGraphicDelimiter(attribute, startDelimiter, endDelimiter)
            elif iidName == "IID_IGraphicTooltip":
                attribute, tooltip = self.parseGraphicTooltip(attribute, tooltip)
            elif iidName == "IID_IGraphicLineAttributes":
                attribute, outline, lineSize, lineStyle = self.parseGraphicLineAttributes(attribute, outline, lineSize, lineStyle)
            elif iidName == "IID_IGraphicDimmAttributes":
                attribute, dimmColor, dimmFactor = self.parseGraphicDimmAttributes(attribute, dimmColor, dimmFactor)
            elif iidName == "IID_IGraphicRoundable":
                attribute, roundable = self.parseGraphicRoundable(attribute, roundable)
            elif iidName == "IID_IGraphicCloseable":
                attribute, closeable = self.parseGraphicCloseable(attribute, closeable)

            attribute = attribute.nextSiblingElement("attribute")

        dimmFactor, dimmColor, outline, _ = self.applyDimm(dimmFactor, dimmColor, outline)

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
                attribute, points = self.parseGraphic(attribute, points, "EPSG:3857")
            elif iidName == "IID_IGraphicTooltip":
                attribute, tooltip = self.parseGraphicTooltip(attribute, tooltip)
            elif iidName == "IID_IGraphicLineAttributes":
                attribute, outline, lineSize, lineStyle = self.parseGraphicLineAttributes(attribute, outline, lineSize, lineStyle)
            elif iidName == "IID_IGraphicFillAttributes":
                attribute, fill, fillStyle = self.parseGraphicFillAttributes(attribute, fill, fillStyle)
            elif iidName == "IID_IGraphicDimmAttributes":
                attribute, dimmColor, dimmFactor = self.parseGraphicDimmAttributes(attribute, dimmColor, dimmFactor)
            elif iidName == "IID_IGraphicRoundable":
                attribute, roundable = self.parseGraphicRoundable(attribute, roundable)

            attribute = attribute.nextSiblingElement("attribute")

        dimmFactor, dimmColor, outline, fill = self.applyDimm(dimmFactor, dimmColor, outline, fill)

        # TODO: roundable
        poly = QgsPolygonV2()
        ring = QgsLineStringV2()
        ring.setPoints(points)
        ring.addVertex(points[0])
        poly.setExteriorRing(ring)

        self.iface.redliningLayer().addShape(QgsGeometry(poly), outline, fill, lineSize, lineStyle, fillStyle, "", tooltip)

    def parseText(self, object):
        text = ""
        tooltip = ""
        font = QFont()
        color = QColor()
        dimmColor = QColor()
        width = 0.0
        height = 0.0
        rotation = 0.0
        dimmFactor = 0.0
        whu = 0

        attribute = object.firstChildElement("attributeList").firstChildElement("attribute")
        while not attribute.isNull():
            iidName = attribute.attribute("iidName")
            if iidName == "IID_IGraphic":
                points = []
                attribute, points = self.parseGraphic(attribute, points, "EPSG:3857")
                if points:
                    point = points[0]
            elif iidName == "IID_IGraphicTooltip":
                attribute, tooltip = self.parseGraphicTooltip(attribute, tooltip)
# These are in the spec but make little sense
# else if(iidName == "IID_IGraphicLineAttributes")
#   self.parseGraphicLineAttributes(attribute, outline, lineSize, lineStyle);
# else if(iidName == "IID_IGraphicFillAttributes")
#   self.parseGraphicFillAttributes(attribute, fill, fillStyle);
            elif iidName == "IID_IGraphicDimmAttributes":
                attribute, dimmColor, dimmFactor = self.parseGraphicDimmAttributes(attribute, dimmColor, dimmFactor)
            elif iidName == "IID_IGraphicSinglePointAttributes":
                attribute, width, height, rotation = self.parseGraphicSinglePointAttributes(attribute, width, height, rotation)
            elif iidName == "IID_IGraphicWHUSetable":
                attribute, whu = self.parseGraphicWHUSetable(attribute, whu)
            elif iidName == "IID_IGraphicTextAttributes":
                attribute, text, color, font = self.parseGraphicTextAttributes(attribute, text, color, font)

            attribute = attribute.nextSiblingElement("attribute")

        dimmFactor, dimmColor, color, _ = self.applyDimm(dimmFactor, dimmColor, color)

        self.iface.redliningLayer().addText(text, point, color, font, tooltip, -rotation)

    def parseCopexLine(self, object):
        points = []
        lineSize = 1
        lineStyle = Qt.SolidLine
        outline = QColor()
        dimmColor = QColor()
        dimmFactor = 0.
        roundable = False
        closeable = False
        mssxml = ""

        attribute = object.firstChildElement("attributeList").firstChildElement("attribute")
        while not attribute.isNull():
            iidName = attribute.attribute("iidName")
            if iidName == "IID_IGraphic":
                attribute, points = self.parseGraphic(attribute, points)
            elif iidName == "IID_IGraphicLineAttributes":
                attribute, outline, lineSize, lineStyle = self.parseGraphicLineAttributes(attribute, outline, lineSize, lineStyle)
            elif iidName == "IID_IGraphicFillAttributes":
                attribute, fill, fillStyle = self.parseGraphicFillAttributes(attribute, fill, fillStyle)
            elif iidName == "IID_IGraphicDimmAttributes":
                attribute, dimmColor, dimmFactor = self.parseGraphicDimmAttributes(attribute, dimmColor, dimmFactor)
            elif iidName == "IID_IGraphicRoundable":
                attribute, roundable = self.parseGraphicRoundable(attribute, roundable)
            elif iidName == "IID_IGraphicCloseable":
                attribute, closeable = self.parseGraphicCloseable(attribute, closeable)

            attribute = attribute.nextSiblingElement("attribute")

        copexobject = object.firstChildElement("attributeList").firstChildElement("COPExObject")
        if copexobject:
            iidName = copexobject.attribute("iidName")
            if iidName == "IID_ICOPExObject":
                copexobject, mssxml, reversePoints = self.parseCopex(copexobject)

        if reversePoints:
            points.reverse()
        dimmFactor, dimmColor, outline, _ = self.applyDimm(dimmFactor, dimmColor, outline)
        v1points = []
        for p in points:
            v1points.append(QgsPoint(p.x(), p.y()))
        if mssxml and v1points:
            (valid, adjmssxml, messages) = QgsMilXItem.validateMssString(mssxml)
            if not valid:
                return (False, mssxml, messages)
            milx_item = QgsMilXItem()
            milx_item.initialize(adjmssxml, "", v1points, [], QPoint(), QgsMilXItem.NEED_CONTROL_POINTS_AND_INDICES)
            self.milx_layer.addItem(milx_item)
            return (True, "")
        return (False, "")

    def parseCopexSign(self, object):
        points = []
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
        mssxml = ""

        attribute = object.firstChildElement("attributeList").firstChildElement("attribute")
        while not attribute.isNull():
            iidName = attribute.attribute("iidName")
            if iidName == "IID_IGraphic":
                attribute, points = self.parseGraphic(attribute, points)
            elif iidName == "IID_IGraphicTooltip":
                attribute, tooltip = self.parseGraphicTooltip(attribute, tooltip)
            elif (iidName == "IID_IGraphicLineAttributes"):
                attribute, outline, lineSize, lineStyle = self.parseGraphicLineAttributes(attribute, outline, lineSize, lineStyle)
            elif iidName == "IID_IGraphicFillAttributes":
                attribute, fill, fillStyle = self.parseGraphicFillAttributes(attribute, fill, fillStyle)
            elif iidName == "IID_IGraphicDimmAttributes":
                attribute, dimmColor, dimmFactor = self.parseGraphicDimmAttributes(attribute, dimmColor, dimmFactor)
            elif iidName == "IID_IGraphicSinglePointAttributes":
                attribute, width, height, rotation = self.parseGraphicSinglePointAttributes(attribute, width, height, rotation)

            attribute = attribute.nextSiblingElement("attribute")

        copexobject = object.firstChildElement("attributeList").firstChildElement("COPExObject")
        if copexobject:
            iidName = copexobject.attribute("iidName")
            if iidName == "IID_ICOPExObject":
                copexobject, mssxml, reversePoints = self.parseCopex(copexobject)

        if reversePoints:
            points.reverse()
        dimmFactor, dimmColor, outline, fill = self.applyDimm(dimmFactor, dimmColor, outline, fill)
        v1points = []
        for p in points:
            v1points.append(QgsPoint(p.x(), p.y()))
        if mssxml and v1points:
            (valid, adjmssxml, messages) = QgsMilXItem.validateMssString(mssxml)
            if not valid:
                return (False, mssxml, messages)
            milx_item = QgsMilXItem()
            milx_item.initialize(adjmssxml, '', v1points, [], QPoint(), QgsMilXItem.NEED_CONTROL_POINTS_AND_INDICES)
            self.milx_layer.addItem(milx_item)
            return (True, "")
        return (False, "")

    def parseCopex(self, copexobject):
        byte_data_value = copexobject.firstChildElement("ByteArray").attribute("Value")
        clsid = copexobject.attribute("clsid")
        mssxml, reversePoints = OverlayConverter.read_copex(clsid, byte_data_value)
        return copexobject, mssxml, reversePoints

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

    def convertFillStyle(self, fillStyle):
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
