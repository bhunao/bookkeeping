from io import StringIO
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from pandas.errors import ParserError
from sqlmodel import Session

from src.core import get_session
from src.models import DeleteMSG, File, FileUpdate
import pandas as pd

router = APIRouter(prefix="/api")

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


@router.post("/", response_model=File)
async def create_file(file: UploadFile, s: Session = DepSession):
    file_content, _file_dict_record = await validate_csv_file(file)

    # parse file dict record
    for line in _file_dict_record:
        match line:
            case {"Data": data, "Valor": valor, "Identificador": id, "Descrição": desc}:
                assert data
                assert valor
                assert id
                assert desc
                pass
            case _:
                print("not enough", line)

    new_record = File(name=str(file.filename), content=file_content).create(s)
    return new_record


@router.get("/{id}", response_model=File)
async def read_file(id: int | str, s: Session = DepSession):
    record = File.read(s, id)
    return record


@router.get("/all", response_model=list[File])
async def read_all_files(s: Session = DepSession):
    record_list = File.read_all(s)
    return record_list


@router.put("/", response_model=File)
async def update_file(record_update: FileUpdate, s: Session = DepSession):
    record = File.read(s, record_update.id).update(s, record_update)
    return record


@router.delete("/{id}", response_model=DeleteMSG)
async def delete_file(id: int, s: Session = DepSession):
    record = File.read(s, id).delete(s)
    return DeleteMSG(message="File deleted.", file=record)