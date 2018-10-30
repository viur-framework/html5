# -*- coding: utf-8 -*-
import core as html5
import utils

class Button(html5.Button):
	def __init__(self, txt=None, callback=None, *args, **kwargs):
		super(Button, self).__init__(*args, **kwargs)
		self["class"] = "button"
		self["type"] = "button"

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


class Input(html5.Input):
	def __init__(self, type="text", placeholder=None, callback=None, id=None, focusCallback=None, *args, **kwargs):
		"""

		:param type: Input type. Default: "text
		:param placeholder: Placeholder text. Default: None
		:param callback: Function to be called onChanged: callback(id, value)
		:param id: Optional id of the input element. Will be passed to callback
		:return:
		"""
		super(Input, self).__init__(*args, **kwargs)
		self["class"] = "input"
		self["type"] = type
		if placeholder is not None:
			self["placeholder"] = placeholder

		self.callback = callback
		if id is not None:
			self["id"] = id
		self.sinkEvent("onChange")

		self.focusCallback = focusCallback
		if focusCallback:
			self.sinkEvent("onFocus")

	def onChange(self, event):
		event.stopPropagation()
		event.preventDefault()
		if self.callback is not None:
			self.callback(self, self["id"], self["value"])

	def onFocus(self, event):
		event.stopPropagation()
		event.preventDefault()
		if self.focusCallback is not None:
			self.focusCallback(self, self["id"], self["value"])

	def onDetach(self):
		super(Input, self)
		self.callback = None


class Popup(html5.Div):
	def __init__(self, title=None, id=None, className=None, *args, **kwargs):
		super(Popup, self).__init__(*args, **kwargs)

		self["class"] = "alertbox"
		if className is not None and len(className):
			self["class"].append(className)

		if title:
			lbl = html5.Span()
			lbl["class"].append("title")
			lbl.appendChild(html5.TextNode(title))
			self.appendChild(lbl)

		# id can be used to pass information to callbacks
		self.id = id

		self.frameDiv = html5.Div()
		self.frameDiv["class"] = "popup"

		self.frameDiv.appendChild(self)
		html5.Body().appendChild(self.frameDiv)

	def close(self, *args, **kwargs):
		html5.Body().removeChild(self.frameDiv)
		self.frameDiv = None


class InputDialog(Popup):
	def __init__(self, text, value="", successHandler=None, abortHandler=None, successLbl="OK", abortLbl="Cancel",
	             *args, **kwargs):
		super(InputDialog, self).__init__(*args, **kwargs)
		self["class"].append("inputdialog")
		self.successHandler = successHandler
		self.abortHandler = abortHandler

		span = html5.Span()
		span.element.innerHTML = text
		self.appendChild(span)
		self.inputElem = html5.Input()
		self.inputElem["type"] = "text"
		self.inputElem["value"] = value
		self.appendChild(self.inputElem)
		okayBtn = Button(successLbl, self.onOkay)
		okayBtn["class"].append("btn_okay")
		self.appendChild(okayBtn)
		cancelBtn = Button(abortLbl, self.onCancel)
		cancelBtn["class"].append("btn_cancel")
		self.appendChild(cancelBtn)
		self.sinkEvent("onkeydown")
		self.inputElem.focus()

	def onkeydown(self, event):
		if hasattr(event, "key"):
			key = event.key
		elif hasattr(event, "keyIdentifier"):
			# Babelfish: Translate "keyIdentifier" into "key"
			if event.keyIdentifier in ["Esc", "U+001B"]:
				key = "Escape"
			else:
				key = event.keyIdentifier
		if "Enter" == key:
			event.stopPropagation()
			event.preventDefault()
			self.onOkay()
		elif "Escape" == key:
			event.stopPropagation()
			event.preventDefault()
			self.onCancel()

	def onOkay(self, *args, **kwargs):
		if self.successHandler:
			self.successHandler(self, self.inputElem["value"])
		self.close()

	def onCancel(self, *args, **kwargs):
		if self.abortHandler:
			self.abortHandler(self, self.inputElem["value"])
		self.close()


class Alert(Popup):
	"""
	Just displaying an alerting message box with OK-button.
	"""

	def __init__(self, msg, title=None, okCallback=None, okLabel="OK", *args, **kwargs):
		super(Alert, self).__init__(title, *args, **kwargs)
		self.addClass("alert")

		self.okCallback = okCallback

		message = html5.Span()
		message.addClass("alert-msg")
		self.appendChild(message)

		if isinstance(msg, html5.Widget):
			message.appendChild(msg)
		else:
			utils.textToHtml(message, msg)

		okBtn = Button(okLabel, callback=self.onOkBtnClick)
		okBtn.addClass("alert-btn-ok")
		self.appendChild(okBtn)

		self.sinkEvent("onKeyDown")
		okBtn.focus()

	def drop(self):
		self.okCallback = None
		self.close()

	def onOkBtnClick(self, sender=None):
		if self.okCallback:
			self.okCallback(self)

		self.drop()

	def onKeyDown(self, event):
		if hasattr(event, "key"):
			key = event.key
		elif hasattr(event, "keyIdentifier"):
			key = event.keyIdentifier
		else:
			key = None

		if key == "Enter":
			event.stopPropagation()
			event.preventDefault()
			self.onOkBtnClick()


