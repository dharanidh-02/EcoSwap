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
    if not form_image:
        current_app.logger.warning("No image file provided")
        return ''
    
    if not form_image.filename:
        current_app.logger.warning("Image file has no filename")
        return ''
    
    if not allowed_file(form_image.filename):
        current_app.logger.warning(f"File type not allowed: {form_image.filename}")
        return ''
    
    # Generate random filename
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    image_fn = random_hex + f_ext
    image_path = os.path.join(current_app.root_path, 'static/uploads', image_fn)
    
    # Ensure uploads directory exists
    upload_dir = os.path.join(current_app.root_path, 'static/uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Resize image to reduce file size
    try:
        current_app.logger.info(f"Opening image: {form_image.filename}")
        img = Image.open(form_image)
        current_app.logger.info(f"Image size: {img.width}x{img.height}")
        
        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Resize if image is too large
        if img.width > max_size[0] or img.height > max_size[1]:
            current_app.logger.info(f"Resizing image from {img.width}x{img.height} to max {max_size}")
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        current_app.logger.info(f"Saving image to: {image_path}")
        img.save(image_path, optimize=True, quality=85)
        current_app.logger.info(f"Image saved successfully: {image_fn}")
        return f'uploads/{image_fn}'
    except Exception as e:
        current_app.logger.error(f'Error saving image {form_image.filename}: {str(e)}')
        import traceback
        current_app.logger.error(f'Traceback: {traceback.format_exc()}')
        return ''

def save_multiple_images(form_images, max_files=5):
    """Save multiple uploaded images and return list of filenames"""
    if not form_images:
        current_app.logger.info("No additional images provided")
        return []
    
    saved_images = []
    count = 0
    
    for i, form_image in enumerate(form_images):
        if count >= max_files:
            current_app.logger.info(f"Reached max file limit ({max_files}), skipping remaining images")
            break
        
        current_app.logger.info(f"Processing additional image {i+1}: {getattr(form_image, 'filename', 'Unknown')}")
        
        if form_image and form_image.filename and allowed_file(form_image.filename):
            image_url = save_image(form_image)
            if image_url:
                saved_images.append(image_url)
                count += 1
                current_app.logger.info(f"Successfully processed additional image {i+1}")
            else:
                current_app.logger.error(f"Failed to save additional image {i+1}: {form_image.filename}")
        else:
            current_app.logger.warning(f"Invalid or empty additional image {i+1}")
    
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
