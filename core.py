# -*- coding: utf-8 -*

########################################################################################################################
# DOM-access functions and variables
########################################################################################################################

try:
	# PyJS
	jseval = eval

	window = jseval("window.top")
	document = window.document

except NameError:
	print("Emulation mode")
	from xml.dom.minidom import parseString
	jseval = None

	window = None
	document = parseString('<html><head /><body /></html>')


def domCreateAttribute(tag, ns=None):
	"""
		Creates a new HTML/SVG/... attribute
		 :param ns: the namespace. Default: HTML. Possible values: HTML, SVG, XBL, XUL
   """
	uri = None

	if ns == "SVG":
		uri = "http://www.w3.org/2000/svg"
	elif ns == "XBL":
		uri = "http://www.mozilla.org/xbl"
	elif ns == "XUL":
		uri = "http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul"

	if uri:
		return document.createAttribute(uri, tag)

	return document.createAttribute(tag)


def domCreateElement(tag, ns=None):
	"""
		Creates a new HTML/SVG/... tag
		  :param ns: the namespace. Default: HTML. Possible values: HTML, SVG, XBL, XUL
	"""
	uri = None

	if ns == "SVG":
		uri = "http://www.w3.org/2000/svg"
	elif ns == "XBL":
		uri = "http://www.mozilla.org/xbl"
	elif ns == "XUL":
		uri = "http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul"

	if uri:
		return document.createElementNS(uri, tag)

	return document.createElement(tag)


def domCreateTextNode(txt=""):
	return document.createTextNode(txt)


def domGetElementById(idTag):
	return document.getElementById(idTag)


def domElementFromPoint(x, y):
	return document.elementFromPoint(x, y)


def domGetElementsByTagName(tag):
	items = document.getElementsByTagName(tag)
	return [items.item(i) for i in range(0, items.length)]


########################################################################################################################
# HTML Widgets
########################################################################################################################

# TextNode -------------------------------------------------------------------------------------------------------------

class TextNode(object):
	"""
		Represents a piece of text inside the DOM.
		This is the *only* object not deriving from "Widget", as it does
		not support any of its properties.
	"""

	def __init__(self, txt=None, *args, **kwargs):
		super(TextNode, self).__init__()
		self._parent = None
		self._children = []
		self.element = domCreateTextNode(txt or "")
		self._isAttached = False

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

	def children(self):
		return []


# _WidgetClassWrapper --------------------------------------------------------------------------------------------------

class _WidgetClassWrapper(list):
	def __init__(self, targetWidget):
		super(_WidgetClassWrapper, self).__init__()
		self.targetWidget = targetWidget
		clsStr = targetWidget.element.getAttribute("class")
		if clsStr:
			for c in clsStr.split(" "):
				list.append(self, c)

	def _updateElem(self):
		if len(self) == 0:
			self.targetWidget.element.removeAttribute("class")
		else:
			self.targetWidget.element.setAttribute("class", " ".join(self))

	def append(self, p_object):
		list.append(self, p_object)
		self._updateElem()

	def clear(self):
		list.clear(self)
		self._updateElem()

	def remove(self, value):
		try:
			list.remove(self, value)
		except:
			pass
		self._updateElem()

	def extend(self, iterable):
		list.extend(self, iterable)
		self._updateElem()

	def insert(self, index, p_object):
		list.insert(self, index, p_object)
		self._updateElem()

	def pop(self, index=None):
		list.pop(self, index)
		self._updateElem()


# _WidgetDataWrapper ---------------------------------------------------------------------------------------------------

class _WidgetDataWrapper(dict):
	def __init__(self, targetWidget):
		super(_WidgetDataWrapper, self).__init__()
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


# _WidgetStyleWrapper --------------------------------------------------------------------------------------------------

class _WidgetStyleWrapper(dict):
	def __init__(self, targetWidget):
		super(_WidgetStyleWrapper, self).__init__()
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


# Widget ---------------------------------------------------------------------------------------------------------------

class Widget(object):
	_baseClass = None
	_namespace = None

	def __init__(self, *args, **kwargs):
		if "_wrapElem" in kwargs.keys():
			self.element = kwargs["_wrapElem"]
			del kwargs["_wrapElem"]
		else:
			assert self._baseClass is not None
			self.element = domCreateElement(self._baseClass, ns=self._namespace)

		super(Widget, self).__init__()

		self._children = []
		self._catchedEvents = {}
		self._disabledState = None
		self._isAttached = False
		self._parent = None

		self._lastDisplayState = None

	def sinkEvent(self, *args):
		for event_attrName in args:
			event = event_attrName.lower()

			if event_attrName in self._catchedEvents or event in ["onattach", "ondetach"]:
				continue

			eventFn = getattr(self, event_attrName, None)
			assert eventFn and callable(eventFn), "{} must provide a {} method".format(str(self), event_attrName)

			self._catchedEvents[event_attrName] = eventFn

			if event.startswith("on"):
				event = event[2:]

			self.element.addEventListener(event, eventFn)

			# print("sink", event, eventFn)

	def unsinkEvent(self, *args):
		for event_attrName in args:
			event = event_attrName.lower()

			if event_attrName not in self._catchedEvents:
				continue

			eventFn = self._catchedEvents[event_attrName]
			del self._catchedEvents[event_attrName]

			if event.startswith("on"):
				event = event[2:]

			self.element.removeEventListener(event, eventFn)

			# print("unsink", ret, eventFn)

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
				self._disabledState = {"events": self._catchedEvents.keys(), "recursionCounter": 1}
				self.unsinkEvent(*self._catchedEvents.keys())
		else:

			if self._disabledState:
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

	def _getTargetfuncName(self, key, type):
		assert type in ["get", "set"]
		return "_{}{}{}".format(type, key[0].upper(), key[1:])

	def __getitem__(self, key):
		funcName = self._getTargetfuncName(key, "get")
		# print("GET", funcName, key)

		if funcName in dir(self):
			# print(self._baseClass or str(self), "get", key, getattr(self, funcName)())
			return getattr(self, funcName)()

		return None

	def __setitem__(self, key, value):
		funcName = self._getTargetfuncName(key, "set")
		# print("SET", funcName, key, value)

		if funcName in dir(self):
			# print( self._baseClass or str( self ), "set", key, value )
			return getattr(self, funcName)(value)

		raise ValueError("{} is no valid attribute for {}".format(key, (self._baseClass or str(self))))

	def __str__(self):
		return str(self.__class__.__name__)

	def _getData(self):
		"""
		Custom data attributes are intended to store custom data private to the page or application, for which there are no more appropriate attributes or elements.
		:param name:
		:returns:
		"""
		return _WidgetDataWrapper(self)

	def _getTranslate(self):
		"""
		Specifies whether an elements attribute values and contents of its children are to be translated when the page is localized, or whether to leave them unchanged.
		:returns: True | False
		"""
		return True if self.element.translate == "yes" else False

	def _setTranslate(self, val):
		"""
		Specifies whether an elements attribute values and contents of its children are to be translated when the page is localized, or whether to leave them unchanged.
		:param val: True | False
		"""
		self.element.translate = "yes" if val == True else "no"

	def _getTitle(self):
		"""
		Advisory information associated with the element.
		:returns: str
		"""
		return self.element.title

	def _setTitle(self, val):
		"""
		Advisory information associated with the element.
		:param val: str
		"""
		self.element.title = val

	def _getTabindex(self):
		"""
		Specifies whether the element represents an element that is is focusable (that is, an element which is part of the sequence of focusable elements in the document), and the relative order of the element in the sequence of focusable elements in the document.
		:returns: number
		"""
		return self.element.getAttribute("tabindex")

	def _setTabindex(self, val):
		"""
		Specifies whether the element represents an element that is is focusable (that is, an element which is part of the sequence of focusable elements in the document), and the relative order of the element in the sequence of focusable elements in the document.
		:param val:  number
		"""
		self.element.setAttribute("tabindex", val)

	def _getSpellcheck(self):
		"""
		Specifies whether the element represents an element whose contents are subject to spell checking and grammar checking.
		:returns: True | False
		"""
		return (True if self.element.spellcheck == "true" else False)

	def _setSpellcheck(self, val):
		"""
		Specifies whether the element represents an element whose contents are subject to spell checking and grammar checking.
		:param val: True | False
		"""
		self.element.spellcheck = str(val).lower()

	def _getLang(self):
		"""
		Specifies the primary language for the contents of the element and for any of the elements attributes that contain text.
		:returns: language tag e.g. de|en|fr|es|it|ru|
		"""
		return self.element.lang

	def _setLang(self, val):
		"""
		Specifies the primary language for the contents of the element and for any of the elements attributes that contain text.
		:param val: language tag
		"""
		self.element.lang = val

	def _getHidden(self):
		"""
		Specifies that the element represents an element that is not yet, or is no longer, relevant.
		:returns: True | False
		"""
		return (True if self.element.hasAttribute("hidden") else False)

	def _setHidden(self, val):
		"""
		Specifies that the element represents an element that is not yet, or is no longer, relevant.
		:param val: True | False
		"""
		if val == True:
			self.element.setAttribute("hidden", "")
		else:
			self.element.removeAttribute("hidden")

	def _getDropzone(self):
		"""
		Specifies what types of content can be dropped on the element, and instructs the UA about which actions to take with content when it is dropped on the element.
		:returns: "copy" | "move" | "link"
		"""
		return self.element.dropzone

	def _setDropzone(self, val):
		"""
		Specifies what types of content can be dropped on the element, and instructs the UA about which actions to take with content when it is dropped on the element.
		:param val: "copy" | "move" | "link"
		"""
		self.element.dropzone = val

	def _getDraggable(self):
		"""
		Specifies whether the element is draggable.
		:returns: True | False | "auto"
		"""
		return (self.element.draggable if str(self.element.draggable) == "auto" else (
			True if str(self.element.draggable).lower() == "true" else False))

	def _setDraggable(self, val):
		"""
		Specifies whether the element is draggable.
		:param val: True | False | "auto"
		"""
		self.element.draggable = str(val).lower()

	def _getDir(self):
		"""
		Specifies the elements text directionality.
		:returns: ltr | rtl | auto
		"""
		return self.element.dir

	def _setDir(self, val):
		"""
		Specifies the elements text directionality.
		:param val: ltr | rtl | auto
		"""
		self.element.dir = val

	def _getContextmenu(self):
		"""
		The value of the id attribute on the menu with which to associate the element as a context menu.
		:returns:
		"""
		return self.element.contextmenu

	def _setContextmenu(self, val):
		"""
		The value of the id attribute on the menu with which to associate the element as a context menu.
		:param val:
		"""
		self.element.contextmenu = val

	def _getContenteditable(self):
		"""
		Specifies whether the contents of the element are editable.
		:returns: True | False
		"""
		v = self.element.getAttribute("contenteditable")
		return (str(v).lower() == "true")

	def _setContenteditable(self, val):
		"""
		Specifies whether the contents of the element are editable.
		:param val: True | False
		"""
		self.element.setAttribute("contenteditable", str(val).lower())

	def _getAccesskey(self):
		"""
		A key label or list of key labels with which to associate the element; each key label represents a keyboard shortcut which UAs can use to activate the element or give focus to the element.
		:param self:
		:returns:
		"""
		return (self.element.accesskey)

	def _setAccesskey(self, val):
		"""
		A key label or list of key labels with which to associate the element; each key label represents a keyboard shortcut which UAs can use to activate the element or give focus to the element.
		:param self:
		:param val:
		"""
		self.element.accesskey = val

	def _getId(self):
		"""
		Specifies a unique id for an element
		:param self:
		:returns:
		"""
		return self.element.id

	def _setId(self, val):
		"""
		Specifies a unique id for an element
		:param self:
		:param val:
		"""
		self.element.id = val

	def _getClass(self):
		"""
		The class attribute specifies one or more classnames for an element.
		:returns:
		"""
		return _WidgetClassWrapper(self)

	def _setClass(self, value):
		"""
		The class attribute specifies one or more classnames for an element.
		:param self:
		:param value:
		@raise ValueError:
		"""

		if value is None:
			self.element.setAttribute("class", " ")
		elif isinstance(value, str):
			self.element.setAttribute("class", value)
		elif isinstance(value, list):
			self.element.setAttribute("class", " ".join(value))
		else:
			raise ValueError("Class must be a str, a List or None")

	def _getStyle(self):
		"""
		The style attribute specifies an inline style for an element.
		:param self:
		:returns:
		"""
		return _WidgetStyleWrapper(self)

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

	def isHidden(self):
		"""
		Checks if a widget is hidden.
		:return: True if hidden, False otherwise.
		"""
		return self["style"].get("display", "") == "none"

	def isVisible(self):
		"""
		Checks if a widget is visible.
		:return: True if visible, False otherwise.
		"""
		return not self.isHidden()

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

		elif not (isinstance(child, Widget) or isinstance(child, TextNode)):
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

	def onFocusIn(self, event):
		pass

	def onFocusOut(self, event):
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

		try:
			return self._children[n]
		except IndexError:
			return None

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

	def fromHTML(self, html, appendTo=None, bindTo=None, vars=None):
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

		return fromHTML(html, appendTo=appendTo, bindTo=bindTo, vars=vars)


