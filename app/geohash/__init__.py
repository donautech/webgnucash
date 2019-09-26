from flask import Blueprint

bp = Blueprint('geohash', __name__)

from app.geohash import routes
from app.geohash import gen_geohashes