import datetime
import re

from flask import Markup
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm.exc import NoResultFound

from main import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(128))

    def __init__(self, username, password):
        self.username = username.lower()
        self.set_password(password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def get(cls, username):
        try:
            return User.query.filter(User.username == username.lower()).one()
        except NoResultFound:
            return None

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), unique=True)

    posts = db.relationship("Post", secondary="post_tag", back_populates="tags")

class PostTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(500))
    slug = db.Column(db.String(500), unique=True)
    content = db.Column(db.Text)
    published = db.Column(db.Boolean)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    tags = db.relationship("Tag", secondary="post_tag", back_populates="posts")
    comments = db.relationship("Comment")
    images = db.relationship("Image")


    @property
    def html_content(self):
        """
        Generate HTML representation of the markdown-formatted blog post
        """
        hilite = CodeHiliteExtension(linenums=False, css_class='highlight')
        extras = ExtraExtension()
        markdown_content = markdown(self.content, extensions=[hilite, extras])
        return Markup(markdown_content)

    def add_tag(self, name):
        existing_tag = Tag.query.filter(Tag.name == name).first()
        if existing_tag:
            self.tags.append(existing_tag)
            self.save()
        else:
            new_tag = Tag()
            new_tag.name = name
            db.session.add(new_tag)
            self.tags.append(new_tag)
            self.save()


    def save(self, *args, **kwargs):
        # Generate a URL-friendly representation of the post's title.
        if not self.slug:
            self.slug = re.sub('[^\w]+', '-', self.title.lower()).strip('-')
        db.session.add(self)
        db.session.commit()

    @classmethod
    def public(cls):
        return Post.query.filter(
            Post.published == True,
            Post.slug != 'about',
            Post.slug != 'contact'
        ).order_by(Post.created.desc())

    @classmethod
    def drafts(cls):
        return Post.query.filter(Post.published == False).order_by(Post.created.desc())

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    name = db.Column(db.String(128))
    comment = db.Column(db.Text)

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    location = db.Column(db.Text)

    def __init__(self, post_id, location):
        self.post_id = post_id
        self.location = location

    def save(self):
        db.session.add(self)
        db.session.commit()