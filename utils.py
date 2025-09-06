import os
import secrets
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(form_image, max_size=(800, 800)):
    """Save uploaded image and return the filename"""
    if not form_image or not allowed_file(form_image.filename):
        return ''
    
    # Generate random filename
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    image_fn = random_hex + f_ext
    image_path = os.path.join(current_app.root_path, 'static/uploads', image_fn)
    
    # Resize image to reduce file size
    try:
        img = Image.open(form_image)
        # Resize if image is too large
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        img.save(image_path, optimize=True, quality=85)
        return f'uploads/{image_fn}'
    except Exception as e:
        current_app.logger.error(f'Error saving image: {e}')
        return ''

def save_multiple_images(form_images, max_files=5):
    """Save multiple uploaded images and return list of filenames"""
    if not form_images:
        return []
    
    saved_images = []
    count = 0
    
    for form_image in form_images:
        if count >= max_files:
            break
        
        if form_image and form_image.filename and allowed_file(form_image.filename):
            image_url = save_image(form_image)
            if image_url:
                saved_images.append(image_url)
                count += 1
    
    return saved_images

def create_notification(user_id, title, message, notification_type='info', link=None):
    """Create a notification for a user"""
    from models import Notification
    from app import db
    
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notification_type,
        link=link
    )
    db.session.add(notification)
    db.session.commit()
    return notification

def get_condition_badge_class(condition):
    """Return Bootstrap badge class for product condition"""
    condition_classes = {
        'New': 'bg-success',
        'Like New': 'bg-info',
        'Good': 'bg-primary',
        'Fair': 'bg-warning',
        'Poor': 'bg-danger'
    }
    return condition_classes.get(condition, 'bg-secondary')

def get_rating_stars(rating):
    """Return HTML for star rating display"""
    if not rating:
        return '<span class="text-muted">No rating</span>'
    
    full_stars = int(rating)
    half_star = rating - full_stars >= 0.5
    empty_stars = 5 - full_stars - (1 if half_star else 0)
    
    html = '⭐' * full_stars
    if half_star:
        html += '⭐'  # For simplicity, using full star for half
    html += '☆' * empty_stars
    
    return f'<span class="text-warning">{html}</span> <small class="text-muted">({rating:.1f})</small>'
