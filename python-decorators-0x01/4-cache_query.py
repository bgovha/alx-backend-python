import time
import sqlite3
import functools

query_cache = {}

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

def cache_query(func):
    """Decorator that caches query results"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key from the query
        # The query is in kwargs
        query = kwargs.get('query', '')
        
        # Check if result is already cached
        if query in query_cache:
            print(f"Using cached result for query: {query}")
            return query_cache[query]
        
        # If not cached, execute the function
        print(f"Executing query and caching result: {query}")
        result = func(*args, **kwargs)
        
        # Store result in cache
        query_cache[query] = result
        
        return result
    
    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

# First call - queries database
users = fetch_users_with_cache(query="SELECT * FROM users")

# Second call - uses cached result (instant!)
users_again = fetch_users_with_cache(query="SELECT * FROM users")