########################################################################################################################
# Attribute Collectors
########################################################################################################################

# _attrLabel ---------------------------------------------------------------------------------------------------------------

class _attrLabel(object):
	def _getLabel(self):
		return self.element.getAttribute("label")

	def _setLabel(self, val):
		self.element.setAttribute("label", val)


# _attrCharset --------------------------------------------------------------------------------------------------------------

class _attrCharset(object):
	def _getCharset(self):
		return self.element._attrCharset

	def _setCharset(self, val):
		self.element._attrCharset = val


# _attrCite -----------------------------------------------------------------------------------------------------------------

class _attrCite(object):
	def _getCite(self):
		return self.element._attrCite

	def _setCite(self, val):
		self.element._attrCite = val


class _attrDatetime(object):
	def _getDatetime(self):
		return self.element.datetime

	def _setDatetime(self, val):
		self.element.datetime = val


# Form -----------------------------------------------------------------------------------------------------------------

class _attrForm(object):
	def _getForm(self):
		return self.element.form

	def _setForm(self, val):
		self.element.form = val


class _attrAlt(object):
	def _getAlt(self):
		return self.element.alt

	def _setAlt(self, val):
		self.element.alt = val


class _attrAutofocus(object):
	def _getAutofocus(self):
		return (True if self.element.hasAttribute("autofocus") else False)

	def _setAutofocus(self, val):
		if val == True:
			self.element.setAttribute("autofocus", "")
		else:
			self.element.removeAttribute("autofocus")


class _attrDisabled(object):
	def _setDisabled(self, val):
		Widget._setDisabled(self, val)
		if self._getDisabled():
			self.element.disabled = True
		else:
			self.element.disabled = False


class _attrChecked(object):
	def _getChecked(self):
		return self.element.checked

	def _setChecked(self, val):
		self.element.checked = val


class _attrIndeterminate(object):
	def _getIndeterminate(self):
		return (self.element.indeterminate)

	def _setIndeterminate(self, val):
		self.element.indeterminate = val


class _attrName(object):
	def _getName(self):
		return self.element.getAttribute("name")

	def _setName(self, val):
		self.element.setAttribute("name", val)


class _attrValue(object):
	def _getValue(self):
		return self.element.value

	def _setValue(self, val):
		self.element.value = val


class _attrAutocomplete(object):
	def _getAutocomplete(self):
		return True if self.element.autocomplete == "on" else False

	def _setAutocomplete(self, val):
		self.element.autocomplete = "on" if val == True else "off"


class _attrRequired(object):
	def _getRequired(self):
		return (True if self.element.hasAttribute("required") else False)

	def _setRequired(self, val):
		if val == True:
			self.element.setAttribute("required", "")
		else:
			self.element.removeAttribute("required")


class _attrMultiple(object):
	def _getMultiple(self):
		return (True if self.element.hasAttribute("multiple") else False)

	def _setMultiple(self, val):
		if val == True:
			self.element.setAttribute("multiple", "")
		else:
			self.element.removeAttribute("multiple")


class _attrSize(object):
	def _getSize(self):
		return self.element.size

	def _setSize(self, val):
		self.element.size = val


class _attrFor(object):
	def _getFor(self):
		return self.element.getAttribute("for")

	def _setFor(self, val):
		self.element.setAttribute("for", val)


class _attrInputs(_attrRequired):
	def _getMaxlength(self):
		return self.element.maxlength

	def _setMaxlength(self, val):
		self.element.maxlength = val

	def _getPlaceholder(self):
		return self.element.placeholder

	def _setPlaceholder(self, val):
		self.element.placeholder = val

	def _getReadonly(self):
		return (True if self.element.hasAttribute("readonly") else False)

	def _setReadonly(self, val):
		if val == True:
			self.element.setAttribute("readonly", "")
		else:
			self.element.removeAttribute("readonly")


