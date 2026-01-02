from flask import Flask, send_from_directory, render_template, request, Response, jsonify
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

#! serve our static files
#! routes go /content/static/<path>
@app.route('/content/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

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