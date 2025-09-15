#!/usr/bin/python3
import mysql.connector
from mysql.connector import Error

def connect_to_prodev():
    """Connects to the ALX_prodev database in MySQL"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Replace with your MySQL username if needed
            password='',  # Replace with your MySQL password if needed
            database='ALX_prodev'
        )
        return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev database: {e}")
        return None

def stream_users():
    """
    Generator function that streams rows from user_data table one by one.
    Uses yield to return each row as a dictionary.
    """
    connection = connect_to_prodev()
    if not connection:
        return
    
    cursor = None
    try:
        # Use a buffered cursor to fetch rows one by one
        cursor = connection.cursor(buffered=True)
        
        # Execute the query
        cursor.execute("SELECT user_id, name, email, age FROM user_data")
        
        # Fetch and yield rows one by one
        row = cursor.fetchone()
        while row:
            user_dict = {
                'user_id': row[0],
                'name': row[1],
                'email': row[2],
                'age': row[3]
            }
            yield user_dict
            row = cursor.fetchone()
            
    except Error as e:
        print(f"Error streaming users: {e}")
    finally:
        # Clean up resources
        if cursor:
            cursor.close()
        if connection:
            connection.close()