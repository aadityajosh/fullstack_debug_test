# app.py - Fixed Flask backend
from flask import Flask, request, jsonify
import sqlite3

app = Flask(_name_)


@app.route("/feedback", methods=["GET"])
def get_feedback():
    conn = sqlite3.connect('feedback.db')
    # Return rows as dictionaries to include column names
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    rating = request.args.get("rating")
    sort = request.args.get("sort", "desc")

    # Validate sort parameter to prevent injection
    if sort.lower() not in ['asc', 'desc']:
        sort = 'desc'

    params = []
    query = "SELECT * FROM feedback"

    # Use parameterized query to prevent SQL injection
    if rating:
        query += " WHERE rating = ?"
        params.append(rating)

    query += f" ORDER BY created_at {sort}"

    # Execute with params and convert to list of dicts
    feedback_rows = cursor.execute(query, params).fetchall()
    feedback = [dict(row) for row in feedback_rows]

    conn.close()
    return jsonify(feedback)


@app.route("/feedback", methods=["POST"])
def post_feedback():
    data = request.get_json()
    # Basic validation
    if not data or "message" not in data or "rating" not in data:
        return jsonify({"error": "Invalid payload"}), 400

    conn = sqlite3.connect('feedback.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO feedback (message, rating) VALUES (?, ?)",
        (data["message"], data["rating"])
    )
    conn.commit()
    conn.close()
    return jsonify({"status":"ok"}),201