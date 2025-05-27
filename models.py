# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(20),  nullable=False, unique=True)
    email         = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type     = db.Column(db.String(20), nullable=True)  # 'freelancer' or 'client'
    created_at    = db.Column(db.DateTime,    nullable=False, default=datetime.utcnow)
    is_active     = db.Column(db.Boolean, default=True)

    # Relationships - Fixed to avoid ambiguity
    freelancer_profile = db.relationship('FreelancerProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    client_profile = db.relationship('ClientProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    
    # Message relationships with explicit foreign keys
    sent_messages = db.relationship(
        'Message', 
        foreign_keys='Message.sender_id', 
        backref='sender', 
        cascade='all, delete-orphan'
    )
    received_messages = db.relationship(
        'Message', 
        foreign_keys='Message.receiver_id', 
        backref='receiver', 
        cascade='all, delete-orphan'
    )
    
    # Project relationships with explicit foreign keys
    client_projects = db.relationship(
        'Project', 
        foreign_keys='Project.client_id',
        backref='client',
        cascade='all, delete-orphan',
        lazy=True
    )
    
    freelancer_projects = db.relationship(
        'Project', 
        foreign_keys='Project.freelancer_id',
        backref='freelancer',
        lazy=True
    )
    
    # Rating relationships with explicit foreign keys
    given_ratings = db.relationship(
        'Rating', 
        foreign_keys='Rating.client_id', 
        backref='rating_client', 
        cascade='all, delete-orphan'
    )
    received_ratings = db.relationship(
        'Rating', 
        foreign_keys='Rating.freelancer_id', 
        backref='rating_freelancer', 
        cascade='all, delete-orphan'
    )
    
    # Project message relationship
    project_messages_sent = db.relationship(
        'ProjectMessage',
        foreign_keys='ProjectMessage.sender_id',
        backref='message_sender',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<User {self.username}>'

    # Store hashed password, never the plain text
    @property
    def password(self):
        raise AttributeError('Password is write-only')

    @password.setter
    def password(self, plaintext):
        self.password_hash = generate_password_hash(plaintext)

    def check_password(self, plaintext):
        return check_password_hash(self.password_hash, plaintext)
    
    def set_password(self, password):
        """Set new password (used for password reset)"""
        self.password_hash = generate_password_hash(password)
    
    def generate_reset_token(self, serializer):
        """Generate a password reset token"""
        return serializer.dumps(self.email, salt='password-reset-salt')
    
    @staticmethod
    def verify_reset_token(token, serializer, expiration=3600):
        """Verify password reset token (expires in 1 hour by default)"""
        try:
            email = serializer.loads(
                token, 
                salt='password-reset-salt', 
                max_age=expiration
            )
            return User.query.filter_by(email=email).first()
        except (SignatureExpired, BadSignature):
            return None

class FreelancerProfile(db.Model):
    __tablename__ = 'freelancer_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    title = db.Column(db.String(200), nullable=False)  # Professional title
    description = db.Column(db.Text, nullable=False)  # Detailed description
    skills = db.Column(db.Text, nullable=False)  # Comma-separated skills
    experience_level = db.Column(db.String(50), nullable=False)  # Beginner, Intermediate, Expert
    hourly_rate = db.Column(db.Float, nullable=True)
    location = db.Column(db.String(100), nullable=True)
    education = db.Column(db.Text, nullable=True)
    certifications = db.Column(db.Text, nullable=True)
    portfolio_links = db.Column(db.Text, nullable=True)  # Comma-separated URLs
    languages = db.Column(db.Text, nullable=True)  # Comma-separated languages
    availability = db.Column(db.String(50), nullable=True)  # Full-time, Part-time, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_skills_list(self):
        """Return skills as a list"""
        return [skill.strip() for skill in self.skills.split(',') if skill.strip()]
    
    def get_portfolio_links_list(self):
        """Return portfolio links as a list"""
        if not self.portfolio_links:
            return []
        return [link.strip() for link in self.portfolio_links.split(',') if link.strip()]
    
    def get_languages_list(self):
        """Return languages as a list"""
        if not self.languages:
            return []
        return [lang.strip() for lang in self.languages.split(',') if lang.strip()]

class ClientProfile(db.Model):
    __tablename__ = 'client_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    company_name = db.Column(db.String(200), nullable=False)
    company_description = db.Column(db.Text, nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    company_size = db.Column(db.String(50), nullable=True)  # 1-10, 11-50, 51-200, etc.
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    budget = db.Column(db.Float, nullable=True)
    deadline = db.Column(db.Date, nullable=True)
    skills_required = db.Column(db.Text, nullable=False)  # Comma-separated skills
    project_type = db.Column(db.String(50), nullable=False)  # Fixed Price, Hourly
    status = db.Column(db.String(20), default='open')  # open, in_progress, completed, cancelled
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    freelancer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('ProjectMessage', backref='project', cascade='all, delete-orphan')
    
    def get_skills_required_list(self):
        """Return required skills as a list"""
        return [skill.strip() for skill in self.skills_required.split(',') if skill.strip()]

class ProjectMessage(db.Model):
    __tablename__ = 'project_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Rating(db.Model):
    __tablename__ = 'ratings'
    
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    freelancer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    review = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint to prevent multiple ratings from same client to same freelancer
    __table_args__ = (db.UniqueConstraint('client_id', 'freelancer_id', name='unique_client_freelancer_rating'),)
