import tkinter as tk
from tkinter import messagebox


def login():

    login_window = tk.Toplevel(window)

    login_window.title("Login")
    login_window.geometry("400x300")


    username_label = tk.Label(
        login_window,
        text="Username"
    )
    username_label.pack(pady=5)


    username_entry = tk.Entry(login_window)
    username_entry.pack(pady=5)


    password_label = tk.Label(
        login_window,
        text="Password"
    )
    password_label.pack(pady=5)


    password_entry = tk.Entry(
        login_window,
        show="*"
    )
    password_entry.pack(pady=5)


    def submit_login():

        username = username_entry.get()
        password = password_entry.get()

        print("Username:", username)
        print("Password:", password)

        messagebox.showinfo(
            "Login",
            "Login button working"
        )


    submit_button = tk.Button(
        login_window,
        text="Submit Login",
        command=submit_login
    )

    submit_button.pack(pady=20)



window = tk.Tk()

window.title("DocuMind AI")
window.geometry("700x500")


title = tk.Label(
    window,
    text="Welcome to DocuMind AI",
    font=("Arial", 20)
)

title.pack(pady=20)


login_button = tk.Button(
    window,
    text="Login",
    width=20,
    height=2,
    command=login
)

login_button.pack(pady=10)


window.mainloop()
