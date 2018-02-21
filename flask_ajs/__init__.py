from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'notsosecret'

userpass = 'mysql://root:@'
basedir  = '127.0.0.1'
dbname   = '/ajs'
socket   = '?unix_socket=/opt/lampp/var/mysql/mysql.sock'
dbname   = dbname + socket

app.config['SQLALCHEMY_DATABASE_URI'] = userpass + basedir + dbname

db = SQLAlchemy(app)
migrate = Migrate(app, db)



from . import models
from . import views
