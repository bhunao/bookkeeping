from fastapi import APIRouter, Depends, UploadFile
from sqlmodel import Session

from src.core import get_session
from src.models import File, DeleteMSG, FileUpdate


router = APIRouter(prefix="/api")

DepSession: Session = Depends(get_session)


@router.post("/")
async def create_file(file: UploadFile, s: Session = DepSession):
    new_record = File(file_name=str(file.filename), string_content="").create(s)
    return new_record


@router.get("/all")
async def get_all(s: Session = DepSession):
    record_list = File.read_all(s)
    return record_list


@router.put("/update")
async def update_file(new_record: FileUpdate, s: Session = DepSession):
    record = File.read(s, new_record.id).update(s, new_record)
    return record


@router.delete("/{id}", response_model=DeleteMSG)
async def delete_file(id: int, s: Session = DepSession):
    record = File.read(s, id).delete(s)
    return DeleteMSG(message="File deleted.", file=record)
