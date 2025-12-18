from flask import Flask, send_from_directory, render_template, request, Response, redirect, url_for, flash, session, jsonify
from PIL import Image
import io
import os
import json
from src.blog_service import BlogService
from src.firebase_config import ADMIN_EMAIL

app = Flask(__name__, template_folder='../src/templates', static_folder='../src/static')
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

blog_service = BlogService()

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

@app.route('/blog')
def blog():
    posts = blog_service.get_all_posts()
    return render_template('blog.html', posts=posts)

@app.route('/blog/post/<post_id>')
def blog_post(post_id):
    post = blog_service.get_post_by_id(post_id)
    if not post:
        return "Post not found", 404
    
    comments = blog_service.get_comments_for_post(post_id)
    return render_template('blog_post.html', post=post, comments=comments)

@app.route('/blog/post/<post_id>/comment', methods=['POST'])
def add_comment(post_id):
    author_name = request.form.get('author_name')
    author_email = request.form.get('author_email')
    content = request.form.get('content')
    
    if not all([author_name, author_email, content]):
        flash('All fields are required')
        return redirect(url_for('blog_post', post_id=post_id))
    
    comment = blog_service.add_comment(post_id, author_name, author_email, content)
    if comment:
        flash('Comment added successfully!')
    else:
        flash('Error adding comment')
    
    return redirect(url_for('blog_post', post_id=post_id))

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        # Pass Firebase config to template
        firebase_config = {
            'FIREBASE_API_KEY': os.getenv('FIREBASE_API_KEY'),
            'FIREBASE_AUTH_DOMAIN': os.getenv('FIREBASE_AUTH_DOMAIN'),
            'FIREBASE_PROJECT_ID': os.getenv('FIREBASE_PROJECT_ID'),
            'FIREBASE_STORAGE_BUCKET': os.getenv('FIREBASE_STORAGE_BUCKET'),
            'FIREBASE_MESSAGING_SENDER_ID': os.getenv('FIREBASE_MESSAGING_SENDER_ID'),
            'FIREBASE_APP_ID': os.getenv('FIREBASE_APP_ID')
        }
        return render_template('admin_login.html', config=firebase_config)
    
    posts = blog_service.get_all_posts(limit=50)
    return render_template('admin.html', posts=posts)

@app.route('/admin/auth', methods=['POST'])
def admin_auth():
    try:
        id_token = request.json.get('idToken')
        if not id_token:
            return jsonify({'success': False, 'error': 'No token provided'}), 400
        
        # Verify the token with Firebase Admin SDK
        from firebase_admin import auth
        decoded_token = auth.verify_id_token(id_token)
        email = decoded_token.get('email')
        
        if email == ADMIN_EMAIL:
            session['admin_logged_in'] = True
            session['admin_email'] = email
            session['admin_name'] = decoded_token.get('name', email)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
    
    except Exception as e:
        print(f"Auth error: {e}")
        return jsonify({'success': False, 'error': 'Invalid token'}), 400

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin'))

@app.route('/admin/post/new', methods=['GET', 'POST'])
def admin_new_post():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if title and content:
            post = blog_service.create_post(
                title, content, 
                session.get('admin_email'), 
                session.get('admin_name')
            )
            if post:
                flash('Post created successfully!')
                return redirect(url_for('admin'))
            else:
                flash('Error creating post')
    
    return render_template('admin_new_post.html')

@app.route('/admin/post/<post_id>/edit', methods=['GET', 'POST'])
def admin_edit_post(post_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    
    post = blog_service.get_post_by_id(post_id)
    if not post:
        return "Post not found", 404
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if blog_service.update_post(post_id, title, content):
            flash('Post updated successfully!')
            return redirect(url_for('admin'))
        else:
            flash('Error updating post')
    
    return render_template('admin_edit_post.html', post=post)

@app.route('/admin/post/<post_id>/delete', methods=['POST'])
def admin_delete_post(post_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    
    if blog_service.delete_post(post_id):
        flash('Post deleted successfully!')
    else:
        flash('Error deleting post')
    
    return redirect(url_for('admin'))

@app.route('/admin/comment/<comment_id>/delete', methods=['POST'])
def admin_delete_comment(comment_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    
    if blog_service.delete_comment(comment_id):
        flash('Comment deleted successfully!')
    else:
        flash('Error deleting comment')
    
    return redirect(request.referrer or url_for('admin'))

#! serve our static files
#! routes go /content/static/<path>
@app.route('/content/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/images/optimized/<path:filename>')
def serve_optimized_image(filename):
    try:
        quality = int(request.args.get('q', 75))
        width = request.args.get('w')
        
        full_path = os.path.join(app.static_folder, 'images', filename)
        
        if not os.path.exists(full_path):
            return "Image not found", 404
        
        with Image.open(full_path) as img:
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