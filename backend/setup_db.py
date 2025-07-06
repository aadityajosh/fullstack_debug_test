# setup_db.py
import sqlite3

# This will create the 'feedback.db' file if it doesn't exist
conn = sqlite3.connect('feedback.db')
cursor = conn.cursor()

print("Database connected.")

# Drop the table if it exists to ensure a clean setup
cursor.execute("DROP TABLE IF EXISTS feedback")
print("Dropped existing table (if any).")

# Create the 'feedback' table
# - id: A unique number for each entry (for React keys)
# - message: The feedback text
# - rating: The star rating (1-5)
# - created_at: A timestamp that defaults to when the feedback was added
cursor.execute("""
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT NOT NULL,
    rating INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
print("Created 'feedback' table.")


# --- Insert some sample data ---
sample_feedback = [
    ('This is an amazing product! Highly recommend.', 5),
    ('The new update is a bit buggy.', 2),
    ('Works as expected. Solid 4-star experience.', 4),
    ('Customer support was very helpful. Five stars!', 5),
    ('Absolutely terrible, would not use again.', 1)
]

cursor.executemany(
    "INSERT INTO feedback (message, rating) VALUES (?, ?)",
    sample_feedback
)
print(f"Inserted {len(sample_feedback)} sample records.")


# Save (commit) the changes and close the connection
conn.commit()
conn.close()

print("✅ Database 'feedback.db' created and populated successfully.")