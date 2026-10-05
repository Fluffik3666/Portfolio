"""Site-wide SEO: canonical URLs, per-page metadata and structured data.

One place decides what every page claims about itself, so a title, its
canonical URL, its Open Graph card and its JSON-LD can't drift apart. Routes
call :func:`page` and hand the result to the template, which renders it through
``_head.html``.
"""

import os

try:
    from src import work_data
except ImportError:
    import work_data

# The canonical origin. Overridable so preview deployments can describe
# themselves honestly rather than claiming to be production.
SITE_URL = os.getenv('SITE_URL', 'https://alexanderbagrov.com').rstrip('/')

SITE_NAME = 'Sasha Bagrov'
AUTHOR = 'Sasha Bagrov'
LOCALE = 'en_GB'
TWITTER_CARD = 'summary_large_image'

OG_IMAGE = '/static/images/og/og-card.jpg'
OG_IMAGE_W, OG_IMAGE_H = 1200, 630
OG_IMAGE_ALT = 'Sasha Bagrov — developer, founder and photographer, London'

# Pages worth indexing, in sitemap order. Anything not listed here is either
# private (the tutoring account area) or an API.
SITEMAP = [
    {'path': '/', 'priority': '1.0', 'changefreq': 'monthly'},
    {'path': '/photos', 'priority': '0.8', 'changefreq': 'monthly'},
    {'path': '/tutoring/book', 'priority': '0.7', 'changefreq': 'monthly'},
    {'path': '/cv', 'priority': '0.6', 'changefreq': 'monthly'},
]

ROBOTS_DISALLOW = [
    '/api/',
    '/tutoring/api/',
    '/tutoring/account',
    '/tutoring/admin',
    '/tutoring/auth',
    '/tutoring/checkout',
    '/tutoring/webhook',
]

PROFILES = [
    'https://github.com/Fluffik3666',
    'https://kidshustle.app',
    'https://yfl.lovable.app/',
    'https://apps.apple.com/gb/app/animeatlas/id6739979715',
]


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


def gallery_schema():
    return {
        '@context': 'https://schema.org',
        '@type': 'ImageGallery',
        'name': 'Photography — Sasha Bagrov',
        'description': (
            'Photography shot around London, mostly black and white, on a '
            'Canon EOS R8.'
        ),
        'url': absolute('/photos'),
        'author': {'@id': f'{SITE_URL}/#person'},
    }


def tutoring_schema():
    return {
        '@context': 'https://schema.org',
        '@type': 'Service',
        'name': 'One-to-one Python tutoring',
        'serviceType': 'Programming tutoring',
        'description': (
            'Structured 45-minute online Python lessons for beginners, taught '
            'one to one.'
        ),
        'url': absolute('/tutoring/book'),
        'provider': {'@id': f'{SITE_URL}/#person'},
        'areaServed': {'@type': 'Country', 'name': 'United Kingdom'},
        'availableChannel': {
            '@type': 'ServiceChannel',
            'serviceUrl': absolute('/tutoring/book'),
        },
    }


def robots_txt():
    lines = ['User-agent: *', 'Allow: /']
    lines += [f'Disallow: {path}' for path in ROBOTS_DISALLOW]
    lines += ['', f'Sitemap: {absolute("/sitemap.xml")}']
    return '\n'.join(lines) + '\n'


def sitemap_xml(lastmod=None):
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for entry in SITEMAP:
        out.append('  <url>')
        out.append(f'    <loc>{absolute(entry["path"])}</loc>')
        if lastmod:
            out.append(f'    <lastmod>{lastmod}</lastmod>')
        out.append(f'    <changefreq>{entry["changefreq"]}</changefreq>')
        out.append(f'    <priority>{entry["priority"]}</priority>')
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
