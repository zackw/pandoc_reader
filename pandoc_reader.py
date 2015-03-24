import subprocess
import sys

import logging
logger = logging.getLogger(__name__)

try:                import xml.etree.cElementTree as ET
except ImportError: import xml.etree.ElementTree  as ET

try:                from io import StringIO
except ImportError: from cStringIO import StringIO

from pelican import signals
from pelican.readers import BaseReader

from . import embed_metadata_filter

def check_command(proc, cmd):
    """Roughly as subprocess.check_call does, wait for PROC and throw
       an exception if it didn't exit successfully.  CMD should be the
       command passed to subprocess.Popen."""
    status = proc.wait()
    if status:
        raise subprocess.CalledProcessError(status, cmd)

def extract_metadata(text):
    """A filter script converts Pandoc's internal representation of the
       metadata into an HTML tree structure so that it will make it to
       the output, with strings properly formatted.  Separate that
       tree from the HTML for the document itself, and decode it into
       Pelican's desired representation."""

    def walk_dl(e):
        rv = {}
        key = None
        for child in e:
            if child.tag == "dt":
                assert key is None
                assert len(child) == 0
                key = child.text
            else:
                assert child.tag == "dd"
                assert key is not None
                assert len(child) == 1
                rv[key] = walk(child[0])
                key = None
        return rv

    def walk_ul(e):
        rv = []
        for child in e:
            assert child.tag == "li"
            assert len(child) == 1
            rv.append(walk(child[0]))
        return rv

    def walk_value(e):
        assert e.get("class") == "metavalue"
        # Setting e.tag and e.tail to None temporarily seems to be the
        # least-hassle way to persuade ET.tostring to dump the *contents*
        # of e but not e itself.
        tag = e.tag
        tail = e.tail
        try:
            e.tag = None
            e.tail = None
            return (ET.tostring(e, encoding="utf-8", method="html")
                    .decode("utf-8").strip())
        finally:
            e.tag = tag
            e.tail = tail

    def walk(e):
        if e.tag == "dl":
            return walk_dl(e)
        elif e.tag == "ul":
            return walk_ul(e)
        elif e.tag == "div" or e.tag == "span":
            return walk_value(e)
        else:
            logger.error("unexpected metadata structure: " +
                         ET.tostring(e, encoding="utf-8", method="html")
                         .decode("utf-8"))


    metadata, _, document = text.partition("<hr />")
    document = document.strip()

    # Remove namespaces from all metadata elements while parsing them.
    # This is necessary because Pandoc thinks you have to put an
    # xmlns= on every use of <math>, and that makes ET.tostring
    # generate tags like <ns0:math>, which an HTML (not XHTML) parser
    # will not understand.
    it = ET.iterparse(StringIO(metadata))
    for _, el in it:
        if "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]

    assert it.root.tag == "dl"
    return document, walk(it.root)

class PandocReader(BaseReader):
    enabled = True
    file_extensions = ["md", "markdown", "mkd", "mdown"]

    def memoize_settings(self):
        """Load settings and compute the various subprocess invocations we
           will be using."""
        if hasattr(self, "pd_extensions"): return

        extra_args = self.settings.get("PANDOC_ARGS", [])

        pos_extensions = set()
        neg_extensions = set()
        for ext in self.settings.get("PANDOC_EXTENSIONS", []):
            if len(ext) >= 2:
                if ext[0] == "-":
                    neg_extensions.add(ext[1:])
                    continue
                elif ext[0] == "+":
                    pos_extensions.add(ext[1:])
                    continue
            logger.error("invalid PANDOC_EXTENSIONS item {!r}".format(ext))

        # For compatibility with older versions of this plugin that
        # parsed vaguely MMD-style metadata blocks themselves, we
        # default to +mmd_title_block.  Unfortunately,
        # +mmd_title_block causes Pandoc to mis-parse YAML and
        # possibly also native title blocks (see
        # https://github.com/jgm/pandoc/issues/2026).  Therefore,
        # if there's nothing about title blocks in PANDOC_EXTENSIONS,
        # we also explicitly disable YAML and native title blocks.

        if ("mmd_title_block"     not in pos_extensions and
            "mmd_title_block"     not in neg_extensions and
            "pandoc_title_block"  not in pos_extensions and
            "pandoc_title_block"  not in neg_extensions and
            "yaml_metadata_block" not in pos_extensions and
            "yaml_metadata_block" not in neg_extensions):
            pos_extensions.add("mmd_title_block")
            neg_extensions.add("pandoc_title_block")
            neg_extensions.add("yaml_metadata_block")

        both_exts = pos_extensions & neg_extensions
        if both_exts:
            logger.error("Pandoc syntax extensions both enabled and disabled: "
                         + " ".join(sorted(both_exts)))
            pos_extensions -= both_exts
            neg_extensions -= both_exts

        syntax = "markdown"
        if pos_extensions:
            syntax += "".join(sorted("+"+ext for ext in pos_extensions))
        if neg_extensions:
            syntax += "".join(sorted("-"+ext for ext in neg_extensions))

        pd_cmd_1 = ["pandoc", "-f", syntax, "-t", "json"]
        pd_cmd_2 = ["pandoc", "-f", "json", "-t", "html5"]
        # We don't know whether the extra_args are relevant to the reader or
        # writer, and it is harmless to supply them to both.
        pd_cmd_1.extend(extra_args)
        pd_cmd_2.extend(extra_args)

        self.pd_cmd_1 = pd_cmd_1
        self.pd_cmd_2 = pd_cmd_2
        self.filt_cmd = [sys.executable, embed_metadata_filter.__file__]
        logger.debug("Reader command: " + " ".join(self.pd_cmd_1))
        logger.debug("Writer command: " + " ".join(self.pd_cmd_2))
        logger.debug("Filter command: " + " ".join(self.filt_cmd))

    def read(self, filename):
        self.memoize_settings()

        # We do not use --filter because that requires the filter to
        # be directly executable.  By constructing a pipeline by hand
        # we can use sys.executable and not worry about #! lines or
        # execute bits.
        PIPE = subprocess.PIPE
        fp = None
        p1 = None
        p2 = None
        p3 = None
        try:
            fp = open(filename, "rb")
            p1 = subprocess.Popen(self.pd_cmd_1, stdin=fp, stdout=PIPE)
            p2 = subprocess.Popen(self.filt_cmd, stdin=p1.stdout, stdout=PIPE)
            p3 = subprocess.Popen(self.pd_cmd_2, stdin=p2.stdout, stdout=PIPE)

            text = p3.stdout.read().decode("utf-8")

        finally:
            if fp is not None: fp.close()
            if p1 is not None: check_command(p1, self.pd_cmd_1)
            if p2 is not None: check_command(p2, self.filt_cmd)
            if p3 is not None: check_command(p3, self.pd_cmd_2)

        document, raw_metadata = extract_metadata(text)
        metadata = {}
        for k, v in raw_metadata.items():
            k = k.lower()
            metadata[k] = self.process_metadata(k, v)

        return document, metadata

def add_reader(readers):
    for ext in PandocReader.file_extensions:
        readers.reader_classes[ext] = PandocReader

def register():
    signals.readers_init.connect(add_reader)
