
import tkinter as tk
from tkinter import messagebox

from modules.user_model import authenticate_user
from gui.student_dashboard import open_student_dashboard

# =========================
# COLORS
# =========================

NAVY = "#142F43"
DARK_NAVY = "#102637"
TEAL = "#258C8C"
LIGHT_TEAL = "#E8F4F3"
BACKGROUND = "#F5F7F9"
WHITE = "#FFFFFF"
TEXT = "#243746"
GRAY = "#84919D"
BORDER = "#E5EAEE"


# =========================
# MAIN WINDOW
# =========================

root = None
selected_role = None
email_entry = None
password_entry = None
show_password = False


def clear_window():
    for widget in root.winfo_children():
        widget.destroy()


# =========================
# ROLE SELECTION PAGE
# =========================

def open_role_selection():

    global selected_role

    selected_role = None
    clear_window()

    root.title("MIDAD | Welcome")
    root.geometry("1100x700")
    root.minsize(900, 650)
    root.configure(bg=BACKGROUND)

    # Main container
    main_frame = tk.Frame(root, bg=BACKGROUND)
    main_frame.pack(fill="both", expand=True)

    # Left branding section
    left_frame = tk.Frame(
        main_frame,
        bg=NAVY,
        width=400
    )
    left_frame.pack(side="left", fill="both")
    left_frame.pack_propagate(False)

    tk.Label(
        left_frame,
        text="MIDAD",
        font=("Arial", 38, "bold"),
        fg=WHITE,
        bg=NAVY
    ).pack(pady=(190, 10))

    tk.Label(
        left_frame,
        text="SMART UNIVERSITY LIBRARY",
        font=("Arial", 11, "bold"),
        fg="#B8D5D8",
        bg=NAVY
    ).pack()

    tk.Frame(
        left_frame,
        bg=TEAL,
        height=3,
        width=70
    ).pack(pady=25)

    tk.Label(
        left_frame,
        text="A World of Knowledge\nAwaits You.",
        font=("Arial", 19),
        fg=WHITE,
        bg=NAVY,
        justify="center"
    ).pack()

    # Right section
    right_frame = tk.Frame(
        main_frame,
        bg=BACKGROUND
    )
    right_frame.pack(
        side="right",
        fill="both",
        expand=True
    )

    tk.Label(
        right_frame,
        text="Welcome to MIDAD",
        font=("Arial", 25, "bold"),
        fg=NAVY,
        bg=BACKGROUND
    ).pack(pady=(100, 10))

    tk.Label(
        right_frame,
        text="Please select your account type to continue",
        font=("Arial", 11),
        fg=GRAY,
        bg=BACKGROUND
    ).pack(pady=(0, 35))

    # Role cards
    roles = [
        ("ADMIN", "Manage the library system", "Administrator"),
        ("STUDENT", "Explore and borrow books", "Student"),
        ("INSTRUCTOR", "Access instructor services", "Instructor")
    ]

    for title, description, role in roles:

        card = tk.Frame(
            right_frame,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1,
            cursor="hand2"
        )

        card.pack(
            fill="x",
            padx=75,
            pady=9,
            ipady=12
        )

        title_label = tk.Label(
            card,
            text=f"LOGIN AS {title}",
            font=("Arial", 12, "bold"),
            fg=NAVY,
            bg=WHITE,
            cursor="hand2"
        )
        title_label.pack(anchor="w", padx=20, pady=(8, 3))

        description_label = tk.Label(
            card,
            text=description,
            font=("Arial", 10),
            fg=GRAY,
            bg=WHITE,
            cursor="hand2"
        )
        description_label.pack(anchor="w", padx=20, pady=(0, 8))

        def select_role(selected, event=None):
            open_login_page(selected)

        card.bind(
            "<Button-1>",
            lambda event, r=role: select_role(r)
        )

        title_label.bind(
            "<Button-1>",
            lambda event, r=role: select_role(r)
        )

        description_label.bind(
            "<Button-1>",
            lambda event, r=role: select_role(r)
        )

        def on_enter(event, c=card):
            c.configure(
                highlightbackground=TEAL,
                highlightthickness=2
            )

        def on_leave(event, c=card):
            c.configure(
                highlightbackground=BORDER,
                highlightthickness=1
            )

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

    tk.Label(
        right_frame,
        text="© MIDAD - Smart University Library",
        font=("Arial", 9),
        fg=GRAY,
        bg=BACKGROUND
    ).pack(side="bottom", pady=25)


# =========================
# LOGIN PAGE
# =========================

