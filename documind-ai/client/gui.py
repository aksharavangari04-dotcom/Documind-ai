import tkinter as tk
from tkinter import filedialog, messagebox
import requests
from config import BASE_URL
from auth import login as api_login
from api_client import CorpusClient
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
        font=("Arial", 12),
        bg="white",
        fg="black",
        insertbackground="black"
    )
    keyword_entry.pack(pady=10)

    # Text box styled with dark background and white text
    result_box = tk.Text(
        search_window,
        width=60,
        height=15,
        font=("Arial", 11),
        bg="#1E293B",
        fg="#FFFFFF",
        insertbackground="white",
        highlightthickness=1,
        highlightbackground="#3B82F6"
    )
    result_box.pack(pady=20)
     
    def search():
        keyword = keyword_entry.get().strip()

        if not keyword:
            messagebox.showwarning("Input Error", "Please enter a search keyword.")
            return

        # Prepare Text Box
        result_box.config(state="normal")
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, "Searching documents... Please wait.\n\n")
        search_window.update_idletasks()

        try: 
            results = client.search(keyword)

            result_box.delete("1.0", tk.END)

            if not results:
                result_box.insert(tk.END, f"No documents found for '{keyword}'.\n")
                return

            for item in results:
                try:
                    # Get record ID safely
                    rec_id = item.get("record_id") if isinstance(item, dict) else item
                    
                    record = None
                    if rec_id:
                        try:
                            record = client.get_record(rec_id)
                        except Exception as rec_err:
                            print(f"Warning: Failed to fetch record {rec_id}:", rec_err)

                    # Normalize record format
                    if hasattr(record, "json"):
                        record = record.json()
                    elif isinstance(record, str):
                        import json
                        try:
                            record = json.loads(record)
                        except Exception:
                            record = {"extracted_text": record}

                    # Fallback to item dict if record fetch failed
                    if not record and isinstance(item, dict):
                        record = item
                    elif not record:
                        record = {}

                    # Safely extract title and content
                    title_val = (
                        record.get("title") or 
                        record.get("name") or 
                        item.get("title") or 
                        f"Record ({rec_id})"
                    )
                    
                    desc_val = (
                        record.get("description") or 
                        record.get("extracted_text") or 
                        record.get("content") or 
                        record.get("text") or 
                        "No content available"
                    )

                    # Insert formatted result
                    result_box.insert(tk.END, f"📌 Title: {title_val}\n")
                    result_box.insert(tk.END, f"📝 Content:\n{desc_val}\n")
                    result_box.insert(tk.END, "\n-----------------------------------\n\n")
                    
                    search_window.update_idletasks()

                except Exception as item_err:
                    print(f"Skipping single item due to error: {item_err}")
                    continue

        except Exception as e:
            result_box.delete("1.0", tk.END)
            result_box.insert(tk.END, f"Error fetching search results: {e}\n")
    
    search_button = tk.Button(
        search_window,
        text="Search",
        command=search
    )
    search_button.pack(pady=10)


def open_categories():

    category_window = tk.Toplevel(window)
    category_window.title("Categories")
    category_window.geometry("700x600")
    category_window.configure(bg="#0F172A")
   
    title = tk.Label(
        category_window,
        text="Available Categories",
        font=("Arial", 20, "bold"),
        bg="#0F172A",
        fg="white"
    )
    title.pack(pady=20)

    text_box = tk.Text(
        category_window,
        width=50,
        height=18,
        font=("Arial", 11),
        bg="#1E293B",
        fg="#FFFFFF"
    )
    text_box.pack(pady=10)
   
    # Fetch real categories directly from Corpus API
    try:
        categories = client.get_categories()
        text_box.config(state="normal")
        text_box.delete("1.0", tk.END)

        if not categories:
            text_box.insert(tk.END, "No categories found or unable to fetch from API.\n")
        else:
            for cat in categories:
                cat_name = cat.get("name") or cat.get("category_name") if isinstance(cat, dict) else str(cat)
                text_box.insert(tk.END, f"• {cat_name}\n")
    except Exception as e:
        text_box.insert(tk.END, f"Error loading categories from API: {e}\n")

    text_box.config(state="disabled")


