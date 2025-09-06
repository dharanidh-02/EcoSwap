import os
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import db, bcrypt, csrf
from models import (User, Product, Cart, PurchaseHistory, ProductImage, Review, 
                    Wishlist, Offer, Message, Notification)
from forms import (LoginForm, RegistrationForm, EditProfileForm, ChangePasswordForm, 
                   ProductForm, SearchForm, ChatForm, EnhancedSearchForm, ReviewForm,
                   OfferForm, MessageForm)
from utils import (allowed_file, save_image, save_multiple_images, create_notification,
                   get_condition_badge_class, get_rating_stars)
from ai_assistant import assistant

def register_routes(app):
    
    @app.route('/')
    @app.route('/index')
    def index():
        form = SearchForm()
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '', type=str)
        category = request.args.get('category', '', type=str)
        
        query = Product.query.filter_by(is_sold=False)
        
        if search:
            query = query.filter(Product.title.contains(search))
        
        if category:
            query = query.filter_by(category=category)
        
        products = query.order_by(Product.created_at.desc()).paginate(
            page=page, per_page=12, error_out=False)
        
        return render_template('index.html', title='EcoSwap - Sustainable Marketplace', 
                             products=products, form=form, search=search, category=category)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.password_hash and check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                next_page = request.args.get('next')
                flash('Login successful!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            flash('Invalid email or password', 'danger')
        
        return render_template('login.html', title='Sign In', form=form)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User()
            user.username = form.username.data
            user.email = form.email.data
            user.password_hash = generate_password_hash(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html', title='Register', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return render_template('dashboard.html', title='Dashboard')

    @app.route('/edit_profile', methods=['GET', 'POST'])
    @login_required
    def edit_profile():
        form = EditProfileForm(current_user.username, current_user.email)
        if form.validate_on_submit():
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('dashboard'))
        elif request.method == 'GET':
            form.username.data = current_user.username
            form.email.data = current_user.email
        
        return render_template('dashboard.html', title='Edit Profile', edit_form=form)

    @app.route('/change_password', methods=['GET', 'POST'])
    @login_required
    def change_password():
        form = ChangePasswordForm()
        if form.validate_on_submit():
            if current_user.password_hash and check_password_hash(current_user.password_hash, form.current_password.data):
                current_user.password_hash = generate_password_hash(form.new_password.data)
                db.session.commit()
                flash('Your password has been updated!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Current password is incorrect.', 'danger')
        
        return render_template('dashboard.html', title='Change Password', password_form=form)

    @app.route('/add_product', methods=['GET', 'POST'])
    @login_required
    def add_product():
        form = ProductForm()
        if form.validate_on_submit():
            # Save main image with detailed logging
            image_url = ''
            if form.image.data:
                current_app.logger.info(f"Processing main image: {form.image.data.filename}")
                image_url = save_image(form.image.data)
                if image_url:
                    current_app.logger.info(f"Main image saved successfully: {image_url}")
                else:
                    current_app.logger.error(f"Failed to save main image: {form.image.data.filename}")
                    flash('Main image could not be saved. Please try again with a different image.', 'warning')
            
            # Create product
            product = Product()
            product.title = form.title.data
            product.description = form.description.data
            product.category = form.category.data
            product.condition = form.condition.data
            product.price = form.price.data
            product.location = form.location.data
            product.image_url = image_url
            product.is_featured = form.is_featured.data
            product.owner_id = current_user.id
            db.session.add(product)
            db.session.flush()  # To get the product ID
            
            # Save additional images
            if form.additional_images.data:
                additional_image_urls = save_multiple_images(form.additional_images.data)
                for i, img_url in enumerate(additional_image_urls):
                    product_image = ProductImage()
                    product_image.product_id = product.id
                    product_image.image_url = img_url
                    product_image.order_index = i + 1
                    db.session.add(product_image)
            
            db.session.commit()
            flash('Your product has been listed!', 'success')
            return redirect(url_for('my_listings'))
        
        return render_template('add_product.html', title='Add Product', form=form)

    @app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
    @login_required
    def edit_product(id):
        product = Product.query.get_or_404(id)
        if product.owner != current_user:
            flash('You can only edit your own products.', 'danger')
            return redirect(url_for('index'))
        
        form = ProductForm()
        if form.validate_on_submit():
            product.title = form.title.data
            product.description = form.description.data
            product.category = form.category.data
            product.price = form.price.data
            
            if form.image.data:
                product.image_url = save_image(form.image.data)
            
            db.session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('my_listings'))
        elif request.method == 'GET':
            form.title.data = product.title
            form.description.data = product.description
            form.category.data = product.category
            form.price.data = product.price
        
        return render_template('edit_product.html', title='Edit Product', form=form, product=product)

    @app.route('/delete_product/<int:id>')
    @login_required
    def delete_product(id):
        product = Product.query.get_or_404(id)
        if product.owner != current_user:
            flash('You can only delete your own products.', 'danger')
            return redirect(url_for('index'))
        
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
        return redirect(url_for('my_listings'))

    @app.route('/product/<int:id>')
    def product_detail(id):
        product = Product.query.get_or_404(id)
        
        # Increment view count
        product.views += 1
        db.session.commit()
        
        # Get reviews for this product
        reviews = Review.query.filter_by(product_id=id).order_by(Review.created_at.desc()).all()
        
        # Check if current user has this in wishlist
        in_wishlist = False
        if current_user.is_authenticated:
            wishlist_item = Wishlist.query.filter_by(user_id=current_user.id, product_id=id).first()
            in_wishlist = wishlist_item is not None
        
        # Get offers for this product (if owner)
        offers = []
        if current_user.is_authenticated and product.owner == current_user:
            offers = Offer.query.filter_by(product_id=id).order_by(Offer.created_at.desc()).all()
        
        # Similar products (same category, different owner)
        similar_products = Product.query.filter(
            Product.category == product.category,
            Product.id != product.id,
            Product.is_sold == False,
            Product.owner_id != product.owner_id
        ).limit(4).all()
        
        return render_template('product_detail.html', title=product.title, 
                             product=product, reviews=reviews, in_wishlist=in_wishlist,
                             offers=offers, similar_products=similar_products)

    @app.route('/my_listings')
    @login_required
    def my_listings():
        page = request.args.get('page', 1, type=int)
        products = Product.query.filter_by(owner_id=current_user.id).order_by(
            Product.created_at.desc()).paginate(
            page=page, per_page=12, error_out=False)
        
        return render_template('my_listings.html', title='My Listings', products=products)

    @app.route('/add_to_cart/<int:id>')
    @login_required
    def add_to_cart(id):
        product = Product.query.get_or_404(id)
        
        if product.owner == current_user:
            flash('You cannot add your own product to cart.', 'warning')
            return redirect(url_for('product_detail', id=id))
        
        if product.is_sold:
            flash('This product is already sold.', 'warning')
            return redirect(url_for('product_detail', id=id))
        
        existing_cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=id).first()
        if existing_cart_item:
            flash('Product is already in your cart.', 'info')
            return redirect(url_for('cart'))
        
        cart_item = Cart()
        cart_item.user_id = current_user.id
        cart_item.product_id = id
        db.session.add(cart_item)
        db.session.commit()
        flash('Product added to cart!', 'success')
        return redirect(url_for('cart'))

    @app.route('/remove_from_cart/<int:id>')
    @login_required
    def remove_from_cart(id):
        cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=id).first_or_404()
        db.session.delete(cart_item)
        db.session.commit()
        flash('Product removed from cart.', 'info')
        return redirect(url_for('cart'))

    @app.route('/cart')
    @login_required
    def cart():
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        total = sum(item.product.price for item in cart_items if not item.product.is_sold)
        return render_template('cart.html', title='Shopping Cart', cart_items=cart_items, total=total)

    @app.route('/checkout')
    @login_required
    def checkout():
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        
        if not cart_items:
            flash('Your cart is empty.', 'warning')
            return redirect(url_for('cart'))
        
        # Process purchase
        for cart_item in cart_items:
            if not cart_item.product.is_sold:
                # Create purchase history
                purchase = PurchaseHistory()
                purchase.user_id = current_user.id
                purchase.product_id = cart_item.product_id
                purchase.price_paid = cart_item.product.price
                db.session.add(purchase)
                
                # Mark product as sold
                cart_item.product.is_sold = True
                
                # Remove from cart
                db.session.delete(cart_item)
        
        db.session.commit()
        flash('Purchase completed successfully!', 'success')
        return redirect(url_for('purchase_history'))

    @app.route('/purchase_history')
    @login_required
    def purchase_history():
        page = request.args.get('page', 1, type=int)
        purchases = PurchaseHistory.query.filter_by(user_id=current_user.id).order_by(
            PurchaseHistory.purchase_date.desc()).paginate(
            page=page, per_page=10, error_out=False)
        
        return render_template('purchase_history.html', title='Purchase History', purchases=purchases)

    @app.route('/ai_chat', methods=['GET', 'POST'])
    def ai_chat():
        form = ChatForm()
        chat_history = request.form.getlist('chat_history') if request.method == 'POST' else []
        
        if form.validate_on_submit():
            user_message = form.message.data
            
            # Get AI response
            ai_response = assistant.get_response(user_message)
            
            # Add to chat history
            chat_history.append({
                'role': 'user',
                'content': user_message,
                'timestamp': 'now'
            })
            chat_history.append({
                'role': 'assistant',
                'content': ai_response,
                'timestamp': 'now'
            })
            
            form.message.data = ''  # Clear the form
        
        return render_template('ai_chat.html', title='AI Assistant', form=form, chat_history=chat_history)

    @app.route('/api/ai_chat', methods=['POST'])
    @csrf.exempt
    def api_ai_chat():
        """API endpoint for AJAX chat requests"""
        try:
            data = request.get_json()
            user_message = data.get('message', '')
            conversation_history = data.get('history', [])
            
            if not user_message:
                return {'error': 'Message is required'}, 400
            
            # Get AI response
            ai_response = assistant.get_response(user_message, conversation_history)
            
            return {
                'response': ai_response,
                'status': 'success'
            }
        except Exception as e:
            return {'error': 'Failed to get AI response', 'status': 'error'}, 500

    @app.route('/api/quick_help/<topic>')
    def api_quick_help(topic):
        """API endpoint for quick help responses"""
        try:
            response = assistant.get_quick_help(topic)
            return {
                'response': response,
                'status': 'success'
            }
        except Exception as e:
            return {'error': 'Failed to get help', 'status': 'error'}, 500

    # Enhanced Search Routes
    @app.route('/search')
    def enhanced_search():
        form = EnhancedSearchForm()
        page = request.args.get('page', 1, type=int)
        
        # Get search parameters
        search = request.args.get('search', '', type=str)
        category = request.args.get('category', '', type=str)
        condition = request.args.get('condition', '', type=str)
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        location = request.args.get('location', '', type=str)
        sort_by = request.args.get('sort_by', 'newest', type=str)
        
        # Build query
        query = Product.query.filter_by(is_sold=False)
        
        if search:
            query = query.filter(Product.title.contains(search) | Product.description.contains(search))
        if category:
            query = query.filter_by(category=category)
        if condition:
            query = query.filter_by(condition=condition)
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        if location:
            query = query.filter(Product.location.contains(location))
        
        # Apply sorting
        if sort_by == 'oldest':
            query = query.order_by(Product.created_at.asc())
        elif sort_by == 'price_low':
            query = query.order_by(Product.price.asc())
        elif sort_by == 'price_high':
            query = query.order_by(Product.price.desc())
        elif sort_by == 'popular':
            query = query.order_by(Product.views.desc())
        else:  # newest
            query = query.order_by(Product.created_at.desc())
        
        products = query.paginate(page=page, per_page=12, error_out=False)
        
        return render_template('enhanced_search.html', title='Advanced Search', 
                             products=products, form=form, search=search, 
                             category=category, condition=condition, min_price=min_price,
                             max_price=max_price, location=location, sort_by=sort_by)

    # Wishlist Routes
    @app.route('/wishlist')
    @login_required
    def wishlist():
        page = request.args.get('page', 1, type=int)
        wishlist_items = Wishlist.query.filter_by(user_id=current_user.id).order_by(
            Wishlist.added_at.desc()).paginate(page=page, per_page=12, error_out=False)
        
        return render_template('wishlist.html', title='My Wishlist', wishlist_items=wishlist_items)

    @app.route('/add_to_wishlist/<int:id>')
    @login_required
    def add_to_wishlist(id):
        product = Product.query.get_or_404(id)
        
        if product.owner == current_user:
            flash('You cannot add your own product to wishlist.', 'warning')
            return redirect(url_for('product_detail', id=id))
        
        existing_item = Wishlist.query.filter_by(user_id=current_user.id, product_id=id).first()
        if existing_item:
            flash('Product is already in your wishlist.', 'info')
        else:
            wishlist_item = Wishlist()
            wishlist_item.user_id = current_user.id
            wishlist_item.product_id = id
            db.session.add(wishlist_item)
            db.session.commit()
            flash('Product added to wishlist!', 'success')
        
        return redirect(url_for('product_detail', id=id))

    @app.route('/remove_from_wishlist/<int:id>')
    @login_required
    def remove_from_wishlist(id):
        wishlist_item = Wishlist.query.filter_by(user_id=current_user.id, product_id=id).first_or_404()
        db.session.delete(wishlist_item)
        db.session.commit()
        flash('Product removed from wishlist.', 'info')
        return redirect(url_for('wishlist'))

    # Review Routes
    @app.route('/add_review/<int:product_id>', methods=['GET', 'POST'])
    @login_required
    def add_review(product_id):
        product = Product.query.get_or_404(product_id)
        
        # Check if user has purchased this product
        purchase = PurchaseHistory.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if not purchase:
            flash('You can only review products you have purchased.', 'warning')
            return redirect(url_for('product_detail', id=product_id))
        
        # Check if user already reviewed this product
        existing_review = Review.query.filter_by(user_id=current_user.id, product_id=product_id).first()
        if existing_review:
            flash('You have already reviewed this product.', 'info')
            return redirect(url_for('product_detail', id=product_id))
        
        form = ReviewForm()
        if form.validate_on_submit():
            review = Review(
                product_id=product_id,
                user_id=current_user.id,
                rating=form.rating.data,
                comment=form.comment.data
            )
            db.session.add(review)
            db.session.commit()
            
            # Create notification for product owner
            create_notification(
                product.owner_id,
                'New Review',
                f'{current_user.username} reviewed your product "{product.title}"',
                'info',
                url_for('product_detail', id=product_id)
            )
            
            flash('Review added successfully!', 'success')
            return redirect(url_for('product_detail', id=product_id))
        
        return render_template('add_review.html', title='Add Review', form=form, product=product)

    # Offer Routes
    @app.route('/make_offer/<int:product_id>', methods=['GET', 'POST'])
    @login_required
    def make_offer(product_id):
        product = Product.query.get_or_404(product_id)
        
        if product.owner == current_user:
            flash('You cannot make an offer on your own product.', 'warning')
            return redirect(url_for('product_detail', id=product_id))
        
        if product.is_sold:
            flash('This product is already sold.', 'warning')
            return redirect(url_for('product_detail', id=product_id))
        
        form = OfferForm()
        if form.validate_on_submit():
            offer = Offer(
                product_id=product_id,
                user_id=current_user.id,
                amount=form.amount.data,
                message=form.message.data
            )
            db.session.add(offer)
            db.session.commit()
            
            # Create notification for product owner
            create_notification(
                product.owner_id,
                'New Offer',
                f'{current_user.username} made an offer of ${form.amount.data:.2f} for "{product.title}"',
                'info',
                url_for('product_detail', id=product_id)
            )
            
            flash('Offer submitted successfully!', 'success')
            return redirect(url_for('product_detail', id=product_id))
        
        return render_template('make_offer.html', title='Make Offer', form=form, product=product)

    @app.route('/respond_to_offer/<int:offer_id>/<action>')
    @login_required
    def respond_to_offer(offer_id, action):
        offer = Offer.query.get_or_404(offer_id)
        
        if offer.product.owner != current_user:
            flash('You can only respond to offers on your products.', 'danger')
            return redirect(url_for('index'))
        
        if action == 'accept':
            offer.status = 'accepted'
            # Mark product as sold
            offer.product.is_sold = True
            # Create purchase history
            purchase = PurchaseHistory(
                user_id=offer.user_id,
                product_id=offer.product_id,
                price_paid=offer.amount
            )
            db.session.add(purchase)
            # Update user stats
            current_user.total_sales += 1
            offer.buyer.total_purchases += 1
            
            # Create notification for buyer
            create_notification(
                offer.user_id,
                'Offer Accepted!',
                f'Your offer for "{offer.product.title}" has been accepted!',
                'success',
                url_for('purchase_history')
            )
            
            flash('Offer accepted! Product marked as sold.', 'success')
        elif action == 'reject':
            offer.status = 'rejected'
            # Create notification for buyer
            create_notification(
                offer.user_id,
                'Offer Declined',
                f'Your offer for "{offer.product.title}" was declined.',
                'info',
                url_for('product_detail', id=offer.product_id)
            )
            flash('Offer rejected.', 'info')
        
        db.session.commit()
        return redirect(url_for('product_detail', id=offer.product_id))

    # User Profile Routes
    @app.route('/profile/<username>')
    def user_profile(username):
        user = User.query.filter_by(username=username).first_or_404()
        
        # Get user's products
        page = request.args.get('page', 1, type=int)
        products = Product.query.filter_by(owner_id=user.id, is_sold=False).order_by(
            Product.created_at.desc()).paginate(page=page, per_page=8, error_out=False)
        
        # Get user's reviews (as seller)
        seller_reviews = []
        for product in user.products:
            seller_reviews.extend(product.reviews)
        
        return render_template('user_profile.html', title=f'{user.username} - Profile', 
                             user=user, products=products, seller_reviews=seller_reviews)

    # Messaging Routes
    @app.route('/messages')
    @login_required
    def messages():
        page = request.args.get('page', 1, type=int)
        received_messages = Message.query.filter_by(recipient_id=current_user.id).order_by(
            Message.created_at.desc()).paginate(page=page, per_page=10, error_out=False)
        
        sent_messages = Message.query.filter_by(sender_id=current_user.id).order_by(
            Message.created_at.desc()).all()
        
        return render_template('messages.html', title='Messages', 
                             received_messages=received_messages, sent_messages=sent_messages)

    @app.route('/send_message/<int:recipient_id>', methods=['GET', 'POST'])
    @app.route('/send_message/<int:recipient_id>/<int:product_id>', methods=['GET', 'POST'])
    @login_required
    def send_message(recipient_id, product_id=None):
        recipient = User.query.get_or_404(recipient_id)
        product = Product.query.get(product_id) if product_id else None
        
        form = MessageForm()
        form.recipient_id.data = recipient_id
        if product:
            form.product_id.data = product_id
            form.subject.data = f'Inquiry about: {product.title}'
        
        if form.validate_on_submit():
            message = Message(
                sender_id=current_user.id,
                recipient_id=form.recipient_id.data,
                product_id=form.product_id.data if form.product_id.data else None,
                subject=form.subject.data,
                content=form.content.data
            )
            db.session.add(message)
            db.session.commit()
            
            # Create notification
            create_notification(
                recipient_id,
                'New Message',
                f'{current_user.username} sent you a message',
                'info',
                url_for('messages')
            )
            
            flash('Message sent successfully!', 'success')
            return redirect(url_for('messages'))
        
        return render_template('send_message.html', title='Send Message', 
                             form=form, recipient=recipient, product=product)

    @app.route('/mark_message_read/<int:message_id>')
    @login_required
    def mark_message_read(message_id):
        message = Message.query.get_or_404(message_id)
        
        if message.recipient != current_user:
            flash('Access denied.', 'danger')
            return redirect(url_for('messages'))
        
        message.is_read = True
        db.session.commit()
        return redirect(url_for('messages'))

    # Notifications Routes
    @app.route('/notifications')
    @login_required
    def notifications():
        page = request.args.get('page', 1, type=int)
        user_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
            Notification.created_at.desc()).paginate(page=page, per_page=15, error_out=False)
        
        return render_template('notifications.html', title='Notifications', 
                             notifications=user_notifications)

    @app.route('/mark_notification_read/<int:notification_id>')
    @login_required
    def mark_notification_read(notification_id):
        notification = Notification.query.get_or_404(notification_id)
        
        if notification.user != current_user:
            flash('Access denied.', 'danger')
            return redirect(url_for('notifications'))
        
        notification.is_read = True
        db.session.commit()
        
        if notification.link:
            return redirect(notification.link)
        return redirect(url_for('notifications'))

    @app.route('/mark_all_notifications_read')
    @login_required
    def mark_all_notifications_read():
        Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
        db.session.commit()
        flash('All notifications marked as read.', 'success')
        return redirect(url_for('notifications'))

    # Analytics Dashboard

    @app.route('/analytics')
    @login_required
    def analytics():
        # Get user's selling statistics
        total_products = len(current_user.products)
        sold_products = len([p for p in current_user.products if p.is_sold])
        active_products = total_products - sold_products
        total_views = sum(p.views for p in current_user.products)
        total_revenue = sum(p.purchase_history[0].price_paid for p in current_user.products if p.purchase_history)
        
        # Get monthly sales data (last 6 months)
        from datetime import datetime, timedelta
        import calendar
        
        monthly_sales = {}
        for i in range(6):
            date = datetime.utcnow() - timedelta(days=30*i)
            month_name = calendar.month_name[date.month]
            year = date.year
            key = f"{month_name} {year}"
            
            # Count sales for this month
            month_start = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            next_month = month_start.replace(month=month_start.month + 1) if month_start.month < 12 else month_start.replace(year=month_start.year + 1, month=1)
            
            sales_count = PurchaseHistory.query.join(Product).filter(
                Product.owner_id == current_user.id,
                PurchaseHistory.purchase_date >= month_start,
                PurchaseHistory.purchase_date < next_month
            ).count()
            
            monthly_sales[key] = sales_count
        
        # Category breakdown
        category_stats = {}
        for product in current_user.products:
            if product.category not in category_stats:
                category_stats[product.category] = {'total': 0, 'sold': 0}
            category_stats[product.category]['total'] += 1
            if product.is_sold:
                category_stats[product.category]['sold'] += 1
        
        return render_template('analytics.html', title='Analytics Dashboard',
                             total_products=total_products, sold_products=sold_products,
                             active_products=active_products, total_views=total_views,
                             total_revenue=total_revenue, monthly_sales=monthly_sales,
                             category_stats=category_stats)