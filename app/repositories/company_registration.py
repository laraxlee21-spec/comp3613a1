import logging

from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.models.internship import Company
from app.models.user import User

logger = logging.getLogger(__name__)


class CompanyRegistrationRepository:
    def __init__(self, db: Session):
        self.db = db

    def username_or_email_exists(self, username: str, email: str) -> bool:
        statement = select(User.id).where(
            (User.username == username) | (User.email == email)
        )
        return self.db.exec(statement).first() is not None

    def create_company_account(self, user: User, company: Company) -> Company:
        company.user = user
        user.role = "company"
        try:
            self.db.add(company)
            self.db.commit()
            self.db.refresh(company)
            return company
        except IntegrityError:
            self.db.rollback()
            raise
        except Exception:
            logger.exception("Unable to create company account")
            self.db.rollback()
            raise
