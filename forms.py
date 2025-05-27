from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, FloatField, SelectField, 
    DateField, PasswordField, BooleanField, SubmitField,
    IntegerField, ValidationError
)
from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, NumberRange, 
    Optional, URL, Regexp
)
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=20, message='Username must be between 4 and 20 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Invalid email address')
    ])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class FreelancerProfileForm(FlaskForm):
    title = StringField('Professional Title', validators=[
        DataRequired(),
        Length(min=10, max=200, message='Title must be between 10 and 200 characters')
    ], render_kw={"placeholder": "e.g., Full Stack Web Developer, Data Scientist, Graphic Designer"})
    
    description = TextAreaField('Professional Summary', validators=[
        DataRequired(),
        Length(min=50, max=2000, message='Description must be between 50 and 2000 characters')
    ], render_kw={"placeholder": "Describe your skills, experience, and what makes you unique...", "rows": 6})
    
    skills = TextAreaField('Skills', validators=[
        DataRequired(),
        Length(min=10, max=1000, message='Skills must be between 10 and 1000 characters')
    ], render_kw={"placeholder": "Python, JavaScript, React, Node.js, Machine Learning, etc. (comma-separated)"})
    
    experience_level = SelectField('Experience Level', choices=[
        ('beginner', 'Beginner (0-2 years)'),
        ('intermediate', 'Intermediate (2-5 years)'),
        ('expert', 'Expert (5+ years)')
    ], validators=[DataRequired()])
    
    hourly_rate = FloatField('Hourly Rate (USD)', validators=[
        DataRequired(),
        NumberRange(min=5, max=500, message='Hourly rate must be between $5 and $500')
    ])
    
    location = StringField('Location', validators=[
        Optional(),
        Length(max=200, message='Location must be less than 200 characters')
    ], render_kw={"placeholder": "City, Country"})
    
    education = TextAreaField('Education', validators=[
        Optional(),
        Length(max=1000, message='Education must be less than 1000 characters')
    ], render_kw={"placeholder": "Your educational background..."})
    
    certifications = TextAreaField('Certifications', validators=[
        Optional(),
        Length(max=1000, message='Certifications must be less than 1000 characters')
    ], render_kw={"placeholder": "List your relevant certifications..."})
    
    portfolio_links = TextAreaField('Portfolio Links', validators=[
        Optional(),
        Length(max=1000, message='Portfolio links must be less than 1000 characters')
    ], render_kw={"placeholder": "GitHub, Behance, personal website, etc. (one per line)"})
    
    languages = StringField('Languages', validators=[
        Optional(),
        Length(max=500, message='Languages must be less than 500 characters')
    ], render_kw={"placeholder": "English (Native), Spanish (Fluent), etc."})
    
    availability = SelectField('Availability', choices=[
        ('full-time', 'Full-time (40+ hours/week)'),
        ('part-time', 'Part-time (20-40 hours/week)'),
        ('as-needed', 'As needed (< 20 hours/week)')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Create Freelancer Profile')

class ClientProfileForm(FlaskForm):
    company_name = StringField('Company/Organization Name', validators=[
        DataRequired(),
        Length(min=2, max=200, message='Company name must be between 2 and 200 characters')
    ])
    
    company_description = TextAreaField('Company Description', validators=[
        Optional(),
        Length(max=2000, message='Description must be less than 2000 characters')
    ], render_kw={"placeholder": "Brief description of your company or organization...", "rows": 4})
    
    industry = SelectField('Industry', choices=[
        ('', 'Select Industry'),
        ('technology', 'Technology'),
        ('healthcare', 'Healthcare'),
        ('finance', 'Finance'),
        ('education', 'Education'),
        ('retail', 'Retail'),
        ('manufacturing', 'Manufacturing'),
        ('consulting', 'Consulting'),
        ('marketing', 'Marketing & Advertising'),
        ('real-estate', 'Real Estate'),
        ('non-profit', 'Non-Profit'),
        ('startup', 'Startup'),
        ('other', 'Other')
    ], validators=[Optional()])
    
    location = StringField('Location', validators=[
        Optional(),
        Length(max=200, message='Location must be less than 200 characters')
    ], render_kw={"placeholder": "City, Country"})
    
    website = StringField('Website', validators=[
        Optional(),
        Length(max=200, message='Website must be less than 200 characters')
    ], render_kw={"placeholder": "https://yourcompany.com"})
    
    company_size = SelectField('Company Size', choices=[
        ('', 'Select Company Size'),
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('200+', '200+ employees')
    ], validators=[Optional()])
    
    phone = StringField('Phone Number', validators=[
        Optional(),
        Length(max=20, message='Phone number must be less than 20 characters')
    ], render_kw={"placeholder": "+1 (555) 123-4567"})
    
    submit = SubmitField('Create Client Profile')

class ProjectForm(FlaskForm):
    title = StringField('Project Title', validators=[
        DataRequired(),
        Length( min=1,max=200, message='Title must be between 10 and 200 characters')
    ], render_kw={"placeholder": "Clear, descriptive title for your project"})
    
    description = TextAreaField('Project Description', validators=[
        DataRequired(),
        Length(min=20, max=5000, message='Description must be between 50 and 5000 characters')
    ], render_kw={"placeholder": "Detailed description of your project requirements...", "rows": 8})
    
    budget = FloatField('Budget (USD)', validators=[
        DataRequired(),
        NumberRange(min=50, max=100000, message='Budget must be between $50 and $100,000')
    ])
    
    deadline = DateField('Deadline', validators=[Optional()], format='%Y-%m-%d')
    
    skills_required = TextAreaField('Skills Required', validators=[
        DataRequired(),
        Length(min=5, max=1000, message='Skills must be between 5 and 1000 characters')
    ], render_kw={"placeholder": "Python, JavaScript, React, Design, etc. (comma-separated)"})
    
    project_type = SelectField('Project Type', choices=[
        ('fixed', 'Fixed Price'),
        ('hourly', 'Hourly Rate')
    ], validators=[DataRequired()])
    
    submit = SubmitField('Post Project')

class MessageForm(FlaskForm):
    subject = StringField('Subject', validators=[
        DataRequired(),
        Length(min=5, max=200, message='Subject must be between 5 and 200 characters')
    ])
    
    content = TextAreaField('Message', validators=[
        DataRequired(),
        Length(min=10, max=5000, message='Message must be between 10 and 5000 characters')
    ], render_kw={"rows": 6})
    
    submit = SubmitField('Send Message')

class RatingForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        (5, '5 Stars - Excellent'),
        (4, '4 Stars - Very Good'),
        (3, '3 Stars - Good'),
        (2, '2 Stars - Fair'),
        (1, '1 Star - Poor')
    ], coerce=int, validators=[DataRequired()])
    
    review = TextAreaField('Review', validators=[
        Optional(),
        Length(max=2000, message='Review must be less than 2000 characters')
    ], render_kw={"placeholder": "Share your experience working with this freelancer...", "rows": 4})
    
    submit = SubmitField('Submit Rating')

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Invalid email address')
    ])
    submit = SubmitField('Request Password Reset')

class ResetPasswordRequestForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')

class SearchForm(FlaskForm):
    search = StringField('Search', validators=[Optional()])
    skill_filter = StringField('Skills', validators=[Optional()])
    location_filter = StringField('Location', validators=[Optional()])
    min_rate = FloatField('Min Rate', validators=[Optional(), NumberRange(min=0)])
    max_rate = FloatField('Max Rate', validators=[Optional(), NumberRange(min=0)])
    experience_filter = SelectField('Experience Level', choices=[
        ('', 'Any Level'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('expert', 'Expert')
    ], validators=[Optional()])
    submit = SubmitField('Search')

class ProjectSearchForm(FlaskForm):
    search = StringField('Search', validators=[Optional()])
    skill_filter = StringField('Skills', validators=[Optional()])
    budget_min = FloatField('Min Budget', validators=[Optional(), NumberRange(min=0)])
    budget_max = FloatField('Max Budget', validators=[Optional(), NumberRange(min=0)])
    project_type = SelectField('Project Type', choices=[
        ('', 'Any Type'),
        ('fixed', 'Fixed Price'),
        ('hourly', 'Hourly Rate')
    ], validators=[Optional()])
    submit = SubmitField('Search')