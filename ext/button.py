from html5.form import Button as fButton
from html5.textnode import TextNode

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
		self.removeAllChildren()

		if txt is not None:
			self.appendChild(TextNode(txt))

	def onClick(self, event):
		event.stopPropagation()
		event.preventDefault()
		if self.callback is not None:
			self.callback(self)

	def onDetach(self):
		super(Button,self)
		self.callback = None
