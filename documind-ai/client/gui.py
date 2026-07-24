import tkinter as tk
from tkinter import filedialog, messagebox
import requests
from config import BASE_URL
from auth import login as api_login
from api_client import CorpusClient
from session import save_session, load_session

# Initialize client
client = CorpusClient()

# Color Palette (Modern Dark Slate Theme)
BG_DARK = "#0F172A"       # Main window background
CARD_BG = "#1E293B"       # Card / Container background
TEXT_MAIN = "#F8FAFC"     # Primary text color
TEXT_MUTED = "#94A3B8"    # Subtitle / Muted text color
ACCENT_BLUE = "#3B82F6"   # Primary action buttons
ACCENT_TEAL = "#14B8A6"   # Secondary / Launch action buttons
ACCENT_GRAY = "#334155"   # Neutral / Logout button
BORDER_COLOR = "#334155"


def create_styled_button(parent, text, command, bg_color=ACCENT_BLUE, width=22, height=2):
    """Creates a flat, modern styled Tkinter button with hover feedback."""
    btn = tk.Button(
        parent,
        text=text,
        command=command,
        bg=bg_color,
        fg="white",
        activebackground="#2563EB",
        activeforeground="white",
        font=("DejaVu Sans", 11, "bold"),
        bd=0,
        relief="flat",
        cursor="hand2",
        width=width,
        height=height
    )
    return btn


# -------------------------------------------------------------------
# 1. SEARCH DOCUMENTS WINDOW
# -------------------------------------------------------------------
def open_search():
    search_window = tk.Toplevel(window)
    search_window.title("Search Documents")
    search_window.geometry("720x620")
    search_window.configure(bg=BG_DARK)

    tk.Label(
        search_window,
        text="Search Documents",
        font=("DejaVu Sans", 20, "bold"),
        bg=BG_DARK,
        fg=TEXT_MAIN
    ).pack(pady=(25, 5))

    tk.Label(
        search_window,
        text="Enter a keyword to query the Indic Corpus database",
        font=("DejaVu Sans", 10),
        bg=BG_DARK,
        fg=TEXT_MUTED
    ).pack(pady=(0, 15))

    # Input Frame
    input_frame = tk.Frame(search_window, bg=BG_DARK)
    input_frame.pack(pady=5)

    keyword_entry = tk.Entry(
        input_frame,
        width=32,
        font=("DejaVu Sans", 12),
        bg=CARD_BG,
        fg=TEXT_MAIN,
        insertbackground="white",
        bd=1,
        relief="solid"
    )
    keyword_entry.pack(side="left", padx=5, ipady=4)

    # Result Text Area
    result_box = tk.Text(
        search_window,
        width=65,
        height=14,
        font=("DejaVu Sans", 10),
        bg=CARD_BG,
        fg=TEXT_MAIN,
        insertbackground="white",
        bd=0,
        padx=12,
        pady=12,
        wrap="word"
    )
    result_box.pack(pady=20)

    def search():
        keyword = keyword_entry.get().strip()

        if not keyword:
            messagebox.showwarning("Input Required", "Please enter a search keyword.")
            return

        result_box.config(state="normal")
        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, "Querying database... Please wait.\n\n")
        search_window.update_idletasks()

        try:
            results = client.search(keyword)
            result_box.delete("1.0", tk.END)

            if not results:
                result_box.insert(tk.END, f"No matching documents found for '{keyword}'.\n")
                return

            for item in results:
                try:
                    # Extract the ID directly from the record payload or item dictionary
                    rec_id = None
                    if isinstance(item, dict):
                        rec_id = item.get("id") or item.get("record_id") or item.get("_id")
                    else:
                        rec_id = item

                    record = None
                    if rec_id:
                        try:
                            record = client.get_record(rec_id)
                        except Exception:
                            pass

                    if hasattr(record, "json"):
                        record = record.json()
                    elif not isinstance(record, dict):
                        record = item if isinstance(item, dict) else {}

                    # Fallback check for ID inside the retrieved record object
                    if not rec_id and isinstance(record, dict):
                        rec_id = record.get("id") or record.get("record_id")

                    title_val = record.get("title") or record.get("name") or f"Record ({rec_id})"
                    desc_val = (
                        record.get("description") or 
                        record.get("extracted_text") or 
                        record.get("content") or 
                        "No content text available."
                    )

                    # Display ID clearly at the top of each item
                    result_box.insert(tk.END, f"RECORD ID: {rec_id}\n")
                    result_box.insert(tk.END, f"TITLE: {title_val}\n")
                    result_box.insert(tk.END, f"CONTENT:\n{desc_val}\n")
                    result_box.insert(tk.END, "-" * 50 + "\n\n")
                    search_window.update_idletasks()

                except Exception:
                    continue

        except Exception as e:
            result_box.delete("1.0", tk.END)
            result_box.insert(tk.END, f"Error fetching search results: {e}\n")

    search_btn = create_styled_button(input_frame, "Search", search, bg_color=ACCENT_BLUE, width=10, height=1)
    search_btn.pack(side="left", padx=5)