class _attrFormhead(object):
	def _getFormaction(self):
		return self.element.formaction

	def _setFormaction(self, val):
		self.element.formaction = val

	def _getFormenctype(self):
		return self.element.formenctype

	def _setFormenctype(self, val):
		self.element.formenctype = val

	def _getFormmethod(self):
		return self.element.formmethod

	def _setFormmethod(self, val):
		self.element.formmethod = val

	def _getFormtarget(self):
		return self.element.formtarget

	def _setFormtarget(self, val):
		self.element.formtarget = val

	def _getFormnovalidate(self):
		return (True if self.element.hasAttribute("formnovalidate") else False)

	def _setFormnovalidate(self, val):
		if val == True:
			self.element.setAttribute("formnovalidate", "")
		else:
			self.element.removeAttribute("formnovalidate")


# _attrHref -----------------------------------------------------------------------------------------------------------------

class _attrHref(object):
	def _getHref(self):
		"""
		Url of a Page
		:param self:
		"""
		return self.element.href

	def _setHref(self, val):
		"""
		Url of a Page
		:param val: URL
		"""
		self.element.href = val

	def _getHreflang(self):
		return self.element.hreflang

	def _setHreflang(self, val):
		self.element.hreflang = val


class _attrTarget(object):
	def _getTarget(self):
		return self.element.target

	def _setTarget(self, val):
		self.element.target = val


# _attrMedia ----------------------------------------------------------------------------------------------------------------

class _attrType(object):
	def _getType(self):
		return self.element.type

	def _setType(self, val):
		self.element.type = val


class _attrMedia(_attrType):
	def _getMedia(self):
		return self.element.media

	def _setMedia(self, val):
		self.element.media = val


class _attrDimensions(object):
	def _getWidth(self):
		return self.element.width

	def _setWidth(self, val):
		self.element.width = val

	def _getHeight(self):
		return self.element.height

	def _setHeight(self, val):
		self.element.height = val


class _attrUsemap(object):
	def _getUsemap(self):
		return self.element.usemap

	def _setUsemap(self, val):
		self.element.usemap = val


class _attrMultimedia(object):
	def _getAutoplay(self):
		return True if self.element.hasAttribute("autoplay") else False

	def _setAutoplay(self, val):
		if val:
			self.element.setAttribute("autoplay", "")
		else:
			self.element.removeAttribute("autoplay")

	def _getPlaysinline(self):
		return True if self.element.hasAttribute("playsinline") else False

	def _setPlaysinline(self, val):
		if val:
			self.element.setAttribute("playsinline", "")
		else:
			self.element.removeAttribute("playsinline")

	def _getControls(self):
		return True if self.element.hasAttribute("controls") else False

	def _setControls(self, val):
		if val:
			self.element.setAttribute("controls", "")
		else:
			self.element.removeAttribute("controls")

	def _getLoop(self):
		return True if self.element.hasAttribute("loop") else False

	def _setLoop(self, val):
		if val:
			self.element.setAttribute("loop", "")
		else:
			self.element.removeAttribute("loop")

	def _getMuted(self):
		return True if self.element.hasAttribute("muted") else False

	def _setMuted(self, val):
		if val:
			self.element.setAttribute("muted", "")
		else:
			self.element.removeAttribute("muted")

	def _getPreload(self):
		return self.element.preload

	def _setPreload(self, val):
		self.element.preload = val


# _attrRel ------------------------------------------------------------------------------------------------------------------

class _attrRel(object):
	def _getRel(self):
		return self.element.rel

	def _setRel(self, val):
		self.element.rel = val


# _attrSrc ------------------------------------------------------------------------------------------------------------------

class _attrSrc(object):
	def _getSrc(self):
		return self.element.src

	def _setSrc(self, val):
		self.element.src = val


# Svg ------------------------------------------------------------------------------------------------------------------

class _attrSvgViewBox(object):
	def _getViewBox(self):
		return self.element.viewBox

	def _setViewBox(self, val):
		self.element.setAttribute("viewBox", val)

	def _getPreserveAspectRatio(self):
		return self.element.preserveAspectRatio

	def _setPreserveAspectRatio(self, val):
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
	def _getFill(self):
		return self.element.fill

	def _setFill(self, val):
		self.element.setAttribute("fill", val)

	def _getStroke(self):
		return self.element.stroke

	def _setStroke(self, val):
		self.element.setAttribute("stroke", val)


class _isVoid(object):
	pass


########################################################################################################################
# HTML Elements
########################################################################################################################

# A --------------------------------------------------------------------------------------------------------------------

class A(Widget, _attrHref, _attrTarget, _attrMedia, _attrRel, _attrName):
	_baseClass = "a"

	def __init__(self, *args, **kwargs):
		super(A, self).__init__(*args, **kwargs)

	def _getDownload(self):
		"""
		The download attribute specifies the path to a download
		:returns: filename
		"""
		return self.element.download

	def _setDownload(self, val):
		"""
		The download attribute specifies the path to a download
		:param val: filename
		"""
		self.element.download = val


# Area -----------------------------------------------------------------------------------------------------------------

class Area(A, _attrAlt, _isVoid):
	_baseClass = "area"

	def __init__(self, *args, **kwargs):
		super(Area, self).__init__(*args, **kwargs)

	def _getCoords(self):
		return self.element.coords

	def _setCoords(self, val):
		self.element.coords = val

	def _getShape(self):
		return self.element.shape

	def _setShape(self, val):
		self.element.shape = val


# Audio ----------------------------------------------------------------------------------------------------------------

class Audio(Widget, _attrSrc, _attrMultimedia):
	_baseClass = "audio"

	def __init__(self, *args, **kwargs):
		super(Audio, self).__init__(*args, **kwargs)


# Bdo ------------------------------------------------------------------------------------------------------------------

class Bdo(Widget):
	_baseClass = "bdo"

	def __init__(self, *args, **kwargs):
		super(Bdo, self).__init__(*args, **kwargs)


# Blockquote -----------------------------------------------------------------------------------------------------------

class Blockquote(Widget):
	_baseClass = "blockquote"

	def __init__(self, *args, **kwargs):
		super(Blockquote, self).__init__(*args, **kwargs)

	def _getBlockquote(self):
		return self.element.blockquote

	def _setBlockquote(self, val):
		self.element.blockquote = val


# Body -----------------------------------------------------------------------------------------------------------------

class BodyCls(Widget):

	def __init__(self, *args, **kwargs):
		super(BodyCls, self).__init__(_wrapElem=domGetElementsByTagName("body")[0])
		self._isAttached = True


_body = None


def Body():
	global _body

	if _body is None:
		_body = BodyCls()

	return _body


# Canvas ---------------------------------------------------------------------------------------------------------------

class Canvas(Widget, _attrDimensions):
	_baseClass = "canvas"

	def __init__(self, *args, **kwargs):
		super(Canvas, self).__init__(*args, **kwargs)


# Command --------------------------------------------------------------------------------------------------------------

class Command(Widget, _attrLabel, _attrType, _attrDisabled, _attrChecked):
	_baseClass = "command"

	def __init__(self, *args, **kwargs):
		super(Command, self).__init__(*args, **kwargs)

	def _getIcon(self):
		return self.element.icon

	def _setIcon(self, val):
		self.element.icon = val

	def _getRadiogroup(self):
		return self.element.radiogroup

	def _setRadiogroup(self, val):
		self.element.radiogroup = val


# _Del -----------------------------------------------------------------------------------------------------------------

class _Del(Widget, _attrCite, _attrDatetime):
	_baseClass = "_del"

	def __init__(self, *args, **kwargs):
		super(_Del, self).__init__(*args, **kwargs)


# Dialog --------------------------------------------------------------------------------------------------------------

class Dialog(Widget):
	_baseClass = "dialog"

	def __init__(self, *args, **kwargs):
		super(Dialog, self).__init__(*args, **kwargs)

	def _getOpen(self):
		return (True if self.element.hasAttribute("open") else False)

	def _setOpen(self, val):
		if val == True:
			self.element.setAttribute("open", "")
		else:
			self.element.removeAttribute("open")


# Div ------------------------------------------------------------------------------------------------------------------

class Div(Widget):
	_baseClass = "div"

	def __init__(self, *args, **kwargs):
		super(Div, self).__init__(**kwargs)
		self.appendChild(args)


# Elements -------------------------------------------------------------------------------------------------------------


class Abbr(Widget):
	_baseClass = "abbr"

	def __init__(self, *args, **kwargs):
		super(Abbr, self).__init__(*args, **kwargs)


class Address(Widget):
	_baseClass = "address"

	def __init__(self, *args, **kwargs):
		super(Address, self).__init__(*args, **kwargs)


class Article(Widget):
	_baseClass = "article"

	def __init__(self, *args, **kwargs):
		super(Article, self).__init__(*args, **kwargs)


