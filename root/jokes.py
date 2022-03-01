import functools


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from db import get_db

bp = Blueprint('jokes', __name__, url_prefix='/jokes')

def fetcher():
    url = 'https://v2.jokeapi.dev/joke/Any'
    response = urllib.request.urlopen(url)
    data = response.read()
    joke_data = json.loads(data)
    print(joke_data)
    return joke_data

def save_joke(joke):
    db = get_db()
    false = None

    if joke['type'] == 'twopart':
        joke['joke'] = joke['setup'] + '\n' + joke['delivery']

    if joke['safe'] == 'false':
        safe = 0
    else:
        safe = 1

    if joke['error'] is None:
        db.execute(
            "INSERT INTO joke (category, joke, flags) VALUE (?,?,?)", 
            (joke['category'], joke['joke'], safe),
        )
        db.commit()

@bp.route('get_jokes')
def create_joke():
    with app.app_context():
        joke = fetcher()
        save_joke(joke)
    return joke