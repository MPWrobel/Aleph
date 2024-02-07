import pytest
import tempfile

from aleph import make_app
from aleph.db import get_db
from pathlib import Path


@pytest.fixture
def app():
    db_file = tempfile.NamedTemporaryFile()
    app = make_app(
        SECRET_KEY='dev',
        TESTING=True,
        DATABASE=db_file.name
    )

    with app.app_context():
        db = get_db()
        db.executefile('aleph/schema.sql')
        for sql_file in Path('tests/').glob('*.sql'):
            db.executefile(sql_file)

    yield app

    db_file.close()


@pytest.fixture
def client(app):
    return app.test_client()
