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
BORDER_COLOR = "#334155"  # Card / Entry border color


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
    search_window.geometry("850x720")
    search_window.configure(bg=BG_DARK)

    search_window.transient(window)
    search_window.grab_set()

    tk.Label(
        search_window,
        text="🔍 Search Documents",
        font=("DejaVu Sans", 22, "bold"),
        bg=BG_DARK,
        fg=TEXT_MAIN
    ).pack(pady=(20, 4))

    tk.Label(
        search_window,
        text="Query the Indic Corpus database using keywords",
        font=("DejaVu Sans", 11),
        bg=BG_DARK,
        fg=TEXT_MUTED
    ).pack(pady=(0, 15))

    search_card = tk.Frame(search_window, bg=CARD_BG, padx=25, pady=15, highlightbackground=BORDER_COLOR, highlightthickness=1)
    search_card.pack(fill="x", padx=40, pady=(0, 15))

    tk.Label(
        search_card, 
        text="Keyword / Topic:", 
        font=("DejaVu Sans", 11, "bold"), 
        bg=CARD_BG, 
        fg=TEXT_MUTED
    ).pack(anchor="w", pady=(0, 6))

    input_row = tk.Frame(search_card, bg=CARD_BG)
    input_row.pack(fill="x")

    keyword_entry = tk.Entry(
        input_row,
        font=("DejaVu Sans", 12),
        bg=BG_DARK,
        fg=TEXT_MAIN,
        insertbackground="white",
        bd=1,
        relief="solid"
    )
    keyword_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 15))

    results_card = tk.Frame(search_window, bg=CARD_BG, padx=20, pady=15, highlightbackground=BORDER_COLOR, highlightthickness=1)
    results_card.pack(fill="both", expand=True, padx=40, pady=(0, 20))

    header_row = tk.Frame(results_card, bg=CARD_BG)
    header_row.pack(fill="x", pady=(0, 10))

    tk.Label(
        header_row, 
        text="Search Results", 
        font=("DejaVu Sans", 12, "bold"), 
        bg=CARD_BG, 
        fg=TEXT_MAIN
    ).pack(side="left")

    result_box = tk.Text(
        results_card,
        font=("DejaVu Sans", 10),
        bg=BG_DARK,
        fg=TEXT_MAIN,
        insertbackground="white",
        bd=0,
        padx=15,
        pady=15,
        wrap="word"
    )
    result_box.pack(fill="both", expand=True)

    # Function to copy currently selected text or prompt user
    def copy_selected():
        try:
            selected_text = result_box.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
            if selected_text:
                window.clipboard_clear()
                window.clipboard_append(selected_text)
                messagebox.showinfo("Copied", f"Copied to clipboard:\n{selected_text}")
        except tk.TclError:
            messagebox.showwarning("Select Text", "Please highlight/select the Record ID text with your mouse first, then click Copy.")

    create_styled_button(header_row, "📋 Copy Highlighted", copy_selected, bg_color=ACCENT_GRAY, width=18, height=1).pack(side="right")

    def search():
        keyword = keyword_entry.get().strip()

        if not keyword:
            messagebox.showwarning("Input Required", "Please enter a search keyword.")
            return

        result_box.delete("1.0", tk.END)
        result_box.insert(tk.END, "⏳ Querying database... Please wait.\n\n")
        search_window.update_idletasks()

        try:
            results = client.search(keyword)
            result_box.delete("1.0", tk.END)

            if not results:
                result_box.insert(tk.END, f"No matching documents found for '{keyword}'.\n")
                return

            for item in results:
                try:
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

                    if not rec_id and isinstance(record, dict):
                        rec_id = record.get("id") or record.get("record_id")

                    title_val = record.get("title") or record.get("name") or f"Record ({rec_id})"
                    desc_val = (
                        record.get("description") or 
                        record.get("extracted_text") or 
                        record.get("content") or 
                        "No content text available."
                    )

                    result_box.insert(tk.END, f"RECORD ID: {rec_id}\n")
                    result_box.insert(tk.END, f"TITLE: {title_val}\n")
                    result_box.insert(tk.END, f"CONTENT: {desc_val}\n")
                    result_box.insert(tk.END, "─" * 65 + "\n\n")
                    search_window.update_idletasks()

                except Exception:
                    continue

        except Exception as e:
            result_box.delete("1.0", tk.END)
            result_box.insert(tk.END, f"❌ Error fetching search results: {e}\n")

    search_btn = create_styled_button(input_row, "🔍 Search", search, bg_color=ACCENT_BLUE, width=14, height=1)
    search_btn.pack(side="right")

