import os
import math
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///yalieats.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET"])
def home():
    return render_template("before_main.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user for an account."""
    
    # POST
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("first_name"):
            return render_template("missing_firstname.html")
        elif not request.form.get("last_name"):
            return render_template("missing_lastname.html")
        elif not request.form.get("email_address"):
            return render_template("missing_emailaddress.html")
        elif not request.form.get("username"):
            return render_template("missing_username.html")
        elif not request.form.get("password"):
            return render_template("missing_password.html")
        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("no_match.html")

        # Add user to database
        try:
            id = db.execute("INSERT INTO members (first_name, last_name, email_address, username, password) VALUES(?, ?, ?, ?, ?)",
                            request.form.get("first_name"), request.form.get("last_name"), request.form.get("email_address"),request.form.get("username"),
                            generate_password_hash(request.form.get("password")))
        except ValueError:
            return render_template("username_taken.html")

        # Log user in
        session["member_id"] = id

        # Let user know they're registered
        flash("Registered!")
        return redirect("/")

    # GET
    else:
        return render_template("register.html")

@app.route("/before_main", methods=["GET"])
def before_main():
    return render_template("before_main.html")

@app.route("/main", methods=["GET"])
def main():
    return render_template("main.html")

@app.route("/your_account", methods=["GET"])
def your_account():
    return render_template("your_account.html")

@app.route("/search_by_restaurant", methods=["GET"])
def search_by_restaurant():
    return render_template("search_by_restaurant.html")

@app.route("/search_by_filters", methods=["GET"])
def search_by_filters():
    return render_template("search_by_filters.html")

@app.route("/reviews_static", methods=["GET"])
def reviews_static():
    return render_template("reviews.html")

@app.route("/about_us", methods=["GET"])
def about_us():
    return render_template("about_us.html")

@app.route("/contact_us", methods=["GET"])
def contact_us():
    return render_template("contact_us.html")

@app.route("/write_a_review", methods=["GET", "POST"])
def write_a_review():
    """Access the form to write a review and actually be able to write and submit a review to the database"""
    
    # POST
    if request.method == "POST":

        # Validate form submission
        if not request.form.get("restaurant_name"):
            return render_template("missing_restaurant_name.html")
        
        try:
            restaurant_entry = db.execute("SELECT restaurant_name FROM restaurants WHERE restaurant_name = :name", name=request.form.get("restaurant_name"))
            restaurant_name = restaurant_entry[0]["restaurant_name"]
        except IndexError:
            return render_template("invalid_restaurant_name.html")

        if not request.form.get("price_rating"):
            return render_template("missing_price_rating.html")
        elif not request.form.get("portion_size_rating"):
            return render_template("missing_portion_size.html")
        elif not request.form.get("recommendation"):
            return render_template("missing_recommendation.html")
        elif not request.form.get("overall_restaurant_rating"):
            return render_template("missing_overall_restaurant_rating.html")
        elif not request.form.get("deliciousness_rating"):
            return render_template("missing_overall_deliciousness_rating.html")
        elif not request.form.get("review_text"):
            return render_template("missing_review_text.html")
        
        id_entry = db.execute("SELECT id FROM restaurants JOIN reviews ON reviews.restaurant_id = restaurants.id WHERE restaurants.restaurant_name = :id", id=request.form.get("restaurant_name"))
        get_id = id_entry[0]["id"]

        new_review = db.execute("INSERT INTO reviews (restaurant_id, memberID, price_rating, portion_size_rating, recommendation, overall_restaurant_rating, deliciousness_rating, review_text) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", get_id, session["member_id"], request.form.get("price_rating"), request.form.get("portion_size_rating"), request.form.get("recommendation"), request.form.get("overall_restaurant_rating"), request.form.get("deliciousness_rating"), request.form.get("review_text"))
        return render_template("main.html")
    # GET
    else:
        return render_template("write_a_review.html")

@app.route("/reviews", methods=["POST"])
def reviews():
    """Get the reviews for a restaurant"""
    if not request.form.get("restaurant_name"):
        return render_template("restaurant_empty_error.html")
    
    review_entry = db.execute("SELECT AVG(price_rating) FROM reviews JOIN restaurants ON restaurants.id = reviews.restaurant_id WHERE restaurants.restaurant_name = :name", name=request.form.get("restaurant_name"))
    if not review_entry:
        return render_template("restaurant_search_error.html")
    else: 
        price_rating = round( review_entry[0]["AVG(price_rating)"], 1)
        review_entry1 = db.execute("SELECT AVG(portion_size_rating) FROM reviews JOIN restaurants ON restaurants.id = reviews.restaurant_id WHERE restaurants.restaurant_name = :name", name=request.form.get("restaurant_name"))
        portion_size_rating = round( review_entry1[0]["AVG(portion_size_rating)"], 1)
        review_entry2 = db.execute("SELECT recommendation FROM reviews JOIN restaurants ON restaurants.id = reviews.restaurant_id WHERE restaurants.restaurant_name = :name", name=request.form.get("restaurant_name"))
        recommendation = review_entry2[0]["recommendation"]
        review_entry3 = db.execute("SELECT AVG(overall_restaurant_rating) FROM reviews JOIN restaurants ON restaurants.id = reviews.restaurant_id WHERE restaurants.restaurant_name = :name", name=request.form.get("restaurant_name"))
        overall_restaurant_rating = round( review_entry3[0]["AVG(overall_restaurant_rating)"], 1)
        review_entry4 = db.execute("SELECT AVG(deliciousness_rating) FROM reviews JOIN restaurants ON restaurants.id = reviews.restaurant_id WHERE restaurants.restaurant_name = :name", name=request.form.get("restaurant_name"))
        deliciousness_rating = round( review_entry4[0]["AVG(deliciousness_rating)"], 1)
        review_entry5 = db.execute("SELECT review_text FROM reviews JOIN restaurants ON restaurants.id = reviews.restaurant_id WHERE restaurants.restaurant_name = :name", name=request.form.get("restaurant_name"))
        review_text = review_entry5[0]["review_text"]
        restaurant_entry = db.execute("SELECT restaurant_name FROM restaurants WHERE restaurant_name = :name", name=request.form.get("restaurant_name"))
        restaurant_name = restaurant_entry[0]["restaurant_name"]
        bang_for_buck_rating = round((.35 * portion_size_rating + .35 * price_rating + .30 * deliciousness_rating), 1)
        
    return render_template("review_result.html", restaurant_name=restaurant_name, price_rating=price_rating, portion_size_rating=portion_size_rating, recommendation=recommendation, overall_restaurant_rating=overall_restaurant_rating, deliciousness_rating=deliciousness_rating, review_text=review_text, bang_for_buck_rating=bang_for_buck_rating)


@app.route("/search_for_restaurant", methods=["POST"])
def search_for_restaurant():
    """Allows the user to enter a restaurant name and get information about it"""
    if not request.form.get("restaurant_name"):
        return render_template("restaurant_empty_error.html")
    
    restaurant_entry = db.execute("SELECT restaurant_name FROM restaurants WHERE restaurant_name = :name", name=request.form.get("restaurant_name"))
    if not restaurant_entry:
        return render_template("restaurant_search_error.html")
    else:
        restaurant_name = restaurant_entry[0]["restaurant_name"]
        restaurant_entry1 = db.execute("SELECT address FROM restaurants WHERE restaurant_name = :name", name=request.form.get("restaurant_name"))
        address = restaurant_entry1[0]["address"]
        restaurant_entry2 = db.execute("SELECT phone_number FROM restaurants WHERE restaurant_name = :name", name=request.form.get("restaurant_name"))
        phone_number = restaurant_entry2[0]["phone_number"]
        restaurant_entry3 = db.execute("SELECT type_of_food FROM restaurants WHERE restaurant_name = :name", name=request.form.get("restaurant_name"))
        type_of_food = restaurant_entry3[0]["type_of_food"]
        restaurant_entry4 = db.execute("SELECT restaurant_vibe FROM restaurants WHERE restaurant_name = :name", name=request.form.get("restaurant_name"))
        restaurant_vibe = restaurant_entry4[0]["restaurant_vibe"]
        restaurant_entry5 = db.execute("SELECT on_snackpass FROM restaurants WHERE restaurant_name = :name", name=request.form.get("restaurant_name"))
        on_snackpass = restaurant_entry5[0]["on_snackpass"]
    
    return render_template("restaurant_result.html", name=restaurant_name, address=address, phone_number=phone_number, type_of_food=type_of_food, restaurant_vibe=restaurant_vibe, on_snackpass=on_snackpass)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""
    
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("username_error.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("password_error.html")

        # Query database for username
        rows = db.execute("SELECT * FROM members WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return render_template("login_error.html")

        # Remember which user has logged in
        session["member_id"] = rows[0]["member_id"]

        # Redirect user to main home page for logged-in members
        return redirect("/main")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")