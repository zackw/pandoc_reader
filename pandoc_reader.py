import re
import subprocess
from pelican import signals
from pelican.readers import BaseReader
from pelican.utils import pelican_open

# The syntax of "plain" metadata is aligned with markdown.extensions.meta.
META_RE = re.compile(r'^[ ]{0,3}(?P<key>[A-Za-z0-9_-]+):\s*(?P<value>.*)')
META_MORE_RE = re.compile(r'^[ ]{4,}(?P<value>.*)')
END_RE = re.compile(r'^\s*$')

def parse_plain_metadata(lines):
    meta = {}
    if not lines:
        return meta

    lines.reverse()
    while lines:
        line = lines.pop()
        if END_RE.match(line):
            break
        m = META_RE.match(line)
        if m:
            key = m.group('key').lower().strip()
            value = m.group('value').strip()
            if key in meta:
                meta[key].append(value)
            else:
                meta[key] = [value]
        else:
            m2 = META_MORE_RE.match(line)
            if m2 and key:
                meta[key].append(m2.group('value').strip())
            else:
                lines.append(line)
                break

    lines.reverse()
    # Flatten all 1-entry lists.
    for k in list(meta.keys()):
        v = meta[k]
        if len(v) == 0:
            del meta[k]
        elif len(v) == 1:
            meta[k] = v[0]

    return meta

# Load PyYaml only if required.
yaml_load = None
def get_yaml_load():
    global yaml_load
    if yaml_load is None:
        import yaml
        try:
            from yaml import CSafeLoader as SafeLoader
        except ImportError:
            from yaml import SafeLoader

        def _yaml_load(block):
            return yaml.load("\n".join(block), SafeLoader)
        yaml_load = _yaml_load
    return yaml_load

def parse_yaml_metadata(lines):
    for i, l in enumerate(lines):
        if i > 0 and (lines[i] == '---' or lines[i] == '...'):
            yblock = lines[1:i]
            del lines[0:(i+1)]
            break
    else:
        return {}

    meta = get_yaml_load()(yblock)
    return { k.lower(): v for k, v in meta.items() }


class PandocReader(BaseReader):
    enabled = True
    file_extensions = ['md', 'markdown', 'mkd', 'mdown']

    def read(self, filename):
        tab_width = self.settings.get('PANDOC_TAB_WIDTH', 8)
        with pelican_open(filename) as fp:
            text = [line.expandtabs(tab_width) for line in fp.splitlines()]

        if text[0] == '---':
            metadata = parse_yaml_metadata(text)
        else:
            metadata = parse_plain_metadata(text)

        metadata = { k: self.process_metadata(k, v)
                     for k, v in metadata.items() }
        content = "\n".join(text)

        extra_args = self.settings.get('PANDOC_ARGS', [])
        extensions = self.settings.get('PANDOC_EXTENSIONS', '')
        if isinstance(extensions, list):
            extensions = ''.join(extensions)

        pandoc_cmd = ["pandoc", "--from=markdown" + extensions, "--to=html5"]
        pandoc_cmd.extend(extra_args)

        proc = subprocess.Popen(pandoc_cmd,
                                stdin = subprocess.PIPE,
                                stdout = subprocess.PIPE)

        output = proc.communicate(content.encode('utf-8'))[0].decode('utf-8')
        status = proc.wait()
        if status:
            raise subprocess.CalledProcessError(status, pandoc_cmd)

        return output, metadata

def add_reader(readers):
    for ext in PandocReader.file_extensions:
        readers.reader_classes[ext] = PandocReader

def register():
    signals.readers_init.connect(add_reader)
