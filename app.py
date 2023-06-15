from sqlalchemy import or_
import os
from dotenv import load_dotenv

from flask import (Flask, request, jsonify)

# from flask_debugtoolbar import DebugToolbarExtension
from flask_cors import CORS
# from sqlalchemy.exc import IntegrityError

from models import (
    db, connect_db, User, Listing)

from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, JWTManager)

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

# toolbar = DebugToolbarExtension(app)

connect_db(app)
jwt = JWTManager(app)

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
# @jwt_required()
def get_user(username):
    """Return user object as json."""

    user = User.query.filter_by(username=username).one()
    serialized = User.serialize(user)

    return jsonify(user=serialized)


@app.route('/api/users/<username>/reservations', methods=["GET"])
# @jwt_required()
def get_user_reservations(username):
    """Returns a user's reservations as JSON"""

    reservations = Listing.query.with_entities(
        Listing.title, Listing.id).filter_by(rented_by=username)

    serialized = [{"username": username,
                   "listingId": r.id}
                  for r in reservations]

    return jsonify(reservations=serialized)


##############################################################################
# Listings routes:

@app.get('/api/listings')
def get_listings():
    """Return all listings as JSON"""

    search = request.args.get('q')

    listings = Listing.query.all()

    if not search:
        listings = Listing.query.all()
    else:
        listings = Listing.query.filter(or_(Listing.location.ilike(f"%{search}%"),
                                            Listing.title.ilike(f"%{search}%"),
                                            Listing.description.ilike(f"%{search}%"))
                                        ).all()

    serialized = [Listing.serialize(listing) for listing in listings]

    return jsonify(listings=serialized)


@app.get('/api/listings/<int:listing_id>')
def get_listing(listing_id):
    """Return listing as JSON"""

    listing = Listing.query.filter_by(id=listing_id).one()
    serialized = Listing.serialize(listing)

    return jsonify(listing=serialized)


# TODO: Test route
@app.post('/api/listings/add')
@jwt_required()
def create_listing():
    """Add a listing and returns listing details as JSON."""

    username = get_jwt_identity()
    user = User.query.filter_by(username=username).one()

    title = request.form.get('title')
    print("title: ", title)
    description = request.form.get('description')
    print("description: ", description)
    location = request.form.get('location')
    print("location: ", location)
    price = request.form.get('price')
    print("price: ", price)
    file = request.files['photo_url']
    print("file: ", file)    

    data = {
        "title": title,
        "description": description,
        "location": location,
        "price": price,
        "created_by": user.username,
    }
    
    print("DATA: ", data)

    listing = Listing.create(data, file, username)
    db.session.commit()

    serialized = Listing.serialize(listing)

    return jsonify(listing=serialized), 201


@app.post('/api/listings/<int:listing_id>/reserve')
@jwt_required
def reserve_listing(listing_id):
    """Reserve a listing"""

    username = get_jwt_identity()
    user = User.query.filter_by(username=username).one()
    listing = Listing.filter_by(listing_id).one()

    listing.rented_by = user
    db.session.commit()

    serialized = Listing.serialize(listing)

    return jsonify(reservation=serialized), 201


##############################################################################
# Homepage and error pages

@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return jsonify({"error": "Page not found."}), 404
