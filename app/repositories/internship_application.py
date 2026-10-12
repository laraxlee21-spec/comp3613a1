import logging

from sqlmodel import Session, select

from app.models.internship import InternshipApplication, Student

logger = logging.getLogger(__name__)


class InternshipApplicationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_student_by_email(self, email: str) -> Student | None:
        statement = select(Student).where(Student.email == email)
        return self.db.exec(statement).one_or_none()

    def has_application(self, student_id: int, listing_id: int) -> bool:
        statement = select(InternshipApplication.application_id).where(
            InternshipApplication.student_id == student_id,
            InternshipApplication.listing_id == listing_id,
        )
        return self.db.exec(statement).first() is not None

    def save_submission(
        self,
        application: InternshipApplication,
    ) -> InternshipApplication:
        try:
            self.db.add(application)
            self.db.commit()
            self.db.refresh(application)
            return application
        except Exception:
            logger.exception("Unable to save internship application")
            self.db.rollback()
            raise
