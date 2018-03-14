
class ViewBox(object):
	def _getViewBox(self):
		return self.element.viewBox
	def _setViewBox(self,val):
		self.element.setAttribute("viewBox", val)

	def _getPreserveAspectRatio(self):
		return self.element.preserveAspectRatio
	def _setPreserveAspectRatio(self,val):
		self.element.setAttribute("preserveAspectRatio", val)


class Dimensions(object):
	def _getWidth(self):
		return self.element.width
	def _setWidth(self,val):
		self.element.setAttribute("width", val)

	def _getHeight(self):
		return self.element.height
	def _setHeight(self,val):
		self.element.setAttribute("height", val)

	def _getX(self):
		return self.element.x
	def _setX(self,val):
		self.element.setAttribute("x", val)

	def _getY(self):
		return self.element.y
	def _setY(self,val):
		self.element.setAttribute("y", val)

	def _getR(self):
		return self.element.r
	def _setR(self,val):
		self.element.setAttribute("r", val)

	def _getRx(self):
		return self.element.rx
	def _setRx(self,val):
		self.element.setAttribute("rx", val)

	def _getRy(self):
		return self.element.ry
	def _setRy(self,val):
		self.element.setAttribute("ry", val)

	def _getCx(self):
		return self.element.cx
	def _setCx(self,val):
		self.element.setAttribute("cx", val)

	def _getCy(self):
		return self.element.cy
	def _setCy(self,val):
		self.element.setAttribute("cy", val)

class Points(object):
	def _getPoints(self):
		return self.element.points
	def _setPoints(self,val):
		self.element.setAttribute("points", val)

	def _getX1(self):
		return self.element.x1
	def _setX1(self,val):
		self.element.setAttribute("x1", val)

	def _getY1(self):
		return self.element.y1
	def _setY1(self,val):
		self.element.setAttribute("y1", val)

	def _getX2(self):
		return self.element.x2
	def _setX2(self,val):
		self.element.setAttribute("x2", val)

	def _getY2(self):
		return self.element.y2
	def _setY2(self,val):
		self.element.setAttribute("y2", val)

class Transform(object):
	def _getTransform(self):
		return self.element.transform
	def _setTransform(self,val):
		self.element.setAttribute("transform", val)

class Xlink(object):
	def _getXlinkhref(self):
		return self.element.getAttribute("xlink:href")
	def _setXlinkhref(self,val):
		self.element.setAttribute("xlink:href", val)

class Styles(object):
	def _getFill(self):
		return self.element.fill
	def _setFill(self,val):
		self.element.setAttribute("fill", val)

	def _getStroke(self):
		return self.element.stroke
	def _setStroke(self,val):
		self.element.setAttribute("stroke", val)

	# def _getStrokeWidth(self):
	# 	return self.element.getAttribute("stroke-width")
	# def _setStrokeWidth(self,val):
	# 	self.element.setAttribute("stroke-width", val)
	#
	# def _getStrokeLinejoin(self):
	# 	return self.element.getAttribute("stroke-linejoin")
	# def _setStrokeLinejoin(self,val):
	# 	self.element.setAttribute("stroke-linejoin", val)
	#
	# def _getStrokeMiterlimit(self):
	# 	return self.element.getAttribute("stroke-miterlimit")
	# def _setStrokeMiterlimit(self,val):
	# 	self.element.setAttribute("stroke-miterlimit", val)
	#
	# def _getFontFamily(self):
	# 	return self.element.getAttribute("font-family")
	# def _setFontFamily(self,val):
	# 	self.element.setAttribute("font-family", val)
	#
	# def _getFontsSize(self):
	# 	return self.element.getAttribute("font-size")
	# def _setFontSize(self,val):
	# 	self.element.setAttribute("font-size", val)
	#
	# def _getTextAnchor(self):
	# 	return self.element.getAttribute("text-anchor")
	# def _setTextAnchor(self,val):
	# 	self.element.setAttribute("text-anchor", val)
