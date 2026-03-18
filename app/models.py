from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    loyalty_points = Column(Integer, default=0)
    email_verified = Column(Boolean, default=False)
    email_verification_code = Column(String, nullable=True)
    email_verification_expires_at = Column(DateTime, nullable=True)
    email_verification_attempts = Column(Integer, default=0)
    password_reset_code = Column(String, nullable=True)
    password_reset_expires_at = Column(DateTime, nullable=True)
    password_reset_attempts = Column(Integer, default=0)

    bookings = relationship("Booking", back_populates="user")

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    amenities = Column(String, nullable=True)
    price_per_night = Column(Float)
    image_url = Column(String)
    image_gallery = Column(String, nullable=True)
    
    bookings = relationship("Booking", back_populates="room")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    room_id = Column(Integer, ForeignKey("rooms.id"))
    check_in_date = Column(DateTime)
    check_out_date = Column(DateTime)
    total_price = Column(Float)
    guest_count = Column(Integer, default=1)
    promo_code = Column(String, nullable=True)
    discount_percent = Column(Float, default=0)
    needs_transfer = Column(Boolean, default=False)
    special_request = Column(String, nullable=True)
    booking_reference = Column(String, unique=True, index=True)
    payment_status = Column(String, default="pending")
    payment_reference = Column(String, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True)
    discount_percent = Column(Float, default=0)
    is_active = Column(Boolean, default=True)


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    message = Column(String)
    source = Column(String, default="website")
    status = Column(String, default="new")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
