# html5

**html5** is a HTML5-DOM library that has been written in Python.

## About

This library serves as a toolkit for writing DOM-oriented web-apps using the
Python programming language.

The most prominent software completely established on this library is the
[vi](https://github.com/viur-framework/vi/), the visual administration interface
for ViUR-based applications.

[ViUR](https://www.viur.is) is a free software development framework for the
Google App Engine™ platform.

## Prerequisites

Currently works with [PyJS](https://github.com/pyjs/pyjs), a Python-to-JavaScript transpiling framework.

## Quick Start

Let's create a simple game app!

```python
import html5, pyjd

class game(html5.Div):
	def __init__(self, *args, **kwargs):
		super(game, self).__init__()
		self.addClass("wrap")
		self.sinkEvent("onChange")

		html5.parse.fromHTML(
		"""
		<div class="wrap">
			<div class="left">
				<label>
					Your Name:
					<input [name]="myInput" type="text" placeholder="Name">
				</label>
			</div>
			<div class="right">
				<h1>Hello <span [name]="mySpan" class="name">Enter Name</span>!</h1>
			</div>
		</div>
		""", self)

	def onChange(self, event):
		if html5.utils.doesEventHitWidgetOrChildren(event, self.myInput):
			self.mySpan.removeAllChildren()
			self.mySpan.appendChild(self.myInput["value"])

if __name__ == '__main__':
	pyjd.setup()
	html5.Body().appendChild(game())
	pyjd.run()
```

Just compile it with

	pyjsbuild game.py
