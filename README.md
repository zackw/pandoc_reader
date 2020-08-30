# pandoc_reader: use Pandoc as a Markdown engine for Pelican

[![Build Status](https://img.shields.io/github/workflow/status/pelican-plugins/pandoc_reader/build)](https://github.com/zackw/pandoc_reader/actions) [![PyPI Version](https://img.shields.io/pypi/v/pelican-pandoc_reader)](https://pypi.org/project/pelican-pandoc_reader/)

This plugin gives [Pelican][] support for rendering [Markdown][]
with the [Pandoc][] utility.

[Markdown]: http://daringfireball.net/projects/markdown/
[Pandoc]: http://johnmacfarlane.net/pandoc/
[Pelican]: http://getpelican.com

## Installation

This plugin can be installed via:

    python -m pip install pelican-pandoc-reader

You must also make sure the `pandoc` command-line utility is installed
and available via `$PATH`.

## Configuration

Additional command line parameters can be passed to pandoc via the
PANDOC_ARGS parameter.

    PANDOC_ARGS = [
      '--mathjax',
      '--smart',
      '--toc',
      '--toc-depth=2',
      '--number-sections',
    ]

Pandoc's markdown extensions can be enabled or disabled via the
PANDOC_EXTENSIONS parameter.

    PANDOC_EXTENSIONS = [
      '+hard_line_breaks',
      '-citations'
    ]

## Contributing


Contributions are welcome and much appreciated. Every little bit
helps. You can contribute by improving the documentation, adding
missing features, and fixing bugs. You can also help out by reviewing
and commenting on [existing issues][].

To start contributing to this plugin, review the [Contributing to
Pelican][] documentation, beginning with the **Contributing Code**
section.

[existing issues]: https://github.com/zackw/pandoc_reader/issues
[Contributing to Pelican]: https://docs.getpelican.com/en/latest/contribute.html
