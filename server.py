#! /usr/bin/env python2.7

'''
The webserver for running the application.
All routes, session, cookies, user logins are defined here.
Runs on port 8080 by default.
Set debug=True inside app.run() for debugging.
'''


import os
import time
from datetime import datetime, timedelta

import redis
from flask.ext.seasurf import SeaSurf
from flask import (Flask, render_template, url_for, request, redirect, jsonify,
                   session, send_from_directory)
from flask.ext.login import (LoginManager, current_user, login_user,
                             logout_user, login_required, UserMixin)


from utils import (user_exists, register_user, validate_user,
                   get_level, update_level, awesome_sort, extended_strip,
                   get_url, get_level_data, get_rev_level, admin)

# Flask stuff: Application name, configuration, secrets, logins, CSRF, etc.
app = Flask(__name__)
app.secret_key = "it's-peanut-butter-jelly-time"
csrf = SeaSurf(app)

# Set the time-zone.
os.environ['TZ'] = 'Asia/Kolkata'
time.tzset()


# Authenticated users.
class User(UserMixin):
    '''
    Class for maintaining the state of the logged users; integrated with
    flask-login for user and session management.
    '''
    def __init__(self, username):
        self.id = username

# flask-login stuff.
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = 'strong'


# Callback function for user_loader.
@login_manager.user_loader
def load_user(username):
    '''
    Callback method for login_manager.
    '''
    present = user_exists(database, username)
    if not present:
        return None
    return User(username)


# Redis stuff.
database = redis.StrictRedis(host='localhost', port=6379, db=0)


# Configure the session cookie expiration.
@app.before_request
def make_session_permanent():
    '''
    Session lifetime.
    '''
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=12)


'''
View functions for /, /login, /register, /login, /google, /leaderboard,
                   /jigsaw-sadistic-glory.
'''


@app.route('/')
def home():
    '''
    The homepage.
    '''
    now = datetime.now()
    launch = datetime(2016, 3, 28, 19, 30, 0)
    begin = now >= launch
    return render_template('home.html', begin=begin)


@csrf.include
@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    Handle user registrations.
    '''
    username_gotcha = 'The username <b>{0}</b> is taken!'.format
    password_gotcha = "The passwords you entered don't match."

    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        confirm = request.form.get('confirm').strip()
        phone = request.form.get('phone-number').strip()

        if user_exists(database, username):
            error = username_gotcha(username)
            return render_template('register.html', error=error, thanks=False)
        elif password != confirm:
            error = password_gotcha
            return render_template('register.html', error=error, thanks=False)

        else:
            register_user(database, username, password, phone)
            return render_template('register.html', error=None, thanks=True)

    return render_template('register.html', error=None, thanks=False)


@csrf.include
@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    Handle user logins.
    '''
    now = datetime.now()
    launch = datetime(2016, 3, 27, 19, 30, 0)
    begin = now >= launch

    if begin is False:
        return redirect('/')

    if request.method == "POST":
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()

        if validate_user(database, username, password):
            auth_user = User(username)
            login_user(auth_user)
            user_level = get_level(database, current_user.id)
            return redirect(get_url(database, user_level))

        else:
            return render_template('login.html', force=False, error=True)
    else:
        if current_user.is_authenticated:
            user_level = get_level(database, current_user.id)
            resume = get_url(database, user_level)
            return render_template('login.html', force=True,
                                   username=current_user.id, error=False,
                                   resume=resume)

        return render_template('login.html', force=False, error=None)


@csrf.include
@login_required
@app.route('/google', methods=['POST'])
def google():
    '''
    Build the query URL for Google Search.
    '''
    query = request.form.get('google-query')
    google_url = "https://google.com/search?q={0}".format(query)
    return redirect(google_url)


@login_required
@app.route('/logout')
def logout():
    '''
    Log the user out of the application.
    '''
    logout_user()
    return redirect('/')


