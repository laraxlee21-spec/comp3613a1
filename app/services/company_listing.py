from app.models.internship import Company, InternshipListing
from app.models.user import User
from app.repositories.company_listing import CompanyListingRepository
from app.schemas.company import CompanyListingCreate


class CompanyProfileMissing(LookupError):
    pass


class CompanyListingService:
    def __init__(self, repository: CompanyListingRepository):
        self.repository = repository

    def _company_for_user(self, user: User) -> Company:
        if user.id is None:
            raise CompanyProfileMissing("The signed-in account has no database ID.")
        company = self.repository.get_company_for_user(user.id)
        if company is None or company.company_id is None:
            raise CompanyProfileMissing(
                "The signed-in company account has no company profile."
            )
        return company

    def create_listing(
        self,
        *,
        user: User,
        title: str,
        description: str,
        skills: str,
        requirements: str,
        location: str,
        number_of_positions: int,
    ) -> InternshipListing:
        data = CompanyListingCreate(
            title=title.strip(),
            description=description.strip(),
            skills=skills.strip(),
            requirements=requirements.strip(),
            location=location.strip(),
            number_of_positions=number_of_positions,
        )
        company = self._company_for_user(user)
        return self.repository.create_listing(company.company_id, data)

    def list_company_listings(self, user: User) -> list[InternshipListing]:
        company = self._company_for_user(user)
        return self.repository.list_for_company(company.company_id)
