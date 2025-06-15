"""
Forms for worker dispatch system
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from wtforms import StringField, TextAreaField, SelectField, PasswordField, HiddenField
from wtforms.validators import DataRequired, Email, Length, Optional


class WorkerLoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class ServiceCallForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired(), Length(max=200)])
    customer_name = StringField('Customer Name', validators=[DataRequired(), Length(max=100)])
    location = StringField('Location/Address', validators=[DataRequired(), Length(max=300)])
    description = TextAreaField('Job Description', validators=[DataRequired(), Length(max=1000)])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'), 
        ('high', 'High'),
        ('urgent', 'Urgent')
    ], default='medium', validators=[DataRequired()])
    assigned_to = SelectField('Assign to Worker', validators=[DataRequired()])
    attachments = MultipleFileField('Attach Files', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx'], 'Images and documents only!')
    ])


class JobStatusUpdateForm(FlaskForm):
    call_id = HiddenField('Call ID', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('cancelled', 'Cancelled')
    ], validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])


class FileUploadForm(FlaskForm):
    call_id = HiddenField('Call ID', validators=[DataRequired()])
    files = MultipleFileField('Upload Files', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx', 'mp4', 'mov'], 
                   'Images, documents, and videos only!')
    ])
    note = TextAreaField('Note', validators=[Optional(), Length(max=300)])