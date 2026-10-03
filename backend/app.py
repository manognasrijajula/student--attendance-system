from flask import Flask, jsonify, request, send_from_directory
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
   return send_from_directory(os.path.join(os.path.dirname(__file__), ".."), "dashboard.html")
@app.route("/students")
def students():
    cursor=db.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()
    cursor.close()
    return jsonify(data)

@app.route("/attendance")
def attendance():
    cursor=db.cursor(cursor_factory=RealDictCursor)
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

    try:
        sql = """
        INSERT INTO students
        (student_id, student_name, roll_number, course, year)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(
            sql,
            (student_id, student_name, student_id, course, year)
        )

        db.commit()

        return jsonify({
            "message": "Student added successfully!"
        })

    except psycopg2.errors.UniqueViolation:
        db.rollback()

        return jsonify({
            "error": "Student ID already exists"
        }), 409

    except Exception as e:
        db.rollback()

        return jsonify({
            "error": str(e)
        }), 500

    finally:
        cursor.close()
@app.route("/reports")
def reports():
   cursor=db.cursor(cursor_factory=RealDictCursor)
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
@app.route("/<path:filename>")
def serve_files(filename):
    return send_from_directory(
        os.path.join(os.path.dirname(__file__), ".."),
        filename
    )
if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

