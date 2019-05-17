# Changelog

This file documents any relevant changes done to ViUR html5 since version 2.

## [develop] 

This is the current development version.

## [2.4.0] Agung

Release date: May 17, 2019

- Bugfix: Fixed bug with disabling of input widgets.
- Feature: Fully refactored the librarys source base into just two single files, to reduce number of required files to download and make the library easier to access.
- Feature: New function `Widget.isHidden()` to check if a widget is currently shown.
- Feature: Improved handling of key-events. 
- Feature: Allow to close popups by pressing `ESC`.
- Feature: Improvements for SVG and TextNode.

## [2.3.0] Kilauea

Release date: Oct 2, 2018

- Refactored `html5.ext.SelectDialog`
- Extended html parser to apply data-attributes
- Switching event handling to newer JavaScript event listener API
- Added `onFocusIn` and `onFocusOut` events

## [2.2.0] Etna

Release date: Apr 23, 2018

- Implemented `html5.Head()` to access the document's head object within the library.
- Directly append text in construction of Li().

## [2.1.0]

Release date: Nov 2, 2017

- Introduced a build-in HTML parser (`Widget.fromHTML()`) that is capable to compile HTML-code into DOM-objects of the html5 library, and an extra-feature to bind them to their root node for further access. This attempt makes it possible to create PyJS apps using the HTML5 library without creating every single element by hand.
- A more distinct way for `Widget.hide()` and `Widget.show()` that cannot be overridden by styling. (setting "hidden" does not work when another display value is set).
- Utility functions `Widget.enable() and `Widget.disable()`.
- Directly append text in construction of Div() and Span().
- Allow for tuple and list processing in table cell assignments.
- Adding `utils.parseFloat()` and `utils.parseInt()` utility functions.
- Implemented `colspan` attribute for Th()
- New README.md and CHANGELOG.md.

## 2.0

Release date: Dec 22, 2016

- v[2.0.1]: Directly append text in construction of Option().
- v[2.0.1]: Anything added to Widget.appendChild() or Widget.prependChild() which is not a widget is handled as text (TextNode() is automatically created).
- New functions `Widget.prependChild()`, `Widget.insertBefore()`, `Widget.children()`, `Widget.removeAllChildren()`,
 `Widget.addClass()`, `Widget.removeClass()`, `Widget.toggleClass()`
- Utility functions `utils.doesEventHitWidgetOrParents()`, `utils.doesEventHitWidgetOrChildren()` taken from vi77
- Insert text blocks easier with `utils.textToHtml()`
- Several bugfixes

[develop]: https://github.com/viur-framework/html5/compare/v2.4.0...develop
[2.4.0]: https://github.com/viur-framework/html5/compare/v2.3.0...v2.4.0
[2.3.0]: https://github.com/viur-framework/html5/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/viur-framework/html5/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/viur-framework/html5/compare/v2.0.0...v2.1.0
[2.0.1]: https://github.com/viur-framework/html5/compare/v2.0.0...v2.0.1
