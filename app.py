from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug import secure_filename
import os
app = Flask(__name__)
db = SQLAlchemy(app)
# Configure Database Connection
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:123456@localhost/myflaskapp'
# Configure Image Upload Settings
app.config['UPLOAD_FOLDER'] = os.getcwd() + '/static/images'
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024
ALLOWED_EXTENISION = ('.png', '.jpg', '.jpeg', '.gif')
# Create Post Model
class Post(db.Model):
  __tablename__ = 'posts'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(200), nullable=False)
  content = db.Column(db.Text, nullable=False)
  image = db.Column(db.String(255), nullable=False)
  created_at = db.Column(db.DateTime)
  def __init__(self, title, content, image):
    self.title = title
    self.image = image
    self.content = content
    self.created_at = datetime.now()
# Check image Extensions Helper Function
def allowed_extenision(name):
  return name.endswith(ALLOWED_EXTENISION)
"""
  @path /
  @name index
  @method GET
  @desc Home Page
"""
@app.route('/')
def index():
  return render_template('index.html')
"""
  @path /posts
  @name posts
  @method GET
  @desc Posts Page
"""
@app.route('/posts')
def posts():
  posts = Post.query.order_by(Post.created_at).all()
  return render_template('posts.html', posts=posts)
"""
  @path /posts/create
  @name create
  @method GET, POST
  @desc Create action and page
"""
@app.route('/posts/create', methods=["GET", "POST"])
def create():
  if request.method == "POST":
    title = request.form['title']
    content = request.form['content']
    image = request.files['image']
    if title and content and image and len(image.filename) <= 255 and allowed_extenision(image.filename):
      image.filename = str(str(datetime.now())+'_'+str(image.filename))
      filename = secure_filename(image.filename)
      post = Post(title=title, image=filename, content=content)
      image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      db.session.add(post)
      db.session.commit()
      return redirect(url_for('posts'))
  return render_template('create.html', posts=posts)
"""
  @path /posts/:id
  @name show
  @vairables id
  @method GET
  @desc Show Post
"""
@app.route('/posts/<int:id>')
def show(id):
  post = Post.query.get(id)
  return render_template('post.html', post=post)
"""
  @path /posts/:id/edit
  @name edit
  @vairbales id
  @methods GET, POST
  @desc Post Update action and page
"""
@app.route('/posts/<int:id>/edit', methods=["GET", "POST"])
def edit(id):
  post = Post.query.get(id)
  if request.method == "POST":
    title = request.form.get('title')
    content = request.form.get('content')
    image = request.files.get('image')
    if title and content and image and len(image.filename) <= 255 and allowed_extenision(image.filename):
      os.remove(os.path.join(app.config['UPLOAD_FOLDER'], image.filename))
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
  return render_template('edit.html', post=post)
"""
  @path /posts/:id/delete
  @name delete
  @vairbales id
  @methods POST
  @desc Post Delete action
"""
@app.route('/posts/<int:id>/delete', methods=['POST'])
def delete(id):
  post = Post.query.get(id)
  os.remove(os.path.join(app.config['UPLOAD_FOLDER'], post.image))
  db.session.delete(post)
  db.session.commit()
  return redirect(url_for('posts'))
# Run Script
if __name__ == '__main__':
  app.secret_key = 'secret123'
  app.run(debug=True)