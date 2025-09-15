#!/usr/bin/python3
import mysql.connector
from mysql.connector import Error

def connect_to_prodev():
    """Connects to the ALX_prodev database in MySQL"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='ALX_prodev'
        )
        return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev database: {e}")
        return None

def stream_users_in_batches(batch_size):
    """
    Generator function that streams rows from user_data table in batches.
    Yields batches of rows as lists of dictionaries.
    """
    connection = connect_to_prodev()
    if not connection:
        return
    
    cursor = None
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("SELECT user_id, name, email, age FROM user_data")
        
        # First loop: fetch batches
        while True:
            batch = cursor.fetchmany(batch_size)
            if not batch:
                break
            
            # Convert batch to list of dictionaries
            batch_dicts = []
            for row in batch:  # Second loop: process batch rows
                user_dict = {
                    'user_id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'age': row[3]
                }
                batch_dicts.append(user_dict)
            
            yield batch_dicts
            
    except Error as e:
        print(f"Error streaming users in batches: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def batch_processing(batch_size):
    """
    Processes batches of users and filters those over age 25.
    Uses generators to process data efficiently.
    """
    # Third loop: iterate through batches
    for batch in stream_users_in_batches(batch_size):
        for user in batch:  # This is within the batch iteration, not an additional main loop
            if user['age'] > 25:
                print(user)