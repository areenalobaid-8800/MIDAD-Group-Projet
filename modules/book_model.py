
from mysql.connector import Error
from database.connection import create_connection


# ================= SEARCH BOOKS =================

def search_books(search_text):

    connection = create_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT
                Books.Book_ID,
                Books.Title,
                Books.Author,
                Books.Description,
                Books.Total_Copies,
                Books.Available_Copies,
                Categories.Category_Name
            FROM Books
            LEFT JOIN Categories
                ON Books.Category_ID = Categories.Category_ID
            WHERE Books.Title LIKE %s
               OR Books.Author LIKE %s
            ORDER BY Books.Title
            LIMIT 10
        """

        search_value = f"%{search_text}%"

        cursor.execute(
            query,
            (search_value, search_value)
        )

        return cursor.fetchall()

    except Error as e:
        print("Book Search Error:", e)
        return []

    finally:
        cursor.close()
        connection.close()


# ================= MOST BORROWED BOOKS =================

def get_most_borrowed_books():

    connection = create_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        query = """
            SELECT
                Books.Book_ID,
                Books.Title,
                Books.Author,
                Books.Cover_Image,
                COUNT(Borrowings.Borrowing_ID) AS Borrowing_Count
            FROM Books
            LEFT JOIN Borrowings
                ON Books.Book_ID = Borrowings.Book_ID
            GROUP BY
                Books.Book_ID,
                Books.Title,
                Books.Author,
                Books.Cover_Image
            ORDER BY
                Borrowing_Count DESC,
                Books.Title ASC
            LIMIT 3
        """

        cursor.execute(query)

        return cursor.fetchall()

    except Error as e:
        print("Most Borrowed Books Error:", e)
        return []

    finally:
        cursor.close()
        connection.close()


# ================= ADD TO FAVORITES =================

def add_to_favorites(user_id, book_id):

    connection = create_connection()

    if connection is None:
        return "error"

    cursor = connection.cursor()

    try:
        query = """
            INSERT INTO Favorites (User_ID, Book_ID)
            VALUES (%s, %s)
        """

        cursor.execute(
            query,
            (user_id, book_id)
        )

        connection.commit()

        return "added"

    except Error as e:

        connection.rollback()

        # Duplicate favorite
        if e.errno == 1062:
            return "exists"

        print("Add Favorite Error:", e)
        return "error"

    finally:
        cursor.close()
        connection.close()


# ================= BORROW BOOK =================

def borrow_book(user_id, book_id):

    connection = create_connection()

    if connection is None:
        return "error"

    cursor = connection.cursor()

    try:
        # Check and decrease available copies
        update_query = """
            UPDATE Books
            SET Available_Copies = Available_Copies - 1
            WHERE Book_ID = %s
              AND Available_Copies > 0
        """

        cursor.execute(
            update_query,
            (book_id,)
        )

        # No available copies
        if cursor.rowcount == 0:
            connection.rollback()
            return "unavailable"

        # Register the borrowing
        insert_query = """
            INSERT INTO Borrowings (
                User_ID,
                Book_ID,
                Borrow_Date,
                Due_Date,
                Status
            )
            VALUES (
                %s,
                %s,
                CURDATE(),
                DATE_ADD(CURDATE(), INTERVAL 7 DAY),
                'Borrowed'
            )
        """

        cursor.execute(
            insert_query,
            (user_id, book_id)
        )

        connection.commit()

        return "success"

    except Error as e:

        connection.rollback()

        print("Borrow Book Error:", e)
        return "error"

    finally:
        cursor.close()
        connection.close()
