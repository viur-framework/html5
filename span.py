from html5.widget import Widget

class Span(Widget):
    _baseClass = "span"

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.appendChild(args)
