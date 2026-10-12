from app.models.internship import InternshipListing
from app.repositories.internship_catalog import InternshipCatalogRepository


class InternshipCatalogService:
    def __init__(self, repository: InternshipCatalogRepository):
        self.repository = repository

    def list_listings(self, query: str = "") -> list[InternshipListing]:
        return self.repository.list_listings(query)

    def get_listing(self, listing_id: int) -> InternshipListing | None:
        return self.repository.get_listing(listing_id)
