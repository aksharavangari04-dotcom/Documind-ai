# 🧠 DocuMind AI

### Intelligent Corpus Web Assistant for Indic Document Processing & Search

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Deployment](https://img.shields.io/badge/Deployed%20on-Render-46E3B7.svg)](https://render.com/)
[![API](https://img.shields.io/badge/API-Indic%20Corpus%20v1-0284c7.svg)](#)

DocuMind AI is a full-stack, cloud-deployed web dashboard built with **Streamlit** and Python. It directly integrates with the **Indic Corpus Collections API** to allow real-time document search, structured multi-modal content inspection, audio playback/transcription, AI-assisted summaries, and file uploads within a polished, dual-theme UI.

---

## 📌 Features at a Glance

| Feature | Description | API / Service |
| :--- | :--- | :--- |
| 🔐 **Secure Authentication** | Phone & password login/registration with persistent session management. | `POST /api/v1/auth/login` |
| 🔍 **Corpus Search** | Fast query-based search across corpus documents with keyword matching. | `GET /api/v1/records/search` |
| 📂 **Category Explorer** | Dynamic category navigation and dataset browsing. | `GET /api/v1/categories/` |
| 📑 **Multi-Modal Inspection** | Unified record viewer handling text, cloud file URLs, and streaming audio playback. | `GET /api/v1/records/{id}` |
| 💡 **AI Document Summarizer** | Extracts executive summaries, key metadata metrics, and source context. | `POST /api/v1/summarize` |
| 📤 **Corpus File Ingestion** | Upload unstructured documents directly to the Indic Corpus platform. | `POST /api/v1/records/upload` |

---

## 🛠️ Tech Stack & Architecture

* **Frontend:** Streamlit, Custom Responsive CSS (Dual-Theme & Glassmorphism)
* **Backend Integration:** RESTful Indic Corpus Collections API (`requests`)
* **Session Management:** Secure token storage with local session persistence (`session.py`)
* **Deployment:** Cloud-hosted containerized web service on Render

---

## 🚀 Quick Start & Local Setup

### 1. Clone the Repository
```bash
git clone [https://code.swecha.org/akshara.vangari/akshara.vangari.git](https://code.swecha.org/akshara.vangari/akshara.vangari.git)
cd akshara.vangari/documind-ai/client
