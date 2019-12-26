import datetime
import functools
import os
import re
import urllib

from flask import (
    flash,
    redirect,
    render_template,
    request,
    Response,
    session,
    url_for
)

from sqlalchemy import exc
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension

from main import app, db
from models import Entry

@app.context_processor
def inject_globals():
    return {'now': datetime.datetime.utcnow()}

def login_required(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        if session.get('logged_in'):
            return fn(*args, **kwargs)
        return redirect(url_for('login', next=request.path))
    return inner

@app.route('/login/', methods=['GET', 'POST'])
def login():
    next_url = request.args.get('next') or request.form.get('next')
    if request.method == 'POST' and request.form.get('password'):
        password = request.form.get('password')
        # TODO: If using a one-way hash, you would also hash the user-submitted
        # password and do the comparison on the hashed versions.
        if password == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            session.permanent = True  # Use cookie to store session.
            flash('You are now logged in.', 'success')
            return redirect(next_url or url_for('index'))
        else:
            flash('Incorrect password.', 'danger')
    return render_template('login.html', next_url=next_url)

@app.route('/logout/', methods=['GET', 'POST'])
def logout():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('login'))
    return render_template('logout.html')

@app.route('/')
def index():
    return render_template('index.html', entries=Entry.public().all())

def _create_or_edit(entry, template):
    if request.method == 'POST':
        entry.title = request.form.get('title') or ''
        entry.content = request.form.get('content') or ''
        entry.published = True if request.form.get('published') == 'y' else False
        if not (entry.title and entry.content):
            flash('Title and Content are required.', 'danger')
        else:
            try:
                entry.save()
            except exc.IntegrityError:
                flash('Error: this title is already in use.', 'danger')
            else:
                flash('Entry saved successfully.', 'success')
                if entry.published:
                    return redirect(url_for('detail', slug=entry.slug))
                else:
                    return redirect(url_for('edit', slug=entry.slug))

    return render_template(template, entry=entry)

@app.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
    return _create_or_edit(Entry(title='', content=''), 'create.html')

@app.route('/drafts/')
@login_required
def drafts():
    return render_template('index.html', entries=Entry.drafts().all())

@app.route('/posts/<slug>/')
def detail(slug):
    if session.get('logged_in'):
        query = Entry.query.filter(Entry.slug == slug)
    else:
        query = Entry.public().filter(Entry.slug == slug)
    entry = query.first()
    return render_template('detail.html', entry=entry, slug=entry.slug)

@app.route('/posts/<slug>/edit/', methods=['GET', 'POST'])
@login_required
def edit(slug):
    entry = Entry.query.filter(Entry.slug == slug).first()
    return _create_or_edit(entry, 'edit.html')

@app.errorhandler(404)
def not_found(exc):
    return Response('<h3>Not found</h3>'), 404

def main():
    db.create_all()
    app.run(debug=True)

if __name__ == '__main__':
    main()