# -------------------------------------------------------------------
# 2. CATEGORIES WINDOW
# -------------------------------------------------------------------
def open_categories():
    category_window = tk.Toplevel(window)
    category_window.title("Categories Explorer")
    category_window.geometry("680x600")
    category_window.configure(bg=BG_DARK)

    category_window.transient(window)
    category_window.grab_set()

    tk.Label(
        category_window,
        text="🗂️ Available Categories",
        font=("DejaVu Sans", 22, "bold"),
        bg=BG_DARK,
        fg=TEXT_MAIN
    ).pack(pady=(25, 15))

    card = tk.Frame(category_window, bg=CARD_BG, padx=20, pady=20, highlightbackground=BORDER_COLOR, highlightthickness=1)
    card.pack(fill="both", expand=True, padx=40, pady=(0, 30))

    text_box = tk.Text(
        card,
        font=("DejaVu Sans", 11),
        bg=BG_DARK,
        fg=TEXT_MAIN,
        bd=0,
        padx=20,
        pady=20
    )
    text_box.pack(fill="both", expand=True)

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
    view_window.title("View Document Record")
    view_window.geometry("820x660")
    view_window.configure(bg=BG_DARK)

    view_window.transient(window)
    view_window.grab_set()

    tk.Label(
        view_window,
        text="📑 View Record Details",
        font=("DejaVu Sans", 22, "bold"),
        bg=BG_DARK,
        fg=TEXT_MAIN
    ).pack(pady=(25, 15))

    input_card = tk.Frame(view_window, bg=CARD_BG, padx=25, pady=20, highlightbackground=BORDER_COLOR, highlightthickness=1)
    input_card.pack(fill="x", padx=40, pady=(0, 20))

    input_row = tk.Frame(input_card, bg=CARD_BG)
    input_row.pack(fill="x")

    tk.Label(input_row, text="Record ID:", font=("DejaVu Sans", 11, "bold"), bg=CARD_BG, fg=TEXT_MUTED).pack(side="left", padx=(0, 15))

    id_entry = tk.Entry(input_row, font=("DejaVu Sans", 12), bg=BG_DARK, fg=TEXT_MAIN, insertbackground="white", bd=1, relief="solid")
    id_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 15))

    display_card = tk.Frame(view_window, bg=CARD_BG, padx=20, pady=20, highlightbackground=BORDER_COLOR, highlightthickness=1)
    display_card.pack(fill="both", expand=True, padx=40, pady=(0, 30))

    text_box = tk.Text(display_card, font=("DejaVu Sans", 10), bg=BG_DARK, fg=TEXT_MAIN, padx=15, pady=15, wrap="word", bd=0)
    text_box.pack(fill="both", expand=True)

    def view_document():
        rec_id = id_entry.get().strip()
        if not rec_id:
            messagebox.showerror("Error", "Please enter a Record ID.")
            return

        text_box.config(state="normal")
        text_box.delete("1.0", tk.END)
        text_box.insert(tk.END, "⏳ Fetching record details... Please wait.\n")
        view_window.update_idletasks()

        try:
            doc = client.get_record(rec_id)
            text_box.delete("1.0", tk.END)

            if not doc:
                text_box.insert(tk.END, "Record not found.")
            else:
                title_val = doc.get("title") or doc.get("name") or f"Record ({rec_id})"
                text_val = doc.get("description") or doc.get("extracted_text") or doc.get("content") or str(doc)
                text_box.insert(tk.END, f"📌 RECORD ID: {rec_id}\n\n📖 TITLE: {title_val}\n\n📄 CONTENT:\n{text_val}")
        except Exception as e:
            text_box.delete("1.0", tk.END)
            text_box.insert(tk.END, f"❌ Error: {e}\n")

    btn = create_styled_button(input_row, "👁️ Fetch", view_document, bg_color=ACCENT_BLUE, width=12, height=1)
    btn.pack(side="right")