class Aside(Widget):
	_baseClass = "aside"

	def __init__(self, *args, **kwargs):
		super(Aside, self).__init__(*args, **kwargs)


class B(Widget):
	_baseClass = "b"

	def __init__(self, *args, **kwargs):
		super(B, self).__init__(*args, **kwargs)


class Bdi(Widget):
	_baseClass = "bdi"

	def __init__(self, *args, **kwargs):
		super(Bdi, self).__init__(*args, **kwargs)


class Br(Widget, _isVoid):
	_baseClass = "br"

	def __init__(self, *args, **kwargs):
		super(Br, self).__init__(*args, **kwargs)


class Caption(Widget):
	_baseClass = "caption"

	def __init__(self, *args, **kwargs):
		super(Caption, self).__init__(*args, **kwargs)


class Cite(Widget):
	_baseClass = "Cite"

	def __init__(self, *args, **kwargs):
		super(Cite, self).__init__(*args, **kwargs)


class Code(Widget):
	_baseClass = "code"

	def __init__(self, *args, **kwargs):
		super(Code, self).__init__(*args, **kwargs)


class Datalist(Widget):
	_baseClass = "datalist"

	def __init__(self, *args, **kwargs):
		super(Datalist, self).__init__(*args, **kwargs)


class Dfn(Widget):
	_baseClass = "dfn"

	def __init__(self, *args, **kwargs):
		super(Dfn, self).__init__(*args, **kwargs)


class Em(Widget):
	_baseClass = "em"

	def __init__(self, *args, **kwargs):
		super(Em, self).__init__(*args, **kwargs)


class Figcaption(Widget):
	_baseClass = "figcaption"

	def __init__(self, *args, **kwargs):
		super(Figcaption, self).__init__(*args, **kwargs)


class Figure(Widget):
	_baseClass = "figure"

	def __init__(self, *args, **kwargs):
		super(Figure, self).__init__(*args, **kwargs)


class Footer(Widget):
	_baseClass = "footer"

	def __init__(self, *args, **kwargs):
		super(Footer, self).__init__(*args, **kwargs)


class Header(Widget):
	_baseClass = "header"

	def __init__(self, *args, **kwargs):
		super(Header, self).__init__(*args, **kwargs)


class H1(Widget):
	_baseClass = "h1"

	def __init__(self, *args, **kwargs):
		super(H1, self).__init__(*args, **kwargs)


class H2(Widget):
	_baseClass = "h2"

	def __init__(self, *args, **kwargs):
		super(H2, self).__init__(*args, **kwargs)


class H3(Widget):
	_baseClass = "h3"

	def __init__(self, *args, **kwargs):
		super(H3, self).__init__(*args, **kwargs)


class H4(Widget):
	_baseClass = "h4"

	def __init__(self, *args, **kwargs):
		super(H4, self).__init__(*args, **kwargs)


class H5(Widget):
	_baseClass = "h5"

	def __init__(self, *args, **kwargs):
		super(H5, self).__init__(*args, **kwargs)


class H6(Widget):
	_baseClass = "h6"

	def __init__(self, *args, **kwargs):
		super(H6, self).__init__(*args, **kwargs)


class Hr(Widget, _isVoid):
	_baseClass = "hr"

	def __init__(self, *args, **kwargs):
		super(Hr, self).__init__(*args, **kwargs)


class I(Widget):
	_baseClass = "i"

	def __init__(self, *args, **kwargs):
		super(I, self).__init__(*args, **kwargs)


class Kdb(Widget):
	_baseClass = "kdb"

	def __init__(self, *args, **kwargs):
		super(Kdb, self).__init__(*args, **kwargs)


class Legend(Widget):
	_baseClass = "legend"

	def __init__(self, *args, **kwargs):
		super(Legend, self).__init__(*args, **kwargs)


class Mark(Widget):
	_baseClass = "mark"

	def __init__(self, *args, **kwargs):
		super(Mark, self).__init__(*args, **kwargs)


class Noscript(Widget):
	_baseClass = "noscript"

	def __init__(self, *args, **kwargs):
		super(Noscript, self).__init__(*args, **kwargs)


class P(Widget):
	_baseClass = "p"

	def __init__(self, *args, **kwargs):
		super(P, self).__init__(*args, **kwargs)


class Rq(Widget):
	_baseClass = "rq"

	def __init__(self, *args, **kwargs):
		super(Rq, self).__init__(*args, **kwargs)


class Rt(Widget):
	_baseClass = "rt"

	def __init__(self, *args, **kwargs):
		super(Rt, self).__init__(*args, **kwargs)


class Ruby(Widget):
	_baseClass = "ruby"

	def __init__(self, *args, **kwargs):
		super(Ruby, self).__init__(*args, **kwargs)


class S(Widget):
	_baseClass = "s"

	def __init__(self, *args, **kwargs):
		super(S, self).__init__(*args, **kwargs)


class Samp(Widget):
	_baseClass = "samp"

	def __init__(self, *args, **kwargs):
		super(Samp, self).__init__(*args, **kwargs)


class Section(Widget):
	_baseClass = "section"

	def __init__(self, *args, **kwargs):
		super(Section, self).__init__(*args, **kwargs)


class Small(Widget):
	_baseClass = "small"

	def __init__(self, *args, **kwargs):
		super(Small, self).__init__(*args, **kwargs)


class Strong(Widget):
	_baseClass = "strong"

	def __init__(self, *args, **kwargs):
		super(Strong, self).__init__(*args, **kwargs)


class Sub(Widget):
	_baseClass = "sub"

	def __init__(self, *args, **kwargs):
		super(Sub, self).__init__(*args, **kwargs)


class Summery(Widget):
	_baseClass = "summery"

	def __init__(self, *args, **kwargs):
		super(Summery, self).__init__(*args, **kwargs)


class Sup(Widget):
	_baseClass = "sup"

	def __init__(self, *args, **kwargs):
		super(Sup, self).__init__(*args, **kwargs)


class U(Widget):
	_baseClass = "u"

	def __init__(self, *args, **kwargs):
		super(U, self).__init__(*args, **kwargs)


class Var(Widget):
	_baseClass = "var"

	def __init__(self, *args, **kwargs):
		super(Var, self).__init__(*args, **kwargs)


class Wbr(Widget):
	_baseClass = "wbr"

	def __init__(self, *args, **kwargs):
		super(Wbr, self).__init__(*args, **kwargs)


# Embed ----------------------------------------------------------------------------------------------------------------

class Embed(Widget, _attrSrc, _attrType, _attrDimensions, _isVoid):
	_baseClass = "embed"

	def __init__(self, *args, **kwargs):
		super(Embed, self).__init__(*args, **kwargs)


# Form -----------------------------------------------------------------------------------------------------------------

class Button(_attrDisabled, Widget, _attrType, _attrForm, _attrAutofocus, _attrName, _attrValue, _attrFormhead):
	_baseClass = "button"

	def __init__(self, *args, **kwargs):
		_attrDisabled.__init__(self, *args, **kwargs)
		Widget.__init__(self, *args, **kwargs)
		_attrType.__init__(self, *args, **kwargs)
		_attrForm.__init__(self, *args, **kwargs)
		_attrAutofocus.__init__(self, *args, **kwargs)
		_attrName.__init__(self, *args, **kwargs)
		_attrValue.__init__(self, *args, **kwargs)
		_attrFormhead.__init__(self, *args, **kwargs)


class Fieldset(_attrDisabled, Widget, _attrForm, _attrName):
	_baseClass = "fieldset"

	def __init__(self, *args, **kwargs):
		_attrDisabled.__init__(self, *args, **kwargs)
		Widget.__init__(self, *args, **kwargs)
		_attrForm.__init__(self, *args, **kwargs)
		_attrName.__init__(self, *args, **kwargs)


class Form(Widget, _attrDisabled, _attrName, _attrTarget, _attrAutocomplete):
	_baseClass = "form"

	def __init__(self, *args, **kwargs):
		_attrDisabled.__init__(self, *args, **kwargs)
		Widget.__init__(self, *args, **kwargs)
		_attrName.__init__(self, *args, **kwargs)
		_attrTarget.__init__(self, *args, **kwargs)
		_attrAutocomplete.__init__(self, *args, **kwargs)

	def _getNovalidate(self):
		return (True if self.element.hasAttribute("novalidate") else False)

	def _setNovalidate(self, val):
		if val == True:
			self.element.setAttribute("novalidate", "")
		else:
			self.element.removeAttribute("novalidate")

	def _getAction(self):
		return self.element.action

	def _setAction(self, val):
		self.element.action = val

	def _getMethod(self):
		return self.element.method

	def _setMethod(self, val):
		self.element.method = val

	def _getEnctype(self):
		return self.element.enctype

	def _setEnctype(self, val):
		self.element.enctype = val

	def _getAccept_attrCharset(self):
		return getattr(self.element, "accept-_attrCharset")

	def _setAccept_attrCharset(self, val):
		self.element.setAttribute("accept-_attrCharset", val)


