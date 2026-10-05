from flask import Flask, render_template, request, Response, jsonify, redirect, send_from_directory, url_for
from PIL import Image
import hashlib
import io
from datetime import datetime, timezone
import os
import re
import json
import cssmin
import rjsmin

try:
    from src.firebase_config import initialize_firebase
    from src import work_data
    from src import seo as seo_mod
except ImportError:
    from firebase_config import initialize_firebase
    import work_data
    import seo as seo_mod

app = Flask(__name__, template_folder='../src/templates', static_folder='../src/static')

storage_bucket = initialize_firebase()

_min_cache = {}
_asset_version_cache = {}

# Image hashes are precomputed by scripts/optimize_images.sh. The images
# themselves are served straight from Vercel's static build and deliberately
# kept out of the serverless bundle, so the bytes aren't here to hash at
# request time -- the manifest stands in for them.
def _load_image_manifest():
    manifest_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'image_manifest.json'
    )
    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}

_image_manifest = _load_image_manifest()

def asset_version(filename):
    """Short content hash for a static file, or None if it can't be read.

    Appended to static URLs as ?v= so a cached stylesheet can never be paired
    with newer markup that expects different rules.
    """
    filepath = os.path.join(app.static_folder, filename)
    try:
        mtime = os.path.getmtime(filepath)
    except OSError:
        # Not on disk: fall back to the precomputed manifest, which is how
        # images resolve now that they ship outside the bundle.
        if filename.startswith('images/'):
            key = filename[len('images/'):]
            return _image_manifest.get(key) or _image_manifest.get(
                os.path.basename(filename)
            )
        return None
    cached = _asset_version_cache.get(filepath)
    if cached and cached[0] == mtime:
        return cached[1]
    try:
        with open(filepath, 'rb') as f:
            digest = hashlib.blake2b(f.read(), digest_size=6).hexdigest()
    except OSError:
        return None
    _asset_version_cache[filepath] = (mtime, digest)
    return digest

# Stamp every url_for('static', ...) with the file's hash, so templates don't
# have to remember to do it.
@app.url_defaults
def add_asset_version(endpoint, values):
    if endpoint != 'static' or 'filename' not in values or 'v' in values:
        return
    version = asset_version(values['filename'])
    if version:
        values['v'] = version

def cache_headers(resp):
    """Cache hashed URLs hard; anything unversioned only briefly.

    s-maxage lets Vercel's CDN keep serving these without re-invoking the
    function, which is what keeps a cold start off the critical path.
    """
    if request.args.get('v'):
        resp.headers['Cache-Control'] = (
            'public, max-age=31536000, s-maxage=31536000, immutable'
        )
    else:
        resp.headers['Cache-Control'] = (
            'public, max-age=3600, s-maxage=86400, stale-while-revalidate=604800'
        )
    return resp

# Widths generated per photo by scripts/optimize_images.sh. Kept in step with
# the IMAGES list in that script.
_PHOTO_WIDTHS = {
    'sb_photos_bw-2': (600, 900, 1400),
    'sb_photos_bw': (900, 1400, 2000),
}

def photo_sources(name, fmt):
    """srcset for one photo in one format, letting the browser pick a width."""
    widths = _PHOTO_WIDTHS.get(name, ())
    return ', '.join(
        '{} {}w'.format(
            url_for('static', filename='images/derived/{}-{}.{}'.format(
                name, w, fmt
            )),
            w,
        )
        for w in widths
    )

def photo_fallback(name, width):
    """URL of the plain-JPEG derivative used as the <img> src."""
    return url_for(
        'static', filename='images/derived/{}-{}.jpg'.format(name, width)
    )

app.jinja_env.globals['seo_site'] = {
    'name': seo_mod.SITE_NAME,
    'author': seo_mod.AUTHOR,
    'locale': seo_mod.LOCALE,
    'twitter_card': seo_mod.TWITTER_CARD,
    'image_w': seo_mod.OG_IMAGE_W,
    'image_h': seo_mod.OG_IMAGE_H,
    'image_alt': seo_mod.OG_IMAGE_ALT,
}
app.jinja_env.globals['photo_sources'] = photo_sources
app.jinja_env.globals['photo_fallback'] = photo_fallback

