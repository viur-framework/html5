#-*- coding: utf-8 -*-
import html5, string

def _buildDescription():
	"""
	Generates a dictionary of all to the html5-library
	known tags and their associated objects and attributes.
	"""
	tags = {}

	for cname in dir(html5):
		cl = getattr(html5, cname)
		try:

			inst = cl()
			if cname != "Body" and isinstance(inst, html5.Widget):
				attr = []

				for fname in dir(inst):
					if fname.startswith("_set"):
						attr.append(fname[4:].lower())

				tags[cname.lower()] = (cl, attr)

		except:
			pass

	for tag in sorted(tags.keys()):
		print("%s: %s" % (tag, ", ".join(sorted(tags[tag][1]))))

	return tags

# Globally hold tag description, which is built once.
_tags = None

def fromHTML(html, root = None):
	"""
	Parses the provided HTML code according to the objects defined in the html5-library.

	Constructs all objects as DOM nodes. The first level is chained into root.
	If no root is provided, root will be set to html5.Body().

	The HTML elements are parsed for notations of kind [name]="ident", making
	the corresponding instance available to the widget as widget.ident in the
	Python code.

	Example:

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

	def scanWhite(l):
		"""
		Scan and return whitespace.
		"""

		ret = ""
		while l and l[0] in "\r\n\t ":
			ret += l.pop(0)

		return ret

	def scanWord(l):
		"""
		Scan and return a word.
		"""

		ret = ""
		while l and l[0] not in "\r\n\t <>=\"'":
			ret += l.pop(0)

		return ret

	global _tags
	stack = []

	if _tags is None:
		_tags = _buildDescription()

	if root is None:
		root = html5.Body()

	stack.append((root, None))
	html = [ch for ch in html]

	while html:
		tag = None
		text = ""

		while stack and stack[-1][1] in ["br", "input", "img"]:
			stack.pop()

		if not stack:
			break

		parent = stack[-1][0]

		while html:
			#print("html", html)
			#print(stack)

			ch = html.pop(0)

			# Opening tag
			if html and ch == "<" and html[0] != "/":
				tag = scanWord(html)
				if tag.lower() in _tags:
					break

				text += ch + tag

			# Closing tag
			elif html and stack[-1][1] and ch == "<" and html[0] == "/":
				junk = ch
				junk += html.pop(0)

				tag = scanWord(html)
				junk += tag

				print("/", tag.lower(), stack[-1][1].lower())
				if stack[-1][1].lower() == tag.lower():
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

		if text:
			print("text", text)
			parent.appendChild(html5.TextNode(text))

		if tag:
			wdg = _tags[tag][0]()

			parent.appendChild(wdg)
			stack.append((wdg, tag))

			print("tag", tag)

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


				att = scanWord(html).lower()
				val = att

				if not att:
					html.pop(0)
					continue

				if att in _tags[tag][1] or att in ["[name]", "style"]:
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

					if att == "[name]":
						if val in dir(root):
							print("Cannot assign name '%s' because it already exists in %r" % (val, root))

						elif not (any([val.startswith(x) for x in string.letters + "_"])
									and all([x in string.letters + string.digits + "_" for x in val[1:]])):
							print("Cannot assign name '%s' because it contains invalid characters" % val)

						else:
							setattr(root, val, wdg)
							print("Name '%s' assigned to %r" % (val, root))

					elif att == "class":
						print(tag, att, val.split())
						stack[-1][0].addClass(*val.split())

					elif att == "style":
						for dfn in val.split(";"):
							if not ":" in dfn:
								continue

							att, val = dfn.split(":", 1)

							print(tag, "style", att.strip(), val.strip())
							stack[-1][0]["style"][att.strip()] = val.strip()

					else:
						print(tag, att, val)
						stack[-1][0][att] = val

				continue
