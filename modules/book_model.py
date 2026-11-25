from mysql.connector import Error
from database.connection import create_connection


# ================= WAITING LIST HELPERS =================

def _promote_waiting_users(cursor, book_id):
    """
    Assign available copies to waiting users in request order.
    Reserved copies are deducted from Available_Copies.
    """

    while True:

        cursor.execute("""
            SELECT Available_Copies
            FROM Books
            WHERE Book_ID = %s
            FOR UPDATE
        """, (book_id,))

        book = cursor.fetchone()

        if book is None or book[0] <= 0:
            break

        cursor.execute("""
            SELECT Waiting_ID
            FROM Waiting_List
            WHERE Book_ID = %s
              AND Status = 'Waiting'
            ORDER BY Request_Date ASC, Waiting_ID ASC
            LIMIT 1
            FOR UPDATE
        """, (book_id,))

        waiting_user = cursor.fetchone()

        if waiting_user is None:
            break

        waiting_id = waiting_user[0]

        cursor.execute("""
            UPDATE Books
            SET Available_Copies = Available_Copies - 1
            WHERE Book_ID = %s
              AND Available_Copies > 0
        """, (book_id,))

        if cursor.rowcount == 0:
            break

        cursor.execute("""
            UPDATE Waiting_List
            SET
                Status = 'Ready for Pickup',
                Pickup_Deadline = DATE_ADD(NOW(), INTERVAL 3 DAY)
            WHERE Waiting_ID = %s
              AND Status = 'Waiting'
        """, (waiting_id,))


def _process_expired_reservations(cursor):
    """
    Expire reservations whose pickup deadline has passed.
    Release their reserved copies and promote the next users.
    """

    cursor.execute("""
        SELECT Waiting_ID, Book_ID
        FROM Waiting_List
        WHERE Status = 'Ready for Pickup'
          AND Pickup_Deadline <= NOW()
        ORDER BY Pickup_Deadline ASC, Waiting_ID ASC
        FOR UPDATE
    """)

    expired_reservations = cursor.fetchall()

    for waiting_id, book_id in expired_reservations:

        cursor.execute("""
            UPDATE Waiting_List
            SET Status = 'Expired'
            WHERE Waiting_ID = %s
              AND Status = 'Ready for Pickup'
              AND Pickup_Deadline <= NOW()
        """, (waiting_id,))

        if cursor.rowcount == 0:
            continue

        cursor.execute("""
            UPDATE Books
            SET Available_Copies = Available_Copies + 1
            WHERE Book_ID = %s
        """, (book_id,))

        _promote_waiting_users(cursor, book_id)


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
                Books.Cover_Image,
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
        cursor.execute(query, (search_value, search_value))

        return cursor.fetchall()

    except Error as e:
        print("Book Search Error:", e)
        return []

    finally:
        cursor.close()
        connection.close()


# ================= GET ALL BOOKS =================

