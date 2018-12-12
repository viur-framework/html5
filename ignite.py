# -*- coding: utf-8 -*-
import core as html5

class Label(html5.Label):
	def __init__(self, *args, **kwargs):
		super(Label, self).__init__(*args, **kwargs)
		self.addClass("label ignt-label")

class Input(html5.Input):
	def __init__(self, *args, **kwargs):
		super(Input, self).__init__(*args, **kwargs)
		self.addClass("input ignt-input")

class Check(html5.Div):
	def __init__(self, *args, **kwargs):
		super(Check, self).__init__(*args, **kwargs)
		self.addClass("check ignt-check")

		checkInput = html5.Input()
		checkInput.addClass("check-input")
		checkInput["type"] = "checkbox"
		self.appendChild(checkInput)

		checkLabel = html5.Label(forElem=checkInput)
		checkLabel.addClass("check-label")
		self.appendChild(checkLabel)

class Radio(html5.Div):
	def __init__(self, *args, **kwargs):
		super(Radio, self).__init__(*args, **kwargs)
		self.addClass("radio ignt-radio")

		radioInput = html5.Input()
		radioInput.addClass("radio-input")
		radioInput["type"] = "radio"
		self.appendChild(radioInput)

		radioLabel = html5.Label(forElem=radioInput)
		radioLabel.addClass("radio-label")
		self.appendChild(radioLabel)

class Select(html5.Select):
	def __init__(self, *args, **kwargs):
		super(Select, self).__init__(*args, **kwargs)
		self.addClass("select ignt-select")

class Textarea(html5.Textarea):
	def __init__(self, *args, **kwargs):
		super(Textarea, self).__init__(*args, **kwargs)
		self.addClass("textarea ignt-textarea")
