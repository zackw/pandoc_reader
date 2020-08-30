# pandoc-reader plugin for Pelican: main plugin code.
#
# Copyright 2014-2020 the authors listed in the package metadata.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0

import contextlib
import json
import subprocess

from pelican import signals
from pelican.readers import BaseReader

try:
    from importlib.resources import path as resource_path
except ImportError:
    # fallback to the standalone module in 3.6
    from importlib_resources import path as resource_path


class PandocReader(BaseReader):
    enabled = True
    file_extensions = ["md", "markdown", "mkd", "mdown"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # The default Pandoc configuration directory is part of the
        # package's resources and needs to be context-managed, but we
        # want it to stick around as long as the reader itself exists
        # so as not to waste time extracting it from the wheel
        # repeatedly for each file to be read.
        self._holder = contextlib.ExitStack()
        if "PANDOC_CFG" in self.settings:
            from os.path import abspath

            self.settings["PANDOC_CFG"] = abspath(self.settings["PANDOC_CFG"])
        else:
            self.settings["PANDOC_CFG"] = str(
                self._holder.enter_context(
                    resource_path(__package__, "pandoc")
                ).resolve(strict=True)
            )

    def __del__(self):
        self._holder.close()

    def read(self, filename):
        with open(filename, "rb") as fp:
            output = subprocess.run(
                [
                    "pandoc",
                    "--data-dir=" + self.settings["PANDOC_CFG"],
                    "--defaults=pelican",
                ],
                stdin=fp,
                stdout=subprocess.PIPE,
                encoding="utf-8",
                check=True,
            )

        lines = output.stdout.splitlines()
        content = " ".join(lines[1:])
        metadata = {
            name: self.process_metadata(name, value)
            for name, value in json.loads(lines[0]).items()
        }

        return content, metadata


def add_reader(readers):
    for ext in PandocReader.file_extensions:
        readers.reader_classes[ext] = PandocReader


def register():
    signals.readers_init.connect(add_reader)
