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

To configure Pandoc, use the `pelican-pandoc-reader-config` utility
(which is installed along with this plugin) to extract the built-in
Pandoc “user data directory” to a location within your website’s
source tree.  In your Pelican configuration, set `PANDOC_CFG` to point
to the extracted directory.  Then edit the file `defaults/pelican.yaml`
within the extracted directory.  See comments in that file for further
instructions.

Older versions of this plugin offered Pelican configuration settings
named `PANDOC_ARGS` and `PANDOC_EXTENSIONS`.  These settings are no
longer supported.  We believe that you can get all of the same effects
by editing `defaults/pelican.yaml`.  Entries in `PANDOC_ARGS`
correspond to various named keys at the top level of
`defaults/pelican.yaml`. Entries in the `PANDOC_EXTENSIONS` array
should become annotations on the `from: markdown` line.  If you
discover that something you used to be able to do is no longer
possible, please file a bug report and let us know.

You can also put anything else in this directory that goes in a Pandoc
user data directory.  In particular, Pandoc “filters” should be added
the `filters` subdirectory of the extracted directory.  One important
exception is that the file `templates/pelican.html5` should not be
modified; the plugin relies on it remaining exactly as is.

## Server-side KaTeX

We provide a sample Pandoc filter, `filters/serverside-katex.lua`,
which offers an alternative means of using [KaTeX][] to render
mathematics.  Unlike Pandoc’s built-in KaTeX support
(`html-math-method: katex`), it does not require the client to run
JavaScript.  Instead, it requires the `katex` command-line utility to
be available (e.g. via `npm install katex`) when the site is rendered.
You will still need to use the HTML5 doctype in your templates, and
load KaTeX’s *style sheet* (CSS file) on each page containing math.
The filter adds a property named `has_math` to the page metadata when
it finds math on the page.  (Due to [bugs in Pandoc][], this property
is not a boolean.  It will have the *string* value `"true"` when there
is math, and it will not be present at all when there is no math.)

To use the filter, uncomment the line referencing
`serverside-katex.lua` in the filters list in `pelican.yaml`.
This will override any `html-math-method` setting.

[KaTeX]: https://katex.org/
[bugs in Pandoc]: https://github.com/jgm/pandoc/issues?q=6288+6630+6650

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
