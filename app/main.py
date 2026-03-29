from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os

from app.api.routes import auth, email
from app.db.init_db import init_db
from app.db.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.email import Email

from app.core.security import (
    verify_password,
    create_access_token,
    hash_password
)



app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

templates = Jinja2Templates(
    directory=os.path.join(BASE_DIR, "templates")
)
templates.env.cache = {}


init_db()


app.include_router(auth.router)
app.include_router(email.router)




@app.get("/")
def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {}
    )


@app.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Invalid email or password"}
        )

    token = create_access_token(str(user.id))

    response = RedirectResponse("/inbox", status_code=303)
    response.set_cookie(
    "access_token",
    token,
    httponly=True,
    samesite="lax",   
    secure=False      
)

    return response


@app.get("/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("access_token")
    return response




@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        request,
        "register.html",
        {}
    )



@app.get("/inbox")
def inbox(request: Request, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):
    

    return templates.TemplateResponse(
        request,
        "inbox.html",
        {"user": current_user}
    )


@app.get("/send")
def send_page(request: Request, db: Session = Depends(get_db),current_user: User = Depends(get_current_user)):

    return templates.TemplateResponse(
        request,
        "send.html",
        {"user": current_user}
    )



@app.get("/spam")
def spam_page(request: Request):

    return templates.TemplateResponse(
        request,
        "spam.html",
        {}
    )




@app.exception_handler(404)
def not_found(request: Request, exc):
    return templates.TemplateResponse(
        request,
        "404.html",
        {"message": "Page not found"},
        status_code=404
    )

@app.exception_handler(403)
def forbidden(request: Request, exc):
    return templates.TemplateResponse(
        request,
        "403.html",
        {"message": "Access forbidden"},
        status_code=403
    )

@app.exception_handler(500)
def server_error(request: Request, exc):
    return templates.TemplateResponse(
        request,
        "500.html",
        {"message": "Internal server error"},
        status_code=500
    )
    
@app.exception_handler(HTTPException)
def auth_exception_handler(request: Request, exc: HTTPException):

    if exc.status_code == 401:
        # HTMX or browser → redirect
        if "text/html" in request.headers.get("accept", ""):
            return RedirectResponse("/", status_code=303)

    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )