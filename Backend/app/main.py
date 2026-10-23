from fastapi import FastAPI  
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 1. Create the central FastAPI application object
app =FastAPI(
    title="HostelHub Api",
    description="Backend API for Hostel management system",
    version="1.0.0"
)
# 2. Configure CORS (Allows frontend to connect with backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],# Allows all frontends to access the API
    allow_credentials=True,
    allow_methods=["*"],# Allows all HTTP methods (GET, POST, PUT, DELETE)
    allow_headers=["*"], # Allows all headers

)
# 3. Pydantic Model (Defines the shape of data coming from frontend)
class loginRequest(BaseModel):
    role:str
    username:str
    password:str

# 4. Root test route
@app.get("/")
def home():
    return{
        "status":"online",
        "message":"HostelHUB Backend is running successfully!"
    }

# 5. Login API Endpoint (POST Request)
@app.post("/api/auth/login")
def login (
    data : loginRequest
):    
    #Check Admin credentials
    if data.role =="admin" and data.username =="admin" and data.password == "admin123":
        return {
            "success":True,
            "message":"Admin login successfully",
            "role":"admin",
            "name":"Chief Warden"
        }
    # Check Student credentials
    elif data.role =="student" and data.username =="student" and data.password =="student123":
        return {
            "success":True,
            "message": "Student login successfully!",
            "role":"student",
            "name": "Rahul Sharma"
        }
          # Invalid credentials
    
    else:
            return {
                "success":False,
                "message":"Invalid username or password "
            }
    
# 6. Sample Students Data (Abhi Python list me, Phase 3 me MySQL Database se aayega)
students_db = [
    {
        "id":1,
        "roll_no":"CS231041",
        "NAME":"Ayushi Rathore",
        "email":"ayushi@gmail.com",
        "phone":"+91 6261957723",
        "room_no":"204",
        "fee_status":"paid"
    },
        {
        "id": 2,
        "roll_no": "CS202402",
        "name": "Amit Patel",
        "email": "amit@example.com",
        "phone": "+91 98765 12345",
        "room_no": "A-204 (Bed 1)",
        "fee_status": "Paid"
    },
    {
        "id": 3,
        "roll_no": "EC202415",
        "name": "Priya Verma",
        "email": "priya@example.com",
        "phone": "+91 98123 45678",
        "room_no": "B-105 (Bed 1)",
        "fee_status": "Pending"
    },
    {
        "id": 4,
        "roll_no": "ME202408",
        "name": "Rohan Gupta",
        "email": "rohan@example.com",
        "phone": "+91 98234 56789",
        "room_no": "C-302 (Bed 2)",
        "fee_status": "Paid"
    }
]
# 7. Get All Students API Endpoint
@app.get("/api/students")
def get_all_students():
    return{
        "success":"True",
        "total":len(students_db),
        "students":students_db,
    }
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("Backend.app.main:app", host="127.0.0.1", port=8000, reload=True)

###its my first git practice 