"""Food folio models"""
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    """Users model"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    first_name = db.Column(db.Text, nullable=False, unique=True)
    last_name = db.Column(db.Text)
    email = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    pfp = db.Column(db.Text)
    
    favorites = db.relationship('Favorite')
    
    @classmethod
    def signup(cls, email, first_name, last_name, password):
        """create user instance and save to db, with hashed password. Returns user"""
        
        h = bcrypt.generate_password_hash(password) #gen. bytestring
        hash_utf8 = h.decode("utf8") #save as a regular string
        
        user = User(first_name=first_name, last_name=last_name, email=email, password=hash_utf8)
        
        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, email, password):
        """checks if email exists and password is valid.
        Returns user if found, else returns False"""
        
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False
        
    def serialize(self):
        """serialize self into a dict"""
        
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "pfp": self.pfp
        }
        
class Favorite(db.Model):
    """Favorites model"""
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True)
    recipe_id = db.Column(db.Integer, primary_key=True)