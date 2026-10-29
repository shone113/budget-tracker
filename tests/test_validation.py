import pytest

from tests.conftest import create_budget, create_category


@pytest.mark.parametrize("data", [
    {"name": "", "color": "#123456"},
    {"name": "   ", "color": "#123456"},
    {"name": "a" * 31, "color": "#123456"},
    {"name": "Food", "color": "red"},
    {"name": "Food", "color": "#12345"},
    {"color": "#123456"},
    {"name": "Food"},
])
def test_create_category_invalid(client, data):
    assert client.post("/categories", json=data).status_code == 422


def test_category_name_is_unique_ignoring_case(client):
    create_category(client, "Food")
    response = client.post("/categories", json={"name": "fOOd", "color": "#123456"})
    assert response.status_code == 409



VALID_TRANSACTION = {"type": "expense", "amount": "12.50", "date": "2026-10-08", "description": "Lunch"}


@pytest.mark.parametrize("field, value", [
    ("type", "other"),
    ("amount", "0"),
    ("amount", "-5"),
    ("amount", "1000000.01"),
    ("amount", "12.555"),
    ("amount", "abc"),
    ("date", "2026-13-01"),
    ("date", "08.10.2026"),
    ("description", "a" * 201),
])
def test_create_transaction_invalid(client, field, value):
    category_id = create_category(client, "Food")
    data = VALID_TRANSACTION | {"category_id": category_id, field: value}
    assert client.post("/transactions", json=data).status_code == 422


@pytest.mark.parametrize("field", ["type", "amount", "date", "category_id"])
def test_create_transaction_missing_required_field(client, field):
    category_id = create_category(client, "Food")
    data = VALID_TRANSACTION | {"category_id": category_id}
    del data[field]
    assert client.post("/transactions", json=data).status_code == 422


def test_create_transaction_category_must_exist(client):
    data = VALID_TRANSACTION | {"category_id": 999}
    assert client.post("/transactions", json=data).status_code == 422


@pytest.mark.parametrize("amount", ["0.01", "1000000", "12.5"])
def test_create_transaction_amount_limits_are_allowed(client, amount):
    category_id = create_category(client, "Food")
    data = VALID_TRANSACTION | {"category_id": category_id, "amount": amount}
    assert client.post("/transactions", json=data).status_code == 201



@pytest.mark.parametrize("field, value", [
    ("month", "2026-13"),
    ("month", "2026-10-01"),
    ("month", "10-2026"),
    ("amount", "0"),
    ("amount", "12.555"),
    ("amount", "1000000.01"),
])
def test_create_budget_invalid(client, field, value):
    category_id = create_category(client, "Food")
    data = {"category_id": category_id, "month": "2026-10", "amount": "100"} | {field: value}
    assert client.post("/budgets", json=data).status_code == 422


def test_create_budget_category_must_exist(client):
    data = {"category_id": 999, "month": "2026-10", "amount": "100"}
    assert client.post("/budgets", json=data).status_code == 422


def test_category_has_at_most_one_budget_per_month(client):
    category_id = create_category(client, "Food")
    create_budget(client, category_id, "2026-10", "100")
    response = client.post("/budgets", json={"category_id": category_id, "month": "2026-10", "amount": "200"})
    assert response.status_code == 409


def test_deleting_category_deletes_its_budgets(client):
    category_id = create_category(client, "Food")
    create_budget(client, category_id, "2026-10", "100")
    client.delete(f"/categories/{category_id}")
    assert client.get("/budgets?month=2026-10").json() == []