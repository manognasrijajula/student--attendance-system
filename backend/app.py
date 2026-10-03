from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)
CORS(app)

db = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=5432,
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    dbname="postgres",
    sslmode="require"
)


@app.route("/")
def home():
    return "Student Attendance System Backend is Running!"
@app.route("/students")
def students():
    db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)

@app.route("/attendance")
def attendance():
    db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT 
            students.student_name,
            students.roll_number,
            attendance.attendance_date,
            attendance.status
        FROM students
        JOIN attendance
        ON students.student_id = attendance.student_id
    """)
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)
@app.route("/mark_attendance", methods=["POST"])
def mark_attendance():

    data = request.json

    student_id = data["student_id"]
    attendance_date = data["attendance_date"]
    status = data["status"]

    cursor = db.cursor()

    sql = """
    INSERT INTO attendance
    (student_id, attendance_date, status)
    VALUES (%s, %s, %s)
    """

    cursor.execute(
        sql,
        (student_id, attendance_date, status)
    )

    db.commit()
    cursor.close()

    return jsonify({
        "message": "Attendance marked successfully!"
    })
@app.route("/add_student", methods=["POST"])
def add_student():
    data = request.json

    student_id = data["student_id"]
    student_name = data["student_name"]
    course = data["course"]
    year = data["year"]

    cursor = db.cursor()

    sql = """
    INSERT INTO students (student_id, student_name, course, year)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(sql, (student_id, student_name, course, year))
    db.commit()

    cursor.close()

    return jsonify({"message": "Student added successfully!"})
@app.route("/reports")
def reports():
   db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("""
        SELECT 
            students.student_id,
            students.student_name,
            students.roll_number,
            students.course,
            students.year,
            COUNT(attendance.student_id) AS total_classes,
            SUM(CASE WHEN attendance.status = 'Present' THEN 1 ELSE 0 END) AS present,
            SUM(CASE WHEN attendance.status = 'Absent' THEN 1 ELSE 0 END) AS absent
        FROM students
        LEFT JOIN attendance
        ON students.student_id = attendance.student_id
        GROUP BY 
            students.student_id,
            students.student_name,
            students.roll_number,
            students.course,
            students.year
    """)

    data = cursor.fetchall()
    cursor.close()

    return jsonify(data)
if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))