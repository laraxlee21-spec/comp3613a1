from pydantic import BaseModel, EmailStr, Field


class CompanyListingCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    skills: str = Field(min_length=1)
    requirements: str = Field(min_length=1)
    location: str = Field(min_length=1)
    number_of_positions: int = Field(ge=1)


class CompanyRegistration(BaseModel):
    username: str = Field(min_length=1)
    email: EmailStr
    password: str = Field(min_length=1)
    company_name: str = Field(min_length=1)
    contact_name: str = Field(min_length=1)
    industry: str = Field(min_length=1)
