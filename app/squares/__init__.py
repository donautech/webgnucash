from flask import Blueprint

bp = Blueprint('squares', __name__)

from app.squares import addcat
from app.squares import makemodel
from app.squares import square_solver
