from collections.abc import Generator
from pydantic_settings import BaseSettings
from sqlmodel import Session, create_engine


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///bookkeeper.db"


settings = Settings()
engine = create_engine(settings.DATABASE_URL)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