def get_all_books():

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
                Books.Cover_Image,
                Categories.Category_Name
            FROM Books
            LEFT JOIN Categories
                ON Books.Category_ID = Categories.Category_ID
            ORDER BY Books.Title ASC
        """

        cursor.execute(query)

        return cursor.fetchall()

    except Error as e:
        print("Get All Books Error:", e)
        return []

    finally:
        cursor.close()
        connection.close()


# ================= CHECK WAITING LIST ELIGIBILITY =================

def can_join_waiting_list(user_id, book_id):

    connection = create_connection()

    if connection is None:
        return "error"

    cursor = connection.cursor()

    try:
        _process_expired_reservations(cursor)
        connection.commit()

        cursor.execute("""
            SELECT Available_Copies
            FROM Books
            WHERE Book_ID = %s
        """, (book_id,))

        book = cursor.fetchone()

        if book is None:
            return "not_found"

        cursor.execute("""
            SELECT Borrowing_ID
            FROM Borrowings
            WHERE User_ID = %s
              AND Book_ID = %s
              AND Status = 'Borrowed'
            LIMIT 1
        """, (user_id, book_id))

        if cursor.fetchone():
            return "borrowed"

        cursor.execute("""
            SELECT Waiting_ID
            FROM Waiting_List
            WHERE User_ID = %s
              AND Book_ID = %s
              AND Status IN ('Waiting', 'Ready for Pickup')
            LIMIT 1
        """, (user_id, book_id))

        if cursor.fetchone():
            return "exists"

        if book[0] > 0:
            return "available"

        return "allowed"

    except Error as e:
        print("Check Waiting List Eligibility Error:", e)
        return "error"

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
            LIMIT 5
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
        cursor.execute("""
            INSERT INTO Favorites (User_ID, Book_ID)
            VALUES (%s, %s)
        """, (user_id, book_id))

        connection.commit()
        return "added"

    except Error as e:

        connection.rollback()

        if e.errno == 1062:
            return "exists"

        print("Add Favorite Error:", e)
        return "error"

    finally:
        cursor.close()
        connection.close()


# ================= GET STUDENT FAVORITES =================

def get_student_favorites(user_id):

    connection = create_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                Books.Book_ID,
                Books.Title,
                Books.Author,
                Books.Description,
                Books.Cover_Image,
                Books.Available_Copies,
                Categories.Category_Name
            FROM Favorites
            INNER JOIN Books
                ON Favorites.Book_ID = Books.Book_ID
            LEFT JOIN Categories
                ON Books.Category_ID = Categories.Category_ID
            WHERE Favorites.User_ID = %s
            ORDER BY Books.Title ASC
        """, (user_id,))

        return cursor.fetchall()

    except Error as e:
        print("Get Student Favorites Error:", e)
        return []

    finally:
        cursor.close()
        connection.close()


# ================= REMOVE FROM FAVORITES =================

def remove_from_favorites(user_id, book_id):

    connection = create_connection()

    if connection is None:
        return "error"

    cursor = connection.cursor()

    try:
        cursor.execute("""
            DELETE FROM Favorites
            WHERE User_ID = %s
              AND Book_ID = %s
        """, (user_id, book_id))

        if cursor.rowcount == 0:
            connection.rollback()
            return "not_found"

        connection.commit()
        return "removed"

    except Error as e:

        connection.rollback()
        print("Remove Favorite Error:", e)
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
        _process_expired_reservations(cursor)

        cursor.execute("""
            SELECT Available_Copies
            FROM Books
            WHERE Book_ID = %s
            FOR UPDATE
        """, (book_id,))

        book = cursor.fetchone()

        if book is None or book[0] <= 0:
            connection.rollback()
            return "unavailable"

        cursor.execute("""
            UPDATE Books
            SET Available_Copies = Available_Copies - 1
            WHERE Book_ID = %s
              AND Available_Copies > 0
        """, (book_id,))

        if cursor.rowcount == 0:
            connection.rollback()
            return "unavailable"

        cursor.execute("""
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
        """, (user_id, book_id))

        connection.commit()
        return "success"

    except Error as e:

        connection.rollback()
        print("Borrow Book Error:", e)
        return "error"

    finally:
        cursor.close()
        connection.close()


# ================= GET STUDENT BORROWINGS =================

def get_student_borrowings(user_id):

    connection = create_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                Borrowings.Borrowing_ID,
                Books.Book_ID,
                Books.Title,
                Books.Author,
                Borrowings.Borrow_Date,
                Borrowings.Due_Date,
                Borrowings.Return_Date,
                Borrowings.Status
            FROM Borrowings
            INNER JOIN Books
                ON Borrowings.Book_ID = Books.Book_ID
            WHERE Borrowings.User_ID = %s
            ORDER BY
                Borrowings.Borrow_Date DESC,
                Borrowings.Borrowing_ID DESC
        """, (user_id,))

        return cursor.fetchall()

    except Error as e:
        print("Get Student Borrowings Error:", e)
        return []

    finally:
        cursor.close()
        connection.close()


# ================= RETURN BOOK =================

def return_book(user_id, borrowing_id):

    connection = create_connection()

    if connection is None:
        return "error"

    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT Book_ID
            FROM Borrowings
            WHERE Borrowing_ID = %s
              AND User_ID = %s
              AND Status = 'Borrowed'
            FOR UPDATE
        """, (borrowing_id, user_id))

        borrowing = cursor.fetchone()

        if borrowing is None:
            connection.rollback()
            return "not_found"

        book_id = borrowing[0]

        cursor.execute("""
            UPDATE Borrowings
            SET
                Status = 'Returned',
                Return_Date = CURDATE()
            WHERE Borrowing_ID = %s
              AND User_ID = %s
              AND Status = 'Borrowed'
        """, (borrowing_id, user_id))

        if cursor.rowcount == 0:
            connection.rollback()
            return "not_found"

        cursor.execute("""
            UPDATE Books
            SET Available_Copies = Available_Copies + 1
            WHERE Book_ID = %s
        """, (book_id,))

        if cursor.rowcount == 0:
            connection.rollback()
            return "error"

        _process_expired_reservations(cursor)
        _promote_waiting_users(cursor, book_id)

        connection.commit()
        return "success"

    except Error as e:

        connection.rollback()
        print("Return Book Error:", e)
        return "error"

    finally:
        cursor.close()
        connection.close()


