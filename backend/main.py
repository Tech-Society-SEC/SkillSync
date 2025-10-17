import sqlite3
from fastapi import FastAPI

app = FastAPI()

@app.get("/jobs")
def get_jobs():
    conn = sqlite3.connect("skillsync.db")
    c = conn.cursor()
    c.execute("SELECT * FROM jobs")
    jobs = c.fetchall()
    conn.close()
    return {"jobs": jobs}
