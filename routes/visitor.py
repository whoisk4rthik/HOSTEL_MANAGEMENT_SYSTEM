from flask import Blueprint
from database_connection import mysql # ADDED: Import the globally shared MySQL object

bp = Blueprint('visitor', __name__, url_prefix='/visitor')

# Additional visitor management routes can be added here.