# ================= JOIN WAITING LIST =================

def join_waiting_list(user_id, book_id):

    connection = create_connection()

    if connection is None:
        return "error"

    cursor = connection.cursor()

    try:
        _process_expired_reservations(cursor)

        cursor.execute("""
            SELECT Available_Copies
            FROM Books
            WHERE Book_ID = %s
            FOR UPDATE
        """, (book_id,))

        book = cursor.fetchone()

        if book is None:
            connection.rollback()
            return "not_found"

        cursor.execute("""
            SELECT Borrowing_ID
            FROM Borrowings
            WHERE User_ID = %s
              AND Book_ID = %s
              AND Status = 'Borrowed'
            LIMIT 1
            FOR UPDATE
        """, (user_id, book_id))

        if cursor.fetchone():
            connection.rollback()
            return "borrowed"

        cursor.execute("""
            SELECT Waiting_ID
            FROM Waiting_List
            WHERE User_ID = %s
              AND Book_ID = %s
              AND Status IN ('Waiting', 'Ready for Pickup')
            LIMIT 1
            FOR UPDATE
        """, (user_id, book_id))

        if cursor.fetchone():
            connection.rollback()
            return "exists"

        if book[0] > 0:
            connection.rollback()
            return "available"

        cursor.execute("""
            INSERT INTO Waiting_List (
                User_ID,
                Book_ID,
                Request_Date,
                Status
            )
            VALUES (%s, %s, NOW(), 'Waiting')
        """, (user_id, book_id))

        connection.commit()
        return "joined"

    except Error as e:

        connection.rollback()
        print("Join Waiting List Error:", e)
        return "error"

    finally:
        cursor.close()
        connection.close()


# ================= GET STUDENT WAITING LIST =================

def get_student_waiting_list(user_id):

    connection = create_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        _process_expired_reservations(cursor)
        connection.commit()

        cursor.execute("""
            SELECT
                Waiting_List.Waiting_ID,
                Waiting_List.Book_ID,
                Books.Title,
                Books.Author,
                Waiting_List.Request_Date,
                Waiting_List.Status,
                Waiting_List.Pickup_Deadline,

                CASE
                    WHEN Waiting_List.Status = 'Waiting' THEN (
                        SELECT COUNT(*) + 1
                        FROM Waiting_List AS Earlier
                        WHERE Earlier.Book_ID = Waiting_List.Book_ID
                          AND Earlier.Status = 'Waiting'
                          AND (
                              Earlier.Request_Date < Waiting_List.Request_Date
                              OR (
                                  Earlier.Request_Date = Waiting_List.Request_Date
                                  AND Earlier.Waiting_ID < Waiting_List.Waiting_ID
                              )
                          )
                    )
                    ELSE NULL
                END AS Queue_Position

            FROM Waiting_List
            INNER JOIN Books
                ON Waiting_List.Book_ID = Books.Book_ID

            WHERE Waiting_List.User_ID = %s
              AND Waiting_List.Status IN ('Waiting', 'Ready for Pickup')

            ORDER BY Waiting_List.Request_Date DESC
        """, (user_id,))

        return cursor.fetchall()

    except Error as e:

        connection.rollback()
        print("Get Student Waiting List Error:", e)
        return []

    finally:
        cursor.close()
        connection.close()


