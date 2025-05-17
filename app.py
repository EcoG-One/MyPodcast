import os
from flask import Flask, flash, render_template, request, redirect, url_for, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship, registry
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from podcast import create_podcast

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# SQLAlchemy configuration
db_path = os.path.join(os.getcwd(), "data", "podcasts.db")
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{db_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

mapper_registry = registry()
mapper_registry.configure()

# Association Table
podcasts_per_user = Table(
    'podcasts_per_user', db.Model.metadata,
    Column('user_id', Integer, ForeignKey('user.id'),
           primary_key=True),
    Column('podcast_id', Integer, ForeignKey('podcast.id'),
           primary_key=True)
)

# SQLAlchemy Models
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now(),
                           nullable=False)  # Date stamp column
    updated_at = Column(db.DateTime, default=func.now(), onupdate=func.now(),
                        nullable=False)  # Auto-updating timestamp
    # Many-to-Many Relationship
    podcasts = relationship("Podcast", secondary=podcasts_per_user,
                         back_populates="users")


class Podcast(db.Model):
    __tablename__ = 'podcast'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=True, nullable=False)
    podcast_url = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=func.now(),
                           nullable=False)  # Date stamp column
    updated_at = Column(db.DateTime, default=func.now(), onupdate=func.now(),
                        nullable=False)  # Auto-updating timestamp
    # Many-to-Many Relationship
    users = relationship("User", secondary=podcasts_per_user,
                         back_populates="podcasts")


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
        # flash('Please Wait, your Podcast will be ready in a couple of minutes')
        podcast = Podcast.query.filter_by(title=topic).first()
        if podcast:
            audio_url = f"audio/{podcast.podcast_url}"
            return render_template('podcast.html', audio_file=audio_url)
        else:
            try:
                create_podcast(topic)
                podcast_url = f'{topic}.mp3'
                new_podcast = Podcast(title=topic, podcast_url=podcast_url)
                db.session.add(new_podcast)
                db.session.commit()
                audio_url = f"audio/{podcast_url}"
                return render_template('podcast.html', audio_file=audio_url)
            except Exception as e:
                db.session.rollback()
                flash(str(e),'error')

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