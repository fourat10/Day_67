from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date
from datetime import datetime
import os


app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
Bootstrap5(app)
ckeditor = CKEditor(app)


# CREATE DATABASE
class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///posts.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle")
    name = StringField("Author", validators=[DataRequired()])
    url = StringField("Image URL", validators=[URL()])
    content = CKEditorField("Content", validators=[DataRequired()])
    submit = SubmitField("Submit")


"""
with app.app_context():
    db.create_all()
"""


@app.route('/')
def get_all_posts():
    # TODO: Query the database for all the posts. Convert the data to a python list.
    blogs = db.session.execute(db.select(BlogPost)).scalars().all()
    posts = []
    for blog in blogs:
        posts.append(blog)
    return render_template("index.html", all_posts=posts)


# TODO: Add a route so that you can click on individual posts.
@app.route('/<int:post_id>')
def show_post(post_id):
    # TODO: Retrieve a BlogPost from the database based on the post_id
    # requested_post = db.get_or_404(BlogPost, post_id)
    requested_post = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalars().all()
    return render_template("post.html", post=requested_post[0])


# TODO: add_new_post() to create a new blog post
@app.route('/new-post', methods=["GET", "POST"])
def post_post():
    form = PostForm()
    if form.validate_on_submit():
        # Process the form data and add it to the database
        print(form.subtitle.data)
        # Get today's date
        today_date = datetime.today()

        # Format the date
        formatted_date = today_date.strftime("%B %d, %Y")

        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            name=form.name.data,
            url=form.url.data,
            content=form.content.data,
            date=formatted_date,
        )

        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for('get_all_posts'))  # or wherever you want to redirect after submission
    return render_template("make-post.html", form=form)



# TODO: edit_post() to change an existing blog post
@app.route("/edit-post/<post_id>", methods=["GET","POST"])
def edit_post(post_id):

    post = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
    valid = False
    if post :
        valid = True
    edit_form = PostForm(
        title=post.title,
        subtitle=post.subtitle,
        url=post.img_url,
        name=post.author,
        content=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.url.data
        post.author = edit_form.name.data
        post.body = edit_form.content.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form , test=valid)


# TODO: delete_post() to remove a blog post from the database
@app.route("/delete-post/<post_id>", methods=["GET","DELETE"])
def delete_post(post_id):
    post = db.session.execute(db.select(BlogPost).where(BlogPost.id == post_id)).scalar()
    if post :
        db.session.delete(post)
        db.session.commit()
    return redirect(url_for("get_all_posts"))
# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=False)
