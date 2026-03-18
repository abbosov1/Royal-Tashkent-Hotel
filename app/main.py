import os
import base64
from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, File, UploadFile, BackgroundTasks
import uuid
import json
from typing import List
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage

from . import models, database, auth
from .database import engine, get_db

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "").strip()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "").strip()

SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", os.getenv("MAIL_USERNAME", ""))
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", os.getenv("MAIL_PASSWORD", ""))
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER or "no-reply@royaltashkent.local")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
EMAIL_INLINE_SEND = os.getenv("EMAIL_INLINE_SEND", "").lower() == "true"
CODE_ATTEMPT_LIMIT = 6

LOYALTY_TIERS = [
    ("Bronze", 0),
    ("Silver", 250),
    ("Gold", 600),
    ("Platinum", 1200),
]

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

# Auto-migrate booking/user feature columns for existing DBs
MIGRATIONS = [
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS loyalty_points INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_code VARCHAR",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_expires_at TIMESTAMP",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verification_attempts INTEGER DEFAULT 0",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_code VARCHAR",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_expires_at TIMESTAMP",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_attempts INTEGER DEFAULT 0",
    "ALTER TABLE bookings ADD COLUMN IF NOT EXISTS guest_count INTEGER DEFAULT 1",
    "ALTER TABLE bookings ADD COLUMN IF NOT EXISTS promo_code VARCHAR",
    "ALTER TABLE bookings ADD COLUMN IF NOT EXISTS discount_percent FLOAT DEFAULT 0",
    "ALTER TABLE bookings ADD COLUMN IF NOT EXISTS needs_transfer BOOLEAN DEFAULT FALSE",
    "ALTER TABLE bookings ADD COLUMN IF NOT EXISTS special_request VARCHAR",
    "ALTER TABLE bookings ADD COLUMN IF NOT EXISTS booking_reference VARCHAR",
    "ALTER TABLE bookings ADD COLUMN IF NOT EXISTS payment_status VARCHAR DEFAULT 'pending'",
    "ALTER TABLE bookings ADD COLUMN IF NOT EXISTS payment_reference VARCHAR",
    "ALTER TABLE bookings ADD COLUMN IF NOT EXISTS paid_at TIMESTAMP",
    "ALTER TABLE rooms ADD COLUMN IF NOT EXISTS image_gallery VARCHAR",
    "ALTER TABLE rooms ADD COLUMN IF NOT EXISTS amenities VARCHAR",
    "CREATE UNIQUE INDEX IF NOT EXISTS ix_bookings_booking_reference ON bookings (booking_reference)",
]

for migration_sql in MIGRATIONS:
    try:
        with engine.begin() as conn:
            conn.execute(text(migration_sql))
    except Exception:
        try:
            if "IF NOT EXISTS" in migration_sql:
                sqlite_sql = migration_sql.replace(" IF NOT EXISTS", "")
                with engine.begin() as conn:
                    conn.execute(text(sqlite_sql))
        except Exception:
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


def normalize_promo_code(raw_code: str) -> str:
    return (raw_code or "").strip().upper()


def get_discount_percent(db: Session, promo_code: str) -> int:
    normalized = normalize_promo_code(promo_code)
    if not normalized:
        return 0
    promo = (
        db.query(models.PromoCode)
        .filter(models.PromoCode.code == normalized, models.PromoCode.is_active == True)
        .first()
    )
    if not promo:
        return 0
    return int(promo.discount_percent or 0)


def is_admin_user(user: models.User | None) -> bool:
    return bool(user and getattr(user, "is_admin", False))


def loyalty_tier(points: int) -> str:
    current_tier = LOYALTY_TIERS[0][0]
    for tier_name, threshold in LOYALTY_TIERS:
        if points >= threshold:
            current_tier = tier_name
    return current_tier


def upload_to_data_url(upload_file: UploadFile | None) -> str | None:
    if not upload_file or not upload_file.filename:
        return None
    ext = upload_file.filename.split('.')[-1].lower()
    mime = "image/png" if ext == "png" else "image/webp" if ext == "webp" else "image/jpeg"
    return mime


