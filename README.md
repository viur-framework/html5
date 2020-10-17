# ViUR html5

**html5** is a DOM-abstraction layer and API that is used to create client-side Web-Apps running in the browser and written in Python.

## About

This API and framework is used to implement HTML5 web-apps using the Python programming language. The framework is an abstraction layer for a DOM running in [Pyodide](https://github.com/iodide-project/pyodide), a Python 3 interpreter compiled to web-assembly.

It provides

- class abstraction for all HTML5-DOM-elements, e.g. `html5.Div()`
- a built-in HTML parser and executor to generate DOM objects from HTML-code
- helpers for adding/removing classes, arrange children, handling events etc.

The most prominent software completely established on this library is [ViUR-vi](https://github.com/viur-framework/viur-vi/), the visual administration interface for ViUR-based applications.

Look [here](https://www.viur.dev/blog/html5-library) for a short introduction about features and usage.

[flare](https://github.com/mausbrand/flare) is now available, which supersedes this library and provides a self-contained version of its core components, but with the aspect to provide a full web-app development framework.
Both libraries, flare & html5, will be held synchronous, except the dialogs and ignite-related stuff.

## Contributing

We take great interest in your opinion about ViUR. We appreciate your feedback and are looking forward to hear about your ideas. Share your vision or questions with us and participate in ongoing discussions.

- [ViUR website](https://www.viur.dev)
- [#ViUR on freenode IRC](https://webchat.freenode.net/?channels=viur)
- [ViUR on GitHub](https://github.com/viur-framework)
- [ViUR on Twitter](https://twitter.com/weloveViUR)

## Credits

ViUR is developed and maintained by [Mausbrand Informationssysteme GmbH](https://www.mausbrand.de/en), from Dortmund in Germany. We are a software company consisting of young, enthusiastic software developers, designers and social media experts, working on exciting projects for different kinds of customers. All of our newer projects are implemented with ViUR, from tiny web-pages to huge company intranets with hundreds of users.

Help of any kind to extend and improve or enhance this project in any kind or way is always appreciated.

## License

Copyright (C) 2012-2020 by Mausbrand Informationssysteme GmbH.

Mausbrand and ViUR are registered trademarks of Mausbrand Informationssysteme GmbH.

You may use, modify and distribute this software under the terms and conditions of the MIT license. See the file LICENSE provided within this package for more information.
