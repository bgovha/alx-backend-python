import sqlite3

class ExecuteQuery:
    """
    Context manager that handles connection and executes a query
    """
    
    def __init__(self, db_name, query, params=None):
        """
        Initialize with database name, query, and optional parameters
        
        Args:
            db_name: Name of the database file
            query: SQL query to execute
            params: Tuple of parameters for the query (optional)
        """
        self.db_name = db_name
        self.query = query
        self.params = params if params else ()
        self.connection = None
        self.cursor = None
        self.results = None
    
    def __enter__(self):
        """
        Opens connection, executes query, and returns results
        """
        print(f"Connecting to database: {self.db_name}")
        
        # Open connection
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()
        
        # Execute query
        print(f"Executing query: {self.query}")
        print(f"With parameters: {self.params}")
        
        self.cursor.execute(self.query, self.params)
        
        # Fetch results
        self.results = self.cursor.fetchall()
        
        # Return results to the 'as' variable
        return self.results
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Closes cursor and connection
        """
        if self.cursor:
            self.cursor.close()
        
        if self.connection:
            self.connection.close()
            print("Connection closed")
        
        # Return False to propagate any exceptions
        return False


# Usage
if __name__ == "__main__":
    # Query users older than 25
    query = "SELECT * FROM users WHERE age > ?"
    param = (25,)  # Note: must be a tuple, even for single parameter
    
    with ExecuteQuery('users.db', query, param) as results:
        print("\nUsers older than 25:")
        for row in results:
            print(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}")
    
    print("\n" + "="*50)
    
    # Another example: Get all users
    with ExecuteQuery('users.db', "SELECT * FROM users") as results:
        print("\nAll users:")
        for row in results:
            print(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}")