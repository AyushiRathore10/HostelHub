import mysql.connector

conn   = mysql.connector.connect(host='localhost', user='root', password='root')
cursor = conn.cursor()

cursor.execute("CREATE DATABASE IF NOT EXISTS hostelhub")
cursor.execute("USE hostelhub")

cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
for tbl in ['fees','complaints','notices','students','rooms','admins']:
    cursor.execute(f"DROP TABLE IF EXISTS {tbl}")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

cursor.execute("""
CREATE TABLE admins (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    username   VARCHAR(50)  NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")

cursor.execute("""
CREATE TABLE rooms (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    room_no    VARCHAR(20) NOT NULL UNIQUE,
    block      VARCHAR(10) NOT NULL,
    floor      INT         NOT NULL,
    room_type  VARCHAR(50) NOT NULL DEFAULT 'Double Sharing',
    capacity   INT         NOT NULL DEFAULT 2,
    occupied   INT         NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")

cursor.execute("""
CREATE TABLE students (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    roll_no    VARCHAR(20)  NOT NULL UNIQUE,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(100) NOT NULL UNIQUE,
    phone      VARCHAR(15),
    course     VARCHAR(100) DEFAULT 'B.Tech',
    year       INT          DEFAULT 1,
    room_no    VARCHAR(20),
    bed_no     INT          DEFAULT 1,
    fee_status ENUM('Paid','Pending') DEFAULT 'Pending',
    password   VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")

cursor.execute("""
CREATE TABLE complaints (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(100) NOT NULL,
    roll_no      VARCHAR(20)  NOT NULL,
    room_no      VARCHAR(20),
    category     VARCHAR(50)  NOT NULL,
    title        VARCHAR(200) NOT NULL,
    description  TEXT,
    status       ENUM('Pending','In Progress','Resolved') DEFAULT 'Pending',
    date_filed   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")

cursor.execute("""
CREATE TABLE fees (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    roll_no      VARCHAR(20)   NOT NULL,
    receipt_id   VARCHAR(20)   NOT NULL UNIQUE,
    description  VARCHAR(200)  DEFAULT 'Semester Hostel Fee',
    total_fee    DECIMAL(10,2) NOT NULL DEFAULT 30000.00,
    amount_paid  DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    payment_mode VARCHAR(50)   DEFAULT 'Online',
    status       ENUM('Paid','Pending') DEFAULT 'Pending',
    date_paid    DATE,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (roll_no) REFERENCES students(roll_no) ON DELETE CASCADE
)""")

cursor.execute("""
CREATE TABLE notices (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    title      VARCHAR(200) NOT NULL,
    body       TEXT         NOT NULL,
    posted_by  VARCHAR(100) DEFAULT 'Admin',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)""")

conn.commit()

cursor.execute("""
    INSERT INTO admins (username, password, name, email) VALUES
    ('admin','admin123','Chief Warden','admin@hostelhub.com')
""")

cursor.executemany("""
    INSERT INTO rooms (room_no,block,floor,room_type,capacity,occupied)
    VALUES (%s,%s,%s,%s,%s,%s)""", [
    ('A-101','A',1,'Double Sharing',2,0),
    ('A-204','A',2,'Double Sharing',2,2),
    ('B-105','B',1,'Double Sharing',2,1),
    ('C-302','C',3,'Triple Sharing',3,2),
])

cursor.executemany("""
    INSERT INTO students
    (roll_no,name,email,phone,course,year,room_no,bed_no,fee_status,password)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", [
    ('CS202401','Rahul Sharma', 'rahul@example.com','9876543210','B.Tech CSE',2,'A-204',2,'Paid',   'pass123'),
    ('CS202402','Amit Patel',   'amit@example.com', '9876512345','B.Tech CSE',2,'A-204',1,'Paid',   'pass123'),
    ('EC202415','Priya Verma',  'priya@example.com','9812345678','B.Tech ECE',1,'B-105',1,'Pending','pass123'),
    ('ME202408','Rohan Gupta',  'rohan@example.com','9823456789','B.Tech ME', 3,'C-302',2,'Paid',   'pass123'),
    ('CS202405','Vikas Jain',   'vikas@example.com','9834567890','B.Tech CSE',2,'C-302',1,'Pending','pass123'),
])

cursor.executemany("""
    INSERT INTO fees
    (roll_no,receipt_id,description,total_fee,amount_paid,payment_mode,status,date_paid)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", [
    ('CS202401','REC-1001','Semester 2026 - Room and Mess Fee',30000,30000,'Online','Paid',   '2026-10-05'),
    ('CS202402','REC-1002','Semester 2026 - Room and Mess Fee',30000,30000,'Online','Paid',   '2026-10-08'),
    ('EC202415','REC-1003','Semester 2026 - Room and Mess Fee',30000,15000,'Card',  'Pending','2026-10-10'),
    ('ME202408','REC-1004','Semester 2026 - Room and Mess Fee',30000,30000,'NetBanking','Paid','2026-10-11'),
    ('CS202405','REC-1005','Semester 2026 - Room and Mess Fee',30000,0,    'Not Paid','Pending',None),
])

cursor.executemany("""
    INSERT INTO complaints
    (student_name,roll_no,room_no,category,title,description,status)
    VALUES (%s,%s,%s,%s,%s,%s,%s)""", [
    ('Rahul Sharma','CS202401','A-204','Electrical','Ceiling fan making loud noise',       'Fan regulator not working, blades vibrating.', 'In Progress'),
    ('Amit Patel',  'CS202402','B-105','Plumbing',  'Bathroom tap leaking continuously',  'Tap dripping since last night.',               'Pending'),
    ('Priya Verma', 'EC202415','C-302','Internet',  'Wi-Fi signal weak and disconnecting', 'Signal weak in the evening hours.',            'Resolved'),
    ('Rohan Gupta', 'ME202408','A-101','Cleanliness','Corridor dustbin overflowing',       'Dustbin not cleaned for 3 days.',              'Pending'),
])

cursor.executemany(
    "INSERT INTO notices (title,body,posted_by) VALUES (%s,%s,%s)", [
    ('Wi-Fi Maintenance Notice',    'Wi-Fi in Block A under maintenance from 2-4 PM today.', 'Admin'),
    ('Mess Menu Update',            'Special festival dinner this Friday at 8 PM.',           'Admin'),
    ('Hostel Night Curfew Reminder','All students must check in before 9:30 PM at main gate.','Admin'),
])

conn.commit()

print("=== DATABASE SETUP COMPLETE ===")
for table in ['admins','rooms','students','fees','complaints','notices']:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"  {table:12}: {cursor.fetchone()[0]} rows")

conn.close()
print("\nRun server: cd Backend && uvicorn app.main:app --reload")
