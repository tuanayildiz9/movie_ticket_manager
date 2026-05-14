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
    kid = app.storage.user.get("kunde_id")
    return UUID(kid) if kid else None


def get_email() -> str | None:
    return app.storage.user.get("email")


def logout():
    app.storage.user.clear()
    ui.navigate.to("/login")
