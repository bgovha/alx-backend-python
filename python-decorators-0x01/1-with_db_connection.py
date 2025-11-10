import sqlite3
import functools

def with_db_connection(func):
    """Decorator that handles database connections"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Open connection
        conn = sqlite3.connect('users.db')
        
        try:
            # Pass connection to the function
            result = func(conn, *args, **kwargs)
            return result
        finally:
            # Always close connection, even if error occurs
            conn.close()
    
    return wrapper

@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

# Usage - notice we don't pass 'conn', the decorator does!
user = get_user_by_id(user_id=1)
print(user)