from html5.widget import Widget

class Div(Widget):
    _baseClass = "div"

    def __init__(self, *args, **kwargs):
        super(Div, self).__init__(**kwargs)
        self.appendChild(args)
