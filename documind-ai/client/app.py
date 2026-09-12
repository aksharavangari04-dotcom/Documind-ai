import streamlit as st
import api_client

st.set_page_config(page_title="DocuMind AI", page_icon="📄", layout="centered")

st.title("📄 DocuMind AI – Intelligent Corpus Assistant")
st.caption("Interact with documents, search, and view content live.")

st.divider()

# Main Interface: View / Summarize
st.subheader("Document Operations")

doc_id = st.text_input("Enter Document ID:", placeholder="e.g., 1")

col1, col2 = st.columns(2)

with col1:
    if st.button("View Document", use_container_width=True):
        if doc_id:
            try:
                doc = api_client.get_document(doc_id)
                st.text_area("Document Content", doc.get("content", str(doc)), height=300)
            except Exception as e:
                st.error(f"Error fetching document: {e}")
        else:
            st.warning("Please enter a valid Document ID.")

with col2:
    if st.button("Summarize Document", use_container_width=True):
        if doc_id:
            try:
                summary = api_client.summarize_document(doc_id)
                st.text_area("Summary", summary.get("summary", str(summary)), height=300)
            except Exception as e:
                st.error(f"Error summarizing document: {e}")
        else:
            st.warning("Please enter a valid Document ID.")