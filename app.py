from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError  
from flask import Flask, flash, redirect, url_for
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, ValidationError, Length
from forms import RegistrationForm, LoginForm

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:amal6230/.#@localhost/freelancehub"
app.config["SECRET_KEY"] = '56ee6ec2d9da0a4ffdd6bcb90809def3'
# db = SQLAlchemy(app)

# class User(db.Model, UserMixin):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(20), nullable=False, unique=True)
#     password = db.Column(db.String(80), nullable=False)


class Registerform(FlaskForm):
    username = StringField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Username"},
    )
    password = PasswordField(
        validators=[InputRequired(), Length(min=4, max=20)],
        render_kw={"placeholder": "Password"},
    )
    submit = SubmitField("Register")


@app.route("/")
def index():
    return "it's begin"
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
        # new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        # db.session.add(new_user)  # ✅ Add user to database session
        # db.session.commit()  # ✅ Commit changes

        flash(f'Account created for { form.username.data }!', 'success')
        return redirect(url_for('home'))
    return render_template("register.html", form=form)

@app.route("/login", methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash(f'Login Successful for { form.username.data }!', 'success')
        return redirect(url_for('home'))
    return render_template("login.html", form=form)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def page_not_found1(e):
    return render_template("500.html"), 404

if __name__ == "__main__":
    app.run(debug=True)
