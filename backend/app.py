from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import os

app = Flask(__name__)
CORS(app)

# MySQL connection
db = mysql.connector.connect(
    host="localhost",
    port=3307,
    user="root",
    password=os.getenv("MYSQL_PASSWORD"),
    database="student_attendance"
)


@app.route("/")
def home():
    return "Student Attendance System Backend is Running!"
@app.route("/students")
def students():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)

@app.route("/attendance")
def attendance():
    cursor = db.cursor(dictionary=True)
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
    cursor = db.cursor(dictionary=True)

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