class YesNoDialog(Popup):
	def __init__(self, question, title=None, yesCallback=None, noCallback=None, yesLabel="Yes", noLabel="No", *args,
	             **kwargs):
		super(YesNoDialog, self).__init__(title, *args, **kwargs)
		self["class"].append("yesnodialog")

		self.yesCallback = yesCallback
		self.noCallback = noCallback

		lbl = html5.Span()
		lbl["class"].append("question")
		self.appendChild(lbl)

		if isinstance(question, html5.Widget):
			lbl.appendChild(question)
		else:
			utils.textToHtml(lbl, question)

		btnYes = Button(yesLabel, callback=self.onYesClicked)
		btnYes["class"].append("btn_yes")
		self.appendChild(btnYes)

		if len(noLabel):
			btnNo = Button(noLabel, callback=self.onNoClicked)
			btnNo["class"].append("btn_no")
			self.appendChild(btnNo)

		self.sinkEvent("onkeydown")
		btnYes.focus()

	def onkeydown(self, event):
		if hasattr(event, "key"):
			key = event.key
		elif hasattr(event, "keyIdentifier"):
			# Babelfish: Translate "keyIdentifier" into "key"
			if event.keyIdentifier in ["Esc", "U+001B"]:
				key = "Escape"
			else:
				key = event.keyIdentifier
		else:
			key = None

		if "Enter" == key:
			event.stopPropagation()
			event.preventDefault()
			self.onYesClicked()
		elif "Escape" == key:
			event.stopPropagation()
			event.preventDefault()
			self.onNoClicked()

	def drop(self):
		self.yesCallback = None
		self.noCallback = None
		self.close()

	def onYesClicked(self, *args, **kwargs):
		if self.yesCallback:
			self.yesCallback(self)

		self.drop()

	def onNoClicked(self, *args, **kwargs):
		if self.noCallback:
			self.noCallback(self)

		self.drop()


class SelectDialog(Popup):

	def __init__(self, prompt, items=None, title=None, okBtn="OK", cancelBtn="Cancel", forceSelect=False,
	             callback=None, *args, **kwargs):
		super(SelectDialog, self).__init__(title, *args, **kwargs)
		self["class"].append("selectdialog")

		self.callback = callback
		self.items = items
		assert isinstance(self.items, list)

		# Prompt
		if prompt:
			lbl = html5.Span()
			lbl["class"].append("prompt")

			if isinstance(prompt, html5.Widget):
				lbl.appendChild(prompt)
			else:
				utils.textToHtml(lbl, prompt)

			self.appendChild(lbl)

		# Items
		if not forceSelect and len(items) <= 3:
			for idx, item in enumerate(items):
				if isinstance(item, dict):
					title = item.get("title")
					cssc = item.get("class")
				elif isinstance(item, tuple):
					title = item[1]
					cssc = None
				else:
					title = item

				btn = Button(title, callback=self.onAnyBtnClick)
				btn.idx = idx

				if cssc:
					btn.addClass(cssc)

				self.appendChild(btn)
		else:
			self.select = html5.Select()
			self.appendChild(self.select)

			for idx, item in enumerate(items):
				if isinstance(item, dict):
					title = item.get("title")
				elif isinstance(item, tuple):
					title = item[1]
				else:
					title = item

				opt = html5.Option(title)
				opt["value"] = str(idx)

				self.select.appendChild(opt)

			if okBtn:
				self.appendChild(Button(okBtn, callback=self.onOkClick))

			if cancelBtn:
				self.appendChild(Button(cancelBtn, callback=self.onCancelClick))

	def onAnyBtnClick(self, sender):
		item = self.items[sender.idx]

		if isinstance(item, dict) and item.get("callback") and callable(item["callback"]):
			item["callback"](item)

		if self.callback:
			self.callback(item)

		self.items = None
		self.close()

	def onCancelClick(self, sender=None):
		self.close()

	def onOkClick(self, sender=None):
		assert self.select["selectedIndex"] >= 0
		item = self.items[int(self.select.children(self.select["selectedIndex"])["value"])]

		if isinstance(item, dict) and item.get("callback") and callable(item["callback"]):
			item["callback"](item)

		if self.callback:
			self.callback(item)

		self.items = None
		self.select = None
		self.close()


class TextareaDialog(Popup):
	def __init__(self, text, value="", successHandler=None, abortHandler=None, successLbl="OK", abortLbl="Cancel",
	             *args, **kwargs):
		super(TextareaDialog, self).__init__(*args, **kwargs)
		self["class"].append("textareadialog")
		self.successHandler = successHandler
		self.abortHandler = abortHandler

		span = html5.Span()
		span.element.innerHTML = text
		self.appendChild(span)
		self.inputElem = html5.Textarea()
		self.inputElem["value"] = value
		self.appendChild(self.inputElem)
		okayBtn = Button(successLbl, self.onOkay)
		okayBtn["class"].append("btn_okay")
		self.appendChild(okayBtn)
		cancelBtn = Button(abortLbl, self.onCancel)
		cancelBtn["class"].append("btn_cancel")
		self.appendChild(cancelBtn)
		self.sinkEvent("onkeydown")
		self.inputElem.focus()

	def onkeydown(self, event):
		if hasattr(event, "key"):
			key = event.key
		elif hasattr(event, "keyIdentifier"):
			# Babelfish: Translate "keyIdentifier" into "key"
			if event.keyIdentifier in ["Esc", "U+001B"]:
				key = "Escape"
			else:
				key = event.keyIdentifier

		# Some keys have special treatment
		if "Enter" == key:
			pass

		elif "Escape" == key:
			event.stopPropagation()
			event.preventDefault()
			self.onCancel()

	def onOkay(self, *args, **kwargs):
		if self.successHandler:
			self.successHandler(self, self.inputElem["value"])
		self.close()

	def onCancel(self, *args, **kwargs):
		if self.abortHandler:
			self.abortHandler(self, self.inputElem["value"])
		self.close()
