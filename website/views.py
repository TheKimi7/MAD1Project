from flask import Blueprint, render_template, redirect, url_for, request, flash, Markup
import flask_login
from .models import post, user
from . import db
from .imageupload import ImageUpload, PostUpload
import os

views = Blueprint("views", __name__)

@views.route("/")
@views.route("/home")
@flask_login.login_required
def home():
    feed = flask_login.current_user.followed_post()
    return render_template("home.html", user = flask_login.current_user, posts=feed)

@views.route("/search", methods=['GET','POST'])
@flask_login.login_required
def search():
    uqr = user.query
    if request.method =='POST':
        user_searched = request.form.get('search')
        resulter = uqr.filter(user.username.like('%' + user_searched + '%'))
        results = resulter.order_by(user.username).all()
        if user_searched != '':
            if len(results) != 0:
                flash('End of Search Results', 'warning')
                return render_template("search.html", user = flask_login.current_user, results=results)
            else:
                flash('No user found', 'warning')
    return render_template("search.html", user = flask_login.current_user)



@views.route("/newpost", methods=['GET', 'POST'])
@flask_login.login_required
def newpost():
    postf = PostUpload()
    if request.method == 'POST':
        title = request.form.get("title")
        caption = request.form.get("caption")
        if title == '':
            flash('Title needed', 'danger')
        elif caption == '':
            flash('Caption needed', 'danger')
        
        if postf.picture.data:
            pfpath = os.path.join(os.getcwd(),'website/static/post_pic', flask_login.current_user.username, postf.picture.data.filename)
            postf.picture.data.save(pfpath)
            image = url_for('static', filename='post_pic/'+str(flask_login.current_user.username) +'/'+ str(postf.picture.data.filename))
            content = post(title=title, caption=caption, image=image, author_user = flask_login.current_user.id)
            db.session.add(content)
            db.session.commit()
            flash('Post Created', 'success')
            return redirect(url_for("views.home"))
            
        else:
            print(postf.picture.data)
            flash('Image needed', 'danger')
    return render_template("newpost.html", user=flask_login.current_user, form = PostUpload())

@views.route("/deletepost/<id>", methods=['GET', 'POST'])
@flask_login.login_required
def deletepost(id):
    Post = post.query.filter_by(id=id).first()
    if not Post:
        flash("Post already deleted", 'danger')
    elif flask_login.current_user.id != Post.author_user:
        flash("You are not authorised to delete this post", 'danger')
    else:
        os.remove("website"+str(Post.image))
        db.session.delete(Post)
        db.session.commit()
        flash("Post deleted successfully.", 'success')
    
    return redirect(url_for("views.home"))

@views.route("/editpost/<id>", methods=['GET', 'POST'])
@flask_login.login_required
def editpost(id):
    Post = post.query.filter_by(id=id).first()
    if Post.author_user != flask_login.current_user.id:
        flash("You are not authorized to edit the post", 'danger')
    elif not Post:
        flash("Post not found", 'danger')
    else:
        if request.method == 'POST':
            title = request.form.get("title")
            caption = request.form.get("caption")
            if Post.title != title or Post.caption != caption:
                Post.title = title
                Post.caption = caption
                db.session.commit()
                flash("Post edited successfully.", 'success')   
        else:
            return render_template('editpost.html', post=Post, user=flask_login.current_user)
    return redirect(url_for('views.home'))

@views.route("/user/<username>")
@flask_login.login_required
def profile(username):
    User = user.query.filter_by(username=username).first()
    if not User:
        flash("Profile does not exist.", 'error')
        return redirect(url_for("views.home"))

    posts = User.posts
    profile_pic = url_for('static', filename='profile_pic/' + flask_login.current_user.profile_pic)
    return render_template("profile.html", User=User, user=flask_login.current_user, posts=posts, username=username, lezn=len(posts), profile_pic=profile_pic)

@views.route("/edituser/<id>", methods=['GET', 'POST'])
@flask_login.login_required
def edituser(id):
    imgf = ImageUpload()
    User = user.query.filter_by(id=id).first()
    if not User:
        flash("Profile does not exist.", 'error')
        return redirect(url_for("views.home"))
    elif  User.id != flask_login.current_user.id:
        flash("You are not authorized to access this page", 'danger')
    else:
        if request.method == 'POST':
            eml = request.form.get("email")
            usr = request.form.get("username")
            pass1 = request.form.get("password-2")
            pass2 = request.form.get("password-2")

            if imgf.picture.data:
                fname, fext = os.path.splitext(imgf.picture.data.filename)
                pfpath = os.path.join(os.getcwd(),'website/static/profile_pic', (usr+fext))
                imgf.picture.data.save(pfpath)
                User.profile_pic = url_for('static', filename='profile_pic/' +(usr+fext))

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
            elif (email_already_exist is not None) & (email_already_exist != User):
                flash(Markup('Email already in use.'), category='warning')
            elif (user_already_exist is not None) & (user_already_exist != User):
                flash('Username already exist. Choose a different username.', category='danger')
            elif pass1 != pass2:
                flash('Passwords do not match. Re enter the password correctly.', category='danger')
            elif len(usr) <= 3:
                flash('Username must be longer than 3 characters.', category='danger')
            elif len(pass1) < 8:
                flash('Password must be atleast 8 characters long.', category='danger')
            else:
                User.email = eml
                User.username = usr
                User.password = pass1

                db.session.commit()
                flash('User Updated', 'success')
                return redirect(url_for("views.profile", username=User.username))
        else:
            return render_template('edituser.html', User=User, user=flask_login.current_user, form = ImageUpload())
    return redirect(url_for('views.home'))

@views.route("/deleteuser/<id>", methods=['GET', 'POST'])
@flask_login.login_required
def deleteuser(id):
    User = user.query.filter_by(id=id).first()
    if not User:
        flash("Post already deleted", 'danger')
    elif flask_login.current_user.id != User.id:
        flash("You are not authorised to delete this post", 'danger')
    else:
        Posts = post.query.filter_by(author_user=id).all()
        for Post in Posts:
            os.remove(Post.image)
            db.session.delete(Post)
        os.rmdir(os.path.join(os.getcwd(),'website/static/post_pic', flask_login.current_user.username ))
        if User.profile_pic != 'spt.jpg':
            if os.path.exists("website"+str(User.profile_pic)):
                os.remove("website"+str(User.profile_pic))
        db.session.delete(User)
        db.session.commit()
        flash("User deleted successfully.", 'success')
        return redirect(url_for('views.home'))

@views.route('/follow/<username>')
@flask_login.login_required
def follow(username):
    if request.method =='GET':
        User = user.query.filter_by(username=username).first()
        if User is None:
            flash('User not found.', 'warning')
            return redirect(url_for('views.home'))
        flask_login.current_user.follow(User)
        db.session.commit()
        flash('You are following '+username)
        return redirect(url_for('views.profile', username=username))
    else:
        return redirect(url_for('views.home'))

@views.route('/unfollow/<username>')
@flask_login.login_required
def unfollow(username):
    if request.method =='GET':
        User = user.query.filter_by(username=username).first()
        if User is None:
            flash('User not found.', 'warning')
            return redirect(url_for('views.home'))
        flask_login.current_user.unfollow(User)
        db.session.commit()
        flash('You unfollowed '+username)
        return redirect(url_for('views.profile', username=username))
    else:
        return redirect(url_for('views.home'))