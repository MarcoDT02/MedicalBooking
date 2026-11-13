import pytest
from marshmallow import ValidationError
from models import User
from schemas import AppointmentSchema, UserLoginSchema, UserRegisterSchema


def test_password_hashing():
    user = User(username="mario_rossi")
    user.set_password("mypassword123")

    assert user.password_hash != "mypassword123"
    assert user.check_password("mypassword123") is True
    assert user.check_password("wrongpassword") is False


def test_user_register_schema_valid():
    schema = UserRegisterSchema()
    data = schema.load({"username": "patient_one", "password": "password123"})

    assert data["username"] == "patient_one"
    assert data["password"] == "password123"


def test_user_register_schema_invalid():
    schema = UserRegisterSchema()

    with pytest.raises(ValidationError) as exc_info:
        schema.load({"username": "ab", "password": "123"})

    errors = exc_info.value.messages
    assert "username" in errors
    assert "password" in errors


def test_user_login_schema_missing_fields():
    schema = UserLoginSchema()

    with pytest.raises(ValidationError) as exc_info:
        schema.load({})

    errors = exc_info.value.messages
    assert "username" in errors
    assert "password" in errors


def test_appointment_schema_valid():
    schema = AppointmentSchema()
    data = schema.load({
        "date": "2026-05-20",
        "time": "14:30",
        "notes": "Routine checkup",
    })

    assert data["date"] == "2026-05-20"
    assert data["time"] == "14:30"
    assert data["notes"] == "Routine checkup"


def test_appointment_schema_invalid_date_and_time():
    schema = AppointmentSchema()

    with pytest.raises(ValidationError) as exc_info:
        schema.load({
            "date": "20-05-2026",
            "time": "2:30PM",
            "notes": "x" * 205,
        })

    errors = exc_info.value.messages
    assert "date" in errors
    assert "time" in errors
    assert "notes" in errors