# <pre>/<textarea> content is whitespace-significant, so keep it verbatim.
_VERBATIM_RE = re.compile(
    r'<(pre|textarea)\b[^>]*>.*?</\1>',
    flags=re.DOTALL | re.IGNORECASE,
)
_STYLE_RE = re.compile(
    r'(<style\b[^>]*>)(.*?)(</style>)',
    flags=re.DOTALL | re.IGNORECASE,
)
_SCRIPT_RE = re.compile(
    r'(<script\b[^>]*>)(.*?)(</script>)',
    flags=re.DOTALL | re.IGNORECASE,
)
_TYPE_RE = re.compile(r'type\s*=\s*["\']?([^"\'>\s]+)', flags=re.IGNORECASE)
# Only these script types are JavaScript we can safely run through the JS
# minifier; anything else (e.g. application/json, text/template) is left alone.
_JS_TYPES = {'', 'text/javascript', 'application/javascript', 'module'}

# cssmin strips the whitespace around `+` everywhere, including inside calc().
# `calc(var(--a)+var(--b))` is invalid -- calc requires whitespace around + and
# the browser drops the whole declaration -- so put it back. Only `+` is
# affected; cssmin already leaves `-` alone, and touching that would corrupt
# negative values. A `+` inside calc() is always an operator, so this is safe,
# and restricting it to balanced calc() spans keeps selector combinators and
# :nth-child(2n+1) untouched.
def _restore_calc_spacing(css):
    out = []
    i = 0
    lowered = css.lower()
    while True:
        start = lowered.find('calc(', i)
        if start == -1:
            out.append(css[i:])
            return ''.join(out)
        open_paren = start + len('calc(') - 1
        depth = 0
        end = None
        for j in range(open_paren, len(css)):
            if css[j] == '(':
                depth += 1
            elif css[j] == ')':
                depth -= 1
                if depth == 0:
                    end = j
                    break
        if end is None:
            out.append(css[i:])
            return ''.join(out)
        out.append(css[i:open_paren + 1])
        out.append(css[open_paren + 1:end].replace('+', ' + '))
        out.append(')')
        i = end + 1


def minify_css(text):
    return _restore_calc_spacing(cssmin.cssmin(text))


def minify_html(html):
    stash = []

    def _stash(text):
        stash.append(text)
        return f'\x00{len(stash) - 1}\x00'

    # Protect whitespace-significant blocks before we touch anything else.
    html = _VERBATIM_RE.sub(lambda m: _stash(m.group(0)), html)

    # Minify inline CSS, then stash it so markup collapsing can't touch it.
    def _minify_style(match):
        open_tag, body, close_tag = match.groups()
        try:
            body = minify_css(body)
        except Exception:
            pass
        return _stash(open_tag + body + close_tag)

    html = _STYLE_RE.sub(_minify_style, html)

    # Minify inline JS (skip external and non-JS scripts), then stash it.
    def _minify_script(match):
        open_tag, body, close_tag = match.groups()
        script_type = _TYPE_RE.search(open_tag)
        is_js = (script_type.group(1).lower() if script_type else '') in _JS_TYPES
        if 'src=' not in open_tag.lower() and is_js and body.strip():
            try:
                body = rjsmin.jsmin(body)
            except Exception:
                pass
        return _stash(open_tag + body + close_tag)

    html = _SCRIPT_RE.sub(_minify_script, html)

    # Collapse the remaining markup.
    html = re.sub(r'<!--(?!\[if).*?-->', '', html, flags=re.DOTALL)
    html = re.sub(r'>\s+<', '><', html)
    html = re.sub(r'\s{2,}', ' ', html)
    html = html.strip()

    html = re.sub(r'\x00(\d+)\x00', lambda m: stash[int(m.group(1))], html)
    return html

def get_minified(filepath, minifier):
    mtime = os.path.getmtime(filepath)
    if filepath in _min_cache and _min_cache[filepath][0] == mtime:
        return _min_cache[filepath][1]
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    minified = minifier(content)
    _min_cache[filepath] = (mtime, minified)
    return minified