# ================= LEAVE WAITING LIST =================

def leave_waiting_list(user_id, waiting_id):

    connection = create_connection()

    if connection is None:
        return "error"

    cursor = connection.cursor()

    try:
        _process_expired_reservations(cursor)

        cursor.execute("""
            SELECT Book_ID, Status
            FROM Waiting_List
            WHERE Waiting_ID = %s
              AND User_ID = %s
              AND Status IN ('Waiting', 'Ready for Pickup')
            FOR UPDATE
        """, (waiting_id, user_id))

        request = cursor.fetchone()

        if request is None:
            connection.rollback()
            return "not_found"

        book_id, status = request

        cursor.execute("""
            UPDATE Waiting_List
            SET Status = 'Cancelled'
            WHERE Waiting_ID = %s
              AND User_ID = %s
              AND Status IN ('Waiting', 'Ready for Pickup')
        """, (waiting_id, user_id))

        if cursor.rowcount == 0:
            connection.rollback()
            return "not_found"

        if status == "Ready for Pickup":

            cursor.execute("""
                UPDATE Books
                SET Available_Copies = Available_Copies + 1
                WHERE Book_ID = %s
            """, (book_id,))

            _promote_waiting_users(cursor, book_id)

        connection.commit()
        return "cancelled"

    except Error as e:

        connection.rollback()
        print("Leave Waiting List Error:", e)
        return "error"

    finally:
        cursor.close()
        connection.close()


# ================= COLLECT RESERVED BOOK =================

def collect_waiting_book(user_id, waiting_id):

    connection = create_connection()

    if connection is None:
        return "error"

    cursor = connection.cursor()

    try:
        _process_expired_reservations(cursor)

        cursor.execute("""
            SELECT Book_ID
            FROM Waiting_List
            WHERE Waiting_ID = %s
              AND User_ID = %s
              AND Status = 'Ready for Pickup'
              AND Pickup_Deadline > NOW()
            FOR UPDATE
        """, (waiting_id, user_id))

        request = cursor.fetchone()

        if request is None:
            connection.commit()
            return "not_ready"

        book_id = request[0]

        cursor.execute("""
            SELECT Borrowing_ID
            FROM Borrowings
            WHERE User_ID = %s
              AND Book_ID = %s
              AND Status = 'Borrowed'
            LIMIT 1
            FOR UPDATE
        """, (user_id, book_id))

        if cursor.fetchone():
            connection.rollback()
            return "already_borrowed"

        cursor.execute("""
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
        """, (user_id, book_id))

        cursor.execute("""
            UPDATE Waiting_List
            SET Status = 'Collected'
            WHERE Waiting_ID = %s
              AND User_ID = %s
              AND Status = 'Ready for Pickup'
        """, (waiting_id, user_id))

        if cursor.rowcount == 0:
            connection.rollback()
            return "not_ready"

        connection.commit()
        return "success"

    except Error as e:

        connection.rollback()
        print("Collect Waiting Book Error:", e)
        return "error"

    finally:
        cursor.close()
        connection.close()


# ================= MYSTERY BORROW =================

def get_book_categories():

    connection = create_connection()

    if connection is None:
        return []

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT Category_ID, Category_Name
            FROM Categories
            ORDER BY Category_Name ASC
        """)

        return cursor.fetchall()

    except Error as e:
        print("Get Book Categories Error:", e)
        return []

    finally:
        cursor.close()
        connection.close()


def get_random_book_by_category(category_id):

    connection = create_connection()

    if connection is None:
        return None

    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                Books.Book_ID,
                Books.Title,
                Books.Author,
                Books.Description,
                Books.Available_Copies,
                Categories.Category_Name
            FROM Books
            INNER JOIN Categories
                ON Books.Category_ID = Categories.Category_ID
            WHERE Books.Category_ID = %s
              AND Books.Available_Copies > 0
            ORDER BY RAND()
            LIMIT 1
        """, (category_id,))

        return cursor.fetchone()

    except Error as e:
        print("Mystery Borrow Error:", e)
        return None

    finally:
        cursor.close()
        connection.close()