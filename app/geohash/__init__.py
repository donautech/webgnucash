from flask import Blueprint

bp = Blueprint('geohash', __name__)

from app.geohash import routes