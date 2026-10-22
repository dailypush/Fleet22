"""Check local HTML/CSS resources, internal anchors and sitemap."""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree
from ..utils.path_utils import PROJECT_ROOT


class Resources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if attributes.get('id'):
            self.ids.add(attributes['id'])
        for key in ('href', 'src', 'poster'):
            if attributes.get(key):
                self.links.append(attributes[key])


def check_site(root=PROJECT_ROOT):
    errors = []
    files = [root / 'index.html', *sorted((root / 'pages').rglob('*.html')),
             *sorted((root / 'analysis').rglob('*.html')), *sorted((root / 'tools').rglob('*.html'))]
    parsed = {}
    for path in files:
        parser = Resources()
        parser.feed(path.read_text())
        parsed[path.resolve()] = parser
    for path, parser in parsed.items():
        for link in parser.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            target = (root / unquote(url.path.lstrip('/')) if url.path.startswith('/')
                      else path.parent / unquote(url.path)) if url.path else path
            if not target.exists():
                errors.append(f'{path.relative_to(root)}: missing {link}')
            elif url.fragment and target.resolve() in parsed and unquote(url.fragment) not in parsed[target.resolve()].ids:
                # Bootstrap controls use JS fragment targets too; these must exist.
                errors.append(f'{path.relative_to(root)}: missing anchor {link}')
    for path in (root / 'assets/css').glob('*.css'):
        for link in re.findall(r'url\([\'"]?([^\)\'"\s]+)', path.read_text()):
            if not urlsplit(link).scheme and not (path.parent / link).exists():
                errors.append(f'{path.relative_to(root)}: missing {link}')
    sitemap = ElementTree.parse(root / 'sitemap.xml')
    for location in sitemap.findall('.//{*}loc'):
        target = root / (urlsplit(location.text).path.lstrip('/') or 'index.html')
        if not target.is_file():
            errors.append(f'sitemap: missing {location.text}')
    return errors


if __name__ == '__main__':
    errors = check_site()
    print('\n'.join(errors) if errors else 'Local site links, resources, anchors and sitemap passed.')
    sys.exit(bool(errors))
