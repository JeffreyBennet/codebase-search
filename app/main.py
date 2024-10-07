from fastapi import FastAPI
from app.api import routes 

app = FastAPI()

# Include the router for GitHub repositories
app.include_router(routes.router)

@app.get("/")
async def read_root():
    return {"message": "Hello from FastAPI!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
