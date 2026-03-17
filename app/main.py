import os
import base64
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, Cookie, File, UploadFile
import shutil
import uuid
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

from . import models, database, auth
from .database import engine, get_db

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "royalthotel@gmail.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "abbosov0605.")

# Create DB tables
models.Base.metadata.create_all(bind=engine)

# Auto-migrate is_admin column for existing DBs (like on Vercel)
try:
    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE"))
except Exception as e:
    print(f"Migration error (could be SQLite or already exists): {e}")
    try:
        # Fallback for SQLite locally if needed
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE"))
    except:
        pass

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

    return templates.TemplateResponse("index.html", {"request": request, "user": user, "rooms": rooms, "admin_email": ADMIN_EMAIL})


@app.get("/hotel-in-tashkent", response_class=HTMLResponse)
async def hotel_in_tashkent_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    return templates.TemplateResponse("hotel_in_tashkent.html", {"request": request, "user": user, "admin_email": ADMIN_EMAIL})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    # Auto-create admin user if not exists
    admin_user = db.query(models.User).filter(models.User.email == ADMIN_EMAIL).first()
    if not admin_user:
        hashed_password = auth.get_password_hash(ADMIN_PASSWORD)
        new_admin = models.User(email=ADMIN_EMAIL, full_name="Admin", hashed_password=hashed_password, is_admin=True)
        db.add(new_admin)
        try:
            db.commit()
        except:
            db.rollback()
    else:
        admin_user.is_admin = True
        try:
            db.commit()
        except:
            db.rollback()
    
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

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
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True, max_age=2592000)
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
        return RedirectResponse(url="/register?error=2", status_code=status.HTTP_303_SEE_OTHER)
    
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
    is_admin = (getattr(user, 'is_admin', False) or (getattr(user, 'is_admin', False) or user.email == ADMIN_EMAIL)) 
    
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user, "bookings": bookings, "is_admin": is_admin, "admin_email": ADMIN_EMAIL})

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user or not getattr(user, 'is_admin', False) and not getattr(user, 'is_admin', False) and user.email != ADMIN_EMAIL:
        return RedirectResponse(url="/")
        
    rooms = db.query(models.Room).all()
    bookings = db.query(models.Booking).all()
    users = db.query(models.User).all()
    return templates.TemplateResponse("admin.html", {"request": request, "user": user, "rooms": rooms, "bookings": bookings, "users": users, "admin_email": ADMIN_EMAIL})

@app.post("/admin/room/add")
async def admin_add_room(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    price_per_night: float = Form(...),
    image: UploadFile = File(None),
    image_url: str = Form(""),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user or not getattr(user, 'is_admin', False) and not getattr(user, 'is_admin', False) and user.email != ADMIN_EMAIL:
        return RedirectResponse(url="/")
        
    final_image_url = image_url if image_url else "/static/images/room1.jpg"
    
    if image and image.filename:
        contents = await image.read()
        if len(contents) <= 5 * 1024 * 1024:  # up to 5MB
            ext = image.filename.split('.')[-1].lower()
            mime = "image/png" if ext == "png" else "image/webp" if ext == "webp" else "image/jpeg"
            encoded = base64.b64encode(contents).decode('utf-8')
            final_image_url = f"data:{mime};base64,{encoded}"
        else:
            print("File too large for Base64 Vercel encoding")

    new_room = models.Room(name=name, description=description, price_per_night=price_per_night, image_url=final_image_url)
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
    if not user or not getattr(user, 'is_admin', False) and not getattr(user, 'is_admin', False) and user.email != ADMIN_EMAIL:
        return RedirectResponse(url="/")
        
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if room:
        # First delete associated bookings
        db.query(models.Booking).filter(models.Booking.room_id == room.id).delete()
        db.delete(room)
        db.commit()
        
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)




@app.post("/admin/booking/delete/{booking_id}")
async def admin_delete_booking(
    request: Request,
    booking_id: int,
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user or not getattr(user, 'is_admin', False) and not getattr(user, 'is_admin', False) and user.email != ADMIN_EMAIL:
        return RedirectResponse(url="/")
        
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if booking:
        db.delete(booking)
        db.commit()
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/user/delete/{user_id}")
async def admin_delete_user(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user or not getattr(user, 'is_admin', False) and not getattr(user, 'is_admin', False) and user.email != ADMIN_EMAIL:
        return RedirectResponse(url="/")
        
    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    if target_user and target_user.email != ADMIN_EMAIL:
        db.query(models.Booking).filter(models.Booking.user_id == target_user.id).delete()
        db.delete(target_user)
        db.commit()
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/admin/room/edit/{room_id}")
async def admin_edit_room(
    request: Request,
    room_id: int,
    name: str = Form(...),
    description: str = Form(...),
    price_per_night: float = Form(...),
    image: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user or not getattr(user, 'is_admin', False) and not getattr(user, 'is_admin', False) and user.email != ADMIN_EMAIL:
        return RedirectResponse(url="/")
        
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if room:
        room.name = name
        room.description = description
        room.price_per_night = price_per_night
        
        if image and image.filename:
            contents = await image.read()
            if len(contents) <= 5 * 1024 * 1024:
                ext = image.filename.split('.')[-1].lower()
                mime = "image/png" if ext == "png" else "image/webp" if ext == "webp" else "image/jpeg"
                encoded = base64.b64encode(contents).decode('utf-8')
                room.image_url = f"data:{mime};base64,{encoded}"
            else:
                pass
        db.commit()
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/dashboard/booking/cancel/{booking_id}")
async def dashboard_cancel_booking(
    request: Request,
    booking_id: int,
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
        
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id, models.Booking.user_id == user.id).first()
    if booking:
        db.delete(booking)
        db.commit()
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/dashboard/booking/reschedule/{booking_id}")
async def dashboard_reschedule_booking(
    request: Request,
    booking_id: int,
    new_check_in: str = Form(...),
    new_check_out: str = Form(...),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
        
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id, models.Booking.user_id == user.id).first()
    if booking:
        try:
            in_d = datetime.strptime(new_check_in, "%Y-%m-%d")
            out_d = datetime.strptime(new_check_out, "%Y-%m-%d")
            if out_d > in_d:
                booking.check_in_date = in_d
                booking.check_out_date = out_d
                days = (out_d - in_d).days
                booking.total_price = days * booking.room.price_per_night
                db.commit()
        except: pass
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/admin/settings")
async def admin_settings(
    request: Request,
    email: str = Form(...),
    new_password: str = Form(""),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user or not (getattr(user, "is_admin", False) or (getattr(user, 'is_admin', False) or user.email == ADMIN_EMAIL)):
        return RedirectResponse(url="/")
        
    user.email = email
    if new_password:
        user.hashed_password = auth.get_password_hash(new_password)
    user.is_admin = True
    db.commit()
    
    from datetime import timedelta
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True, max_age=2592000)
    return response