# -------------------------------------------------------------------
# 2. CATEGORIES WINDOW
# -------------------------------------------------------------------
def open_categories():
    category_window = tk.Toplevel(window)
    category_window.title("Categories")
    category_window.geometry("600x550")
    category_window.configure(bg=BG_DARK)

    tk.Label(
        category_window,
        text="Available Categories",
        font=("DejaVu Sans", 20, "bold"),
        bg=BG_DARK,
        fg=TEXT_MAIN
    ).pack(pady=20)

    text_box = tk.Text(
        category_window,
        width=45,
        height=16,
        font=("DejaVu Sans", 11),
        bg=CARD_BG,
        fg=TEXT_MAIN,
        bd=0,
        padx=15,
        pady=15
    )
    text_box.pack(pady=10)

    try:
        categories = client.get_categories()
        text_box.config(state="normal")
        text_box.delete("1.0", tk.END)

        if not categories:
            text_box.insert(tk.END, "No categories available.\n")
        else:
            for cat in categories:
                cat_name = cat.get("name") or cat.get("category_name") if isinstance(cat, dict) else str(cat)
                text_box.insert(tk.END, f"•  {cat_name}\n\n")
    except Exception as e:
        text_box.insert(tk.END, f"Error loading categories: {e}\n")

    text_box.config(state="disabled")


# -------------------------------------------------------------------
# 3. VIEW DOCUMENT WINDOW
# -------------------------------------------------------------------
def open_view():
    view_window = tk.Toplevel(window)
    view_window.title("View Document")
    view_window.geometry("700x600")
    view_window.configure(bg=BG_DARK)

    tk.Label(
        view_window,
        text="View Record Details",
        font=("DejaVu Sans", 20, "bold"),
        bg=BG_DARK,
        fg=TEXT_MAIN
    ).pack(pady=(20, 5))

    input_frame = tk.Frame(view_window, bg=BG_DARK)
    input_frame.pack(pady=10)

    tk.Label(input_frame, text="Record ID:", font=("DejaVu Sans", 11), bg=BG_DARK, fg=TEXT_MAIN).pack(side="left", padx=5)

    id_entry = tk.Entry(input_frame, width=30, font=("DejaVu Sans", 11), bg=CARD_BG, fg=TEXT_MAIN, insertbackground="white", bd=1)
    id_entry.pack(side="left", padx=5, ipady=3)

    text_box = tk.Text(view_window, width=65, height=14, font=("DejaVu Sans", 10), bg=CARD_BG, fg=TEXT_MAIN, padx=12, pady=12, wrap="word")
    text_box.pack(pady=15)

    def view_document():
        rec_id = id_entry.get().strip()
        if not rec_id:
            messagebox.showerror("Error", "Please enter a Record ID.")
            return

        text_box.config(state="normal")
        text_box.delete("1.0", tk.END)
        text_box.insert(tk.END, "Fetching record details... Please wait.\n")
        view_window.update_idletasks()

        try:
            doc = client.get_record(rec_id)
            text_box.delete("1.0", tk.END)

            if not doc:
                text_box.insert(tk.END, "Record not found.")
            else:
                title_val = doc.get("title") or doc.get("name") or f"Record ({rec_id})"
                text_val = doc.get("description") or doc.get("extracted_text") or doc.get("content") or str(doc)
                text_box.insert(tk.END, f"RECORD ID: {rec_id}\n\nTITLE: {title_val}\n\nCONTENT:\n{text_val}")
        except Exception as e:
            text_box.delete("1.0", tk.END)
            text_box.insert(tk.END, f"Error: {e}\n")

    btn = create_styled_button(input_frame, "Fetch", view_document, bg_color=ACCENT_BLUE, width=10, height=1)
    btn.pack(side="left", padx=5)


