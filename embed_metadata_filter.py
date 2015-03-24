# This is a filter script which embeds all of the metadata parsed by
# Pandoc into the HTML output, where the main body of the reader can
# pick it up.  In order to preserve Pandoc's translation of Markdown
# in metadata values, we convert the metadata structure into an HTML
# tree structure.  A <hr> separates the translated metadata from the
# document itself.
#
# See http://johnmacfarlane.net/pandoc/scripting.html for documentation
# of the JSON-serialized AST that we are manipulating.

import json
import sys

def N(t, c, cls=None):
    if cls is not None: c = [ ["", [cls], []], c ]
    return { "t": t, "c": c }

def cvt_metainlines(c):
    return N("Plain", [N("Span", c, "metavalue")])

def cvt_metamap(c):
    return N("DefinitionList", [ ( [N("Str", key)], [[ convert(val) ]] )
                                 for key, val in sorted(c.items()) ])

CONVERTERS = {
    "MetaMap":               cvt_metamap,
    "MetaInlines":           cvt_metainlines,
    "MetaBool":    lambda c: cvt_metainlines([N("Str", str(c).lower())]),
    "MetaString":  lambda c: cvt_metainlines([N("Str", c)]),
    "MetaBlocks":  lambda c: N("Div", c, "metavalue"),
    "MetaList":    lambda c: N("BulletList", [ [convert(item)] for item in c ])
}

def convert(item):
    return CONVERTERS[item["t"]](item["c"])

def main():
    blob = json.load(sys.stdin)
    metadata = blob[0]['unMeta']
    rendered = [cvt_metamap(metadata), N("HorizontalRule", [])]
    rendered.extend(blob[1])
    blob = [blob[0], rendered]
    json.dump(blob, sys.stdout, separators=(',',':'))

# This filter script is imported by pandoc_reader in order to learn its
# actual filename, so don't do anything unless invoked as __main__.
if __name__ == '__main__': main()
