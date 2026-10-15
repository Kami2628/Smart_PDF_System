import sqlite3
import os


DATABASE_PATH = os.path.join(
    "output",
    "smart_pdf.db"
)


def get_connection():
    os.makedirs(
        "output",
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS pdf_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            operation TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id)
            REFERENCES users(id)
        )
        """
    )

    connection.commit()
    connection.close()


def create_user(username, password):

    connection = get_connection()

    cursor = connection.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO users (
                username,
                password
            )
            VALUES (?, ?)
            """,
            (
                username,
                password
            )
        )

        connection.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        connection.close()


def authenticate_user(username, password):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, username
        FROM users
        WHERE username = ?
        AND password = ?
        """,
        (
            username,
            password
        )
    )

    user = cursor.fetchone()

    connection.close()

    if user:

        return dict(user)

    return None


def add_pdf_history(
    user_id,
    file_name,
    operation
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO pdf_history (
            user_id,
            file_name,
            operation
        )
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            file_name,
            operation
        )
    )

    connection.commit()
    connection.close()


def get_pdf_history(user_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            file_name,
            operation,
            created_at
        FROM pdf_history
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,)
    )

    history = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return history