import os
import mysql.connector
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from app.database import get_connection

app = FastAPI(
    title="HostelHub API",
    description="Complete Backend API for Hostel Management System",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LoginRequest(BaseModel):
    role: str
    username: str
    password: str

class StudentCreate(BaseModel):
    roll_no: str
    name: str
    email: str
    phone: str
    course: str
    year: int
    room_no: str
    bed_no: int
    fee_status: str
    password: str

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    course: Optional[str] = None
    year: Optional[int] = None
    room_no: Optional[str] = None
    bed_no: Optional[int] = None
    fee_status: Optional[str] = None

class ComplaintRequest(BaseModel):
    student_name: str
    roll_no: str
    room_no: str
    category: str
    title: str
    description: str

class ComplaintStatusUpdate(BaseModel):
    status: str

class RoomCreate(BaseModel):
    room_no: str
    block: str
    floor: int
    room_type: str
    capacity: int

class FeeUpdate(BaseModel):
    amount_paid: float
    payment_mode: str

class NoticeCreate(BaseModel):
    title: str
    body: str
    posted_by: Optional[str] = "Admin"


@app.get("/", tags=["Health"])
def home():
    return {
        "status": "online",
        "message": "HostelHub Backend is running!",
        "docs": "Visit http://127.0.0.1:8000/docs for Swagger UI"
    }


@app.post("/api/auth/login", tags=["Auth"])
def login(data: LoginRequest):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if data.role == "admin":
            cursor.execute(
                "SELECT * FROM admins WHERE username=%s AND password=%s",
                (data.username, data.password)
            )
            user = cursor.fetchone()
            if user:
                return {
                    "success": True,
                    "message": "Admin login successful",
                    "role": "admin",
                    "name": user["name"],
                    "id": user["id"]
                }
        elif data.role == "student":
            cursor.execute(
                "SELECT * FROM students WHERE roll_no=%s AND password=%s",
                (data.username, data.password)
            )
            user = cursor.fetchone()
            if user:
                return {
                    "success": True,
                    "message": "Student login successful",
                    "role": "student",
                    "name": user["name"],
                    "roll_no": user["roll_no"],
                    "room_no": user["room_no"],
                    "id": user["id"]
                }
        return {"success": False, "message": "Invalid username or password"}
    finally:
        cursor.close()
        conn.close()


@app.get("/api/dashboard/stats", tags=["Dashboard"])
def get_dashboard_stats():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT COUNT(*) AS total FROM students")
        total_students = cursor.fetchone()["total"]

        cursor.execute("SELECT SUM(capacity - occupied) AS available FROM rooms")
        row = cursor.fetchone()
        available_rooms = row["available"] if row["available"] else 0

        cursor.execute("SELECT COUNT(*) AS total FROM rooms")
        total_rooms = cursor.fetchone()["total"]

        cursor.execute(
            "SELECT COALESCE(SUM(total_fee - amount_paid),0) AS pending FROM fees WHERE status='Pending'"
        )
        pending_fees = cursor.fetchone()["pending"]

        cursor.execute(
            "SELECT COUNT(*) AS open FROM complaints WHERE status != 'Resolved'"
        )
        open_complaints = cursor.fetchone()["open"]

        return {
            "success": True,
            "total_students": total_students,
            "available_rooms": int(available_rooms),
            "total_rooms": total_rooms,
            "pending_fees": float(pending_fees),
            "open_complaints": open_complaints
        }
    finally:
        cursor.close()
        conn.close()


@app.get("/api/students", tags=["Students"])
def get_all_students():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, roll_no, name, email, phone, course, year, room_no, bed_no, fee_status, created_at FROM students"
        )
        students = cursor.fetchall()
        for s in students:
            if s.get("created_at"):
                s["created_at"] = str(s["created_at"])
        return {"success": True, "total": len(students), "students": students}
    finally:
        cursor.close()
        conn.close()


@app.get("/api/students/{roll_no}", tags=["Students"])
def get_student_by_roll(roll_no: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT id, roll_no, name, email, phone, course, year, room_no, bed_no, fee_status FROM students WHERE roll_no=%s",
            (roll_no,)
        )
        student = cursor.fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return {"success": True, "student": student}
    finally:
        cursor.close()
        conn.close()


