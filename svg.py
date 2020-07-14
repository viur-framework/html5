# -*- coding: utf-8 -*-
from math import pi, cos, sin, tan
from . import core as html5

####################################################################
# math utilities
####################################################################


# constructors for matrices:
def nullTransform():
	return 1, 0, 0, 1, 0, 0


def translate(dx, dy):
	return 1, 0, 0, 1, dx, dy


def scale(sx, sy):
	return sx, 0, 0, sy, 0, 0


def rotate(angle):
	a = angle * pi / 180
	return cos(a), sin(a), -sin(a), cos(a), 0, 0


def skewX(angle):
	a = angle * pi / 180
	return 1, 0, tan(a), 1, 0, 0


def skewY(angle):
	a = angle * pi / 180
	return 1, tan(a), 0, 1, 0, 0


def mmult(A, B):
	"A postmultiplied by B"
	# I checked this RGB
	# [a0 a2 a4]    [b0 b2 b4]
	# [a1 a3 a5] *  [b1 b3 b5]
	# [      1 ]    [      1 ]
	#
	return (
		A[0] * B[0] + A[2] * B[1],
		A[1] * B[0] + A[3] * B[1],
		A[0] * B[2] + A[2] * B[3],
		A[1] * B[2] + A[3] * B[3],
		A[0] * B[4] + A[2] * B[5] + A[4],
		A[1] * B[4] + A[3] * B[5] + A[5]
	)


def inverse(A):
	"For A affine 2D represented as 6vec return 6vec version of A**(-1)"
	# I checked this RGB
	det = float(A[0] * A[3] - A[2] * A[1])
	R = [A[3] / det, -A[1] / det, -A[2] / det, A[0] / det]
	return tuple(R + [-R[0] * A[4] - R[2] * A[5], -R[1] * A[4] - R[3] * A[5]])


def zTransformPoint(A, v):
	"Apply the homogenous part of atransformation a to vector v --> A*v"
	return A[0] * v[0] + A[2] * v[1], A[1] * v[0] + A[3] * v[1]


def transformPoint(A, v):
	"Apply transformation a to vector v --> A*v"
	return A[0] * v[0] + A[2] * v[1] + A[4], A[1] * v[0] + A[3] * v[1] + A[5]


def transformPoints(matrix, V):
	r = [transformPoint(matrix, v) for v in V]
	if isinstance(V, tuple): r = tuple(r)
	return r


def zTransformPoints(matrix, V):
	return list(map(lambda x, matrix=matrix: zTransformPoint(matrix, x), V))


########################################################################################################################
# Attribute Collectors
########################################################################################################################

class _attrSvgViewBox(object):

	def _getViewbox(self):
		viewBox = self.element.viewBox
		try:
			return " ".join(
				[str(x) for x in [viewBox.baseVal.x, viewBox.baseVal.y, viewBox.baseVal.width, viewBox.baseVal.height]])
		except:
			return ""

	def _setViewbox(self, val):
		self.element.setAttribute("viewBox", val)

	def _getPreserveaspectratio(self):
		return self.element.preserveAspectRatio

	def _setPreserveaspectratio(self, val):
		self.element.setAttribute("preserveAspectRatio", val)


class _attrSvgDimensions(object):

	def _getWidth(self):
		return self.element.width

	def _setWidth(self, val):
		self.element.setAttribute("width", val)

	def _getHeight(self):
		return self.element.height

	def _setHeight(self, val):
		self.element.setAttribute("height", val)

	def _getX(self):
		return self.element.x

	def _setX(self, val):
		self.element.setAttribute("x", val)

	def _getY(self):
		return self.element.y

	def _setY(self, val):
		self.element.setAttribute("y", val)

	def _getR(self):
		return self.element.r

	def _setR(self, val):
		self.element.setAttribute("r", val)

	def _getRx(self):
		return self.element.rx

	def _setRx(self, val):
		self.element.setAttribute("rx", val)

	def _getRy(self):
		return self.element.ry

	def _setRy(self, val):
		self.element.setAttribute("ry", val)

	def _getCx(self):
		return self.element.cx

	def _setCx(self, val):
		self.element.setAttribute("cx", val)

	def _getCy(self):
		return self.element.cy

	def _setCy(self, val):
		self.element.setAttribute("cy", val)


class _attrSvgPoints(object):

	def _getPoints(self):
		return self.element.points

	def _setPoints(self, val):
		self.element.setAttribute("points", val)

	def _getX1(self):
		return self.element.x1

	def _setX1(self, val):
		self.element.setAttribute("x1", val)

	def _getY1(self):
		return self.element.y1

	def _setY1(self, val):
		self.element.setAttribute("y1", val)

	def _getX2(self):
		return self.element.x2

	def _setX2(self, val):
		self.element.setAttribute("x2", val)

	def _getY2(self):
		return self.element.y2

	def _setY2(self, val):
		self.element.setAttribute("y2", val)


