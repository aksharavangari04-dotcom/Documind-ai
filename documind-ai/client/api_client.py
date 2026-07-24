import os
import uuid
import json
import requests
from config import BASE_URL
from session import load_session, save_session


class CorpusClient:
    def __init__(self, token=None):
        self.token = token

    def _get_headers(self):
        token = self.token
        if not token:
            session = load_session()
            if session and "access_token" in session:
                token = session["access_token"]
        
        if not token:
            raise Exception("Please log in first.")
            
        return {"Authorization": f"Bearer {token}"}

    def login(self, phone, password):
        """Logs in user and persists session with access_token and user_id."""
        url = f"{BASE_URL}/api/v1/auth/login"
        payload = {
            "phone": phone,
            "password": password
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            user_id = data.get("user_id") or "987ba50f-92cd-406e-8ac9-2bccb7e9d29e"
            
            save_session({
                "access_token": access_token,
                "user_id": user_id
            })
            
            self.token = access_token
            return data
            
        raise Exception(f"Login failed ({response.status_code}): {response.text}")

    def search(self, keyword):
        headers = self._get_headers()
        url = f"{BASE_URL}/api/v1/records/search"
        response = requests.get(url, headers=headers, params={"query": keyword})
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Search failed: {response.text}")

    def get_categories(self):
        """Fetch categories list from the server."""
        headers = self._get_headers()
        url = f"{BASE_URL}/api/v1/categories/"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return []

    def get_record(self, record_id):
        headers = self._get_headers()
        url = f"{BASE_URL}/api/v1/records/{record_id}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to fetch record: {response.text}")

    def summarize(self, record_id):
        headers = self._get_headers()
        url = f"{BASE_URL}/api/v1/records/{record_id}/extracted_text"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data and (data.get("summary") or data.get("extracted_text")):
                    return data

            rec = self.get_record(record_id)
            if rec:
                text = rec.get("description") or rec.get("content") or rec.get("title") or "No text content found."
                return {"summary": text}

            return None
        except Exception as e:
            raise Exception(f"Summarize failed: {str(e)}")

    def get_current_user_id(self):
        """Fetch current user's UUID from /api/v1/auth/me"""
        try:
            headers = self._get_headers()
            url = f"{BASE_URL}/api/v1/auth/me"
            res = requests.get(url, headers=headers)
            if res.status_code == 200:
                data = res.json()
                return data.get("id") or data.get("uid")
        except Exception as e:
            print(f"Error fetching user ID: {e}")
        return None

    def upload_document(self, file_path, category_ids=None, title=None, media_type="text", language="en"):
        headers = self._get_headers()
        file_name = os.path.basename(file_path)
        generated_uuid = str(uuid.uuid4())

        # 1. Active User ID
        session = load_session() or {}
        user_id = session.get("user_id") or "987ba50f-92cd-406e-8ac9-2bccb7e9d29e"

        # 2. Validate Title (at least 2 words)
        if not title or len(title.strip().split()) < 2:
            clean_name = os.path.splitext(file_name)[0].replace("_", " ").replace("-", " ")
            title = f"{clean_name.capitalize()} Document" if len(clean_name.split()) < 2 else clean_name

        # 3. Dynamic Category Lookup (Preserving UUIDs/Strings)
        if not category_ids:
            categories_data = self.get_categories()
            if isinstance(categories_data, list) and len(categories_data) > 0:
                first_cat = categories_data[0]
                cat_id = first_cat.get("id") if isinstance(first_cat, dict) else first_cat
                category_list = [str(cat_id)]
            else:
                category_list = [1]
        elif isinstance(category_ids, list):
            category_list = [str(x) if not isinstance(x, int) else x for x in category_ids]
        else:
            category_list = [str(category_ids) if not isinstance(category_ids, int) else category_ids]

        # Format as JSON array string
        category_json = json.dumps(category_list)

        # ----------------------------------------------------
        # STEP 1: Upload Chunk
        # ----------------------------------------------------
        chunk_url = f"{BASE_URL}/api/v1/records/upload/chunk"

        try:
            with open(file_path, "rb") as file_data:
                chunk_files = {
                    "chunk": (file_name, file_data, "text/plain")
                }
                chunk_data = {
                    "filename": file_name,
                    "chunk_index": 0,
                    "total_chunks": 1,
                    "upload_uuid": generated_uuid
                }

                chunk_res = requests.post(chunk_url, headers=headers, files=chunk_files, data=chunk_data)
                
                if chunk_res.status_code not in (200, 201):
                    return chunk_res

        except FileNotFoundError:
            raise Exception("File not found on local system.")
        except Exception as e:
            raise Exception(f"Chunk upload failed: {str(e)}")

        # ----------------------------------------------------
        # STEP 2: Finalize Record Upload
        # ----------------------------------------------------
        finalize_url = f"{BASE_URL}/api/v1/records/upload"

        # Headers without forced Content-Type
        finalize_headers = {k: v for k, v in headers.items() if k.lower() != "content-type"}

        finalize_data = {
            "title": title,
            "filename": file_name,
            "upload_uuid": generated_uuid,
            "user_id": str(user_id),
            "media_type": "text",
            "total_chunks": 1,
            "release_rights": "creator",
            "language": language,
            "category_ids": category_json
        }

        print("Finalize URL:", finalize_url)
        print("Headers:", finalize_headers)
        print("Data:", finalize_data)

        finalize_res = requests.post(finalize_url, headers=finalize_headers, data=finalize_data)
        print("Status:", finalize_res.status_code)
        print("Response:", finalize_res.text)
        
        return finalize_res