def open_view():

    view_window = tk.Toplevel(window)
    view_window.title("View Document")
    view_window.geometry("700x600")
    view_window.configure(bg="#0F172A")

    title = tk.Label(
        view_window,
        text="View Document Record",
        font=("Arial", 20, "bold"),
        bg="#0F172A",
        fg="white"
    )
    title.pack(pady=20)
    
    tk.Label(
        view_window,
        text="Enter Record ID",
        font=("Arial", 11),
        bg="#0F172A",
        fg="white"
    ).pack()

    id_entry = tk.Entry(
        view_window,
        width=35,
        font=("Arial", 12),
        bg="white",
        fg="black"
    )
    id_entry.pack(pady=10)

    text_box = tk.Text(
        view_window,
        width=70,
        height=14,
        font=("Arial", 11),
        bg="#1E293B",
        fg="#FFFFFF"
    )
    text_box.pack(pady=10)

    def view_document():
        rec_id = id_entry.get().strip()
        if not rec_id:
            messagebox.showerror("Error", "Please enter a valid Record ID")
            return

        text_box.config(state="normal")
        text_box.delete("1.0", tk.END)
        text_box.insert(tk.END, "Fetching record details from API... Please wait.\n")
        view_window.update_idletasks()

        try:
            doc = client.get_record(rec_id)
            text_box.delete("1.0", tk.END)

            if not doc:
                text_box.insert(tk.END, "Record not found or error communicating with API.")
            else:
                title_val = doc.get("title") or doc.get("name") or f"Record ({rec_id})"
                text_val = (
                    doc.get("description") or 
                    doc.get("extracted_text") or 
                    doc.get("content") or 
                    str(doc)
                )
                text_box.insert(
                    tk.END,
                    f"📌 Record ID: {rec_id}\n\n"
                    f"📌 Title: {title_val}\n\n"
                    f"📝 Content / Extracted Details:\n{text_val}"
                )
        except Exception as e:
            text_box.delete("1.0", tk.END)
            text_box.insert(tk.END, f"Error fetching record: {e}\n")

    tk.Button(
        view_window,
        text="View Record",
        command=view_document,
        bg="#3B82F6",
        fg="white",
        width=20,
        height=2,
        font=("Arial", 11, "bold")
    ).pack(pady=10)


def open_dashboard():

    dashboard = tk.Toplevel(window)
    dashboard.title("DocuMind AI Dashboard")
    dashboard.geometry("800x700")
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

    tk.Button(
        dashboard,
        text="Search Documents",
        width=25,
        height=2,
        bg="#3B82F6",
        fg="white",
        font=("Arial", 11, "bold"),
        command=open_search
    ).pack(pady=10)

    tk.Button(
        dashboard,
        text="Categories",
        width=25,
        height=2,
        bg="#8B5CF6",
        fg="white",
        font=("Arial", 11, "bold"),
        command=open_categories
    ).pack(pady=10)

    tk.Button(
        dashboard,
        text="View Document",
        width=25,
        height=2,
        bg="#10B981",
        fg="white",
        font=("Arial", 11, "bold"),
        command=open_view
    ).pack(pady=10)

    tk.Button(
        dashboard,
        text="Upload Document",
        width=25,
        height=2,
        bg="#F59E0B",
        fg="white",
        font=("Arial", 11, "bold"),
        command=open_upload
    ).pack(pady=10)

    tk.Button(
        dashboard,
        text="Summarize Document",
        width=25,
        height=2,
        bg="#EF4444",
        fg="white",
        font=("Arial", 11, "bold"),
        command=open_summarize
    ).pack(pady=10)

    def logout():
        dashboard.destroy()
        window.deiconify()

    tk.Button(
        dashboard,
        text="Logout",
        width=25,
        height=2,
        bg="#EF4444",
        fg="white",
        font=("Arial", 11, "bold"),
        command=logout
    ).pack(pady=20)


