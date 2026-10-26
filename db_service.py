import os
import pymysql
import hashlib
from dotenv import load_dotenv

load_dotenv(override=True)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )


def create_tables():

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    cognito_sub VARCHAR(255) NOT NULL UNIQUE,
                    email VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Files table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    filename VARCHAR(255) NOT NULL,
                    s3_key VARCHAR(500) NOT NULL,
                    file_hash CHAR(64) NOT NULL,
                    file_size BIGINT,
                    file_type VARCHAR(100),
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                    FOREIGN KEY (user_id)
                    REFERENCES users(id)
                    ON DELETE CASCADE,

                    UNIQUE KEY unique_user_file_hash
                    (user_id, file_hash)
                )
            """)

        connection.commit()

        print("RDS tables created successfully!")

    finally:
        connection.close()


def test_connection():

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT DATABASE() AS database_name;"
            )

            result = cursor.fetchone()

            print(
                "Connected to database:",
                result["database_name"]
            )

    finally:
        connection.close()

def get_or_create_user(cognito_sub, email):

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            # Check whether user already exists
            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE cognito_sub = %s
                """,
                (cognito_sub,)
            )

            user = cursor.fetchone()

            if user:
                return user["id"]

            # Create new user
            cursor.execute(
                """
                INSERT INTO users
                (cognito_sub, email)
                VALUES (%s, %s)
                """,
                (cognito_sub, email)
            )

            connection.commit()

            return cursor.lastrowid

    finally:
        connection.close()
        
def file_exists_for_user(user_id, file_hash):

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT id, filename
                FROM files
                WHERE user_id = %s
                AND file_hash = %s
                """,
                (user_id, file_hash)
            )

            return cursor.fetchone()

    finally:
        connection.close()

def get_file_for_user(user_id, s3_key):

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT *
                FROM files
                WHERE user_id = %s
                AND s3_key = %s
                """,
                (user_id, s3_key)
            )

            return cursor.fetchone()

    finally:
        connection.close()

def save_file_metadata(
    user_id,
    filename,
    s3_key,
    file_hash,
    file_size,
    file_type
):

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO files
                (
                    user_id,
                    filename,
                    s3_key,
                    file_hash,
                    file_size,
                    file_type
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    filename,
                    s3_key,
                    file_hash,
                    file_size,
                    file_type
                )
            )

        connection.commit()

    finally:
        connection.close()  
        
def delete_file_metadata(user_id, s3_key):

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM files
                WHERE user_id = %s
                AND s3_key = %s
                """,
                (user_id, s3_key)
            )

        connection.commit()

    finally:
        connection.close()
        
if __name__ == "__main__":

    test_connection()
    create_tables()