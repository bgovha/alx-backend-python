import sqlite3
import functools

def log_queries(func):
    """Decorator that logs SQL queries"""
    @functools.wraps(func)  # Preserves original function's metadata
    def wrapper(*args, **kwargs):
        # Find the 'query' argument
        # It could be in args or kwargs
        if 'query' in kwargs:
            print(f"Executing SQL Query: {kwargs['query']}")
        elif args:
            # Check if first argument might be the query
            for arg in args:
                if isinstance(arg, str) and 'SELECT' in arg.upper():
                    print(f"Executing SQL Query: {arg}")
                    break
        
        # Call the original function
        return func(*args, **kwargs)
    
    return wrapper

@log_queries
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# Usage
users = fetch_all_users(query="SELECT * FROM users")