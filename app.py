import os
from flask import Flask, flash, render_template, request, redirect, url_for, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, insert, ForeignKey, select
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
    Column('user_id', db.Integer, db.ForeignKey('user.id'),
           primary_key=True),
    Column('podcast_id', db.Integer, db.ForeignKey('podcast.id'),
           primary_key=True)
)

# SQLAlchemy Models
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)
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
    user = User.query.filter_by(username=session['username']).first()
    user_id = user.id
    stmt = select(podcasts_per_user).where(
        podcasts_per_user.c.user_id == user_id)
    podcast_ids_for_user = []
    results = db.session.execute(stmt).fetchall()
    if results:
        podcast_ids_for_user = [row[1] for row in results]
    user_podcasts_list = []
    if request.method == 'POST':
        topic = request.form['topic']
        podcast = Podcast.query.filter_by(title=topic).first()

        if podcast:
            podcast_id = podcast.id
            stmt = select(podcasts_per_user).where(
                podcasts_per_user.c.user_id == user_id)
            results = db.session.execute(stmt).fetchall()
            podcast_ids_for_user = [row[1] for row in results]
            if not podcast.id in podcast_ids_for_user:
                stmt = insert(podcasts_per_user).values(user_id=user_id,
                                                        podcast_id=podcast_id)
                db.session.execute(stmt)
                db.session.commit()
            audio_url = f"audio/{podcast.podcast_url}"
            return render_template('podcast.html', audio_file=audio_url)
        else:
           # flash(
            #    'Please Wait, the AI Magic is preparing your Podcast.\nIt will be ready in a couple of minutes')
            try:
                podcast_url = create_podcast(topic)
                new_podcast = Podcast(title=topic, podcast_url=podcast_url)
                db.session.add(new_podcast)
                db.session.commit()
                stmt = insert(podcasts_per_user).values(user_id=user_id,
                                                        podcast_id=new_podcast.id)
                db.session.execute(stmt)
                db.session.commit()
             #   session['_flashes'].clear()
                audio_url = f"audio/{podcast_url}"
                return render_template('podcast.html', audio_file=audio_url)
            except Exception as e:
                db.session.rollback()
                flash(str(e),'error')

    if request.method == 'GET':
        if podcast_ids_for_user:
            [user_podcasts_list.append(Podcast.query.filter_by(id=i).first()) for i in podcast_ids_for_user]
    return render_template('welcome.html',
                                   user_podcasts_list=user_podcasts_list)



@app.route('/previous_podcasts')
def previous_podcasts():
    user_podcasts_list = []
    if session:
        user = User.query.filter_by(username=session['username']).first()
        user_id = user.id
        stmt = select(podcasts_per_user).where(
            podcasts_per_user.c.user_id == user_id)
        podcast_ids_for_user = []
        results = db.session.execute(stmt).fetchall()
        if results:
            podcast_ids_for_user = [row[1] for row in results]
        if podcast_ids_for_user:
            [user_podcasts_list.append(Podcast.query.filter_by(id=i).first()) for i
             in podcast_ids_for_user]
    else:
        flash("Please Log in First")
    return render_template('previous_podcasts.html', user_podcasts_list=user_podcasts_list)


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


@app.route('/podcast')
def podcast():
    return render_template('podcast.html', audio_file=f"audio/{request.args.get('audio_file')}")


@app.route('/options')
def options():
    if request.method == 'POST':
        options = {
        "ai_model": request.form['ai_model'],
        "host1_name": request.form['host1_name'],
        "host2_name": request.form['host2_name'],
        "host1_voice": request.form['host1_voice'],
        "host2_voice": request.form['host1_voice'],
        "host1_mood": request.form['host1_mood'],
        "host2_mood": request.form['host1_mood']
        }
        return render_template('welcome.html', options=options)
    return render_template('options.html')


@app.route('/about')
def about():
    return render_template('about.html')


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
    app.run(host="0.0.0.0", port=5000, debug=True)