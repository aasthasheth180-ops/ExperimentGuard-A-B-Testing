import os
from uuid import uuid4

import jwt
from sqlalchemy import select

from src.experimentguard.auth import verify_password
from src.experimentguard.models import UserRecord


def test_register_creates_user_in_database(auth_client, db_session):
    # Generate a unique email to avoid collisions between test runs.
    email = f"registration_{uuid4().hex}@example.com"
    password = "SecureTestPassword123!"

    # Send a real registration request to FastAPI.
    response = auth_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    # A successful registration should return HTTP 201.
    assert response.status_code == 201, response.text

    data = response.json()

    assert data["email"] == email
    assert isinstance(data["id"], int)

    # Check that the user was actually stored in PostgreSQL.
    saved_user = db_session.scalar(
        select(UserRecord).where(UserRecord.email == email)
    )

    assert saved_user is not None
    assert saved_user.id == data["id"]

    # Passwords must never be stored as plaintext.
    assert saved_user.password_hash != password

    # The stored hash must verify against the original password.
    assert verify_password(password, saved_user.password_hash)



def test_register_rejects_duplicate_email(auth_client, db_session):
    email = f"duplicate_{uuid4().hex}@example.com"
    password = "SecureTestPassword123!"

    # First registration should succeed.
    first_response = auth_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert first_response.status_code == 201

    # Register the same email again, using different capitalization.
    second_response = auth_client.post(
        "/auth/register",
        json={
            "email": email.upper(),
            "password": password,
        },
    )

    # The API must reject the duplicate account.
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Account already exists."

    # Confirm that only one account exists.
    users = db_session.scalars(
        select(UserRecord).where(UserRecord.email == email)
    ).all()

    assert len(users) == 1



def test_login_returns_valid_jwt(auth_client, monkeypatch):
    email = f"login_{uuid4().hex}@example.com"
    password = "SecureTestPassword123!"

    # 1. Register a new user.
    register_response = auth_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert register_response.status_code == 201

    user_id = register_response.json()["id"]

    # 2. Log in using the registered credentials.
    login_response = auth_client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    data = login_response.json()

    # 3. Verify the expected token response.
    assert data["token_type"] == "bearer"
    assert isinstance(data["access_token"], str)

    # 4. Decode and validate the JWT signature.
    token_payload = jwt.decode(
    data["access_token"],
    os.environ["JWT_SECRET_KEY"],
    algorithms=["HS256"],
)

    # 5. Verify the token belongs to the correct user.
    assert token_payload["sub"] == str(user_id)

    # 6. Verify the token has timestamps.
    assert "iat" in token_payload
    assert "exp" in token_payload
    assert token_payload["exp"] > token_payload["iat"]



def test_login_rejects_invalid_credentials(auth_client):
    email = f"invalid_login_{uuid4().hex}@example.com"
    correct_password = "SecureTestPassword123!"

    # Register a real account first.
    register_response = auth_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": correct_password,
        },
    )

    assert register_response.status_code == 201

    # Case 1: Existing email, incorrect password.
    wrong_password_response = auth_client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "WrongPassword123!",
        },
    )

    assert wrong_password_response.status_code == 401
    assert wrong_password_response.json()["detail"] == (
        "Invalid email or password."
    )

    # Case 2: Email address that does not exist.
    unknown_email_response = auth_client.post(
        "/auth/login",
        json={
            "email": f"unknown_{uuid4().hex}@example.com",
            "password": correct_password,
        },
    )

    assert unknown_email_response.status_code == 401
    assert unknown_email_response.json()["detail"] == (
        "Invalid email or password."
    )

    # Neither response should return an access token.
    assert "access_token" not in wrong_password_response.json()
    assert "access_token" not in unknown_email_response.json()




def test_auth_me_returns_current_user(auth_client):
    email = f"me_{uuid4().hex}@example.com"
    password = "SecureTestPassword123!"

    register_response = auth_client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201

    login_response = auth_client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = auth_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": register_response.json()["id"],
        "email": email,
    }


def test_auth_me_rejects_missing_invalid_and_expired_tokens(
    auth_client, monkeypatch
):
    from datetime import datetime, timedelta, timezone

    import jwt

    # No token.
    missing = auth_client.get("/auth/me")
    assert missing.status_code == 401

    # Invalid token.
    invalid = auth_client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert invalid.status_code == 401

    # Expired but correctly signed token.
    expired_token = jwt.encode(
        {
            "sub": "999999",
            "iat": datetime.now(timezone.utc) - timedelta(hours=2),
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        },
        os.environ["JWT_SECRET_KEY"],
        algorithm="HS256",
    )

    expired = auth_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert expired.status_code == 401


def test_inactive_user_cannot_login_or_access_me(
    auth_client, db_session
):
    email = f"inactive_{uuid4().hex}@example.com"
    password = "SecureTestPassword123!"

    register_response = auth_client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 201

    login_response = auth_client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    user_id = register_response.json()["id"]

    # Disable the account.
    user = db_session.get(UserRecord, user_id)
    assert user is not None
    user.is_active = False
    db_session.commit()

    # Existing JWT must no longer grant access.
    me_response = auth_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 401

    # Disabled account must not be allowed to log in again.
    second_login = auth_client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert second_login.status_code == 401


