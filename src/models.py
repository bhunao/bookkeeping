from decimal import Decimal

from fastapi import Depends
from sqlmodel import Field, Session

from src.core import get_session, MODEL

DepSession: Session = Depends(get_session)


# Files
class FileBase(MODEL):
    name: str
    content: bytes


class FileUpdate(MODEL):
    id: int
    name: str


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
