from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db

from app.core.error_handlers import register_error_handlers

from app.api.routes import categories

app = FastAPI(title=settings.app_name)
register_error_handlers(app)
app.include_router(categories.router)         

@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}