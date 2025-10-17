import sqlite3

# Connect (or create) database
conn = sqlite3.connect("skillsync.db")
c = conn.cursor()

# Create workers table
c.execute("""
CREATE TABLE IF NOT EXISTS workers (
    worker_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    transcript TEXT,
    skills TEXT,
    experience TEXT,
    language TEXT,
    profile_card_url TEXT
)
""")

# Create jobs table
c.execute("""
CREATE TABLE IF NOT EXISTS jobs (
    job_id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_title TEXT,
    skills_required TEXT,
    location TEXT,
    pay TEXT,
    job_link TEXT
)
""")

conn.commit()
conn.close()
print("Database and tables created successfully!")