# Minify every HTML page we render (works locally and on Vercel's Python runtime).
@app.after_request
def minify_html_response(response):
    if response.mimetype == 'text/html' and not response.direct_passthrough:
        try:
            response.set_data(minify_html(response.get_data(as_text=True)))
        except (UnicodeDecodeError, RuntimeError):
            pass
    return response

def page_cache_headers(resp):
    """Let the CDN serve public pages so the function stays off the hot path.

    These pages are static markup, so the edge can hold them for a day and
    keep serving a stale copy for a week while it revalidates in the
    background -- a visitor then pays neither the cold start nor the
    round trip to the function's region.
    """
    resp.headers['Cache-Control'] = (
        'public, max-age=0, s-maxage=86400, stale-while-revalidate=604800'
    )
    resp.headers['Vary'] = 'Accept-Encoding'
    return resp

#! serve our important routes
@app.route('/')
def index():
    resp = Response(render_template(
        'index.html',
        seo=seo_mod.page(
            '/',
            'Sasha Bagrov — Developer, Founder & Photographer in London',
            'London developer, founder and photographer. Founder of '
            'KidsHustle, a regulated UK marketplace for teenage work. '
            'Python, Swift, GCP and Kubernetes.',
            og_type='profile',
            schema=[seo_mod.person_schema(), seo_mod.website_schema()],
        ),
        timeline=work_data.timeline(),
        acts=work_data.acts(),
        skill_groups=work_data.SKILL_GROUPS,
        skill_names=work_data.skill_names(),
        skill_projects=work_data.skill_projects(),
        work=work_data.WORK,
        languages=work_data.LANGUAGES,
        education=work_data.EDUCATION,
    ))
    return page_cache_headers(resp)

# The tutoring section is retired. Its booking page was public and indexed, so
# send anything still pointing at it to the homepage rather than a dead end.
@app.route('/tutoring')
@app.route('/tutoring/<path:_subpath>')
def tutoring_retired(_subpath=None):
    return redirect(url_for('index'), code=301)


@app.route('/photos')
def photos():
    return page_cache_headers(Response(render_template(
        'photos.html',
        seo=seo_mod.page(
            '/photos',
            'Photography — Sasha Bagrov',
            'Photography by Sasha Bagrov: black-and-white and colour work '
            'shot around London on a Canon EOS R8.',
            schema=[seo_mod.gallery_schema()],
        ),
    )))


#! SEO endpoints
@app.route('/robots.txt')
def robots():
    resp = Response(seo_mod.robots_txt(), mimetype='text/plain')
    resp.headers['Cache-Control'] = 'public, max-age=86400, s-maxage=604800'
    return resp


@app.route('/sitemap.xml')
def sitemap():
    # Templates are the closest honest proxy for when the pages last changed.
    newest = 0
    for folder in (app.template_folder, app.static_folder):
        for root, _dirs, files in os.walk(folder):
            for name in files:
                try:
                    newest = max(newest, os.path.getmtime(os.path.join(root, name)))
                except OSError:
                    continue
    lastmod = datetime.fromtimestamp(newest, tz=timezone.utc).strftime('%Y-%m-%d') \
        if newest else None
    resp = Response(seo_mod.sitemap_xml(lastmod), mimetype='application/xml')
    resp.headers['Cache-Control'] = 'public, max-age=86400, s-maxage=604800'
    return resp


@app.route('/site.webmanifest')
def site_webmanifest():
    resp = jsonify(seo_mod.webmanifest())
    resp.headers['Cache-Control'] = 'public, max-age=604800'
    return resp


# Served from the repo root path crawlers and browsers probe directly. On
# Vercel these are intercepted by vercel.json and served off the CDN; this
# keeps them working locally and as a fallback.
@app.route('/favicon.ico')
def favicon():
    return cache_headers(send_from_directory(
        app.static_folder, 'images/icons/favicon.ico',
        mimetype='image/x-icon',
    ))


@app.route('/apple-touch-icon.png')
@app.route('/apple-touch-icon-precomposed.png')
def apple_touch_icon():
    return cache_headers(send_from_directory(
        app.static_folder, 'images/icons/apple-touch-icon.png',
        mimetype='image/png',
    ))

