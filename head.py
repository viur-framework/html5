from html5.widget import Widget
from html5 import document

class HeadCls( Widget ):

	def __init__( self, *args, **kwargs ):
		elem = document
		super(HeadCls, self).__init__(_wrapElem=document.getElementsByTagName("head")[0])
		self._isAttached = True

_head = None
def Head():
	global _head
	if _head is None:
		_head = HeadCls()
	return _head
