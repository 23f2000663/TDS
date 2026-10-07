import csv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)

students = []

with open("q-fastapi.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        students.append({
            "studentId": int(row["studentId"]),
            "class": row["class"]
        })

@app.get("/api")
def get_students(class_: Optional[List[str]] = Query(default=None, alias="class")):
    if not class_:
        return {"students": students}

    filtered = [
        student
        for student in students
        if student["class"] in class_
    ]

    return {"students": filtered}