import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db, create_document, get_documents
from schemas import Guest, Booking, Iddocument, Notification

app = FastAPI(title="HotelOps API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "HotelOps backend is running"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# ----------------------------------------------------------------------------
# Aadhaar/PAN OCR Extraction (Stub)
# ----------------------------------------------------------------------------
class OCRResult(BaseModel):
    id_type: Optional[str] = None
    id_number: Optional[str] = None
    full_name: Optional[str] = None
    dob: Optional[str] = None
    raw_text: Optional[str] = None


@app.post("/api/ocr", response_model=OCRResult)
async def ocr_extract(file: UploadFile = File(...)):
    """Stub OCR extractor. In production, integrate with OCR provider.
    For now, we store the file metadata and return mock extracted fields.
    """
    # Save document metadata in db for audit
    meta = {
        "filename": file.filename,
        "content_type": file.content_type,
        "received_at": datetime.utcnow().isoformat(),
    }
    create_document("iddocument", {"file_name": file.filename, "extracted": {}, "raw_text": None, **meta})

    # Return a mocked response to enable end-to-end flow
    return OCRResult(
        id_type="aadhaar" if file.filename.lower().endswith((".jpg", ".png", ".jpeg")) else "pan",
        id_number="XXXX-XXXX-1234",
        full_name="Sample Guest",
        dob="1990-01-01",
        raw_text="Mocked OCR content"
    )


# ----------------------------------------------------------------------------
# Guest + Booking CRUD (minimal for MVP)
# ----------------------------------------------------------------------------
@app.post("/api/guests")
async def create_guest(guest: Guest):
    guest_id = create_document("guest", guest)
    return {"_id": guest_id, **guest.model_dump()}


@app.get("/api/guests")
async def list_guests(q: Optional[str] = None, limit: int = 25):
    filt = {}
    if q:
        # very simple filter: match exact phone or id_number
        filt = {"$or": [{"phone": q}, {"id_number": q}]}
    docs = get_documents("guest", filt, limit)
    # Convert ObjectIds to strings if present
    for d in docs:
        if "_id" in d:
            d["_id"] = str(d["_id"])  
    return docs


@app.post("/api/bookings")
async def create_booking(booking: Booking):
    booking_id = create_document("booking", booking)
    return {"_id": booking_id, **booking.model_dump()}


@app.get("/api/bookings")
async def list_bookings(limit: int = 50):
    docs = get_documents("booking", {}, limit)
    for d in docs:
        if "_id" in d:
            d["_id"] = str(d["_id"])  
    return docs


# ----------------------------------------------------------------------------
# Notifications (WhatsApp/SMS) - Stub senders
# ----------------------------------------------------------------------------
class SendNotificationPayload(BaseModel):
    channel: str
    to: str
    message: str


@app.post("/api/notify")
async def send_notification(payload: SendNotificationPayload):
    """Queue a notification record and simulate sending.
    Replace with Twilio/Meta WhatsApp Business API in production.
    """
    notif = Notification(channel=payload.channel, to=payload.to, message=payload.message)
    notif_id = create_document("notification", notif)
    # Simulate immediate success
    return {"status": "sent", "id": notif_id}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