def open_login_page(role):

    global selected_role
    global email_entry, password_entry
    global show_password

    selected_role = role
    show_password = False

    clear_window()

    root.title("MIDAD | Login")
    root.geometry("1100x700")
    root.configure(bg=BACKGROUND)

    # Main container
    main_frame = tk.Frame(root, bg=BACKGROUND)
    main_frame.pack(fill="both", expand=True)

    # Branding section
    left_frame = tk.Frame(
        main_frame,
        bg=NAVY,
        width=400
    )
    left_frame.pack(side="left", fill="both")
    left_frame.pack_propagate(False)

    tk.Label(
        left_frame,
        text="MIDAD",
        font=("Arial", 38, "bold"),
        fg=WHITE,
        bg=NAVY
    ).pack(pady=(190, 10))

    tk.Label(
        left_frame,
        text="SMART UNIVERSITY LIBRARY",
        font=("Arial", 11, "bold"),
        fg="#B8D5D8",
        bg=NAVY
    ).pack()

    tk.Frame(
        left_frame,
        bg=TEAL,
        height=3,
        width=70
    ).pack(pady=25)

    tk.Label(
        left_frame,
        text="Your Library,\nYour Space.",
        font=("Arial", 19),
        fg=WHITE,
        bg=NAVY,
        justify="center"
    ).pack()

    # Right section
    right_frame = tk.Frame(
        main_frame,
        bg=BACKGROUND
    )
    right_frame.pack(
        side="right",
        fill="both",
        expand=True
    )

    tk.Label(
        right_frame,
        text="Welcome Back!",
        font=("Arial", 27, "bold"),
        fg=NAVY,
        bg=BACKGROUND
    ).pack(pady=(125, 8))

    tk.Label(
        right_frame,
        text=f"Sign in to your {selected_role.lower()} account",
        font=("Arial", 11),
        fg=GRAY,
        bg=BACKGROUND
    ).pack(pady=(0, 35))

    # Login form
    form_frame = tk.Frame(
        right_frame,
        bg=BACKGROUND,
        width=380
    )
    form_frame.pack()

    # Email
    tk.Label(
        form_frame,
        text="Email Address",
        font=("Arial", 10, "bold"),
        fg=TEXT,
        bg=BACKGROUND
    ).pack(anchor="w", pady=(0, 8))

    email_entry = tk.Entry(
        form_frame,
        font=("Arial", 12),
        bg=WHITE,
        fg=TEXT,
        relief="flat",
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=TEAL,
        width=38
    )
    email_entry.pack(ipady=12, pady=(0, 22))

    # Password
    tk.Label(
        form_frame,
        text="Password",
        font=("Arial", 10, "bold"),
        fg=TEXT,
        bg=BACKGROUND
    ).pack(anchor="w", pady=(0, 8))

    password_frame = tk.Frame(
        form_frame,
        bg=WHITE,
        highlightbackground=BORDER,
        highlightthickness=1
    )
    password_frame.pack(fill="x", pady=(0, 10))

    password_entry = tk.Entry(
        password_frame,
        font=("Arial", 12),
        bg=WHITE,
        fg=TEXT,
        relief="flat",
        show="*"
    )
    password_entry.pack(
        side="left",
        fill="x",
        expand=True,
        padx=10,
        ipady=10
    )

    show_button = tk.Button(
        password_frame,
        text="Show",
        font=("Arial", 9),
        fg=TEAL,
        bg=WHITE,
        relief="flat",
        cursor="hand2",
        command=toggle_password
    )
    show_button.pack(side="right", padx=10)

    # Sign In button
    sign_in_button = tk.Button(
        form_frame,
        text="SIGN IN",
        font=("Arial", 11, "bold"),
        fg=WHITE,
        bg=TEAL,
        activebackground=NAVY,
        activeforeground=WHITE,
        relief="flat",
        cursor="hand2",
        command=login
    )
    sign_in_button.pack(
        fill="x",
        ipady=12,
        pady=(20, 15)
    )

    # Back button
    back_button = tk.Button(
        right_frame,
        text="← Back to account selection",
        font=("Arial", 10),
        fg=TEAL,
        bg=BACKGROUND,
        activebackground=BACKGROUND,
        relief="flat",
        cursor="hand2",
        command=open_role_selection
    )
    back_button.pack(pady=10)

    tk.Label(
        right_frame,
        text="© MIDAD - Smart University Library",
        font=("Arial", 9),
        fg=GRAY,
        bg=BACKGROUND
    ).pack(side="bottom", pady=20)

    email_entry.focus_set()

    root.bind("<Return>", lambda event: login())


# =========================
# SHOW / HIDE PASSWORD
# =========================

def toggle_password():

    global show_password

    show_password = not show_password

    if show_password:
        password_entry.config(show="")
    else:
        password_entry.config(show="*")


# =========================
# LOGIN FUNCTION
# =========================

def login():

    email = email_entry.get().strip()
    password = password_entry.get()

    if not email or not password:
        messagebox.showwarning(
            "Missing Information",
            "Please enter your email address and password."
        )
        return

    user = authenticate_user(email, password)

    if user is None:
        messagebox.showerror(
            "Login Failed",
            "Invalid email address or password."
        )
        return

    # Verify selected role against database role
    if user["Role"] != selected_role:

        messagebox.showerror(
            "Access Denied",
            f"This account is not registered as {selected_role}."
        )
        return

    messagebox.showinfo(
        "Login Successful",
        f"Welcome, {user['Name']}!"
    )

    if selected_role == "Student":

        root.unbind("<Return>")
        root.destroy()
        open_student_dashboard(user)

    elif selected_role == "Instructor":

        messagebox.showinfo(
            "Coming Soon",
            "Instructor Dashboard is coming soon."
        )

    elif selected_role == "Administrator":

        messagebox.showinfo(
            "Coming Soon",
            "Administrator Dashboard is coming soon."
        )


# =========================
# RUN APPLICATION
# =========================

def open_login_window():

    global root

    root = tk.Tk()
    root.geometry("1100x700")
    root.minsize(900, 650)

    open_role_selection()

    root.mainloop()


if __name__ == "__main__":
    open_login_window()
