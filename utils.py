import os
import secrets
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(form_image):
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
        if img.width > 800 or img.height > 800:
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        img.save(image_path, optimize=True, quality=85)
        return f'uploads/{image_fn}'
    except Exception as e:
        current_app.logger.error(f'Error saving image: {e}')
        return ''
