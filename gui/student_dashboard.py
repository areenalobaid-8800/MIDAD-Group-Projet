
import tkinter as tk
from tkinter import messagebox

from modules.book_model import (
    search_books,
    get_most_borrowed_books,
    add_to_favorites,
    borrow_book
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

    sidebar = tk.Frame(
        root,
        bg=NAVY,
        width=235
    )
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

    navigation = [
        ("⌂", "Dashboard"),
        ("▤", "My Borrowings"),
        ("↩", "Return Books"),
        ("☷", "Waiting List"),
        ("♡", "My Favorites"),
        ("✦", "You May Like"),
        ("?", "Mystery Borrow")
    ]

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
            command=lambda page=name: show_message(page)
        ).pack(fill="x", padx=12, pady=3)

    # Logout

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

    # ================= MAIN CONTENT =================

    main_content = tk.Frame(
        root,
        bg=BACKGROUND
    )

    main_content.pack(
        side="left",
        fill="both",
        expand=True
    )

    # ================= HEADER =================

    header = tk.Frame(
        main_content,
        bg=WHITE,
        height=90
    )

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

    # Scrollable results area

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

    results_canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    results_scrollbar.pack(
        side="right",
        fill="y"
    )

    def update_scroll_region(event=None):

        results_canvas.configure(
            scrollregion=results_canvas.bbox("all")
        )

    def update_inner_width(event):

        results_canvas.itemconfig(
            results_window,
            width=event.width
        )

    results_inner_frame.bind(
        "<Configure>",
        update_scroll_region
    )

    results_canvas.bind(
        "<Configure>",
        update_inner_width
    )

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

            # Update displayed availability

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
            ).pack(
                fill="x",
                padx=12,
                pady=12
            )

            return

        for book in books:

            # Book Card

            book_card = tk.Frame(
                results_inner_frame,
                bg=WHITE,
                highlightbackground=BORDER,
                highlightthickness=1,
                padx=18,
                pady=15
            )

            book_card.pack(
                fill="x",
                padx=12,
                pady=7
            )

            # Book Information

            info_frame = tk.Frame(
                book_card,
                bg=WHITE
            )

            info_frame.pack(
                fill="x",
                anchor="w"
            )

            tk.Label(
                info_frame,
                text="▤",
                font=("Arial", 27),
                bg=WHITE,
                fg=TEAL
            ).pack(
                side="left",
                padx=(0, 18)
            )

            details_frame = tk.Frame(
                info_frame,
                bg=WHITE
            )

            details_frame.pack(
                side="left",
                fill="x",
                expand=True
            )

            # Book Title

            tk.Label(
                details_frame,
                text=book["Title"],
                font=("Arial", 12, "bold"),
                bg=WHITE,
                fg=NAVY,
                wraplength=450,
                justify="left"
            ).pack(anchor="w")

            # Author

            tk.Label(
                details_frame,
                text=f"Author: {book['Author']}",
                font=("Arial", 10),
                bg=WHITE,
                fg=GRAY
            ).pack(
                anchor="w",
                pady=(5, 3)
            )

            # Category

            category = book["Category_Name"] or "Not specified"

            tk.Label(
                details_frame,
                text=f"Category: {category}",
                font=("Arial", 9),
                bg=WHITE,
                fg=GRAY
            ).pack(anchor="w")

            # Short Description

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
            ).pack(
                anchor="w",
                pady=(6, 2)
            )

            # Available Copies

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
            ).pack(
                anchor="w",
                pady=(5, 0)
            )

            # Buttons

            buttons_frame = tk.Frame(
                book_card,
                bg=WHITE
            )

            buttons_frame.pack(
                fill="x",
                pady=(15, 0)
            )

            favorite_button = tk.Button(
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
            )

            favorite_button.pack(
                side="left",
                padx=(0, 10)
            )

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

    search_entry.bind(
        "<KeyRelease>",
        search_while_typing
    )

    # ================= USER GREETING =================

    tk.Label(
        header,
        text=f"Welcome, {user['Name']}",
        font=("Arial", 11, "bold"),
        bg=WHITE,
        fg=NAVY
    ).place(
        relx=0.97,
        rely=0.5,
        anchor="e"
    )

    # ================= PAGE CONTENT =================

    content = tk.Frame(
        main_content,
        bg=BACKGROUND
    )

    content.pack(
        fill="both",
        expand=True,
        padx=35,
        pady=25
    )

    # Main Heading

    tk.Label(
        content,
        text="Your Library, Your Space.",
        font=("Arial", 23, "bold"),
        bg=BACKGROUND,
        fg=NAVY
    ).pack(anchor="w", pady=(0, 20))

    # ================= BANNER =================

    banner = tk.Frame(
        content,
        bg=NAVY,
        height=190
    )

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

    books_frame = tk.Frame(
        content,
        bg=BACKGROUND
    )

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

    quick_frame = tk.Frame(
        content,
        bg=BACKGROUND
    )

    quick_frame.pack(fill="x")

    quick_items = [
        ("▤", "My Borrowings"),
        ("♡", "My Favorites"),
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
            command=lambda page=name: show_message(page)
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
