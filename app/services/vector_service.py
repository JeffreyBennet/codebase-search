import pinecone

class VectorService:
    def __init__(self, api_key, environment, index_name):
        pinecone.init(api_key=api_key, environment=environment)
        self.index = pinecone.Index(index_name)

    def insert(self, embedding, metadata):
        """Insert an embedding into the Pinecone vector database."""
        vector_id = metadata['file_path'] + "_" + str(hash(metadata['chunk']))
        self.index.upsert([(vector_id, embedding, metadata)])

    def search(self, query_embedding, top_k=10):
        """Search the database for top K similar embeddings."""
        results = self.index.query(queries=[query_embedding], top_k=top_k, include_metadata=True)
        return results['matches']