async def encode_upload_image(upload_file: UploadFile | None) -> str | None:
    mime = upload_to_data_url(upload_file)
    if not mime:
        return None
    contents = await upload_file.read()
    if len(contents) > 5 * 1024 * 1024:
        return None
    encoded = base64.b64encode(contents).decode('utf-8')
    return f"data:{mime};base64,{encoded}"


def normalize_room_gallery(main_image_url: str, existing_gallery_raw: str | None = None) -> list[str]:
    images: list[str] = []
    if main_image_url:
        images.append(main_image_url)

    if existing_gallery_raw:
        try:
            parsed = json.loads(existing_gallery_raw)
            if isinstance(parsed, list):
                images.extend([str(item).strip() for item in parsed if str(item).strip()])
        except Exception:
            pass

    deduped: list[str] = []
    seen = set()
    for image in images:
        if image not in seen:
            deduped.append(image)
            seen.add(image)
    return deduped[:6]


def normalize_amenities(raw: str | None) -> str:
    return ", ".join([item.strip() for item in (raw or "").split(",") if item.strip()])


def generate_verification_code() -> str:
    # 6-digit code for email verification flow.
    return str(uuid.uuid4().int)[-6:]


def send_email(to_email: str, subject: str, body: str, html_body: str | None = None) -> None:
    smtp_host = (SMTP_HOST or "").strip()
    smtp_user = (SMTP_USER or "").strip()
    smtp_password = (SMTP_PASSWORD or "").replace(" ", "")

    if not smtp_host or not smtp_user or not smtp_password:
        missing = []
        if not smtp_host:
            missing.append("SMTP_HOST")
        if not smtp_user:
            missing.append("SMTP_USER/MAIL_USERNAME")
        if not smtp_password:
            missing.append("SMTP_PASSWORD/MAIL_PASSWORD")
        print(f"Email skipped: SMTP is not configured (missing: {', '.join(missing)})")
        return

    try:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = SMTP_FROM
        message["To"] = to_email
        message.set_content(body)
        if html_body:
            message.add_alternative(html_body, subtype="html")

        errors = []

        # Try configured mode first, then fallback to maximize delivery on restrictive hosts.
        try_modes = []
        preferred_mode = "ssl" if SMTP_PORT == 465 and not SMTP_USE_TLS else "tls"
        try_modes.append(preferred_mode)
        if preferred_mode == "tls":
            try_modes.append("ssl")
        else:
            try_modes.append("tls")

        for mode in try_modes:
            try:
                if mode == "ssl":
                    ssl_port = 465 if SMTP_PORT == 587 else SMTP_PORT
                    with smtplib.SMTP_SSL(smtp_host, ssl_port, timeout=10) as server:
                        server.login(smtp_user, smtp_password)
                        server.send_message(message)
                else:
                    with smtplib.SMTP(smtp_host, SMTP_PORT, timeout=10) as server:
                        server.ehlo()
                        server.starttls()
                        server.ehlo()
                        server.login(smtp_user, smtp_password)
                        server.send_message(message)

                print(f"Email sent successfully to {to_email} via {mode.upper()}")
                return
            except Exception as exc:
                errors.append(f"{mode.upper()}: {exc}")

        print(f"Email send failed to {to_email}: {' | '.join(errors)}")
    except Exception as exc:
        print(f"Email build/send unexpected failure to {to_email}: {exc}")


def dispatch_email(
    background_tasks: BackgroundTasks,
    to_email: str,
    subject: str,
    body: str,
    html_body: str | None = None,
) -> None:
    # Use inline mode only when explicitly enabled; never let email failures crash requests.
    if EMAIL_INLINE_SEND:
        try:
            send_email(to_email, subject, body, html_body)
        except Exception as exc:
            print(f"Inline email dispatch failed for {to_email}: {exc}")
        return
    background_tasks.add_task(send_email, to_email, subject, body, html_body)


