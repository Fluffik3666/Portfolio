from flask import Flask, render_template, request, Response, jsonify, session, send_file
from PIL import Image
import hashlib
import io
import os
import re
import json
import cssmin
import rjsmin
import stripe

try:
    from src.firebase_config import initialize_firebase
    from src.stripe_bluprnt import blueprint
except ImportError:
    from firebase_config import initialize_firebase
    from stripe_bluprnt import blueprint

stripe.api_key = os.getenv("STRIPE_API_KEY")

app = Flask(__name__, template_folder='../src/templates', static_folder='../src/static')
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-change-me')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.register_blueprint(blueprint)

storage_bucket = initialize_firebase()

_min_cache = {}
_asset_version_cache = {}

def asset_version(filename):
    """Short content hash for a static file, or None if it can't be read.

    Appended to static URLs as ?v= so a cached stylesheet can never be paired
    with newer markup that expects different rules.
    """
    filepath = os.path.join(app.static_folder, filename)
    try:
        mtime = os.path.getmtime(filepath)
    except OSError:
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
    """Cache hashed URLs hard; anything unversioned only briefly."""
    if request.args.get('v'):
        resp.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    else:
        resp.headers['Cache-Control'] = 'public, max-age=3600'
    return resp

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
            body = cssmin.cssmin(body)
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

#! serve our important routes
@app.route('/')
def index():
    return render_template('index.html', logged_in='user_uid' in session)

@app.route('/photos')
def photos():
    return render_template('photos.html')

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
    minified = get_minified(filepath, cssmin.cssmin)
    resp = Response(minified, mimetype='text/css')
    return cache_headers(resp)

@app.route('/cv')
def serve_cv():
    return send_file('../src/static/media/cv.pdf', as_attachment=False)

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
        return jsonify({'images': images})

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

            return Response(img_io.getvalue(), mimetype='image/jpeg')

    except Exception as e:
        return f"Error processing image: {str(e)}", 500




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
