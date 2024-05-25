from flask import Flask, render_template, redirect, session, flash, g, request
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import requests

from models import db, connect_db, User, Favorite
from secrets_1 import api_key, app_key
from forms import SignUp, LoginForm, EditProfile

app = Flask(__name__)
app.app_context().push()

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///food-folio"
app.config["SQLLCHEMY_TRACK_MODIFICATIONS"] = True
app.config['SECRET_KEY'] = app_key
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
toolbar = DebugToolbarExtension(app)

connect_db(app)

CURR_USER = 'current_user'
BASE_URL = 'https://api.spoonacular.com/recipes'

@app.before_request
def global_user():
    """Add current user to Flask global if logged in, else none"""
    
    if CURR_USER in session:
        g.user = User.query.get(session[CURR_USER])
    else:
        g.user = None
        
# ----------------------- HOME ROUTE  -----------------------
@app.route('/')
def home_page():
    """Render home page template"""
    # get 4 random recipes from API
    resp = requests.get(f"{BASE_URL}/random", params={"apiKey": api_key, "number": 4})
    data = resp.json()
    
    return render_template('index.html', data=data)

# ----------------------- GENERAL ROUTES  -----------------------
@app.route('/signup', methods=["GET", "POST"])
def user_singup():
    """Show account details of user"""
    form = SignUp()
    
    if form.validate_on_submit():
        try:
            new_user = User.signup(
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                password=form.password.data
            )
            db.session.commit()
            
            session[CURR_USER] = new_user.id
            return redirect('/')
        except: 
            return redirect('/signup')
            
    return render_template('users/signup.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    """Login User"""
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.authenticate(
            email=form.email.data, 
            password=form.password.data
            )
        
        if user:
            session[CURR_USER] = user.id
            return redirect('/')
        else:
            form.password.errors.append('email or password is incorrect')
            
    return render_template('users/login.html', form=form)

@app.route('/logout', methods=["POST"])
def logout():
    """Logout current user"""
    
    session.pop(CURR_USER)
    return redirect('/')

# ----------------------- USER ROUTES -----------------------
@app.route('/users/<int:user_id>', methods=["GET", "POST"])
def show_user(user_id):
    """Show user profile and list of their favorite recipes"""
    
    if not g.user:
        flash("You don't have permission to do that", 'danger')
        return redirect('/')
    
    user = User.query.get(user_id)
    
    return render_template('users/profile.html', user=user)

@app.route('/users/<int:user_id>/edit', methods=["GET", "POST"])
def edit_user(user_id):
    """Show form for editing user details. Only accessible by logged-in user"""
    
    if not g.user:
        flash("You don't have permission to do that", 'danger')
        return redirect('/')
    
    user = User.query.get_or_404(user_id)
    form = EditProfile(obj=user)
    
    if user.id != g.user.id:
        flash("You don't have permission to do that", 'danger')
        return redirect('/')
    
    if form.validate_on_submit:
        if User.authenticate(user.email, user.password):
            user.email = form.email.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.pfp = form.pfp.data
            
            db.session.commit()
            
    return render_template('users/edit_profile.html', user=user, form=form)

@app.route('/recipe/<int:message_id>/like', methods=['POST'])
def add_favorite(recipe_id):
    """Toggle a favorited recipe for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    new_fav = Favorite(user_id=g.user.id, recipe_id=recipe_id)
    user_favs = g.user.favorites

    if new_fav in user_favs:
        g.user.favorites = [fav for fav in user_favs if fav != new_fav]
    else:
        g.user.favorites.append(new_fav)
    
    db.session.add(new_fav)
    db.session.commit()

# ----------------------- RECIPE ROUTES -----------------------
@app.route('/recipes/<int:recipe_id>')
def show_recipe(recipe_id):
    """Show details of a single recipe"""
    
    res = requests.get(f"{BASE_URL}/{recipe_id}/information", params={"apiKey": api_key})
    recipe = res.json()
    
    return render_template('recipes/recipe_page.html', recipe=recipe)

@app.route('/search')
def search_recipes():
    """Search recipes based on search query"""
    
    search = request.args.get('q')
    
    r = requests.get(f"{BASE_URL}/complexSearch", params={"apiKey": api_key, "query": search})
    results = r.json()
    
    return render_template('recipes/search_results.html', results=results, search=search)       