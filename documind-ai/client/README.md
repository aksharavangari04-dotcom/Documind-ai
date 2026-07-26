<div align="center">

  <h1>🧠 DocuMind AI</h1>
  <p><strong>Intelligent Corpus Assistant for Indic Document Processing & Search</strong></p>

  [![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
  [![Tkinter](https://img.shields.io/badge/GUI-Tkinter-FF6F00?style=for-the-badge)](https://docs.python.org/3/library/tkinter.html)
  [![uv](https://img.shields.io/badge/Package_Manager-uv-DE5D83?style=for-the-badge)](https://github.com/astral-sh/uv)
  [![API](https://img.shields.io/badge/API-Indic_Corpus_v1-008080?style=for-the-badge)](https://code.swecha.org/)

  <br />

  <p align="center">
    A desktop assistant built with Python and Tkinter that interacts directly with the <strong>Indic Corpus Collections API</strong>. <br />
    Effortlessly search, inspect, summarize, and ingest unstructured documents through a fast dark-themed interface.
  </p>

</div>

---

## 📌 About The Project

**DocuMind AI** simplifies working with large document repositories by providing a desktop dashboard for text search, AI-assisted summarization, document ingestion, and dynamic dataset category exploration. It enforces secure token-based user authentication with local session persistence so you stay logged in seamlessly.

---

## ✨ Features At A Glance

| Feature | Description | API Endpoint |
| :--- | :--- | :--- |
| **🔐 Secure Auth** | Access token generation & local session persistence (`session.json`) | `POST /api/v1/auth/login` |
| **🔍 Real-Time Search** | Query document corpus by keyword with quick-copy capabilities | `GET /api/v1/records/search` |
| **📄 Record Inspection** | Fetch detailed text content, ASR output, and record metadata | `GET /api/v1/records/{id}` |
| **📂 Category Browser** | Dynamically browse available corpus categories | `GET /api/v1/categories/` |
| **📤 File Ingestion** | Upload local text documents with live chunk-streaming logs | `POST /api/v1/records/upload` |
| **📝 Smart Summarizer** | Generate executive summaries and text extractions on demand | `GET /api/v1/records/{id}/extracted_text` |
| **🎨 Dark Slate UI** | Modern dark-mode interface built natively in Python Tkinter | Desktop Native |

---

## 🛠️ Tech Stack & Architecture

* **Frontend:** Python (`tkinter`, `tkinter.ttk`)
* **HTTP Client:** `requests`
* **Session Persistence:** Local JSON session storage (`session.py`)
* **Package Manager:** [`uv`](https://github.com/astral-sh/uv)
* **Backend API:** Indic Corpus Collections API (`/api/v1`)

---

## 💻 Quick Start & Installation

### 1. Clone Repository
```bash
git clone [https://code.swecha.org/akshara.vangari/akshara.vangari.git](https://code.swecha.org/akshara.vangari/akshara.vangari.git)
cd akshara.vangari/documind-ai/client