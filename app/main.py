import os
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime

from . import models, database, auth
from .database import engine, get_db

# Create DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Royal Tashkent Hotel")

# Получаем абсолютный путь к текущей директории (app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


def get_current_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        from jose import jwt
        payload = jwt.decode(token.replace("Bearer ", ""), auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        user = db.query(models.User).filter(models.User.email == email).first()
        return user
    except:
        return None


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    rooms = db.query(models.Room).all()
    
    # Init some rooms if empty (for demo)
    if not rooms:
        demo_rooms = [
            models.Room(name="Deluxe Oasis", description="Plush king-size bed, city view.", price_per_night=120, image_url="/static/images/room1.jpg"),
            models.Room(name="Executive Suite", description="Panoramic views, exclusive lounge access.", price_per_night=250, image_url="/static/images/room2.jpg"),
            models.Room(name="Royal Penthouse", description="Ultimate luxury. Private terrace, jacuzzi.", price_per_night=800, image_url="/static/images/room3.jpg"),
        ]
        db.add_all(demo_rooms)
        db.commit()
        rooms = db.query(models.Room).all()

    return templates.TemplateResponse("index.html", {"request": request, "user": user, "rooms": rooms})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login_post(
    response: RedirectResponse,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not auth.verify_password(password, user.hashed_password):
        # Simply return template with error for simplicity
        return RedirectResponse(url="/login?error=1", status_code=status.HTTP_303_SEE_OTHER)
    
    access_token = auth.create_access_token(data={"sub": user.email})
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@app.post("/register")
async def register_post(
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.email == email).first()
    if db_user:
        return RedirectResponse(url="/login?error=2", status_code=status.HTTP_303_SEE_OTHER)
    
    hashed_password = auth.get_password_hash(password)
    new_user = models.User(email=email, full_name=full_name, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return RedirectResponse(url="/login?registered=1", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response

@app.post("/book/{room_id}")
async def book_room(
    request: Request,
    room_id: int,
    check_in: str = Form(...),
    check_out: str = Form(...),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
        
    try:
        in_date = datetime.strptime(check_in, "%Y-%m-%d")
        out_date = datetime.strptime(check_out, "%Y-%m-%d")
        days = (out_date - in_date).days
        if days < 1: days = 1
        total_price = days * room.price_per_night
    except:
        return RedirectResponse(url="/?error=invalid_dates", status_code=status.HTTP_303_SEE_OTHER)

    new_booking = models.Booking(
        user_id=user.id,
        room_id=room.id,
        check_in_date=in_date,
        check_out_date=out_date,
        total_price=total_price
    )
    db.add(new_booking)
    db.commit()
    
    return RedirectResponse(url="/dashboard?success=booked", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
    
    bookings = db.query(models.Booking).filter(models.Booking.user_id == user.id).all()
    # Simple check if current user is admin
    is_admin = user.email == "admin@royaltashkent.com" 
    
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "bookings": bookings, "is_admin": is_admin})

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or user.email != "admin@royaltashkent.com":
        return RedirectResponse(url="/")
        
    rooms = db.query(models.Room).all()
    bookings = db.query(models.Booking).all()
    return templates.TemplateResponse("admin.html", {"request": request, "user": user, "rooms": rooms, "bookings": bookings})

@app.post("/admin/room/add")
async def admin_add_room(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    price_per_night: float = Form(...),
    image_url: str = Form(...),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user or user.email != "admin@royaltashkent.com":
        return RedirectResponse(url="/")
        
    new_room = models.Room(name=name, description=description, price_per_night=price_per_night, image_url=image_url)
    db.add(new_room)
    db.commit()
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/room/delete/{room_id}")
async def admin_delete_room(
    request: Request,
    room_id: int,
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user or user.email != "admin@royaltashkent.com":
        return RedirectResponse(url="/")
        
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if room:
        # First delete associated bookings
        db.query(models.Booking).filter(models.Booking.room_id == room.id).delete()
        db.delete(room)
        db.commit()
        
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


