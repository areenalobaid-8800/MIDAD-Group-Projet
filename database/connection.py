
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()


def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )

        if connection.is_connected():
            print("Connected to MIDAD Database Successfully!")
            return connection

    except Error as e:
        print("Database Connection Failed:", e)

    return None


if __name__ == "__main__":
    connection = create_connection()

    if connection:
        connection.close()
        print("Database Connection Closed.")
