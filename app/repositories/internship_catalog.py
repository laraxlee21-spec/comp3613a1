import logging

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models.internship import Company, InternshipListing

logger = logging.getLogger(__name__)


class InternshipCatalogRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_listings(self, query: str = "") -> list[InternshipListing]:
        statement = select(InternshipListing).options(
            selectinload(InternshipListing.company)
        )
        if query:
            pattern = f"%{query.strip()}%"
            statement = statement.where(
                InternshipListing.title.ilike(pattern)
                | InternshipListing.skills.ilike(pattern)
            )
        return list(self.db.exec(statement).all())

    def get_listing(self, listing_id: int) -> InternshipListing | None:
        statement = (
            select(InternshipListing)
            .options(selectinload(InternshipListing.company))
            .where(InternshipListing.listing_id == listing_id)
        )
        return self.db.exec(statement).one_or_none()

    def seed_demo_listings(self) -> int:
        if self.db.exec(select(InternshipListing.listing_id).limit(1)).first() is not None:
            return 0

        companies = [
            Company(
                company_name="ABC Technologies",
                contact_name="Internship Team",
                email="careers@abc.example",
                industry="Technology",
                listings=[
                    InternshipListing(
                        title="Software Development Intern",
                        description=(
                            "Assist the company's software development team with "
                            "building, testing, and maintaining software applications."
                        ),
                        skills="Python, Java, Problem-solving, Teamwork",
                        requirements=(
                            "Currently enrolled in a university programme.\n"
                            "Basic programming knowledge.\n"
                            "Able to work collaboratively with a team."
                        ),
                        location="Port of Spain",
                        duration="3 months",
                        number_of_positions=2,
                    )
                ],
            ),
            Company(
                company_name="Tech Solutions Ltd.",
                contact_name="Internship Team",
                email="careers@techsolutions.example",
                industry="Technology",
                listings=[
                    InternshipListing(
                        title="IT Support Intern",
                        description="Help troubleshoot computer and network issues.",
                        skills="Networking, Troubleshooting",
                        requirements="",
                        location="Chaguanas",
                        number_of_positions=3,
                    )
                ],
            ),
            Company(
                company_name="Data Insights Ltd.",
                contact_name="Internship Team",
                email="careers@datainsights.example",
                industry="Data analytics",
                listings=[
                    InternshipListing(
                        title="Data Analyst Intern",
                        description="Assist with analysing and organising data.",
                        skills="SQL, Excel",
                        requirements="",
                        location="San Fernando",
                        number_of_positions=1,
                    )
                ],
            ),
        ]
        try:
            self.db.add_all(companies)
            self.db.commit()
            return len(companies)
        except Exception:
            logger.exception("Unable to seed demo internship listings")
            self.db.rollback()
            raise
