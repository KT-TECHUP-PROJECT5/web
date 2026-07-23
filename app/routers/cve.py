from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.common.auth import get_current_user
from app.core.database import get_db
BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")

router = APIRouter()


@router.get("/cve")
def cve_page(request: Request, db: Session = Depends(get_db)):
    legacy_file = PROJECT_DIR / "requirements-legacy.txt"
    dependencies = [
        line.strip()
        for line in legacy_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
    return templates.TemplateResponse(
        request,
        "cve.html",
        {"user": get_current_user(request, db), "dependencies": dependencies},
    )
