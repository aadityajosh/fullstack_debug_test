# Feedback API

A simple Flask-based RESTful API for collecting and retrieving user feedback, including a message and a rating. The API supports posting new feedback and fetching existing feedback with options for sorting and filtering.

## Features

-   **Submit Feedback**: Users can submit feedback with a message and a rating.
-   **Retrieve Feedback**: Fetch all feedback entries.
-   **Sorting**: Sort feedback by `created_at` timestamp in ascending or descending order.
-   **Filtering**: Filter feedback entries by rating.
-   **SQLite Database**: Uses SQLite for data persistence.
-   **Robust Error Handling**: Provides meaningful error responses for invalid requests or server issues.
-   **Logging**: Basic logging for monitoring and debugging.
-   **Unit Tests**: Comprehensive unit tests to ensure API functionality and data integrity.

## Summary of a Major Issue Fixed

### SQL Injection Vulnerability

**Problem**: The original `get_feedback` function used an f-string to directly insert the `rating` and `sort` parameters into the SQL query: `f" WHERE rating = {rating}"`. This is a classic SQL injection vulnerability. An attacker could provide a malicious `rating` value like `1; DROP TABLE feedback` to manipulate and damage your database.

**Fix**: The corrected code uses parameterized queries (`?` placeholder). The database driver safely handles the `rating` value, preventing any malicious SQL from being executed. For the `sort` parameter, which cannot be parameterized, the fix involves validating it against a whitelist of allowed values (`'asc'`, `'desc'`) before using it in the query.

## Other Improvements That Were Made

-   **Database Connection Handling**: A `get_db_connection` function was created to centralize the connection logic and set `conn.row_factory = sqlite3.Row`. This makes the output from `fetchall()` a list of dictionary-like objects, which is more intuitive to work with and converts easily to JSON.

-   **JSON Serialization**: The response from `get_feedback` is now properly serialized to a list of dictionaries (`[dict(row) for row in feedback]`), which is the standard and expected format for a JSON API.

-   **POST Request Validation**: Added a basic check in `post_feedback` to ensure the incoming JSON data contains the required `message` and `rating` fields, returning a `400 Bad Request` error if not.

-   **Database Initialization**: Included an `init_db` function to create the `feedback` table if it doesn't exist when the application starts.

-   **Proper HTTP Status Codes**: The `post_feedback` route now returns a `201 Created` status code upon success, which is more semantically correct than the default `200 OK`.

## Frontend (`App.jsx`)

The frontend code has two main problems:

1.  **Incorrect API Requests**: It sends `rating=null` on the initial load and `rating=` when "All Ratings" is selected. This will either fail or be misinterpreted by the backend. The fetch logic should be updated to only add the `rating` parameter when a valid rating is actually selected.

2.  **Poor React Keys**: Using the array index `i` for the `key` prop is not recommended. If the data has a unique identifier (like a database ID), that should always be used.

## How to Run

### Backend

```sh
cd backend
python3 -m venv venv
source venv/bin/activate
pip install flask
python app.py

Frontend 

cd frontend
npm install
npm start