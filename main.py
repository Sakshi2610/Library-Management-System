from fastapi import FastAPI, HTTPException, Query, Path
from pymongo import MongoClient
from pydantic import BaseModel, Field

app = FastAPI()

client = MongoClient("mongodb+srv://sakshirane:Yadnesh28@library-management.kp8aoei.mongodb.net/")
db = client["library-management-system"]

class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    id: int
    name: str
    age: int
    address: Address

@app.post("/students", status_code=201)
def create_student(student: Student):
    last_student = db.students.find_one(sort=[("id", -1)])
    last_id = last_student["id"] if last_student else 0
    
    student_id = last_id + 1
    student.id = student_id

    db.students.insert_one(student.dict())
    return {"id": student_id}

@app.get("/students")
def list_students(country: str = Query(None), age: int = Query(None)):
    query = {}
    if country:
        query["address.country"] = country
    if age:
        query["age"] = {"$gte": age}
    students = list(db.students.find(query, {"_id": 0}))
    return {"data": students}

@app.get("/students/{student_id}")
def get_student(student_id: int = Path(...)):
    student = db.students.find_one({"id": student_id}, {"_id": 0})
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

from fastapi import FastAPI, HTTPException, Response

@app.patch("/students/{student_id}", status_code=204)
def update_student(student_id: int, student: Student):
    updated_student = db.students.update_one({"id": student_id}, {"$set": student.dict()})
    if not updated_student.modified_count:
        raise HTTPException(status_code=404, detail="Student not found")

@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    deleted_student = db.students.delete_one({"id": student_id})
    if not deleted_student.deleted_count:
        raise HTTPException(status_code=404, detail="Student not found")
