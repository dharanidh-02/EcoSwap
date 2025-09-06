import os
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from app import db, bcrypt, csrf
from models import User, Product, Cart, PurchaseHistory
from forms import (LoginForm, RegistrationForm, EditProfileForm, ChangePasswordForm, 
                   ProductForm, SearchForm, ChatForm)
from utils import allowed_file, save_image
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
            if user and check_password_hash(user.password_hash, form.password.data):
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
            user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=generate_password_hash(form.password.data)
            )
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
            if check_password_hash(current_user.password_hash, form.current_password.data):
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
            image_url = ''
            if form.image.data:
                image_url = save_image(form.image.data)
            
            product = Product(
                title=form.title.data,
                description=form.description.data,
                category=form.category.data,
                price=form.price.data,
                image_url=image_url,
                owner_id=current_user.id
            )
            db.session.add(product)
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
        return render_template('product_detail.html', title=product.title, product=product)

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
        
        cart_item = Cart(user_id=current_user.id, product_id=id)
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
                purchase = PurchaseHistory(
                    user_id=current_user.id,
                    product_id=cart_item.product_id,
                    price_paid=cart_item.product.price
                )
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