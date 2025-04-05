#!/usr/bin/env python
# coding: utf-8

import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",          # Change if needed
    password="Yyaasshhnk#@2511",  # Replace with your actual password
    database="chatbot_db",
    use_pure=True
)

cursor = conn.cursor()

# Create Database if not exists
cursor.execute("CREATE DATABASE IF NOT EXISTS chatbot_db;")
cursor.execute("USE chatbot_db;")

# Table creation queries
tables = {
    "weather": """
        CREATE TABLE IF NOT EXISTS weather (
            id INT AUTO_INCREMENT PRIMARY KEY,
            input_pattern VARCHAR(255) NOT NULL,
            response TEXT NOT NULL
        )
    """,
    "maths": """
        CREATE TABLE IF NOT EXISTS maths (
            id INT AUTO_INCREMENT PRIMARY KEY,
            input_pattern VARCHAR(255) NOT NULL,
            response TEXT NOT NULL
        )
    """,
    "travel": """
        CREATE TABLE IF NOT EXISTS travel (
            id INT AUTO_INCREMENT PRIMARY KEY,
            input_pattern VARCHAR(255) NOT NULL,
            response TEXT NOT NULL
        )
    """,
    "general_convo": """
        CREATE TABLE IF NOT EXISTS general_convo (
            id INT AUTO_INCREMENT PRIMARY KEY,
            input_pattern VARCHAR(255) NOT NULL,
            response TEXT NOT NULL
        )
    """,
    "time_date": """
        CREATE TABLE IF NOT EXISTS time_date (
            id INT AUTO_INCREMENT PRIMARY KEY,
            input_pattern VARCHAR(255) NOT NULL,
            response TEXT NOT NULL
        )
    """,
    "chat_history": """
        CREATE TABLE IF NOT EXISTS chat_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
}

# Creating tables
for table_name, table_query in tables.items():
    cursor.execute(table_query)

# Insert sample data
sample_data = {
    "weather": [
        ("What is the weather in ?", "The weather in DYNAMIC_PLACE is DYNAMIC_WEATHER."),
        ("Will it rain in ?", "The rain probability in DYNAMIC_PLACE is DYNAMIC_RAIN_CHANCE."),
        ("Is it cold in ?", "The temperature in DYNAMIC_PLACE is DYNAMIC_TEMPERATURE.")
    ],
    "maths": [
        ("What is [num1] + [num2]?", "[num1] + [num2] = DYNAMIC_SUM."),
        ("What is [num1] - [num2]?", "[num1] - [num2] = DYNAMIC_DIFFERENCE."),
        ("What is [num1] * [num2]?", "[num1] * [num2] = DYNAMIC_PRODUCT."),
        ("What is [num1] / [num2]?", "[num1] / [num2] = DYNAMIC_QUOTIENT.")
    ],
    "travel": [
        ("How far is [place1] from [place2]?", "The distance between [place1] and [place2] is DYNAMIC_DISTANCE km."),
        ("How can I go from [place1] to [place2]?", "You can travel from [place1] to [place2] via DYNAMIC_TRAVEL_MODE."),
        ("How long does it take to go from [place1] to [place2]?", "It takes approximately DYNAMIC_TRAVEL_TIME to travel from [place1] to [place2].")
    ],
    "general_convo": [
        ("How are you?", "I am just a bot, but I am doing great! How can I assist you?"),
        ("What is your name?", "I am Chatbot, your virtual assistant."),
        ("Tell me a joke.", "Why did the scarecrow win an award? Because he was outstanding in his field!"),
        ("hi", "Hello, how are you doing!"),
        ("hello", "Hello, how are you doing!"),
        ("hey", "Hello, how are you doing!")
    ],
    "time_date": [
        ("What is the current time?", "The current time is DYNAMIC_TIME."),
        ("What is today’s date?", "Today’s date is DYNAMIC_DATE."),
        ("What day is it today?", "Today is DYNAMIC_DAY.")
    ]
}

# Insert data into tables
for table_name, data in sample_data.items():
    cursor.execute(f"TRUNCATE TABLE {table_name};")
    query = f"INSERT INTO {table_name} (input_pattern, response) VALUES (%s, %s)"
    cursor.executemany(query, data)

# Commit changes
conn.commit()

# Show all tables
cursor.execute("SHOW TABLES;")
tables = cursor.fetchall()
print("Tables in the database:")
for table in tables:
    print(table[0])

# Retrieve data from all tables
for table_name in sample_data.keys():
    cursor.execute(f"SELECT * FROM {table_name};")
    rows = cursor.fetchall()
    print(f"\nData from {table_name}:")
    for row in rows:
        print(row)

# Close connection
cursor.close()
conn.close()

print("\nDatabase setup completed successfully.")