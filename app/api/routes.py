import os
import uuid
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from app.agents.search.search_agent import SearchAgent
from app.models.generate_model import GenerateCodeRequest
from app.models.retrieve_model import RetrieveCodeRequest
from app.models.search_model import SearchRequest
from app.services.embedding_service import EmbeddingService
from app.services.github_service import GitHubService
from app.services.graph_service import GraphService
from app.services.indexing_service import IndexingService
from app.services.llm.llm import LLM
from app.agents.agents import AgentOrchestrator
from app.services.search_service import SearchService
from app.services.vector_service import VectorService
from app.services.zip_service import ZipService  # Assuming the orchestrator is in this path

# Create a router instance
router = APIRouter()

# Dependency to initialize the AgentOrchestrator
def get_orchestrator(project_dir: str):
    llm = LLM(api_key="sk-OSfVTEAqltnjqo40HnkicT2fOXVfEMXDUpDeLV41Y-T3BlbkFJiJf0qxG0xQ0Jvm5aHGZmtV7FfxNx4HzwTd2vt-AnoA")  # Provide your LLM API key
    orchestrator = AgentOrchestrator(llm, project_dir)
    return orchestrator

# Define a background task function to handle code generation
def run_code_generation(orchestrator, user_prompt):
    try:
        user_context = []  # Optional user context
        # Call the orchestrator to generate code based on the user prompt
        result = orchestrator.orchestrate(user_prompt, [], {}, user_context)
        # You could add logic here to save the result in a database or a file
        if isinstance(result, dict):
            # Handle successful code generation result (e.g., save it to DB, etc.)
            pass
        else:
            # Handle failure (e.g., log errors or save failure reason)
            pass
    except Exception as e:
        # Handle any exceptions, like logging them
        pass

# Define an endpoint for generating code using the orchestrator, with background processing
@router.post("/api/v1/generate")
async def generate_code(generate_code_request: GenerateCodeRequest, background_tasks: BackgroundTasks):
    try:
        unique_id = str(uuid.uuid4())
        # Extract data from the request
        user_prompt = generate_code_request.user_prompt

        # Initialize orchestrator with the provided project directory
        orchestrator = get_orchestrator(unique_id + "/" +generate_code_request.project_name + "/")

        # Add the background task to run the code generation
        background_tasks.add_task(run_code_generation, orchestrator, user_prompt)

        # Return immediately with a unique hash
        return {"status": "running", "hash": unique_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Define an endpoint for generating code using the orchestrator, with background processing
@router.post("/api/v1/retrieve")
async def retrieve_code(generate_code_request: RetrieveCodeRequest):
    try:

        # Generate a unique hash or ID
        unique_id = generate_code_request.hash

        # Define the path where the zipped file will be temporarily stored
        output_zip_path = os.path.join("/tmp", f"{unique_id}_zipped_directory.zip")

        # Use the ZipService to zip the directory
        zip_file_path = ZipService.zip_directory(unique_id, output_zip_path)

        # Return the zipped file as a response
        response = FileResponse(zip_file_path, media_type="application/zip", filename=f"{unique_id}_repository.zip")

        # Return the response with the file
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
# Initialize services inside the route to ensure each request gets fresh instances
def get_services():
    github_service = GitHubService()
    indexing_service = IndexingService(openai_api_key="your-openai-api-key")
    embedding_service = EmbeddingService(openai_api_key="your-openai-api-key")
    graph_service = GraphService(neptune_endpoint="your-neptune-endpoint", aws_access_key="your-aws-access-key", aws_secret_key="your-aws-secret-key")
    vector_service = VectorService(api_key="your-pinecone-api-key", environment="your-pinecone-env", index_name="your-index-name")
    search_service = SearchService(vector_service)

    # Initialize the SearchAgent
    search_agent = SearchAgent(
        github_service,
        indexing_service,
        embedding_service,
        graph_service,
        vector_service,
        search_service
    )
    return search_agent

@router.post("/api/v1/search")
async def analyze_repository(request_data: SearchRequest):
    """
    Endpoint to analyze a public GitHub repository based on a prompt.
    Request body:
    {
        "repo_url": "https://github.com/username/repo.git",
        "prompt": "user authentication"
    }
    """
    try:
        # Extract data from the request
        repo_url = request_data.repo_url
        prompt = request_data.prompt

        # Initialize the services and search agent
        search_agent = get_services()

        # Call the SearchAgent to process the repository and query
        response = search_agent.process_repository(repo_url, prompt)

        # Return the response as JSON
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