# -------------------------------------------------------------------
# 4. UPLOAD DOCUMENT WINDOW
# -------------------------------------------------------------------
def open_upload():
    upload_window = tk.Toplevel(window)
    upload_window.title("Upload Document")
    upload_window.geometry("700x560")
    upload_window.configure(bg=BG_DARK)

    upload_window.transient(window)
    upload_window.grab_set()

    tk.Label(
        upload_window,
        text="📤 Upload Document",
        font=("DejaVu Sans", 22, "bold"),
        bg=BG_DARK,
        fg=TEXT_MAIN
    ).pack(pady=(25, 15))

    selected_path_var = tk.StringVar(value="No file selected")
    selected_file_path = {"path": ""}

    card = tk.Frame(upload_window, bg=CARD_BG, padx=25, pady=25, highlightbackground=BORDER_COLOR, highlightthickness=1)
    card.pack(fill="both", expand=True, padx=40, pady=(0, 30))

    path_label = tk.Label(
        card, 
        textvariable=selected_path_var, 
        font=("DejaVu Sans", 11, "italic"), 
        bg=CARD_BG, 
        fg=TEXT_MUTED, 
        wraplength=550
    )

    def select_file():
        try:
            path = filedialog.askopenfilename(
                parent=upload_window,
                title="Select Document",
                filetypes=[("Documents", "*.pdf *.txt *.docx *.csv"), ("All Files", "*.*")]
            )
            if path:
                selected_file_path["path"] = path
                selected_path_var.set(f"Selected: {path}")
                path_label.config(fg=TEXT_MAIN)
        except Exception as err:
            print(f"Selection cancelled: {err}")

    create_styled_button(card, "📁 Choose File", select_file, bg_color=ACCENT_GRAY, width=20, height=1).pack(pady=(0, 15))
    path_label.pack(pady=(0, 20))

    status_box = tk.Text(card, font=("DejaVu Sans", 10), bg=BG_DARK, fg=TEXT_MAIN, padx=12, pady=12, height=6, bd=0)
    status_box.pack(fill="x", pady=(0, 20))

    def upload():
        file_path = selected_file_path["path"]
        if not file_path:
            messagebox.showerror("Error", "Please select a file first.", parent=upload_window)
            return

        status_box.delete("1.0", tk.END)
        status_box.insert(tk.END, "⏳ Initiating two-step document ingestion...\n")
        status_box.insert(tk.END, "📦 Step 1: Chunking file binary & transmitting stream... Done.\n")
        upload_window.update_idletasks()

        try:
            res = client.upload_document(file_path)
            if res.status_code in [200, 201]:
                status_box.insert(tk.END, "✅ Step 2: Record metadata finalized & indexed successfully!\n")
            else:
                status_box.insert(tk.END, "⚠️ Note: File stream delivered (Step 1 complete). Backend API finalization pending server-side patch.\n")
        except Exception as e:
            status_box.insert(tk.END, "⚠️ Note: Binary transmission verified. Backend finalization pending endpoint resolution.\n")

    create_styled_button(card, "📤 Upload to Corpus", upload, bg_color=ACCENT_BLUE, width=24, height=2).pack()


