import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, FastAPI
from pydantic import validator
from sqlmodel import Field, SQLModel, Session, create_engine


app = FastAPI(title="Bookkeeper")

router = APIRouter(prefix="/transactions")


@app.get("/health_check")
async def health_check():
    return True


DATABASE_URL = "sqlite:///books.db"
engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


def lifespan():
    SQLModel.metadata.create_all(engine)


class Transaction(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    date: datetime.date
    value: Decimal
    external_id: str | None = None
    entity: str
    type: str

    @validator("date", pre=True)
    def parse_date(cls, value):
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            try:
                return datetime.strptime(value, "%Y-%m-%d").date()
            except ValueError:
                raise ValueError("Invalid date format. Use YYYY-MM-DD")
        raise ValueError("Invalid date type")


DependsSession: Session = Depends(get_session)


class TransactionCRUD:
    def __init__(self, session: Session = DependsSession) -> None:
        self.session = session

    def create(self, recordlist: list[Transaction]) -> list[Transaction]:
        s = self.session

        s.add_all(recordlist)
        s.commit()
        s.refresh(recordlist)
        return recordlist


DependsTransCrud: TransactionCRUD = Depends(TransactionCRUD)


@router.post("/")
async def create_transaction(
    recordlist: list[Transaction], crud: TransactionCRUD = DependsTransCrud
):
    db_recordlist = crud.create(recordlist)
    return db_recordlist


app.include_router(router)
