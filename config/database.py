from sqlmodel import SQLModel, Session, create_engine

# Import ORM tables so SQLModel metadata knows about every mapped class before create_all().
from backend.models import orm as _orm  # noqa: F401

# Import ORM models so SQLModel metadata contains all table definitions.
from backend.models import orm  # noqa: F401

DATABASE_URL = "sqlite:///movie_ticket_manager.db"

engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session