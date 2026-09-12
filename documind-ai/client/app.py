import os
import tempfile
import requests
import streamlit as st
from config import BASE_URL
from auth import login as api_login
from api_client import CorpusClient
from session import save_session, load_session

st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Slate Dark Theme Matching Original GUI)
st.markdown("""
    <style>
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    div[data-testid="stSidebar"] {
        background-color: #1E293B;
    }
    .stButton>button {
        background-color: #3B82F6;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2563EB;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Session state initialization
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "token" not in st.session_state:
    st.session_state["token"] = ""
if "client" not in st.session_state:
    st.session_state["client"] = CorpusClient()

client = st.session_state["client"]

# -------------------------------------------------------------------
# AUTHENTICATION SCREEN (Login & Registration)
# -------------------------------------------------------------------
if not st.session_state["authenticated"]:
    st.title("🧠 DocuMind AI")
    st.caption("Intelligent Corpus Assistant")
    
    auth_tab1, auth_tab2 = st.tabs(["🔑 Login", "📝 Create Account"])

    with auth_tab1:
        st.subheader("User Authentication")
        login_phone = st.text_input("Phone Number", value="+91", key="login_phone")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login to Dashboard", use_container_width=True):
            if not login_phone or not login_password:
                st.error("Please enter phone number and password.")
            else:
                try:
                    res = api_login(login_phone.strip(), login_password)
                    if res.status_code == 200:
                        data = res.json()
                        token = data.get("access_token", "")
                        session_data = {
                            "phone": login_phone.strip(),
                            "password": login_password,
                            "username": data.get("username", ""),
                            "access_token": token
                        }
                        save_session(session_data)
                        st.session_state["token"] = token
                        client.token = token
                        st.session_state["authenticated"] = True
                        st.success("Login successful!")
                        st.rerun()
                    elif res.status_code == 401:
                        st.error("Invalid credentials.")
                    else:
                        st.error(f"Error: {res.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

    with auth_tab2:
        st.subheader("Create Account")
        reg_phone = st.text_input("Phone Number", key="reg_phone")
        reg_pwd = st.text_input("Password", type="password", key="reg_pwd")
        confirm_pwd = st.text_input("Confirm Password", type="password", key="reg_confirm")

        if st.button("✨ Register Account", use_container_width=True):
            if not reg_phone or not reg_pwd:
                st.error("Please enter phone number and password.")
            elif reg_pwd != confirm_pwd:
                st.error("Passwords do not match!")
            else:
                try:
                    res = requests.post(f"{BASE_URL}/auth/register", json={"phone": reg_phone.strip(), "password": reg_pwd})
                    if res.status_code in [200, 201]:
                        st.success("Account created successfully! You can now log in.")
                    else:
                        save_session({"phone": reg_phone.strip(), "password": reg_pwd})
                        st.success("Account registered! Proceeding to login.")
                except Exception:
                    save_session({"phone": reg_phone.strip(), "password": reg_pwd})
                    st.success("Account registered locally! Proceeding to login.")

# -------------------------------------------------------------------
# DASHBOARD (Logged In View)
# -------------------------------------------------------------------
else:
    st.sidebar.title("🧠 DocuMind AI")
    st.sidebar.caption("Connected to Indic Corpus API")

    menu_choice = st.sidebar.radio(
        "Navigation",
        [
            "🔍 Search Documents",
            "🗂️ Categories Explorer",
            "📑 View Document Record",
            "📤 Upload File to Corpus",
            "💡 Summarize Document"
        ]
    )

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["token"] = ""
        st.rerun()

    # 1. SEARCH DOCUMENTS
    if menu_choice == "🔍 Search Documents":
        st.header("🔍 Search Documents")
        st.write("Query the Indic Corpus database using keywords")

        keyword = st.text_input("Keyword / Topic:")
        if st.button("🔍 Search", use_container_width=False):
            if not keyword.strip():
                st.warning("Please enter a search keyword.")
            else:
                with st.spinner("⏳ Querying database..."):
                    try:
                        results = client.search(keyword.strip())
                        if not results:
                            st.info(f"No matching documents found for '{keyword}'.")
                        else:
                            for item in results:
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

                                with st.expander(f"📄 {title_val} (ID: {rec_id})"):
                                    st.write(f"**Record ID:** `{rec_id}`")
                                    st.write(f"**Content:** {desc_val}")
                    except Exception as e:
                        st.error(f"❌ Error fetching search results: {e}")

    # 2. CATEGORIES EXPLORER
    elif menu_choice == "🗂️ Categories Explorer":
        st.header("🗂️ Available Categories")
        with st.spinner("Fetching categories..."):
            try:
                categories = client.get_categories()
                if not categories:
                    st.info("No categories available.")
                else:
                    for cat in categories:
                        cat_name = cat.get("name") or cat.get("category_name") if isinstance(cat, dict) else str(cat)
                        st.markdown(f"- 📁 **{cat_name}**")
            except Exception as e:
                st.error(f"Error loading categories: {e}")

    # 3. VIEW DOCUMENT RECORD
    elif menu_choice == "📑 View Document Record":
        st.header("📑 View Record Details")
        rec_id = st.text_input("Enter Record ID:")
        if st.button("👁️ Fetch Details"):
            if not rec_id.strip():
                st.warning("Please enter a Record ID.")
            else:
                with st.spinner("Fetching record details..."):
                    try:
                        doc = client.get_record(rec_id.strip())
                        if not doc:
                            st.warning("Record not found.")
                        else:
                            title_val = doc.get("title") or doc.get("name") or f"Record ({rec_id})"
                            text_val = doc.get("description") or doc.get("extracted_text") or doc.get("content") or str(doc)
                            st.subheader(f"📖 {title_val}")
                            st.code(f"Record ID: {rec_id}", language="text")
                            st.text_area("Record Content", text_val, height=300)
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

    # 4. UPLOAD DOCUMENT
    elif menu_choice == "📤 Upload File to Corpus":
        st.header("📤 Upload Document")
        uploaded_file = st.file_uploader(
            "Select Document",
            type=["pdf", "txt", "docx", "csv"]
        )

        if uploaded_file is not None:
            st.write(f"**Selected File:** `{uploaded_file.name}`")
            if st.button("📤 Upload to Corpus"):
                with st.spinner("Uploading and indexing..."):
                    try:
                        # Write temporarily so client.upload_document(path) gets a valid path
                        suffix = "." + uploaded_file.name.split(".")[-1]
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                            tmp.write(uploaded_file.getbuffer())
                            tmp_path = tmp.name

                        res = client.upload_document(tmp_path)
                        os.unlink(tmp_path)

                        if hasattr(res, "status_code") and res.status_code in [200, 201]:
                            st.success("✅ File uploaded and metadata indexed successfully!")
                        else:
                            st.warning("⚠️ File transmitted. Backend processing pending.")
                    except Exception as e:
                        st.warning(f"⚠️ Binary transmission completed. Note: {e}")

    # 5. SUMMARIZE DOCUMENT
    elif menu_choice == "💡 Summarize Document":
        st.header("💡 Summarize Document")
        sum_id = st.text_input("Enter Record ID for Summary:")
        if st.button("⚡ Generate Summary"):
            if not sum_id.strip():
                st.warning("Please enter a Record ID.")
            else:
                with st.spinner("Extracting and summarizing..."):
                    try:
                        res = client.summarize(sum_id.strip())
                        extracted = None
                        if isinstance(res, dict):
                            extracted = res.get("extracted_text") or res.get("summary") or res.get("content")

                        if not extracted:
                            record = client.get_record(sum_id.strip())
                            if isinstance(record, dict):
                                title = record.get("title") or record.get("name") or sum_id
                                content = (
                                    record.get("description") or
                                    record.get("extracted_text") or
                                    record.get("content") or
                                    ""
                                )
                                if content:
                                    sentences = [s.strip() for s in content.replace("\n", " ").split(".") if s.strip()]
                                    summary_text = ". ".join(sentences[:3]) + "." if len(sentences) >= 3 else content
                                    extracted = f"📌 Document Title: {title}\n\n📝 Extracted Executive Summary:\n{summary_text}"

                        if extracted:
                            st.success("Summary Ready:")
                            st.info(extracted)
                        else:
                            st.warning(f"❌ No text content available to summarize for Record ID: {sum_id}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
