# app.py

import os
from datetime import datetime
from sqlalchemy import or_, and_, desc

from flask import (
    Flask, flash, redirect,
    url_for, render_template,
    request, session, jsonify
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, login_user,
    logout_user, login_required,
    current_user, UserMixin
)
from flask_mail import Mail, Message
from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from itsdangerous import (
    URLSafeTimedSerializer,
    SignatureExpired, BadSignature
)

# Your local modules
from models import (
    db, User, FreelancerProfile, ClientProfile, 
    Project, ProjectMessage, Rating, Message as PrivateMessage
)
from forms import (
    RegistrationForm,
    LoginForm,
    RequestResetForm,
    ResetPasswordRequestForm,
    FreelancerProfileForm,
    ClientProfileForm,
    ProjectForm,
    MessageForm,
    RatingForm
)

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:amal6230/.#@localhost/freelancehub1"
app.config["SECRET_KEY"] = '56ee6ec2d9da0a4ffdd6bcb90809def3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Email configuration (Gmail example)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = '0712ano@gmail.com'  
app.config['MAIL_PASSWORD'] = 'mwge wzac gead vpzz'     
app.config['MAIL_DEFAULT_SENDER'] = '0712ano@gmail.com'

# Initialize extensions
db.init_app(app)
mail = Mail(app)

# Initialize URLSafeTimedSerializer
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# User loader callback for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper function to send reset email
def send_reset_email(user):
    """Send password reset email to user"""
    token = user.generate_reset_token(serializer)
    reset_url = url_for('reset_password', token=token, _external=True)
    
    msg = Message(
        'Password Reset Request',
        recipients=[user.email]
    )
    
    msg.body = f'''To reset your password, visit the following link:
{reset_url}

If you did not make this request, simply ignore this email and no changes will be made.

This link will expire in 1 hour.
'''
    
    msg.html = f'''
    <h2>Password Reset Request</h2>
    <p>To reset your password, click the following link:</p>
    <p><a href="{reset_url}">Reset Password</a></p>
    <p>If you did not make this request, simply ignore this email and no changes will be made.</p>
    <p><strong>This link will expire in 1 hour.</strong></p>
    '''
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_message_notification(recipient_email, sender_name, message_content):
    """Send email notification for new messages"""
    msg = Message(
        f'New Message from {sender_name} - FreelanceHub',
        recipients=[recipient_email]
    )
    
    msg.body = f'''You have received a new message from {sender_name} on FreelanceHub.

Message: {message_content[:100]}{'...' if len(message_content) > 100 else ''}

Login to FreelanceHub to view the full message and reply.
'''
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send message notification: {e}")
        return False

