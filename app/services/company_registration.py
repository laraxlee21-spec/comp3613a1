from sqlalchemy.exc import IntegrityError

from app.models.internship import Company
from app.models.user import User
from app.repositories.company_registration import CompanyRegistrationRepository
from app.schemas.company import CompanyRegistration
from app.utilities.security import encrypt_password


class CompanyAccountConflict(ValueError):
    pass


class CompanyRegistrationService:
    def __init__(self, repository: CompanyRegistrationRepository):
        self.repository = repository

    def register_company(
        self,
        *,
        username: str,
        email: str,
        password: str,
        company_name: str,
        contact_name: str,
        industry: str,
    ) -> Company:
        data = CompanyRegistration(
            username=username.strip(),
            email=email.strip(),
            password=password,
            company_name=company_name.strip(),
            contact_name=contact_name.strip(),
            industry=industry.strip(),
        )
        if self.repository.username_or_email_exists(data.username, data.email):
            raise CompanyAccountConflict("Username or email already exists.")

        user = User(
            username=data.username,
            email=data.email,
            password=encrypt_password(data.password),
            role="company",
        )
        company = Company(
            company_name=data.company_name,
            contact_name=data.contact_name,
            email=data.email,
            industry=data.industry,
            user=user,
        )
        try:
            return self.repository.create_company_account(user, company)
        except IntegrityError as exc:
            raise CompanyAccountConflict(
                "Username or email already exists."
            ) from exc
