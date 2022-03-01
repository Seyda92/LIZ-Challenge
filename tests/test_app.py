import sys
import time
from unittest import TestCase
import random as rnd

sys.path.append('..')
from root.app import create_app, fetcher, save_joke
from root.db import get_db


class TestApp(TestCase):

    def test_fetcher(self):
        """
        This function test the fetch function and asserts if an error in the api call occured
        """
        joke = fetcher()
        self.assertEqual(joke['error'], False)


    def test_save_joke_single(self):
        """
        This function test the the save_joke funktion for single part jokes
        """
        app = create_app({
        'TESTING': True,
        })
        joke_id = rnd.randint(1000,100000)
        joke = {
            'error': False,
            'id': joke_id,
            'category': 'test',
            'type': 'single',
            'joke': 'this is a test joke',
            'safe': 'False'
        }
        
        with app.app_context():
            error = save_joke(joke)
            db = get_db()
            db_joke = db.execute(
                'SELECT * FROM jokes WHERE joke_id = ?', (joke['id'],)        
            ).fetchone()
        self.assertEqual(joke['joke'],db_joke['joke'])


    def test_save_joke_twopart(self):
        """
        This function test the the save_joke funktion for twopart jokes
        """
        app = create_app({
        'TESTING': True,
        })
        joke_id = rnd.randint(1000,100000)
        joke = {
            'error': False,
            'id': joke_id,
            'category': 'test',
            'type': 'twopart',
            'setup': 'this is the setup',
            'delivery': 'this is the delivery',
            'safe': 'False'
        }
        
        with app.app_context():
            error = save_joke(joke)
            db = get_db()
            db_joke = db.execute(
                'SELECT * FROM jokes WHERE joke_id = ?', (joke['id'],)        
            ).fetchone()

        joke['joke'] = joke['setup'] + '\n' + joke['delivery']

        self.assertEqual(joke['joke'],db_joke['joke'])

    def test_save_joke_duplicat(self):
        """
        This function test the the save_joke funktion for a duplicate joke
        """
        app = create_app({
        'TESTING': True,
        })

        joke_id = rnd.randint(1000,100000)

        joke = {
            'error': False,
            'id': joke_id,
            'category': 'test',
            'type': 'single',
            'joke': 'this is a test joke',
            'safe': 'False'
        }
        
        with app.app_context():
            _error = save_joke(joke)
            error = save_joke(joke)

        self.assertEqual(error, f"joke with id: {joke_id} already exists")

    def test_scheduler(self):
        """
        This function test the the scheduler by checking if the latest entry 
        to the database changes after 1 minute
        """
        app = create_app({
        'TESTING': True,
        })
        with app.app_context():
            db = get_db()
            first_joke = db.execute(
                'SELECT * FROM jokes ORDER BY id DESC LIMIT 1'        
            ).fetchone()

            time.sleep(60)

            second_joke = db.execute(
                'SELECT * FROM jokes ORDER BY id DESC LIMIT 1'        
            ).fetchone()

        self.assertNotEqual(first_joke['joke'],second_joke['joke'])

