from flask import Flask, render_template
from shutil import copy
from os import environ, mkdir, path


def make_app(**test_config) -> Flask:
    app = Flask(__name__,
                instance_path=environ.get('ALEPH_INSTANCE'),
                instance_relative_config=True)

    if not path.isdir(app.instance_path):
        mkdir(app.instance_path)
        copy('default.cfg', path.join(app.instance_path, 'aleph.cfg'))

    if test_config:
        app.config.from_mapping(test_config)
    else:
        app.config.from_pyfile('aleph.cfg')

    @app.route('/')
    def root():
        return render_template('base.html')

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app
