from app.models.internship import InternshipApplication, Student
from app.repositories.internship_application import InternshipApplicationRepository
from app.repositories.internship_catalog import InternshipCatalogRepository


class InternshipListingNotFound(LookupError):
    pass


class InternshipListingUnavailable(ValueError):
    pass


class DuplicateInternshipApplication(ValueError):
    pass


class StudentEmailMismatch(ValueError):
    pass


class StudentProfileIncomplete(ValueError):
    pass


class InternshipApplicationService:
    def __init__(
        self,
        repository: InternshipApplicationRepository,
        catalog_repository: InternshipCatalogRepository,
    ):
        self.repository = repository
        self.catalog_repository = catalog_repository

    def get_student_profile(self, email: str) -> Student | None:
        return self.repository.get_student_by_email(email)

    def submit_application(
        self,
        *,
        listing_id: int,
        account_email: str,
        full_name: str,
        email: str,
        programme_of_study: str,
        skills: str,
        certifications: str,
        career_interests: str,
    ) -> InternshipApplication:
        if email.strip().casefold() != account_email.casefold():
            raise StudentEmailMismatch(
                "Use the email address associated with your signed-in account."
            )
        if any(
            not value.strip()
            for value in (
                full_name,
                programme_of_study,
                skills,
                certifications,
                career_interests,
            )
        ):
            raise StudentProfileIncomplete("Complete all application form fields.")

        listing = self.catalog_repository.get_listing(listing_id)
        if listing is None:
            raise InternshipListingNotFound("That internship listing no longer exists.")
        if listing.number_of_positions <= 0:
            raise InternshipListingUnavailable(
                "There are no available positions for this internship."
            )

        student = self.repository.get_student_by_email(account_email)
        if student is not None:
            if student.student_id is None:
                raise RuntimeError("Student profile has no database ID.")
            if self.repository.has_application(student.student_id, listing_id):
                raise DuplicateInternshipApplication(
                    "You have already applied for this internship."
                )
            student.full_name = full_name.strip()
            student.programme_of_study = programme_of_study.strip()
            student.skills = skills.strip()
            student.certifications = certifications.strip()
            student.career_interests = career_interests.strip()
        else:
            student = Student(
                full_name=full_name.strip(),
                email=account_email,
                programme_of_study=programme_of_study.strip(),
                skills=skills.strip(),
                certifications=certifications.strip(),
                career_interests=career_interests.strip(),
            )

        application = InternshipApplication(listing_id=listing_id, student=student)
        return self.repository.save_submission(application)
