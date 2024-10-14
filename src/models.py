from typing import Self
from fastapi import Depends, HTTPException, status
from sqlmodel import Field, SQLModel, Session, select
from decimal import Decimal

from src.core import get_session


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
        query = select(File)
        result = session.exec(query).all()  # pyright: ignore[reportUnknownMemberType]
        return result

    def update(self, session: Session, schema: SQLModel) -> Self:
        fields_to_update = schema.__fields__.keys() & self.__fields__.keys()
        for field in fields_to_update:
            value: str = getattr(schema, field)
            setattr(self, field, value)
        session.commit()
        session.refresh(self)
        return self

    def delete(self, session: Session) -> Self:
        session.delete(self)
        session.commit()
        return self


MODEL = DatabaseMixin


# Files
class FileBase(MODEL):
    file_name: str
    string_content: str


class FileUpdate(MODEL):
    id: int
    file_name: str


class File(FileBase, table=True):
    id: int | None = Field(primary_key=True, default=None)
    pass


# Entities
class EntityType(MODEL, talbe=True):
    id: int = Field(primary_key=True)
    name: str


class EntityBase(MODEL):
    name: str
    type_id: int | None = None
    description: str


class Entity(EntityBase, table=True):
    id: int = Field(primary_key=True)
    pass


# Transactions
class BaseTransaction(MODEL):
    entity: str
    value: Decimal
    external_id: str | None = None


class Transaction(BaseTransaction, table=True):
    id: int = Field(primary_key=True)
    pass


# something something
class DeleteMSG(MODEL):
    message: str
    file: File
