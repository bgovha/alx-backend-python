import time
import sqlite3
import functools

def with_db_connection(func):
    """Same as before"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            result = func(conn, *args, **kwargs)
            return result
        finally:
            conn.close()
    return wrapper

def retry_on_failure(retries=3, delay=2):
    """Decorator that retries on failure"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            
            while attempt < retries:
                try:
                    # Try to execute the function
                    result = func(*args, **kwargs)
                    return result
                    
                except Exception as e:
                    attempt += 1
                    print(f"Attempt {attempt} failed: {e}")
                    
                    if attempt < retries:
                        print(f"Retrying in {delay} seconds...")
                        time.sleep(delay)  # Wait before retrying
                    else:
                        print("All retries failed")
                        raise  # Re-raise after all retries exhausted
        
        return wrapper
    return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

# Usage
users = fetch_users_with_retry()
print(users)