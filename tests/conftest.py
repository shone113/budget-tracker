import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app import models  # noqa: F401
from app.core.config import settings
from app.db.session import Base, get_db
from app.main import app

engine = create_engine(settings.test_database_url)
TestingSession = sessionmaker(bind=engine, autoflush=False)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def clean_tables():
    yield
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE transactions, budgets, categories RESTART IDENTITY CASCADE"))


@pytest.fixture
def client():
    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def create_category(client, name, color="#123456"):
    return client.post("/categories", json={"name": name, "color": color}).json()["id"]


def create_transaction(client, type, amount, date, category_id, description=None):
    response = client.post("/transactions", json={
        "type": type, "amount": amount, "date": date,
        "category_id": category_id, "description": description,
    })
    assert response.status_code == 201
    return response.json()


def create_budget(client, category_id, month, amount):
    response = client.post("/budgets", json={"category_id": category_id, "month": month, "amount": amount})
    assert response.status_code == 201
    return response.json()