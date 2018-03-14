# -*- coding: utf-8 -*

'''
from html5 import parse
'''

class TextNode(object):
	"""
		Represents a piece of text inside the DOM.
		This is the *only* object not deriving from "Widget", as it does
		not support any of its properties.
	"""

	def __init__(self, txt=None, *args, **kwargs):
		super().__init__()
		self._parent = None
		self._children = []
		self.element = document.createTextNode("")
		self._isAttached = False

		if txt is not None:
			self.element.data = txt

	def _setText(self, txt):
		self.element.data = txt

	def _getText(self):
		return self.element.data

	def __str__(self):
		return self.element.data

	def onAttach(self):
		self._isAttached = True

	def onDetach(self):
		self._isAttached = False

	def _setDisabled(self, disabled):
		return

	def _getDisabled(self):
		return False


class ClassWrapper(object):
	def __init__(self, targetWidget):
		super().__init__()
		self.targetWidget = targetWidget
		self.classList = []

		clsStr = targetWidget.element.getAttribute("class")
		if clsStr:
			for c in clsStr.split(" "):
				self.classList.append(c)

	def _updateElem(self):
		if len(self) == 0:
			self.targetWidget.element.removeAttribute("class")
		else:
			self.targetWidget.element.setAttribute("class", " ".join(self.classList))

	def append(self, p_object):
		self.classList.append(p_object)
		self._updateElem()

	def clear(self):
		self.classList.clear()
		self._updateElem()

	def remove(self, value):
		try:
			self.classList.remove(value)
			self._updateElem()
		except:
			pass

	def extend(self, iterable):
		self.classList.extend(iterable)
		self._updateElem()

	def insert(self, index, p_object):
		self.classList.insert(index, p_object)
		self._updateElem()

	def pop(self, index=None):
		self.classList.pop(self, index)
		self._updateElem()

'''
class DataWrapper(dict):
	def __init__(self, targetWidget):
		super().__init__()
		self.targetWidget = targetWidget
		alldata = targetWidget.element
		for data in dir(alldata.dataset):
			dict.__setitem__(self, data, getattr(alldata.dataset, data))

	def __setitem__(self, key, value):
		dict.__setitem__(self, key, value)
		self.targetWidget.element.setAttribute(str("data-" + key), value)

	def update(self, E=None, **F):
		dict.update(self, E, **F)
		if E is not None and "keys" in dir(E):
			for key in E:
				self.targetWidget.element.setAttribute(str("data-" + key), E["data-" + key])
		elif E:
			for (key, val) in E:
				self.targetWidget.element.setAttribute(str("data-" + key), "data-" + val)
		for key in F:
			self.targetWidget.element.setAttribute(str("data-" + key), F["data-" + key])
'''
'''
class StyleWrapper(dict):
	def __init__(self, targetWidget):
		super().__init__()
		self.targetWidget = targetWidget
		style = targetWidget.element.style
		for key in dir(style):
			# Convert JS-Style-Syntax to CSS Syntax (ie borderTop -> border-top)
			realKey = ""
			for currChar in key:
				if currChar.isupper():
					realKey += "-"
				realKey += currChar.lower()
			val = style.getPropertyValue(realKey)
			if val:
				dict.__setitem__(self, realKey, val)

	def __setitem__(self, key, value):
		dict.__setitem__(self, key, value)
		self.targetWidget.element.style.setProperty(key, value)

	def update(self, E=None, **F):
		dict.update(self, E, **F)
		if E is not None and "keys" in dir(E):
			for key in E:
				self.targetWidget.element.style.setProperty(key, E[key])
		elif E:
			for (key, val) in E:
				self.targetWidget.element.style.setProperty(key, val)
		for key in F:
			self.targetWidget.element.style.setProperty(key, F[key])
'''

