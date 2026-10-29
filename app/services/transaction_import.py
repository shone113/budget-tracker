import csv
import io

from pydantic import ValidationError
from sqlalchemy import insert, select
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError
from app.models import Category, Transaction
from app.schemas.transaction_import import ImportRowError, TransactionImportResponse, TransactionImportRow

MAX_ROWS = 1_000_000
BATCH_SIZE = 5_000
COLUMNS = ["type", "amount", "date", "description", "category"]

def import_transactions(db: Session, file) -> TransactionImportResponse:
    categories = {name.lower(): id for id, name in db.execute(select(Category.id, Category.name))}
    text = io.TextIOWrapper(file, encoding="utf-8-sig", newline="")

    imported = 0
    failed = []
    batch = []

    try:
        row_count = sum(1 for row in csv.reader(text) if row) - 1
        if row_count > MAX_ROWS:
            raise BusinessRuleError(f"The file can have at most {MAX_ROWS} rows.")
        text.seek(0)

        reader = csv.DictReader(text)
        if reader.fieldnames != COLUMNS:
            raise BusinessRuleError(f"The first row must be: {','.join(COLUMNS)}")

        for row in reader:
            if None in row:
                failed.append(ImportRowError(row=reader.line_num, errors=["Too many columns."]))
                continue

            try:
                data = TransactionImportRow(**{key: (value or "").strip() for key, value in row.items()})
            except ValidationError as e:
                errors = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
                failed.append(ImportRowError(row=reader.line_num, errors=errors))
                continue

            category_id = categories.get(data.category.lower())
            if category_id is None:
                failed.append(ImportRowError(row=reader.line_num, errors=[f"category: '{data.category}' does not exist"]))
                continue

            batch.append(data.model_dump(exclude={"category"}) | {"category_id": category_id})
            if len(batch) == BATCH_SIZE:
                db.execute(insert(Transaction), batch)
                imported += len(batch)
                batch = []

    except UnicodeDecodeError:
        raise BusinessRuleError("The file must be UTF-8 encoded.")

    if batch:
        db.execute(insert(Transaction), batch)
        imported += len(batch)

    db.commit()
    return TransactionImportResponse(imported=imported, failed=failed)