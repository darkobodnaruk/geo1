from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
 
db = SQLAlchemy()
 
class User(db.Model):
  __tablename__ = 'users'
  uid = db.Column(db.Integer, primary_key = True)
  email = db.Column(db.String(120), unique=True)
  pwdhash = db.Column(db.String(54))
   
  def __init__(self, email, password):
    self.email = email.lower()
    self.set_password(password)
     
  def set_password(self, password):
    self.pwdhash = generate_password_hash(password)
   
  def check_password(self, password):
    return check_password_hash(self.pwdhash, password)


class VisitorLocation(db.Model):
  __tablename__ = 'visitor_locations'
  id = db.Column(db.Integer, primary_key = True)
  uid = db.Column(db.Integer)
  visitor_id = db.Column(db.String(120))
  lat = db.Column(db.Float)
  lng = db.Column(db.Float)
  dt = db.Column(db.DateTime)

  def __init__(self, uid, visitor_id, lat, lng, dt):
    self.uid = uid
    self.visitor_id = visitor_id
    self.lat = lat
    self.lng = lng
    self.dt = dt

class LastLocation(db.Model):
  __tablename__ = 'last_locations'
  id = db.Column(db.Integer, primary_key = True)
  uid = db.Column(db.Integer)
  visitor_id = db.Column(db.String(120))
  lat = db.Column(db.Float)
  lng = db.Column(db.Float)
  dt = db.Column(db.DateTime)

  def __init__(self):
    pass
