from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, FloatField, BooleanField, PasswordField, MultipleFileField
from wtforms.validators import DataRequired, Email, Length, NumberRange
from wtforms.widgets import TextArea

class BidRequestForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    job_type = SelectField('Job Type', choices=[
        ('', 'Select Job Type'),
        ('industrial_install', 'Industrial Installation'),
        ('3d_lidar_scan', '3D LiDAR Scanning'),
        ('troubleshooting', 'Troubleshooting'),
        ('panel_upgrade', 'Panel Upgrade'),
        ('wiring', 'New Wiring'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    project_size = SelectField('Project Size', choices=[
        ('', 'Select Project Size'),
        ('small', 'Small (Under $5K)'),
        ('medium', 'Medium ($5K - $20K)'),
        ('large', 'Large ($20K - $50K)'),
        ('enterprise', 'Enterprise ($50K+)')
    ], validators=[DataRequired()])
    location = StringField('Project Location', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Project Description', validators=[Length(max=1000)])
    files = MultipleFileField('Upload Images/Videos', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov', 'avi'], 'Images and videos only!')
    ])

class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    product_type = SelectField('Type', choices=[
        ('digital', 'Digital'),
        ('physical', 'Physical')
    ], validators=[DataRequired()])
    stripe_price_id = StringField('Stripe Price ID')
    image_url = StringField('Image URL')
    file_path = StringField('File Path (Digital Products)')
    is_active = BooleanField('Active')

class TrainingVideoForm(FlaskForm):
    title = StringField('Video Title', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Description')
    youtube_url = StringField('YouTube URL', validators=[DataRequired()])
    is_premium = BooleanField('Premium Content')
    stripe_price_id = StringField('Stripe Price ID (if premium)')

class ObjectDetectionForm(FlaskForm):
    image = FileField('Upload Image', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    comment = TextAreaField('Optional Comment', validators=[Length(max=500)], 
                           description='Add any details about what you see in the image')