# -------------------------------------------------------------------
# 4. UPLOAD DOCUMENT WINDOW
# -------------------------------------------------------------------
def open_upload():
    upload_window = tk.Toplevel(window)
    upload_window.title("Upload Document")
    upload_window.geometry("600x500")
    upload_window.configure(bg=BG_DARK)

    tk.Label(
        upload_window,
        text="Upload Document",
        font=("DejaVu Sans", 20, "bold"),
        bg=BG_DARK,
        fg=TEXT_MAIN
    ).pack(pady=20)

    selected_file = {"path": ""}

    path_label = tk.Label(upload_window, text="No file selected", font=("DejaVu Sans", 10, "italic"), bg=BG_DARK, fg=TEXT_MUTED, wraplength=450)

    def select_file():
        path = filedialog.askopenfilename(
            title="Select Document",
            filetypes=[("Documents", "*.pdf *.txt *.docx *.csv"), ("All Files", "*.*")]
        )
        if path:
            selected_file["path"] = path
            path_label.config(text=f"Selected: {path}", fg=TEXT_MAIN)

    create_styled_button(upload_window, "Choose File", select_file, bg_color=ACCENT_GRAY, width=18, height=1).pack(pady=10)
    path_label.pack(pady=10)

    status_box = tk.Text(upload_window, width=55, height=5, font=("DejaVu Sans", 10), bg=CARD_BG, fg=TEXT_MAIN, padx=10, pady=10)
    status_box.pack(pady=10)

    def upload():
        if not selected_file["path"]:
            messagebox.showerror("Error", "Please select a file first.")
            return

        status_box.delete("1.0", tk.END)
        status_box.insert(tk.END, "Uploading document to backend...\n")
        upload_window.update_idletasks()

        try:
            res = client.upload_document(selected_file["path"])
            if res.status_code in [200, 201]:
                status_box.delete("1.0", tk.END)
                status_box.insert(tk.END, "Upload Successful!\n")
            else:
                status_box.delete("1.0", tk.END)
                status_box.insert(tk.END, f"Upload Failed ({res.status_code}):\n{res.text}")
        except Exception as e:
            status_box.delete("1.0", tk.END)
            status_box.insert(tk.END, f"Error: {e}\n")

    create_styled_button(upload_window, "Upload to Corpus", upload, bg_color=ACCENT_BLUE, width=20, height=2).pack(pady=15)


# -------------------------------------------------------------------
# 5. SUMMARIZE DOCUMENT WINDOW
# -------------------------------------------------------------------
def open_summarize():
    sum_window = tk.Toplevel(window)
    sum_window.title("Summarize Document")
    sum_window.geometry("650x550")
    sum_window.configure(bg=BG_DARK)

    tk.Label(sum_window, text="Summarize Document", font=("DejaVu Sans", 20, "bold"), bg=BG_DARK, fg=TEXT_MAIN).pack(pady=20)

    input_frame = tk.Frame(sum_window, bg=BG_DARK)
    input_frame.pack(pady=5)

    tk.Label(input_frame, text="Record ID:", font=("DejaVu Sans", 11), bg=BG_DARK, fg=TEXT_MAIN).pack(side="left", padx=5)
    doc_entry = tk.Entry(input_frame, width=28, font=("DejaVu Sans", 11), bg=CARD_BG, fg=TEXT_MAIN, insertbackground="white", bd=1)
    doc_entry.pack(side="left", padx=5, ipady=3)

    summary_box = tk.Text(sum_window, width=60, height=12, font=("DejaVu Sans", 10), bg=CARD_BG, fg=TEXT_MAIN, padx=12, pady=12, wrap="word")
    summary_box.pack(pady=15)

    def summarize():
        rec_id = doc_entry.get().strip()
        if not rec_id:
            messagebox.showerror("Error", "Please enter a Record ID.")
            return

        summary_box.delete("1.0", tk.END)
        summary_box.insert(tk.END, "Generating summary... Please wait.\n")
        sum_window.update_idletasks()

        try:
            res = client.summarize(rec_id)
            summary_box.delete("1.0", tk.END)
            if res:
                text = res.get("summary") or res.get("extracted_text") or str(res)
                summary_box.insert(tk.END, f"SUMMARY / EXTRACTED TEXT:\n\n{text}")
            else:
                summary_box.insert(tk.END, "Summary unavailable for this record.")
        except Exception as e:
            summary_box.delete("1.0", tk.END)
            summary_box.insert(tk.END, f"Error: {e}\n")

    btn = create_styled_button(input_frame, "Summarize", summarize, bg_color=ACCENT_BLUE, width=12, height=1)
    btn.pack(side="left", padx=5)


