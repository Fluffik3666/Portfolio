from datetime import datetime
from better_profanity import profanity
from firebase_config import initialize_firebase, ADMIN_EMAIL
import uuid

db, auth = initialize_firebase()

class BlogService:
    def __init__(self):
        self.db = db
        self.auth = auth
        profanity.load_censor_words()
    
    def create_post(self, title, content, author_email, author_name):
        """Create a new blog post"""
        try:
            post_data = {
                'id': str(uuid.uuid4()),
                'title': title,
                'content': content,
                'author_email': author_email,
                'author_name': author_name,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'published': True,
                'comment_count': 0
            }
            
            doc_ref = self.db.collection('blog_posts').document(post_data['id'])
            doc_ref.set(post_data)
            return post_data
        except Exception as e:
            print(f"Error creating post: {e}")
            return None
    
    def get_all_posts(self, limit=10):
        """Get all published blog posts"""
        try:
            posts = []
            query = (self.db.collection('blog_posts')
                    .where('published', '==', True)
                    .order_by('created_at', direction='DESCENDING')
                    .limit(limit))
            
            docs = query.stream()
            for doc in docs:
                post_data = doc.to_dict()
                posts.append(post_data)
            
            return posts
        except Exception as e:
            print(f"Error getting posts: {e}")
            return []
    
    def get_post_by_id(self, post_id):
        """Get a specific blog post by ID"""
        try:
            doc_ref = self.db.collection('blog_posts').document(post_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
        except Exception as e:
            print(f"Error getting post: {e}")
            return None
    
    def update_post(self, post_id, title=None, content=None):
        """Update a blog post"""
        try:
            doc_ref = self.db.collection('blog_posts').document(post_id)
            update_data = {'updated_at': datetime.now()}
            
            if title:
                update_data['title'] = title
            if content:
                update_data['content'] = content
            
            doc_ref.update(update_data)
            return True
        except Exception as e:
            print(f"Error updating post: {e}")
            return False
    
    def delete_post(self, post_id):
        """Delete a blog post"""
        try:
            # Delete all comments first
            comments_ref = self.db.collection('comments').where('post_id', '==', post_id)
            comments = comments_ref.stream()
            for comment in comments:
                comment.reference.delete()
            
            # Delete the post
            self.db.collection('blog_posts').document(post_id).delete()
            return True
        except Exception as e:
            print(f"Error deleting post: {e}")
            return False
    
    def add_comment(self, post_id, author_name, author_email, content):
        """Add a comment to a blog post"""
        try:
            # Filter profanity
            clean_content = profanity.censor(content)
            clean_author_name = profanity.censor(author_name)
            
            comment_data = {
                'id': str(uuid.uuid4()),
                'post_id': post_id,
                'author_name': clean_author_name,
                'author_email': author_email,
                'content': clean_content,
                'created_at': datetime.now(),
                'approved': True  # Auto-approve for now, can add moderation later
            }
            
            # Add comment
            doc_ref = self.db.collection('comments').document(comment_data['id'])
            doc_ref.set(comment_data)
            
            # Update post comment count
            from google.cloud import firestore
            post_ref = self.db.collection('blog_posts').document(post_id)
            post_ref.update({
                'comment_count': firestore.Increment(1)
            })
            
            return comment_data
        except Exception as e:
            print(f"Error adding comment: {e}")
            return None
    
    def get_comments_for_post(self, post_id):
        """Get all approved comments for a post"""
        try:
            comments = []
            query = (self.db.collection('comments')
                    .where('post_id', '==', post_id)
                    .where('approved', '==', True)
                    .order_by('created_at'))
            
            docs = query.stream()
            for doc in docs:
                comment_data = doc.to_dict()
                comments.append(comment_data)
            
            return comments
        except Exception as e:
            print(f"Error getting comments: {e}")
            return []
    
    def delete_comment(self, comment_id):
        """Delete a comment"""
        try:
            # Get comment to find post_id
            comment_ref = self.db.collection('comments').document(comment_id)
            comment = comment_ref.get()
            
            if comment.exists:
                post_id = comment.to_dict()['post_id']
                comment_ref.delete()
                
                # Update post comment count
                from google.cloud import firestore
                post_ref = self.db.collection('blog_posts').document(post_id)
                post_ref.update({
                    'comment_count': firestore.Increment(-1)
                })
                return True
            return False
        except Exception as e:
            print(f"Error deleting comment: {e}")
            return False
    
    def is_admin(self, email):
        """Check if user is admin"""
        return email == ADMIN_EMAIL