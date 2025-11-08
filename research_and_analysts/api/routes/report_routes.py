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

@router.post("/login", response_class=HTMLResponse)
async def login(request:Request, username:str = Form(...), password:str = Form(...)):
    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()

    if user and verify_password(password, user.password):
        session_id = f"{username}_session"
        SESSION[session_id] = username
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(key="session_id", value="session_id")
        return response
    return request.app.templates.TemplateResponse(
        "login.html",
        {"request":request, "error":"Invalid username or password"}
    )