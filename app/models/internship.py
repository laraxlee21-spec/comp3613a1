from datetime import date
from typing import Optional

from sqlalchemy import Column, Text, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.models.user import User


class Student(SQLModel, table=True):
    __tablename__ = "student"

    student_id: int | None = Field(default=None, primary_key=True)
    full_name: str
    email: str = Field(index=True, unique=True)
    programme_of_study: str
    skills: str = Field(sa_column=Column(Text, nullable=False))
    certifications: str = Field(sa_column=Column(Text, nullable=False))
    career_interests: str = Field(sa_column=Column(Text, nullable=False))
    applications: list["InternshipApplication"] = Relationship(back_populates="student")


class Company(SQLModel, table=True):
    __tablename__ = "company"

    company_id: int | None = Field(default=None, primary_key=True)

    user_id: int | None = Field(
        default=None,
        foreign_key="user.id",
        unique=True,
        index=True,
    )
    user: Optional["User"] = Relationship(back_populates="company")

    company_name: str
    contact_name: str
    email: str
    industry: str
    listings: list["InternshipListing"] = Relationship(back_populates="company")


class InternshipListing(SQLModel, table=True):
    __tablename__ = "internship_listing"

    listing_id: int | None = Field(default=None, primary_key=True)
    company_id: int = Field(foreign_key="company.company_id", index=True)
    title: str
    description: str = Field(sa_column=Column(Text, nullable=False))
    skills: str = Field(sa_column=Column(Text, nullable=False))
    requirements: str = Field(sa_column=Column(Text, nullable=False))
    location: str
    duration: str | None = None
    number_of_positions: int = Field(ge=0)
    company: Company = Relationship(back_populates="listings")
    applications: list["InternshipApplication"] = Relationship(back_populates="listing")
    matches: list["InternshipMatch"] = Relationship(back_populates="listing")


class InternshipApplication(SQLModel, table=True):
    __tablename__ = "internship_application"
    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "listing_id",
            name="uq_application_student_listing",
        ),
    )


    match: Optional["InternshipMatch"] = Relationship(
        back_populates="application",
        sa_relationship_kwargs={"uselist": False},
    )
    application_id: int | None = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.student_id", index=True)
    listing_id: int = Field(foreign_key="internship_listing.listing_id", index=True)
    application_date: date = Field(default_factory=date.today)
    status: str = "Submitted"
    student: Student = Relationship(back_populates="applications")
    listing: InternshipListing = Relationship(back_populates="applications")

class InternshipMatch(SQLModel, table=True):
    __tablename__ = "internship_match"
    __table_args__ = (
        UniqueConstraint("application_id", name="uq_match_application"),
    )

    match_id: int | None = Field(default=None, primary_key=True)
    application_id: int = Field(
        foreign_key="internship_application.application_id",
        index=True,
    )
    listing_id: int = Field(
        foreign_key="internship_listing.listing_id",
        index=True,
    )
    match_score: float
    match_status: str
    notification_status: str

    application: "InternshipApplication" = Relationship(back_populates="match")
    listing: "InternshipListing" = Relationship(back_populates="matches")