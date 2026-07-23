import tkinter as tk
from tkinter import messagebox
from auth import login as api_login
from api_client import CorpusClient
from sample_data import documents
from session import save_session, load_session

client = CorpusClient()

def open_search():

    search_window = tk.Toplevel(window)
    search_window.title("Search Documents")
    search_window.geometry("700x600")
    search_window.configure(bg="#0F172A")

    title = tk.Label(
        search_window,
        text="Search Documents",
        font=("Arial", 20, "bold"),
        bg="#0F172A",
        fg="white"
    )
    title.pack(pady=20)

    keyword_entry = tk.Entry(
        search_window,
        width=35,
        font=("Arial", 12)
    )
    keyword_entry.pack(pady=10)

    result_box = tk.Text(
        search_window,
        width=60,
        height=15,
        font=("Arial", 11)
    )
    result_box.pack(pady=20)

    def search():

        keyword = keyword_entry.get().strip()

        results = client.search(keyword)

        result_box.delete("1.0", tk.END)

        if not results:
            result_box.insert(tk.END, "No documents found.")
            return

        for doc in results:
            result_box.insert(
                tk.END,
                f"ID: {doc['id']}\n"
                f"Title: {doc['title']}\n"
                f"Category: {doc['category']}\n\n"
            )

    tk.Button(
        search_window,
        text="Search",
        command=search,
        bg="#3B82F6",
        fg="white",
        width=20,
        height=2
    ).pack()

def open_categories():

    category_window = tk.Toplevel(window)

    category_window.title("Categories")
    category_window.geometry("700x600")
    category_window.configure(bg="#0F172A")
   
    title = tk.Label(

        category_window,
        text="Available Categories",
        font=("Arial",20,"bold"),
        bg="#0F172A",
        fg="white"
    )

    title.pack(pady=20)

    text_box = tk.Text(
        category_window,
        width=40,
        height=18,
        font=("Arial",12)
     )

    text_box.pack(pady=10)
   
    categories = set()

    for doc in documents:
        categories.add(doc["category"])

    for category in sorted(categories):
        text_box.insert(
            tk.END,
            f"• {category}\n"
        )
    text_box.config(state="disabled")


