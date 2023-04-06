from sqlalchemy import or_
import os
from dotenv import load_dotenv

from flask import (Flask, request, jsonify)

from flask_debugtoolbar import DebugToolbarExtension
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError

from models import (
    db, connect_db, User, Listing)

load_dotenv()

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
CORS(app)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['JWT_SECRET_KEY'] = os.environ['JWT_SECRET_KEY']
app.config['AWS_ACCESS_KEY'] = os.environ['AWS_ACCESS_KEY']
app.config['AWS_SECRET_ACCESS_KEY'] = os.environ['AWS_SECRET_ACCESS_KEY']
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)
# TODO: jwt = JWTManager(app)

SECRET_KEY = os.environ['SECRET_KEY']


##############################################################################
# User signup/login/logout

@app.route('/api/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB.
    """
