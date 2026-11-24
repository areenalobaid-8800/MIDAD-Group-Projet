
import bcrypt
from mysql.connector import Error
from database.connection import create_connection


def authenticate_user(email, password):
    connection = create_connection()

    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT User_ID, Name, Email, Password, Role
            FROM Users
            WHERE Email = %s
        """

        cursor.execute(query, (email,))
        user = cursor.fetchone()

        if user is None:
            print("Email not found.")
            return None

        stored_password = user["Password"]

        # Check hashed passwords
        if stored_password.startswith("$2"):
            password_is_valid = bcrypt.checkpw(
                password.encode("utf-8"),
                stored_password.encode("utf-8")
            )

        # Support existing plain-text passwords
        else:
            password_is_valid = password == stored_password

            # Convert the password to a secure hash after successful login
            if password_is_valid:
                hashed_password = bcrypt.hashpw(
                    password.encode("utf-8"),
                    bcrypt.gensalt()
                ).decode("utf-8")

                update_query = """
                    UPDATE Users
                    SET Password = %s
                    WHERE User_ID = %s
                """

                cursor.execute(
                    update_query,
                    (hashed_password, user["User_ID"])
                )
                connection.commit()

        if password_is_valid:
            user.pop("Password")
            print("Login successful!")
            return user

        print("Incorrect password.")
        return None

    except Error as e:
        print("Login error:", e)
        return None

    finally:
        cursor.close()
        connection.close()
