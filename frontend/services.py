from uuid import UUID

from sqlmodel import Session, select

from backend.models.orm.kategorie_sql import Kategorie as KategorieORM
from backend.models.orm.sitzplatz_sql import Sitzplatz as SitzplatzORM
from backend.models.orm.sprache_sql import Sprache as SpracheORM
from backend.models.orm.zahlungsart_sql import Zahlungsart as ZahlungsartORM
from config.database import engine

_svc: dict = {}


def init_services(user_service, film_service, bestellung_service, admin_service, snack_repo, bestellung_repo) -> None:
    _svc.update({
        "user": user_service,
        "film": film_service,
        "bestellung": bestellung_service,
        "admin": admin_service,
        "snack_repo": snack_repo,
        "bestellung_repo": bestellung_repo,
    })


def user_service():
    return _svc["user"]


def film_service():
    return _svc["film"]


def bestellung_service():
    return _svc["bestellung"]


def admin_service():
    return _svc["admin"]


def snack_repo():
    return _svc["snack_repo"]


def bestellung_repo():
    return _svc["bestellung_repo"]


def get_all_kategorien() -> list[dict]:
    with Session(engine) as session:
        rows = session.exec(select(KategorieORM)).all()
        return [{"id": row.kategorie_id, "name": row.name} for row in rows]


def get_all_sprachen() -> list[dict]:
    with Session(engine) as session:
        rows = session.exec(select(SpracheORM)).all()
        return [{"id": row.sprache_id, "name": row.name} for row in rows]


def get_all_zahlungsarten() -> list[dict]:
    with Session(engine) as session:
        rows = session.exec(select(ZahlungsartORM)).all()
        return [{"id": row.zahlungsart_id, "name": row.name} for row in rows]


def get_kategorie_names(ids: list[UUID]) -> list[str]:
    if not ids:
        return []
    with Session(engine) as session:
        names = []
        for uid in ids:
            row = session.get(KategorieORM, uid)
            if row:
                names.append(row.name)
        return names


def get_all_seats_for_vorstellung(vorstellung_id: UUID) -> list[dict]:
    """Alle Sitze einer Vorstellung – inkl. bereits belegter (für Saalplan)."""
    with Session(engine) as session:
        rows = session.exec(
            select(SitzplatzORM).where(SitzplatzORM.vorstellung_id == vorstellung_id)
        ).all()
        return [
            {
                "sitzplatz_id": row.sitzplatz_id,
                "sitz_label": row.sitz_label,
                "sektor": row.sektor,
                "besetzt": row.besetzt,
            }
            for row in rows
        ]


def get_sitzplatz_info(sitzplatz_id: UUID) -> dict | None:
    with Session(engine) as session:
        row = session.get(SitzplatzORM, sitzplatz_id)
        if row:
            return {"sitz_label": row.sitz_label, "sektor": row.sektor}
    return None


def get_sprache_names(ids: list[UUID]) -> list[str]:
    if not ids:
        return []
    with Session(engine) as session:
        names = []
        for uid in ids:
            row = session.get(SpracheORM, uid)
            if row:
                names.append(row.name)
        return names
