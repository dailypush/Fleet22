"""Render shared static navigation/footer fragments and sitemap (no runtime build).

Run after editing templates. --check verifies checked-in HTML is up to date.
"""
import argparse
import re
from datetime import date
from pathlib import Path
from string import Template
from .utils.path_utils import PROJECT_ROOT

PUBLIC_PAGES = ['index.html', *sorted(str(p.relative_to(PROJECT_ROOT))
                                    for p in (PROJECT_ROOT / 'pages').rglob('*.html'))]
GENERATED_PAGES = [*PUBLIC_PAGES, 'tools/test_na.html', 'tools/documents/hull_cleaning.html', 'tools/documents/event_crew_weighin.html']
NAV_LINKS = [('index.html', 'Home'), ('pages/classifieds.html', 'Classifieds'),
             ('pages/members.html', 'Members'), ('pages/fleetdues.html', 'Fleet Dues'),
             ('pages/join.html', 'Join'), ('pages/events_archive.html', 'Event Archive')]
BOOTSTRAP_CSS = '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">'
BOOTSTRAP_JS = '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js" integrity="sha384-FKyoEForCGlyvwx9Hj09JcYn3nv7wiPVlz7YYwJrWVcXK/BmnVDxM+D2scQbITxI" crossorigin="anonymous" defer></script>'


def render_page(relative, source):
    root = '/'.join(['..'] * (len(Path(relative).parts) - 1)) or '.'
    links = []
    page_links = list(NAV_LINKS)
    tool_labels = {'tools/documents/hull_cleaning.html': 'Hull Cleaning',
                   'tools/documents/event_crew_weighin.html': 'Crew Weigh-In'}
    if relative in tool_labels:
        page_links.append((relative, tool_labels[relative]))
    for target, label in page_links:
        active = relative == target or (target == 'pages/events_archive.html' and relative in {
            'pages/north_americans_2024.html', 'pages/media_kit.html',
            'pages/news/cleveland-race-week-2024-highlights.html'})
        links.append('                <li class="nav-item"><a class="nav-link' + (' active' if active else '') +
                     f'" href="{root}/{target}"' + (' aria-current="page"' if relative == target else '') + f'>{label}</a></li>')
    navigation = Template((PROJECT_ROOT / 'templates/navigation.html').read_text()).substitute(root=root, links='\n'.join(links)).strip()
    extra = ''
    if relative == 'pages/north_americans_2024.html':
        extra = '        <p><a href="./events_archive.html">Browse the event archive</a></p>'
    footer = Template((PROJECT_ROOT / 'templates/footer.html').read_text()).substitute(year=date.today().year, extra=extra).strip()
    for name, content, fallback in [('navigation', navigation, r'<nav\b.*?</nav>'), ('footer', footer, r'<footer\b.*?</footer>')]:
        rendered = f'<!-- shared:{name} -->\n{content}\n<!-- /shared:{name} -->'
        marker = rf'<!-- shared:{name} -->.*?<!-- /shared:{name} -->'
        if re.search(marker, source, re.S):
            source = re.sub(marker, lambda _: rendered, source, count=1, flags=re.S)
        elif re.search(fallback, source, re.S):
            source = re.sub(fallback, lambda _: rendered, source, count=1, flags=re.S)
        elif name == 'footer':
            source = source.replace('</body>', rendered + '\n</body>')
        else:
            raise ValueError(f'Navigation missing in {relative}')
    source = re.sub(r'<link\b[^>]*href="https://[^" ]*/bootstrap(?:@[^/" ]+|/[^/" ]+)?/[^" ]*bootstrap.min.css"[^>]*>', lambda _: BOOTSTRAP_CSS, source)
    source = re.sub(r'<script\b[^>]*src="https://[^" ]*/bootstrap(?:@[^/" ]+|/[^/" ]+)?/[^" ]*bootstrap(?:.bundle)?.min.js"[^>]*></script>', lambda _: BOOTSTRAP_JS, source)
    source = re.sub(r'\s*<script src="https://[^" ]*(?:jquery|popper)[^" ]*"[^>]*></script>', '', source)
    return source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    outputs = {relative: render_page(relative, (PROJECT_ROOT / relative).read_text()) for relative in GENERATED_PAGES}
    urls = ['' if p == 'index.html' else p for p in PUBLIC_PAGES]
    urls += ['analysis/githeatmap.html', 'analysis/heatmap.html', 'analysis/treemap/treemap.html', 'analysis/sail_analysis_heatmap.html']
    outputs['sitemap.xml'] = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>https://www.fleet22.us/{url}</loc></url>\n' for url in urls) + '</urlset>\n'
    stale = []
    for relative, output in outputs.items():
        path = PROJECT_ROOT / relative
        if path.read_text() != output:
            stale.append(relative)
            if not args.check:
                path.write_text(output)
    if args.check and stale:
        print('Run python -m scripts.generate_site to update: ' + ', '.join(stale))
        return 1
    print(f'Shared site fragments and sitemap {"checked" if args.check else "generated"}.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
