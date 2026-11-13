import pytest
from app import create_app
from models import db


@pytest.fixture()
def app():
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret-key-at-least-32-bytes-long",
    }
    app = create_app(test_config)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth_headers(client):
    client.post(
        "/api/register",
        json={"username": "patient1", "password": "password123"},
    )
    response = client.post(
        "/api/login",
        json={"username": "patient1", "password": "password123"},
    )
    token = response.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}