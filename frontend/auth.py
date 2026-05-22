from uuid import UUID

from nicegui import app, ui


def is_logged_in() -> bool:
    return bool(app.storage.user.get("logged_in", False))


def is_admin() -> bool:
    return bool(app.storage.user.get("is_admin", False))


def get_account_id() -> UUID | None:
    aid = app.storage.user.get("account_id")
    return UUID(aid) if aid else None


def get_kunde_id() -> UUID | None:
    """Gibt die kunde_id zurück – lädt sie bei Bedarf frisch aus der DB."""
    kid = app.storage.user.get("kunde_id")
    if kid and str(kid).strip():
        return UUID(str(kid))

    # Fallback: Kunde anhand account_id nachschlagen und in Session speichern
    if not is_admin():
        aid = app.storage.user.get("account_id")
        if aid:
            try:
                import frontend.services as svc
                kunde = svc.user_service().get_profile_by_account_id(UUID(aid))
                if kunde:
                    app.storage.user["kunde_id"] = str(kunde.kunde_id)
                    return kunde.kunde_id
            except Exception:
                pass
    return None


def get_email() -> str | None:
    return app.storage.user.get("email")


def logout():
    app.storage.user.clear()
    ui.navigate.to("/login")
