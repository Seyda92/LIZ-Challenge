import os
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, flash
import atexit
import urllib.request, json
from .db import init_app, get_db

def create_app(test_config=None):
    """
    create and configure the app and creates the different pages
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    
    @app.route('/')
    def home():
        """
        very simple home page with just 1 button to get to the get_jokes page
        """
        return render_template('base.html')

    @app.route('/get_jokes')
    def get_jokes():
        """
        simple page which fetches a joke and saves it to the db
        """
        with app.app_context():
            joke = fetcher()
            error = save_joke(joke)
            #if error is not None:
            #    flash(error)
        return joke

    """
    the scheduler calls in an interval of 60 seconds the get_jokes funktion
    """
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=get_jokes, trigger="interval", seconds=60)
    scheduler.start()

    atexit.register(lambda: scheduler.shutdown())

    init_app(app)

    return app


def fetcher():
    """
    this function fetches a joke from the jokeapi and returns it
    """
    url = 'https://v2.jokeapi.dev/joke/Any'
    response = urllib.request.urlopen(url)
    data = response.read()
    joke_data = json.loads(data)
    return joke_data

def save_joke(joke):
    """
    This function checks whether the joke is a twopart joke and if so converts it to a single part joke
    Then it checks if the joke is safe and converts the boolean to 0 or 1 
    Lastly it checks if the joke is already in the db, in which case an error is returned. 
    Otherwise the joke is saved into the database
    """
    db = get_db()
    error = None
    if joke['type'] == 'twopart':
        joke['joke'] = joke['setup'] + '\n' + joke['delivery']

    if joke['safe'] == 'False':
        safe = 0
    else:
        safe = 1

    if joke['error'] is False:
        try:
            db.execute(
                "INSERT INTO jokes (joke_id, category, joke, flags) VALUES (?, ?, ?, ?)", 
                (joke['id'], joke['category'], joke['joke'], safe),
            )
            db.commit()
        except db.IntegrityError:
            error = f"joke with id: {joke['id']} already exists"

    return error

