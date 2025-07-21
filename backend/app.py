import logging
import sqlite3
from flask import Flask, request, jsonify

# --- 1. Configure Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# --- Database configuration ---
# Default to a file-based database. This will be overridden for testing.
app.config['DATABASE'] = 'feedback.db'

# --- Helper Function for DB Connection ---
def _get_db_connection():
    try:
        # Use the database path from app.config
        db_path = app.config.get('DATABASE', 'feedback.db')
        logging.info(f"Attempting to connect to database: {db_path}")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        return None

# Assign the helper function to the app instance for consistent access
app.get_db_connection = _get_db_connection

# --- DB Initialization ---
# Modified to accept a connection, and not close it within this function.
def init_db(conn):
    if conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message TEXT NOT NULL,
                rating INTEGER NOT NULL
            )
        ''')
        conn.commit()
        logging.info("Database initialized successfully.")
    else:
        logging.error("Failed to get database connection during initialization.")


# --- GET /feedback Route ---
@app.route("/feedback", methods=["GET"])
def get_feedback():
    logging.info(f"GET /feedback request with args: {request.args}")
    try:
        # Use app.get_db_connection, which now respects app.config['DATABASE']
        with app.get_db_connection() as conn:
            if conn is None:
                logging.error("GET /feedback: Database connection is None.")
                return jsonify({"error": "Could not connect to the database"}), 500

            cursor = conn.cursor()
            rating = request.args.get("rating")
            sort = request.args.get("sort", "desc")

            if sort.lower() not in ['asc', 'desc']:
                logging.warning(f"Invalid sort parameter '{sort}' received. Defaulting to 'desc'.")
                sort = 'desc'

            params = []
            query = "SELECT * FROM feedback"

            if rating:
                try:
                    rating = int(rating)
                    query += " WHERE rating = ?"
                    params.append(rating)
                except ValueError:
                    logging.warning(f"Invalid rating parameter '{request.args.get('rating')}' received.")
                    return jsonify({"error": "Invalid rating format. Must be an integer."}), 400

            # Corrected: Add id as a secondary sort key to handle identical timestamps
            query += f" ORDER BY created_at {sort}, id {sort}"

            feedback_rows = cursor.execute(query, params).fetchall()
            return jsonify([dict(row) for row in feedback_rows])

    except sqlite3.Error as e:
        logging.error(f"Database error occurred in get_feedback: {e}")
        return jsonify({"error": "A database error occurred."}), 500
    except Exception as e:
        logging.error(f"An unexpected server error occurred in get_feedback: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

# --- POST /feedback Route ---
@app.route("/feedback", methods=["POST"])
def post_feedback():
    logging.info("POST /feedback request received")
    data = request.get_json()

    if not data or "message" not in data or "rating" not in data:
        logging.warning("POST /feedback request with missing 'message' or 'rating'.")
        return jsonify({"error": "Invalid payload: 'message' and 'rating' are required."}), 400

    try:
        message = str(data["message"])
        rating = int(data["rating"])
    except (ValueError, TypeError):
        logging.warning(f"Invalid data type for rating: {data.get('rating')}")
        return jsonify({"error": "Invalid data format: 'rating' must be an integer."}), 400

    try:
        with app.get_db_connection() as conn:
            if conn is None:
                logging.error("POST /feedback: Database connection is None.")
                return jsonify({"error": "Could not connect to the database"}), 500

            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO feedback (message, rating) VALUES (?, ?)",
                (message, rating)
            )
            conn.commit()
            logging.info(f"Successfully inserted new feedback with rating: {rating}")
            return jsonify({"status": "ok"}), 201

    except sqlite3.Error as e:
        logging.error(f"Database error on insert: {e}")
        return jsonify({"error": "A database error occurred while saving feedback."}), 500
    except Exception as e:
        logging.error(f"An unexpected server error occurred on post: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

if __name__ == '__main__':
    # When running the app directly, get a connection and pass it to init_db
    conn_for_init = app.get_db_connection()
    if conn_for_init:
        init_db(conn_for_init)
        conn_for_init.close() # Close connection after initialization
    else:
        logging.error("Failed to get a database connection to initialize the DB on app startup.")

    app.run(debug=True)