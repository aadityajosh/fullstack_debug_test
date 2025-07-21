import unittest
import json
import sqlite3
import os
import time # Import time for potential future debugging if sleep is an issue
from app import app, init_db # Import app and init_db

class FeedbackAppTestCase(unittest.TestCase):
    """This class represents the test case for the feedback API."""

    def setUp(self):
        """
        Set up a new test client and initialize a new in-memory database before each test.
        """
        app.config['TESTING'] = True
        self.client = app.test_client()

        # Store the original get_db_connection to restore it later
        self._original_get_db_connection = app.get_db_connection

        # Create a new in-memory database connection for this test
        self.test_conn = sqlite3.connect(':memory:')
        self.test_conn.row_factory = sqlite3.Row

        # Override app's get_db_connection to use our test connection
        def get_test_db_connection():
            return self.test_conn
        app.get_db_connection = get_test_db_connection

        # Initialize the database schema using the test connection
        with app.app_context():
            init_db(self.test_conn)

    def tearDown(self):
        """
        Clean up after each test.
        """
        if self.test_conn:
            self.test_conn.close()
        app.get_db_connection = self._original_get_db_connection

    # --- Tests for POST /feedback ---

    def test_post_feedback_success(self):
        payload = {"message": "This is great!", "rating": 5}
        response = self.client.post('/feedback', json=payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {"status": "ok"})

    def test_post_feedback_invalid_payload(self):
        payload = {"rating": 4}
        response = self.client.post('/feedback', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertIn("message' and 'rating' are required", response.json['error'])

        payload = {"message": "No rating here."}
        response = self.client.post('/feedback', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertIn("message' and 'rating' are required", response.json['error'])

    def test_post_feedback_invalid_rating_type(self):
        payload = {"message": "Rating is a string", "rating": "five"}
        response = self.client.post('/feedback', json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertEqual(response.json['error'], "Invalid data format: 'rating' must be an integer.")

    # --- Tests for GET /feedback ---

    def test_get_feedback_empty(self):
        response = self.client.get('/feedback')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [])

    def test_get_feedback_with_data(self):
        """Test getting feedback after posting some data."""
        # Post some data first
        post1_data = {"message": "First post", "rating": 3}
        self.client.post('/feedback', json=post1_data)
        time.sleep(0.01) # Ensure distinct timestamps for better sorting reliability

        post2_data = {"message": "Second post", "rating": 5}
        self.client.post('/feedback', json=post2_data)

        # --- DEBUGGING: Verify data directly from DB before API call ---
        with self.test_conn:
            cursor = self.test_conn.cursor()
            db_rows = cursor.execute("SELECT id, message, created_at FROM feedback ORDER BY id ASC").fetchall()
            print("\n--- DB Content Before GET (Ordered by ID) ---")
            for row in db_rows:
                print(f"ID: {row['id']}, Message: {row['message']}, Created At: {row['created_at']}")
            print("--------------------------------------------")
        # --- END DEBUGGING ---

        response = self.client.get('/feedback')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(len(data), 2)
        # Default sort is 'desc', so the second post should be first
        self.assertEqual(data[0]['message'], "Second post")
        self.assertEqual(data[1]['message'], "First post")

    def test_get_feedback_filter_by_rating(self):
        self.client.post('/feedback', json={"message": "A decent rating", "rating": 3})
        self.client.post('/feedback', json={"message": "A great rating", "rating": 5})
        self.client.post('/feedback', json={"message": "Another great one", "rating": 5})

        response = self.client.get('/feedback?rating=5')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(len(data), 2)
        for item in data:
            self.assertEqual(item['rating'], 5)

    def test_get_feedback_sort_asc(self):
        self.client.post('/feedback', json={"message": "Post A", "rating": 1})
        time.sleep(0.01)
        self.client.post('/feedback', json={"message": "Post B", "rating": 2})

        response = self.client.get('/feedback?sort=asc')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['message'], "Post A")
        self.assertEqual(data[1]['message'], "Post B")

    def test_get_feedback_sort_desc(self):
        self.client.post('/feedback', json={"message": "Post A", "rating": 1})
        time.sleep(0.01)
        self.client.post('/feedback', json={"message": "Post B", "rating": 2})

        response = self.client.get('/feedback?sort=desc')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['message'], "Post B")
        self.assertEqual(data[1]['message'], "Post A")

    def test_get_feedback_invalid_sort_parameter(self):
        self.client.post('/feedback', json={"message": "Post A", "rating": 1})
        time.sleep(0.01)
        self.client.post('/feedback', json={"message": "Post B", "rating": 2})

        response = self.client.get('/feedback?sort=invalid-value')
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertEqual(data[0]['message'], "Post B")


if __name__ == '__main__':
    unittest.main()