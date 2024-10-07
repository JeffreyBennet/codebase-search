class SearchAgent:
    def __init__(self, github_service, indexing_service, embedding_service, graph_service, vector_db, search_service):
        self.github_service = github_service
        self.indexing_service = indexing_service
        self.embedding_service = embedding_service
        self.graph_service = graph_service
        self.vector_db = vector_db
        self.search_service = search_service

    def process_repository(self, repo_url, prompt):
        """
        Orchestrates the full pipeline: cloning repo, indexing, embedding, graph construction,
        and querying based on a prompt.
        """
        # Step 1: Clone the repository
        repo_path = self.github_service.clone_repo(repo_url)
        code_files = self.github_service.get_code_files(repo_path)

        # Step 2: Process each file
        for file in code_files:
            code_chunks = self.indexing_service.tokenize_code(file)
            for chunk in code_chunks:
                # Extract entities and relationships
                entities, relationships = self.indexing_service.extract_entities_and_relationships(chunk)
                # Add to the graph database
                self.graph_service.add_entities_and_relationships(entities, relationships)
                
                # Embed code chunk and store it in Pinecone
                embedding = self.embedding_service.embed_code_chunk(chunk)
                self.vector_db.insert(embedding, {"file_path": file, "chunk": chunk})

        # Step 3: Query the GraphRAG for relevant entities
        relevant_entities = self.graph_service.query_graph(prompt)

        # Step 4: Perform vector search using Pinecone for the relevant code chunks
        prompt_embedding = self.embedding_service.embed_code_chunk(prompt)
        search_results = self.search_service.query(prompt_embedding)

        # Step 5: Collect and return the relevant files and code snippets
        response = []
        for result in search_results:
            response.append({
                "file_path": result['metadata']['file_path'],
                "code_snippet": result['metadata']['chunk']
            })

        return response
