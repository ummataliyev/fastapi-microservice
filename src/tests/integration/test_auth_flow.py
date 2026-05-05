"""End-to-end test: register → login → /me round-trip.

Demonstrates the testing pattern for HTTP endpoints that hit the database.
"""
from uuid import uuid4

from fastapi.testclient import TestClient


def test_register_login_me_round_trip(client: TestClient) -> None:
    email = f"alice-{uuid4().hex[:8]}@example.com"
    password = "hunter2-secure"

    # Register
    response = client.post(
        "/template/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert response.status_code == 201, response.text
    tokens = response.json()
    assert tokens["token_type"] == "bearer"
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    # Login (independent verification — fresh token pair)
    response = client.post(
        "/template/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    tokens = response.json()

    # Use the access token to read /me
    response = client.get(
        "/template/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["email"] == email
    assert payload["type"] == "access"
    assert "sub" in payload


def test_login_with_wrong_password_returns_401(client: TestClient) -> None:
    email = f"bob-{uuid4().hex[:8]}@example.com"
    password = "right-password"

    register = client.post(
        "/template/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert register.status_code == 201

    login = client.post(
        "/template/api/v1/auth/login",
        json={"email": email, "password": "wrong-password"},
    )
    assert login.status_code == 401
    assert login.json()["type"] == "InvalidCredentialsError"


def test_register_duplicate_email_returns_409(client: TestClient) -> None:
    email = f"carol-{uuid4().hex[:8]}@example.com"
    password = "carol-secure"

    first = client.post(
        "/template/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert first.status_code == 201

    second = client.post(
        "/template/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert second.status_code == 409
    assert second.json()["type"] == "AlreadyExistsError"
