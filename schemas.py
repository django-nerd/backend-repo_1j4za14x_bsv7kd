"""
Database Schemas for Hotel Operations App

Each Pydantic model represents a collection in MongoDB.
Collection name is the lowercase of the class name by default.
"""
from __future__ import annotations

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal, List
from datetime import datetime

# -----------------------------------------------------------------------------
# Core Entities
# -----------------------------------------------------------------------------

class Guest(BaseModel):
    full_name: str = Field(..., description="Guest full name as on ID")
    phone: Optional[str] = Field(None, description="Primary contact number with country code")
    email: Optional[EmailStr] = Field(None, description="Email for receipts/notifications")
    address: Optional[str] = Field(None, description="Residential address")
    id_type: Optional[Literal["aadhaar", "pan", "passport", "other"]] = Field(None)
    id_number: Optional[str] = Field(None, description="Normalized ID number")
    dob: Optional[str] = Field(None, description="Date of birth in YYYY-MM-DD if known")
    meta: dict = Field(default_factory=dict, description="Any additional extracted fields")

class Booking(BaseModel):
    guest_id: str = Field(..., description="Reference to guest _id")
    room_number: str = Field(..., description="Allocated room number")
    check_in: datetime = Field(..., description="Check-in datetime")
    check_out: datetime = Field(..., description="Check-out datetime")
    rate: float = Field(..., ge=0, description="Rate per night or package total, currency-agnostic")
    source: Optional[Literal["walkin", "ota", "corporate", "phone", "website"]] = Field("walkin")
    notes: Optional[str] = None
    status: Literal["booked", "checked_in", "checked_out", "cancelled"] = "booked"

class Iddocument(BaseModel):
    guest_id: Optional[str] = Field(None, description="Reference to guest _id if already created")
    doc_type: Optional[Literal["aadhaar", "pan", "passport", "other"]] = None
    id_number: Optional[str] = None
    raw_text: Optional[str] = None
    extracted: dict = Field(default_factory=dict)
    file_name: Optional[str] = None

class Notification(BaseModel):
    channel: Literal["sms", "whatsapp"]
    to: str
    message: str
    status: Literal["queued", "sent", "failed"] = "queued"
    provider: Optional[str] = None
    error: Optional[str] = None

# -----------------------------------------------------------------------------
# Example default models kept for reference (not used by app directly)
# -----------------------------------------------------------------------------
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = Field(None, ge=0, le=120)
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True

# -----------------------------------------------------------------------------
# Helper export (FastAPI can serve these via /schema)
# -----------------------------------------------------------------------------
SCHEMAS: List[type[BaseModel]] = [Guest, Booking, Iddocument, Notification]