def open_upload():

    upload_window = tk.Toplevel(window)
    upload_window.title("Upload Document")
    upload_window.geometry("700x600")
    upload_window.configure(bg="#0F172A")

    tk.Label(
        upload_window,
        text="Upload Document to Corpus",
        font=("Arial", 20, "bold"),
        bg="#0F172A",
        fg="white"
    ).pack(pady=20)

    # Label to show selected file path
    path_label = tk.Label(
        upload_window,
        text="No file selected",
        font=("Arial", 10, "italic"),
        bg="#0F172A",
        fg="#94A3B8",
        wraplength=500
    )

    selected_file_path = {"path": ""}

    def select_file():
        file_path = filedialog.askopenfilename(
            title="Select a Document",
            filetypes=[
                ("All Supported Files", "*.pdf *.txt *.docx *.png *.jpg *.csv"),
                ("Text Files", "*.txt"),
                ("PDF Documents", "*.pdf"),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            selected_file_path["path"] = file_path
            path_label.config(text=f"Selected: {file_path}", fg="#38BDF8")

    # Browse File Button
    tk.Button(
        upload_window,
        text="📁 Choose File",
        command=select_file,
        bg="#334155",
        fg="white",
        font=("Arial", 11),
        width=20
    ).pack(pady=10)

    path_label.pack(pady=10)

    # Status Message Box
    status_box = tk.Text(
        upload_window,
        width=60,
        height=6,
        font=("Arial", 10),
        bg="#1E293B",
        fg="#FFFFFF"
    )
    status_box.pack(pady=10)

    def upload():
        file_path = selected_file_path["path"]
        if not file_path:
            messagebox.showerror("Error", "Please select a file first using 'Choose File'.")
            return

        status_box.delete("1.0", tk.END)
        status_box.insert(tk.END, "Uploading document to backend... Please wait.\n")
        upload_window.update_idletasks()

        try:
            response = client.upload_document(file_path)

            if response.status_code in [200, 201]:
                res_data = response.json() if hasattr(response, "json") else {}
                rec_id = res_data.get("record_id") or res_data.get("id") or "Success"
                
                status_box.delete("1.0", tk.END)
                status_box.insert(tk.END, f"✅ Upload Successful!\n")
                status_box.insert(tk.END, f"Record ID: {rec_id}\n")
                messagebox.showinfo("Success", "File uploaded successfully to real API!")
            else:
                status_box.delete("1.0", tk.END)
                status_box.insert(tk.END, f"❌ Upload Failed (Status {response.status_code}):\n{response.text}")

        except Exception as e:
            status_box.delete("1.0", tk.END)
            status_box.insert(tk.END, f"❌ Error uploading file: {e}\n")

    tk.Button(
        upload_window,
        text="Upload to Backend",
        command=upload,
        bg="#F59E0B",
        fg="white",
        font=("Arial", 11, "bold"),
        width=20,
        height=2
    ).pack(pady=15)


def open_summarize():

    summarize_window = tk.Toplevel(window)
    summarize_window.title("Summarize Document")
    summarize_window.geometry("700x600")
    summarize_window.configure(bg="#0F172A")

    title = tk.Label(
        summarize_window,
        text="Summarize Document",
        font=("Arial", 20, "bold"),
        bg="#0F172A",
        fg="white"
    )
    title.pack(pady=20)

    tk.Label(
        summarize_window,
        text="Enter Record ID",
        bg="#0F172A",
        fg="white",
        font=("Arial", 11)
    ).pack()

    document_id_entry = tk.Entry(
        summarize_window,
        width=35,
        font=("Arial", 12),
        bg="white",
        fg="black"
    )
    document_id_entry.pack(pady=10)

    summary_box = tk.Text(
        summarize_window,
        width=70,
        height=12,
        font=("Arial", 11),
        bg="#1E293B",
        fg="#FFFFFF"
    )
    summary_box.pack(pady=10)

    def summarize():
        rec_id = document_id_entry.get().strip()

        if not rec_id:
            messagebox.showerror("Error", "Please enter Record ID.")
            return

        summary_box.delete("1.0", tk.END)
        summary_box.insert(tk.END, "Fetching extracted text/summary from API... Please wait.\n")
        summarize_window.update_idletasks()

        try:
            result = client.summarize(rec_id)
            summary_box.delete("1.0", tk.END)

            if result:
                summary_text = result.get("summary") or result.get("text") or result.get("extracted_text") or str(result)
                summary_box.insert(tk.END, f"📝 Summary / Extracted Text:\n\n{summary_text}")
            else:
                summary_box.insert(tk.END, "Record summary not found or unavailable.")

        except Exception as e:
            summary_box.delete("1.0", tk.END)
            summary_box.insert(tk.END, f"Error generating summary: {e}\n")

    tk.Button(
        summarize_window,
        text="Summarize",
        width=20,
        height=2,
        bg="#EF4444",
        fg="white",
        font=("Arial", 11, "bold"),
        command=summarize
    ).pack(pady=10)


def login():

    login_window = tk.Toplevel(window)
    login_window.title("DocuMind AI Login")
    login_window.geometry("700x600")
    login_window.configure(bg="#1E293B")

    tk.Label(
        login_window,
        text="🔐 Login",
        font=("Arial", 22, "bold"),
        bg="#1E293B",
        fg="white"
    ).pack(pady=20)

    # Phone Number
    tk.Label(
        login_window,
        text="📱 Phone Number",
        font=("Arial", 11),
        bg="#1E293B",
        fg="white"
    ).pack()

    phone_entry = tk.Entry(
        login_window,
        width=30,
        font=("Arial", 11)
    )
    phone_entry.pack(pady=8)

    # Password
    tk.Label(
        login_window,
        text="🔑 Password",
        font=("Arial", 11),
        bg="#1E293B",
        fg="white"
    ).pack()

    password_entry = tk.Entry(
        login_window,
        width=30,
        show="*",
        font=("Arial", 11)
    )
    password_entry.pack(pady=8)

    # Load saved session
    session = load_session()
    if session:
        phone_entry.insert(0, session.get("phone", ""))
        password_entry.insert(0, session.get("password", ""))

    def submit_login():
        phone = phone_entry.get().strip()
        password = password_entry.get()

        if phone == "" or password == "":
            messagebox.showerror("Error", "Please enter phone number and password.")
            return

        try:
            response = api_login(phone, password)

            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token", "")

                save_session({
                    "phone": phone,
                    "password": password,
                    "username": data.get("username", ""),
                    "access_token": token
                })

                client.token = token
                
                # Close login window & transition straight to Dashboard
                login_window.destroy()
                window.withdraw()
                open_dashboard()

            elif response.status_code == 401:
                messagebox.showerror("Login Failed", "Incorrect phone number or password.")
            else:
                messagebox.showerror("Error", response.text)

        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    tk.Button(
        login_window,
        text="🚀 Login",
        width=20,
        height=2,
        bg="#14B8A6",
        fg="white",
        font=("Arial", 11, "bold"),
        command=submit_login
    ).pack(pady=25)


# Main Application Window
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

login_button = tk.Button(
    window,
    text="Login",
    width=22,
    height=2,
    bg="#14B8A6",
    fg="white",
    font=("Arial", 12, "bold"),
    command=login
)
login_button.pack(pady=30)

window.mainloop()