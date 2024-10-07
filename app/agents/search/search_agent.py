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

        # Step 2: Process each file and build graph
        for file in code_files:
            code_chunks = self.indexing_service.tokenize_code(file)
            for chunk in code_chunks:
                # Extract entities and relationships from the code
                entities, relationships = self.indexing_service.extract_entities_and_relationships(chunk)
                
                # Add extracted entities and relationships to the graph
                self.graph_service.add_entities_and_relationships(entities, relationships)
                
                # Embed code chunk and store it in the vector database (Pinecone)
                embedding = self.embedding_service.embed_code_chunk(chunk)
                self.vector_db.insert(embedding, {"file_path": file, "chunk": chunk})

        # Step 3: Query the graph to find entities related to the prompt
        # This allows us to capture semantically connected parts of the codebase
        relevant_entities_from_graph = self.graph_service.query_graph(prompt)

        # Step 4: Perform vector search based on the prompt using Pinecone
        prompt_embedding = self.embedding_service.embed_code_chunk(prompt)
        search_results = self.search_service.query(prompt_embedding)

        # Step 5: Refine search results using graph relationships
        # Here, we use the entities retrieved from the graph to filter or prioritize results from the vector search.
        refined_results = self.refine_results_using_graph(search_results, relevant_entities_from_graph)

        # Step 6: Collect and return the relevant files and code snippets
        response = []
        for result in refined_results:
            response.append({
                "file_path": result['metadata']['file_path'],
                "code_snippet": result['metadata']['chunk']
            })

        return response

    def refine_results_using_graph(self, search_results, relevant_entities_from_graph):
        """
        Refine the search results based on relationships in the graph.
        """
        refined_results = []
        
        # Iterate over search results and check if the entities related to the result
        # are present in the graph query results
        for result in search_results:
            # Extract the file path or chunk of code from the metadata
            code_snippet = result['metadata']['chunk']
            
            # Check if the entities extracted from the code snippet are related to the graph entities
            snippet_entities, _ = self.indexing_service.extract_entities_and_relationships(code_snippet)
            
            # If there's any intersection between snippet entities and graph entities, prioritize this result
            if any(entity in relevant_entities_from_graph for entity in snippet_entities):
                refined_results.append(result)

        # Return refined results, sorted based on relevance (optional)
        return sorted(refined_results, key=lambda x: x['score'], reverse=True)  # Assuming results have 'score'