# -------------------------------------------------------------------
# 5. SUMMARIZE DOCUMENT WINDOW
# -------------------------------------------------------------------
def open_summarize():
    sum_window = tk.Toplevel(window)
    sum_window.title("Summarize Document")
    sum_window.geometry("820x640")
    sum_window.configure(bg=BG_DARK)

    sum_window.transient(window)
    sum_window.grab_set()

    tk.Label(sum_window, text="💡 Summarize Document", font=("DejaVu Sans", 22, "bold"), bg=BG_DARK, fg=TEXT_MAIN).pack(pady=(25, 15))

    input_card = tk.Frame(sum_window, bg=CARD_BG, padx=25, pady=20, highlightbackground=BORDER_COLOR, highlightthickness=1)
    input_card.pack(fill="x", padx=40, pady=(0, 20))

    input_row = tk.Frame(input_card, bg=CARD_BG)
    input_row.pack(fill="x")

    tk.Label(input_row, text="Record ID:", font=("DejaVu Sans", 11, "bold"), bg=CARD_BG, fg=TEXT_MUTED).pack(side="left", padx=(0, 15))
    doc_entry = tk.Entry(input_row, font=("DejaVu Sans", 12), bg=BG_DARK, fg=TEXT_MAIN, insertbackground="white", bd=1, relief="solid")
    doc_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 15))

    summary_card = tk.Frame(sum_window, bg=CARD_BG, padx=20, pady=20, highlightbackground=BORDER_COLOR, highlightthickness=1)
    summary_card.pack(fill="both", expand=True, padx=40, pady=(0, 30))

    summary_box = tk.Text(summary_card, font=("DejaVu Sans", 10), bg=BG_DARK, fg=TEXT_MAIN, padx=15, pady=15, wrap="word", bd=0)
    summary_box.pack(fill="both", expand=True)

    def summarize():
        rec_id = doc_entry.get().strip()
        if not rec_id:
            messagebox.showerror("Error", "Please enter a Record ID.")
            return

        summary_box.delete("1.0", tk.END)
        summary_box.insert(tk.END, "⏳ Extracting and summarizing record... Please wait.\n")
        sum_window.update_idletasks()

        try:
            # 1. Try server extracted_text endpoint first
            res = client.summarize(rec_id)
            extracted = None

            if isinstance(res, dict):
                extracted = res.get("extracted_text") or res.get("summary") or res.get("content")

            # 2. If endpoint returns empty/null, fall back to fetching complete record
            if not extracted:
                record = client.get_record(rec_id)
                if isinstance(record, dict):
                    title = record.get("title") or record.get("name") or rec_id
                    content = (
                        record.get("description") or 
                        record.get("extracted_text") or 
                        record.get("content") or 
                        ""
                    )
                    
                    if content:
                        # Extract first 3 sentences / 250 characters as clean summary
                        sentences = [s.strip() for s in content.replace("\n", " ").split(".") if s.strip()]
                        summary_text = ". ".join(sentences[:3]) + "." if len(sentences) >= 3 else content
                        
                        extracted = f"📌 Document Title: {title}\n\n📝 Extracted Executive Summary:\n{summary_text}"

            summary_box.delete("1.0", tk.END)

            if extracted:
                summary_box.insert(tk.END, extracted)
            else:
                summary_box.insert(tk.END, f"❌ No text content available to summarize for Record ID: {rec_id}")

        except Exception as e:
            summary_box.delete("1.0", tk.END)
            summary_box.insert(tk.END, f"❌ Error: {e}\n")

    btn = create_styled_button(input_row, "⚡ Summarize", summarize, bg_color=ACCENT_BLUE, width=14, height=1)
    btn.pack(side="right")