def open_view():

    view_window = tk.Toplevel(window)

    view_window.title("View Document")
    view_window.geometry("700x600")
    view_window.configure(bg="#0F172A")

    title = tk.Label(
        view_window,
        text="View First Document",
        font=("Arial", 20, "bold"),
        bg="#0F172A",
        fg="white"
    )
    title.pack(pady=20)
    
    tk.Label(
        view_window,
        text="Enter Document ID",
        font=("Arial", 11),
        bg="#0F172A",
        fg="white"
    ).pack()

    id_entry = tk.Entry(
        view_window,
        width=20,
        font=("Arial", 12)
    )
    id_entry.pack(pady=10)

    text_box = tk.Text(
        view_window,
        width=70,
        height=12,
        font=("Arial", 11)
    )
    text_box.pack(pady=10)

    text_box.config(state="disabled")

    def view_document():

        text_box.config(state="normal")
        text_box.delete("1.0", tk.END)

        try:
            doc_id = int(id_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Enter a valid ID")
            return

        doc = client.get_document(doc_id)

        if doc is None:
            text_box.insert(tk.END, "Document not found.")
        else:
            text_box.insert(
                tk.END,
                f"ID: {doc['id']}\n\n"
                f"Title: {doc['title']}\n\n"
                f"Category: {doc['category']}\n\n"
                f"Content:\n{doc['content']}"
            )

        text_box.config(state="disabled")

    tk.Button(
        view_window,
        text="View",
        command=view_document,
        bg="#3B82F6",
        fg="white",
        width=20,
        height=2
    ).pack(pady=10)


def open_dashboard():
    dashboard = tk.Toplevel(window)

    dashboard.title("DocuMind AI Dashboard")
    dashboard.geometry("800x500")
    dashboard.configure(bg="#0F172A")

    title = tk.Label(
        dashboard,
        text="DocuMind AI Dashboard",
        font=("Arial", 24, "bold"),
        bg="#0F172A",
        fg="white"
    )
    title.pack(pady=20)

    welcome = tk.Label(
        dashboard,
        text="Welcome! You have successfully logged in.",
        font=("Arial", 14),
        bg="#0F172A",
        fg="#CBD5E1"
    )
    welcome.pack(pady=10)

    search_button = tk.Button(
        dashboard,
        text="Search Documents",
        width=25,
        height=2,
        bg="#3B82F6",
        fg="white",
        font=("Arial", 11, "bold"),
        command=open_search
    )
    search_button.pack(pady=10)

    categories_button = tk.Button(
        dashboard,
        text="Categories",
        width=25,
        height=2,
        bg="#8B5CF6",
        fg="white",
        font=("Arial", 11, "bold"),
        command=open_categories
    )
    
    categories_button.pack(pady=10)

    view_button = tk.Button(
        dashboard,
        text="View Document",
        width=25,
        height=2,
        bg="#10B981",
        fg="white",
        font=("Arial", 11, "bold"),
        command=open_view
    )

    view_button.pack(pady=10)

    upload_button = tk.Button(
        dashboard,
        text="Upload Document",
        width=25,
        height=2,
        bg="#F59E0B",
        fg="white",
        font=("Arial", 11, "bold"),
        command=open_upload
    )
    upload_button.pack(pady=10)

    logout_button = tk.Button(
        dashboard,
        text="Logout",
        width=25,
        height=2,
        bg="#EF4444",
        fg="white",
        font=("Arial", 11, "bold"),
        command=dashboard.destroy
    )
    logout_button.pack(pady=20)


def open_upload():

    upload_window = tk.Toplevel(window)

    upload_window.title("Upload Document")
    upload_window.geometry("700x600")
    upload_window.configure(bg="#0F172A")

    tk.Label(
        upload_window,
        text="Upload Document",
        font=("Arial", 20, "bold"),
        bg="#0F172A",
        fg="white"
    ).pack(pady=20)

    tk.Label(
        upload_window,
        text="File Name",
        bg="#0F172A",
        fg="white"
    ).pack()

    file_entry = tk.Entry(upload_window, width=35)
    file_entry.pack(pady=10)

    def upload():
        filename = file_entry.get().strip()

        if filename == "":
            messagebox.showerror("Error", "Please enter a file name.")
            return

        messagebox.showinfo(
            "Success",
            f"{filename} uploaded successfully! (Demo Mode)"
        )

    tk.Button(
        upload_window,
        text="Upload",
        command=upload,
        bg="#F59E0B",
        fg="white",
        width=20,
        height=2
    ).pack(pady=20)


def login():

    login_window = tk.Toplevel(window)
    login_window.title("DocuMind AI Login")
    login_window.geometry("700x600")
    login_window.configure(bg="#1E293B")

    login_title = tk.Label(
        login_window,
        text="Login",
        font=("Arial", 22, "bold"),
        bg="#1E293B",
        fg="white"
    )
    login_title.pack(pady=20)

    phone_label = tk.Label(
        login_window,
        text="Phone Number",
        font=("Arial", 11),
        bg="#1E293B",
        fg="white"
    )
    phone_label.pack()

    phone_entry = tk.Entry(
        login_window,
        width=30,
        font=("Arial", 11)
    )
    phone_entry.pack(pady=8)

    password_label = tk.Label(
        login_window,
        text="Password",
        font=("Arial", 11),
        bg="#1E293B",
        fg="white"
    )
    password_label.pack()

    password_entry = tk.Entry(
        login_window,
        width=30,
        show="*",
        font=("Arial", 11)
    )
    password_entry.pack(pady=8)

    def submit_login():

        phone = phone_entry.get().strip()
        password = password_entry.get()

        try:
            response = api_login(phone, password)

            print("Status Code:", response.status_code)
            print("Response:", response.text)

            if response.status_code == 200:

                data = response.json()

                save_session({
                    "access_token": data["access_token"],
                    "username": data["username"],
                    "phone": data["phone"]
                })

                messagebox.showinfo(
                    "Success",
                    "Login Successful!"
                )

                login_window.destroy()
                open_dashboard()

            elif response.status_code == 401:
                messagebox.showerror(
                    "Login Failed",
                    "Incorrect phone number or password."
                )

            else:
                messagebox.showerror(
                    "Error",
                    response.text
                )

        except Exception as e:
            messagebox.showerror(
                "Connection Error",
                str(e)
            )

    submit_button = tk.Button(
        login_window,
        text="Login",
        width=20,
        height=2,
        bg="#14B8A6",
        fg="white",
        font=("Arial", 11, "bold"),
        command=submit_login
    )
    submit_button.pack(pady=25)


window = tk.Tk()

window.title("DocuMind AI")
window.geometry("800x550")
window.configure(bg="#0F172A")

title = tk.Label(
    window,
    text="DocuMind AI",
    font=("Arial", 28, "bold"),
    bg="#0F172A",
    fg="white"
)
title.pack(pady=(40, 10))

subtitle = tk.Label(
    window,
    text="Intelligent Corpus Assistant",
    font=("Arial", 14),
    bg="#0F172A",
    fg="#CBD5E1"
)
subtitle.pack()

session = load_session()

login_button = tk.Button(
    window,
    text="Login",
    width=22,
    height=2,
    bg="#14B8A6",
    fg="white",
    font=("Arial", 12, "bold"),
    command=open_dashboard if session else login
)
login_button.pack(pady=30)

window.mainloop()