class Input(_attrDisabled, Widget, _attrType, _attrForm, _attrAlt, _attrAutofocus, _attrChecked,
				_attrIndeterminate, _attrName, _attrDimensions, _attrValue, _attrFormhead,
					_attrAutocomplete, _attrInputs, _attrMultiple, _attrSize, _attrSrc, _isVoid):
	_baseClass = "input"

	def __init__(self, *args, **kwargs):
		_attrDisabled.__init__(self, *args, **kwargs)
		Widget.__init__(self, *args, **kwargs)
		_attrType.__init__(self, *args, **kwargs)
		_attrForm.__init__(self, *args, **kwargs)
		_attrAlt.__init__(self, *args, **kwargs)
		_attrAutofocus.__init__(self, *args, **kwargs)
		_attrChecked.__init__(self, *args, **kwargs)
		_attrIndeterminate.__init__(self, *args, **kwargs)
		_attrName.__init__(self, *args, **kwargs)
		_attrDimensions.__init__(self, *args, **kwargs)
		_attrValue.__init__(self, *args, **kwargs)
		_attrFormhead.__init__(self, *args, **kwargs)
		_attrAutocomplete.__init__(self, *args, **kwargs)
		_attrInputs.__init__(self, *args, **kwargs)
		_attrMultiple.__init__(self, *args, **kwargs)
		_attrSize.__init__(self, *args, **kwargs)
		_attrSrc.__init__(self, *args, **kwargs)

	def _getAccept(self):
		return self.element.accept

	def _setAccept(self, val):
		self.element.accept = val

	def _getList(self):
		return self.element.list

	def _setList(self, val):
		self.element.list = val

	def _getMax(self):
		return self.element.max

	def _setMax(self, val):
		self.element.max = val

	def _getMin(self):
		return self.element.min

	def _setMin(self, val):
		self.element.min = val

	def _getPattern(self):
		return self.element.pattern

	def _setPattern(self, val):
		self.element.pattern = val

	def _getStep(self):
		return self.element.step

	def _setStep(self, val):
		self.element.step = val


class Label(Widget, _attrForm, _attrFor):
	_baseClass = "label"
	autoIdCounter = 0

	def __init__(self, txt="", forElem=None, *args, **kwargs):
		super(Label, self).__init__(*args, **kwargs)
		if txt:
			self.appendChild(TextNode(txt))
		if forElem:
			if not forElem["id"]:
				idx = Label.autoIdCounter
				Label.autoIdCounter += 1
				forElem["id"] = "label-autoid-for-{}".format(idx)
			self["for"] = forElem["id"]


class Optgroup(_attrDisabled, Widget, _attrLabel):
	_baseClass = "optgroup"

	def __init__(self, *args, **kwargs):
		_attrDisabled.__init__(self, *args, **kwargs)
		Widget.__init__(self, *args, **kwargs)
		_attrLabel.__init__(self, *args, **kwargs)


class Option(_attrDisabled, Widget, _attrLabel, _attrValue):
	_baseClass = "option"

	def __init__(self, txt="", *args, **kwargs):
		_attrDisabled.__init__(self, *args, **kwargs)
		Widget.__init__(self, *args, **kwargs)
		_attrLabel.__init__(self, *args, **kwargs)
		_attrValue.__init__(self, *args, **kwargs)

		if txt:
			self.appendChild(txt)

	def _getSelected(self):
		return (True if self.element.selected else False)

	# return( True if self.element.hasAttribute("selected") else False )
	def _setSelected(self, val):
		if val == True:
			self.element.selected = True
		else:
			self.element.selected = False


class Output(Widget, _attrForm, _attrName, _attrFor):
	_baseClass = "output"

	def __init__(self, *args, **kwargs):
		super(Output, self).__init__(*args, **kwargs)


class Select(_attrDisabled, Widget, _attrForm, _attrAutofocus, _attrName, _attrRequired, _attrMultiple, _attrSize):
	_baseClass = "select"

	def __init__(self, *args, **kwargs):
		_attrDisabled.__init__(self, *args, **kwargs)
		Widget.__init__(self, *args, **kwargs)
		_attrForm.__init__(self, *args, **kwargs)
		_attrAutofocus.__init__(self, *args, **kwargs)
		_attrName.__init__(self, *args, **kwargs)
		_attrRequired.__init__(self, *args, **kwargs)
		_attrMultiple.__init__(self, *args, **kwargs)
		_attrSize.__init__(self, *args, **kwargs)

	def _getSelectedIndex(self):
		return (self.element.selectedIndex)

	def _getOptions(self):
		return (self.element.options)


class Textarea(Widget, _attrDisabled, _attrForm, _attrAutofocus, _attrName, _attrInputs, _attrValue):
	_baseClass = "textarea"

	def __init__(self, *args, **kwargs):
		super(Textarea, self).__init__(*args, **kwargs)

	def _getCols(self):
		return self.element.cols

	def _setCols(self, val):
		self.element.cols = val

	def _getRows(self):
		return self.element.rows

	def _setRows(self, val):
		self.element.rows = val

	def _getWrap(self):
		return self.element.wrap

	def _setWrap(self, val):
		self.element.wrap = val


# Head -----------------------------------------------------------------------------------------------------------------

class HeadCls(Widget):

	def __init__(self, *args, **kwargs):
		super(HeadCls, self).__init__(_wrapElem=domGetElementsByTagName("head")[0])
		self._isAttached = True


_head = None


def Head():
	global _head
	if _head is None:
		_head = HeadCls()
	return _head


# Iframe ---------------------------------------------------------------------------------------------------------------

class Iframe(Widget, _attrSrc, _attrName, _attrDimensions):
	_baseClass = "iframe"

	def __init__(self, *args, **kwargs):
		super(Iframe, self).__init__(*args, **kwargs)

	def _getSandbox(self):
		return self.element.sandbox

	def _setSandbox(self, val):
		self.element.sandbox = val

	def _getSrcdoc(self):
		return self.element.src

	def _setSrcdoc(self, val):
		self.element.src = val

	def _getSeamless(self):
		return (True if self.element.hasAttribute("seamless") else False)

	def _setSeamless(self, val):
		if val == True:
			self.element.setAttribute("seamless", "")
		else:
			self.element.removeAttribute("seamless")


# Img ------------------------------------------------------------------------------------------------------------------

class Img(Widget, _attrSrc, _attrDimensions, _attrUsemap, _attrAlt, _isVoid):
	_baseClass = "img"

	def __init__(self, src=None, *args, **kwargs):
		super(Img, self).__init__(*args, **kwargs)
		if src is not None:
			self["src"] = src

	def _getCrossorigin(self):
		return self.element.crossorigin

	def _setCrossorigin(self, val):
		self.element.crossorigin = val

	def _getIsmap(self):
		return self.element.ismap

	def _setIsmap(self, val):
		self.element.ismap = val


# Ins ------------------------------------------------------------------------------------------------------------------

class Ins(Widget, _attrCite, _attrDatetime):
	_baseClass = "ins"

	def __init__(self, *args, **kwargs):
		super(Ins, self).__init__(*args, **kwargs)


# Keygen ---------------------------------------------------------------------------------------------------------------

class Keygen(Form, _attrAutofocus, _attrDisabled):
	_baseClass = "keygen"

	def __init__(self, *args, **kwargs):
		super(Keygen, self).__init__(*args, **kwargs)

	def _getChallenge(self):
		return (True if self.element.hasAttribute("challenge") else False)

	def _setChallenge(self, val):
		if val == True:
			self.element.setAttribute("challenge", "")
		else:
			self.element.removeAttribute("challenge")

	def _getKeytype(self):
		return self.element.keytype

	def _setKeytype(self, val):
		self.element.keytype = val


# Link -----------------------------------------------------------------------------------------------------------------

class Link(Widget, _attrHref, _attrMedia, _attrRel, _isVoid):
	_baseClass = "link"

	def __init__(self, *args, **kwargs):
		super(Link, self).__init__(*args, **kwargs)

	def _getSizes(self):
		return self.element.sizes

	def _setSizes(self, val):
		self.element.sizes = val


# List -----------------------------------------------------------------------------------------------------------------

class Ul(Widget):
	_baseClass = "ul"

	def __init__(self, *args, **kwargs):
		super(Ul, self).__init__(*args, **kwargs)


