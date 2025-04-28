import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# SQLAlchemy configuration
db_path = os.path.join(os.getcwd(), "data", "podcasts.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# SQLAlchemy Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)


def init_db():
    """
    Initializes the database and creates all necessary tables.
    """
    db.create_all()


@app.route('/')
def home():
    """
    Route: Home
    Checks if user has logged in
    :return: Rendered HTML template for the home page
     or redirects to login/register page
    """
    if 'username' in session:
        return redirect(url_for('welcome'))
    return render_template('home.html')


@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    """
    Route: welcome
    Inputs the Podcast topic
    :return:
    """
    if request.method == 'POST':
        topic = request.form['topic']
        print(topic)

    return render_template('welcome.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Route: Register
    Registers a new user
    :return: Rendered HTML template for the register page
     and after registration redirects to login page
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='scrypt', salt_length=16)

        try:
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Username already exists. Please choose a different one.', 'error')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Route: Login
    :return: Rendered HTML template for the login page
     and after successful login redirects to home page
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    """
    Route: Logout
    :return: redirects to home page
    """
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)