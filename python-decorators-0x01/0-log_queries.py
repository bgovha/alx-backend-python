import sqlite3
import functools

def log_queries(func):
    """Decorator that logs SQL queries"""
    @functools.wraps(func) 
    def wrapper(*args, **kwargs):
     
        if 'query' in kwargs:
            print(f"Executing SQL Query: {kwargs['query']}")
        elif args:
       
            for arg in args:
                if isinstance(arg, str) and 'SELECT' in arg.upper():
                    print(f"Executing SQL Query: {arg}")
                    break
        
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

users = fetch_all_users(query="SELECT * FROM users")