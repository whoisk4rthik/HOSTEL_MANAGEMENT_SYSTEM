from flask import Blueprint
from database_connection import mysql # ADDED: Import the globally shared MySQL object

bp = Blueprint('mess', __name__, url_prefix='/mess')

# Additional mess management routes can be added here