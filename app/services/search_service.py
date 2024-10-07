class SearchService:
    def __init__(self, vector_db):
        self.vector_db = vector_db
    
    def query(self, query_embedding, top_k=10):
        """Query the vector database for the most relevant code chunks."""
        results = self.vector_db.search(query_embedding, top_k=top_k)
        return results
