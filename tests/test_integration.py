def test_register_success(client):
    response = client.post(
        "/api/register",
        json={"username": "newpatient", "password": "password123"},
    )
    data = response.get_json()

    assert response.status_code == 201
    assert data["message"] == "User registered successfully!"
    assert "user_id" in data


def test_register_duplicate_username(client):
    payload = {"username": "existinguser", "password": "password123"}
    client.post("/api/register", json=payload)

    response = client.post("/api/register", json=payload)
    data = response.get_json()

    assert response.status_code == 409
    assert data["error"] == "Conflict"


def test_register_validation_error(client):
    response = client.post(
        "/api/register",
        json={"username": "a", "password": "123"},
    )
    data = response.get_json()

    assert response.status_code == 400
    assert data["error"] == "Validation Error"


def test_login_success(client):
    client.post(
        "/api/register",
        json={"username": "loginpatient", "password": "password123"},
    )

    response = client.post(
        "/api/login",
        json={"username": "loginpatient", "password": "password123"},
    )
    data = response.get_json()

    assert response.status_code == 200
    assert "access_token" in data


def test_login_invalid_credentials(client):
    client.post(
        "/api/register",
        json={"username": "loginpatient", "password": "password123"},
    )

    response = client.post(
        "/api/login",
        json={"username": "loginpatient", "password": "wrongpassword"},
    )
    data = response.get_json()

    assert response.status_code == 401
    assert data["error"] == "Unauthorized"


def test_book_appointment_success(client, auth_headers):
    response = client.post(
        "/api/appointments",
        json={
            "date": "2026-06-15",
            "time": "10:00",
            "notes": "First consultation",
        },
        headers=auth_headers,
    )
    data = response.get_json()

    assert response.status_code == 201
    assert data["message"] == "Appointment booked successfully!"
    assert data["appointment"]["date"] == "2026-06-15"
    assert data["appointment"]["time"] == "10:00"
    assert data["appointment"]["patient_id"] == 1


def test_book_appointment_conflict_same_slot(client, auth_headers):
    payload = {"date": "2026-06-15", "time": "11:00", "notes": "Dental check"}
    client.post("/api/appointments", json=payload, headers=auth_headers)

    response = client.post("/api/appointments", json=payload, headers=auth_headers)
    data = response.get_json()

    assert response.status_code == 409
    assert data["error"] == "Conflict"


def test_book_appointment_invalid_format(client, auth_headers):
    response = client.post(
        "/api/appointments",
        json={"date": "15/06/2026", "time": "11:00"},
        headers=auth_headers,
    )
    data = response.get_json()

    assert response.status_code == 400
    assert data["error"] == "Validation Error"


def test_book_appointment_missing_token(client):
    response = client.post(
        "/api/appointments",
        json={"date": "2026-06-15", "time": "12:00"},
    )
    data = response.get_json()

    assert response.status_code == 401
    assert data["error"] == "Authorization Required"


def test_get_my_appointments_isolated_per_user(client, auth_headers):
    client.post(
        "/api/appointments",
        json={"date": "2026-06-20", "time": "09:30", "notes": "Blood test"},
        headers=auth_headers,
    )

    client.post(
        "/api/register",
        json={"username": "patient2", "password": "password123"},
    )
    login_res = client.post(
        "/api/login",
        json={"username": "patient2", "password": "password123"},
    )
    patient2_token = login_res.get_json()["access_token"]
    patient2_headers = {"Authorization": f"Bearer {patient2_token}"}

    res_patient1 = client.get("/api/appointments", headers=auth_headers)
    res_patient2 = client.get("/api/appointments", headers=patient2_headers)

    assert res_patient1.status_code == 200
    assert res_patient1.get_json()["count"] == 1
    assert res_patient2.status_code == 200
    assert res_patient2.get_json()["count"] == 0