from flask import Flask, send_from_directory, render_template, request, Response
from PIL import Image
import io
import os
import json
from src.firebase_config import initialize_firebase

app = Flask(__name__, template_folder='../src/templates', static_folder='../src/static')

# Initialize Firebase Storage
storage_bucket = initialize_firebase()

#! serve our important routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/photos')
def photos():
    return render_template('photos.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/skills')
def skills():
    return render_template('skills.html')

#! serve our static files
#! routes go /content/static/<path>
@app.route('/content/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/images/optimized/<path:filename>')
def serve_optimized_image(filename):
    try:
        if not storage_bucket:
            return "Firebase Storage not initialized", 500

        quality = int(request.args.get('q', 75))
        width = request.args.get('w')

        # Get the blob from Firebase Storage
        blob = storage_bucket.blob(f'images/{filename}')

        if not blob.exists():
            return "Image not found", 404

        # Download the image to memory
        image_bytes = blob.download_as_bytes()

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