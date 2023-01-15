from flask import Blueprint, render_template, redirect, url_for, request, flash, Markup
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .models import user
import shutil

import os

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        rem = request.form.get('checkbox')
        
        if username == '':
            flash("Please enter your username", 'warning')
        elif password == '':
            flash("Please enter your password", 'warning')
        else:
            User = user.query.filter_by(username=username).first()
            if User:
                if password == User.password:
                    flash("Logged in!", category='success')
                    login_user(User, remember = (True if rem == "True" else False) )
                    return redirect(url_for('views.home'))
                else:
                    flash("Invalid Password", 'danger')
            else:
                flash(Markup('You haven\'t registered yet. <a href="/signup" class="alert-link">Sign Up</a> instead'), category='warning')

    return render_template("login.html", user = current_user)

@auth.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        eml = request.form.get("email")
        usr = request.form.get("username")
        pass1 = request.form.get("password-2")
        pass2 = request.form.get("password-2")
    
        email_already_exist = user.query.filter_by(email=eml).first()
        user_already_exist = user.query.filter_by(username=usr).first()

        import re
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        def isValid(email):
            if re.fullmatch(regex, email):
                return ("Valid email")
            else:
                return ("Invalid email")
        if isValid(eml) == "Invalid email":
            flash('Invalid email address', category='danger')
        elif email_already_exist:
            flash(Markup('Email already in use. <a href="/login" class="alert-link">Login</a> instead.'), category='warning')
        elif user_already_exist:
            flash('Username already exist. Choose a different username.', category='danger')
        elif pass1 != pass2:
            flash('Passwords do not match. Re enter the password correctly.', category='danger')
        elif len(usr) <= 3:
            flash('Username must be longer than 3 characters.', category='danger')
        elif len(pass1) < 8:
            flash('Password must be atleast 8 characters long.', category='danger')
        else:
            new_user = user(email=eml, username=usr, password=pass1)
            path = os.path.join(os.getcwd(),'website/static/post_pic', usr)
            if os.path.exists(path):
                shutil.rmtree(path, ignore_errors=False, onerror=None)
            os.mkdir(path)
            path = os.path.join(os.getcwd(),'website/static/profile_pic')
            for filename in os.listdir(path):
                if filename != 'spt.jpg':
                    os.remove(os.path.join(path,filename))
            db.session.add(new_user)
            db.session.commit()
            flash('User Created. Login to Proceed', 'success')
            return redirect(url_for("auth.login"))

    return render_template("signup.html", user = current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("views.home"))