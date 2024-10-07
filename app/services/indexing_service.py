import openai
import os

class IndexingService:
    def __init__(self, openai_api_key):
        openai.api_key = openai_api_key

    def tokenize_code(self, code_file):
        """Tokenizes the code file into chunks like functions and classes."""
        with open(code_file, 'r') as f:
            code = f.read()
        # Tokenizing logic: You can split by functions, classes, or other logical structures
        return code.split("\n\n")  # Example of splitting by blank lines

    def extract_entities_and_relationships(self, code_chunk):
        """Extract entities and relationships using OpenAI."""
        response = openai.Completion.create(
            engine="gpt-4",
            prompt=f"Extract all entities and relationships from the following code:\n\n{code_chunk}",
            max_tokens=150
        )
        entities = []  # Extracted entities
        relationships = []  # Extracted relationships
        # Parse the response (adjust the parsing based on the response structure)
        completion_text = response['choices'][0]['text'].strip()
        if "Entities:" in completion_text:
            entities_part = completion_text.split("Entities:")[1].split("Relationships:")[0].strip()
            entities = entities_part.split(", ") if entities_part else []
        if "Relationships:" in completion_text:
            relationships_part = completion_text.split("Relationships:")[1].strip()
            relationships = relationships_part.split(", ") if relationships_part else []
        return entities, relationships