def queue_booking_email(background_tasks: BackgroundTasks, user: models.User, booking: models.Booking, room: models.Room):
    subject = f"Booking Confirmed: {booking.booking_reference or booking.id}"
    body = (
        f"Hello {user.full_name},\n\n"
        f"Your booking has been created successfully.\n\n"
        f"Room: {room.name}\n"
        f"Booking reference: {booking.booking_reference or booking.id}\n"
        f"Check-in: {booking.check_in_date.strftime('%Y-%m-%d')}\n"
        f"Check-out: {booking.check_out_date.strftime('%Y-%m-%d')}\n"
        f"Total: ${booking.total_price}\n"
        f"Payment status: {booking.payment_status}\n\n"
        f"Thank you for choosing Royal Tashkent Hotel."
    )
    html_body = f"""
        <html><body style='font-family:Arial,sans-serif;background:#f8f6f2;padding:20px;'>
            <div style='max-width:620px;margin:0 auto;background:#ffffff;border:1px solid #eadfce;border-radius:12px;padding:20px;'>
                <h2 style='margin-top:0;color:#5f3b1d;'>Booking Confirmed</h2>
                <p>Hello <strong>{user.full_name}</strong>, your booking is confirmed.</p>
                <table style='width:100%;border-collapse:collapse;'>
                    <tr><td style='padding:8px;border-bottom:1px solid #eee;'>Room</td><td style='padding:8px;border-bottom:1px solid #eee;'><strong>{room.name}</strong></td></tr>
                    <tr><td style='padding:8px;border-bottom:1px solid #eee;'>Reference</td><td style='padding:8px;border-bottom:1px solid #eee;'><strong>{booking.booking_reference or booking.id}</strong></td></tr>
                    <tr><td style='padding:8px;border-bottom:1px solid #eee;'>Check-in</td><td style='padding:8px;border-bottom:1px solid #eee;'>{booking.check_in_date.strftime('%Y-%m-%d')}</td></tr>
                    <tr><td style='padding:8px;border-bottom:1px solid #eee;'>Check-out</td><td style='padding:8px;border-bottom:1px solid #eee;'>{booking.check_out_date.strftime('%Y-%m-%d')}</td></tr>
                    <tr><td style='padding:8px;'>Total</td><td style='padding:8px;'><strong>${booking.total_price}</strong></td></tr>
                </table>
                <p style='margin-top:14px;color:#6e6e6e;'>Thank you for choosing Royal Tashkent Hotel.</p>
            </div>
        </body></html>
    """
    dispatch_email(background_tasks, user.email, subject, body, html_body)


def queue_payment_email(background_tasks: BackgroundTasks, user: models.User, booking: models.Booking, room: models.Room):
    subject = f"Payment Received: {booking.booking_reference or booking.id}"
    body = (
        f"Hello {user.full_name},\n\n"
        f"We received your payment successfully.\n\n"
        f"Room: {room.name}\n"
        f"Booking reference: {booking.booking_reference or booking.id}\n"
        f"Payment reference: {booking.payment_reference or 'N/A'}\n"
        f"Amount paid: ${booking.total_price}\n"
        f"Paid at: {booking.paid_at.strftime('%Y-%m-%d %H:%M:%S') if booking.paid_at else 'N/A'}\n\n"
        f"Your receipt is available in your dashboard."
    )
    html_body = f"""
        <html><body style='font-family:Arial,sans-serif;background:#f8f6f2;padding:20px;'>
            <div style='max-width:620px;margin:0 auto;background:#ffffff;border:1px solid #eadfce;border-radius:12px;padding:20px;'>
                <h2 style='margin-top:0;color:#1f6f4f;'>Payment Received</h2>
                <p>Hello <strong>{user.full_name}</strong>, we have received your payment.</p>
                <table style='width:100%;border-collapse:collapse;'>
                    <tr><td style='padding:8px;border-bottom:1px solid #eee;'>Room</td><td style='padding:8px;border-bottom:1px solid #eee;'><strong>{room.name}</strong></td></tr>
                    <tr><td style='padding:8px;border-bottom:1px solid #eee;'>Booking Ref</td><td style='padding:8px;border-bottom:1px solid #eee;'><strong>{booking.booking_reference or booking.id}</strong></td></tr>
                    <tr><td style='padding:8px;border-bottom:1px solid #eee;'>Payment Ref</td><td style='padding:8px;border-bottom:1px solid #eee;'><strong>{booking.payment_reference or 'N/A'}</strong></td></tr>
                    <tr><td style='padding:8px;'>Amount</td><td style='padding:8px;'><strong>${booking.total_price}</strong></td></tr>
                </table>
            </div>
        </body></html>
    """
    dispatch_email(background_tasks, user.email, subject, body, html_body)


