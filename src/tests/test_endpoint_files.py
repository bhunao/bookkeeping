from collections.abc import Generator
from typing import Any
from pytest import fixture
from fastapi.testclient import TestClient

from src.main import app
from src.models import FileUpdate


@fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client


file_name = "test_imaginary_file.csv"
file_content = "imaginary file content"


def upload_file(client: TestClient):
    global file_name
    global file_content
    files = {"file": (file_name, file_content, "text/plain")}
    response = client.post("/api/", files=files)
    return response


def test_upload_file(client: TestClient):
    global file_name
    global file_content
    response = upload_file(client)
    response_json: dict[Any, Any] = response.json()
    assert response.status_code == 200
    assert response_json.get("name") == file_name
    assert response_json.get("content") == file_content
    assert response_json.get("id")


def test_rename_file(client: TestClient):
    uploaded_file_response = upload_file(client)
    uploaded_file: dict[Any, Any] = uploaded_file_response.json()
    novo_nome = "novo nome"
    file_update = FileUpdate(id=uploaded_file["id"], name=novo_nome)
    response = client.put("/api/", json=file_update.model_dump())
    response_json: dict[Any, Any] = response.json()
    assert response.status_code == 200
    assert response_json.get("name") == novo_nome
