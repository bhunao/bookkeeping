from datetime import date as _date
from decimal import Decimal

from fastapi import Depends
from sqlmodel import Field, Session

from src.core import MODEL, get_session

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


# Transactions
class TransactionBase(MODEL):
    date: _date
    value: Decimal
    external_id: str | None = None
    entity: str
    type: str


class TransactionUpdate(MODEL):
    id: int
    date: _date | None = None
    value: Decimal | None = None
    external_id: str | None = None
    entity: str | None = None
    type: str | None = None


class Transaction(TransactionBase, table=True):
    id: int | None = Field(primary_key=True, default=None)


# something something
class DeleteMSG(MODEL):
    message: str
    file: File
