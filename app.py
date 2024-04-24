from flask import Flask, render_template, redirect, session, flash, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Favorite
from secrets_1 import api_key, app_key
from forms import SignUp, LoginForm

app = Flask(__name__)
app.app_context().push()

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///food-folio"
app.config["SQLLCHEMY_TRACK_MODIFICATIONS"] = True
app.config['SECRET_KEY'] = app_key
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
toolbar = DebugToolbarExtension(app)

connect_db(app)

CURR_USER = 'current_user'

@app.before_request
def global_user():
    """Add current user to Flask global if logged in, else none"""
    
    if CURR_USER in session:
        g.user = User.query.get(session[CURR_USER])
    else:
        g.user = None
        

@app.route('/')
def home_page():
    """Render home page template"""
    return render_template('index.html')

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
            
    return render_template('signup.html', form=form)

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
            form.email.errors.append('email not found')
            
    return render_template('login.html', form=form)

@app.route('/logout', methods=["POST"])
def logout():
    """Logout current user"""
    
    session.pop(CURR_USER)
    return redirect('/')

# ----------------------- USER ROUTES -----------------------