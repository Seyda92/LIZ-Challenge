import os
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask import render_template
import atexit
import urllib.request, json
from db import get_db

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass



    # a simple page that says hello
    @app.route('/')
    def home():
        return render_template('base.html')

    @app.route('/get_jokes')
    def get_jokes():
        with app.app_context():
            joke = fetcher()
            save_joke(joke)
        return joke

    @app.route('/view_jokes')
    def view_jokes():
        return render_template('view_jokes.html')

    scheduler = BackgroundScheduler()
    scheduler.add_job(func=get_jokes, trigger="interval", seconds=60)
    scheduler.start()

    atexit.register(lambda: scheduler.shutdown())

    import db
    db.init_app(app)

    return app


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

