from html5 import Button as fButton

class Button(fButton):
	def __init__(self, txt=None, callback=None, *args, **kwargs):
		super(Button,self).__init__(*args, **kwargs)
		self["class"] = "button"
		self["type"]="button"

		if txt is not None:
			self.setText(txt)

		self.callback = callback
		self.sinkEvent("onClick")

	def setText(self, txt):
		if txt is not None:
			self.element.innerHTML = txt
		else:
			self.element.innerHTML = ""

	def onClick(self, event):
		event.stopPropagation()
		event.preventDefault()
		if self.callback is not None:
			self.callback(self)
