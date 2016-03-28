#! /usr/bin/env python2.7

'''
Helper modules for the web-app.
'''

import re
import time
import uuid
import pickle
import string
import hashlib


def awesome_sort(mappings):
    '''
    Sort based on multiple constraints.
    '''
    to_sort = []
    for mapping in mappings.values():
        mapping = pickle.loads(mapping)
        to_sort.append([mapping['username'], mapping['timestamp'],
                        mapping['level']])
    ordered = sorted(to_sort, key=lambda mapping: (mapping[2], -mapping[1]),
                     reverse=True)
    return ordered


def extended_strip(text):
    '''
    Extended strip() method to remove non-standard
    ASCII characters and punctuations.
    '''
    raw = ''.join(token for token in text.strip() if 0 < ord(token) < 128)
    extra = ''.join(token for token in raw if token not in string.punctuation)
    stripped = re.sub(r'\s+', ' ', extra)
    return stripped


def user_exists(database, username):
    '''
    Get all the users in the database.
    '''
    return database.hexists('users', username)


def generate_password_hash(password, _salt=None):
    '''
    Generate the SHA1 hash with salt for the password.
    '''
    salt = uuid.uuid4().hex if _salt is None else _salt
    hashed_password = hashlib.sha1(password + salt).hexdigest()
    return salt, hashed_password


def validate_user(database, username, password):
    '''
    Password check before login.
    Everything is of type: str.
    '''
    if user_exists(database, username):
        data = pickle.loads(database.hget('users', username))
        salt, stored = data['salt'], data['password']
        _, hashed = generate_password_hash(password, salt)
        return hashed == stored
    return False


def register_user(database, username, password, phone):
    '''
    Register the user.
    The level and timestamp variables are stored as type: int.
    Hashmap: users.
    '''
    salt, hashed = generate_password_hash(password)
    level = 1
    timestamp = int(time.time())
    payload = {
        'username': username,
        'password': hashed,
        'phone-number': phone,
        'timestamp': timestamp,
        'level': level,
        'salt': salt
    }

    database.hset('users', username, pickle.dumps(payload))


def get_level(database, username):
    '''
    Get the current level of the user.
    The level is returned as type: int.
    Hashmap: users.
    '''
    return pickle.loads(database.hget('users', username))['level']


def update_level(database, username, level):
    '''
    Update the current level with the timestamp for the user.
    '''
    data = pickle.loads(database.hget('users', username))
    data['timestamp'], data['level'] = int(time.time()), level
    database.hset('users', username, pickle.dumps(data))


def get_url(database, level):
    '''
    Get the URL for a level.
    The level is referenced as type: str.
    Hashmap: urls.
    '''
    if level >= 27:
        return '/extolment'

    url = str(database.hget('urls', str(level)))
    return ''.join(['/question', url])


def get_rev_level(database, url):
    '''
    Get the level for a given URL.
    '''
    level = database.hget('rev-urls', url)
    return int(level) if level is not None else None


def get_level_data(database, level):
    '''
    Get the data for each level.
    The level is referenced as type: str.
    Hashmap: levels.
    '''
    raw = database.hget('levels', str(level))
    level_data = pickle.loads(raw)
    level_data['level'] = str(level_data['level']).zfill(2)
    return level_data


def admin(database):
    '''
    Admin access to user details.
    '''
    response = {'users': []}
    users = database.hgetall('users')
    if users is not None:
        for user in users.values():
            data = pickle.loads(user)
            condensed = {
                'username': data['username'],
                'contact': data['phone-number'],
                'level': data['level'],
                'timestamp': data['timestamp']
            }
            response['users'].append(condensed)
    return response
