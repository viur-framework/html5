from html5.widget import Widget
from html5.style import Style
from html5.html5Attr.svg import ViewBox, Dimensions, Styles, Transform, Points, Xlink
from html5.html5Attr.href import Href

class Svg(Widget, ViewBox, Dimensions, Transform):
    _baseClass = "svg"
    _namespace = "SVG"

    def __init__(self, version=None, viewBox=None, heigth=None, width=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _getVersion(self):
        return self.element.version
    def _setVersion(self,val):
        self.element.setAttribute("version", val)

    def _getXmlns(self):
        return self.element.xmlns
    def _setXmlns(self,val):
        self.element.setAttribute("xmlns", val)

class SvgCircle(Widget, Transform, Dimensions):
    _baseClass = "circle"
    _namespace = "SVG"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class SvgEllipse(Widget, Transform, Dimensions):
    _baseClass = "ellipse"
    _namespace = "SVG"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class SvgG(Widget, Transform, Styles):
    _baseClass = "g"
    _namespace = "SVG"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _getTransform(self):
        return self.element.transform
    def _setTransform(self,val):
        self.element.setAttribute("transform", val)

class SvgImage(Widget, ViewBox, Dimensions, Transform, Xlink):
    _baseClass = "image"
    _namespace = "SVG"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class SvgLine(Widget, Transform, Points):
    _baseClass = "line"
    _namespace = "SVG"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class SvgPath(Widget, Transform):
    _baseClass = "path"
    _namespace = "SVG"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _getD(self):
        return self.element.d
    def _setD(self,val):
        self.element.setAttribute("d", val)

    def _getPathLength(self):
        return self.element.pathLength
    def _setPathLength(self,val):
        self.element.setAttribute("pathLength", val)


class SvgPolygon(Widget, Transform, Points):
    _baseClass = "polygon"
    _namespace = "SVG"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class SvgPolyline(Widget, Transform, Points):
    _baseClass = "polyline"
    _namespace = "SVG"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class SvgRect(Widget, Dimensions, Transform, Styles):
    _baseClass = "rect"
    _namespace = "SVG"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class SvgText(Widget, Dimensions, Transform, Styles):
    _baseClass = "text"
    _namespace = "SVG"

    def __init__(self, text="",  *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.element.appendChild(eval("document.createTextNode('{}')".format(text)))
