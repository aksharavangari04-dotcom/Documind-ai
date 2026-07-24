<div align="center">

  <h1>🧠 DocuMind AI</h1>
  <p><strong>Intelligent Corpus Assistant for Indic Document Processing & Search</strong></p>

  [![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Tkinter](https://img.shields.io/badge/GUI-Tkinter-FF6F00?style=for-the-badge)](https://docs.python.org/3/library/tkinter.html)
  [![uv](https://img.shields.io/badge/Package_Manager-uv-DE5D83?style=for-the-badge)](https://github.com/astral-sh/uv)
  [![API](https://img.shields.io/badge/API-Indic_Corpus_v1-008080?style=for-the-badge)](https://github.com/)

  <br />

  <p align="center">
    A sleek, dark-themed desktop assistant that interacts directly with the <strong>Indic Corpus Collections API</strong> to offer real-time document search, record retrieval, categorization, summarization, and direct file ingestion.
  </p>

</div>

---

## ✨ Features At A Glance

| Feature | Description | API Endpoint |
| :--- | :--- | :--- |
| **🔐 Secure Auth** | Access token generation & auto-load via persistent session | `POST /api/v1/auth/login` |
| **🔍 Real-Time Search** | Query document corpuses by keyword with live rendering | `GET /api/v1/records/search` |
| **📄 Record Inspection** | Fetch detailed text content, ASR output, and metadata | `GET /api/v1/records/{id}` |
| **📂 Category Browser** | Dynamically list all available dataset categories | `GET /api/v1/categories/` |
| **📁 Direct File Upload** | Local file picker for uploading documents (`.pdf`, `.txt`, `.docx`) | `POST /api/v1/records/upload` |
| **📝 Text Summarization** | Fetch raw extracted text and automated summaries for records | `GET /api/v1/records/{id}/extracted_text` |
| **🎨 Modern UI** | Custom dark mode palette (`#0F172A`) built with Tkinter | Client Native |

---

## 🛠️ Tech Stack & Architecture

* **UI Framework:** Python `tkinter`
* **HTTP & API Integration:** `requests`
* **Session Persistence Engine:** Local JSON storage (`session.py`)
* **Environment & Package Management:** [`uv`](https://github.com/astral-sh/uv)
* **Backend:** Indic Corpus Collections API (`/api/v1`)

---

## 💻 Quick Start & Installation

### 1. Clone Repository
```bash
git clone [https://github.com/your-username/documind-ai.git](https://github.com/your-username/documind-ai.git)
cd documind-ai