from flask import Blueprint
from database_connection import mysql # ADDED: Import the globally shared MySQL object

bp = Blueprint('room', __name__, url_prefix='/room')

# Additional room management routes can be added here