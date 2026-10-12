from fastapi import HTTPException, Request, status
from fastapi.responses import HTMLResponse

from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.repositories.internship_matching import InternshipMatchingRepository
from app.services.internship_matching import InternshipMatchingService

from . import router, templates


@router.get("/app", response_class=HTMLResponse)
async def user_home_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    if user.role != "regular_user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only student accounts may access the student dashboard.",
        )

    matching_service = InternshipMatchingService(
        InternshipMatchingRepository(db)
    )
    matches = matching_service.get_matches_for_student(user.email)

    return templates.TemplateResponse(
        request=request,
        name="app.html",
        context={"user": user, "matches": matches},
    )