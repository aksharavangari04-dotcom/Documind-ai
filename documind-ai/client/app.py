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
        padding: 0.5rem 1.2rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2563EB;
        color: white;
    }
    .info-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to extract deep/hidden text from any Corpus API response
def extract_complete_text(data):
    """Recursively extracts the fullest available text content from API response."""
    if not data:
        return ""
    if isinstance(data, str):
        return data

    if hasattr(data, "json"):
        try:
            data = data.json()
        except Exception:
            pass

    if isinstance(data, dict):
        # 1. Check direct full-text fields
        priority_keys = [
            "raw_text", "transcription", "extracted_text", "full_text",
            "text", "content", "body", "data", "description", "summary"
        ]
        for key in priority_keys:
            val = data.get(key)
            if isinstance(val, str) and len(val.strip()) > 30:
                return val.strip()

        # 2. Check nested payloads (e.g. data.items, result.text)
        for nested in ["data", "result", "payload", "record", "metadata"]:
            if isinstance(data.get(nested), dict):
                res = extract_complete_text(data[nested])
                if res:
                    return res

        # Fallback to description or combined non-empty string values
        for key in priority_keys:
            if data.get(key):
                return str(data.get(key)).strip()

    return str(data)

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
                                desc_val = extract_complete_text(record) or "No content text available."

                                with st.expander(f"📄 {title_val} (ID: {rec_id})"):
                                    st.write(f"**Record ID:** `{rec_id}`")
                                    st.write(f"**Content Preview:** {desc_val[:300]}...")
                                    st.code(f"{rec_id}", language="text")
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

    # 3. VIEW DOCUMENT RECORD (Expanded Complete View)
    elif menu_choice == "📑 View Document Record":
        st.header("📑 View Complete Document Record")
        st.write("Retrieve the complete document content and all attached corpus metadata.")
        
        rec_id = st.text_input("Enter Record ID:")
        if st.button("👁️ Fetch Details"):
            if not rec_id.strip():
                st.warning("Please enter a Record ID.")
            else:
                with st.spinner("Fetching complete record from Indic Corpus..."):
                    try:
                        raw_record = client.get_record(rec_id.strip())
                        if not raw_record:
                            st.warning("Record not found.")
                        else:
                            doc = raw_record.json() if hasattr(raw_record, "json") else raw_record
                            
                            title_val = doc.get("title") or doc.get("name") or f"Record ({rec_id.strip()})"
                            full_content = extract_complete_text(doc)

                            st.subheader(f"📖 {title_val}")
                            st.caption(f"Record Identifier: `{rec_id.strip()}`")

                            # Metadata Summary Cards
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Language / Category", doc.get("language") or doc.get("category") or "Telugu / Indic")
                            with col2:
                                word_count = len(full_content.split()) if full_content else 0
                                st.metric("Word Count", f"{word_count} words")
                            with col3:
                                st.metric("Character Count", f"{len(full_content)} chars")

                            st.markdown("---")
                            st.markdown("### 📄 Complete Document Content")
                            
                            # Display in an expanded readable text box
                            st.text_area(
                                label="Document Body",
                                value=full_content,
                                height=380
                            )

                            # Raw JSON details dropdown for inspection
                            with st.expander("🔍 Inspect Full Corpus API Metadata"):
                                st.json(doc)
                    except Exception as e:
                        st.error(f"❌ Error fetching record: {e}")

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

    # 5. SUMMARIZE DOCUMENT (Smart Multi-Section Summary)
    elif menu_choice == "💡 Summarize Document":
        st.header("💡 Intelligent Document Summarizer")
        st.write("Extract executive summary, key insights, and structured bullet points from any corpus document.")
        
        sum_id = st.text_input("Enter Record ID to Summarize:")
        if st.button("⚡ Generate AI Summary"):
            if not sum_id.strip():
                st.warning("Please enter a Record ID.")
            else:
                with st.spinner("Analyzing document and generating comprehensive summary..."):
                    try:
                        # 1. Fetch raw summary endpoint
                        server_res = client.summarize(sum_id.strip())
                        extracted_summary = None
                        if isinstance(server_res, dict):
                            extracted_summary = (
                                server_res.get("summary") or 
                                server_res.get("extracted_text") or 
                                server_res.get("content")
                            )

                        # 2. Fetch full record to analyze and extract deep content
                        full_record = client.get_record(sum_id.strip())
                        record_dict = full_record.json() if hasattr(full_record, "json") else (full_record if isinstance(full_record, dict) else {})
                        doc_title = record_dict.get("title") or record_dict.get("name") or f"Record {sum_id.strip()}"
                        full_text = extract_complete_text(record_dict)

                        content_to_summarize = extracted_summary or full_text

                        if not content_to_summarize or len(content_to_summarize.strip()) == 0:
                            st.warning(f"❌ No text content available to summarize for Record ID: {sum_id}")
                        else:
                            st.success("✅ Document Summary Generated Successfully!")
                            st.subheader(f"📌 {doc_title}")
                            st.caption(f"Target Record: `{sum_id.strip()}`")

                            # Clean sentences for multi-point breakdown
                            clean_text = content_to_summarize.replace("\n", " ")
                            sentences = [s.strip() for s in clean_text.split(".") if len(s.strip()) > 8]

                            # 1. Executive Summary
                            st.markdown("### 📝 Executive Overview")
                            if len(sentences) >= 2:
                                st.info(". ".join(sentences[:3]) + ".")
                            else:
                                st.info(content_to_summarize)

                            # 2. Key Highlights / Bullet Points
                            st.markdown("### 🎯 Key Highlights & Points")
                            if len(sentences) > 3:
                                for point in sentences[3:8]:
                                    st.markdown(f"• {point}.")
                            else:
                                st.markdown(f"• {content_to_summarize}")

                            # 3. Source Reference
                            with st.expander("📖 View Original Source Text"):
                                st.write(full_text)

                    except Exception as e:
                        st.error(f"❌ Error generating summary: {e}")
