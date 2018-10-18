from html5 import Textarea as fTextarea

class Input(fTextarea):
	def __init__(self, placeholder=None, callback=None, id=None, *args, **kwargs):
		"""

		:param placeholder: Placeholder text. Default: None
		:param callback: Function to be called onChanged: callback(id, value)
		:param id: Optional id of the input element. Will be passed to callback
		:return:
		"""
		super(Input,self).__init__(*args, **kwargs)
		self["class"] = "input"
		if placeholder is not None:
			self["placeholder"]=placeholder

		self.callback = callback
		if id is not None:
			self["id"] = id
		self.sinkEvent("onChange")

	def onChange(self, event):
		event.stopPropagation()
		event.preventDefault()
		if self.callback is not None:
			self.callback(self, self["id"], self["value"])

	def onDetach(self):
		super(Input,self)
		self.callback = None
