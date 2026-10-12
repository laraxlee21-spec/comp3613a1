from fastapi import Request
from fastapi.responses import RedirectResponse

from app.dependencies import SessionDep
from app.dependencies.auth import AdminDep
from app.repositories.internship_matching import InternshipMatchingRepository
from app.services.internship_matching import InternshipMatchingService
from app.utilities.flash import flash

from . import router


@router.post("/admin/matching/run", name="admin_matching_action")
def admin_matching_action(
    request: Request,
    db: SessionDep,
    _admin: AdminDep,
):
    repository = InternshipMatchingRepository(db)
    service = InternshipMatchingService(repository)
    service.run_matching()

    flash(request, "Matching completed.", "success")
    return RedirectResponse(
        request.url_for("admin_home_view"),
        status_code=303,
    )