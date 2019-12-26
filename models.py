import datetime

from flask import Markup
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension

from main import db

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    slug = db.Column(db.String(250), unique=True)
    content = db.Column(db.String(1000))
    published = db.Column(db.Boolean,index=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow, index=True)

    @property
    def html_content(self):
        """
        Generate HTML representation of the markdown-formatted blog entry
        """
        hilite = CodeHiliteExtension(linenums=False, css_class='highlight')
        extras = ExtraExtension()
        markdown_content = markdown(self.content, extensions=[hilite, extras])
        return Markup(markdown_content)

    def save(self, *args, **kwargs):
        # Generate a URL-friendly representation of the entry's title.
        if not self.slug:
            self.slug = re.sub('[^\w]+', '-', self.title.lower()).strip('-')
        db.session.add(self)
        db.session.commit()

    @classmethod
    def public(cls):
        return Entry.query.filter(Entry.published == True).order_by(Entry.timestamp.desc())

    @classmethod
    def drafts(cls):
        return Entry.query.filter(Entry.published == False).order_by(Entry.timestamp.desc())