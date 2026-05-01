import pytest

from app import create_app
from app.db import db


def pytest_sessionfinish(session, exitstatus):
    if exitstatus == pytest.ExitCode.NO_TESTS_COLLECTED:
        session.exitstatus = pytest.ExitCode.OK


@pytest.fixture()
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "UPLOAD_DIR": "/tmp/cognitive-ai-learning-platform-test-uploads",
    })
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app


@pytest.fixture()
def client(app):
    return app.test_client()