class _attrSvgTransform(object):

	def _getTransform(self):
		return self.element.transform

	def _setTransform(self, val):
		self.element.setAttribute("transform", val)


class _attrSvgXlink(object):

	def _getXlinkhref(self):
		return self.element.getAttribute("xlink:href")

	def _setXlinkhref(self, val):
		self.element.setAttribute("xlink:href", val)


class _attrSvgStyles(object):

	def __init__(self, *args, **kwargs):
		print("_attrSvgStyles:__init__: kwargs = {}".format(kwargs))
		if 'fill' in kwargs:
			self._setFill(kwargs.pop('fill'))
		if 'fillopacity' in kwargs:
			self._setFillopacity(kwargs.pop('fillopacity'))
		if 'stroke' in kwargs:
			self._setStroke(kwargs.pop('stroke'))
		if 'strokeopacity' in kwargs:
			self._setStrokeopacity(kwargs.pop('strokeopacity'))
		if 'strokewidth' in kwargs:
			print("_attrSvgStyles:__init__: strokewidth")
			self._setStrokewidth(kwargs.pop('strokewidth'))
		if 'strokelinejoin' in kwargs:
			self._setStrokelinejoin(kwargs.pop('strokelinejoin'))
		if 'strokelinecap' in kwargs:
			self._setStrokelinecap(kwargs.pop('strokelinecap'))
		if 'strokedasharray' in kwargs:
			self._setStrokedasharray(kwargs.pop('strokedasharray'))
		super().__init__(*args, **kwargs)

	def _getFill(self):
		return self.element.fill

	def _setFill(self, val):
		'''Set the fill color'''
		self.element.setAttribute("fill", val)

	def _getFillopacity(self):
		return self.element.getAttribute("fill-opacity")

	def _setFillopacity(self, val):
		self.element.setAttribute("fill-opacity", val)

	def _getStroke(self):
		return self.element.stroke

	def _setStroke(self, val):
		'''Set the stroke color'''
		self.element.setAttribute("stroke", val)

	def _getStrokeopacity(self):
		return self.element.getAttribute("stroke-opacity")

	def _setStrokeopacity(self, val):
		self.element.setAttribute("stroke-opacity", val)

	def _getStrokewidth(self):
		return self.element.getAttribute("stroke-width")

	def _setStrokewidth(self, val):
		self.element.setAttribute("stroke-width", val)

	def _getStrokelinecap(self):
		return self.element.getAttribute("stroke-linecap")

	def _setStrokelinecap(self, val):
		self.element.setAttribute("stroke-linecap", val)

	def _getStrokelinejoin(self):
		return self.element.getAttribute("stroke-linejoin")

	def _setStrokelinejoin(self, val):
		self.element.setAttribute("stroke-linejoin", val)

	def _getStrokedasharray(self):
		return self.element.getAttribute("stroke-dasharray")

	def _setStrokedasharray(self, val):
		self.element.setAttribute("stroke-dasharray", val)



########################################################################################################################
# SVG Widgets
########################################################################################################################

@html5.tag
class SvgWidget(html5.Widget):
	_namespace = "SVG"


@html5.tag
class Svg(SvgWidget, _attrSvgViewBox, _attrSvgDimensions, _attrSvgTransform):
	_tagName = "svg"

	def _getVersion(self):
		return self.element.version

	def _setVersion(self, val):
		self.element.setAttribute("version", val)

	def _getXmlns(self):
		return self.element.xmlns

	def _setXmlns(self, val):
		self.element.setAttribute("xmlns", val)


@html5.tag
class SvgCircle(SvgWidget, _attrSvgTransform, _attrSvgDimensions, _attrSvgStyles):
	_tagName = "circle"

	def __init__(self, *args, **kwargs):
		SvgWidget.__init__(self, *args, **kwargs)
		_attrSvgStyles.__init__(self, *args, **kwargs)


@html5.tag
class SvgEllipse(SvgWidget, _attrSvgTransform, _attrSvgDimensions, _attrSvgStyles):
	_tagName = "ellipse"

	def __init__(self, *args, **kwargs):
		SvgWidget.__init__(self, *args, **kwargs)
		_attrSvgStyles.__init__(self, *args, **kwargs)


