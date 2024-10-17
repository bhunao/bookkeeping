from collections.abc import Generator
from datetime import date
from decimal import Decimal
from random import randint
from typing import Any

from fastapi.testclient import TestClient
from pytest import fixture
from sqlmodel import Session, create_engine

from src.main import app
from src.models import FileUpdate, Transaction, TransactionUpdate


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


engine = create_engine("sqlite:///test_bookkeeper.db")


@fixture
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides["get_session"] = get_session  # pyright: ignore[reportArgumentType]
    with TestClient(app) as client:
        yield client


file_name = "test_imaginary_file.csv"
file_content = "imaginary file content"


def upload_file(client: TestClient):
    global file_name, file_content
    files = {"file": (file_name, file_content, "text/plain")}
    response = client.post("/api/files/", files=files)
    return response


def test_upload_file(client: TestClient):
    global file_name, file_content
    response = upload_file(client)
    response_json: dict[Any, Any] = response.json()
    assert response.status_code == 200, response.text
    assert response_json.get("name") == file_name
    assert response_json.get("content") == file_content
    assert response_json.get("id")


def test_read_all_files(client: TestClient):
    response = upload_file(client)
    assert response.status_code == 200, response.text

    response2 = client.get("/api/files/all")
    response_json2: list[dict[Any, Any]] = response2.json()
    assert response2.status_code == 200, response2.text
    assert len(response_json2) > 0


def test_read_file(client: TestClient):
    response = upload_file(client)
    response_json: dict[Any, Any] = response.json()
    assert response.status_code == 200, response.text

    response = client.get(f"/api/files/{response_json["id"]}")
    assert response.status_code == 200, response.text


def test_rename_file(client: TestClient):
    uploaded_file_response = upload_file(client)
    uploaded_file: dict[Any, Any] = uploaded_file_response.json()
    novo_nome = "novo nome"
    assert uploaded_file.get("id")
    assert isinstance(uploaded_file["id"], int)
    file_update = FileUpdate(id=uploaded_file["id"], name=novo_nome)
    response = client.put("/api/files/", json=file_update.model_dump())
    response_json: dict[Any, Any] = response.json()
    assert response.status_code == 200, response.text
    assert response_json.get("name") == novo_nome


def test_delete_file(client: TestClient):
    uploaded_response = upload_file(client)
    uploaded_json: dict[Any, Any] = uploaded_response.json()
    response = client.delete(f"/api/files/{uploaded_json["id"]}")
    assert response.status_code == 200, response.text


def test_create_transaction(client: TestClient):
    new_record = dict(
        date=date.today().isoformat(),
        value=randint(0, 350),
        entity="bergamais",
        type="compra debito",
    )
    response = client.post("/api/transactions/", json=new_record)
    assert response.status_code == 200, response.text

    res_json: dict[str, Any] = response.json()
    assert res_json.get("date") == new_record["date"]
    assert float(res_json.get("value")) == float(new_record["value"])
    assert res_json.get("entity") == new_record["entity"]
    assert res_json.get("type") == new_record["type"]


def test_read_transaction(client: TestClient):
    new_record = dict(
        date=date.today().isoformat(),
        value=randint(0, 350),
        entity="bergamais",
        type="compra debito",
    )
    response = client.post("/api/transactions/", json=new_record)
    assert response.status_code == 200, response.text

    res_json: dict[str, Any] = response.json()
    response2 = client.get(f"/api/transactions/{res_json.get("id")}")
    assert response2.status_code == 200, response2.text

    res_json2: dict[str, Any] = response2.json()
    assert res_json2.get("date") == new_record["date"]
    assert float(res_json2.get("value")) == float(new_record["value"])
    assert res_json2.get("entity") == new_record["entity"]
    assert res_json2.get("type") == new_record["type"]


def test_update_transaction(client: TestClient):
    new_record = dict(
        date=date.today().isoformat(),
        value=randint(0, 350),
        entity="bergamais",
        type="compra debito",
    )
    response = client.post("/api/transactions/", json=new_record)
    assert response.status_code == 200, response.text

    res_json: dict[str, Any] = response.json()
    assert Transaction(**res_json)
    update_record = TransactionUpdate(id=res_json["id"], entity="treismais")
    response2 = client.put(
        "/api/transactions/", json=update_record.model_dump()
    )
    assert response2.status_code == 200, response2.text

    res_json2: dict[str, Any] = response2.json()
    assert res_json2.get("entity") == update_record.entity, response2.text


def test_delete_transaction(client: TestClient):
    new_record = dict(
        date=date.today().isoformat(),
        value=Decimal(randint(0, 350)),
        entity="bergamais",
        type="compra debito",
    )
    response = client.post("/api/transactions/", json=new_record)
    assert response.status_code == 200, response.text
    assert Transaction(**response.json())

    response2 = client.delete(f"/api/transactions/{res_json.get("id")}")
    assert response2.status_code == 200, response2.text