@app.post("/api/students", tags=["Students"])
def add_student(data: StudentCreate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO students (roll_no, name, email, phone, course, year, room_no, bed_no, fee_status, password)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (data.roll_no, data.name, data.email, data.phone,
             data.course, data.year, data.room_no, data.bed_no,
             data.fee_status, data.password)
        )
        cursor.execute(
            "UPDATE rooms SET occupied = occupied + 1 WHERE room_no = %s",
            (data.room_no,)
        )
        conn.commit()
        return {"success": True, "message": "Student added successfully"}
    except mysql.connector.IntegrityError as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=f"Duplicate entry: {str(e)}")
    finally:
        cursor.close()
        conn.close()


@app.put("/api/students/{roll_no}", tags=["Students"])
def update_student(roll_no: str, data: StudentUpdate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        fields = {k: v for k, v in data.model_dump().items() if v is not None}
        if not fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        set_clause = ", ".join(f"{k}=%s" for k in fields)
        values = list(fields.values()) + [roll_no]
        cursor.execute(f"UPDATE students SET {set_clause} WHERE roll_no=%s", values)
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Student not found")
        return {"success": True, "message": "Student updated successfully"}
    finally:
        cursor.close()
        conn.close()


@app.delete("/api/students/{roll_no}", tags=["Students"])
def delete_student(roll_no: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT room_no FROM students WHERE roll_no=%s", (roll_no,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Student not found")
        cursor.execute("DELETE FROM students WHERE roll_no=%s", (roll_no,))
        if row["room_no"]:
            cursor.execute(
                "UPDATE rooms SET occupied = GREATEST(occupied - 1, 0) WHERE room_no=%s",
                (row["room_no"],)
            )
        conn.commit()
        return {"success": True, "message": "Student deleted successfully"}
    finally:
        cursor.close()
        conn.close()


@app.get("/api/rooms", tags=["Rooms"])
def get_all_rooms():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM rooms ORDER BY block, room_no")
        rooms = cursor.fetchall()
        for room in rooms:
            cursor.execute(
                "SELECT name, roll_no FROM students WHERE room_no=%s",
                (room["room_no"],)
            )
            room["occupants"] = cursor.fetchall()
            room["available_beds"] = room["capacity"] - room["occupied"]
            if room.get("created_at"):
                room["created_at"] = str(room["created_at"])
        return {"success": True, "total": len(rooms), "rooms": rooms}
    finally:
        cursor.close()
        conn.close()


@app.post("/api/rooms", tags=["Rooms"])
def add_room(data: RoomCreate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO rooms (room_no, block, floor, room_type, capacity) VALUES (%s,%s,%s,%s,%s)",
            (data.room_no, data.block, data.floor, data.room_type, data.capacity)
        )
        conn.commit()
        return {"success": True, "message": "Room added successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@app.delete("/api/rooms/{room_no}", tags=["Rooms"])
def delete_room(room_no: str):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM rooms WHERE room_no=%s", (room_no,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Room not found")
        return {"success": True, "message": "Room deleted successfully"}
    finally:
        cursor.close()
        conn.close()


@app.get("/api/fees", tags=["Fees"])
def get_all_fees():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT f.id, f.receipt_id, s.name, f.roll_no, s.room_no,
                   f.description, f.total_fee, f.amount_paid,
                   (f.total_fee - f.amount_paid) AS due_balance,
                   f.payment_mode, f.status, f.date_paid
            FROM fees f
            JOIN students s ON f.roll_no = s.roll_no
            ORDER BY f.id
        """)
        fees = cursor.fetchall()
        for fee in fees:
            if fee.get("date_paid"):
                fee["date_paid"] = str(fee["date_paid"])
            fee["total_fee"]   = float(fee["total_fee"])
            fee["amount_paid"] = float(fee["amount_paid"])
            fee["due_balance"] = float(fee["due_balance"])
        return {"success": True, "fees": fees}
    finally:
        cursor.close()
        conn.close()


@app.get("/api/fees/{roll_no}", tags=["Fees"])
def get_student_fees(roll_no: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT f.id, f.receipt_id, f.roll_no, f.description,
                   f.total_fee, f.amount_paid,
                   (f.total_fee - f.amount_paid) AS due_balance,
                   f.payment_mode, f.status, f.date_paid, f.created_at,
                   s.name, s.room_no
            FROM fees f
            JOIN students s ON f.roll_no = s.roll_no
            WHERE f.roll_no = %s
        """, (roll_no,))
        fees = cursor.fetchall()
        for fee in fees:
            if fee.get("date_paid"):
                fee["date_paid"] = str(fee["date_paid"])
            if fee.get("created_at"):
                fee["created_at"] = str(fee["created_at"])
            fee["total_fee"]   = float(fee["total_fee"])
            fee["amount_paid"] = float(fee["amount_paid"])
            fee["due_balance"] = float(fee["due_balance"])
        return {"success": True, "fees": fees}
    finally:
        cursor.close()
        conn.close()