# API Routes
@app.route('/api/unread_messages')
@login_required
def api_unread_messages():
    """API endpoint to get unread message count"""
    count = PrivateMessage.query.filter_by(receiver_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered. Please use a different email.', 'danger')
            return render_template("register.html", form=form)
        
        existing_username = User.query.filter_by(username=form.username.data).first()
        if existing_username:
            flash('Username already taken. Please choose a different username.', 'danger')
            return render_template("register.html", form=form)
        
        try:
            new_user = User(
                username=form.username.data,
                email=form.email.data
            )
            # This invokes the password.setter above
            new_user.password = form.password.data

            # Save to the database
            db.session.add(new_user)
            db.session.commit()

            # Log in the user and generate session flag for role selection popup
            login_user(new_user)
            session['show_role_popup'] = True
            flash(f'Account created for {form.username.data}! Please select your role.', 'success')
            return redirect(url_for('select_role'))  # Direct to role selection
        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {e}")
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template("register.html", form=form)
    
    return render_template("register.html", form=form)

@app.route("/select_role")
@login_required
def select_role():
    """Show role selection page after registration"""
    return render_template("select_role.html")

@app.route("/register_freelancer", methods=['GET', 'POST'])
@login_required
def register_freelancer():
    form = FreelancerProfileForm()
    if form.validate_on_submit():
        try:
            # Update user role
            current_user.user_type = 'freelancer'
            
            # Create freelancer profile
            freelancer_profile = FreelancerProfile(
                user_id=current_user.id,
                title=form.title.data,
                description=form.description.data,
                skills=form.skills.data,
                experience_level=form.experience_level.data,
                hourly_rate=form.hourly_rate.data,
                location=form.location.data,
                education=form.education.data,
                certifications=form.certifications.data,
                portfolio_links=form.portfolio_links.data,
                languages=form.languages.data,
                availability=form.availability.data
            )
            
            db.session.add(freelancer_profile)
            db.session.commit()
            
            # Clear role selection session flag
            session.pop('show_role_popup', None)
            
            flash('Freelancer profile created successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            print(f"Freelancer profile creation error: {e}")
            flash('An error occurred while creating your profile. Please try again.', 'danger')
    
    return render_template("freelancer_form.html", form=form)

@app.route("/register_client", methods=['GET', 'POST'])
@login_required
def register_client():
    form = ClientProfileForm()
    if form.validate_on_submit():
        try:
            # Check if client profile already exists
            existing_profile = ClientProfile.query.filter_by(user_id=current_user.id).first()
            if existing_profile:
                flash('Client profile already exists for this user.', 'warning')
                return redirect(url_for('dashboard'))
            
            # Update user role first
            current_user.user_type = 'client'
            
            # Create client profile with proper validation
            client_profile = ClientProfile(
                user_id=current_user.id,
                company_name=form.company_name.data.strip(),
                company_description=form.company_description.data.strip() if form.company_description.data else None,
                industry=form.industry.data.strip() if form.industry.data else None,
                location=form.location.data.strip() if form.location.data else None,
                website=form.website.data.strip() if form.website.data else None,
                company_size=form.company_size.data if form.company_size.data else None,
                phone=form.phone.data.strip() if form.phone.data else None
            )
            
            # Add both user and profile to session
            db.session.add(client_profile)
            db.session.commit()
            
            # Clear role selection session flag
            session.pop('show_role_popup', None)
            
            flash('Client profile created successfully!', 'success')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Client profile creation error: {str(e)}")
            print(f"Form data: {form.data}")
            print(f"Form errors: {form.errors}")
            flash(f'An error occurred while creating your profile: {str(e)}', 'danger')
    else:
        if request.method == 'POST':
            print(f"Form validation failed: {form.errors}")
            flash('Please check the form for errors and try again.', 'danger')
    
    return render_template("client_form.html", form=form)

@app.route("/login", methods=['GET','POST'])
def login():
    form = LoginForm()
    
    if request.method == 'POST':
        print(f"POST request received")
        print(f"Form data: {dict(request.form)}")
        print(f"Form errors before validation: {form.errors}")
        
    if form.validate_on_submit():
        print(f"Form validated successfully")
        print(f"Email: {form.email.data}")
        
        # Find user by email
        user = User.query.filter_by(email=form.email.data).first()
        print(f"User found: {user}")
        
        # Check if user exists and password is correct
        if user and user.check_password(form.password.data):
            print("Password check passed")
            login_user(user, remember=form.remember.data)
            print(f"User logged in: {current_user.is_authenticated}")
            flash(f'Login successful! Welcome back, {user.username}!', 'success')
            
            # Redirect based on user type
            if user.user_type:
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('select_role'))
        else:
            print("Password check failed or user not found")
            flash('Invalid email or password. Please try again.', 'danger')
    else:
        if request.method == 'POST':
            print(f"Form validation failed: {form.errors}")
    
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route("/dashboard")
@login_required
def dashboard():
    """Main dashboard for both freelancers and clients"""
    if current_user.user_type == 'freelancer':
        # Get freelancer's profile and recent messages
        freelancer_profile = FreelancerProfile.query.filter_by(user_id=current_user.id).first()
        recent_messages = PrivateMessage.query.filter_by(receiver_id=current_user.id).order_by(desc(PrivateMessage.created_at)).limit(5).all()
        ratings = Rating.query.filter_by(freelancer_id=current_user.id).all()
        avg_rating = sum([r.rating for r in ratings]) / len(ratings) if ratings else 0
        
        # Get all freelancers for the feed (excluding current user)
        all_freelancers = FreelancerProfile.query.join(User).filter(User.id != current_user.id).all()
        
        return render_template("freelancer_dashboard.html", 
                             profile=freelancer_profile,
                             recent_messages=recent_messages,
                             ratings=ratings,
                             avg_rating=round(avg_rating, 1),
                             all_freelancers=all_freelancers)
    
    elif current_user.user_type == 'client':
        # Get client's profile, projects, and messages
        client_profile = ClientProfile.query.filter_by(user_id=current_user.id).first()
        projects = Project.query.filter_by(client_id=current_user.id).order_by(desc(Project.created_at)).all()
        recent_messages = PrivateMessage.query.filter_by(receiver_id=current_user.id).order_by(desc(PrivateMessage.created_at)).limit(5).all()
        
        # Get all freelancers for the feed with ratings
        freelancers_query = FreelancerProfile.query.join(User).all()
        
        # Calculate ratings for each freelancer
        freelancer_data = []
        for freelancer in freelancers_query:
            ratings = Rating.query.filter_by(freelancer_id=freelancer.user_id).all()
            avg_rating = sum([r.rating for r in ratings]) / len(ratings) if ratings else 0
            freelancer_data.append({
                'profile': freelancer,
                'avg_rating': round(avg_rating, 1),
                'total_ratings': len(ratings)
            })
        
        # Sort by average rating (highest first)
        freelancer_data.sort(key=lambda x: x['avg_rating'], reverse=True)
        
        return render_template("client_dashboard.html",
                             profile=client_profile,
                             projects=projects,
                             recent_messages=recent_messages,
                             freelancers=freelancer_data)
    else:
        return redirect(url_for('select_role'))

@app.route("/browse_freelancers")
@login_required
def browse_freelancers():
    """Browse all freelancers with filtering and search"""
    search = request.args.get('search', '')
    skill_filter = request.args.get('skill', '')
    experience_filter = request.args.get('experience', '')
    
    query = FreelancerProfile.query.join(User)
    
    if search:
        query = query.filter(or_(
            FreelancerProfile.title.contains(search),
            FreelancerProfile.skills.contains(search),
            FreelancerProfile.description.contains(search)
        ))
    
    if skill_filter:
        query = query.filter(FreelancerProfile.skills.contains(skill_filter))
    
    if experience_filter:
        query = query.filter(FreelancerProfile.experience_level == experience_filter)
    
    # Order by average rating
    freelancers = query.all()
    
    # Calculate average ratings for sorting
    freelancer_data = []
    for freelancer in freelancers:
        ratings = Rating.query.filter_by(freelancer_id=freelancer.user_id).all()
        avg_rating = sum([r.rating for r in ratings]) / len(ratings) if ratings else 0
        freelancer_data.append({
            'profile': freelancer,
            'avg_rating': avg_rating,
            'total_ratings': len(ratings)
        })
    
    # Sort by average rating (highest first)
    freelancer_data.sort(key=lambda x: x['avg_rating'], reverse=True)
    
    return render_template("browse_freelancers.html", 
                         freelancers=freelancer_data,
                         search=search,
                         skill_filter=skill_filter,
                         experience_filter=experience_filter)

@app.route("/browse_projects")
@login_required
def browse_projects():
    """Browse all open projects with filtering and search"""
    search = request.args.get('search', '')
    skill_filter = request.args.get('skill', '')
    budget_min = request.args.get('budget_min', type=float)
    budget_max = request.args.get('budget_max', type=float)
    project_type = request.args.get('project_type', '')
    
    query = Project.query.filter_by(status='open').join(User, Project.client_id == User.id)
    
    if search:
        query = query.filter(or_(
            Project.title.contains(search),
            Project.description.contains(search),
            Project.skills_required.contains(search)
        ))
    
    if skill_filter:
        query = query.filter(Project.skills_required.contains(skill_filter))
    
    if budget_min:
        query = query.filter(Project.budget >= budget_min)
    
    if budget_max:
        query = query.filter(Project.budget <= budget_max)
    
    if project_type:
        query = query.filter(Project.project_type == project_type)
    
    projects = query.order_by(desc(Project.created_at)).all()
    
    return render_template("browse_projects.html", 
                         projects=projects,
                         search=search,
                         skill_filter=skill_filter,
                         budget_min=budget_min,
                         budget_max=budget_max,
                         project_type=project_type)

@app.route("/freelancer_profile/<int:user_id>")
@login_required
def freelancer_profile(user_id):
    """View detailed freelancer profile"""
    user = User.query.get_or_404(user_id)
    if user.user_type != 'freelancer':
        flash('User is not a freelancer.', 'danger')
        return redirect(url_for('browse_freelancers'))
    
    freelancer_profile = FreelancerProfile.query.filter_by(user_id=user_id).first_or_404()
    ratings = Rating.query.filter_by(freelancer_id=user_id).order_by(desc(Rating.created_at)).all()
    avg_rating = sum([r.rating for r in ratings]) / len(ratings) if ratings else 0
    
    return render_template("freelancer_profile.html",
                         user=user,
                         profile=freelancer_profile,
                         ratings=ratings,
                         avg_rating=round(avg_rating, 1),
                         total_ratings=len(ratings))

@app.route("/client_profile/<int:user_id>")
@login_required
def client_profile(user_id):
    """View detailed client profile"""
    user = User.query.get_or_404(user_id)
    if user.user_type != 'client':
        flash('User is not a client.', 'danger')
        return redirect(url_for('dashboard'))
    
    client_profile = ClientProfile.query.filter_by(user_id=user_id).first_or_404()
    projects = Project.query.filter_by(client_id=user_id).filter_by(status='open').order_by(desc(Project.created_at)).all()
    
    return render_template("client_profile.html",
                         user=user,
                         profile=client_profile,
                         projects=projects)

@app.route("/post_project", methods=['GET', 'POST'])
@login_required
def post_project():
    """Post a new project (clients only)"""
    if current_user.user_type != 'client':
        flash('Only clients can post projects.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = ProjectForm()
    if form.validate_on_submit():
        try:
            project = Project(
                title=form.title.data,
                description=form.description.data,
                budget=form.budget.data,
                deadline=form.deadline.data,
                skills_required=form.skills_required.data,
                project_type=form.project_type.data,
                client_id=current_user.id
            )
            
            db.session.add(project)
            db.session.commit()
            
            flash('Project posted successfully!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            print(f"Project posting error: {e}")
            flash('An error occurred while posting the project.', 'danger')
    
    return render_template("post_project.html", form=form)

@app.route("/edit_project/<int:project_id>", methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    """Edit an existing project"""
    project = Project.query.get_or_404(project_id)
    
    # Check if current user is the owner of the project
    if project.client_id != current_user.id:
        flash('You are not authorized to edit this project.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = ProjectForm(obj=project)
    if form.validate_on_submit():
        try:
            form.populate_obj(project)
            db.session.commit()
            flash('Project updated successfully!', 'success')
            return redirect(url_for('project_detail', project_id=project.id))
        except Exception as e:
            db.session.rollback()
            print(f"Project update error: {e}")
            flash('An error occurred while updating the project.', 'danger')
    
    return render_template("post_project.html", form=form, project=project)

@app.route("/project_detail/<int:project_id>")
@login_required
def project_detail(project_id):
    """View detailed project information"""
    project = Project.query.get_or_404(project_id)
    client = User.query.get(project.client_id)
    client_profile = ClientProfile.query.filter_by(user_id=project.client_id).first()
    
    return render_template("project_detail.html", 
                         project=project, 
                         client=client,
                         client_profile=client_profile)

@app.route("/messages")
@login_required
def messages():
    """View all messages"""
    received_messages = PrivateMessage.query.filter_by(receiver_id=current_user.id).order_by(desc(PrivateMessage.created_at)).all()
    sent_messages = PrivateMessage.query.filter_by(sender_id=current_user.id).order_by(desc(PrivateMessage.created_at)).all()
    
    return render_template("messages.html", 
                         received_messages=received_messages,
                         sent_messages=sent_messages)

@app.route("/view_message/<int:message_id>")
@login_required
def view_message(message_id):
    """View a specific message and mark as read"""
    message = PrivateMessage.query.get_or_404(message_id)
    
    # Check if user is sender or receiver
    if message.sender_id != current_user.id and message.receiver_id != current_user.id:
        flash('You are not authorized to view this message.', 'danger')
        return redirect(url_for('messages'))
    
    # Mark as read if user is the receiver
    if message.receiver_id == current_user.id and not message.is_read:
        message.is_read = True
        db.session.commit()
    
    return render_template("view_message.html", message=message)

@app.route("/send_message/<int:receiver_id>", methods=['GET', 'POST'])
@login_required
def send_message(receiver_id):
    """Send a private message"""
    receiver = User.query.get_or_404(receiver_id)
    form = MessageForm()
    
    if form.validate_on_submit():
        try:
            message = PrivateMessage(
                sender_id=current_user.id,
                receiver_id=receiver_id,
                subject=form.subject.data,
                content=form.content.data
            )
            
            db.session.add(message)
            db.session.commit()
            
            # Send email notification
            send_message_notification(receiver.email, current_user.username, form.content.data)
            
            flash('Message sent successfully!', 'success')
            return redirect(url_for('messages'))
        except Exception as e:
            db.session.rollback()
            print(f"Message sending error: {e}")
            flash('An error occurred while sending the message.', 'danger')
    
    return render_template("send_message.html", form=form, receiver=receiver)

@app.route("/rate_freelancer/<int:freelancer_id>", methods=['GET', 'POST'])
@login_required
def rate_freelancer(freelancer_id):
    """Rate a freelancer (clients only)"""
    if current_user.user_type != 'client':
        flash('Only clients can rate freelancers.', 'danger')
        return redirect(url_for('dashboard'))
    
    freelancer = User.query.get_or_404(freelancer_id)
    if freelancer.user_type != 'freelancer':
        flash('User is not a freelancer.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Check if client has already rated this freelancer
    existing_rating = Rating.query.filter_by(client_id=current_user.id, freelancer_id=freelancer_id).first()
    
    form = RatingForm()
    if form.validate_on_submit():
        try:
            if existing_rating:
                # Update existing rating
                existing_rating.rating = form.rating.data
                existing_rating.review = form.review.data
            else:
                # Create new rating
                rating = Rating(
                    client_id=current_user.id,
                    freelancer_id=freelancer_id,
                    rating=form.rating.data,
                    review=form.review.data
                )
                db.session.add(rating)
            
            db.session.commit()
            flash('Rating submitted successfully!', 'success')
            return redirect(url_for('freelancer_profile', user_id=freelancer_id))
        except Exception as e:
            db.session.rollback()
            print(f"Rating submission error: {e}")
            flash('An error occurred while submitting the rating.', 'danger')
    
    if existing_rating:
        form.rating.data = existing_rating.rating
        form.review.data = existing_rating.review
    
    return render_template("rate_freelancer.html", form=form, freelancer=freelancer)

# Password Reset Routes
@app.route("/reset_password_request", methods=['GET', 'POST'])
def reset_password_request():
    """Handle forgot password requests"""
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user:
            if send_reset_email(user):
                flash('A password reset link has been sent to your email address.', 'info')
            else:
                flash('Failed to send reset email. Please try again later.', 'danger')
        else:
            # Don't reveal if email exists or not for security
            flash('If an account with that email exists, a reset link will be sent.', 'info')
        
        return redirect(url_for('login'))
    
    return render_template("reset_password_request.html", title="Reset Password", form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token"""
    user = User.verify_reset_token(token, serializer)
    
    if not user:
        flash('Invalid or expired reset link', 'warning')
        return redirect(url_for('reset_password_request'))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        # Update password
        user.set_password(form.password.data)
        db.session.commit()
        
        flash('Your password has been reset successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', title='Reset Password', form=form)

# Update error handlers in app.py
@app.errorhandler(404)
def page_not_found(e):
    try:
        return render_template("404.html"), 404
    except:
        return "Page not found", 404

@app.errorhandler(500)
def internal_error(e):
    try:
        return render_template("500.html"), 500
    except:
        return "Internal server error", 500

# Add this route if you need notifications
@app.route('/notifications/unread-count')
@login_required
def unread_notifications():
    return jsonify(count=0)  # Temporary implementation

# Create database tables
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")

if __name__ == "__main__":
    app.run(debug=True)