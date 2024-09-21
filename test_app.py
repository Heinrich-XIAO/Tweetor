 # conftest.py
import pytest
import sqlite3
from flask import g
from app import app
import helpers
import os
os.environ['TESTING'] = 'true';
app.config.update(TESTING=True)


@pytest.fixture(scope='function')
def client_with_authentication():
    # Log in as an admin user
    with app.test_client() as client:
        response = client.post('/login', data=dict(handle='admin', password='admin_password'))
        assert response.status_code == 200, "Login failed"
    # Return the client for use in tests
    return app.test_client()

@pytest.fixture(scope='session')
def db_connection():

    DATABASE = ':memory:'
    
    conn = sqlite3.connect(DATABASE)
    
    # Execute database_setup.py to create tables and insert initial data
    exec(open("database_setup.py").read())
    
    yield conn
    conn.close()

@pytest.fixture(scope='function')
def client(db_connection):
    app.config['TESTING'] = True
    ctx = app.app_context()
    ctx.push()
    yield app.test_client()
    ctx.pop()
def test_submit_flit_while_logged_in(client_with_authentication):
    # Set up test data
    test_content = "test 1"
    test_meme_url = "https://media.tenor.com/image.jpg"

    # Submit a flit while logged in
    response = client_with_authentication.post(
        '/submit_flit',
        data={'content': test_content, 'meme_link': test_meme_url},
    )

    # Assert that the response is as expected
    assert response.status_code == 302  # Redirect status code
    assert response.location == url_for('home')  # Expected redirection location
