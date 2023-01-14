from flask_jwt_extended import JWTManager
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import create_access_token
from sqlalchemy import or_
import os
from dotenv import load_dotenv
from forms import ListingAddForm, UserAddForm, CSRFProtection, LoginForm
from sqlalchemy.exc import IntegrityError

from flask import (
    Flask, render_template, request, flash, redirect, session, g, jsonify
)

from models import (
    db, connect_db, User, Listing)

load_dotenv()

CURR_USER_KEY = "curr_user"


# database_url = os.environ['DATABASE_URL']
# database_url = database_url.replace('postgres://', 'postgresql://')

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ['DATABASE_URL'].replace("postgres://", "postgresql://"))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
# toolbar = DebugToolbarExtension(app)

connect_db(app)


##############################################################################
# User signup/login/logout

# @app.before_request
# def add_user_to_g():
#     """If we're logged in, add curr user to Flask global."""

#     if CURR_USER_KEY in session:
#         g.user = User.query.get(session[CURR_USER_KEY])

#     else:
#         g.user = None


# @app.before_request
# def add_csrf_only_form():
#     """Add a CSRF-only form so that every route can use it."""

#     g.csrf_form = CSRFProtection()


# def do_login(user):
#     """Log in user."""

#     session[CURR_USER_KEY] = user.username


# def do_logout():
#     """Log out user."""

#     if CURR_USER_KEY in session:
#         del session[CURR_USER_KEY]


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

    db.session.add(user)
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
        return jsonify({"Error": "invalid credentials"}), 400

    access_token = create_access_token(identity=username)

    return jsonify(token=access_token)


# @app.post('/api/logout')
# def logout():
#     """Handle logout of user and redirect to homepage."""

#     form = g.csrf_form

#     if not form.validate_on_submit() or not g.user:
#         flash("Access unauthorized.", "danger")
#         return redirect("/")

#     do_logout()

#     flash("You have successfully logged out.", 'success')
#     return redirect("/login")

##############################################################################
# Standard restful routes for listings:


@app.get('/api/listings')
def list_listings():
    """Page with listing of listings."""

    search = request.args.get('q')

    listings = Listing.query.all()

    if not search:
        listings = Listing.query.all()
    else:
        listings = Listing.query.filter(or_(Listing.location.ilike(f"%{search}%"),
                                            Listing.title.ilike(f"%{search}%"),
                                            Listing.description.ilike(f"%{search}%"))
                                        ).all()

    return render_template('listings.html', listings=listings)


@app.get('/api/listings/<int:listing_id>')
def show_listing(listing_id):
    """Show listing details."""

    listing = Listing.query.get_or_404(listing_id)

    return render_template('listing-details.html', listing=listing)


@app.post('/api/listings/<int:listing_id>/delete')
def delete_listing(listing_id):
    """Delete listing."""

    form = g.csrf_form

    listing = Listing.query.get_or_404(listing_id)

    if not form.validate_on_submit() or (g.user.username != listing.created_by):
        flash("Access unauthorized.", "danger")
        return redirect("/")

    db.session.delete(listing)
    db.session.commit()

    flash("Listing deleted.", "success")
    return redirect("/listings")


@app.post('/api/listings/<int:listing_id>/reserve')
def reserve_listing(listing_id):
    """Reserve a listing."""

    form = g.csrf_form

    listing = Listing.query.get_or_404(listing_id)
    curr_user = g.user.username

    if not form.validate_on_submit() or not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/listings/{listing_id}")

    listing.rented_by = curr_user

    db.session.commit()

    flash("Booking Confirmed!", "success")
    return redirect(f"/listings/{listing_id}")


@app.route('/api/listings/add', methods=["GET", "POST"])
def add_listings():
    """add a listing to listings."""
    if not g.user:
        flash("Please sign-up to create a listing", "warning")
        return redirect("/")

    form = ListingAddForm()

    if form.validate_on_submit():

        data = form.data
        file = request.files['photo_url']
        username = g.user.username

        Listing.create(data, file, username)
        db.session.commit()
        flash("Listing successfully added.", "success")
        return redirect(f"/users/{username}")

    return render_template('add-listing.html', form=form)

##############################################################################
# General user routes:


@app.get('/api/users/<username>')
def user_profile(username):
    """Page with listing of properties rented by logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    listings = Listing.query.filter_by(created_by=username)
    user = User.query.get_or_404(username)

    return render_template('/user-page.html', user=user, listings=listings)


@app.get('/api/users/<username>/reservations')
def user_reservations(username):
    """Page with listing of properties rented by logged-in user."""

    curr_user = g.user.username

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    if curr_user != username:
        return redirect(f"/users/{curr_user}/reservations")

    listings = Listing.query.filter_by(rented_by=username)
    user = User.query.get_or_404(username)

    return render_template('/my-reservations.html', user=user, listings=listings)


##############################################################################
# General routes:

@app.get('/')
def homepage():
    """ show listings page."""

    return redirect("/api/listings")


@app.errorhandler(404)
def page_not_found(e):
    """404 NOT FOUND page."""

    return jsonify({"error": "Page not found."}), 404
