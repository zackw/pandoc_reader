pandoc_reader
=============

A pandoc [markdown][] reader plugin for [pelican][]


Requirements
------------

  - [pandoc][] in `$PATH`

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

Pandoc's syntactic extensions to Markdown can be enabled or disabled via the
`PANDOC_EXTENSIONS` parameter.

    PANDOC_EXTENSIONS = [
      '+hard_line_breaks',
      '-citations'
    ]

File Metadata
-------------

For compatibility with older versions of this plugin that parsed MultiMarkdown-like title blocks internally, the [`mmd_title_block`][mmd_title_block] syntax extension is enabled by default.  Unfortunately, this causes Pandoc to misinterpret YAML metadata and possibly also native title blocks (see [Pandoc issue 2026][]).  Therefore, those metadata formats are *disabled* by default.  To revert to Pandoc's default behavior (accepting native title blocks and YAML metadata, but not MMD title blocks), include `-mmd_title_block` in `PANDOC_EXTENSIONS`.

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
[mmd_title_block]: http://johnmacfarlane.net/pandoc/README.html#extension-mmd_title_block
[Pandoc issue 2026]: https://github.com/jgm/pandoc/issues/2026
