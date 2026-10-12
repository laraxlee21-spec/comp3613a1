import re
from collections import defaultdict

from app.models.internship import InternshipApplication, InternshipMatch
from app.repositories.internship_matching import InternshipMatchingRepository

_WORD_PATTERN = re.compile(r"[^\W_]+", re.UNICODE)


class InternshipMatchingService:
    def __init__(self, repository: InternshipMatchingRepository):
        self.repository = repository

    @staticmethod
    def _keywords(*values: str) -> set[str]:
        return {
            word
            for value in values
            for word in _WORD_PATTERN.findall(value.casefold())
        }

    @classmethod
    def _score(cls, application: InternshipApplication) -> float:
        student = application.student
        listing = application.listing

        listing_keywords = cls._keywords(listing.skills, listing.requirements)
        if not listing_keywords:
            return 0.0

        student_keywords = cls._keywords(
            student.skills,
            student.certifications,
            student.career_interests,
            student.programme_of_study,
        )
        return 100.0 * len(listing_keywords & student_keywords) / len(
            listing_keywords
        )

    def run_matching(self) -> int:
        applications = self.repository.get_submitted_applications()
        if not applications:
            return 0

        application_ids: list[int] = []
        applications_by_listing: dict[
            int, list[tuple[InternshipApplication, float]]
        ] = defaultdict(list)

        for application in applications:
            if application.application_id is None:
                raise RuntimeError("Submitted application has no database ID.")
            if application.listing.listing_id is None:
                raise RuntimeError("Internship listing has no database ID.")

            application_ids.append(application.application_id)
            applications_by_listing[application.listing.listing_id].append(
                (application, self._score(application))
            )

        existing_matches = self.repository.get_matches_for_applications(
            application_ids
        )
        outcomes: list[InternshipMatch] = []

        for candidates in applications_by_listing.values():
            candidates.sort(
                key=lambda candidate: (
                    -candidate[1],
                    candidate[0].application_date,
                    candidate[0].application_id,
                )
            )
            available_positions = max(
                0,
                candidates[0][0].listing.number_of_positions,
            )

            for index, (application, score) in enumerate(candidates):
                application_id = application.application_id
                listing_id = application.listing.listing_id
                if application_id is None or listing_id is None:
                    raise RuntimeError(
                        "Submitted application or listing has no database ID."
                    )

                match_status = (
                    "Matched" if index < available_positions else "Not Matched"
                )
                match = existing_matches.get(application_id)

                if match is None:
                    match = InternshipMatch(
                        application_id=application_id,
                        listing_id=listing_id,
                        match_score=score,
                        match_status=match_status,
                        notification_status="Unread",
                    )
                else:
                    if match.match_status != match_status:
                        match.notification_status = "Unread"
                    match.listing_id = listing_id
                    match.match_score = score
                    match.match_status = match_status

                outcomes.append(match)

        self.repository.save_outcomes(outcomes)
        return len(outcomes)

    def get_matches_for_student(self, email: str) -> list[InternshipMatch]:
        return self.repository.get_matches_for_student(email)
