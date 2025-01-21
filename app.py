from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from login_utils import login_required 
import re 

app = Flask(__name__)

app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Validate username uniqueness
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists! Please choose another.', 'danger')
            return redirect("/")

        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            flash('Invalid email address! Please enter a valid email.', 'danger')
            return redirect("/")

        # Check if email is unique
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('An account with this email already exists!', 'danger')
            return redirect("/")
        
        # Hash password and save user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect("/")

    return render_template("register.html")

@app.route('/login', methods=['POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']

        # Authenticate user
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!', 'danger')
            return redirect("/")
    return render_template("register.html")
    
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect("/")

@app.route('/profile')
@login_required
def profile():
    user_id = session.get('user_id')
    user = User.query.get(user_id)  # Fetch user details from the database
    return render_template('profile.html', user=user)

@app.route('/dashboard')
@login_required
def dashboard():
    username = session.get('username')  # Get the logged-in user's username
    return render_template('dashboard.html', username=username)


with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)