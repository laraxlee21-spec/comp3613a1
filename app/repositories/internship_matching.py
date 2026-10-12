import logging

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models.internship import (
    InternshipApplication,
    InternshipMatch,
    Student,
)

logger = logging.getLogger(__name__)


class InternshipMatchingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_submitted_applications(self) -> list[InternshipApplication]:
        statement = (
            select(InternshipApplication)
            .where(InternshipApplication.status == "Submitted")
            .options(
                selectinload(InternshipApplication.student),
                selectinload(InternshipApplication.listing),
            )
        )
        return list(self.db.exec(statement).all())

    def get_matches_for_applications(
        self,
        application_ids: list[int],
    ) -> dict[int, InternshipMatch]:
        if not application_ids:
            return {}

        statement = select(InternshipMatch).where(
            InternshipMatch.application_id.in_(application_ids)
        )
        matches = self.db.exec(statement).all()
        return {match.application_id: match for match in matches}

    def save_outcomes(self, outcomes: list[InternshipMatch]) -> None:
        if not outcomes:
            return

        try:
            self.db.add_all(outcomes)
            self.db.commit()
        except Exception:
            logger.exception("Unable to save internship matching outcomes")
            self.db.rollback()
            raise

    def get_matches_for_student(self, email: str) -> list[InternshipMatch]:
        statement = (
            select(InternshipMatch)
            .join(InternshipMatch.application)
            .join(InternshipApplication.student)
            .where(Student.email == email)
            .options(
                selectinload(InternshipMatch.application).selectinload(
                    InternshipApplication.student
                ),
                selectinload(InternshipMatch.application).selectinload(
                    InternshipApplication.listing
                ),
            )
            .order_by(
                InternshipApplication.application_date.desc(),
                InternshipApplication.application_id.desc(),
            )
        )
        return list(self.db.exec(statement).all())
