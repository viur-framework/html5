# -*- coding: utf-8 -*-
import html5

def unescape(val, maxLength = 0):
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
		print(node, i, part)
		if i > 0:
			node.appendChild(html5.Br())

		node.appendChild(html5.TextNode(part))
