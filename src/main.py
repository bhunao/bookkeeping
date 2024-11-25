from contextlib import asynccontextmanager
import datetime
from decimal import Decimal
from pprint import pprint
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from sqlmodel import Field, SQLModel, Session, create_engine
from sqlalchemy.exc import StatementError


@asynccontextmanager
async def lifespan(app: FastAPI):
    assert app
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(title="Bookkeeper", lifespan=lifespan)

router = APIRouter(prefix="/transactions")


@app.get("/health_check")
async def health_check():
    return True


DATABASE_URL = "sqlite:///books.db"
engine = create_engine(DATABASE_URL, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


class Transaction(SQLModel, table=True):
    id: int | None = Field(primary_key=True, default=None)
    date: datetime.date
    value: Decimal
    external_id: str | None = None
    entity: str
    type: str


DependsSession: Session = Depends(get_session)


class TransactionCRUD:
    def __init__(self, session: Session = DependsSession) -> None:
        self.session = session

    def create(self, recordlist: list[Transaction]) -> list[Transaction]:
        s = self.session

        s.add_all(recordlist)
        s.commit()
        [s.refresh(rec) for rec in recordlist]
        return recordlist


DependsTransCrud: TransactionCRUD = Depends(TransactionCRUD)


@router.post("/")
async def create_transaction(
    recordlist: list[Transaction], crud: TransactionCRUD = DependsTransCrud
):
    for i in recordlist:
        i.date = datetime.datetime.strptime(i.date, "%Y-%m-%d")
        pprint((i.date, type(i.date)))

    try:
        db_recordlist = crud.create(recordlist)
    except StatementError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"db error {error=}",
        )
    return db_recordlist


app.include_router(router)
