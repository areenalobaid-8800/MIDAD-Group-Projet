
import tkinter as tk
from tkinter import messagebox

from modules.book_model import (
    search_books,
    get_most_borrowed_books,
    add_to_favorites,
    get_student_favorites,
    remove_from_favorites,
    borrow_book,
    get_student_borrowings,
    return_book,
    join_waiting_list,
    get_student_waiting_list,
    leave_waiting_list,
    collect_waiting_book,
    can_join_waiting_list
)


# ================= COLORS =================

NAVY = "#172B4D"
TEAL = "#2D8C87"
LIGHT_TEAL = "#E8F5F4"
BACKGROUND = "#F5F7FA"
WHITE = "#FFFFFF"
TEXT = "#263238"
GRAY = "#7A8793"
BORDER = "#E1E7ED"


# ================= STUDENT DASHBOARD =================

def open_student_dashboard(user):

    root = tk.Tk()
    root.title("MIDAD | Student Dashboard")
    root.geometry("1200x780")
    root.minsize(1050, 700)
    root.configure(bg=BACKGROUND)

    # ================= SIDEBAR =================

    sidebar = tk.Frame(root, bg=NAVY, width=235)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(
        sidebar,
        text="MIDAD",
        font=("Arial", 25, "bold"),
        bg=NAVY,
        fg=WHITE
    ).pack(pady=(35, 5))

    tk.Label(
        sidebar,
        text="SMART UNIVERSITY LIBRARY",
        font=("Arial", 8),
        bg=NAVY,
        fg="#B8C7D9"
    ).pack(pady=(0, 40))

    def show_message(page_name):

        messagebox.showinfo(
            page_name,
            f"{page_name} page is coming soon."
        )

    # ================= STORE THE PAGES =================

    borrowings_page = None
    return_page = None
    favorites_page = None
    waiting_page = None

    navigation = [
        ("⌂", "Dashboard"),
        ("▤", "My Borrowings"),
        ("↩", "Return Books"),
        ("☷", "Waiting List"),
        ("♡", "My Favorites"),
        ("✦", "You May Like"),
        ("?", "Mystery Borrow")
    ]

    # ================= MAIN CONTENT =================

    main_content = tk.Frame(root, bg=BACKGROUND)
    main_content.pack(side="left", fill="both", expand=True)

    # ================= HEADER =================

    header = tk.Frame(main_content, bg=WHITE, height=90)
    header.pack(fill="x")
    header.pack_propagate(False)

    # ================= SEARCH BAR =================

    search_container = tk.Frame(
        header,
        bg=BACKGROUND,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    search_container.place(
        relx=0.5,
        rely=0.5,
        anchor="center",
        width=410,
        height=44
    )

    search_entry = tk.Entry(
        search_container,
        font=("Arial", 11),
        bg=BACKGROUND,
        fg=GRAY,
        relief="flat",
        borderwidth=0
    )

    search_entry.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=10
    )

    placeholder = "Search by author or title"
    search_entry.insert(0, placeholder)

    def focus_in(event):

        if search_entry.get() == placeholder:
            search_entry.delete(0, "end")
            search_entry.config(fg=TEXT)

    def focus_out(event):

        if not search_entry.get().strip():
            search_entry.delete(0, "end")
            search_entry.insert(0, placeholder)
            search_entry.config(fg=GRAY)

    search_entry.bind("<FocusIn>", focus_in)
    search_entry.bind("<FocusOut>", focus_out)

    # ================= SEARCH RESULTS WINDOW =================

    suggestions_frame = tk.Frame(
        main_content,
        bg=BACKGROUND,
        highlightbackground=BORDER,
        highlightthickness=1
    )

    results_canvas = tk.Canvas(
        suggestions_frame,
        bg=BACKGROUND,
        highlightthickness=0
    )

    results_scrollbar = tk.Scrollbar(
        suggestions_frame,
        orient="vertical",
        command=results_canvas.yview
    )

    results_inner_frame = tk.Frame(
        results_canvas,
        bg=BACKGROUND
    )

    results_window = results_canvas.create_window(
        (0, 0),
        window=results_inner_frame,
        anchor="nw"
    )

    results_canvas.configure(
        yscrollcommand=results_scrollbar.set
    )

    results_canvas.pack(side="left", fill="both", expand=True)
    results_scrollbar.pack(side="right", fill="y")

    def update_scroll_region(event=None):

        results_canvas.configure(
            scrollregion=results_canvas.bbox("all")
        )

    def update_inner_width(event):

        results_canvas.itemconfig(
            results_window,
            width=event.width
        )

    results_inner_frame.bind("<Configure>", update_scroll_region)
    results_canvas.bind("<Configure>", update_inner_width)

    # ================= BOOK ACTIONS =================

    def handle_add_favorite(book):

        result = add_to_favorites(
            user["User_ID"],
            book["Book_ID"]
        )

        if result == "added":

            messagebox.showinfo(
                "My Favorites",
                f"{book['Title']} has been added to your favorites."
            )

            if favorites_page is not None:
                show_my_favorites()

        elif result == "exists":

            messagebox.showinfo(
                "My Favorites",
                "This book is already in your favorites."
            )

        else:

            messagebox.showerror(
                "Error",
                "Could not add this book to your favorites."
            )

    def handle_remove_favorite(book):

        result = messagebox.askyesno(
            "Remove Favorite",
            f"Are you sure you want to remove:\n\n"
            f"{book['Title']}\n\n"
            f"from your favorites?"
        )

        if not result:
            return

        remove_result = remove_from_favorites(
            user["User_ID"],
            book["Book_ID"]
        )

        if remove_result == "removed":

            messagebox.showinfo(
                "My Favorites",
                f"{book['Title']} has been removed from your favorites."
            )

            show_my_favorites()

        elif remove_result == "not_found":

            messagebox.showwarning(
                "My Favorites",
                "This book is no longer in your favorites."
            )

            show_my_favorites()

        else:

            messagebox.showerror(
                "Error",
                "Could not remove this book from your favorites. "
                "Please try again."
            )

    # ================= BORROW BOOK =================

    def handle_borrow(book):

        if book["Available_Copies"] <= 0:

            messagebox.showwarning(
                "Book Unavailable",
                "Sorry, no copies of this book are currently available."
            )
            return

        result = messagebox.askyesno(
            "Confirm Borrowing",
            f"Do you want to borrow:\n\n"
            f"{book['Title']}\n\n"
            f"Loan period: 7 days"
        )

        if not result:
            return

        borrow_result = borrow_book(
            user["User_ID"],
            book["Book_ID"]
        )

        if borrow_result == "success":

            messagebox.showinfo(
                "Borrowing Successful",
                f"You have successfully borrowed:\n"
                f"{book['Title']}\n\n"
                f"Loan period: 7 days."
            )

            search_while_typing()

        elif borrow_result == "unavailable":

            messagebox.showwarning(
                "Book Unavailable",
                "Sorry, this book is no longer available."
            )

            search_while_typing()

        else:

            messagebox.showerror(
                "Borrowing Error",
                "Something went wrong. Please try again."
            )

    # ================= RETURN BOOK ACTION =================

    def handle_return(book):

        result = messagebox.askyesno(
            "Confirm Return",
            f"Are you sure you want to return:\n\n"
            f"{book['Title']}?"
        )

        if not result:
            return

        return_result = return_book(
            user["User_ID"],
            book["Borrowing_ID"]
        )

        if return_result == "success":

            messagebox.showinfo(
                "Return Successful",
                f"You have successfully returned:\n\n"
                f"{book['Title']}"
            )

            show_my_borrowings()

        elif return_result == "not_found":

            messagebox.showwarning(
                "Return Unavailable",
                "This borrowing record is no longer active."
            )

            show_my_borrowings()

        else:

            messagebox.showerror(
                "Return Error",
                "Something went wrong while returning the book. "
                "Please try again."
            )

    # ================= WAITING LIST ACTIONS =================

    def handle_join_waiting(book):

        # Check whether the student already has this book.
        permission = can_join_waiting_list(
            user["User_ID"],
            book["Book_ID"]
        )

        if permission == "borrowed":

            messagebox.showwarning(
                "Waiting List Not Allowed",
                "You cannot join the waiting list because "
                "you already have this book."
            )
            return

        elif permission == "exists":

            messagebox.showinfo(
                "Waiting List",
                "You are already in the waiting list for this book."
            )
            return

        elif permission == "available":

            messagebox.showinfo(
                "Book Available",
                "This book is currently available. "
                "You can borrow it directly."
            )

            search_while_typing()
            return

        elif permission == "not_found":

            messagebox.showerror(
                "Waiting List",
                "This book could not be found."
            )
            return

        elif permission != "allowed":

            messagebox.showerror(
                "Error",
                "Could not verify your waiting list eligibility."
            )
            return

        # Only eligible students can reach this point.
        result = join_waiting_list(
            user["User_ID"],
            book["Book_ID"]
        )

        if result == "joined":

            messagebox.showinfo(
                "Waiting List",
                f"You have successfully joined the waiting list for:\n\n"
                f"{book['Title']}"
            )

            search_while_typing()

            if waiting_page is not None:
                show_waiting_list()

        elif result == "borrowed":

            messagebox.showwarning(
                "Waiting List Not Allowed",
                "You cannot join the waiting list because "
                "you already have this book."
            )

        elif result == "exists":

            messagebox.showinfo(
                "Waiting List",
                "You are already in the waiting list for this book."
            )

        elif result == "available":

            messagebox.showinfo(
                "Book Available",
                "This book is currently available. "
                "You can borrow it directly."
            )

            search_while_typing()

        elif result == "not_found":

            messagebox.showerror(
                "Waiting List",
                "This book could not be found."
            )

        else:

            messagebox.showerror(
                "Error",
                "Could not join the waiting list. Please try again."
            )

    def handle_leave_waiting(book):

        confirm = messagebox.askyesno(
            "Leave Waiting List",
            f"Are you sure you want to leave the waiting list for:\n\n"
            f"{book['Title']}?"
        )

        if not confirm:
            return

        result = leave_waiting_list(
            user["User_ID"],
            book["Waiting_ID"]
        )

        if result == "cancelled":

            messagebox.showinfo(
                "Waiting List",
                "You have successfully left the waiting list."
            )

            show_waiting_list()

        elif result == "not_found":

            messagebox.showwarning(
                "Waiting List",
                "This waiting list request is no longer active."
            )

            show_waiting_list()

        else:

            messagebox.showerror(
                "Error",
                "Could not leave the waiting list. Please try again."
            )

    def handle_collect_waiting(book):

        confirm = messagebox.askyesno(
            "Collect Book",
            f"Do you want to collect:\n\n"
            f"{book['Title']}\n\n"
            f"After collection, the 7-day borrowing period will begin."
        )

        if not confirm:
            return

        result = collect_waiting_book(
            user["User_ID"],
            book["Waiting_ID"]
        )

        if result == "success":

            messagebox.showinfo(
                "Collection Successful",
                f"You have successfully collected:\n\n"
                f"{book['Title']}\n\n"
                f"Borrowing period: 7 days."
            )

            show_waiting_list()

        elif result == "not_ready":

            messagebox.showwarning(
                "Reservation Unavailable",
                "This reservation is no longer available. "
                "Please refresh the waiting list."
            )

            show_waiting_list()

        else:

            messagebox.showerror(
                "Error",
                "Could not collect the book. Please try again."
            )

    # ================= DISPLAY BOOK CARDS =================

    def display_search_results(books):

        for widget in results_inner_frame.winfo_children():
            widget.destroy()

        if not books:

            tk.Label(
                results_inner_frame,
                text="No books found.",
                font=("Arial", 12, "bold"),
                bg=WHITE,
                fg=GRAY,
                padx=20,
                pady=25
            ).pack(fill="x", padx=12, pady=12)

            return

        for book in books:

            book_card = tk.Frame(
                results_inner_frame,
                bg=WHITE,
                highlightbackground=BORDER,
                highlightthickness=1,
                padx=18,
                pady=15
            )

            book_card.pack(fill="x", padx=12, pady=7)

            info_frame = tk.Frame(book_card, bg=WHITE)
            info_frame.pack(fill="x", anchor="w")

            tk.Label(
                info_frame,
                text="▤",
                font=("Arial", 27),
                bg=WHITE,
                fg=TEAL
            ).pack(side="left", padx=(0, 18))

            details_frame = tk.Frame(info_frame, bg=WHITE)
            details_frame.pack(side="left", fill="x", expand=True)

            tk.Label(
                details_frame,
                text=book["Title"],
                font=("Arial", 12, "bold"),
                bg=WHITE,
                fg=NAVY,
                wraplength=450,
                justify="left"
            ).pack(anchor="w")

            tk.Label(
                details_frame,
                text=f"Author: {book['Author']}",
                font=("Arial", 10),
                bg=WHITE,
                fg=GRAY
            ).pack(anchor="w", pady=(5, 3))

            category = book["Category_Name"] or "Not specified"

            tk.Label(
                details_frame,
                text=f"Category: {category}",
                font=("Arial", 9),
                bg=WHITE,
                fg=GRAY
            ).pack(anchor="w")

            description = book.get("Description") or "No description available."

            tk.Label(
                details_frame,
                text=f"Description: {description}",
                font=("Arial", 9),
                bg=WHITE,
                fg=TEXT,
                wraplength=450,
                justify="left",
                anchor="w"
            ).pack(anchor="w", pady=(6, 2))

            available = book["Available_Copies"]

            if available > 0:
                availability_text = f"Available Copies: {available}"
                availability_color = TEAL
            else:
                availability_text = "Currently Unavailable"
                availability_color = "#C0392B"

            tk.Label(
                details_frame,
                text=availability_text,
                font=("Arial", 9, "bold"),
                bg=WHITE,
                fg=availability_color
            ).pack(anchor="w", pady=(5, 0))

            buttons_frame = tk.Frame(book_card, bg=WHITE)
            buttons_frame.pack(fill="x", pady=(15, 0))

            tk.Button(
                buttons_frame,
                text="♡  Add to Favorite",
                font=("Arial", 9, "bold"),
                bg=LIGHT_TEAL,
                fg=NAVY,
                activebackground="#D5ECEA",
                activeforeground=NAVY,
                relief="flat",
                padx=15,
                pady=8,
                cursor="hand2",
                command=lambda b=book: handle_add_favorite(b)
            ).pack(side="left", padx=(0, 10))

            borrow_button = tk.Button(
                buttons_frame,
                text="Borrow",
                font=("Arial", 9, "bold"),
                bg=TEAL,
                fg=WHITE,
                activebackground="#24736F",
                activeforeground=WHITE,
                relief="flat",
                padx=25,
                pady=8,
                cursor="hand2",
                command=lambda b=book: handle_borrow(b)
            )

            borrow_button.pack(side="left")

            if available <= 0:

                borrow_button.config(
                    state="disabled",
                    bg=GRAY
                )

                # Check eligibility before displaying Join Waiting List.
                permission = can_join_waiting_list(
                    user["User_ID"],
                    book["Book_ID"]
                )

                if permission == "allowed":

                    tk.Button(
                        buttons_frame,
                        text="☷  Join Waiting List",
                        font=("Arial", 9, "bold"),
                        bg=LIGHT_TEAL,
                        fg=NAVY,
                        activebackground="#D5ECEA",
                        activeforeground=NAVY,
                        relief="flat",
                        padx=15,
                        pady=8,
                        cursor="hand2",
                        command=lambda b=book: handle_join_waiting(b)
                    ).pack(side="left", padx=(10, 0))

                elif permission == "borrowed":

                    tk.Label(
                        buttons_frame,
                        text="You already have this book",
                        font=("Arial", 9, "bold"),
                        bg=WHITE,
                        fg="#C0392B"
                    ).pack(side="left", padx=(10, 0))

                elif permission == "exists":

                    tk.Label(
                        buttons_frame,
                        text="Already in Waiting List",
                        font=("Arial", 9, "bold"),
                        bg=WHITE,
                        fg="#C58A22"
                    ).pack(side="left", padx=(10, 0))

    # ================= SEARCH WHILE TYPING =================

    def search_while_typing(event=None):

        search_text = search_entry.get().strip()

        if not search_text or search_text == placeholder:
            suggestions_frame.place_forget()
            return

        books = search_books(search_text)
        display_search_results(books)

        suggestions_frame.place(
            relx=0.5,
            y=90,
            anchor="n",
            width=650,
            height=560
        )

        suggestions_frame.lift()

    search_entry.bind("<KeyRelease>", search_while_typing)

    # ================= USER GREETING =================

    tk.Label(
        header,
        text=f"Welcome, {user['Name']}",
        font=("Arial", 11, "bold"),
        bg=WHITE,
        fg=NAVY
    ).place(relx=0.97, rely=0.5, anchor="e")

    # ================= PAGE CONTENT =================

    content = tk.Frame(main_content, bg=BACKGROUND)

    content.pack(
        fill="both",
        expand=True,
        padx=35,
        pady=25
    )

    # ================= SCROLLABLE PAGE HELPER =================

    def create_scrollable_page(parent):

        canvas = tk.Canvas(
            parent,
            bg=BACKGROUND,
            highlightthickness=0
        )

        scrollbar = tk.Scrollbar(
            parent,
            orient="vertical",
            command=canvas.yview
        )

        inner_frame = tk.Frame(canvas, bg=BACKGROUND)

        window_id = canvas.create_window(
            (0, 0),
            window=inner_frame,
            anchor="nw"
        )

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def update_scroll(event=None):

            canvas.configure(
                scrollregion=canvas.bbox("all")
            )

        def update_width(event):

            canvas.itemconfig(
                window_id,
                width=event.width
            )

        inner_frame.bind("<Configure>", update_scroll)
        canvas.bind("<Configure>", update_width)

        return inner_frame

    # ================= BORROWING CARD HELPER =================

    def create_borrowing_card(parent, book, returned=False):

        card = tk.Frame(
            parent,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=20,
            pady=18
        )

        card.pack(fill="x", pady=6)

        tk.Label(
            card,
            text=book["Title"],
            font=("Arial", 13, "bold"),
            bg=WHITE,
            fg=NAVY,
            wraplength=700,
            justify="left"
        ).pack(anchor="w")

        tk.Label(
            card,
            text=f"Author: {book['Author']}",
            font=("Arial", 10),
            bg=WHITE,
            fg=GRAY
        ).pack(anchor="w", pady=(5, 12))

        tk.Label(
            card,
            text=f"Borrow Date: {book['Borrow_Date']}",
            font=("Arial", 9),
            bg=WHITE,
            fg=TEXT
        ).pack(anchor="w", pady=2)

        tk.Label(
            card,
            text=f"Due Date: {book['Due_Date']}",
            font=("Arial", 9),
            bg=WHITE,
            fg=TEXT
        ).pack(anchor="w", pady=2)

        if returned:

            tk.Label(
                card,
                text=f"Return Date: {book['Return_Date']}",
                font=("Arial", 9),
                bg=WHITE,
                fg=TEXT
            ).pack(anchor="w", pady=2)

            tk.Label(
                card,
                text="Returned Successfully",
                font=("Arial", 10, "bold"),
                bg=WHITE,
                fg=TEAL
            ).pack(anchor="w", pady=(8, 0))

        else:

            tk.Label(
                card,
                text="Currently Borrowed",
                font=("Arial", 10, "bold"),
                bg=WHITE,
                fg=TEAL
            ).pack(anchor="w", pady=(8, 0))

            tk.Button(
                card,
                text="↩  Return",
                font=("Arial", 9, "bold"),
                bg=TEAL,
                fg=WHITE,
                activebackground="#24736F",
                activeforeground=WHITE,
                relief="flat",
                padx=22,
                pady=8,
                cursor="hand2",
                command=lambda b=book: handle_return(b)
            ).pack(anchor="w", pady=(12, 0))

    # ================= FAVORITE BOOK CARD =================

    def create_favorite_card(parent, book):

        card = tk.Frame(
            parent,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=20,
            pady=18
        )

        card.pack(fill="x", pady=7)

        info_frame = tk.Frame(card, bg=WHITE)
        info_frame.pack(fill="x")

        tk.Label(
            info_frame,
            text="♡",
            font=("Arial", 30),
            bg=WHITE,
            fg=TEAL
        ).pack(side="left", padx=(0, 18))

        details_frame = tk.Frame(info_frame, bg=WHITE)
        details_frame.pack(side="left", fill="x", expand=True)

        tk.Label(
            details_frame,
            text=book["Title"],
            font=("Arial", 13, "bold"),
            bg=WHITE,
            fg=NAVY,
            wraplength=650,
            justify="left"
        ).pack(anchor="w")

        tk.Label(
            details_frame,
            text=f"Author: {book['Author']}",
            font=("Arial", 10),
            bg=WHITE,
            fg=GRAY
        ).pack(anchor="w", pady=(5, 3))

        category = book.get("Category_Name") or "Not specified"

        tk.Label(
            details_frame,
            text=f"Category: {category}",
            font=("Arial", 9),
            bg=WHITE,
            fg=GRAY
        ).pack(anchor="w")

        description = book.get("Description") or "No description available."

        tk.Label(
            details_frame,
            text=f"Description: {description}",
            font=("Arial", 9),
            bg=WHITE,
            fg=TEXT,
            wraplength=650,
            justify="left"
        ).pack(anchor="w", pady=(6, 3))

        available = book.get("Available_Copies", 0)

        if available > 0:
            availability_text = f"Available Copies: {available}"
            availability_color = TEAL
        else:
            availability_text = "Currently Unavailable"
            availability_color = "#C0392B"

        tk.Label(
            details_frame,
            text=availability_text,
            font=("Arial", 9, "bold"),
            bg=WHITE,
            fg=availability_color
        ).pack(anchor="w", pady=(5, 0))

        tk.Button(
            card,
            text="Remove from Favorites",
            font=("Arial", 9, "bold"),
            bg=LIGHT_TEAL,
            fg=NAVY,
            activebackground="#D5ECEA",
            activeforeground=NAVY,
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
            command=lambda b=book: handle_remove_favorite(b)
        ).pack(anchor="w", pady=(15, 0))

    # ================= MY FAVORITES PAGE =================

    def show_my_favorites():

        nonlocal borrowings_page, return_page, favorites_page, waiting_page

        suggestions_frame.place_forget()
        content.pack_forget()

        for page in (borrowings_page, return_page, waiting_page, favorites_page):
            if page is not None:
                page.destroy()

        borrowings_page = None
        return_page = None
        waiting_page = None

        favorites_page = tk.Frame(main_content, bg=BACKGROUND)

        favorites_page.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=25
        )

        page_inner = create_scrollable_page(favorites_page)

        tk.Label(
            page_inner,
            text="My Favorites",
            font=("Arial", 23, "bold"),
            bg=BACKGROUND,
            fg=NAVY
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(
            page_inner,
            text="View and manage the books you have added to your favorites.",
            font=("Arial", 11),
            bg=BACKGROUND,
            fg=GRAY
        ).pack(anchor="w", pady=(0, 25))

        favorite_books = get_student_favorites(user["User_ID"])

        if favorite_books:

            tk.Label(
                page_inner,
                text=f"Your Favorite Books ({len(favorite_books)})",
                font=("Arial", 17, "bold"),
                bg=BACKGROUND,
                fg=NAVY
            ).pack(anchor="w", pady=(0, 15))

            for book in favorite_books:
                create_favorite_card(page_inner, book)

        else:

            empty_frame = tk.Frame(
                page_inner,
                bg=WHITE,
                highlightbackground=BORDER,
                highlightthickness=1,
                padx=25,
                pady=35
            )

            empty_frame.pack(fill="x", pady=10)

            tk.Label(
                empty_frame,
                text="♡",
                font=("Arial", 38),
                bg=WHITE,
                fg=TEAL
            ).pack(pady=(0, 10))

            tk.Label(
                empty_frame,
                text="Your Favorites List Is Empty",
                font=("Arial", 15, "bold"),
                bg=WHITE,
                fg=NAVY
            ).pack()

            tk.Label(
                empty_frame,
                text="Search for books and add them to your favorites.",
                font=("Arial", 10),
                bg=WHITE,
                fg=GRAY
            ).pack(pady=(8, 0))

    # ================= MY BORROWINGS PAGE =================

    def show_my_borrowings():

        nonlocal borrowings_page, return_page, favorites_page, waiting_page

        suggestions_frame.place_forget()
        content.pack_forget()

        for page in (return_page, favorites_page, waiting_page, borrowings_page):
            if page is not None:
                page.destroy()

        return_page = None
        favorites_page = None
        waiting_page = None

        borrowings_page = tk.Frame(main_content, bg=BACKGROUND)

        borrowings_page.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=25
        )

        page_inner = create_scrollable_page(borrowings_page)

        tk.Label(
            page_inner,
            text="My Borrowings",
            font=("Arial", 23, "bold"),
            bg=BACKGROUND,
            fg=NAVY
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(
            page_inner,
            text="View your current and previous borrowings.",
            font=("Arial", 11),
            bg=BACKGROUND,
            fg=GRAY
        ).pack(anchor="w", pady=(0, 25))

        borrowings = get_student_borrowings(user["User_ID"])

        current_borrowings = [
            book for book in borrowings
            if book["Status"] == "Borrowed"
        ]

        previous_borrowings = [
            book for book in borrowings
            if book["Status"] == "Returned"
        ]

        tk.Label(
            page_inner,
            text="Currently Borrowed",
            font=("Arial", 17, "bold"),
            bg=BACKGROUND,
            fg=NAVY
        ).pack(anchor="w", pady=(0, 15))

        if current_borrowings:

            for book in current_borrowings:
                create_borrowing_card(page_inner, book, returned=False)

        else:

            tk.Label(
                page_inner,
                text="You have no currently borrowed books.",
                font=("Arial", 10),
                bg=WHITE,
                fg=GRAY,
                padx=20,
                pady=20
            ).pack(fill="x", pady=(0, 10))

        tk.Label(
            page_inner,
            text="Previous Borrowings",
            font=("Arial", 17, "bold"),
            bg=BACKGROUND,
            fg=NAVY
        ).pack(anchor="w", pady=(30, 15))

        if previous_borrowings:

            for book in previous_borrowings:
                create_borrowing_card(page_inner, book, returned=True)

        else:

            tk.Label(
                page_inner,
                text="You have no previous borrowings.",
                font=("Arial", 10),
                bg=WHITE,
                fg=GRAY,
                padx=20,
                pady=20
            ).pack(fill="x", pady=(0, 10))

    # ================= RETURN BOOKS PAGE =================

    def show_return_books():

        nonlocal borrowings_page, return_page, favorites_page, waiting_page

        suggestions_frame.place_forget()
        content.pack_forget()

        for page in (borrowings_page, favorites_page, waiting_page, return_page):
            if page is not None:
                page.destroy()

        borrowings_page = None
        favorites_page = None
        waiting_page = None

        return_page = tk.Frame(main_content, bg=BACKGROUND)

        return_page.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=25
        )

        page_inner = create_scrollable_page(return_page)

        tk.Label(
            page_inner,
            text="Return Books",
            font=("Arial", 23, "bold"),
            bg=BACKGROUND,
            fg=NAVY
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(
            page_inner,
            text="View the books you have successfully returned.",
            font=("Arial", 11),
            bg=BACKGROUND,
            fg=GRAY
        ).pack(anchor="w", pady=(0, 25))

        borrowings = get_student_borrowings(user["User_ID"])

        returned_books = [
            book for book in borrowings
            if book["Status"] == "Returned"
        ]

        if returned_books:

            for book in returned_books:
                create_borrowing_card(page_inner, book, returned=True)

        else:

            tk.Label(
                page_inner,
                text="You have not returned any books yet.",
                font=("Arial", 10),
                bg=WHITE,
                fg=GRAY,
                padx=20,
                pady=20
            ).pack(fill="x", pady=(0, 10))

    # ================= WAITING LIST PAGE =================

    def show_waiting_list():

        nonlocal borrowings_page, return_page, favorites_page, waiting_page

        suggestions_frame.place_forget()
        content.pack_forget()

        for page in (borrowings_page, return_page, favorites_page, waiting_page):
            if page is not None:
                page.destroy()

        borrowings_page = None
        return_page = None
        favorites_page = None

        waiting_page = tk.Frame(main_content, bg=BACKGROUND)

        waiting_page.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=25
        )

        page_inner = create_scrollable_page(waiting_page)

        tk.Label(
            page_inner,
            text="Waiting List",
            font=("Arial", 23, "bold"),
            bg=BACKGROUND,
            fg=NAVY
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(
            page_inner,
            text="View and manage the books you are waiting for.",
            font=("Arial", 11),
            bg=BACKGROUND,
            fg=GRAY
        ).pack(anchor="w", pady=(0, 25))

        waiting_books = get_student_waiting_list(user["User_ID"])

        if not waiting_books:

            empty_frame = tk.Frame(
                page_inner,
                bg=WHITE,
                highlightbackground=BORDER,
                highlightthickness=1,
                padx=25,
                pady=35
            )

            empty_frame.pack(fill="x", pady=10)

            tk.Label(
                empty_frame,
                text="☷",
                font=("Arial", 38),
                bg=WHITE,
                fg=TEAL
            ).pack(pady=(0, 10))

            tk.Label(
                empty_frame,
                text="Your Waiting List Is Empty",
                font=("Arial", 15, "bold"),
                bg=WHITE,
                fg=NAVY
            ).pack()

            tk.Label(
                empty_frame,
                text="Search for unavailable books and join their waiting lists.",
                font=("Arial", 10),
                bg=WHITE,
                fg=GRAY
            ).pack(pady=(8, 0))

            return

        tk.Label(
            page_inner,
            text=f"Your Waiting Requests ({len(waiting_books)})",
            font=("Arial", 17, "bold"),
            bg=BACKGROUND,
            fg=NAVY
        ).pack(anchor="w", pady=(0, 15))

        for book in waiting_books:

            card = tk.Frame(
                page_inner,
                bg=WHITE,
                highlightbackground=BORDER,
                highlightthickness=1,
                padx=20,
                pady=18
            )

            card.pack(fill="x", pady=7)

            tk.Label(
                card,
                text=book["Title"],
                font=("Arial", 13, "bold"),
                bg=WHITE,
                fg=NAVY,
                wraplength=650,
                justify="left"
            ).pack(anchor="w")

            tk.Label(
                card,
                text=f"Author: {book['Author']}",
                font=("Arial", 10),
                bg=WHITE,
                fg=GRAY
            ).pack(anchor="w", pady=(5, 10))

            tk.Label(
                card,
                text=f"Request Date: {book['Request_Date']}",
                font=("Arial", 9),
                bg=WHITE,
                fg=TEXT
            ).pack(anchor="w", pady=2)

            if book["Status"] == "Waiting":

                tk.Label(
                    card,
                    text=f"Queue Position: {book['Queue_Position']}",
                    font=("Arial", 10, "bold"),
                    bg=WHITE,
                    fg=TEAL
                ).pack(anchor="w", pady=(7, 2))

                tk.Label(
                    card,
                    text="Status: Waiting",
                    font=("Arial", 10, "bold"),
                    bg=WHITE,
                    fg="#C58A22"
                ).pack(anchor="w", pady=2)

            elif book["Status"] == "Ready for Pickup":

                tk.Label(
                    card,
                    text="Status: Ready for Pickup",
                    font=("Arial", 10, "bold"),
                    bg=WHITE,
                    fg=TEAL
                ).pack(anchor="w", pady=(7, 2))

                tk.Label(
                    card,
                    text=f"Pickup Deadline: {book['Pickup_Deadline']}",
                    font=("Arial", 9, "bold"),
                    bg=WHITE,
                    fg="#C0392B"
                ).pack(anchor="w", pady=2)

                tk.Button(
                    card,
                    text="Collect Book",
                    font=("Arial", 9, "bold"),
                    bg=TEAL,
                    fg=WHITE,
                    activebackground="#24736F",
                    activeforeground=WHITE,
                    relief="flat",
                    padx=20,
                    pady=8,
                    cursor="hand2",
                    command=lambda b=book: handle_collect_waiting(b)
                ).pack(anchor="w", pady=(12, 0))

            tk.Button(
                card,
                text="Leave Waiting List",
                font=("Arial", 9, "bold"),
                bg=LIGHT_TEAL,
                fg=NAVY,
                activebackground="#D5ECEA",
                activeforeground=NAVY,
                relief="flat",
                padx=16,
                pady=8,
                cursor="hand2",
                command=lambda b=book: handle_leave_waiting(b)
            ).pack(anchor="w", pady=(10, 0))

    # ================= SHOW DASHBOARD =================

    def show_dashboard():

        nonlocal borrowings_page, return_page, favorites_page, waiting_page

        suggestions_frame.place_forget()

        for page in (borrowings_page, return_page, favorites_page, waiting_page):
            if page is not None:
                page.destroy()

        borrowings_page = None
        return_page = None
        favorites_page = None
        waiting_page = None

        content.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=25
        )

    # ================= PAGE NAVIGATION =================

    def navigate_page(page_name):

        if page_name == "My Borrowings":
            show_my_borrowings()

        elif page_name == "Return Books":
            show_return_books()

        elif page_name == "My Favorites":
            show_my_favorites()

        elif page_name == "Waiting List":
            show_waiting_list()

        elif page_name == "Dashboard":
            show_dashboard()

        else:
            show_message(page_name)

    # ================= SIDEBAR NAVIGATION BUTTONS =================

    for icon, name in navigation:

        tk.Button(
            sidebar,
            text=f"  {icon}     {name}",
            font=("Arial", 11),
            bg=NAVY,
            fg=WHITE,
            activebackground=TEAL,
            activeforeground=WHITE,
            relief="flat",
            anchor="w",
            padx=20,
            pady=13,
            cursor="hand2",
            command=lambda page=name: navigate_page(page)
        ).pack(fill="x", padx=12, pady=3)

    # ================= LOGOUT =================

    tk.Button(
        sidebar,
        text="  ⇦     Logout",
        font=("Arial", 11),
        bg=NAVY,
        fg="#F2B8B5",
        activebackground="#263D5F",
        activeforeground=WHITE,
        relief="flat",
        anchor="w",
        padx=20,
        pady=13,
        cursor="hand2",
        command=root.destroy
    ).pack(side="bottom", fill="x", padx=12, pady=25)

    # ================= MAIN HEADING =================

    tk.Label(
        content,
        text="Your Library, Your Space.",
        font=("Arial", 23, "bold"),
        bg=BACKGROUND,
        fg=NAVY
    ).pack(anchor="w", pady=(0, 20))

    # ================= BANNER =================

    banner = tk.Frame(content, bg=NAVY, height=190)
    banner.pack(fill="x", pady=(0, 30))
    banner.pack_propagate(False)

    tk.Label(
        banner,
        text="A World of Knowledge Awaits",
        font=("Arial", 23, "bold"),
        bg=NAVY,
        fg=WHITE
    ).pack(anchor="w", padx=30, pady=(35, 8))

    tk.Label(
        banner,
        text="Find your next favorite book at MIDAD.",
        font=("Arial", 11),
        bg=NAVY,
        fg="#D5E0EC"
    ).pack(anchor="w", padx=30)

    tk.Button(
        banner,
        text="EXPLORE BOOKS",
        font=("Arial", 9, "bold"),
        bg=TEAL,
        fg=WHITE,
        activebackground="#24736F",
        activeforeground=WHITE,
        relief="flat",
        padx=22,
        pady=10,
        cursor="hand2",
        command=lambda: show_message("Explore Books")
    ).pack(anchor="w", padx=30, pady=15)

    # ================= YOU MAY LIKE =================

    tk.Label(
        content,
        text="You May Like",
        font=("Arial", 17, "bold"),
        bg=BACKGROUND,
        fg=NAVY
    ).pack(anchor="w", pady=(0, 15))

    books_frame = tk.Frame(content, bg=BACKGROUND)
    books_frame.pack(fill="x", pady=(0, 30))

    most_borrowed_books = get_most_borrowed_books()

    if most_borrowed_books:

        for book in most_borrowed_books:

            book_card = tk.Frame(
                books_frame,
                bg=WHITE,
                highlightbackground=BORDER,
                highlightthickness=1,
                padx=18,
                pady=18
            )

            book_card.pack(
                side="left",
                fill="both",
                expand=True,
                padx=(0, 15)
            )

            tk.Label(
                book_card,
                text="▤",
                font=("Arial", 30),
                bg=WHITE,
                fg=TEAL
            ).pack(anchor="w")

            tk.Label(
                book_card,
                text=book["Title"],
                font=("Arial", 11, "bold"),
                bg=WHITE,
                fg=NAVY,
                wraplength=180,
                justify="left"
            ).pack(anchor="w", pady=(10, 5))

            tk.Label(
                book_card,
                text=book["Author"],
                font=("Arial", 9),
                bg=WHITE,
                fg=GRAY,
                wraplength=180,
                justify="left"
            ).pack(anchor="w")

            tk.Label(
                book_card,
                text=f"Borrowed {book['Borrowing_Count']} times",
                font=("Arial", 9),
                bg=WHITE,
                fg=TEAL
            ).pack(anchor="w", pady=(8, 0))

    else:

        tk.Label(
            books_frame,
            text="No books available in the database.",
            font=("Arial", 10),
            bg=BACKGROUND,
            fg=GRAY
        ).pack(anchor="w")

    # ================= QUICK ACCESS =================

    tk.Label(
        content,
        text="Quick Access",
        font=("Arial", 17, "bold"),
        bg=BACKGROUND,
        fg=NAVY
    ).pack(anchor="w", pady=(0, 15))

    quick_frame = tk.Frame(content, bg=BACKGROUND)
    quick_frame.pack(fill="x")

    quick_items = [
        ("▤", "My Borrowings"),
        ("♡", "My Favorites"),
        ("☷", "Waiting List"),
        ("✦", "Mystery Borrow")
    ]

    for icon, name in quick_items:

        tk.Button(
            quick_frame,
            text=f"{icon}\n\n{name}",
            font=("Arial", 11, "bold"),
            bg=WHITE,
            fg=NAVY,
            activebackground=LIGHT_TEAL,
            activeforeground=NAVY,
            relief="flat",
            highlightbackground=BORDER,
            highlightthickness=1,
            pady=18,
            cursor="hand2",
            command=lambda page=name: navigate_page(page)
        ).pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 15)
        )

    # ================= FOOTER =================

    tk.Label(
        content,
        text="MIDAD | Smart University Library Management System",
        font=("Arial", 8),
        bg=BACKGROUND,
        fg=GRAY
    ).pack(side="bottom", pady=(20, 0))

    root.mainloop()


# ================= RUN DASHBOARD DIRECTLY =================

if __name__ == "__main__":

    demo_user = {
        "User_ID": 1,
        "Name": "Student 01"
    }

    open_student_dashboard(demo_user)
