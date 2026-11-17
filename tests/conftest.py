import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from src.experimentguard.api import app, get_db
from src.experimentguard.auth import get_auth_db, get_current_user


load_dotenv()

TEST_DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    database="experimentguard_test_db",
)

test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
    join_transaction_mode="create_savepoint",
)

@pytest.fixture
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()

    session = TestSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()



@pytest.fixture
def api_client(db_session):
    from fastapi.testclient import TestClient

    def override_get_db():
        yield db_session

    def override_get_current_user():
        return {
            "id": 1,
            "email": "test@example.com",
            "is_active": True,
        }

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = (
        override_get_current_user
    )

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_db, None)
        app.dependency_overrides.pop(get_current_user, None)



@pytest.fixture
def auth_client(db_session, monkeypatch):
    from fastapi.testclient import TestClient

    monkeypatch.setenv(
        "JWT_SECRET_KEY",
        "experimentguard_test_secret_key_1234567890",
    )

    def override_get_auth_db():
        yield db_session

    app.dependency_overrides[get_auth_db] = override_get_auth_db

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.pop(get_auth_db, None)