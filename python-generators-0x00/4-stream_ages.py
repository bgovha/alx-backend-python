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

def stream_user_ages():
    """
    Generator function that streams user ages one by one from the database.
    Yields each age as it's fetched from the database.
    """
    connection = connect_to_prodev()
    if not connection:
        return
    
    cursor = None
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("SELECT age FROM user_data")
        
        # First loop: fetch and yield ages one by one
        row = cursor.fetchone()
        while row:
            yield row[0]  # Yield the age
            row = cursor.fetchone()
            
    except Error as e:
        print(f"Error streaming user ages: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def calculate_average_age():
    """
    Calculates the average age of users using the generator.
    Processes ages one by one without loading entire dataset into memory.
    """
    total_age = 0
    count = 0
    
    # Second loop: iterate through the generator
    for age in stream_user_ages():
        total_age += age
        count += 1
    
    if count == 0:
        return 0
    
    average_age = total_age / count
    print(f"Average age of users: {average_age:.2f}")
    return average_age

if __name__ == "__main__":
    calculate_average_age()