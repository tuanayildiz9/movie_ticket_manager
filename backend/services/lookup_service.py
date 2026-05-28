from uuid import UUID

from sqlmodel import Session, select

from backend.models.orm.kategorie_sql import Kategorie as KategorieORM
from backend.models.orm.sitzplatz_sql import Sitzplatz as SitzplatzORM
from backend.models.orm.sprache_sql import Sprache as SpracheORM
from backend.models.orm.vorstellung_sql import Vorstellung as VorstellungORM
from backend.models.orm.zahlungsart_sql import Zahlungsart as ZahlungsartORM
from config.database import engine


class LookupService:
    def list_categories(self) -> list[dict[str, object]]:
        with Session(engine) as session:
            rows = session.exec(select(KategorieORM)).all()
            return [{"id": row.kategorie_id, "name": row.name} for row in rows]

    def list_languages(self) -> list[dict[str, object]]:
        with Session(engine) as session:
            rows = session.exec(select(SpracheORM)).all()
            return [{"id": row.sprache_id, "name": row.name} for row in rows]

    def list_payment_methods(self) -> list[dict[str, object]]:
        with Session(engine) as session:
            rows = session.exec(select(ZahlungsartORM)).all()
            return [{"id": row.zahlungsart_id, "name": row.name} for row in rows]

    def get_category_names(self, ids: list[UUID]) -> list[str]:
        if not ids:
            return []
        with Session(engine) as session:
            names = []
            for uid in ids:
                row = session.get(KategorieORM, uid)
                if row:
                    names.append(row.name)
            return names

    def get_language_names(self, ids: list[UUID]) -> list[str]:
        if not ids:
            return []
        with Session(engine) as session:
            names = []
            for uid in ids:
                row = session.get(SpracheORM, uid)
                if row:
                    names.append(row.name)
            return names

    def get_all_seats_for_vorstellung(self, vorstellung_id: UUID) -> list[dict[str, object]]:
        with Session(engine) as session:
            rows = session.exec(select(SitzplatzORM).where(SitzplatzORM.vorstellung_id == vorstellung_id)).all()
            return [
                {
                    "sitzplatz_id": row.sitzplatz_id,
                    "sitz_label": row.sitz_label,
                    "sektor": row.sektor,
                    "besetzt": row.besetzt,
                }
                for row in rows
            ]

    def get_vorstellungen_in_saal_ort(self, saal: str, ort: str) -> list[dict[str, object]]:
        with Session(engine) as session:
            rows = session.exec(select(VorstellungORM).where(VorstellungORM.saal == saal, VorstellungORM.ort == ort)).all()
            return [
                {"vorstellung_id": row.vorstellung_id, "startzeit": row.startzeit, "endzeit": row.endzeit}
                for row in rows
            ]

    def get_existing_saele(self) -> list[str]:
        with Session(engine) as session:
            rows = session.exec(select(VorstellungORM.saal).distinct().order_by(VorstellungORM.saal)).all()
            return [row for row in rows if row]

    def get_existing_orte(self) -> list[str]:
        with Session(engine) as session:
            rows = session.exec(select(VorstellungORM.ort).distinct().order_by(VorstellungORM.ort)).all()
            return [row for row in rows if row]

    def get_sitzplatz_info(self, sitzplatz_id: UUID) -> dict[str, object] | None:
        with Session(engine) as session:
            row = session.get(SitzplatzORM, sitzplatz_id)
            if row:
                return {"sitz_label": row.sitz_label, "sektor": row.sektor}
        return None