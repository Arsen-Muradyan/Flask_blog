from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug import secure_filename
from passlib.hash import sha256_crypt
import re
import os
from functools import wraps
app = Flask(__name__)
db = SQLAlchemy(app)
# Configure Database Connection
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:123456@localhost/myflaskapp'
# Configure Image Upload Settings
app.config['UPLOAD_FOLDER'] = os.getcwd() + '/static/images'
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024
ALLOWED_EXTENISION = ('.png', '.jpg', '.jpeg', '.gif')
# Import Models
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime)
    def __init__(self, title, content, image, user_id):
      self.title = title
      self.image = image
      self.user_id = user_id
      self.content = content
      self.created_at = datetime.now()
class User(db.Model):
  __tablename__ = 'users'
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(255), nullable=False)
  email = db.Column(db.String(255), nullable=False, unique=True)
  password = db.Column(db.String(255), nullable=False)
  def __init__(self, username, email, password):
    self.username = username
    self.email = email
    self.password = password
# Check image Extensions Helper Function
def allowed_extenision(name):
  return name.endswith(ALLOWED_EXTENISION)
# Check Login
def login_required(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if 'logged_in' in session:
      return f(*args, **kwargs) 
    else:
      return redirect(url_for('login'))
  return wrap
def login_not_required(f):
  @wraps(f)
  def wrap(*args, **kwargs):
    if not 'logged_in' in session:
      return f(*args, **kwargs) 
    else:
      flash("You are logged in", 'info')
      return redirect(url_for('dashboard'))
  return wrap
"""
  @path /
  @name index
  @method GET
  @desc Home Page
  @access public
"""
@app.route('/')
def index():
  return render_template('index.html')
"""
  @path /posts
  @name posts
  @method GET
  @desc Posts Page
  @access public
"""
@app.route('/posts')
def posts():
  print('logged in' in session)
  posts = Post.query.order_by(Post.created_at).all()
  return render_template('posts/posts.html', posts=posts)
"""
  @path /posts/create
  @name create
  @method GET, POST
  @desc Create action and page
  @access private
"""
@app.route('/posts/create', methods=["GET", "POST"])
@login_required
def create():
  if request.method == "POST":
    title = request.form['title']
    content = request.form['content']
    image = request.files['image']
    if title and content and image and len(image.filename) <= 255 and allowed_extenision(image.filename):
      image.filename = str(str(datetime.now())+'_'+str(image.filename))
      filename = secure_filename(image.filename)
      user = User.query.filter_by(email=session['email']).first()
      post = Post(title=title, image=filename, content=content, user_id=user.id)
      image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      db.session.add(post)
      db.session.commit()
      return redirect(url_for('posts'))
  return render_template('posts/create.html', posts=posts)
"""
  @path /posts/:id
  @name show
  @vairables id
  @method GET
  @desc Show Post
  @access public
"""
@app.route('/posts/<int:id>')
def show(id):
  user = None
  if 'logged_in' in session:
    user = User.query.filter_by(email=session['email']).first()
  post = Post.query.get(id)
  return render_template('posts/post.html', post=post, user=user)
"""
  @path /posts/:id/edit
  @name edit
  @vairbales id
  @methods GET, POST
  @desc Post Update action and page
  @access private
"""
@app.route('/posts/<int:id>/edit', methods=["GET", "POST"])
@login_required
def edit(id):
  post = Post.query.get(id)
  user = User.query.filter_by(email=session['email']).first()
  if user.id == post.user_id:
    if request.method == "POST":
      title = request.form.get('title')
      content = request.form.get('content')
      image = request.files.get('image')
      if title and content and image and len(image.filename) <= 255 and allowed_extenision(image.filename):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.image))
        image.filename = str(str(datetime.now())+'_'+str(image.filename))
        filename = secure_filename(image.filename)
        post.title = title
        post.content = content
        post.image = filename
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        db.session.commit()
        return redirect(url_for('show', id=id))
      elif title and content and not image:
        post.title = title
        post.content = content
        db.session.commit()
        return redirect(url_for('show', id=id))
    return render_template('posts/edit.html', post=post)
  else:
    return redirect(url_for('dashboard'))
"""
  @path /posts/:id/delete
  @name delete
  @vairbales id
  @methods POST
  @desc Post Delete action
  @access private
"""
@app.route('/posts/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
  user = User.query.filter_by(email=session['email']).first()
  post = Post.query.get(id)
  if user.id == post.user_id:
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.image))
    db.session.delete(post)
    db.session.commit()
  else:
    return redirect(url_for('dashboard'))
  return redirect(url_for('dashboard'))
"""
  @path /register
  @methods GET, POST
  @desc Register Page and Action
  @name register
  @access public
"""
@app.route('/register', methods=["GET", "POST"])
@login_not_required
def register():
  if request.method == "POST":
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    password2 = request.form.get('confirm')
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
    if username and email and password and password2:
      if db.session.query(User).filter(User.email == email).count() > 0:
        flash("Email Already Taken", 'danger')
      elif not re.search(regex, email):
        flash("Not Email Syntax", 'danger')
      elif password2 != password:
        flash('Confirm Password', 'danger')
      else:
        user = User(email=email, password=password, username=username)
        user.password =  sha256_crypt.encrypt(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    else:
      flash('All fields required', 'danger')
  return render_template('auth/register.html')
"""
  @path /login
  @methods GET, POST
  @desc Login Page and Action
  @name login
  @access public
"""
@app.route('/login', methods=["GET", "POST"])
@login_not_required
def login():
  if request.method == "POST":
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()
    if user:
      if sha256_crypt.verify(password, user.password):
        session['email'] = email
        session['logged_in'] = True
        return redirect(url_for('index'))
      else:
        flash('Password Not Match', 'danger')
    else:
      flash('User not found', 'danger')
  return render_template('auth/login.html')  
"""
  @path /logout
  @methods GET
  @desc Logout Action
  @name logout
  @access private
"""
@app.route('/logout')
@login_required
def logout():      
  session.clear()
  return redirect(url_for('index'))
"""
  @path /dashboard
  @methods GET
  @desc Dashboard Page
  @name dashboard
  @access private
"""
@app.route('/dashboard')
@login_required
def dashboard():
  user = User.query.filter_by(email=session['email']).first()
  posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at).all()

  return render_template('dashboard.html', posts=posts, user=user)
# Run Script
if __name__ == '__main__':
  app.secret_key = 'secret123'
  app.run(debug=True)