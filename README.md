# 🏢 HostelHub — Hostel Management System

A full-stack Hostel Management System built with **Python FastAPI** (backend), **MySQL** (database), and **HTML/CSS/JavaScript** (frontend). It provides separate portals for Admins (Wardens) and Students.

---

## 📸 Features

### Admin Portal
- 📊 Live Dashboard with student count, room availability, pending fees, open complaints
- 👥 Student Management — Add, View, Search, Delete students
- 🛏️ Room Management — View room occupancy, add rooms, see occupants
- 💳 Fee Management — View all fees, collect dues, update payment status
- 📝 Complaint Management — View all complaints, update status (Pending → In Progress → Resolved)

### Student Portal
- 📊 Personal Dashboard — Room info, fee status, active complaints
- 🛏️ My Room — Room specifications + roommate details
- 💳 Fee Status — View payment receipts and balance due
- 📝 My Complaints — Submit new complaints + track ticket status in real time
- 📢 Notice Board — Live hostel notices posted by admin

---

## 🛠️ Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Frontend  | HTML5, CSS3, Vanilla JavaScript   |
| Backend   | Python 3.x + FastAPI              |
| Database  | MySQL                             |
| ORM       | Raw SQL via mysql-connector-python|
| Config    | python-dotenv (.env file)         |
| API Docs  | Swagger UI (auto-generated)       |

---

## 📁 Project Structure

```
HostelHub/
├── Backend/
│   ├── app/
│   │   ├── __init__.py      # Makes 'app' a Python package
│   │   ├── main.py          # All FastAPI routes/endpoints
│   │   └── database.py      # MySQL connection factory
│   ├── .env                 # DB credentials (NOT committed to Git)
│   ├── .env.example         # Template for credentials (safe to commit)
│   └── requirements.txt     # Python dependencies
│
├── frontend/
│   ├── index.html           # Login page (entry point)
│   ├── login.js             # Login logic + API call
│   ├── style.css            # Login page styles
│   ├── admin/
│   │   ├── dashboard.html   # Admin dashboard
│   │   ├── students.html    # Student management
│   │   ├── rooms.html       # Room management
│   │   ├── fees.html        # Fee management
│   │   ├── complaints.html  # Complaint management
│   │   └── admin.css        # Admin portal styles
│   └── student/
│       ├── dashboard.html   # Student dashboard
│       ├── room.html        # My room details
│       ├── fees.html        # My fee status
│       ├── complaints.html  # My complaints
│       └── student.css      # Student portal styles
│
├── Database/
│   └── hostelhub.sql        # Complete SQL schema (reference)
│
├── setup_db.py              # One-time DB setup script
└── README.md
```

---

## ⚙️ Installation & Setup

### Step 1 — Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/HostelHub.git
cd HostelHub
```

### Step 2 — Install Python Dependencies
```bash
cd Backend
pip install -r requirements.txt
```

### Step 3 — Configure MySQL Credentials
Copy the example file and edit it:
```bash
cp Backend/.env.example Backend/.env
```
Open `Backend/.env` and set your MySQL password:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password_here
DB_NAME=hostelhub
```

### Step 4 — Setup the Database
Run this once from the project root. It creates all tables and inserts sample data:
```bash
python setup_db.py
```

### Step 5 — Start the FastAPI Server
```bash
cd Backend
uvicorn app.main:app --reload
```
Server runs at: **http://127.0.0.1:8000**

### Step 6 — Open the Frontend
Just open `frontend/index.html` in your browser. No web server needed.

---

## 🔐 Demo Login Credentials

| Role    | Username  | Password  |
|---------|-----------|-----------|
| Admin   | admin     | admin123  |
| Student | CS202401  | pass123   |
| Student | CS202402  | pass123   |
| Student | EC202415  | pass123   |

---

## 📡 API Endpoints

| Method | URL                                    | Description                        |
|--------|----------------------------------------|------------------------------------|
| GET    | `/`                                    | Health check                       |
| POST   | `/api/auth/login`                      | Login for admin/student            |
| GET    | `/api/dashboard/stats`                 | Admin dashboard summary            |
| GET    | `/api/students`                        | Get all students                   |
| GET    | `/api/students/{roll_no}`              | Get one student                    |
| POST   | `/api/students`                        | Add new student                    |
| PUT    | `/api/students/{roll_no}`              | Update student                     |
| DELETE | `/api/students/{roll_no}`              | Delete student                     |
| GET    | `/api/rooms`                           | Get all rooms with occupants       |
| POST   | `/api/rooms`                           | Add new room                       |
| DELETE | `/api/rooms/{room_no}`                 | Delete room                        |
| GET    | `/api/fees`                            | Get all fee records                |
| GET    | `/api/fees/{roll_no}`                  | Get fee for one student            |
| PUT    | `/api/fees/{receipt_id}`               | Record/update payment              |
| GET    | `/api/complaints`                      | Get all complaints                 |
| GET    | `/api/complaints/student/{roll_no}`    | Get complaints by student          |
| POST   | `/api/complaints`                      | Submit new complaint               |
| PUT    | `/api/complaints/{id}`                 | Update complaint status            |
| DELETE | `/api/complaints/{id}`                 | Delete complaint                   |
| GET    | `/api/notices`                         | Get all notices                    |
| POST   | `/api/notices`                         | Add notice                         |
| DELETE | `/api/notices/{id}`                    | Delete notice                      |

### 📖 Swagger UI (Interactive API Docs)
Visit **http://127.0.0.1:8000/docs** when the server is running to test all endpoints visually.

---

## 🗄️ Database Schema

**6 Tables:**
- `admins` — Admin login accounts
- `rooms` — Hostel rooms (block, floor, capacity, occupancy)
- `students` — Student profiles and login credentials
- `complaints` — Maintenance complaints filed by students
- `fees` — Semester fee payment records
- `notices` — Notice board posts by admin

---

## 🔄 How Frontend Connects to Backend

```
User fills Login Form
        ↓
login.js sends POST request to http://127.0.0.1:8000/api/auth/login
        ↓
FastAPI receives JSON, queries MySQL, returns { success: true, name: "..." }
        ↓
JS saves role + name in localStorage
        ↓
Redirects to admin/dashboard.html or student/dashboard.html
        ↓
Dashboard page reads localStorage, calls /api/dashboard/stats
        ↓
Displays live data from MySQL
```

---

## 🔒 Security Notes

- `.env` file is in `.gitignore` — passwords never get committed to Git
- Always use `.env.example` as the template when sharing the project
- Passwords in this demo are plain text. In production, use `bcrypt` hashing

---

## 👨‍💻 Author

Built as a Backend Developer Intern project demonstrating FastAPI + MySQL + Vanilla JS integration.
