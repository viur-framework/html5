# ViUR html5

**html5** is a HTML5-DOM library that has been written in Python.

## About

This library serves as a DOM-toolkit for writing HTML5 web-apps using the Python programming language.

The most prominent software completely implemented using this library is [ViUR vi](https://github.com/viur-framework/vi/), the visual administration interface for ViUR-based applications.

[ViUR](https://www.viur.is) is a free software development framework for the [Google App Engine](https://appengine.google.com).

## Prerequisites

This library currently works with [PyJS](https://github.com/pyjs/pyjs), a Python-to-JavaScript transpiling framework.

We're also working on a Python 3 port to run with [pyodide](https://github.com/iodide-project/pyodide).

## Quick Start

Let's create a simple game app!

```python
import html5, pyjd

class game(html5.Div):
	def __init__(self, *args, **kwargs):
		super(game, self).__init__()
		self.sinkEvent("onChange")

		self.fromHTML(
		"""
			<label>
				Your Name:
				<input [name]="myInput" type="text" placeholder="Name">
			</label>

			<h1>Hello <span [name]="mySpan" class="name">Enter Name</span>!</h1>
		""")

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

	$ pyjsbuild game.py

## Contributing

We take great interest in your opinion about ViUR. We appreciate your feedback and are looking forward to hear about your ideas. Share your vision or questions with us and participate in ongoing discussions.

- [ViUR website](https://www.viur.is)
- [#ViUR on freenode IRC](https://webchat.freenode.net/?channels=viur)
- [ViUR on GitHub](https://github.com/viur-framework)
- [ViUR on Twitter](https://twitter.com/weloveViUR)

## Credits

ViUR is developed and maintained by [Mausbrand Informationssysteme GmbH](https://www.mausbrand.de/en), from Dortmund in Germany. We are a software company consisting of young, enthusiastic software developers, designers and social media experts, working on exciting projects for different kinds of customers. All of our newer projects are implemented with ViUR, from tiny web-pages to huge company intranets with hundreds of users.

Help of any kind to extend and improve or enhance this project in any kind or way is always appreciated.

## License

Copyright (C) 2012-2019 by Mausbrand Informationssysteme GmbH.

Mausbrand and ViUR are registered trademarks of Mausbrand Informationssysteme GmbH.

You may use, modify and distribute this software under the terms and conditions of the GNU Lesser General Public License (LGPL). See the file LICENSE provided within this package for more information.