def queue_cancellation_email(background_tasks: BackgroundTasks, user: models.User, booking: models.Booking, room: models.Room):
    subject = f"Booking Cancelled: {booking.booking_reference or booking.id}"
    body = (
        f"Hello {user.full_name},\n\n"
        f"Your booking was cancelled successfully.\n\n"
        f"Room: {room.name}\n"
        f"Booking reference: {booking.booking_reference or booking.id}\n"
        f"Check-in: {booking.check_in_date.strftime('%Y-%m-%d')}\n"
        f"Check-out: {booking.check_out_date.strftime('%Y-%m-%d')}\n"
        f"Total: ${booking.total_price}\n\n"
        f"If this was a mistake, you can create a new booking anytime."
    )
    html_body = f"""
        <html><body style='font-family:Arial,sans-serif;background:#f8f6f2;padding:20px;'>
            <div style='max-width:620px;margin:0 auto;background:#ffffff;border:1px solid #eadfce;border-radius:12px;padding:20px;'>
                <h2 style='margin-top:0;color:#9b2d2d;'>Booking Cancelled</h2>
                <p>Hello <strong>{user.full_name}</strong>, your booking has been cancelled.</p>
                <table style='width:100%;border-collapse:collapse;'>
                    <tr><td style='padding:8px;border-bottom:1px solid #eee;'>Room</td><td style='padding:8px;border-bottom:1px solid #eee;'><strong>{room.name}</strong></td></tr>
                    <tr><td style='padding:8px;border-bottom:1px solid #eee;'>Reference</td><td style='padding:8px;border-bottom:1px solid #eee;'><strong>{booking.booking_reference or booking.id}</strong></td></tr>
                    <tr><td style='padding:8px;border-bottom:1px solid #eee;'>Check-in</td><td style='padding:8px;border-bottom:1px solid #eee;'>{booking.check_in_date.strftime('%Y-%m-%d')}</td></tr>
                    <tr><td style='padding:8px;border-bottom:1px solid #eee;'>Check-out</td><td style='padding:8px;border-bottom:1px solid #eee;'>{booking.check_out_date.strftime('%Y-%m-%d')}</td></tr>
                    <tr><td style='padding:8px;'>Total</td><td style='padding:8px;'><strong>${booking.total_price}</strong></td></tr>
                </table>
            </div>
        </body></html>
    """
    dispatch_email(background_tasks, user.email, subject, body, html_body)


def queue_verification_email(background_tasks: BackgroundTasks, user: models.User):
    subject = "Your Royal Tashkent Verification Code"
    body = (
        f"Hello {user.full_name},\n\n"
        f"Your verification code is: {user.email_verification_code}\n"
        f"This code expires in 10 minutes.\n\n"
        f"If you did not create this account, you can ignore this message."
    )
    dispatch_email(background_tasks, user.email, subject, body)


def queue_reset_password_email(background_tasks: BackgroundTasks, user: models.User):
    subject = "Your Royal Tashkent Password Reset Code"
    body = (
        f"Hello {user.full_name},\n\n"
        f"Your password reset code is: {user.password_reset_code}\n"
        f"This code expires in 10 minutes.\n"
        f"You have up to {CODE_ATTEMPT_LIMIT} attempts.\n\n"
        f"If you did not request password reset, please ignore this message."
    )
    dispatch_email(background_tasks, user.email, subject, body)


@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    rooms = db.query(models.Room).all()

    promo_codes = (
        db.query(models.PromoCode)
        .filter(models.PromoCode.is_active == True)
        .order_by(models.PromoCode.discount_percent.desc())
        .all()
    )

    for room in rooms:
        gallery = normalize_room_gallery(
            room.image_url,
            getattr(room, "image_gallery", None),
        )
        room.gallery_images = gallery[:6]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": user,
            "rooms": rooms,
            "admin_email": ADMIN_EMAIL,
            "promo_codes": promo_codes,
            "promo_codes_json": json.dumps({item.code: int(item.discount_percent) for item in promo_codes}),
        },
    )


