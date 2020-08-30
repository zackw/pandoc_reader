# pandoc-reader plugin for Pelican: helper for customizing configuration.
#
# Copyright 2014-2020 the authors listed in the package metadata.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#    http://www.apache.org/licenses/LICENSE-2.0

"""Unpack Pandoc configuration so it can be customized.

After running this tool for the first time, add the directory it
created to version control and set PANDOC_CFG to point to it in your
Pelican configuration.  Then modify defaults/pelican.yaml as you see
fit; see the comments in that file for further instructions.  You can
also add filters to the filters directory.

In the future, after updating this plugin, we recommend you run this
tool again, pointed at a fresh directory, and then merge any changes
to the default configuration back into your custom configuration.
"""

import argparse
import shutil
import sys

try:
    from importlib.resources import path as resource_path
except ImportError:
    # fallback to the standalone module in 3.6
    from importlib_resources import path as resource_path


def run():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "destdir",
        help="Directory to write the default Pandoc configuration to."
        " Must not already exist.",
    )

    args = ap.parse_args()
    try:
        with resource_path(__package__, "pandoc") as srctree:
            shutil.copytree(str(srctree), args.destdir, symlinks=True)

    except shutil.Error as e:
        for src, dst, why in e.args[0]:
            sys.stderr.write("copying {} to {}: {}\n".format(src, dst, why))
        sys.exit(1)

    except Exception as e:
        sys.stderr.write(str(e) + "\n")
        sys.exit(1)

    sys.exit(0)
