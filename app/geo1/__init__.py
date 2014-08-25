import os
from flask import Flask
 
app = Flask(__name__)
 
app.secret_key = 'development key'
 
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'joze.emajler@gmail.com'
app.config["MAIL_PASSWORD"] = 'KtfM7D3lGw'
 
from routes import mail
mail.init_app(app)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://geo1:geo1@localhost/geo1_development'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://geo1:geo1@' + os.environ['DB_PORT_3306_TCP_ADDR'] + '/geo1_development'

from models import db
db.init_app(app)
 
import geo1.routes

