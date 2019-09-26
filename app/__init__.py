from flask import Flask
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

app = Flask(__name__, static_url_path='/web')

from app.geohash import bp as geohash_bp
from app.squares import bp as sqares_bp


app.register_blueprint(geohash_bp, url_prefix='/geohash')
app.register_blueprint(sqares_bp, url_prefix='/squares')

app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

from app import routes  # , models
