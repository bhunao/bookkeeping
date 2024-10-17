from datetime import datetime
from io import StringIO

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from pandas.errors import ParserError
from sqlmodel import Session

from src.core import get_session
from src.models import DeleteMSG, File, FileUpdate, Transaction, TransactionBase, TransactionUpdate

router_files = APIRouter(prefix="/api/files")
router_transactions = APIRouter(prefix="/api/transactions")

DepSession: Session = Depends(get_session)


d_types = str | int | float


async def validate_csv_file(file: UploadFile) -> tuple[bytes, list[dict[str, d_types]]]:
    assert file
    byte_content = await file.read()
    try:
        str_content = str(byte_content, "utf-8")
        content = StringIO(str_content)
        csv = pd.read_csv(content)
    except UnicodeDecodeError:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid file type, file must be `CSV`.",
        )
    except ParserError:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid CSV file, could not process the content.",
        )
    records = csv.to_dict("records")
    return byte_content, records


@router_files.post("/", response_model=File)
async def create_file(file: UploadFile, s: Session = DepSession):
    file_content, _file_dict_record = await validate_csv_file(file)

    # parse file dict record ===========================
    for line in _file_dict_record:
        match line:
            case {"Data": data, "Valor": value, "Identificador": id, "Descrição": desc}:
                assert data
                assert value
                assert id
                assert desc

                desc: str
                type, _, entity = desc.partition("-")
                date = datetime.strptime(data, "%d/%m/%Y").date()

                _ = Transaction(
                    date=date,
                    value=value,
                    external_id=id,
                    entity=entity.strip(),
                    type=type.strip(),
                ).create(s)

            case _:
                print("not enough", line)
    # ==================================================

    new_record = File(name=str(file.filename), content=file_content).create(s)
    return new_record


@router_files.get("/all", response_model=list[File])
async def read_all_files(s: Session = DepSession):
    record_list = File.read_all(s)
    return record_list


@router_files.get("/{id}", response_model=File)
async def read_file(id: int | str, s: Session = DepSession):
    record = File.read(s, id)
    return record


@router_files.put("/", response_model=File)
async def update_file(record_update: FileUpdate, s: Session = DepSession):
    record = File.read(s, record_update.id).update(s, record_update)
    return record


@router_files.delete("/{id}", response_model=DeleteMSG)
async def delete_file(id: int, s: Session = DepSession):
    record = File.read(s, id).delete(s)
    return DeleteMSG(message="File deleted.", file=record)


@router_transactions.get("/all")
async def read_all_transactions(s: Session = DepSession):
    record = Transaction.read_all(s)
    return record

@router_transactions.post("/")
async def create_transaction(record: TransactionBase, s: Session = DepSession):
    record = Transaction.model_validate(record).create(s)
    return record


@router_transactions.get("/{id}")
async def read_transaction(id: int | str, s: Session = DepSession):
    record = Transaction.read(s, id)
    return record

@router_transactions.put("/")
async def update_transaction(record: TransactionUpdate, s: Session = DepSession):
    updated_record = Transaction.read(s, record.id).update(s, record)
    return updated_record


@router_transactions.delete("/{id}")
async def delete_transaction(id: int, s: Session= DepSession):
    record = Transaction.read(s, id).delete(s)
    return record