class Widget(object):
	_baseClass = None
	_namespace = None

	def __init__(self, *args, **kwargs):
		if "_wrapElem" in kwargs.keys():
			self.element = kwargs["_wrapElem"]
			del kwargs["_wrapElem"]
		else:
			assert self._baseClass is not None
			self.element = document.createElement(self._baseClass, ns=self._namespace)

		super().__init__()

		self._children = []
		self._catchedEvents = []
		self._disabledState = None
		self._isAttached = False
		self._parent = None

		self._lastDisplayState = None

	def sinkEvent(self, *args):
		for eventName in args:
			if eventName in self._catchedEvents or eventName.lower in ["onattach", "ondetach"]:
				continue
			assert eventName in dir(self), "{} must provide a {} method".format(str(self), eventName)
			self._catchedEvents.append(eventName)
			setattr(self.element, eventName.lower(), getattr(self, eventName))

	def unsinkEvent(self, *args):
		for eventName in args:
			if not eventName in self._catchedEvents:
				continue
			self._catchedEvents.remove(eventName)
			setattr(self.element, eventName.lower(), None)

	def disable(self):
		if not self["disabled"]:
			self["disabled"] = True

	def enable(self):
		if self["disabled"]:
			self["disabled"] = False

	def _getDisabled(self):
		return self._disabledState is not None

	def _setDisabled(self, disable):
		for child in self._children:
			child._setDisabled(disable)

		if disable:
			if self._disabledState is not None:
				self._disabledState["recursionCounter"] += 1
			else:
				self._disabledState = {"events": self._catchedEvents[:], "recursionCounter": 1}
				self.unsinkEvent(*self._catchedEvents[:])
		else:

			if self._disabledState is None:
				pass  # Fixme: Print a warning instead?!
			else:
				if self._disabledState["recursionCounter"] > 1:
					self._disabledState["recursionCounter"] -= 1
				else:
					self.sinkEvent(*self._disabledState["events"])
					self._disabledState = None

		if self._getDisabled():
			if not "is_disabled" in self["class"]:
				self["class"].append("is_disabled")
		else:
			if "is_disabled" in self["class"]:
				self["class"].remove("is_disabled")

	def _getTargetFuncName(self, key, type):
		assert type in ["get", "set"]
		return "_{}{}{}".format(type, key[0].upper(), key[1:])

	def __getitem__(self, key):
		funcName = self._getTargetFuncName(key, "get")
		if funcName in dir(self):
			print( self._baseClass or str( self ), "get", key, getattr( self, funcName)() )
			return (getattr(self, funcName)())
		return (None)

	def __setitem__(self, key, value):
		funcName = self._getTargetFuncName(key, "set")
		if funcName in dir(self):
			# print( self._baseClass or str( self ), "set", key, value )
			return (getattr(self, funcName)(value))
		raise ValueError("{} is no valid attribute for {}".format(key, (self._baseClass or str(self))))

	def _getData(self):
		"""
		Custom data attributes are intended to store custom data private to the page or application, for which there are no more appropriate attributes or elements.
		@param name:
		@return:
		"""
		return (DataWrapper(self))

	def _getTranslate(self):
		"""
		Specifies whether an elementâs attribute values and contents of its children are to be translated when the page is localized, or whether to leave them unchanged.
		@return: True | False
		"""
		return True if self.element.translate == "yes" else False

	def _setTranslate(self, val):
		"""
		Specifies whether an elementâs attribute values and contents of its children are to be translated when the page is localized, or whether to leave them unchanged.
		@param val: True | False
		"""
		self.element.translate = "yes" if val == True else "no"

	def _getTitle(self):
		"""
		Advisory information associated with the element.
		@return: String
		"""
		return self.element.title

	def _setTitle(self, val):
		"""
		Advisory information associated with the element.
		@param val: String
		"""
		self.element.title = val

	def _getTabindex(self):
		"""
		Specifies whether the element represents an element that is is focusable (that is, an element which is part of the sequence of focusable elements in the document), and the relative order of the element in the sequence of focusable elements in the document.
		@return: number
		"""
		return self.element.getAttribute("tabindex")

	def _setTabindex(self, val):
		"""
		Specifies whether the element represents an element that is is focusable (that is, an element which is part of the sequence of focusable elements in the document), and the relative order of the element in the sequence of focusable elements in the document.
		@param val:  number
		"""
		self.element.setAttribute("tabindex", val)

	def _getSpellcheck(self):
		"""
		Specifies whether the element represents an element whose contents are subject to spell checking and grammar checking.
		@return: True | False
		"""
		return (True if self.element.spellcheck == "true" else False)

	def _setSpellcheck(self, val):
		"""
		Specifies whether the element represents an element whose contents are subject to spell checking and grammar checking.
		@param val: True | False
		"""
		self.element.spellcheck = str(val).lower()

	def _getLang(self):
		"""
		Specifies the primary language for the contents of the element and for any of the elementâs attributes that contain text.
		@return: language tag e.g. de|en|fr|es|it|ru|
		"""
		return self.element.lang

	def _setLang(self, val):
		"""
		Specifies the primary language for the contents of the element and for any of the elementâs attributes that contain text.
		@param val: language tag
		"""
		self.element.lang = val

	def _getHidden(self):
		"""
		Specifies that the element represents an element that is not yet, or is no longer, relevant.
		@return: True | False
		"""
		return (True if self.element.hasAttribute("hidden") else False)

	def _setHidden(self, val):
		"""
		Specifies that the element represents an element that is not yet, or is no longer, relevant.
		@param val: True | False
		"""
		if val == True:
			self.element.setAttribute("hidden", "")
		else:
			self.element.removeAttribute("hidden")

	def _getDropzone(self):
		"""
		Specifies what types of content can be dropped on the element, and instructs the UA about which actions to take with content when it is dropped on the element.
		@return: "copy" | "move" | "link"
		"""
		return self.element.dropzone

	def _setDropzone(self, val):
		"""
		Specifies what types of content can be dropped on the element, and instructs the UA about which actions to take with content when it is dropped on the element.
		@param val: "copy" | "move" | "link"
		"""
		self.element.dropzone = val

	def _getDraggable(self):
		"""
		Specifies whether the element is draggable.
		@return: True | False | "auto"
		"""
		return (self.element.draggable if str(self.element.draggable) == "auto" else (
		True if str(self.element.draggable).lower() == "true" else False))

	def _setDraggable(self, val):
		"""
		Specifies whether the element is draggable.
		@param val: True | False | "auto"
		"""
		self.element.draggable = str(val).lower()

	def _getDir(self):
		"""
		Specifies the elementâs text directionality.
		@return: ltr | rtl | auto
		"""
		return self.element.dir

	def _setDir(self, val):
		"""
		Specifies the elementâs text directionality.
		@param val: ltr | rtl | auto
		"""
		self.element.dir = val

	def _getContextmenu(self):
		"""
		The value of the id attribute on the menu with which to associate the element as a context menu.
		@return:
		"""
		return self.element.contextmenu

	def _setContextmenu(self, val):
		"""
		The value of the id attribute on the menu with which to associate the element as a context menu.
		@param val:
		"""
		self.element.contextmenu = val

	def _getContenteditable(self):
		"""
		Specifies whether the contents of the element are editable.
		@return: True | False
		"""
		v = self.element.getAttribute("contenteditable")
		return (str(v).lower() == "true")

	def _setContenteditable(self, val):
		"""
		Specifies whether the contents of the element are editable.
		@param val: True | False
		"""
		self.element.setAttribute("contenteditable", str(val).lower())

	def _getAccesskey(self):
		"""
		A key label or list of key labels with which to associate the element; each key label represents a keyboard shortcut which UAs can use to activate the element or give focus to the element.
		@param self:
		@return:
		"""
		return (self.element.accesskey)

	def _setAccesskey(self, val):
		"""
		A key label or list of key labels with which to associate the element; each key label represents a keyboard shortcut which UAs can use to activate the element or give focus to the element.
		@param self:
		@param val:
		"""
		self.element.accesskey = val

	def _getId(self):
		"""
		Specifies a unique id for an element
		@param self:
		@return:
		"""
		return self.element.id

	def _setId(self, val):
		"""
		Specifies a unique id for an element
		@param self:
		@param val:
		"""
		self.element.id = val

	def _getClass(self):
		"""
		The class attribute specifies one or more classnames for an element.
		@return:
		"""
		return ClassWrapper(self)

	def _setClass(self, value):
		"""
		The class attribute specifies one or more classnames for an element.
		@param self:
		@param value:
		@raise ValueError:
		"""

		if value is None:
			self.element.setAttribute("class", " ")
		elif isinstance(value, str):
			self.element.setAttribute("class", value)
		elif isinstance(value, list):
			self.element.setAttribute("class", " ".join(value))
		else:
			raise ValueError("Class must be a String, a List or None")

	def _getStyle(self):
		"""
		The style attribute specifies an inline style for an element.
		@param self:
		@return:
		"""
		return StyleWrapper(self)

	def hide(self):
		"""
		Hide element, if shown.
		:return:
		"""
		state = self["style"].get("display", "")

		if state != "none":
			self._lastDisplayState = state
			self["style"]["display"] = "none"

	def show(self):
		"""
		Show element, if hidden.
		:return:
		"""
		if self._lastDisplayState is not None:
			self["style"]["display"] = self._lastDisplayState
			self._lastDisplayState = None

	def onAttach(self):
		self._isAttached = True
		for c in self._children[:]:
			c.onAttach()

	def onDetach(self):
		self._isAttached = False
		for c in self._children[:]:
			c.onDetach()

	def insertBefore(self, insert, child):
		assert child in self._children, "{} is not a child of {}".format(child, self)

		if insert._parent:
			insert._parent.removeChild(insert)

		self.element.insertBefore(insert.element, child.element)
		self._children.insert(self._children.index(child), insert)

		insert._parent = self
		if self._isAttached:
			insert.onAttach()

	def prependChild(self, child):
		if isinstance(child, list) or isinstance(child, tuple):
			for item in child:
				self.prependChild(item)

			return

		elif not isinstance(child, Widget):
			child = TextNode(str(child))

		if child._parent:
			child._parent._children.remove(child)
			child._parent = None

		if not self._children:
			self.appendChild(child)
		else:
			self.insertBefore(child, self.children(0))

	def appendChild(self, child):
		if isinstance(child, list) or isinstance(child, tuple):
			for item in child:
				self.appendChild(item)

			return

		elif not isinstance(child, Widget):
			child = TextNode(str(child))

		if child._parent:
			child._parent._children.remove(child)

		self._children.append(child)
		self.element.appendChild(child.element)
		child._parent = self
		if self._isAttached:
			child.onAttach()

	def removeChild(self, child):
		assert child in self._children, "{} is not a child of {}".format(child, self)

		if child._isAttached:
			child.onDetach()

		self.element.removeChild(child.element)
		self._children.remove(child)
		child._parent = None

	def removeAllChildren(self):
		"""
		Removes all child widgets of the current widget.
		"""
		for child in self._children[:]:
			self.removeChild(child)

	def isParentOf(self, widget):
		"""
		Checks if an object is the parent of widget.

		:type widget: Widget
		:param widget: The widget to check for.
		:return: True, if widget is a child of the object, else False.
		"""

		# You cannot be your own child!
		if self == widget:
			return False

		for child in self._children:
			if child == widget:
				return True

			if child.isParentOf(widget):
				return True

		return False

	def isChildOf(self, widget):
		"""
		Checks if an object is the child of widget.

		:type widget: Widget
		:param widget: The widget to check for.
		:return: True, if object is a child of widget, else False.
		"""

		# You cannot be your own parent!
		if self == widget:
			return False

		parent = self.parent()
		while parent:
			if parent == widget:
				return True

			parent = widget.parent()

		return False

	def addClass(self, *args):
		"""
		Adds a class or a list of classes to the current widget.
		If the widget already has the class, it is ignored.

		:param args: A list of class names. This can also be a list.
		:type args: list of str | list of list of str
		"""

		for item in args:
			print("addClass", item, self["class"])

			if isinstance(item, list):
				self.addClass(item)

			elif isinstance(item, str) or isinstance(item, unicode):
				for sitem in item.split(" "):
					if sitem not in self["class"]:
						self["class"].append(sitem)
			else:
				raise TypeError()

	def removeClass(self, *args):
		"""
		Removes a class or a list of classes from the current widget.

		:param args: A list of class names. This can also be a list.
		:type args: list of str | list of list of str
		"""

		for item in args:
			if isinstance(item, list):
				self.removeClass(item)

			elif isinstance(item, str) or isinstance(item, unicode):
				for sitem in item.split(" "):
					if sitem in self["class"]:
						self["class"].remove(sitem)
			else:
				raise TypeError()

	def toggleClass(self, on, off=None):
		"""
		Toggles the class ``on``.

		If the widget contains a class ``on``, it is toggled by ``off``.
		``off`` can either be a class name that is substituted, or nothing.

		:param on: Classname to test for. If ``on`` does not exist, but ``off``, ``off`` is replaced by ``on``.
		:type on: str

		:param off: Classname to replace if ``on`` existed.
		:type off: str

		:return: Returns True, if ``on`` was switched, else False.
		:rtype: bool
		"""
		if on in self["class"]:
			self["class"].remove(on)

			if off and off not in self["class"]:
				self["class"].append(off)

			return False

		if off and off in self["class"]:
			self["class"].remove(off)

		self["class"].append(on)
		return True

	def onBlur(self, event):
		pass

	def onChange(self, event):
		pass

	def onContextMenu(self, event):
		pass

	def onFocus(self, event):
		pass

	def onFormChange(self, event):
		pass

	def onFormInput(self, event):
		pass

	def onInput(self, event):
		pass

	def onInvalid(self, event):
		pass

	def onReset(self, event):
		pass

	def onSelect(self, event):
		pass

	def onSubmit(self, event):
		pass

	def onKeyDown(self, event):
		pass

	def onKeyPress(self, event):
		pass

	def onKeyUp(self, event):
		pass

	def onClick(self, event):
		pass

	def onDblClick(self, event):
		pass

	def onDrag(self, event):
		pass

	def onDragEnd(self, event):
		pass

	def onDragEnter(self, event):
		pass

	def onDragLeave(self, event):
		pass

	def onDragOver(self, event):
		pass

	def onDragStart(self, event):
		pass

	def onDrop(self, event):
		pass

	def onMouseDown(self, event):
		pass

	def onMouseMove(self, event):
		pass

	def onMouseOut(self, event):
		pass

	def onMouseOver(self, event):
		pass

	def onMouseUp(self, event):
		pass

	def onMouseWheel(self, event):
		pass

	def onScroll(self, event):
		pass

	def onTouchStart(self, event):
		pass

	def onTouchEnd(self, event):
		pass

	def onTouchMove(self, event):
		pass

	def onTouchCancel(self, event):
		pass

	def focus(self):
		self.element.focus()

	def blur(self):
		self.element.blur()

	def parent(self):
		return self._parent

	def children(self, n=None):
		"""
		Access children of widget.

		If ``n`` is ommitted, it returns a list of all child-widgets;
		Else, it returns the N'th child, or None if its out of bounds.

		:param n: Optional offset of child widget to return.
		:type n: int

		:return: Returns all children or only the requested one.
		:rtype: list | Widget | None
		"""
		if n is None:
			return self._children[:]

		if n >= 0 and n < len(self._children):
			return self._children[n]

		return None

	def _getEventMap(self):
		res = {"onblur": "onBlur",
		       "onchange": "onChange",
		       "oncontextmenu": "onContextMenu",
		       "onfocus": "onFocus",
		       "onformchange": "onFormChange",
		       "onforminput": "onFormInput",
		       "oninput": "onInput",
		       "oninvalid": "onInvalid",
		       "onreset": "onReset",
		       "onselect": "onSelect",
		       "onsubmit": "onSubmit",
		       "onkeydown": "onKeyDown",
		       "onkeypress": "onKeyPress",
		       "onkeyup": "onKeyUp",
		       "onclick": "onClick",
		       "ondblclick": "onDblClick",
		       "ondrag": "onDrag",
		       "ondragend": "onDragEnd",
		       "ondragenter": "onDragEnter",
		       "ondragleave": "onDragLeave",
		       "ondragover": "onDragOver",
		       "ondragstart": "onDragStart",
		       "ondrop": "onDrop",
		       "onmousedown": "onMouseDown",
		       "onmousemove": "onMouseMove",
		       "onmouseout": "onMouseOut",
		       "onmouseover": "onMouseOver",
		       "onmouseup": "onMouseUp",
		       "onmousewheel": "onMouseWheel",
		       "onscroll": "onScroll",
		       "ontouchstart": "onTouchStart",
		       "ontouchend": "onTouchEnd",
		       "ontouchmove": "onTouchMove",
		       "ontouchcancel": "onTouchCancel"
		       }
		return (res)

	def sortChildren(self, key):
		"""
			Sorts our direct children. They are rearranged on DOM level.
			Key must be a function accepting one widget as parameter and must return
			the key used to sort these widgets.
		"""
		self._children.sort(key=key)
		tmpl = self._children[:]
		tmpl.reverse()
		for c in tmpl:
			self.element.removeChild(c.element)
			self.element.insertBefore(c.element, self.element.children.item(0))

	def fromHTML(self, html, appendTo = None, bindTo = None):
		"""
		Parses html and constructs its elements as part of self.

		:param html: HTML code.
		:param appendTo: The entity where the HTML code is constructed below.
						This defaults to self in usual case.
		:param bindTo: The entity where the named objects are bound to.
						This defaults to self in usual case.

		:return:
		"""
		if appendTo is None:
			appendTo = self

		if bindTo is None:
			bindTo = self

		return parse.fromHTML(html, appendTo, bindTo)