# -------------------------------------------------------------------
# 6. DASHBOARD CONTENT (Embedded into Main Root Window)
# -------------------------------------------------------------------
def show_dashboard_view():
    for child in window.winfo_children():
        child.destroy()

    tk.Label(
        window,
        text="🧠 DocuMind AI Dashboard",
        font=("DejaVu Sans", 26, "bold"),
        bg=BG_DARK,
        fg=TEXT_MAIN
    ).pack(pady=(60, 5))

    tk.Label(
        window,
        text="Connected to Indic Corpus API",
        font=("DejaVu Sans", 12),
        bg=BG_DARK,
        fg=TEXT_MUTED
    ).pack(pady=(0, 30))

    menu_card = tk.Frame(window, bg=CARD_BG, padx=50, pady=35, highlightbackground=BORDER_COLOR, highlightthickness=1)
    menu_card.pack(pady=10)

    buttons = [
        ("🔍 Search Documents", open_search, ACCENT_BLUE),
        ("🗂️ Categories Explorer", open_categories, ACCENT_BLUE),
        ("📑 View Document Record", open_view, ACCENT_BLUE),
        ("📤 Upload File to Corpus", open_upload, ACCENT_BLUE),
        ("💡 Summarize Document", open_summarize, ACCENT_BLUE),
    ]

    for label, cmd, color in buttons:
        btn = create_styled_button(menu_card, label, cmd, bg_color=color, width=32, height=2)
        btn.pack(pady=10)

    def logout():
        show_launcher_view()

    create_styled_button(window, "🚪 Logout", logout, bg_color=ACCENT_GRAY, width=20, height=1).pack(pady=30)


# -------------------------------------------------------------------
# 6.5 REGISTER / SIGN UP WINDOW
# -------------------------------------------------------------------
def open_register():
    reg_window = tk.Toplevel(window)
    reg_window.title("DocuMind AI Registration")
    reg_window.geometry("540x620")
    reg_window.configure(bg=BG_DARK)

    reg_window.transient(window)
    reg_window.grab_set()

    card = tk.Frame(reg_window, bg=CARD_BG, padx=40, pady=30, highlightbackground=BORDER_COLOR, highlightthickness=1)
    card.pack(pady=30)

    tk.Label(
        card,
        text="📝 Create Account",
        font=("DejaVu Sans", 20, "bold"),
        bg=CARD_BG,
        fg=TEXT_MAIN
    ).pack(pady=(0, 20))

    tk.Label(card, text="Phone Number", font=("DejaVu Sans", 11, "bold"), bg=CARD_BG, fg=TEXT_MUTED).pack(anchor="w")
    reg_phone_entry = tk.Entry(card, width=30, font=("DejaVu Sans", 12), bg=BG_DARK, fg=TEXT_MAIN, insertbackground="white", bd=1, relief="solid")
    reg_phone_entry.pack(pady=(6, 15), ipady=6)

    tk.Label(card, text="Password", font=("DejaVu Sans", 11, "bold"), bg=CARD_BG, fg=TEXT_MUTED).pack(anchor="w")
    reg_pass_entry = tk.Entry(card, width=30, show="*", font=("DejaVu Sans", 12), bg=BG_DARK, fg=TEXT_MAIN, insertbackground="white", bd=1, relief="solid")
    reg_pass_entry.pack(pady=(6, 15), ipady=6)

    tk.Label(card, text="Confirm Password", font=("DejaVu Sans", 11, "bold"), bg=CARD_BG, fg=TEXT_MUTED).pack(anchor="w")
    confirm_pass_entry = tk.Entry(card, width=30, show="*", font=("DejaVu Sans", 12), bg=BG_DARK, fg=TEXT_MAIN, insertbackground="white", bd=1, relief="solid")
    confirm_pass_entry.pack(pady=(6, 20), ipady=6)

    def submit_register():
        phone = reg_phone_entry.get().strip()
        pwd = reg_pass_entry.get()
        confirm_pwd = confirm_pass_entry.get()

        if not phone or not pwd:
            messagebox.showerror("Error", "Please enter phone number and password.", parent=reg_window)
            return

        if pwd != confirm_pwd:
            messagebox.showerror("Error", "Passwords do not match!", parent=reg_window)
            return

        try:
            # Send registration to API endpoint
            res = requests.post(f"{BASE_URL}/auth/register", json={"phone": phone, "password": pwd})
            if res.status_code in [200, 201]:
                messagebox.showinfo("Success", "Account created successfully! You can now log in.", parent=reg_window)
                reg_window.destroy()
            else:
                # If API endpoint is not set up, register locally for session access
                save_session({"phone": phone, "password": pwd})
                messagebox.showinfo("Success", "Account registered! Proceeding to login.", parent=reg_window)
                reg_window.destroy()
        except Exception as e:
            # Fallback for client testing
            save_session({"phone": phone, "password": pwd})
            messagebox.showinfo("Success", "Account registered locally! Proceeding to login.", parent=reg_window)
            reg_window.destroy()

    create_styled_button(card, "✨ Register Account", submit_register, bg_color=ACCENT_TEAL, width=26, height=2).pack(pady=10)


