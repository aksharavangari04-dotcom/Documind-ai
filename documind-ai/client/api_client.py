import requests
from config import BASE_URL
from session import load_session


class CorpusClient:

    def search(self, query):

        session = load_session()

        if session is None:
            raise Exception("Please login first.")

        token = session["access_token"]

        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(
            f"{BASE_URL}/api/v1/records/search",
            headers=headers,
            params={
                "query": query,
                "limit": 10
            }
        )

        response.raise_for_status()

        return response.json()

     def get_record(self, record_id):

        session = load_session()

        if session is None:
            raise Exception("Please login first.")

        token = session["access_token"]

        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(
            f"{BASE_URL}/api/v1/records/{record_id}",
            headers=headers
        )

        response.raise_for_status()

        return response.json()

    def get_document(self, doc_id):

        for doc in documents:
            if doc["id"] == doc_id:
                return doc

        return None


    def summarize(self, doc_id):

        document = self.get_document(doc_id)

        if document is None:
            return None

        words = document["content"].split()

        return {
            "id": document["id"],
            "title": document["title"],
            "summary": " ".join(words[:30])
        }
