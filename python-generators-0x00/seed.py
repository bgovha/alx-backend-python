#!/usr/bin/python3
import mysql.connector
import csv
import uuid
from mysql.connector import Error

def connect_db():
    """Connects to the MySQL database server"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password=''
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def create_database(connection):
    """Creates the database ALX_prodev if it does not exist"""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
        print("Database ALX_prodev created or already exists")
        cursor.close()
    except Error as e:
        print(f"Error creating database: {e}")

def connect_to_prodev():
    """Connects to the ALX_prodev database in MySQL"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Replace with your MySQL username
            password='',  # Replace with your MySQL password
            database='ALX_prodev'
        )
        return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev database: {e}")
        return None

def create_table(connection):
    """Creates a table user_data if it does not exist with the required fields"""
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(3,0) NOT NULL,
            INDEX idx_user_id (user_id)
        )
        """
        cursor.execute(create_table_query)
        print("Table user_data created successfully")
        cursor.close()
    except Error as e:
        print(f"Error creating table: {e}")

def insert_data(connection, csv_file):
    """Inserts data from CSV file into the database if it does not exist"""
    try:
        cursor = connection.cursor()
        
        # Read CSV file
        with open(csv_file, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header row
            
            for row in csv_reader:
                user_id, name, email, age = row
                
                # Check if record already exists
                check_query = "SELECT user_id FROM user_data WHERE user_id = %s"
                cursor.execute(check_query, (user_id,))
                result = cursor.fetchone()
                
                if not result:
                    # Insert new record
                    insert_query = """
                    INSERT INTO user_data (user_id, name, email, age)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (user_id, name, email, int(age)))
        
        connection.commit()
        print("Data inserted successfully")
        cursor.close()
        
    except Error as e:
        print(f"Error inserting data: {e}")
    except FileNotFoundError:
        print(f"CSV file {csv_file} not found")