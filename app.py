from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:123456@localhost/myflaskapp'
class Post(db.Model):
  __tablename__ = 'posts'
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(200), nullable=False)
  content = db.Column(db.String(200), nullable=False)
  created_at = db.Column(db.DateTime)
  def __init__(self, title, content):
    self.title = title
    self.content = content
    self.created_at = datetime.now()
@app.route('/')
def index():
  return render_template('index.html')
@app.route('/posts')
def posts():
  posts = Post.query.order_by(Post.created_at).all()
  return render_template('posts.html', posts=posts)
@app.route('/posts/create', methods=["GET", "POST"])
def create():
  if request.method == "POST":
    title = request.form['title']
    content = request.form['content']
    post = Post(title=title, content=content)
    db.session.add(post)
    db.session.commit()
  return render_template('create.html', posts=posts)
@app.route('/posts/<int:id>')
def show(id):
  post = Post.query.get(id)

  return render_template('post.html', post=post)
if __name__ == '__main__':
  app.run(debug=True)