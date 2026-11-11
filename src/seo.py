"""Site-wide SEO: canonical URLs, per-page metadata and structured data.

One place decides what every page claims about itself, so a title, its
canonical URL, its Open Graph card and its JSON-LD can't drift apart. Routes
call :func:`page` and hand the result to the template, which renders it through
``_head.html``.
"""

import os

from xml.sax.saxutils import escape as xml_escape

try:
    from src import work_data
except ImportError:
    import work_data

# The canonical origin. Overridable so preview deployments can describe
# themselves honestly rather than claiming to be production.
SITE_URL = os.getenv('SITE_URL', 'https://sashabagrov.com').rstrip('/')

# Hosts the site used to live on. Anything still arriving on one is sent to
# SITE_URL with a permanent redirect, so the inbound links and the search
# ranking built up against the old name follow the site here instead of
# stopping at a domain that no longer serves it. Preview hosts aren't listed,
# so a deployment on *.vercel.app still answers for itself.
LEGACY_HOSTS = frozenset({
    'alexanderbagrov.com',
    'www.alexanderbagrov.com',
})

SITE_NAME = 'Sasha Bagrov'
AUTHOR = 'Sasha Bagrov'
LOCALE = 'en_GB'
TWITTER_CARD = 'summary_large_image'
TWITTER_HANDLE = '@sashabagrov'

OG_IMAGE = '/static/images/og/og-card.jpg'
OG_IMAGE_W, OG_IMAGE_H = 1200, 630
OG_IMAGE_ALT = 'Sasha Bagrov — developer, founder and photographer, London'

LICENSING_PATH = '/licensing'
LICENSING_EMAIL = 'sasha@urbanmechanics.co.uk'
CREDIT_TEXT = 'Photo: Sasha Bagrov'
COPYRIGHT_NOTICE = '© Sasha Bagrov. All rights reserved.'

# Pages worth indexing, in sitemap order. Anything not listed here is an API.
SITEMAP = [
    {'path': '/', 'priority': '1.0', 'changefreq': 'monthly'},
    {'path': '/cv', 'priority': '0.6', 'changefreq': 'monthly'},
    {'path': LICENSING_PATH, 'priority': '0.3', 'changefreq': 'yearly'},
]

ROBOTS_DISALLOW = [
    '/api/',
]

# Images that live in the page markup, so the sitemap can list them without
# asking the storage bucket anything. The gallery's photos are passed in at
# request time instead -- only the app knows what is in the bucket.
# Listed as the JPEG fallbacks: the <picture> elements prefer AVIF and WebP,
# but the JPEG is the version every crawler can read.
PAGE_IMAGES = {
    '/': [
        '/static/images/derived/sb_photos_bw-2-1400.jpg',
        '/static/images/derived/sb_photos_bw-2000.jpg',
    ],
}

PROFILES = [
    'https://github.com/Fluffik3666',
    'https://x.com/sashabagrov',
    'https://kidshustle.app',
    'https://yfl.lovable.app/',
    'https://foundhaus.app/',
    'https://apps.apple.com/gb/app/animeatlas/id6739979715',
]


def is_legacy_host(host):
    """True if `host` is a domain the site has moved away from.

    Takes the raw Host header, so it tolerates a port and any casing.
    """
    return (host or '').split(':')[0].lower() in LEGACY_HOSTS


def absolute(path):
    """Absolute URL for a site-relative path."""
    if path.startswith(('http://', 'https://')):
        return path
    return f"{SITE_URL}/{path.lstrip('/')}"


def page(path, title, description, *, og_type='website', image=None,
         index=True, schema=None):
    """Everything ``_head.html`` needs for one page.

    ``title`` is the page's own name; the template appends the site name
    except on the homepage, where they are the same thing.
    """
    return {
        'title': title,
        'description': description,
        'canonical': absolute(path),
        'og_type': og_type,
        'image': absolute(image or OG_IMAGE),
        'index': index,
        'schema': schema or [],
    }


