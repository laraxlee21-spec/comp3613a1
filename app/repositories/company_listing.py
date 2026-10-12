import logging

from sqlmodel import Session, select

from app.models.internship import Company, InternshipListing
from app.schemas.company import CompanyListingCreate

logger = logging.getLogger(__name__)


class CompanyListingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_company_for_user(self, user_id: int) -> Company | None:
        statement = select(Company).where(Company.user_id == user_id)
        return self.db.exec(statement).one_or_none()

    def create_listing(
        self,
        company_id: int,
        listing_data: CompanyListingCreate,
    ) -> InternshipListing:
        listing = InternshipListing(
            company_id=company_id,
            **listing_data.model_dump(),
        )
        try:
            self.db.add(listing)
            self.db.commit()
            self.db.refresh(listing)
            return listing
        except Exception:
            logger.exception("Unable to save company internship listing")
            self.db.rollback()
            raise

    def list_for_company(self, company_id: int) -> list[InternshipListing]:
        statement = (
            select(InternshipListing)
            .where(InternshipListing.company_id == company_id)
            .order_by(InternshipListing.listing_id.desc())
        )
        return list(self.db.exec(statement).all())
