from flask import Flask, render_template, redirect, url_for
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

    from . import cli, db, filters
    cli.init_app(app)
    db.init_app(app)
    filters.init_app(app)

    from . import auth, students, payments, groups
    app.register_blueprint(auth.bp)
    app.register_blueprint(groups.bp)
    app.register_blueprint(payments.bp)
    app.register_blueprint(students.bp)

    @app.route('/')
    def root():
        return redirect(url_for('students.index'))

    @app.route('/null')
    def null():
        return ''

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('403.html'), 404

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app
