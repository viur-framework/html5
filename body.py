# -*- coding: utf-8 -*-
from html5.widget import Widget

class BodyCls(Widget):

	def __init__( self, *args, **kwargs ):
		super().__init__(_wrapElem=document.getElementsByTagName("body")[0])
		self._isAttached = True

_body = None

def Body():
	global _body

	if _body is None:
		_body = BodyCls()

	return _body
