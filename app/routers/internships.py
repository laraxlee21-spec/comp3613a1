from fastapi import Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from app.dependencies.auth import AuthDep
from app.dependencies.session import SessionDep
from app.repositories.internship_catalog import InternshipCatalogRepository
from app.repositories.internship_application import InternshipApplicationRepository
from app.services.internship_application import (
    DuplicateInternshipApplication,
    InternshipApplicationService,
    InternshipListingNotFound,
    InternshipListingUnavailable,
    StudentEmailMismatch,
    StudentProfileIncomplete,
)
from app.services.internship_catalog import InternshipCatalogService
from app.utilities.flash import flash

from . import router, templates


def _application_service(db: Session) -> InternshipApplicationService:
    return InternshipApplicationService(
        InternshipApplicationRepository(db),
        InternshipCatalogRepository(db),
    )


def _catalog_service(db: Session) -> InternshipCatalogService:
    return InternshipCatalogService(InternshipCatalogRepository(db))


@router.get(
    "/app/internships",
    response_class=HTMLResponse,
    name="browse_internships_view",
)
async def browse_internships_view(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    q: str = Query(default="", max_length=100),
):
    service = _catalog_service(db)
    listings = service.list_listings(q.strip())
    return templates.TemplateResponse(
        request=request,
        name="internship_browse.html",
        context={"user": user, "listings": listings, "search_query": q.strip()},
    )


@router.get(
    "/app/internships/{listing_id}",
    response_class=HTMLResponse,
    name="internship_details_view",
)
async def internship_details_view(
    listing_id: int,
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    listing = _catalog_service(db).get_listing(listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Internship listing not found.")
    return templates.TemplateResponse(
        request=request,
        name="internship_details.html",
        context={"user": user, "listing": listing},
    )


@router.get(
    "/app/internships/{listing_id}/select",
    response_class=HTMLResponse,
    name="select_internship_view",
)
async def select_internship_view(
    listing_id: int,
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    listing = _catalog_service(db).get_listing(listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Internship listing not found.")
    return templates.TemplateResponse(
        request=request,
        name="internship_select.html",
        context={"user": user, "listing": listing},
    )


@router.get(
    "/app/internships/{listing_id}/apply",
    response_class=HTMLResponse,
    name="apply_internship_view",
)
async def apply_internship_view(
    listing_id: int,
    request: Request,
    user: AuthDep,
    db: SessionDep,
):
    catalog_service = _catalog_service(db)
    listing = catalog_service.get_listing(listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Internship listing not found.")
    service = _application_service(db)
    profile = service.get_student_profile(user.email)
    return templates.TemplateResponse(
        request=request,
        name="internship_application.html",
        context={
            "user": user,
            "listing": listing,
            "profile": profile,
            "account_email": user.email,
        },
    )


@router.post("/applications", name="submit_internship_application")
async def submit_internship_application(
    request: Request,
    user: AuthDep,
    db: SessionDep,
    listing_id: int = Form(),
    full_name: str = Form(),
    email: str = Form(),
    programme_of_study: str = Form(),
    skills: str = Form(),
    certifications: str = Form(),
    career_interests: str = Form(),
):
    service = _application_service(db)
    try:
        service.submit_application(
            listing_id=listing_id,
            account_email=user.email,
            full_name=full_name,
            email=email,
            programme_of_study=programme_of_study,
            skills=skills,
            certifications=certifications,
            career_interests=career_interests,
        )
    except (
        DuplicateInternshipApplication,
        InternshipListingUnavailable,
        StudentEmailMismatch,
        StudentProfileIncomplete,
    ) as exc:
        flash(request, str(exc), "warning")
        listing = _catalog_service(db).get_listing(listing_id)
        if listing is None:
            raise HTTPException(status_code=404, detail="Internship listing not found.")
        return templates.TemplateResponse(
            request=request,
            name="internship_application.html",
            context={
                "user": user,
                "listing": listing,
                "account_email": user.email,
                "profile": {
                    "full_name": full_name,
                    "programme_of_study": programme_of_study,
                    "skills": skills,
                    "certifications": certifications,
                    "career_interests": career_interests,
                },
            },
        )
    except InternshipListingNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    flash(request, "Your internship application was submitted.", "success")
    return RedirectResponse(request.url_for("user_home_view"), status_code=303)
