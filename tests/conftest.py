
import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

# Import models so SQLModel knows about all database tables.
from app.models.internship import (
    Student,
    Company,
    InternshipListing,
    InternshipApplication,
    InternshipMatch,
)
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies.session import get_session
from app.dependencies.auth import get_current_user
from app.models.user import User


@pytest.fixture
def test_engine():
    """Create a separate in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(engine)

    yield engine

    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    """Provide a database session for each test."""
    with Session(test_engine) as session:
        yield session


@pytest.fixture
def test_user(db_session):
    """Create a test user in the in-memory database."""
    user = User(
        username="teststudent",
        email="student@example.com",
        password="testpassword",
        role="student",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def client(db_session, test_user, monkeypatch):
    """Create a test client using the in-memory database and test user."""

    # Prevent test requests from triggering normal database recovery.
    monkeypatch.setattr(
        "app.database.recover_if_uninitialized",
        lambda exc: False,
    )

    def override_get_session():
        yield db_session

    def override_get_current_user():
        return test_user

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user] = override_get_current_user

    # Do not use a "with" statement; that would trigger the normal app lifespan.
    test_client = TestClient(app)

    yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_listing(db_session):
    """Create a company and internship listing for integration tests."""
    company = Company(
        company_name="Test Company",
        contact_name="Test Contact",
        email="company@example.com",
        industry="Technology",
    )

    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)

    listing = InternshipListing(
        company_id=company.company_id,
        title="Python Developer Intern",
        description="A test internship for Python developers.",
        skills="Python, SQL",
        requirements="Basic programming knowledge",
        location="Trinidad and Tobago",
        duration="3 months",
        number_of_positions=2,
    )

    db_session.add(listing)
    db_session.commit()
    db_session.refresh(listing)

    return listing