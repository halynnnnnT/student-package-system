from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from datetime import datetime

app = Flask(__name__)
CORS(app)  # 允許跨域請求

import db_config

# 現在你可以使用 db_config.DB_CONFIG 來存取資料庫配置
db_settings = db_config.DB_CONFIG

host = db_settings['host']
user = db_settings['user']
password = db_settings['password']
database = db_settings['database']

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config.DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

# --- API 端點 ---

# 獲取所有學生 (供管理者選擇)
@app.route('/api/students', methods=['GET'])
def get_students():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, student_id, name, room_num FROM student_list ORDER BY student_id")
    students = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(students)

@app.route('/api/packages/add', methods=['POST'])
def add_package():
    data = request.get_json()
    student_db_id = data.get('student_db_id')
    package_description = data.get('package_description')
    # Get the quantity, default to 1 if not provided or invalid
    try:
        quantity = int(data.get('quantity', 1))
        if quantity < 1: # Ensure quantity is at least 1
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1


    if not student_db_id or not package_description:
        return jsonify({'error': 'Missing student_db_id or package_description'}), 400
    
    # If package_description is an empty string from frontend, and you want it to be NULL in DB:
    if package_description == "":
        package_description = None # Explicitly set to None for DB NULL

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor()
    try:
        # Added 'quantity' to the INSERT statement
        sql = "INSERT INTO packages (student_db_id, package_description, status, quantity) VALUES (%s, %s, %s, %s)"
        val = (student_db_id, package_description, 'pending', quantity) # Added quantity here
        cursor.execute(sql, val)
        conn.commit()
        package_id = cursor.lastrowid
        cursor.close()
        conn.close()
        return jsonify({'message': 'Package added successfully', 'package_id': package_id, 'quantity': quantity}), 201
    except mysql.connector.Error as err:
        conn.rollback()
        cursor.close()
        conn.close()
        print(f"Error in add_package: {err}")
        return jsonify({'error': 'Failed to add package'}), 500


@app.route('/api/packages/pending', methods=['GET']) # For Admin page primarily
def get_all_pending_packages():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    # Added p.quantity to the SELECT statement
    query = """
    SELECT p.id, p.package_description, p.arrival_date, p.quantity,
           s.student_id, s.room_num, s.name as student_name
    FROM packages p
    JOIN student_list s ON p.student_db_id = s.id
    WHERE p.status = 'pending'
    ORDER BY p.arrival_date DESC
    """
    cursor.execute(query)
    packages = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(packages)

@app.route('/api/packages/pending/me', methods=['GET']) # For StudentPickUpPage
# @jwt_required() # If using JWT
def get_my_pending_packages():
    # current_user_db_id = get_jwt_identity() # With JWT
    student_db_id = request.args.get('student_db_id', type=int) # Temporary
    if student_db_id is None: # Temporary
        return jsonify({'error': 'student_db_id query parameter is required (temporary)'}), 400
    current_user_db_id = student_db_id # Temporary

    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    # Added p.quantity to the SELECT statement
    query = """
    SELECT p.id, p.package_description, p.arrival_date, p.quantity,
           s.student_id, s.room_num, s.name as student_name
    FROM packages p
    JOIN student_list s ON p.student_db_id = s.id
    WHERE p.status = 'pending' AND p.student_db_id = %s
    ORDER BY p.arrival_date DESC
    """
    try:
        cursor.execute(query, (current_user_db_id,))
        packages = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify(packages)
    except mysql.connector.Error as err:
        cursor.close()
        conn.close()
        print(f"Error in get_my_pending_packages: {err}")
        return jsonify({'error': 'Failed to retrieve packages for current user'}), 500


@app.route('/api/packages/pickup/<int:package_id>', methods=['POST'])
# @jwt_required() # Potentially
def pickup_package(package_id):
    # (Your existing pickup logic - quantity doesn't directly affect pickup status change)
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT student_db_id FROM packages WHERE id = %s AND status = 'pending'", (package_id,))
        package_to_pickup = cursor.fetchone()

        if not package_to_pickup:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Package not found or already picked up'}), 404

        update_cursor = conn.cursor()
        sql = "UPDATE packages SET status = %s, pickup_timestamp = %s WHERE id = %s"
        val = ('picked_up', datetime.now(), package_id)
        update_cursor.execute(sql, val)
        conn.commit()

        if update_cursor.rowcount == 0:
            update_cursor.close()
            cursor.close()
            conn.close()
            return jsonify({'error': 'Package not found or failed to update'}), 404

        update_cursor.close()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Package picked up successfully'}), 200
    except mysql.connector.Error as err:
        conn.rollback()
        if 'cursor' in locals() and cursor.close: cursor.close()
        if 'update_cursor' in locals() and update_cursor.close: update_cursor.close()
        conn.close()
        print(f"Error in pickup_package: {err}")
        return jsonify({'error': 'Failed to pickup package'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)