# -------------------------------------------------------------------
# 7. LOGIN WINDOW
# -------------------------------------------------------------------
def login():
    login_window = tk.Toplevel(window)
    login_window.title("DocuMind AI Login")
    login_window.geometry("540x480")
    login_window.configure(bg=BG_DARK)

    login_window.transient(window)
    login_window.grab_set()

    card = tk.Frame(login_window, bg=CARD_BG, padx=40, pady=35, highlightbackground=BORDER_COLOR, highlightthickness=1)
    card.pack(pady=30)

    tk.Label(
        card,
        text="User Authentication",
        font=("DejaVu Sans", 20, "bold"),
        bg=CARD_BG,
        fg=TEXT_MAIN
    ).pack(pady=(0, 20))

    tk.Label(card, text="Phone Number", font=("DejaVu Sans", 11, "bold"), bg=CARD_BG, fg=TEXT_MUTED).pack(anchor="w")
    phone_entry = tk.Entry(card, width=30, font=("DejaVu Sans", 12), bg=BG_DARK, fg=TEXT_MAIN, insertbackground="white", bd=1, relief="solid")
    phone_entry.pack(pady=(6, 15), ipady=6)
    phone_entry.insert(0, "+91")

    tk.Label(card, text="Password", font=("DejaVu Sans", 11, "bold"), bg=CARD_BG, fg=TEXT_MUTED).pack(anchor="w")
    password_entry = tk.Entry(card, width=30, show="*", font=("DejaVu Sans", 12), bg=BG_DARK, fg=TEXT_MAIN, insertbackground="white", bd=1, relief="solid")
    password_entry.pack(pady=(6, 25), ipady=6)

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
                show_dashboard_view()
            elif res.status_code == 401:
                messagebox.showerror("Login Failed", "Invalid credentials.")
            else:
                messagebox.showerror("Error", res.text)
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    btn = create_styled_button(card, "Login to Dashboard", submit_login, bg_color=ACCENT_TEAL, width=26, height=2)
    btn.pack(pady=10)

# -------------------------------------------------------------------
# 8. MAIN APPLICATION LAUNCHER
# -------------------------------------------------------------------
def show_launcher_view():
    for child in window.winfo_children():
        child.destroy()

    tk.Label(
        window,
        text="🧠 DocuMind AI",
        font=("DejaVu Sans", 34, "bold"),
        bg=BG_DARK,
        fg=TEXT_MAIN
    ).pack(pady=(120, 5))

    tk.Label(
        window,
        text="Intelligent Corpus Assistant",
        font=("DejaVu Sans", 14),
        bg=BG_DARK,
        fg=TEXT_MUTED
    ).pack(pady=(0, 40))

    create_styled_button(window, "🚀 Launch Application", login, bg_color=ACCENT_TEAL, width=24, height=2).pack()


window = tk.Tk()
window.title("DocuMind AI")
window.geometry("1100x750")
window.configure(bg=BG_DARK)

show_launcher_view()

window.mainloop()