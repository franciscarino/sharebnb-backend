from sqlalchemy import or_
import os
from dotenv import load_dotenv

from flask import (Flask, request, jsonify)

from flask_debugtoolbar import DebugToolbarExtension
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError

from models import (
    db, connect_db, User, Listing)

from flask_jwt_extended import (create_access_token, jwt_required)

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

    data = request.json

    user = User.signup(
        username=data.get("username"),
        password=data.get("password"),
        email=data.get("email"),
        bio=data.get("bio")
    )

    db.session.commit()

    access_token = create_access_token(identity=user.username)

    return jsonify(token=access_token), 201


@app.route('/api/login', methods=["POST"])
def login():
    """Handle user login and return token."""

    username = request.json.get("username", None)
    password = request.json.get("password", None)
    user = User.authenticate(username, password)

    if not user:
        return jsonify({"error": "invalid credentials"}), 400

    access_token = create_access_token(identity=username)

    return jsonify(token=access_token)


@app.route('/api/users/<username>', methods=["GET"])
@jwt_required()
def get_user(username):
    """Return user object as json."""

    user = User.query.filter_by(username=username).one()
    serialized = User.serialize(user)

    return jsonify(user=serialized)
