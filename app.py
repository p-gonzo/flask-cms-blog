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
    url_for,
)
from werkzeug.utils import secure_filename
from sqlalchemy import exc

from main import app, db
from models import Post, User, Image

import boto3

s3 = boto3.resource('s3')
s3_bucket = s3.Bucket(os.environ['AWS_BUCKET_NAME'])

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
    if request.method == 'POST' and request.form.get('password') and request.form.get('username'):
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.get(username)
        if user and user.check_password(password):
            session['logged_in'] = True
            session['user_id'] = user.id
            session.permanent = True  # Use cookie to store session.
            flash('Logged in.', 'success')
            return redirect(next_url or url_for('index'))
        else:
            flash('Bad user/password combination.', 'danger')
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

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def _create_or_edit(post, template):
    """
    Create or edit post
    Also used for uploading images
    """
    if request.method == 'POST':
        post.user_id = session['user_id']
        post.title = request.form.get('title') or ''
        post.content = request.form.get('content') or ''
        post.published = True if request.form.get('published') == 'y' else False
        if not (post.title and post.content):
            flash('Title and body required.', 'danger')
        else:
            try:
                post.save()
            except exc.IntegrityError:
                flash('Error: title already in use.', 'danger')
            else:
                flash('Post saved.', 'success')
                if request.form.get('action') == 'preview':
                    return redirect(url_for('preview', slug=post.slug))
                elif request.form.get('action') == 'upload-image':
                    if 'file' not in request.files:
                        flash('No file part', 'danger')
                        return redirect(request.url)
                    file = request.files['file']
                    if file.filename == '':
                        flash('No selected file', 'danger')
                        return redirect(request.url)
                    if file and allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        s3_bucket.put_object(Key=f'{post.slug}/{filename}', Body=file, ACL='public-read')
                        new_image = Image(post.id, f'{os.environ["AWS_BUCKET_URL"]}/{post.slug}/{filename}')
                        new_image.save()
                        return redirect(request.url)
                elif post.published:
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

@app.route('/preview/<slug>/')
@login_required
def preview(slug):
    post = Post.query.filter(Post.slug == slug).first()
    try:
        return render_template('detail.html', post=post, slug=post.slug, preview=True)
    except AttributeError:
        return not_found(None);


@app.route('/posts/<slug>/edit/', methods=['GET', 'POST'])
@login_required
def edit(slug):
    post = Post.query.filter(Post.slug == slug).first()
    return _create_or_edit(post, 'edit.html')

@app.errorhandler(404)
def not_found(exc):
    flash('Page does not exist', 'danger')
    return render_template('index.html', entries=Post.public().all())

def main():
    db.create_all()
    app.run(debug=True)

if __name__ == '__main__':
    main()
