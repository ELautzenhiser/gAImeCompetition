import os

from flask import Flask, render_template

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        # We should load a database here.  Which database will we use?
    )

    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import db
    db.init_app(app)

    @app.route('/about')
    def about():
        return render_template('about.html')

    from . import compete
    app.register_blueprint(compete.bp)

    from . import upload
    @app.route('/upload', methods=['GET', 'POST'])
    def upload_page():
        return upload.upload_file(app)

    return app