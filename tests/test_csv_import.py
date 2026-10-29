from app.services import transaction_import
from tests.conftest import create_category

HEADER = "type,amount,date,description,category\n"


def upload(client, content, filename="transactions.csv"):
    return client.post("/transactions/import", files={"file": (filename, content.encode(), "text/csv")})


def get_transactions(client):
    return client.get("/transactions").json()["items"]


def test_import_example_from_specification(client):
    create_category(client, "Eating out")
    create_category(client, "Other")
    content = HEADER + (
        "expense,12.50,2026-10-08,Lunch,Eating out\n"
        "income,300.00,2026-10-09,,Other\n"
    )

    response = upload(client, content)

    assert response.status_code == 200
    assert response.json() == {"imported": 2, "failed": []}
    assert len(get_transactions(client)) == 2


def test_empty_description_means_no_description(client):
    create_category(client, "Other")

    upload(client, HEADER + "income,300.00,2026-10-09,,Other\n")

    assert get_transactions(client)[0]["description"] is None


def test_category_name_ignores_case(client):
    create_category(client, "Eating out")

    response = upload(client, HEADER + "expense,12.50,2026-10-08,Lunch,eATING OUT\n")

    assert response.json()["imported"] == 1


def test_invalid_rows_are_reported_and_valid_rows_are_imported(client):
    create_category(client, "Food")
    content = HEADER + (
        "expense,10.00,2026-10-01,Valid,Food\n"
        "expense,0,2026-10-01,Zero amount,Food\n"
        "other,10.00,2026-10-01,Wrong type,Food\n"
        "expense,10.00,2026-13-01,Wrong date,Food\n"
        "expense,10.00,2026-10-01,Unknown category,Travel\n"
        "income,20.00,2026-10-02,Valid,food\n"
    )

    response = upload(client, content)
    result = response.json()

    assert response.status_code == 200
    assert result["imported"] == 2
    assert [row["row"] for row in result["failed"]] == [3, 4, 5, 6]
    assert result["failed"][0]["errors"][0].startswith("amount:")
    assert result["failed"][1]["errors"][0].startswith("type:")
    assert result["failed"][2]["errors"][0].startswith("date:")
    assert result["failed"][3]["errors"][0].startswith("category:")
    assert len(get_transactions(client)) == 2


def test_invalid_header_is_rejected(client):
    create_category(client, "Food")

    response = upload(client, "type,amount,date,category\nexpense,10.00,2026-10-01,Food\n")

    assert response.status_code == 422
    assert get_transactions(client) == []


def test_file_with_too_many_rows_is_rejected(client, monkeypatch):
    monkeypatch.setattr(transaction_import, "MAX_ROWS", 2)
    create_category(client, "Food")
    content = HEADER + "expense,10.00,2026-10-01,,Food\n" * 3

    response = upload(client, content)

    assert response.status_code == 422
    assert get_transactions(client) == []


def test_file_with_max_rows_is_imported(client, monkeypatch):
    monkeypatch.setattr(transaction_import, "MAX_ROWS", 2)
    create_category(client, "Food")
    content = HEADER + "expense,10.00,2026-10-01,,Food\n" * 2

    response = upload(client, content)

    assert response.json()["imported"] == 2