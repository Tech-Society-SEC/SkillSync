import sqlite3
from fastapi import FastAPI

app = FastAPI()
@app.get("/")
def root():
    return {"message": "SkillSync Backend is running!"}


@app.get("/jobs")
def get_jobs():
    conn = sqlite3.connect("skillsync.db")
    c = conn.cursor()
    c.execute("SELECT * FROM jobs")
    jobs = c.fetchall()
    conn.close()
    return {"jobs": jobs}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

