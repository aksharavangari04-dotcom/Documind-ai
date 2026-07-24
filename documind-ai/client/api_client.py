import requests
from config import BASE_URL
from session import load_session


class CorpusClient:

    def __init__(self, token=None):
        self.token = token

    def _get_headers(self):
        """Retrieves authorization headers using stored session or client token."""
        token = self.token
        if not token:
            session = load_session()
            if session and "access_token" in session:
                token = session["access_token"]
                self.token = token

        if not token:
            raise Exception("Please login first.")

        return {"Authorization": f"Bearer {token}"}

    def search(self, query):
        """Search records via GET /api/v1/records/search"""
        headers = self._get_headers()
        response = requests.get(
            f"{BASE_URL}/api/v1/records/search",
            headers=headers,
            params={"query": query, "limit": 10}
        )
        response.raise_for_status()
        return response.json()

    def get_record(self, record_id):
        """Get record details via GET /api/v1/records/{record_id}"""
        headers = self._get_headers()
        response = requests.get(
            f"{BASE_URL}/api/v1/records/{record_id}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    def get_categories(self):
        """Fetch available categories via GET /api/v1/categories/"""
        headers = self._get_headers()
        response = requests.get(
            f"{BASE_URL}/api/v1/categories/",
            headers=headers
        )
        response.raise_for_status()
        return response.json()

    def upload_document(self, file_path, category_id=None):
        """Uploads a real file to POST /api/v1/records/upload"""
        headers = self._get_headers()
        url = f"{BASE_URL}/api/v1/records/upload"

        try:
            with open(file_path, "rb") as file_data:
                files = {"file": file_data}
                data = {}
                if category_id:
                    data["category_id"] = category_id

                response = requests.post(url, headers=headers, files=files, data=data)
                return response
        except FileNotFoundError:
            raise Exception("File not found on your local system.")
        except Exception as e:
            raise Exception(f"Upload failed: {str(e)}")

    def summarize(self, record_id):
        """Fetch extracted text/summary via GET /api/v1/records/{record_id}/extracted_text"""
        headers = self._get_headers()
        url = f"{BASE_URL}/api/v1/records/{record_id}/extracted_text"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print("Summarize error:", e)
            return None