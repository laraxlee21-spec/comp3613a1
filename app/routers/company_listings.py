from fastapi import Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError

from app.dependencies import SessionDep
from app.dependencies.auth import CompanyDep
from app.repositories.company_listing import CompanyListingRepository
from app.repositories.company_registration import CompanyRegistrationRepository
from app.services.company_registration import (
    CompanyAccountConflict,
    CompanyRegistrationService,
)
from app.services.company_listing import CompanyListingService, CompanyProfileMissing
from app.utilities.flash import flash
from . import router, templates


def _listing_service(db: SessionDep) -> CompanyListingService:
    return CompanyListingService(CompanyListingRepository(db))


@router.get("/register/company", response_class=HTMLResponse, name="company_register_view")
async def company_register_view(request: Request):
    return templates.TemplateResponse(request=request, name="company_register.html")


@router.post("/register/company", name="company_register_action")
def company_register_action(
    request: Request,
    db: SessionDep,
    username: str = Form(),
    email: str = Form(),
    password: str = Form(),
    company_name: str = Form(),
    contact_name: str = Form(),
    industry: str = Form(),
):
    service = CompanyRegistrationService(CompanyRegistrationRepository(db))
    try:
        service.register_company(
            username=username,
            email=email,
            password=password,
            company_name=company_name,
            contact_name=contact_name,
            industry=industry,
        )
    except CompanyAccountConflict as exc:
        flash(request, str(exc), "danger")
        return RedirectResponse(
            request.url_for("company_register_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except ValidationError:
        flash(request, "Complete all company registration fields with a valid email.", "danger")
        return RedirectResponse(
            request.url_for("company_register_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    flash(request, "Company account created. Sign in to continue.", "success")
    return RedirectResponse(
        request.url_for("login_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/company", response_class=HTMLResponse, name="company_home_view")
async def company_home_view(request: Request, user: CompanyDep):
    return templates.TemplateResponse(
        request=request,
        name="company_home.html",
        context={"user": user},
    )


@router.get(
    "/company/listings",
    response_class=HTMLResponse,
    name="company_my_listings_view",
)
def company_my_listings_view(
    request: Request,
    db: SessionDep,
    user: CompanyDep,
):
    try:
        listings = _listing_service(db).list_company_listings(user)
    except CompanyProfileMissing as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return templates.TemplateResponse(
        request=request,
        name="company_listings.html",
        context={"user": user, "listings": listings},
    )


@router.get(
    "/company/listings/new",
    response_class=HTMLResponse,
    name="company_create_listing_view",
)
async def company_create_listing_view(request: Request, user: CompanyDep):
    return templates.TemplateResponse(
        request=request,
        name="company_listing_form.html",
        context={"user": user},
    )


@router.post(
    "/company/listings",
    name="create_company_listing",
    responses={422: {"description": "Invalid listing form data"}},
)
def create_company_listing(
    request: Request,
    db: SessionDep,
    user: CompanyDep,
    title: str = Form(),
    description: str = Form(),
    skills: str = Form(),
    requirements: str = Form(),
    location: str = Form(),
    number_of_positions: int = Form(ge=1),
):
    try:
        _listing_service(db).create_listing(
            user=user,
            title=title,
            description=description,
            skills=skills,
            requirements=requirements,
            location=location,
            number_of_positions=number_of_positions,
        )
    except CompanyProfileMissing as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValidationError:
        flash(request, "Complete all listing fields and provide at least one position.", "danger")
        return RedirectResponse(
            request.url_for("company_create_listing_view"),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    flash(request, "Internship listing published.", "success")
    return RedirectResponse(
        request.url_for("company_my_listings_view"),
        status_code=status.HTTP_303_SEE_OTHER,
    )