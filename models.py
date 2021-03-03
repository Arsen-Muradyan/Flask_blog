from datetime import datetime
def models(db): 
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
  return Post, User