import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


def init_db():
    """
    Database setup
    Connects to db and creates db tables if they don't exist
    """
    conn = sqlite3.connect('data/podcasts.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


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
            conn = sqlite3.connect('data/podcasts.db')
            c = conn.cursor()
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
            conn.commit()
            conn.close()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
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

        conn = sqlite3.connect('data/podcasts.db')
        c = conn.cursor()
        c.execute('SELECT password FROM users WHERE username = ?', (username,))
        result = c.fetchone()
        conn.close()

        if result and check_password_hash(result[0], password):
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
    init_db()
    app.run(debug=True)