class Ol(Widget):
	_baseClass = "ol"

	def __init__(self, *args, **kwargs):
		super(Ol, self).__init__(*args, **kwargs)


class Li(Widget):
	_baseClass = "li"

	def __init__(self, child=None, *args, **kwargs):
		super(Li, self).__init__(*args, **kwargs)

		if child:
			self.appendChild(child)


class Dl(Widget):
	_baseClass = "dl"

	def __init__(self, *args, **kwargs):
		super(Dl, self).__init__(*args, **kwargs)


class Dt(Widget):
	_baseClass = "dt"

	def __init__(self, *args, **kwargs):
		super(Dt, self).__init__(*args, **kwargs)


class Dd(Widget):
	_baseClass = "dd"

	def __init__(self, *args, **kwargs):
		super(Dd, self).__init__(*args, **kwargs)


# Map ------------------------------------------------------------------------------------------------------------------

class Map(Label, _attrType):
	_baseClass = "map"

	def __init__(self, *args, **kwargs):
		super(Map, self).__init__(*args, **kwargs)


# Menu -----------------------------------------------------------------------------------------------------------------

class Menu(Widget):
	_baseClass = "menu"

	def __init__(self, *args, **kwargs):
		super(Menu, self).__init__(*args, **kwargs)


# Meta -----------------------------------------------------------------------------------------------------------------

class Meta(Widget, _attrName, _attrCharset, _isVoid):
	_baseClass = "meta"

	def __init__(self, *args, **kwargs):
		super(Meta, self).__init__(*args, **kwargs)

	def _getContent(self):
		return self.element.content

	def _setContent(self, val):
		self.element.content = val

	'''
	def _getHttpequiv(self):
		return self.element.http-equiv
	def _setHttpequiv(self,val):
		self.element.http-equiv=val
	'''


# Meter ----------------------------------------------------------------------------------------------------------------

class Meter(Form, _attrValue):
	_baseClass = "meter"

	def __init__(self, *args, **kwargs):
		super(Meter, self).__init__(*args, **kwargs)

	def _getHigh(self):
		return self.element.high

	def _setHigh(self, val):
		self.element.high = val

	def _getLow(self):
		return self.element.low

	def _setLow(self, val):
		self.element.low = val

	def _getMax(self):
		return self.element.max

	def _setMax(self, val):
		self.element.max = val

	def _getMin(self):
		return self.element.min

	def _setMin(self, val):
		self.element.min = val

	def _getOptimum(self):
		return self.element.optimum

	def _setOptimum(self, val):
		self.element.optimum = val


# Nav ------------------------------------------------------------------------------------------------------------------

class Nav(Widget):
	_baseClass = "nav"

	def __init__(self, *args, **kwargs):
		super(Nav, self).__init__(*args, **kwargs)


# Object -----------------------------------------------------------------------------------------------------------------

class Object(Form, _attrType, _attrName, _attrDimensions, _attrUsemap):
	_baseClass = "object"

	def __init__(self, *args, **kwargs):
		super(Object, self).__init__(*args, **kwargs)


# Param -----------------------------------------------------------------------------------------------------------------

class Param(Widget, _attrName, _attrValue, _isVoid):
	_baseClass = "param"

	def __init__(self, *args, **kwargs):
		super(Param, self).__init__(*args, **kwargs)


# Progress -------------------------------------------------------------------------------------------------------------

class Progress(Widget, _attrValue):
	_baseClass = "progress"

	def __init__(self, *args, **kwargs):
		super(Progress, self).__init__(*args, **kwargs)

	def _getMax(self):
		return self.element.max

	def _setMax(self, val):
		self.element.max = val


# Q --------------------------------------------------------------------------------------------------------------------

class Q(Widget, _attrCite):
	_baseClass = "q"

	def __init__(self, *args, **kwargs):
		super(Q, self).__init__(*args, **kwargs)


# Script ----------------------------------------------------------------------------------------------------------------

class Script(Widget, _attrSrc, _attrCharset):
	_baseClass = "script"

	def __init__(self, *args, **kwargs):
		super(Script, self).__init__(*args, **kwargs)

	def _getAsync(self):
		return (True if self.element.hasAttribute("async") else False)

	def _setAsync(self, val):
		if val == True:
			self.element.setAttribute("async", "")
		else:
			self.element.removeAttribute("async")

	def _getDefer(self):
		return (True if self.element.hasAttribute("defer") else False)

	def _setDefer(self, val):
		if val == True:
			self.element.setAttribute("defer", "")
		else:
			self.element.removeAttribute("defer")


# Source ---------------------------------------------------------------------------------------------------------------

class Source(Widget, _attrMedia, _attrSrc, _isVoid):
	_baseClass = "source"

	def __init__(self, *args, **kwargs):
		super(Source, self).__init__(*args, **kwargs)


# Span -----------------------------------------------------------------------------------------------------------------

class Span(Widget):
	_baseClass = "span"

	def __init__(self, *args, **kwargs):
		super(Span, self).__init__(**kwargs)
		self.appendChild(args)


# Style ----------------------------------------------------------------------------------------------------------------

class Style(Widget, _attrMedia):
	_baseClass = "style"

	def __init__(self, *args, **kwargs):
		super(Style, self).__init__(*args, **kwargs)

	def _getScoped(self):
		return (True if self.element.hasAttribute("scoped") else False)

	def _setScoped(self, val):
		if val == True:
			self.element.setAttribute("scoped", "")
		else:
			self.element.removeAttribute("scoped")


# SVG ------------------------------------------------------------------------------------------------------------------

class Svg(Widget, _attrSvgViewBox, _attrSvgDimensions, _attrSvgTransform):
	_baseClass = "svg"
	_namespace = "SVG"

	def __init__(self, version=None, viewBox=None, heigth=None, width=None, *args, **kwargs):
		super(Svg, self).__init__(*args, **kwargs)

	def _getVersion(self):
		return self.element.version

	def _setVersion(self, val):
		self.element.setAttribute("version", val)

	def _getXmlns(self):
		return self.element.xmlns

	def _setXmlns(self, val):
		self.element.setAttribute("xmlns", val)


class SvgCircle(Widget, _attrSvgTransform, _attrSvgDimensions):
	_baseClass = "circle"
	_namespace = "SVG"

	def __init__(self, *args, **kwargs):
		super(SvgCircle, self).__init__(*args, **kwargs)


class SvgEllipse(Widget, _attrSvgTransform, _attrSvgDimensions):
	_baseClass = "ellipse"
	_namespace = "SVG"

	def __init__(self, *args, **kwargs):
		super(SvgEllipse, self).__init__(*args, **kwargs)


class SvgG(Widget, _attrSvgTransform, _attrSvgStyles):
	_baseClass = "g"
	_namespace = "SVG"

	def __init__(self, *args, **kwargs):
		super(SvgG, self).__init__(*args, **kwargs)

	def _getSvgTransform(self):
		return self.element.transform

	def _setSvgTransform(self, val):
		self.element.setAttribute("transform", val)


class SvgImage(Widget, _attrSvgViewBox, _attrSvgDimensions, _attrSvgTransform, _attrSvgXlink):
	_baseClass = "image"
	_namespace = "SVG"

	def __init__(self, *args, **kwargs):
		super(SvgImage, self).__init__(*args, **kwargs)


class SvgLine(Widget, _attrSvgTransform, _attrSvgPoints):
	_baseClass = "line"
	_namespace = "SVG"

	def __init__(self, *args, **kwargs):
		super(SvgLine, self).__init__(*args, **kwargs)


class SvgPath(Widget, _attrSvgTransform):
	_baseClass = "path"
	_namespace = "SVG"

	def __init__(self, *args, **kwargs):
		super(SvgPath, self).__init__(*args, **kwargs)

	def _getD(self):
		return self.element.d

	def _setD(self, val):
		self.element.setAttribute("d", val)

	def _getPathLength(self):
		return self.element.pathLength

	def _setPathLength(self, val):
		self.element.setAttribute("pathLength", val)


class SvgPolygon(Widget, _attrSvgTransform, _attrSvgPoints):
	_baseClass = "polygon"
	_namespace = "SVG"

	def __init__(self, *args, **kwargs):
		super(SvgPolygon, self).__init__(*args, **kwargs)


class SvgPolyline(Widget, _attrSvgTransform, _attrSvgPoints):
	_baseClass = "polyline"
	_namespace = "SVG"

	def __init__(self, *args, **kwargs):
		super(SvgPolyline, self).__init__(*args, **kwargs)


