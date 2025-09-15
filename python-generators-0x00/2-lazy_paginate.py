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

def paginate_users(page_size, offset):
    """
    Fetches a page of users from the database with given page size and offset.
    """
    connection = connect_to_prodev()
    if not connection:
        return []
    
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM user_data LIMIT {page_size} OFFSET {offset}")
        rows = cursor.fetchall()
        return rows
    except Error as e:
        print(f"Error paginating users: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def lazy_paginate(page_size):
    """
    Generator function that lazily loads pages of users from the database.
    Only fetches the next page when needed.
    """
    offset = 0
    
    # Single loop: continue until no more pages
    while True:
        page = paginate_users(page_size, offset)
        
        # If no more results, break the loop
        if not page:
            break
        
        # Yield the current page
        yield page
        
        # Move to next page
        offset += page_size