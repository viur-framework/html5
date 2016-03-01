
def createAttribute(tag, ns=None):
    """
        Creates a new HTML/SVG/... attribute
 		:param ns: the namespace. Default: HTML. Possibble values: HTML, SVG, XBL, XUL
   """
    # print("createAttribute:", tag)
    if ns is None or ns not in ["SVG", "XBL", "XUL"]:
        return(eval("window.top.document.createAttribute(\"%s\")" % tag))
    if ns=="SVG":
        uri = "http://www.w3.org/2000/svg"
    elif ns=="XBL":
        uri = "http://www.mozilla.org/xbl"
    elif ns=="XUL":
        uri = "http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul"
    return(eval('''window.top.document.createAttributeNS("{}", "{}")'''.format(uri, tag)))


def createElement(element, ns=None):
    """
        Creates a new HTML/SVG/... tag
  		:param ns: the namespace. Default: HTML. Possibble values: HTML, SVG, XBL, XUL
   """
    # print("createElement:", element)
    if ns is None or ns not in ["SVG", "XBL", "XUL"]:
        return(eval("window.top.document.createElement(\"%s\")" % element))
    if ns=="SVG":
        uri = "http://www.w3.org/2000/svg"
    elif ns=="XBL":
        uri = "http://www.mozilla.org/xbl"
    elif ns=="XUL":
        uri = "http://www.mozilla.org/keymaster/gatekeeper/there.is.only.xul"
    return(eval('''window.top.document.createElementNS("{}", "{}")'''.format(uri, element)))


def getElementById(idTag):
    return(eval("window.top.document.getElementById(\"%s\")" % idTag))

def getElementsByTagName( tagName ):
    doc = eval("window.top.document");
    res = []
    htmlCol = doc.getElementsByTagName(tagName)
    for x in range( 0, htmlCol.length):
        res.append(htmlCol.item(x))
    return( res )
