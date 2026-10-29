from tests.conftest import create_budget, create_category, create_transaction


def test_empty_month(client):
    response = client.get("/summary?month=2026-10")

    assert response.status_code == 200
    assert response.json() == {
        "month": "2026-10",
        "total_income": "0.00",
        "total_expense": "0.00",
        "balance": "0.00",
        "categories": [],
    }


def test_totals_and_balance(client):
    salary = create_category(client, "Salary")
    food = create_category(client, "Food")
    create_transaction(client, "income", "1000", "2026-10-01", salary)
    create_transaction(client, "expense", "300", "2026-10-15", food)
    create_transaction(client, "expense", "200", "2026-10-31", food)

    summary = client.get("/summary?month=2026-10").json()

    assert summary["total_income"] == "1000.00"
    assert summary["total_expense"] == "500.00"
    assert summary["balance"] == "500.00"


def test_balance_can_be_negative(client):
    food = create_category(client, "Food")
    create_transaction(client, "expense", "50", "2026-10-10", food)

    summary = client.get("/summary?month=2026-10").json()

    assert summary["balance"] == "-50.00"


def test_only_transactions_from_that_month_are_counted(client):
    food = create_category(client, "Food")
    create_transaction(client, "expense", "10", "2026-09-30", food)
    create_transaction(client, "expense", "20", "2026-10-01", food)
    create_transaction(client, "expense", "40", "2026-11-01", food)

    summary = client.get("/summary?month=2026-10").json()

    assert summary["total_expense"] == "20.00"


def test_categories_spent_budget_and_left(client):
    food = create_category(client, "Food")
    transport = create_category(client, "Transport")
    health = create_category(client, "Health")
    create_transaction(client, "expense", "120", "2026-10-05", food)
    create_transaction(client, "expense", "30", "2026-10-06", transport)
    create_budget(client, food, "2026-10", "100")
    create_budget(client, health, "2026-10", "50")

    categories = client.get("/summary?month=2026-10").json()["categories"]

    assert categories == [
        {"category_id": food, "name": "Food", "spent": "120.00", "budget": "100.00", "left": "-20.00"},
        {"category_id": transport, "name": "Transport", "spent": "30.00", "budget": None, "left": None},
        {"category_id": health, "name": "Health", "spent": "0.00", "budget": "50.00", "left": "50.00"},
    ]


def test_categories_without_expense_or_budget_are_not_shown(client):
    salary = create_category(client, "Salary")
    create_category(client, "Unused")
    food = create_category(client, "Food")
    create_transaction(client, "income", "1000", "2026-10-01", salary)
    create_budget(client, food, "2026-11", "100")

    summary = client.get("/summary?month=2026-10").json()

    assert summary["categories"] == []


def test_categories_sorted_by_highest_expense_then_by_name(client):
    for name, amount in [("Books", "10"), ("Groceries", "60"), ("Eating out", "60"), ("Taxi", "90")]:
        category_id = create_category(client, name)
        create_transaction(client, "expense", amount, "2026-10-10", category_id)

    categories = client.get("/summary?month=2026-10").json()["categories"]

    assert [c["name"] for c in categories] == ["Taxi", "Eating out", "Groceries", "Books"]


def test_invalid_month(client):
    assert client.get("/summary?month=2026-13").status_code == 422
    assert client.get("/summary").status_code == 422