@login_required
@app.route('/leaderboard')
def leaderboard():
    '''
    Return the sorted array for the current leaderboard.
    '''

    mappings = database.hgetall('users')
    ordered = awesome_sort(mappings)

    return jsonify({'leaderboard': ordered})


@login_required
@app.route('/rules')
def rules():
    '''
    Rules of the game.
    '''
    return render_template('rules.html')


@login_required
@app.route('/youshallnotpass')
def deadend():
    '''
    The end.
    '''
    return render_template('deadend.html')


@login_required
@app.route('/extolment')
def done():
    '''
    The end.
    '''
    return render_template('finish.html', username=current_user.id)


@app.route('/sudo')
def sudo():
    '''
    Administrator access.
    '''
    password = request.args.get('password')
    if password is not None and password == 'xyzzyspoon!':
        return jsonify(admin(database))

    else:
        return jsonify({}), 403

@csrf.include
@app.route('/question/<path:path>', methods=['GET', 'POST'])
@login_required
def question(path):
    '''
    View function for the question.
    '''
    level = get_rev_level(database, ''.join(['/', path]))

    # For seving morse.mp3
    if request.path == '/question/ugb/morse.mp3':
        return send_from_directory('static', 'media/morse.mp3')

    # Check if it is a valid path.
    if level is None:
        return redirect('/404')

    username = current_user.id
    user_level = get_level(database, username)
    user_url = get_url(database, user_level)
    data = get_level_data(database, level)
    answers = data['answers']
    data.pop('answers')

    if user_level == 26:
        next_url = '/extolment'
    else:
        next_url = get_url(database, level + 1)

    if data['is_image']:
        data['media_url'] = url_for('static', filename=data['media_url'])

    # Check if the user has skipped levels.
    if request.method == 'GET':
        if user_level != level:
            if level in [2] and (user_level) + 1 == level:
                update_level(database, current_user.id, level)
                return redirect(next_url)

            if user_level < level:
                return redirect(user_url)

            return render_template('question.html', username=username,
                                   **data)
        else:
            return render_template('question.html', username=username, **data)

    else:
        answer = request.form.get('answer').lower().strip()
        sanitized = extended_strip(answer)
        # Special cases.
        if level in [16, 17, 19]:
            return redirect('/youshallnotpass')

        if sanitized in answers:
            if level in [13, 14, 15, 18, 19]:
                if level == 13 and sanitized == 'batman':
                    if user_level >= 13 and user_level <= 19:
                        update_level(database, current_user.id, 14)
                    return redirect(get_url(database, 14))

                if level == 13 and sanitized == 'superman':
                    if user_level >= 13 and user_level <= 19:
                        update_level(database, current_user.id, 15)
                    return redirect(get_url(database, 15))

                if level == 14 and sanitized == 'upstairs':
                    if user_level >= 13 and user_level <= 19:
                        update_level(database, current_user.id, 16)
                    return redirect(get_url(database, 16))

                if level == 14 and sanitized == 'downstairs':
                    if user_level >= 13 and user_level <= 19:
                        update_level(database, current_user.id, 17)
                    return redirect(get_url(database, 17))

                if level == 15 and sanitized == 'a':
                    print('a')
                    if user_level >= 13 and user_level <= 19:
                        update_level(database, current_user.id, 18)
                    return redirect(get_url(database, 18))

                if level == 15 and sanitized == 'b':
                    print('b')
                    if user_level >= 13 and user_level <= 19:
                        update_level(database, current_user.id, 19)
                    return redirect(get_url(database, 19))

                if level == 18:
                    if user_level == level:
                        update_level(database, current_user.id, 20)
                    return redirect(get_url(database, 20))
            else:
                if user_level == level:
                    update_level(database, current_user.id, level + 1)
                return redirect(next_url)

        else:
            if level == 18:
                return redirect('/youshallnotpass')

            return render_template('question.html', username=username, **data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
