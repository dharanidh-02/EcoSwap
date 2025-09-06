from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from wtforms import (StringField, TextAreaField, SelectField, FloatField, PasswordField, 
                     SubmitField, IntegerField, BooleanField, HiddenField)
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo, ValidationError, Optional
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please choose a different one.')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6)])
    new_password2 = PasswordField('Repeat New Password', 
                                 validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Change Password')

class ProductForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description', validators=[DataRequired()])
    category = SelectField('Category', 
                          choices=[('Electronics', 'Electronics'),
                                 ('Clothing', 'Clothing'),
                                 ('Furniture', 'Furniture'),
                                 ('Books', 'Books'),
                                 ('Sports', 'Sports'),
                                 ('Home & Garden', 'Home & Garden'),
                                 ('Toys', 'Toys'),
                                 ('Other', 'Other')],
                          validators=[DataRequired()])
    condition = SelectField('Condition',
                           choices=[('New', 'New'),
                                   ('Like New', 'Like New'),
                                   ('Good', 'Good'),
                                   ('Fair', 'Fair'),
                                   ('Poor', 'Poor')],
                           validators=[DataRequired()],
                           default='Good')
    price = FloatField('Price ($)', validators=[DataRequired(), NumberRange(min=0.01)])
    location = StringField('Location (City, State)', validators=[Optional(), Length(max=100)])
    image = FileField('Main Product Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    additional_images = MultipleFileField('Additional Images (up to 5)', 
                                         validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    is_featured = BooleanField('Feature this product (premium listing)')
    submit = SubmitField('Add Product')

class SearchForm(FlaskForm):
    search = StringField('Search Products', validators=[Length(max=100)])
    category = SelectField('Category', 
                          choices=[('', 'All Categories'),
                                 ('Electronics', 'Electronics'),
                                 ('Clothing', 'Clothing'),
                                 ('Furniture', 'Furniture'),
                                 ('Books', 'Books'),
                                 ('Sports', 'Sports'),
                                 ('Home & Garden', 'Home & Garden'),
                                 ('Toys', 'Toys'),
                                 ('Other', 'Other')])
    submit = SubmitField('Search')

class ChatForm(FlaskForm):
    message = TextAreaField('Ask me anything about EcoSwap...', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Send')

class EnhancedSearchForm(FlaskForm):
    search = StringField('Search Products', validators=[Optional(), Length(max=100)])
    category = SelectField('Category', 
                          choices=[('', 'All Categories'),
                                 ('Electronics', 'Electronics'),
                                 ('Clothing', 'Clothing'),
                                 ('Furniture', 'Furniture'),
                                 ('Books', 'Books'),
                                 ('Sports', 'Sports'),
                                 ('Home & Garden', 'Home & Garden'),
                                 ('Toys', 'Toys'),
                                 ('Other', 'Other')])
    condition = SelectField('Condition',
                           choices=[('', 'Any Condition'),
                                   ('New', 'New'),
                                   ('Like New', 'Like New'),
                                   ('Good', 'Good'),
                                   ('Fair', 'Fair'),
                                   ('Poor', 'Poor')])
    min_price = FloatField('Min Price ($)', validators=[Optional(), NumberRange(min=0)])
    max_price = FloatField('Max Price ($)', validators=[Optional(), NumberRange(min=0)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    sort_by = SelectField('Sort By',
                         choices=[('newest', 'Newest First'),
                                 ('oldest', 'Oldest First'),
                                 ('price_low', 'Price: Low to High'),
                                 ('price_high', 'Price: High to Low'),
                                 ('rating', 'Best Rated'),
                                 ('popular', 'Most Popular')])
    submit = SubmitField('Search')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating',
                        choices=[(5, '⭐⭐⭐⭐⭐ Excellent'),
                                (4, '⭐⭐⭐⭐ Very Good'),
                                (3, '⭐⭐⭐ Good'),
                                (2, '⭐⭐ Fair'),
                                (1, '⭐ Poor')],
                        validators=[DataRequired()],
                        coerce=int)
    comment = TextAreaField('Review Comment', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Review')

class OfferForm(FlaskForm):
    amount = FloatField('Offer Amount ($)', validators=[DataRequired(), NumberRange(min=0.01)])
    message = TextAreaField('Message (Optional)', validators=[Optional(), Length(max=300)])
    submit = SubmitField('Make Offer')

class MessageForm(FlaskForm):
    recipient_id = HiddenField('Recipient', validators=[DataRequired()])
    product_id = HiddenField('Product', validators=[Optional()])
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Message', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Send Message')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[Optional(), Length(max=50)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=50)])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    location = StringField('Location', validators=[Optional(), Length(max=100)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    avatar = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    submit = SubmitField('Update Profile')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
    
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already registered. Please choose a different one.')