@app.put("/api/fees/{receipt_id}", tags=["Fees"])
def update_fee_payment(receipt_id: str, data: FeeUpdate):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT total_fee, roll_no FROM fees WHERE receipt_id=%s", (receipt_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Receipt not found")
        new_status = "Paid" if data.amount_paid >= float(row["total_fee"]) else "Pending"
        cursor.execute(
            """UPDATE fees SET amount_paid=%s, payment_mode=%s, status=%s,
               date_paid=CURDATE() WHERE receipt_id=%s""",
            (data.amount_paid, data.payment_mode, new_status, receipt_id)
        )
        cursor.execute(
            "UPDATE students SET fee_status=%s WHERE roll_no=%s",
            (new_status, row["roll_no"])
        )
        conn.commit()
        return {"success": True, "message": f"Payment updated. Status: {new_status}"}
    finally:
        cursor.close()
        conn.close()


@app.get("/api/complaints", tags=["Complaints"])
def get_all_complaints():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM complaints ORDER BY date_filed DESC")
        complaints = cursor.fetchall()
        for c in complaints:
            if c.get("date_filed"):
                c["date_filed"] = str(c["date_filed"])
        return {"success": True, "total": len(complaints), "complaints": complaints}
    finally:
        cursor.close()
        conn.close()


@app.get("/api/complaints/student/{roll_no}", tags=["Complaints"])
def get_student_complaints(roll_no: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT * FROM complaints WHERE roll_no=%s ORDER BY date_filed DESC",
            (roll_no,)
        )
        complaints = cursor.fetchall()
        for c in complaints:
            if c.get("date_filed"):
                c["date_filed"] = str(c["date_filed"])
        return {"success": True, "complaints": complaints}
    finally:
        cursor.close()
        conn.close()


@app.post("/api/complaints", tags=["Complaints"])
def submit_complaint(data: ComplaintRequest):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO complaints (student_name, roll_no, room_no, category, title, description)
               VALUES (%s,%s,%s,%s,%s,%s)""",
            (data.student_name, data.roll_no, data.room_no,
             data.category, data.title, data.description)
        )
        conn.commit()
        return {"success": True, "message": "Complaint submitted successfully!", "id": cursor.lastrowid}
    finally:
        cursor.close()
        conn.close()


@app.put("/api/complaints/{complaint_id}", tags=["Complaints"])
def update_complaint_status(complaint_id: int, data: ComplaintStatusUpdate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE complaints SET status=%s WHERE id=%s",
            (data.status, complaint_id)
        )
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Complaint not found")
        return {"success": True, "message": f"Status updated to {data.status}"}
    finally:
        cursor.close()
        conn.close()


@app.delete("/api/complaints/{complaint_id}", tags=["Complaints"])
def delete_complaint(complaint_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM complaints WHERE id=%s", (complaint_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Complaint not found")
        return {"success": True, "message": "Complaint deleted"}
    finally:
        cursor.close()
        conn.close()


@app.get("/api/notices", tags=["Notices"])
def get_all_notices():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM notices ORDER BY created_at DESC")
        notices = cursor.fetchall()
        for n in notices:
            if n.get("created_at"):
                n["created_at"] = str(n["created_at"])
        return {"success": True, "notices": notices}
    finally:
        cursor.close()
        conn.close()


@app.post("/api/notices", tags=["Notices"])
def add_notice(data: NoticeCreate):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO notices (title, body, posted_by) VALUES (%s,%s,%s)",
            (data.title, data.body, data.posted_by)
        )
        conn.commit()
        return {"success": True, "message": "Notice posted successfully"}
    finally:
        cursor.close()
        conn.close()


@app.delete("/api/notices/{notice_id}", tags=["Notices"])
def delete_notice(notice_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM notices WHERE id=%s", (notice_id,))
        conn.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Notice not found")
        return {"success": True, "message": "Notice deleted"}
    finally:
        cursor.close()
        conn.close()