@app.get("/hotel-in-tashkent", response_class=HTMLResponse)
async def hotel_in_tashkent_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    return templates.TemplateResponse("hotel_in_tashkent.html", {"request": request, "user": user, "admin_email": ADMIN_EMAIL})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: Session = Depends(get_db)):
    # Auto-create admin user if not exists
    if not ADMIN_EMAIL or not ADMIN_PASSWORD:
        return templates.TemplateResponse("login.html", {"request": request})

    admin_user = db.query(models.User).filter(models.User.email == ADMIN_EMAIL).first()
    if not admin_user:
        hashed_password = auth.get_password_hash(ADMIN_PASSWORD)
        new_admin = models.User(
            email=ADMIN_EMAIL,
            full_name="Admin",
            hashed_password=hashed_password,
            is_admin=True,
            email_verified=True,
        )
        db.add(new_admin)
        try:
            db.commit()
        except:
            db.rollback()
    else:
        admin_user.is_admin = True
        admin_user.email_verified = True
        if ADMIN_PASSWORD:
            admin_user.hashed_password = auth.get_password_hash(ADMIN_PASSWORD)
        try:
            db.commit()
        except:
            db.rollback()
    
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.get("/verify-email", response_class=HTMLResponse)
async def verify_email_page(request: Request, email: str = ""):
    return templates.TemplateResponse("verify_email.html", {"request": request, "email": email})


@app.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})


@app.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request, email: str = ""):
    return templates.TemplateResponse("reset_password.html", {"request": request, "email": email})

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

    if not user.email_verified:
        return RedirectResponse(url=f"/verify-email?email={user.email}&error=unverified", status_code=status.HTTP_303_SEE_OTHER)
    
    access_token = auth.create_access_token(data={"sub": user.email})
    response = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True, max_age=2592000)
    return response

