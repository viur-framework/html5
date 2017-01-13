import html5
from html5.ext.popup import Popup
from html5.ext.button import Button

class TextareaDialog( Popup ):
	def __init__(self, text, value="", successHandler=None, abortHandler=None, successLbl="OK", abortLbl="Cancel", *args, **kwargs ):
		super( TextareaDialog, self ).__init__(*args, **kwargs)
		self["class"].append("textareadialog")
		self.successHandler = successHandler
		self.abortHandler = abortHandler

		span = html5.Span()
		span.element.innerHTML = text
		self.appendChild(span)
		self.inputElem = html5.Textarea()
		self.inputElem["value"] = value
		self.appendChild( self.inputElem )
		okayBtn = Button(successLbl, self.onOkay)
		okayBtn["class"].append("btn_okay")
		self.appendChild(okayBtn)
		cancelBtn = Button(abortLbl, self.onCancel)
		cancelBtn["class"].append("btn_cancel")
		self.appendChild(cancelBtn)
		self.sinkEvent("onkeydown")
		self.inputElem.focus()

	def onkeydown(self, event):
		if hasattr(event, 'key'):
			key = event.key
		elif hasattr(event, 'keyIdentifier'):
			# Babelfish: Translate 'keyIdentifier' into 'key'
			if event.keyIdentifier in ['Esc', 'U+001B']:
				key = 'Escape'
			else:
				key = event.keyIdentifier
		print("TextareaDialog:onKeyDown ", key)
		# Some keys have special treatment
		if 'Enter' == key:
			pass
			# event.stopPropagation()
			# event.preventDefault()
			# self.onOkay()
		elif 'Escape' == key:
			event.stopPropagation()
			event.preventDefault()
			self.onCancel()

	def onOkay(self, *args, **kwargs):
		if self.successHandler:
			self.successHandler( self, self.inputElem["value"] )
		self.close()

	def onCancel(self, *args, **kwargs):
		if self.abortHandler:
			self.abortHandler( self, self.inputElem["value"] )
		self.close()
