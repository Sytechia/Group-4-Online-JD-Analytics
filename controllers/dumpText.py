import sqlite3

# Helper function for getting database connection
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # Optional: to access columns by name
    return conn

# Function to insert resume text into the nested_skills column where userid = 1
def insert_resume_text(userid, resume_text):
    con = get_db_connection()  # Establish connection using helper function
    cur = con.cursor()

    try:
        # Check if the user with userid 1 exists
        cur.execute("SELECT 1 FROM userdata WHERE id = ?", (userid,))
        user_exists = cur.fetchone()

        if user_exists:
            # Insert the resume text into the nested_skills column where userid = 1
            cur.execute("UPDATE userdata SET nested_skills = ? WHERE id = ?", (resume_text, userid))
            con.commit()
            print(f"Resume text successfully inserted into 'nested_skills' for user ID: {userid}")
        else:
            # If user doesn't exist, return an error for frontend to handle
            print("User ID not found. Trigger JavaScript alert for account creation.")
            return {"status": "error", "message": "User ID not found. Please create an account."}

    except sqlite3.Error as e:
        print(f"An error occurred while interacting with the database: {e}")
        return {"status": "error", "message": "Database error."}
    
    finally:
        con.close()  # Close the connection