@app.post("/register")
async def register_post(
    background_tasks: BackgroundTasks,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.email == email).first()
    if db_user:
        return RedirectResponse(url="/register?error=2", status_code=status.HTTP_303_SEE_OTHER)
    
    hashed_password = auth.get_password_hash(password)
    verification_code = generate_verification_code()
    new_user = models.User(
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
        email_verified=False,
        email_verification_code=verification_code,
        email_verification_expires_at=datetime.utcnow() + timedelta(minutes=10),
        email_verification_attempts=0,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    queue_verification_email(background_tasks, new_user)
    return RedirectResponse(url=f"/verify-email?email={new_user.email}&sent=1", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/verify-email")
async def verify_email_post(
    background_tasks: BackgroundTasks,
    email: str = Form(...),
    code: str = Form(""),
    code_1: str = Form(""),
    code_2: str = Form(""),
    code_3: str = Form(""),
    code_4: str = Form(""),
    code_5: str = Form(""),
    code_6: str = Form(""),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return RedirectResponse(url="/register?error=2", status_code=status.HTTP_303_SEE_OTHER)

    if user.email_verified:
        return RedirectResponse(url="/login?verified=1", status_code=status.HTTP_303_SEE_OTHER)

    entered_code = (code or "").strip() or "".join([
        (code_1 or "").strip(),
        (code_2 or "").strip(),
        (code_3 or "").strip(),
        (code_4 or "").strip(),
        (code_5 or "").strip(),
        (code_6 or "").strip(),
    ])

    if len(entered_code) != 6:
        return RedirectResponse(url=f"/verify-email?email={email}&error=code_required", status_code=status.HTTP_303_SEE_OTHER)

    if not user.email_verification_expires_at or user.email_verification_expires_at < datetime.utcnow():
        user.email_verification_code = generate_verification_code()
        user.email_verification_expires_at = datetime.utcnow() + timedelta(minutes=10)
        user.email_verification_attempts = 0
        db.commit()
        queue_verification_email(background_tasks, user)
        return RedirectResponse(url=f"/verify-email?email={email}&error=expired&sent=1", status_code=status.HTTP_303_SEE_OTHER)

    if (user.email_verification_code or "") != entered_code:
        user.email_verification_attempts = (user.email_verification_attempts or 0) + 1
        if user.email_verification_attempts >= CODE_ATTEMPT_LIMIT:
            user.email_verification_code = generate_verification_code()
            user.email_verification_expires_at = datetime.utcnow() + timedelta(minutes=10)
            user.email_verification_attempts = 0
            db.commit()
            queue_verification_email(background_tasks, user)
            return RedirectResponse(url=f"/verify-email?email={email}&error=attempt_limit&sent=1", status_code=status.HTTP_303_SEE_OTHER)
        db.commit()
        return RedirectResponse(url=f"/verify-email?email={email}&error=invalid_code", status_code=status.HTTP_303_SEE_OTHER)

    user.email_verified = True
    user.email_verification_code = None
    user.email_verification_expires_at = None
    user.email_verification_attempts = 0
    db.commit()
    return RedirectResponse(url="/login?verified=1", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/verify-email/resend")
async def resend_verification_email(
    background_tasks: BackgroundTasks,
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return RedirectResponse(url="/register?error=2", status_code=status.HTTP_303_SEE_OTHER)

    if user.email_verified:
        return RedirectResponse(url="/login?verified=1", status_code=status.HTTP_303_SEE_OTHER)

    user.email_verification_code = generate_verification_code()
    user.email_verification_expires_at = datetime.utcnow() + timedelta(minutes=10)
    user.email_verification_attempts = 0
    db.commit()
    queue_verification_email(background_tasks, user)
    return RedirectResponse(url=f"/verify-email?email={email}&sent=1", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/forgot-password")
async def forgot_password_post(
    background_tasks: BackgroundTasks,
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return RedirectResponse(url="/forgot-password?sent=1", status_code=status.HTTP_303_SEE_OTHER)

    if not user.email_verified:
        return RedirectResponse(url=f"/verify-email?email={user.email}&error=unverified", status_code=status.HTTP_303_SEE_OTHER)

    user.password_reset_code = generate_verification_code()
    user.password_reset_expires_at = datetime.utcnow() + timedelta(minutes=10)
    user.password_reset_attempts = 0
    db.commit()
    queue_reset_password_email(background_tasks, user)
    return RedirectResponse(url=f"/reset-password?email={user.email}&sent=1", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/reset-password")
async def reset_password_post(
    background_tasks: BackgroundTasks,
    email: str = Form(...),
    code: str = Form(""),
    code_1: str = Form(""),
    code_2: str = Form(""),
    code_3: str = Form(""),
    code_4: str = Form(""),
    code_5: str = Form(""),
    code_6: str = Form(""),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return RedirectResponse(url="/forgot-password?sent=1", status_code=status.HTTP_303_SEE_OTHER)

    entered_code = (code or "").strip() or "".join([
        (code_1 or "").strip(),
        (code_2 or "").strip(),
        (code_3 or "").strip(),
        (code_4 or "").strip(),
        (code_5 or "").strip(),
        (code_6 or "").strip(),
    ])

    if len(entered_code) != 6:
        return RedirectResponse(url=f"/reset-password?email={email}&error=code_required", status_code=status.HTTP_303_SEE_OTHER)

    if new_password != confirm_password:
        return RedirectResponse(url=f"/reset-password?email={email}&error=password_mismatch", status_code=status.HTTP_303_SEE_OTHER)

    if len(new_password) < 6:
        return RedirectResponse(url=f"/reset-password?email={email}&error=password_short", status_code=status.HTTP_303_SEE_OTHER)

    if not user.password_reset_expires_at or user.password_reset_expires_at < datetime.utcnow():
        user.password_reset_code = generate_verification_code()
        user.password_reset_expires_at = datetime.utcnow() + timedelta(minutes=10)
        user.password_reset_attempts = 0
        db.commit()
        queue_reset_password_email(background_tasks, user)
        return RedirectResponse(url=f"/reset-password?email={email}&error=expired&sent=1", status_code=status.HTTP_303_SEE_OTHER)

    if (user.password_reset_code or "") != entered_code:
        user.password_reset_attempts = (user.password_reset_attempts or 0) + 1
        if user.password_reset_attempts >= CODE_ATTEMPT_LIMIT:
            user.password_reset_code = generate_verification_code()
            user.password_reset_expires_at = datetime.utcnow() + timedelta(minutes=10)
            user.password_reset_attempts = 0
            db.commit()
            queue_reset_password_email(background_tasks, user)
            return RedirectResponse(url=f"/reset-password?email={email}&error=attempt_limit&sent=1", status_code=status.HTTP_303_SEE_OTHER)
        db.commit()
        return RedirectResponse(url=f"/reset-password?email={email}&error=invalid_code", status_code=status.HTTP_303_SEE_OTHER)

    user.hashed_password = auth.get_password_hash(new_password)
    user.password_reset_code = None
    user.password_reset_expires_at = None
    user.password_reset_attempts = 0
    db.commit()
    return RedirectResponse(url="/login?password_reset=1", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response

@app.post("/book/{room_id}")
async def book_room(
    request: Request,
    background_tasks: BackgroundTasks,
    room_id: int,
    check_in: str = Form(...),
    check_out: str = Form(...),
    promo_code: str = Form(""),
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
        if days < 1:
            days = 1
        subtotal_price = days * room.price_per_night

        normalized_promo = normalize_promo_code(promo_code)
        discount_percent = get_discount_percent(db, normalized_promo)
        discount_amount = subtotal_price * (discount_percent / 100)
        total_price = round(subtotal_price - discount_amount, 2)
    except:
        return RedirectResponse(url="/?error=invalid_dates", status_code=status.HTTP_303_SEE_OTHER)

    booking_reference = f"RT-{datetime.utcnow().strftime('%y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

    new_booking = models.Booking(
        user_id=user.id,
        room_id=room.id,
        check_in_date=in_date,
        check_out_date=out_date,
        total_price=total_price,
        promo_code=normalized_promo if discount_percent else None,
        discount_percent=discount_percent,
        booking_reference=booking_reference,
        payment_status="pending",
    )

    earned_points = max(5, int(total_price // 10))
    user.loyalty_points = (user.loyalty_points or 0) + earned_points

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    queue_booking_email(background_tasks, user, new_booking, room)
    
    return RedirectResponse(url="/dashboard?success=booked", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
    
    bookings = (
        db.query(models.Booking)
        .filter(models.Booking.user_id == user.id)
        .order_by(models.Booking.created_at.desc())
        .all()
    )
    # Simple check if current user is admin
    is_admin = is_admin_user(user)
    points = user.loyalty_points or 0
    
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "bookings": bookings,
            "is_admin": is_admin,
            "admin_email": ADMIN_EMAIL,
            "loyalty_points": points,
            "loyalty_tier": loyalty_tier(points),
        },
    )

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, payment_status: str = "all", db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not is_admin_user(user):
        return RedirectResponse(url="/")
        
    rooms = db.query(models.Room).all()
    booking_query = db.query(models.Booking)
    if payment_status in {"paid", "pending"}:
        booking_query = booking_query.filter(models.Booking.payment_status == payment_status)
    bookings = booking_query.order_by(models.Booking.created_at.desc()).all()
    users = db.query(models.User).all()
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "user": user,
            "rooms": rooms,
            "bookings": bookings,
            "users": users,
            "admin_email": ADMIN_EMAIL,
            "payment_status": payment_status,
        },
    )

@app.post("/admin/room/add")
async def admin_add_room(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    amenities: str = Form(""),
    price_per_night: float = Form(...),
    image: UploadFile = File(None),
    extra_images: List[UploadFile] = File(default=[]),
    image_url: str = Form(""),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not is_admin_user(user):
        return RedirectResponse(url="/")
        
    final_image_url = image_url if image_url else "/static/images/room1.jpg"
    
    encoded_main = await encode_upload_image(image)
    if encoded_main:
        final_image_url = encoded_main

    gallery_images = [final_image_url]
    for upload in (extra_images or []):
        encoded_extra = await encode_upload_image(upload)
        if encoded_extra:
            gallery_images.append(encoded_extra)
        if len(gallery_images) >= 6:
            break

    new_room = models.Room(
        name=name,
        description=description,
        amenities=normalize_amenities(amenities),
        price_per_night=price_per_night,
        image_url=final_image_url,
        image_gallery=json.dumps(gallery_images[:6]),
    )
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
    if not is_admin_user(user):
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
    if not is_admin_user(user):
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
    if not is_admin_user(user):
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
    amenities: str = Form(""),
    price_per_night: float = Form(...),
    image: UploadFile = File(None),
    extra_images: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not is_admin_user(user):
        return RedirectResponse(url="/")
        
    room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if room:
        room.name = name
        room.description = description
        room.amenities = normalize_amenities(amenities)
        room.price_per_night = price_per_night
        
        encoded_main = await encode_upload_image(image)
        if encoded_main:
            room.image_url = encoded_main

        gallery_images = normalize_room_gallery(room.image_url, getattr(room, "image_gallery", None))
        for upload in (extra_images or []):
            encoded_extra = await encode_upload_image(upload)
            if encoded_extra:
                gallery_images.append(encoded_extra)
            if len(gallery_images) >= 6:
                break

        room.image_gallery = json.dumps(gallery_images[:6])
        db.commit()
    return RedirectResponse(url="/admin", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/dashboard/booking/cancel/{booking_id}")
async def dashboard_cancel_booking(
    request: Request,
    background_tasks: BackgroundTasks,
    booking_id: int,
    db: Session = Depends(get_db)
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")
        
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id, models.Booking.user_id == user.id).first()
    if booking:
        room = booking.room
        queue_cancellation_email(background_tasks, user, booking, room)
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
                subtotal_price = days * booking.room.price_per_night
                discount_percent = booking.discount_percent or 0
                booking.total_price = round(subtotal_price * (1 - (discount_percent / 100)), 2)
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
    if not is_admin_user(user):
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


@app.get("/payment/{booking_id}", response_class=HTMLResponse)
async def payment_page(booking_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")

    booking = (
        db.query(models.Booking)
        .filter(models.Booking.id == booking_id, models.Booking.user_id == user.id)
        .first()
    )
    if not booking:
        return RedirectResponse(url="/dashboard")

    if booking.payment_status == "paid":
        return RedirectResponse(url="/dashboard")

    return templates.TemplateResponse(
        "payment.html",
        {"request": request, "user": user, "booking": booking, "admin_email": ADMIN_EMAIL},
    )


@app.post("/payment/{booking_id}")
async def payment_submit(
    booking_id: int,
    request: Request,
    background_tasks: BackgroundTasks,
    card_holder: str = Form(...),
    card_number: str = Form(...),
    expiry: str = Form(...),
    cvv: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")

    booking = (
        db.query(models.Booking)
        .filter(models.Booking.id == booking_id, models.Booking.user_id == user.id)
        .first()
    )
    if not booking:
        return RedirectResponse(url="/dashboard")

    normalized_card = "".join(ch for ch in card_number if ch.isdigit())
    normalized_cvv = "".join(ch for ch in cvv if ch.isdigit())
    holder_ok = len(card_holder.strip()) >= 3
    expiry_ok = len(expiry.strip()) in {4, 5}

    if len(normalized_card) < 12 or len(normalized_card) > 19 or len(normalized_cvv) not in {3, 4} or not holder_ok or not expiry_ok:
        return RedirectResponse(url=f"/payment/{booking_id}?error=1", status_code=status.HTTP_303_SEE_OTHER)

    booking.payment_status = "paid"
    booking.payment_reference = f"PAY-{uuid.uuid4().hex[:10].upper()}"
    booking.paid_at = datetime.utcnow()
    db.commit()

    queue_payment_email(background_tasks, user, booking, booking.room)
    return RedirectResponse(url=f"/receipt/{booking.id}", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/receipt/{booking_id}", response_class=HTMLResponse)
async def receipt_page(booking_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_from_cookie(request, db)
    if not user:
        return RedirectResponse(url="/login")

    booking = (
        db.query(models.Booking)
        .filter(models.Booking.id == booking_id, models.Booking.user_id == user.id)
        .first()
    )
    if not booking:
        return RedirectResponse(url="/dashboard")

    return templates.TemplateResponse(
        "receipt.html",
        {"request": request, "user": user, "booking": booking, "admin_email": ADMIN_EMAIL},
    )