class SvgRect(Widget, _attrSvgDimensions, _attrSvgTransform, _attrSvgStyles):
	_baseClass = "rect"
	_namespace = "SVG"

	def __init__(self, *args, **kwargs):
		super(SvgRect, self).__init__(*args, **kwargs)


class SvgText(Widget, _attrSvgDimensions, _attrSvgTransform, _attrSvgStyles):
	_baseClass = "text"
	_namespace = "SVG"

	def __init__(self, text="", *args, **kwargs):
		super(SvgText, self).__init__(*args, **kwargs)
		self.element.appendChild(domCreateTextNode(text))


# Table ----------------------------------------------------------------------------------------------------------------


class Tr(Widget):
	_baseClass = "tr"

	def _getRowspan(self):
		span = self.element.getAttribute("rowspan")
		return span if span else 1

	def _setRowspan(self, span):
		assert span >= 1, "span may not be negative"
		self.element.setAttribute("rowspan", span)
		return self


class Td(Widget):
	_baseClass = "td"

	def __init__(self, *args, **kwargs):
		super(Td, self).__init__(**kwargs)
		self.appendChild(args)

	def _getColspan(self):
		span = self.element.getAttribute("colspan")
		return span if span else 1

	def _setColspan(self, span):
		assert span >= 1, "span may not be negative"
		self.element.setAttribute("colspan", span)
		return self

	def _getRowspan(self):
		span = self.element.getAttribute("rowspan")
		return span if span else 1

	def _setRowspan(self, span):
		assert span >= 1, "span may not be negative"
		self.element.setAttribute("rowspan", span)
		return self


class Th(Td):
	_baseClass = "th"


class Thead(Widget):
	_baseClass = "thead"


class Tbody(Widget):
	_baseClass = "tbody"


class ColWrapper(object):
	def __init__(self, parentElem, *args, **kwargs):
		super(ColWrapper, self).__init__(*args, **kwargs)
		self.parentElem = parentElem

	def __getitem__(self, item):
		assert isinstance(item, int), "Invalid col-number. Expected int, got {}".format(str(type(item)))
		if item < 0 or item > len(self.parentElem._children):
			return None

		return self.parentElem._children[item]

	def __setitem__(self, key, value):
		col = self[key]
		assert col is not None, "Cannot assign widget to invalid column"

		col.removeAllChildren()

		if isinstance(value, list) or isinstance(value, tuple):
			for el in value:
				if isinstance(el, Widget) or isinstance(el, TextNode):
					col.appendChild(value)

		elif isinstance(value, Widget) or isinstance(value, TextNode):
			col.appendChild(value)


class RowWrapper(object):
	def __init__(self, parentElem, *args, **kwargs):
		super(RowWrapper, self).__init__(*args, **kwargs)
		self.parentElem = parentElem

	def __getitem__(self, item):
		assert isinstance(item, int), "Invalid row-number. Expected int, got {}".format(str(type(item)))
		if item < 0 or item > len(self.parentElem._children):
			return None

		return ColWrapper(self.parentElem._children[item])


class Table(Widget):
	_baseClass = "table"

	def __init__(self, *args, **kwargs):
		super(Table, self).__init__(*args, **kwargs)
		self.head = Thead()
		self.body = Tbody()
		self.appendChild(self.head)
		self.appendChild(self.body)

	def prepareRow(self, row):
		assert row >= 0, "Cannot create rows with negative index"

		for child in self.body._children:
			row -= child["rowspan"]
			if row < 0:
				return

		while row >= 0:
			self.body.appendChild(Tr())
			row -= 1

	def prepareCol(self, row, col):
		assert col >= 0, "Cannot create cols with negative index"
		self.prepareRow(row)

		for rowChild in self.body._children:
			row -= rowChild["rowspan"]

			if row < 0:
				for colChild in rowChild._children:
					col -= colChild["colspan"]
					if col < 0:
						return

				while col >= 0:
					rowChild.appendChild(Td())
					col -= 1

				return

	def prepareGrid(self, rows, cols):
		for row in range(self.getRowCount(), self.getRowCount() + rows):
			self.prepareCol(row, cols)

	def clear(self):
		for row in self.body._children[:]:

			for col in row._children[:]:
				row.removeChild(col)

			self.body.removeChild(row)

	def _getCell(self):
		return RowWrapper(self.body)

	def getRowCount(self):
		cnt = 0

		for tr in self.body._children:
			cnt += tr["rowspan"]

		return cnt


# Time -----------------------------------------------------------------------------------------------------------------

class Time(Widget, _attrDatetime):
	_baseClass = "time"

	def __init__(self, *args, **kwargs):
		super(Time, self).__init__(*args, **kwargs)


# Track ----------------------------------------------------------------------------------------------------------------

class Track(Label, _attrSrc, _isVoid):
	_baseClass = "track"

	def __init__(self, *args, **kwargs):
		super(Track, self).__init__(*args, **kwargs)

	def _getKind(self):
		return self.element.kind

	def _setKind(self, val):
		self.element.kind = val

	def _getSrclang(self):
		return self.element.srclang

	def _setSrclang(self, val):
		self.element.srclang = val

	def _getDefault(self):
		return (True if self.element.hasAttribute("default") else False)

	def _setDefault(self, val):
		if val == True:
			self.element.setAttribute("default", "")
		else:
			self.element.removeAttribute("default")


# Video ----------------------------------------------------------------------------------------------------------------

class Video(Widget, _attrSrc, _attrDimensions, _attrMultimedia):
	_baseClass = "video"

	def __init__(self, *args, **kwargs):
		super(Video, self).__init__(*args, **kwargs)

	def _getPoster(self):
		return self.element.poster

	def _setPoster(self, val):
		self.element.poster = val


########################################################################################################################
# Utilities
########################################################################################################################

def unescape(val, maxLength=0):
	"""
		Unquotes several HTML-quoted characters in a string.

		:param val: The value to be unescaped.
		:type val: str

		:param maxLength: Cut-off after maxLength characters.
				A value of 0 means "unlimited". (default)
		:type maxLength: int

		:returns: The unquoted string.
		:rtype: str
	"""
	val = val \
		.replace("&lt;", "<") \
		.replace("&gt;", ">") \
		.replace("&quot;", "\"") \
		.replace("&#39;", "'")

	if maxLength > 0:
		return val[0:maxLength]

	return val


def doesEventHitWidgetOrParents(event, widget):
	"""
		Test if event 'event' hits widget 'widget' (or *any* of its parents)
	"""
	while widget:
		if event.target == widget.element:
			return True

		widget = widget.parent()

	return False


def doesEventHitWidgetOrChildren(event, widget):
	"""
		Test if event 'event' hits widget 'widget' (or *any* of its children)
	"""
	if event.target == widget.element:
		return True

	for child in widget._children:
		if doesEventHitWidgetOrChildren(event, child):
			return True

	return False


def textToHtml(node, text):
	"""
	Generates html nodes from text by splitting text into content and into
	line breaks html5.Br.

	:param node: The node where the nodes are appended to.
	:param text: The text to be inserted.
	"""

	for (i, part) in enumerate(text.split("\n")):
		if i > 0:
			node.appendChild(Br())

		node.appendChild(TextNode(part))


def parseInt(s, ret=0):
	"""
	Parses a value as int
	"""
	if not isinstance(s, str):
		return int(s)
	elif s:
		if s[0] in "+-":
			ts = s[1:]
		else:
			ts = s

		if ts and all([_ in "0123456789" for _ in ts]):
			return int(s)

	return ret


def parseFloat(s, ret=0.0):
	"""
	Parses a value as float.
	"""
	if not isinstance(s, str):
		return float(s)
	elif s:
		if s[0] in "+-":
			ts = s[1:]
		else:
			ts = s

		if ts and ts.count(".") <= 1 and all([_ in ".0123456789" for _ in ts]):
			return float(s)

	return ret


########################################################################################################################
# Keycodes
########################################################################################################################

def getKey(event):
	"""
	Returns the Key Identifier of the given event

	Available Codes: https://www.w3.org/TR/2006/WD-DOM-Level-3-Events-20060413/keyset.html#KeySet-Set
	"""
	if hasattr(event, "key"):
		return event.key

	elif hasattr(event, "keyIdentifier"):
		if event.keyIdentifier in ["Esc", "U+001B"]:
			return "Escape"
		else:
			return event.keyIdentifier

	return None


def isArrowLeft(event):
	return getKey(event) in ["ArrowLeft", "Left"]

def isArrowUp(event):
	return getKey(event) in ["ArrowUp", "Up"]

def isArrowRight(event):
	return getKey(event) in ["ArrowRight", "Right"]

def isArrowDown(event):
	return getKey(event) in ["ArrowDown", "Down"]

