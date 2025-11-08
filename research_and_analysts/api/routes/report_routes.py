from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from research_and_analysts.api.services.report_service import ReportService
from research_and_analysts.database.db_config import SessionLocal, User, hash_password, verify_password

router = APIRouter()
SESSION = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_class=HTMLResponse)
async def show_login(request:Request):
    return request.app.templates.TemplateResponse("login.html",{"request":request})