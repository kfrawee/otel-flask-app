import os
import secrets
from datetime import datetime
from functools import lru_cache

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from PIL import Image

from flaskblog import app, bcrypt, db
from flaskblog.forms import (LoginForm, PostForm, RegistrationForm,
                             UpdateAccountForm)
from flaskblog.models import Post, User

# temp database
posts = [
    {
        "author": {
            "image_file": "default.jpg",
            "username": "user1"},
        "title": "Blog Post 1",
        "content": "First post content",
        "date_posted": datetime.utcnow(),
        "id": 1,
    },
    {
        "author": {
            "image_file": "default.jpg",
            "username": "user1"},
        "title": "Blog Post 2",
        "content": "Second post content",
        "date_posted": datetime.utcnow(),
        "id": 2,
    },
    {
        "author": {
            "image_file": "default.jpg",
            "username": "user2"},
        "title": "Blog Post 3",
        "content": "Third post content",
        "date_posted": datetime.utcnow(),
        "id": 3,
    },
]


@app.route("/")
@app.route("/home")
@lru_cache
def home():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(per_page=5, page=page)

    return render_template("home.html", posts=posts, title="Home")


@app.route("/about")
@lru_cache
def about():
    # return {"message": "About page"}
    # raise ValueError("Intended error")
    return render_template("about.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegistrationForm()
    if form.validate_on_submit():
        # hash password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        user = User(
            username=form.username.data, email=form.email.data, password=hashed_password
        )
        # write user to database
        db.session.add(user)
        db.session.commit()
        # flash message
        flash(
            f"Account created for {form.username.data}! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash(
                f"Login successful. Welcome back, {user.username}!", "success")

            # redirect?
            next_page = request.args.get("next")

            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please check email or password", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

def save_image(form_picture):
    new_image_name = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    image_filename = new_image_name + f_ext

    picture_path = os.path.join(
        app.root_path, "static", "profile_pics", image_filename)

    # resize image
    output_size = (125, 125)
    image = Image.open(form_picture)
    image.thumbnail(output_size)

    image.save(picture_path)
    # form_picture.save(picture_path)
    return image_filename

def delete_image(image_name):
    if image_name == "default.jpg":
        return
    try:
        image_path = os.path.join(
            app.root_path, "static", "profile_pics", image_name)
        return os.remove(image_path)
    except Exception:
        return


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            old_image_filename = current_user.image_file
            new_image_filename = save_image(form.picture.data)

            # update current image
            current_user.image_file = new_image_filename
            # delete old image
            delete_image(old_image_filename)

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated successfully!", "success")
        return redirect(url_for("account"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for(
        "static", filename=f"profile_pics/{current_user.image_file}")
    return render_template(
        "account.html", title="Account", image_file=image_file, form=form
    )


@app.route("/post/new", methods=["GET", "POST"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data, content=form.content.data, author=current_user
        )
        db.session.add(post)
        db.session.commit()

        flash("Post create successfully.", "success")
        return redirect(url_for("post", post_id=post.id))
        # return redirect(url_for("home"))

    return render_template(
        "create_post.html", title="New Post", legend="New Post", form=form
    )


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("post.html", title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your post has been updated successfully!", "success")
        return redirect(url_for("post", post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template(
        "create_post.html", title="Update Post", form=form, legend="Update Post"
    )


@app.route("/post/<int:post_id>/delete", methods=["POST"])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted successfully!", "success")
    return redirect(url_for("home"))


@app.route("/user/<string:username>")
@lru_cache
def user_posts(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get("page", 1, type=int)

    posts = (
        Post.query.filter_by(author=user)
        .order_by(Post.date_posted.desc())
        .paginate(page=page, per_page=5)
    )
    return render_template("user_posts.html", posts=posts, user=user, title="Home")