# -------------------------------------------------------------------
# 6. DASHBOARD WINDOW (Placed AFTER open_summarize)
# -------------------------------------------------------------------
def open_dashboard():
    dashboard = tk.Toplevel(window)
    dashboard.title("DocuMind AI - Dashboard")
    dashboard.geometry("750x650")
    dashboard.configure(bg=BG_DARK)

    tk.Label(
        dashboard,
        text="DocuMind AI Dashboard",
        font=("DejaVu Sans", 22, "bold"),
        bg=BG_DARK,
        fg=TEXT_MAIN
    ).pack(pady=(35, 5))

    tk.Label(
        dashboard,
        text="Connected to Indic Corpus API",
        font=("DejaVu Sans", 11),
        bg=BG_DARK,
        fg=TEXT_MUTED
    ).pack(pady=(0, 25))

    # Center Button Menu
    menu_card = tk.Frame(dashboard, bg=CARD_BG, padx=30, pady=25)
    menu_card.pack(pady=10)

    buttons = [
        ("Search Documents", open_search, ACCENT_BLUE),
        ("Categories Explorer", open_categories, ACCENT_BLUE),
        ("View Document Record", open_view, ACCENT_BLUE),
        ("Upload File to Corpus", open_upload, ACCENT_BLUE),
        ("Summarize Document", open_summarize, ACCENT_BLUE),
    ]

    for label, cmd, color in buttons:
        btn = create_styled_button(menu_card, label, cmd, bg_color=color, width=28, height=2)
        btn.pack(pady=8)

    def logout():
        dashboard.destroy()
        window.deiconify()

    create_styled_button(dashboard, "Logout", logout, bg_color=ACCENT_GRAY, width=15, height=1).pack(pady=20)


# -------------------------------------------------------------------
# 7. LOGIN WINDOW
# -------------------------------------------------------------------
def login():
    login_window = tk.Toplevel(window)
    login_window.title("DocuMind AI Login")
    login_window.geometry("500x520")
    login_window.configure(bg=BG_DARK)

    card = tk.Frame(login_window, bg=CARD_BG, padx=30, pady=30)
    card.pack(pady=40)

    tk.Label(
        card,
        text="User Authentication",
        font=("DejaVu Sans", 18, "bold"),
        bg=CARD_BG,
        fg=TEXT_MAIN
    ).pack(pady=(0, 20))

    tk.Label(card, text="Phone Number", font=("DejaVu Sans", 10, "bold"), bg=CARD_BG, fg=TEXT_MUTED).pack(anchor="w")
    phone_entry = tk.Entry(card, width=28, font=("DejaVu Sans", 11), bg=BG_DARK, fg=TEXT_MAIN, insertbackground="white", bd=1)
    phone_entry.pack(pady=(4, 15), ipady=4)

    tk.Label(card, text="Password", font=("DejaVu Sans", 10, "bold"), bg=CARD_BG, fg=TEXT_MUTED).pack(anchor="w")
    password_entry = tk.Entry(card, width=28, show="*", font=("DejaVu Sans", 11), bg=BG_DARK, fg=TEXT_MAIN, insertbackground="white", bd=1)
    password_entry.pack(pady=(4, 20), ipady=4)

    session = load_session()
    if session:
        phone_entry.insert(0, session.get("phone", ""))
        password_entry.insert(0, session.get("password", ""))

    def submit_login():
        phone = phone_entry.get().strip()
        password = password_entry.get()

        if not phone or not password:
            messagebox.showerror("Error", "Please enter phone number and password.")
            return

        try:
            res = api_login(phone, password)
            if res.status_code == 200:
                data = res.json()
                token = data.get("access_token", "")
                save_session({
                    "phone": phone,
                    "password": password,
                    "username": data.get("username", ""),
                    "access_token": token
                })
                client.token = token
                login_window.destroy()
                window.withdraw()
                open_dashboard()
            elif res.status_code == 401:
                messagebox.showerror("Login Failed", "Invalid credentials.")
            else:
                messagebox.showerror("Error", res.text)
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    btn = create_styled_button(card, "Login to Dashboard", submit_login, bg_color=ACCENT_TEAL, width=24, height=2)
    btn.pack(pady=10)


# -------------------------------------------------------------------
# 8. MAIN APPLICATION LAUNCHER
# -------------------------------------------------------------------
window = tk.Tk()
window.title("DocuMind AI")
window.geometry("600x450")
window.configure(bg=BG_DARK)

tk.Label(
    window,
    text="DocuMind AI",
    font=("DejaVu Sans", 28, "bold"),
    bg=BG_DARK,
    fg=TEXT_MAIN
).pack(pady=(80, 5))

tk.Label(
    window,
    text="Intelligent Corpus Assistant",
    font=("DejaVu Sans", 13),
    bg=BG_DARK,
    fg=TEXT_MUTED
).pack(pady=(0, 30))

create_styled_button(window, "Launch Application", login, bg_color=ACCENT_TEAL, width=22, height=2).pack()

window.mainloop()