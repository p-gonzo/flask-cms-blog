import datetime
import re

from flask import Markup
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension

from main import db

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500))
    slug = db.Column(db.String(500), unique=True)
    content = db.Column(db.Text)
    published = db.Column(db.Boolean)
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    @property
    def html_content(self):
        """
        Generate HTML representation of the markdown-formatted blog post
        """
        hilite = CodeHiliteExtension(linenums=False, css_class='highlight')
        extras = ExtraExtension()
        markdown_content = markdown(self.content, extensions=[hilite, extras])
        return Markup(markdown_content)

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