def isEscape(event):
	return getKey(event) == "Escape"

def isReturn(event):
	return getKey(event) == "Enter"

def isControl(event): # The Control (Ctrl) key.
	return getKey(event) == "Control"

def isShift(event):
	return getKey(event) == "Shift"


########################################################################################################################
# HTML parser
########################################################################################################################

# Global variables required by HTML parser
__tags = None
__domParser = None


def registerTag(tagName, widgetClass):
	assert issubclass(widgetClass, Widget), "widgetClass must be a sub-class of Widget!"
	global __tags

	if __tags is None:
		_buildTags()

	attr = []

	for fname in dir(widgetClass):
		if fname.startswith("_set"):
			attr.append(fname[4:].lower())

	__tags[tagName.lower()] = (widgetClass, attr)


def _buildTags(debug=False):
	"""
	Generates a dictionary of all to the html5-library
	known tags and their associated objects and attributes.
	"""
	global __tags

	if __tags is not None:
		return

	if __tags is None:
		__tags = {}

	for cname in globals().keys():
		if cname.startswith("_"):
			continue

		cl = globals()[cname]

		try:
			if not issubclass(cl, Widget):
				continue
		except:
			continue

		registerTag(cname, cl)

	if debug:
		for tag in sorted(__tags.keys()):
			print("{}: {}".format(tag, ", ".join(sorted(__tags[tag][1]))))


def parseHTML(html, debug=False):
	"""
	Parses the provided HTML-code according to the objects defined in the html5-library.
	"""

	def convertEncodedText(txt):
		"""
		Convert HTML-encoded text into decoded string.

		The reason for this function is the handling of HTML entities, which is not
		properly supported by native JavaScript.

		We use the browser's DOM parser to to this, according to
		https://stackoverflow.com/questions/3700326/decode-amp-back-to-in-javascript

		:param txt: The encoded text.
		:return: The decoded text.
		"""
		global __domParser

		if jseval is None:
			return txt

		if __domParser is None:
			__domParser = jseval("new DOMParser")

		dom = __domParser.parseFromString("<!doctype html><body>" + str(txt), "text/html")
		return dom.body.textContent

	def scanWhite(l):
		"""
		Scan and return whitespace.
		"""

		ret = ""
		while l and l[0] in " \t\r\n":
			ret += l.pop(0)

		return ret

	def scanWord(l):
		"""
		Scan and return a word.
		"""

		ret = ""
		while l and l[0] not in " \t\r\n" + "<>=\"'":
			ret += l.pop(0)

		return ret

	stack = []

	# Obtain tag descriptions, if not already done!
	global __tags

	if __tags is None:
		_buildTags(debug=debug)

	# Prepare stack and input
	stack.append((None, None, []))
	html = [ch for ch in html]

	# Parse
	while html:
		tag = None
		text = ""

		# Auto-close void elements (_isVoid), e.g. <hr>, <br>, etc.
		while stack and stack[-1][0] and issubclass(__tags[stack[-1][0]][0], _isVoid):
			stack.pop()

		if not stack:
			break

		parent = stack[-1][2]

		while html:
			# print("html", html)
			# print(stack)

			ch = html.pop(0)

			# Comment
			if html and ch == "<" and "".join(html[:3]) == "!--":
				html = html[3:]
				while html and "".join(html[:3]) != "-->":
					html.pop(0)

				html = html[3:]

			# Opening tag
			elif html and ch == "<" and html[0] != "/":
				tag = scanWord(html)
				if tag.lower() in __tags:
					break

				text += ch + tag

			# Closing tag
			elif html and stack[-1][0] and ch == "<" and html[0] == "/":
				junk = ch
				junk += html.pop(0)

				tag = scanWord(html)
				junk += tag

				# print("/", tag.lower(), stack[-1][1].lower())
				if stack[-1][0] == tag.lower():
					junk += scanWhite(html)
					if html and html[0] == ">":
						html.pop(0)
						stack.pop()
						tag = None
						break

				text += junk
				tag = None

			else:
				text += ch

		# Append plain text (if not only whitespace)
		if (text and ((len(text) == 1 and text in ["\t "])
					  or not all([ch in " \t\r\n" for ch in text]))):
			# print("text", text)
			parent.append(convertEncodedText(text))

		# Create tag
		if tag:
			tag = tag.lower()
			# print("tag", tag)

			elem = (tag, {}, [])

			stack.append(elem)
			parent.append(elem)

			while html:
				scanWhite(html)
				if not html:
					break

				# End of tag >
				if html[0] == ">":
					html.pop(0)
					break

				# Closing tag at end />
				elif html[0] == "/":
					html.pop(0)
					scanWhite(html)

					if html[0] == ">":
						stack.pop()
						html.pop(0)
						break

				att = scanWord(html)
				att = att.lower()  # fixme: Transcrypt bug when combined with line above?
				val = att

				if not att:
					html.pop(0)
					continue

				if att in __tags[tag][1] or att in ["[name]", "style", "disabled", "hidden"] or att.startswith("data-"):
					scanWhite(html)
					if html[0] == "=":
						html.pop(0)
						scanWhite(html)

						if html[0] in "\"'":
							ch = html.pop(0)

							val = ""
							while html and html[0] != ch:
								val += html.pop(0)

							html.pop(0)

					if att not in elem[1]:
						elem[1][att] = val
					else:
						elem[1][att] += " " + val

				continue

	while stack and stack[-1][0]:
		stack.pop()

	return stack[0][2]


def fromHTML(html, appendTo=None, bindTo=None, debug=False, vars=None):
	"""
	Parses the provided HTML code according to the objects defined in the html5-library.
	html can also be pre-compiled by `parseHTML()` so that it executes faster.

	Constructs all objects as DOM nodes. The first level is chained into appendTo.
	If no appendTo is provided, appendTo will be set to html5.Body().

	If bindTo is provided, objects are bound to this widget.

	```python
	import html5

	div = html5.Div()
	html5.parse.fromHTML('''
		<div>Yeah!
			<a href="hello world" [name]="myLink" class="trullman bernd" disabled>
			hah ala malla" bababtschga"
			<img src="/static/images/icon_home.svg" style="background-color: red;"/>st
			<em>ah</em>ralla <i>malla tralla</i> da
			</a>lala
		</div>''', div)

	div.myLink.appendChild("appended!")
	```
	"""

	# Handle defaults
	if appendTo is None:
		appendTo = Body()

	if bindTo is None:
		bindTo = appendTo

	if isinstance(html, str):
		html = parseHTML(html, debug=debug)

	def replaceVars(txt):
		if vars:
			for var, val in vars.items():
				txt = txt.replace("{{%s}}" % var, val)

		return txt

	def interpret(parent, items):
		for item in items:
			if isinstance(item, str):
				parent.appendChild(TextNode(replaceVars(item)))
				continue

			tag = item[0]
			atts = item[1]
			children = item[2]

			# Special handling for tables: A "thead" and "tbody" are already part of table!
			if tag in ["thead", "tbody"] and isinstance(parent, Table):
				wdg = getattr(parent, tag[1:])

			# Usual way: Construct new element and chain it into the parent.
			else:
				wdg = __tags[tag][0]()

			for att, val in atts.items():
				val = replaceVars(val)

				if att == "[name]":
					# Allow disable binding!
					if not bindTo:
						continue

					for name in val.split():
						if name in dir(appendTo):
							print("Cannot assign name '{}' because it already exists in {}".format(val, appendTo))

						elif not (any([name.startswith(x) for x in
									   "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" + "_"])
								  and all(
									[x in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" + "0123456789" + "_"
									 for x in name[1:]])):
							print("Cannot assign name '{}' because it contains invalid characters".format(name))

						else:
							setattr(bindTo, name, wdg)

							if debug:
								print("name '{}' assigned to {}".format(name, bindTo))

				elif att == "class":
					# print(tag, att, val.split())
					wdg.addClass(*val.split())

				elif att == "disabled":
					# print(tag, att, val)
					if val == "disabled":
						wdg.disable()

				elif att == "hidden":
					# print(tag, att, val)
					if val == "hidden":
						wdg.hide()

				elif att == "style":
					for dfn in val.split(";"):
						if ":" not in dfn:
							continue

						att, val = dfn.split(":", 1)

						# print(tag, "style", att.strip(), val.strip())
						wdg["style"][att.strip()] = val.strip()

				elif att.startswith("data-"):
					wdg[att[5:]] = val

				else:
					wdg[att] = val

			interpret(wdg, children)

			if not wdg.parent():
				parent.appendChild(wdg)

	interpret(appendTo, html)

	return html #return compiled HTML (for optional reuse)


if __name__ == '__main__':
	print(globals())
