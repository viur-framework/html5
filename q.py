from html5.widget import Widget
from html5.html5Attr.cite import Cite
class Q( Widget,Cite ):
    _baseClass = "q"

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs )


