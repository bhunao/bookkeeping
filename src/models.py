from sqlmodel import DECIMAL, SQLModel


class File(SQLModel):
    file_name: str
    string_content: str


class Transaction(SQLModel):
    place: str
    value: DECIMAL
