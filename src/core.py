from collections.abc import Generator
from typing import Self

from fastapi import Depends, HTTPException, status
from pydantic_settings import BaseSettings
from sqlmodel import Session, SQLModel, create_engine, select


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///bookkeeper.db"


settings = Settings()
engine = create_engine(settings.DATABASE_URL)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


DepSession: Session = Depends(get_session)


class DatabaseMixin(SQLModel):
    """Database mixin"""

    def create(self, session: Session) -> Self:
        session.add(self)
        session.commit()
        session.refresh(self)
        return self

    @classmethod
    def read(cls, session: Session, id: str | int) -> Self:
        record = session.get(cls, id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File Not Found."
            )
        return record

    @classmethod
    def read_all(cls, session: Session) -> list[Self]:
        query = select(cls)
        result = session.exec(query).all()  # pyright: ignore[reportUnknownMemberType]
        return result

    def update(self, session: Session, schema: SQLModel) -> Self:
        fields_to_update = schema.__fields__.keys() & self.__fields__.keys()
        for field in fields_to_update:
            value: str = getattr(schema, field)
            if not value:
                continue
            setattr(self, field, value)
        session.commit()
        session.refresh(self)
        return self

    def delete(self, session: Session) -> Self:
        session.delete(self)
        session.commit()
        return self


MODEL = DatabaseMixin
