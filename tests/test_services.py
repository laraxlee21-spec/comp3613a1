
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.models.internship import Student
from app.services.internship_application import (
    InternshipApplicationService,
    StudentEmailMismatch,
    StudentProfileIncomplete,
    InternshipListingNotFound,
    InternshipListingUnavailable,
    DuplicateInternshipApplication,
)


@pytest.fixture
def service_setup():
    repository = MagicMock()
    catalog_repository = MagicMock()

    service = InternshipApplicationService(
        repository,
        catalog_repository,
    )

    return service, repository, catalog_repository


@pytest.fixture
def valid_details():
    return {
        "listing_id": 10,
        "account_email": "student@example.com",
        "full_name": "Test Student",
        "email": "student@example.com",
        "programme_of_study": "Computer Science",
        "skills": "Python, Java",
        "certifications": "Python Certificate",
        "career_interests": "Software Development",
    }


def test_rejects_different_email(service_setup, valid_details):
    service, repository, catalog = service_setup

    valid_details["email"] = "wrong@example.com"

    with pytest.raises(StudentEmailMismatch):
        service.submit_application(**valid_details)


def test_rejects_incomplete_application(service_setup, valid_details):
    service, repository, catalog = service_setup

    valid_details["skills"] = ""

    with pytest.raises(StudentProfileIncomplete):
        service.submit_application(**valid_details)


def test_rejects_nonexistent_listing(service_setup, valid_details):
    service, repository, catalog = service_setup

    catalog.get_listing.return_value = None

    with pytest.raises(InternshipListingNotFound):
        service.submit_application(**valid_details)


def test_rejects_listing_with_no_positions(
    service_setup, valid_details
):
    service, repository, catalog = service_setup

    catalog.get_listing.return_value = SimpleNamespace(
        listing_id=10,
        number_of_positions=0,
    )

    with pytest.raises(InternshipListingUnavailable):
        service.submit_application(**valid_details)


def test_rejects_duplicate_application(
    service_setup, valid_details
):
    service, repository, catalog = service_setup

    catalog.get_listing.return_value = SimpleNamespace(
        listing_id=10,
        number_of_positions=2,
    )

    student = Student(
        full_name="Test Student",
        email="student@example.com",
        programme_of_study="Computer Science",
        skills="Python",
        certifications="",
        career_interests="Software Development",
    )
    student.student_id = 5

    repository.get_student_by_email.return_value = student
    repository.has_application.return_value = True

    with pytest.raises(DuplicateInternshipApplication):
        service.submit_application(**valid_details)


def test_successfully_submits_application(
    service_setup, valid_details
):
    service, repository, catalog = service_setup

    catalog.get_listing.return_value = SimpleNamespace(
        listing_id=10,
        number_of_positions=2,
    )

    repository.get_student_by_email.return_value = None
    repository.save_submission.side_effect = lambda application: application

    result = service.submit_application(**valid_details)

    assert result.listing_id == 10
    assert result.student.email == "student@example.com"
    assert result.student.full_name == "Test Student"

    repository.save_submission.assert_called_once()
