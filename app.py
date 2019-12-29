import datetime
import functools
import os
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

from main import app, db
from models import Post

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
    return render_template('index.html', entries=Post.public().all())

def _create_or_edit(post, template):
    if request.method == 'POST':
        post.title = request.form.get('title') or ''
        post.content = request.form.get('content') or ''
        post.published = True if request.form.get('published') == 'y' else False
        if not (post.title and post.content):
            flash('Title and Content are required.', 'danger')
        else:
            try:
                post.save()
            except exc.IntegrityError:
                flash('Error: this title is already in use.', 'danger')
            else:
                flash('Post saved successfully.', 'success')
                if post.published:
                    return redirect(url_for('detail', slug=post.slug))
                else:
                    return redirect(url_for('edit', slug=post.slug))

    return render_template(template, post=post)

@app.route('/create/', methods=['GET', 'POST'])
@login_required
def create():
    return _create_or_edit(Post(title='', content=''), 'create.html')

@app.route('/drafts/')
@login_required
def drafts():
    return render_template('index.html', entries=Post.drafts().all())


@app.route('/about/')
def about():
    query = Post.query.filter(Post.slug == 'about')
    post = query.first()
    try:
        return render_template('detail.html', post=post, slug=post.slug)
    except AttributeError:
        return not_found(None);

@app.route('/contact/')
def contact():
    query = Post.query.filter(Post.slug == 'contact')
    post = query.first()
    try:
        return render_template('detail.html', post=post, slug=post.slug)
    except AttributeError:
        return not_found(None);

@app.route('/posts/<slug>/')
def detail(slug):
    if session.get('logged_in'):
        query = Post.query.filter(Post.slug == slug)
    else:
        query = Post.public().filter(Post.slug == slug)
    post = query.first()
    try:
        return render_template('detail.html', post=post, slug=post.slug)
    except AttributeError:
        return not_found(None);


@app.route('/posts/<slug>/edit/', methods=['GET', 'POST'])
@login_required
def edit(slug):
    post = Post.query.filter(Post.slug == slug).first()
    return _create_or_edit(post, 'edit.html')

@app.errorhandler(404)
def not_found(exc):
    flash('That page does not exist', 'danger')
    return render_template('index.html', entries=Post.public().all())

def main():
    db.create_all()
    app.run(debug=True)

if __name__ == '__main__':
    main()
