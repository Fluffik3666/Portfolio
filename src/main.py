from flask import Flask, render_template, request, Response, jsonify, session
from PIL import Image
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

# Preserve the contents of these blocks verbatim while collapsing surrounding
# markup, so we never mangle inline JS (e.g. `//` comments) or pre-formatted text.
_PRESERVE_RE = re.compile(
    r'<(script|style|pre|textarea)\b[^>]*>.*?</\1>',
    flags=re.DOTALL | re.IGNORECASE,
)

def minify_html(html):
    stash = []

    def _protect(match):
        stash.append(match.group(0))
        return f'\x00{len(stash) - 1}\x00'

    html = _PRESERVE_RE.sub(_protect, html)
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
    resp.headers['Cache-Control'] = 'public, max-age=3600'
    return resp

# Serve minified CSS at the real static path so it works behind Vercel too.
@app.route('/static/css/<path:filename>')
def serve_css(filename):
    filepath = os.path.join(app.static_folder, 'css', filename)
    if not os.path.exists(filepath):
        return "Not found", 404
    minified = get_minified(filepath, cssmin.cssmin)
    resp = Response(minified, mimetype='text/css')
    resp.headers['Cache-Control'] = 'public, max-age=3600'
    return resp

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