def create_authenticated_user(auth_client):
    """Register a test user, log in, and return their credentials."""
    email = f"account_{uuid4().hex}@example.com"
    password = "SecureTestPassword123!"

    registration = auth_client.post(
        "/auth/register",
        json={"email": email, "password": password},
    )
    assert registration.status_code == 201, registration.text

    login = auth_client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200, login.text

    token = login.json()["access_token"]

    return {
        "id": registration.json()["id"],
        "email": email,
        "password": password,
        "headers": {"Authorization": f"Bearer {token}"},
    }

def test_profile_update_success(auth_client, db_session):
    user = create_authenticated_user(auth_client)
    new_email = f"updated_{uuid4().hex}@example.com"

    response = auth_client.patch(
        "/auth/me",
        headers=user["headers"],
        json={
            "email": new_email.upper(),
            "current_password": user["password"],
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["email"] == new_email

    saved = db_session.get(UserRecord, user["id"])
    assert saved.email == new_email

    me = auth_client.get("/auth/me", headers=user["headers"])
    assert me.status_code == 200
    assert me.json()["email"] == new_email


def test_profile_update_wrong_password(auth_client):
    user = create_authenticated_user(auth_client)

    response = auth_client.patch(
        "/auth/me",
        headers=user["headers"],
        json={
            "email": f"updated_{uuid4().hex}@example.com",
            "current_password": "IncorrectPassword123!",
        },
    )

    assert response.status_code == 401

    me = auth_client.get("/auth/me", headers=user["headers"])
    assert me.json()["email"] == user["email"]


def test_profile_update_duplicate_email(auth_client):
    first = create_authenticated_user(auth_client)
    second = create_authenticated_user(auth_client)

    response = auth_client.patch(
        "/auth/me",
        headers=first["headers"],
        json={
            "email": second["email"],
            "current_password": first["password"],
        },
    )

    assert response.status_code == 409


def test_profile_update_invalid_email(auth_client):
    user = create_authenticated_user(auth_client)

    response = auth_client.patch(
        "/auth/me",
        headers=user["headers"],
        json={
            "email": "invalid-email",
            "current_password": user["password"],
        },
    )

    assert response.status_code == 422


def test_profile_update_requires_authentication(auth_client):
    response = auth_client.patch(
        "/auth/me",
        json={
            "email": "someone@example.com",
            "current_password": "SecureTestPassword123!",
        },
    )

    assert response.status_code == 401

def test_password_change_success(auth_client, db_session):
    user = create_authenticated_user(auth_client)
    new_password = "UpdatedSecurePassword456!"

    response = auth_client.patch(
        "/auth/me/password",
        headers=user["headers"],
        json={
            "current_password": user["password"],
            "new_password": new_password,
        },
    )

    assert response.status_code == 200, response.text

    saved = db_session.get(UserRecord, user["id"])
    assert verify_password(new_password, saved.password_hash)
    assert not verify_password(user["password"], saved.password_hash)


def test_password_change_wrong_current_password(auth_client):
    user = create_authenticated_user(auth_client)

    response = auth_client.patch(
        "/auth/me/password",
        headers=user["headers"],
        json={
            "current_password": "WrongPassword123!",
            "new_password": "UpdatedSecurePassword456!",
        },
    )

    assert response.status_code == 401


def test_password_change_rejects_same_password(auth_client):
    user = create_authenticated_user(auth_client)

    response = auth_client.patch(
        "/auth/me/password",
        headers=user["headers"],
        json={
            "current_password": user["password"],
            "new_password": user["password"],
        },
    )

    assert response.status_code == 400


def test_password_change_rejects_short_password(auth_client):
    user = create_authenticated_user(auth_client)

    response = auth_client.patch(
        "/auth/me/password",
        headers=user["headers"],
        json={
            "current_password": user["password"],
            "new_password": "short",
        },
    )

    assert response.status_code == 422


def test_password_change_requires_authentication(auth_client):
    response = auth_client.patch(
        "/auth/me/password",
        json={
            "current_password": "SecureTestPassword123!",
            "new_password": "UpdatedSecurePassword456!",
        },
    )

    assert response.status_code == 401


def test_password_change_updates_login_credentials(auth_client):
    user = create_authenticated_user(auth_client)
    new_password = "UpdatedSecurePassword456!"

    update = auth_client.patch(
        "/auth/me/password",
        headers=user["headers"],
        json={
            "current_password": user["password"],
            "new_password": new_password,
        },
    )
    assert update.status_code == 200

    old_login = auth_client.post(
        "/auth/login",
        json={
            "email": user["email"],
            "password": user["password"],
        },
    )
    assert old_login.status_code == 401

    new_login = auth_client.post(
        "/auth/login",
        json={
            "email": user["email"],
            "password": new_password,
        },
    )
    assert new_login.status_code == 200
    assert "access_token" in new_login.json()