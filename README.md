pandoc_reader
=============

A pandoc [markdown][] reader plugin for [pelican][]


Requirements
------------

  - [pandoc][] in `$PATH`
  - [PyYAML][], only if YAML-format metadata is used.

Installation
------------

Instructions for installation of pelican plugins can be obtained from the [pelican plugin manual](https://github.com/getpelican/pelican-plugins/blob/master/Readme.rst).


Configuration
-------------

Additional command line parameters can be passed to pandoc via the `PANDOC_ARGS` parameter.

    PANDOC_ARGS = [
      '--mathjax',
      '--smart',
      '--toc',
      '--toc-depth=2',
      '--number-sections',
    ]

Pandoc's markdown extensions can be enabled or disabled via the
`PANDOC_EXTENSIONS` parameter.

    PANDOC_EXTENSIONS = [
      '+hard_line_breaks',
      '-citations'
    ]

Hard tabs in the file are expanded to spaces before the file is passed
to Pandoc.  The tab width can be set with the `PANDOC_TAB_WIDTH`
parameter; the default is 8.

File Metadata
-------------

By default, metadata conforms to the same syntax understood by Python
Markdown's [meta-data extension][], which is not unlike that used for
email headers.  It's easiest to give an example:

    Title:   My Document
    Summary: A brief description of my document.
    Authors: Waylan Limberg
             John Doe
    Date:    October 2, 2007
    blank-value:
    base_url: http://example.com

    This is the first paragraph of the document.

If the first line of the document is exactly '`---`' (three dashes),
then the metadata instead ends at the next line which is either
exactly '`---`' or exactly '`...`', and everything in between will be
parsed as [YAML][], using the [PyYAML][] library.  Note that Python
Markdown also recognizes `---` to `...` as metadata delimiters but
does *not* parse what's in between as YAML.

In either syntax, all top-level metadata keys are folded to lowercase
(as expected by Pelican core).  The metadata does *not* pass through
Pandoc; this means, for instance, that Markdown notation within a
metadata value will not be processed.

Contributing
------------

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request


[markdown]: http://daringfireball.net/projects/markdown/
[pandoc]: http://johnmacfarlane.net/pandoc/
[pelican]: http://getpelican.com
[YAML]: http://yaml.org/
[PyYAML]: http://pyyaml.org/
[meta-data extension]: https://pythonhosted.org//Markdown/extensions/meta_data.html
