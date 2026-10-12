"""Database table models.

Import every table model here so ``SQLModel.metadata.create_all`` sees them.
"""

from app.models.user import User
from app.models.internship import (
    Company,
    InternshipApplication,
    InternshipListing,
    Student,
)

__all__ = ["User", "Student", "Company", "InternshipListing", "InternshipApplication"]
