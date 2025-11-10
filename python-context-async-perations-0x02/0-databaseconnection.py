import sqlite3

class DatabaseConnection:
    """Context manager for database connections"""
    
    def __init__(self, db_name):
        """Initialize with database name"""
        self.db_name = db_name
        self.connection = None
    
    def __enter__(self):
        """
        Called when entering the 'with' block
        Opens the database connection
        Returns the connection object
        """
        print(f"Opening database connection to {self.db_name}")
        self.connection = sqlite3.connect(self.db_name)
        return self.connection
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Called when exiting the 'with' block
        Closes the database connection
        
        Parameters:
        - exc_type: Type of exception (if any occurred)
        - exc_value: Exception instance
        - traceback: Traceback object
        
        Returns False to propagate exceptions
        """
        if self.connection:
            print(f"Closing database connection to {self.db_name}")
            self.connection.close()
        
        # Return False to let exceptions propagate
        # Return True to suppress exceptions
        return False


# Usage
if __name__ == "__main__":
    # Use the context manager
    with DatabaseConnection('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        results = cursor.fetchall()
        
        print("\nUsers in database:")
        for row in results:
            print(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}")
    
    # Connection is automatically closed here
    print("\nConnection closed automatically!")