@html5.tag
class SvgG(SvgWidget, _attrSvgTransform, _attrSvgStyles):
	_tagName = "g"

	def __init__(self, *args, **kwargs):
		SvgWidget.__init__(self, *args, **kwargs)
		_attrSvgStyles.__init__(self, *args, **kwargs)

	def _getSvgTransform(self):
		return self.element.transform

	def _setSvgTransform(self, val):
		self.element.setAttribute("transform", val)

	def rotate(self, theta):
		"""Convenience to help you set transforms"""
		self._setSvgTransform(mmult(self.transform, rotate(theta)))

	def translate(self, dx, dy):
		"""Convenience to help you set transforms"""
		self._setSvgTransform(mmult(self.transform, translate(dx, dy)))

	def scale(self, sx, sy):
		"""Convenience to help you set transforms"""
		self._setSvgTransform(mmult(self.transform, scale(sx, sy)))


	def skew(self, kx, ky):
		"""Convenience to help you set transforms"""
		self._setSvgTransform(mmult(mmult(self.transform, skewX(kx)),skewY(ky)))

	def shift(self, x, y):
		'''Convenience function to set the origin arbitrarily'''
		self._setSvgTransform(self.transform[:-2]+(x,y))


@html5.tag
class SvgImage(SvgWidget, _attrSvgViewBox, _attrSvgDimensions, _attrSvgTransform, _attrSvgXlink):
	_tagName = "image"


@html5.tag
class SvgLine(SvgWidget, _attrSvgTransform, _attrSvgPoints, _attrSvgStyles):
	_tagName = "line"

	def __init__(self, *args, **kwargs):
		SvgWidget.__init__(self, *args, **kwargs)
		_attrSvgStyles.__init__(self, *args, **kwargs)

@html5.tag
class SvgPath(SvgWidget, _attrSvgTransform, _attrSvgStyles):
	_tagName = "path"

	def __init__(self, *args, **kwargs):
		SvgWidget.__init__(self, *args, **kwargs)
		_attrSvgStyles.__init__(self, *args, **kwargs)

	def _getD(self):
		return self.element.d

	def _setD(self, val):
		self.element.setAttribute("d", val)

	def _getPathLength(self):
		return self.element.pathLength

	def _setPathLength(self, val):
		self.element.setAttribute("pathLength", val)


@html5.tag
class SvgPolygon(SvgWidget, _attrSvgTransform, _attrSvgPoints, _attrSvgStyles):
	_tagName = "polygon"

	def __init__(self, *args, **kwargs):
		SvgWidget.__init__(self, *args, **kwargs)
		_attrSvgStyles.__init__(self, *args, **kwargs)


@html5.tag
class SvgPolyline(SvgWidget, _attrSvgTransform, _attrSvgPoints, _attrSvgStyles):
	_tagName = "polyline"

	def __init__(self, *args, **kwargs):
		SvgWidget.__init__(self, *args, **kwargs)
		_attrSvgStyles.__init__(self, *args, **kwargs)


@html5.tag
class SvgRect(SvgWidget, _attrSvgDimensions, _attrSvgTransform, _attrSvgStyles):
	_tagName = "rect"

	def __init__(self, *args, **kwargs):
		SvgWidget.__init__(self, *args, **kwargs)
		_attrSvgStyles.__init__(self, *args, **kwargs)


@html5.tag
class SvgText(SvgWidget, _attrSvgDimensions, _attrSvgTransform, _attrSvgStyles):
	_tagName = "text"

	def __init__(self, *args, **kwargs):
		SvgWidget.__init__(self, *args, **kwargs)
		_attrSvgStyles.__init__(self, *args, **kwargs)

	def _getTextanchor(self):
		return self.element.getAttribute("text-anchor")

	def _setTextanchor(self, val):
		self.element.setAttribute("text-anchor", val)

	def _getFontfamily(self):
		return self.element.getAttribute("font-family")

	def _setFontfamily(self, val):
		self.element.setAttribute("font-family", val)

	def _getFontsize(self):
		return self.element.getAttribute("font-size")

	def _setFontsize(self, val):
		self.element.setAttribute("font-size", val)

	def _getText(self):
		return self.element.data

	def _setText(self, txt):
		self.element.data = txt

	def __str__(self):
		return self.element.data




''' later...

class SvgDefs(SvgWidget):
	_tagName = "defs"


class SvgClipPath(SvgWidget):
	_tagName = "clippath"


class SvgLinearGradient(SvgWidget, _attrSvgPoints):
	_tagName = "lineargradient"

	def _setGradientunits(self, value):
		self.element.gradientUnits = value

	def _getGradientunits(self):
		return self.element.gradientUnits

	def _setGradienttransform(self, value):
		self.element.gradientTransform = value

	def _getGradienttransform(self):
		return self.element.gradientTransform


class SvgStop(SvgWidget):
	_tagName = "stop"

	def _setOffset(self, value):
		self.element.offset = value

	def _getOffset(self):
		return self.element.offset

	def _setStopcolor(self, value):
		self.element.offset = value

	def _getStopcolor(self):
		return self.element.offset
'''
