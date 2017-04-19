
class _Label(object):
	def _getLabel(self):
		return self.element.getAttribute("label")

	def _setLabel(self,val):
		self.element.setAttribute("label", val)
