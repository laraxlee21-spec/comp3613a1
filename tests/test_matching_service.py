
from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock

from app.services.internship_matching import InternshipMatchingService


def make_application(application_id, student_skills, listing):
    student = SimpleNamespace(
        skills=student_skills,
        certifications="",
        career_interests="",
        programme_of_study="Computer Science",
    )

    return SimpleNamespace(
        application_id=application_id,
        listing_id=listing.listing_id,
        application_date=date(2026, 1, application_id),
        student=student,
        listing=listing,
    )


def test_matching_returns_zero_when_no_applications():
    repository = MagicMock()
    repository.get_submitted_applications.return_value = []

    service = InternshipMatchingService(repository)

    result = service.run_matching()

    assert result == 0
    repository.save_outcomes.assert_not_called()


def test_calculates_matching_score():
    repository = MagicMock()

    listing = SimpleNamespace(
        listing_id=10,
        skills="Python SQL",
        requirements="AWS",
        number_of_positions=2,
    )

    application = make_application(1, "Python AWS", listing)

    repository.get_submitted_applications.return_value = [application]
    repository.get_matches_for_applications.return_value = {}

    service = InternshipMatchingService(repository)

    result = service.run_matching()

    assert result == 1

    saved_matches = repository.save_outcomes.call_args[0][0]

    assert round(saved_matches[0].match_score, 2) == 66.67
    assert saved_matches[0].match_status == "Matched"


def test_highest_scoring_student_gets_available_position():
    repository = MagicMock()

    listing = SimpleNamespace(
        listing_id=10,
        skills="Python Java",
        requirements="",
        number_of_positions=1,
    )

    strong_application = make_application(1, "Python Java", listing)
    weak_application = make_application(2, "HTML CSS", listing)

    repository.get_submitted_applications.return_value = [
        weak_application,
        strong_application,
    ]
    repository.get_matches_for_applications.return_value = {}

    service = InternshipMatchingService(repository)

    result = service.run_matching()

    assert result == 2

    saved_matches = repository.save_outcomes.call_args[0][0]

    statuses = {
        match.application_id: match.match_status
        for match in saved_matches
    }

    assert statuses[1] == "Matched"
    assert statuses[2] == "Not Matched"
