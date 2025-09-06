from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, FloatField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo, ValidationError
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

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
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
    price = FloatField('Price ($)', validators=[DataRequired(), NumberRange(min=0.01)])
    image = FileField('Product Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
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
