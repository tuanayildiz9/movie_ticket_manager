from pathlib import Path
from sqlmodel import SQLModel, Session, create_engine
from uuid import uuid4

_DB_PATH = Path(__file__).resolve().parent.parent / "movie_ticket_manager.db"
DATABASE_URL = f"sqlite:///{_DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    _migrate_account_split()
    _drop_legacy_tables()


def _migrate_account_split() -> None:
    with engine.begin() as connection:
        table_rows = connection.exec_driver_sql("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        tables = {row[0] for row in table_rows}
        if "kunde" not in tables or "account" not in tables:
            return

        kunde_columns = [row[1] for row in connection.exec_driver_sql("PRAGMA table_info(kunde)").fetchall()]
        if "account_id" not in kunde_columns:
            connection.exec_driver_sql("ALTER TABLE kunde ADD COLUMN account_id TEXT")
            kunde_columns.append("account_id")

        legacy_columns = {"email", "passwort_hash", "rolle"}.issubset(set(kunde_columns))
        if not legacy_columns:
            return

        rows = connection.exec_driver_sql(
            "SELECT kunde_id, email, passwort_hash, rolle, account_id FROM kunde WHERE account_id IS NULL OR account_id = ''"
        ).fetchall()
        for kunde_id, email, passwort_hash, rolle, account_id in rows:
            existing = connection.exec_driver_sql(
                "SELECT account_id FROM account WHERE email = ?",
                (email,),
            ).fetchone()
            if existing is not None:
                resolved_account_id = existing[0]
            else:
                resolved_account_id = str(uuid4())
                connection.exec_driver_sql(
                    "INSERT INTO account (account_id, email, passwort_hash, rolle, aktiv) VALUES (?, ?, ?, ?, ?)",
                    (resolved_account_id, email, passwort_hash, rolle or "kunde", 1),
                )
            connection.exec_driver_sql(
                "UPDATE kunde SET account_id = ? WHERE kunde_id = ?",
                (resolved_account_id, kunde_id),
            )


def _drop_legacy_tables() -> None:
    with engine.begin() as connection:
        connection.exec_driver_sql("DROP TABLE IF EXISTS filmliste_kunde")

def get_session():
    with Session(engine) as session:
        yield session