import sqlite3
import json

# Connect to database
conn = sqlite3.connect("skillsync.db")
c = conn.cursor()

# Sample jobs
jobs = [
    ("Mason", json.dumps(["Masonry", "Brickwork"]), "Delhi", "₹15000", "http://apply1.com"),
    ("Carpenter", json.dumps(["Wood Cutting", "Carpentry"]), "Chennai", "₹12000", "http://apply2.com"),
    ("Electrician", json.dumps(["Electrical Safety", "Wiring"]), "Bangalore", "₹14000", "http://apply3.com")
]

# Insert into jobs table
c.executemany("""
INSERT INTO jobs (job_title, skills_required, location, pay, job_link)
VALUES (?, ?, ?, ?, ?)
""", jobs)

conn.commit()
conn.close()
print("Dummy jobs inserted successfully!")