def person_schema():
    """Person + ProfilePage, the schema a portfolio homepage actually wants."""
    return {
        '@context': 'https://schema.org',
        '@type': 'Person',
        '@id': f'{SITE_URL}/#person',
        'name': AUTHOR,
        'url': SITE_URL,
        'image': absolute(OG_IMAGE),
        'jobTitle': 'Founder & Software Engineer',
        'description': (
            'Developer, founder and photographer in London. Founder of '
            'KidsHustle, a regulated UK marketplace connecting teenagers with '
            'local paid work.'
        ),
        'address': {
            '@type': 'PostalAddress',
            'addressLocality': 'London',
            'addressCountry': 'GB',
        },
        'worksFor': {
            '@type': 'Organization',
            'name': 'Urban Mechanics Ltd',
            'url': 'https://kidshustle.app',
        },
        'alumniOf': {
            '@type': 'EducationalOrganization',
            'name': work_data.EDUCATION['name'],
        },
        'knowsAbout': sorted(work_data.skill_names().values()),
        'sameAs': PROFILES,
    }


def website_schema():
    return {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        '@id': f'{SITE_URL}/#website',
        'url': SITE_URL,
        'name': SITE_NAME,
        'inLanguage': 'en-GB',
        'publisher': {'@id': f'{SITE_URL}/#person'},
    }


def gallery_schema(photos=()):
    """The gallery, and the photographs in it.

    ``photos`` are the render-ready items the page itself puts on screen, so
    the markup and the structured data name the same URLs. A gallery that
    declares itself but lists nothing gives an image crawler no reason to
    look further.
    """
    return {
        '@context': 'https://schema.org',
        '@type': 'ImageGallery',
        'name': 'Photography — Sasha Bagrov',
        'description': (
            'Street and travel photography by Sasha Bagrov: London, Prague, '
            'Mariánské Lázně, Lübeck, New York and the forests in between, '
            'shot on a Canon EOS R8.'
        ),
        'url': absolute('/photos'),
        'author': {'@id': f'{SITE_URL}/#person'},
        'image': [
            {
                '@type': 'ImageObject',
                'contentUrl': absolute(photo['src']),
                'description': photo['alt'],
                'creator': {'@id': f'{SITE_URL}/#person'},
                'copyrightHolder': {'@id': f'{SITE_URL}/#person'},
                'creditText': CREDIT_TEXT,
                'copyrightNotice': COPYRIGHT_NOTICE,
                'license': absolute(LICENSING_PATH),
                'acquireLicensePage': absolute(LICENSING_PATH + '#request'),
            }
            for photo in photos
        ],
    }


def robots_txt():
    lines = ['User-agent: *', 'Allow: /']
    lines += [f'Disallow: {path}' for path in ROBOTS_DISALLOW]
    lines += ['', f'Sitemap: {absolute("/sitemap.xml")}']
    return '\n'.join(lines) + '\n'


def sitemap_xml(lastmod=None, page_images=None):
    """The sitemap, with every page's images declared alongside it.

    ``page_images`` maps a path to extra image URLs for that page -- the
    gallery's photos, which only the app can enumerate. They are merged with
    the ones already known from the markup.

    Images are listed so they can be found without waiting for a crawler to
    render the page and notice them. Only ``image:loc`` is emitted: Google
    dropped support for the caption, title, licence and geo tags in 2022, and
    an unread tag is just weight.
    """
    images = {path: list(locs) for path, locs in PAGE_IMAGES.items()}
    for path, locs in (page_images or {}).items():
        images.setdefault(path, []).extend(locs)

    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
           ' xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    for entry in SITEMAP:
        out.append('  <url>')
        out.append(f'    <loc>{absolute(entry["path"])}</loc>')
        if lastmod:
            out.append(f'    <lastmod>{lastmod}</lastmod>')
        out.append(f'    <changefreq>{entry["changefreq"]}</changefreq>')
        out.append(f'    <priority>{entry["priority"]}</priority>')
        for loc in images.get(entry['path'], ()):
            # Gallery URLs carry a query string, so the ampersands have to be
            # escaped or the document isn't well-formed XML.
            out.append('    <image:image>')
            out.append(f'      <image:loc>{xml_escape(absolute(loc))}</image:loc>')
            out.append('    </image:image>')
        out.append('  </url>')
    out.append('</urlset>')
    return '\n'.join(out) + '\n'


def webmanifest():
    return {
        'name': SITE_NAME,
        'short_name': 'Sasha',
        'description': 'Developer, founder and photographer in London.',
        'start_url': '/',
        'display': 'standalone',
        'background_color': '#000000',
        'theme_color': '#000000',
        'icons': [
            {'src': '/static/images/icons/icon-192.png', 'sizes': '192x192',
             'type': 'image/png', 'purpose': 'any'},
            {'src': '/static/images/icons/icon-512.png', 'sizes': '512x512',
             'type': 'image/png', 'purpose': 'any'},
        ],
    }
