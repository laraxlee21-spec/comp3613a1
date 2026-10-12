from app.repositories.user import UserRepository


def resolve_admin_seed_password(
    repository: UserRepository,
    *,
    production: bool,
    admin_initial_password: str,
) -> str:
    if (
        production
        and repository.get_by_username("admin") is None
        and not admin_initial_password.strip()
    ):
        raise RuntimeError(
            "ADMIN_INITIAL_PASSWORD is required to create the initial "
            "Administrator account in production."
        )
    return admin_initial_password or "adminpass"
