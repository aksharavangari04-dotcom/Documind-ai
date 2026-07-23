from sample_data import documents


class CorpusClient:

    def search(self, query):

        results = []

        query = query.lower()

        # Smart keyword mapping
        keywords = {
            "ai": [
                "artificial intelligence",
                "machine learning",
                "deep learning",
                "ai"
            ],
            "ml": [
                "machine learning",
                "ml"
            ]
        }

        search_terms = keywords.get(query, [query])

        for doc in documents:

            text = (
                doc["title"] + " " + doc["content"]
            ).lower()

            for term in search_terms:
                if term in text:
                    results.append(doc)
                    break

        return results


    def get_document(self, doc_id):

        for doc in documents:
            if doc["id"] == doc_id:
                return doc

        return None


    def summarize(self, doc_id):

        document = self.get_document(doc_id)

        if document is None:
            return None

        content = document["content"]

        words = content.split()

        summary = " ".join(words[:30])

        return {
            "id": doc_id,
            "title": document["title"],
            "summary": summary
        }