# Serve minified JS at the real static path so it works behind Vercel too.
@app.route('/static/js/<path:filename>')
def serve_js(filename):
    filepath = os.path.join(app.static_folder, 'js', filename)
    if not os.path.exists(filepath):
        return "Not found", 404
    minified = get_minified(filepath, rjsmin.jsmin)
    resp = Response(minified, mimetype='application/javascript')
    return cache_headers(resp)

# Serve minified CSS at the real static path so it works behind Vercel too.
@app.route('/static/css/<path:filename>')
def serve_css(filename):
    filepath = os.path.join(app.static_folder, 'css', filename)
    if not os.path.exists(filepath):
        return "Not found", 404
    minified = get_minified(filepath, minify_css)
    resp = Response(minified, mimetype='text/css')
    return cache_headers(resp)

@app.route('/cv')
def serve_cv():
    resp = send_from_directory(
        app.static_folder,
        'media/cv.pdf',
        mimetype='application/pdf',
        as_attachment=False,
        download_name='Sasha-Bagrov-CV.pdf',
    )
    return cache_headers(resp)

#! API endpoints
@app.route('/api/images')
def list_images():
    try:
        if not storage_bucket:
            return jsonify({'error': 'Firebase Storage not initialized'}), 500

        images = []
        # List all blobs with prefix 'images/'
        blobs = storage_bucket.list_blobs(prefix='images/')

        # Parse blobs to find images/{id}/{filename}.JPEG
        image_map = {}
        for blob in blobs:
            parts = blob.name.split('/')
            # Expected format: images/{id}/{filename}.JPEG
            if len(parts) == 3 and parts[0] == 'images':
                try:
                    image_id = int(parts[1])
                    filename = parts[2]
                    # Only process JPEG files
                    if filename.lower().endswith(('.jpeg', '.jpg')):
                        # Remove extension for title
                        title = filename.rsplit('.', 1)[0]
                        image_map[image_id] = {
                            'id': image_id,
                            'title': title,
                            'filename': filename
                        }
                except ValueError:
                    continue

        # Sort by ID and return as list
        images = [image_map[key] for key in sorted(image_map.keys())]
        resp = jsonify({'images': images})
        # The gallery can't render until this resolves, and it's a bucket
        # listing that changes only when photos are added.
        resp.headers['Cache-Control'] = (
            'public, max-age=300, s-maxage=3600, stale-while-revalidate=86400'
        )
        return resp

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/images/<int:image_id>')
def serve_optimized_image(image_id):
    try:
        if not storage_bucket:
            return "Firebase Storage not initialized", 500

        quality = int(request.args.get('q', 75))
        width = request.args.get('w')

        # List all blobs in images/{id}/ folder
        prefix = f'images/{image_id}/'
        blobs = list(storage_bucket.list_blobs(prefix=prefix))

        # Find the first JPEG file
        jpeg_blob = None
        for blob in blobs:
            if blob.name.lower().endswith(('.jpeg', '.jpg')):
                jpeg_blob = blob
                break

        if not jpeg_blob:
            return "Image not found", 404

        # Download the image to memory
        image_bytes = jpeg_blob.download_as_bytes()

        # Open and process the image
        with Image.open(io.BytesIO(image_bytes)) as img:
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')

            if width:
                width = int(width)
                ratio = width / img.width
                height = int(img.height * ratio)
                img = img.resize((width, height), Image.Resampling.LANCZOS)

            img_io = io.BytesIO()
            img.save(img_io, 'JPEG', quality=quality, optimize=True)
            img_io.seek(0)

            resp = Response(img_io.getvalue(), mimetype='image/jpeg')
            # Without this every gallery view re-downloaded the full-res
            # original from the bucket and re-encoded it. The output is a
            # pure function of (id, w, q), so the edge can keep it for a year.
            resp.headers['Cache-Control'] = (
                'public, max-age=31536000, s-maxage=31536000, immutable'
            )
            return resp

    except Exception as e:
        return f"Error processing image: {str(e)}", 500




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
