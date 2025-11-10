import sqlite3
import functools

def with_db_connection(func):
    """Same as Task 1"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
            return result
        finally:
            conn.close()
    return wrapper

def transactional(func):
    """Decorator that manages transactions"""
    @functools.wraps(func)
    def wrapper(conn, *args, **kwargs):
        try:
            # Execute the function
            result = func(conn, *args, **kwargs)
            
            # If successful, commit changes
            conn.commit()
            print("Transaction committed successfully")
            return result
            
        except Exception as e:
            # If error, rollback changes
            conn.rollback()
            print(f"Transaction rolled back due to error: {e}")
            raise  # Re-raise the exception
    
    return wrapper

@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))

# Usage
update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')