import os
import logging
from flask import Flask


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # A default secret that should be overridden by instance config.
        SECRET_KEY='dev',
        # An SQLAlchemy URI.
        SQL_URI=os.environ.get('SCROOGE_SQL_URI', 'postgresql+psycopg2://postgres@localhost/postgres'),
    )

    # Set up logging for Waitress.
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)

    # Just a dummy value to allow importing the scrooge tasks module.
    # We don't make any requests to RapidAPI from this project.
    os.environ['SCROOGE_API_KEY'] = 'dummy'

    if test_config is None:
        # Load the instance config, if it exists, when not testing.
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in.
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    with app.app_context():
        from spectacles.db import session

    @app.teardown_appcontext
    def shutdown_session(_=None):
        session.remove()

    # Apply the blueprints to the app.
    from spectacles import stonk

    app.register_blueprint(stonk.bp)

    # Make url_for('index') == url_for('blog.index').
    app.add_url_rule('/', endpoint='index')

    return app
