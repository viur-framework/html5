from html5.widget import Widget

class Bdo( Widget ):
    _baseClass = "bdo"

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs )