
from sqlmodel import select

from app.models.internship import Student, InternshipApplication


def test_student_can_submit_internship_application(
    client, db_session, test_user, test_listing
):
    """Test that a submitted application is saved in the database."""

    response = client.post(
        "/applications",
        data={
            "listing_id": str(test_listing.listing_id),
            "full_name": "Test Student",
            "email": test_user.email,
            "programme_of_study": "Computer Science",
            "skills": "Python, SQL",
            "certifications": "Python Certificate",
            "career_interests": "Software Development",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303

    student = db_session.exec(
        select(Student).where(Student.email == test_user.email)
    ).first()

    assert student is not None
    assert student.full_name == "Test Student"

    application = db_session.exec(
        select(InternshipApplication).where(
            InternshipApplication.student_id == student.student_id
        )
    ).first()

    assert application is not None
    assert application.listing_id == test_listing.listing_id
    assert application.status == "Submitted"


def test_application_with_different_email_is_rejected(
    client, db_session, test_user, test_listing
):
    """Test that an application using a different email is not saved."""

    response = client.post(
        "/applications",
        data={
            "listing_id": str(test_listing.listing_id),
            "full_name": "Test Student",
            "email": "different@example.com",
            "programme_of_study": "Computer Science",
            "skills": "Python, SQL",
            "certifications": "Python Certificate",
            "career_interests": "Software Development",
        },
        follow_redirects=False,
    )

    assert response.status_code == 200

    student = db_session.exec(
        select(Student).where(Student.email == test_user.email)
    ).first()

    assert student is None

    applications = db_session.exec(
        select(InternshipApplication)
    ).all()

    assert len(applications) == 0
